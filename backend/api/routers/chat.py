"""
/api/chat - query, streaming, search, and export endpoints
"""

import asyncio
import json
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from api.auth import get_current_user_id
from api.database import get_db
from api.dependencies import ModuleManager, get_modules
from api.limiter import limiter
from api.routers.papers import get_papers, namespace_collection_name
from api.schemas import (
    PPTExportRequest,
    QueryRequest,
    QueryResponse,
    RouteInfo,
    SearchRequest,
    SearchResponse,
    SourceDocument,
)
from config import DATA_DIR
from modules.followup_generator import generate_followups
from modules.query_router import RouteType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

STREAM_PIPELINE_TIMEOUT_SECONDS = 120
GENERATION_QUEUE_TIMEOUT_SECONDS = int(
    os.environ.get("GENERATION_QUEUE_TIMEOUT_SECONDS", "29")
)
GENERATION_CONCURRENCY = max(1, int(os.environ.get("GENERATION_CONCURRENCY", "1")))
_generation_semaphore = asyncio.Semaphore(GENERATION_CONCURRENCY)


def _to_source_documents(
    documents: list[dict], truncate: bool = True
) -> list[SourceDocument]:
    return [
        SourceDocument(
            chunk_id=doc.get("chunk_id", ""),
            content=(
                doc.get("content", "")[:500] if truncate else doc.get("content", "")
            ),
            section_type=doc.get("metadata", {}).get("section_type", "unknown"),
            doc_id=doc.get("metadata", {}).get("doc_id", ""),
            page=doc.get("metadata", {}).get("page", 0),
            score=doc.get("rerank_score", doc.get("rrf_score", 0.0)),
        )
        for doc in documents
    ]


def _chunk_text(text: str, chunk_size: int = 24):
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]


async def _run_pipeline_with_generation_gate(
    decision,
    req: QueryRequest,
    m: ModuleManager,
    available_docs: list[str],
    papers: dict,
    internal_collection_name: str,
) -> dict:
    acquired = False
    try:
        await asyncio.wait_for(
            _generation_semaphore.acquire(), timeout=GENERATION_QUEUE_TIMEOUT_SECONDS
        )
        acquired = True
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=429,
            detail=f"Generation queue is full. Retry after {GENERATION_QUEUE_TIMEOUT_SECONDS}s.",
        )

    try:
        return await asyncio.to_thread(
            _run_pipeline,
            decision,
            req,
            m,
            available_docs,
            papers,
            internal_collection_name,
        )
    finally:
        if acquired:
            _generation_semaphore.release()


@router.post("/query", response_model=QueryResponse)
@limiter.limit("20/minute")
async def query(
    request: Request,
    req: QueryRequest,
    user_id: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
    db=Depends(get_db),
):
    internal_collection_name = namespace_collection_name(user_id, req.collection_name)
    papers = await get_papers(db, user_id, req.collection_name)
    available_docs = list(papers.keys())
    if not available_docs:
        raise HTTPException(400, "No uploaded papers found. Upload a paper first.")

    decision = m.query_router.route(req.query, available_docs)
    route_info = RouteInfo(
        route=decision.route.value,
        route_name=m.query_router.get_route_description(decision.route),
        section_filter=decision.section_filter,
        confidence=decision.confidence,
    )

    if not m.has_generator:
        search_results = m.hybrid_retriever.search(
            collection_name=internal_collection_name,
            query=req.query,
            top_k=req.top_k,
        )
        reranked = m.reranker.rerank(req.query, search_results, top_k=req.top_k)
        sources = _to_source_documents(reranked, truncate=False)
        no_gen_answer = (
            "[Generator not loaded: returning search results only]\n\n"
            + "\n\n---\n\n".join(
                f"**[{s.section_type}]** (p.{s.page})\n{s.content[:300]}"
                for s in sources
            )
        )
        return QueryResponse(
            answer=no_gen_answer,
            route=route_info,
            sources=sources,
            steps=[{"step": "search_only", "reason": "no_generator"}],
            pipeline=f"{decision.route.value}_search_only",
            follow_ups=generate_followups(
                query=req.query,
                answer=no_gen_answer,
                route=decision.route.value,
                section_filter=decision.section_filter,
            ),
        )

    result = await _run_pipeline_with_generation_gate(
        decision,
        req,
        m,
        available_docs,
        papers,
        internal_collection_name,
    )
    sources = _to_source_documents(result.get("source_documents", []), truncate=True)
    answer_text = result.get("answer", "")
    follow_ups = generate_followups(
        query=req.query,
        answer=answer_text,
        route=decision.route.value,
        section_filter=decision.section_filter,
        generator=m.generator if m.has_generator else None,
    )

    return QueryResponse(
        answer=answer_text,
        route=route_info,
        sources=sources,
        steps=result.get("steps", []),
        pipeline=result.get("pipeline", ""),
        follow_ups=follow_ups,
    )


@router.post("/query/stream")
@limiter.limit("20/minute")
async def query_stream(
    request: Request,
    req: QueryRequest,
    user_id: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
    db=Depends(get_db),
):
    internal_collection_name = namespace_collection_name(user_id, req.collection_name)
    papers = await get_papers(db, user_id, req.collection_name)
    available_docs = list(papers.keys())
    if not available_docs:
        raise HTTPException(400, "No uploaded papers found. Upload a paper first.")

    decision = m.query_router.route(req.query, available_docs)
    route_info = {
        "route": decision.route.value,
        "route_name": m.query_router.get_route_description(decision.route),
        "section_filter": decision.section_filter,
        "confidence": decision.confidence,
    }

    def sse_event(event: str, payload: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    generation_gate_acquired = False
    if m.has_generator:
        try:
            await asyncio.wait_for(
                _generation_semaphore.acquire(),
                timeout=GENERATION_QUEUE_TIMEOUT_SECONDS,
            )
            generation_gate_acquired = True
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=429,
                detail=f"Generation queue is full. Retry after {GENERATION_QUEUE_TIMEOUT_SECONDS}s.",
            )

    async def event_generator():
        try:
            if not m.has_generator:
                search_results = m.hybrid_retriever.search(
                    collection_name=internal_collection_name,
                    query=req.query,
                    top_k=req.top_k,
                )
                reranked = m.reranker.rerank(req.query, search_results, top_k=req.top_k)
                sources = [
                    {
                        "chunk_id": doc.get("chunk_id", ""),
                        "content": doc.get("content", "")[:500],
                        "section_type": doc.get("metadata", {}).get(
                            "section_type", "unknown"
                        ),
                        "doc_id": doc.get("metadata", {}).get("doc_id", ""),
                        "page": doc.get("metadata", {}).get("page", 0),
                        "score": doc.get("rerank_score", 0.0),
                    }
                    for doc in reranked
                ]
                answer = (
                    "[Generator not loaded: returning search results only]\n\n"
                    + "\n\n---\n\n".join(
                        f"**[{s['section_type']}]** (p.{s['page']})\n{s['content'][:300]}"
                        for s in sources
                    )
                )
                follow_ups = generate_followups(
                    query=req.query,
                    answer=answer,
                    route=decision.route.value,
                    section_filter=decision.section_filter,
                )
                yield sse_event(
                    "metadata", {"route": route_info, "sources": sources, "steps": []}
                )
                yield sse_event("token", {"token": answer})
                yield sse_event(
                    "done", {"full_answer": answer, "follow_ups": follow_ups}
                )
                return

            result = await asyncio.wait_for(
                asyncio.to_thread(
                    _run_pipeline,
                    decision,
                    req,
                    m,
                    available_docs,
                    papers,
                    internal_collection_name,
                ),
                # Keep stream path behavior aligned with non-stream pipeline execution.
                timeout=STREAM_PIPELINE_TIMEOUT_SECONDS,
            )
            source_docs = _to_source_documents(
                result.get("source_documents", []), truncate=True
            )
            sources = [doc.model_dump() for doc in source_docs]
            steps = result.get("steps", [])
            pipeline_name = result.get("pipeline", "")

            answer_text = result.get("answer", "") or "No answer generated."
            follow_ups = generate_followups(
                query=req.query,
                answer=answer_text,
                route=decision.route.value,
                section_filter=decision.section_filter,
                generator=m.generator if m.has_generator else None,
            )

            yield sse_event(
                "metadata",
                {
                    "route": route_info,
                    "sources": sources,
                    "steps": steps,
                    "pipeline": pipeline_name,
                },
            )
            for text_chunk in _chunk_text(answer_text):
                yield sse_event("token", {"token": text_chunk})
                await asyncio.sleep(0)
            yield sse_event(
                "done",
                {
                    "full_answer": answer_text,
                    "follow_ups": follow_ups,
                    "pipeline": pipeline_name,
                },
            )
        except asyncio.TimeoutError:
            logger.error(
                "Streaming pipeline timed out after %ss",
                STREAM_PIPELINE_TIMEOUT_SECONDS,
            )
            yield sse_event(
                "error",
                {
                    "error": "stream_timeout",
                    "detail": f"Pipeline exceeded {STREAM_PIPELINE_TIMEOUT_SECONDS}s timeout",
                    "retryable": True,
                },
            )
        except Exception as exc:
            logger.error("Streaming generation error: %s", exc, exc_info=True)
            yield sse_event(
                "error",
                {
                    "error": "stream_generation_failed",
                    "detail": "Streaming failed during pipeline execution",
                    "retryable": True,
                },
            )
        finally:
            if generation_gate_acquired:
                _generation_semaphore.release()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/search", response_model=SearchResponse)
async def search_only(
    req: SearchRequest,
    user_id: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
    db=Depends(get_db),
):
    internal_collection_name = namespace_collection_name(user_id, req.collection_name)
    papers = await get_papers(db, user_id, req.collection_name)
    if not papers:
        raise HTTPException(404, "Collection not found.")

    results = m.hybrid_retriever.search(
        collection_name=internal_collection_name,
        query=req.query,
        top_k=req.top_k,
        section_filter=req.section_filter,
        doc_id_filter=req.doc_id_filter,
    )
    reranked = m.reranker.rerank(req.query, results, top_k=req.top_k)
    sources = _to_source_documents(reranked, truncate=False)
    bm25_fitted = m.hybrid_retriever.has_bm25_for_collection(internal_collection_name)
    return SearchResponse(results=sources, total=len(sources), bm25_fitted=bm25_fitted)


@router.post("/export/ppt")
async def export_ppt(
    req: PPTExportRequest,
    _: str = Depends(get_current_user_id),
):
    from modules.pptx_exporter import create_pptx

    pptx_bytes = create_pptx(
        answer=req.answer,
        title=req.title,
        subtitle=req.subtitle,
    )
    return StreamingResponse(
        pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": 'attachment; filename="m-rag-summary.pptx"'},
    )


def _run_pipeline(
    decision, req, m, available_docs, papers, internal_collection_name: str
) -> dict:
    from pipelines import (
        pipeline_a_simple_qa,
        pipeline_b_section,
        pipeline_c_compare,
        pipeline_e_summary,
        pipeline_f_quiz,
    )
    from modules.section_detector import SectionDetector

    col = internal_collection_name
    hr = m.hybrid_retriever
    rr = m.reranker
    comp = m.compressor
    gen = m.generator
    qe = m.query_expander

    if decision.route == RouteType.SECTION:
        return pipeline_b_section.run(
            req.query,
            col,
            decision.section_filter,
            hr,
            rr,
            comp,
            gen,
            req.use_cad,
            req.cad_alpha,
            req.use_scd,
            req.scd_beta,
        )
    if decision.route == RouteType.COMPARE:
        return pipeline_c_compare.run(
            req.query,
            col,
            decision.target_doc_ids,
            hr,
            rr,
            comp,
            gen,
            req.use_cad,
            req.cad_alpha,
            req.use_scd,
            req.scd_beta,
        )
    if decision.route == RouteType.CITATION:
        doc = papers[available_docs[0]]
        from modules.chunker import Chunker
        from modules.pdf_parser import PDFParser
        from pipelines import pipeline_d_citation

        return pipeline_d_citation.run(
            req.query,
            col,
            doc,
            hr,
            rr,
            comp,
            gen,
            m.citation_tracker,
            m.embedder,
            m.vector_store,
            SectionDetector(),
            PDFParser(),
            Chunker(),
            str(DATA_DIR),
            req.use_cad,
            req.cad_alpha,
            req.use_scd,
            req.scd_beta,
        )
    if decision.route == RouteType.SUMMARY:
        return pipeline_e_summary.run(
            req.query,
            col,
            hr,
            rr,
            comp,
            gen,
            req.use_cad,
            req.cad_alpha,
            req.use_scd,
            req.scd_beta,
        )
    if decision.route == RouteType.QUIZ:
        return pipeline_f_quiz.run(
            req.query,
            col,
            hr,
            rr,
            comp,
            gen,
            qe,
            req.use_cad,
            req.cad_alpha,
            req.use_scd,
            req.scd_beta,
        )
    return pipeline_a_simple_qa.run(
        query=req.query,
        collection_name=col,
        hybrid_retriever=hr,
        reranker=rr,
        compressor=comp,
        generator=gen,
        query_expander=qe,
        use_hyde=req.use_hyde,
        use_cad=req.use_cad,
        cad_alpha=req.cad_alpha,
        use_scd=req.use_scd,
        scd_beta=req.scd_beta,
    )
