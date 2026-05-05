"""
/api/chat - query, streaming, search, and export endpoints
"""

import asyncio
import json
import logging
import os
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from api.auth import get_current_user_id
from api.database import get_db
from api.dependencies import ModuleManager, get_modules
from api.limiter import limiter
from api.routers.papers import get_papers, namespace_collection_name
from api.schemas import (
    JudgeRequest,
    JudgeResponse,
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


def _ensure_generator_available(m: ModuleManager) -> None:
    if not m.has_generator:
        raise HTTPException(
            status_code=503,
            detail="Generator model is not loaded. This runtime does not support query generation without an LLM.",
        )


def _normalize_compare_text(value: str) -> str:
    value = value.lower().replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", value).strip()


def _dedupe_doc_ids(doc_ids) -> list[str]:
    seen = set()
    deduped: list[str] = []
    for doc_id in doc_ids or []:
        normalized = str(doc_id).strip()
        if normalized and normalized not in seen:
            deduped.append(normalized)
            seen.add(normalized)
    return deduped


def _paper_aliases(doc_id: str, paper) -> list[str]:
    metadata = getattr(paper, "metadata", {}) or {}
    title = getattr(paper, "title", "") or ""
    aliases = [
        doc_id,
        doc_id.replace("_", " "),
        doc_id.replace("-", " "),
        title,
        metadata.get("filename", ""),
        metadata.get("file_name", ""),
        metadata.get("source_file", ""),
        metadata.get("original_filename", ""),
    ]
    return [str(alias).strip() for alias in aliases if str(alias).strip()]


def _find_doc_mentions(query: str, papers: dict, exclude: set[str] | None = None):
    query_text = _normalize_compare_text(query)
    exclude = exclude or set()
    matches = []
    for doc_id, paper in papers.items():
        if doc_id in exclude:
            continue
        for alias in _paper_aliases(doc_id, paper):
            alias_text = _normalize_compare_text(alias)
            if len(alias_text) < 3:
                continue
            if alias_text in query_text:
                matches.append(
                    {
                        "doc_id": doc_id,
                        "alias": alias,
                        "match_length": len(alias_text),
                    }
                )
                break
    matches.sort(key=lambda item: (-item["match_length"], item["doc_id"]))
    return matches


def _score_docs_by_retrieval(
    query: str,
    collection_name: str,
    candidate_doc_ids: list[str],
    hybrid_retriever,
) -> dict[str, float]:
    scores: dict[str, float] = {}
    for doc_id in candidate_doc_ids:
        try:
            results = hybrid_retriever.search(
                collection_name=collection_name,
                query=query,
                top_k=3,
                doc_id_filter=doc_id,
            )
        except Exception as exc:
            logger.info("Compare target retrieval scoring unavailable: %s", exc)
            return {}

        score = 0.0
        for rank, result in enumerate(results[:3]):
            raw_score = result.get("rerank_score", result.get("rrf_score", 0.0))
            try:
                score += float(raw_score) / (rank + 1)
            except (TypeError, ValueError):
                continue
        if results:
            scores[doc_id] = round(score, 6)
    return scores


def _compare_selection(
    doc_ids: list[str],
    method: str,
    reason: str,
    fallback_used: bool = False,
    candidate_scores: dict[str, float] | None = None,
) -> dict:
    return {
        "target_doc_ids": doc_ids,
        "target_selection_method": method,
        "target_selection_reason": reason,
        "fallback_used": fallback_used,
        "candidate_scores": candidate_scores or {},
    }


def _compare_selection_error(
    method: str,
    reason: str,
    message: str,
    target_doc_ids: list[str] | None = None,
) -> dict:
    selection = _compare_selection(
        target_doc_ids or [],
        method,
        reason,
        fallback_used=False,
    )
    selection["error"] = True
    selection["message"] = message
    return selection


def _target_selection_step(selection: dict) -> dict:
    step = {
        "step": "target_selection",
        "target_doc_ids": selection.get("target_doc_ids", []),
        "target_selection_method": selection.get("target_selection_method", ""),
        "target_selection_reason": selection.get("target_selection_reason", ""),
        "selection_reason": selection.get("target_selection_reason", ""),
        "fallback_used": bool(selection.get("fallback_used", False)),
    }
    candidate_scores = selection.get("candidate_scores")
    if candidate_scores:
        step["candidate_scores"] = candidate_scores
    return step


def _compare_selection_error_response(selection: dict) -> dict:
    return {
        "answer": selection.get(
            "message",
            "Comparison target selection failed. Please choose exactly two documents.",
        ),
        "sources": "",
        "source_documents": [],
        "pipeline": "C_compare",
        "compared_docs": selection.get("target_doc_ids", []),
        "steps": [
            _target_selection_step(selection),
            {"step": "error", "reason": selection.get("target_selection_method", "")},
        ],
        "target_selection_method": selection.get("target_selection_method", ""),
        "target_selection_reason": selection.get("target_selection_reason", ""),
        "fallback_used": bool(selection.get("fallback_used", False)),
        "candidate_scores": selection.get("candidate_scores", {}),
        "error": True,
    }


def _select_compare_targets(
    decision,
    req: QueryRequest,
    available_docs: list[str],
    papers: dict,
    collection_name: str,
    hybrid_retriever,
) -> dict:
    available_set = set(available_docs)
    if len(available_docs) < 2:
        return _compare_selection_error(
            "insufficient_available_docs",
            "Fewer than two uploaded documents are available.",
            "At least two uploaded documents are required for comparison. Upload another paper or choose a collection with two documents.",
        )

    explicit_fields = [
        ("target_doc_ids", _dedupe_doc_ids(getattr(req, "target_doc_ids", None))),
        ("compare_doc_ids", _dedupe_doc_ids(getattr(req, "compare_doc_ids", None))),
    ]
    for field_name, doc_ids in explicit_fields:
        if len(doc_ids) > 2:
            return _compare_selection_error(
                "too_many_explicit_targets",
                f"{field_name} provided {len(doc_ids)} targets; exactly two are required.",
                "Comparison requires exactly two target documents. Please provide exactly two IDs.",
                target_doc_ids=doc_ids,
            )

    for field_name, doc_ids in explicit_fields:
        if len(doc_ids) == 2:
            missing = [doc_id for doc_id in doc_ids if doc_id not in available_set]
            if missing:
                return _compare_selection_error(
                    "unknown_explicit_targets",
                    f"{field_name} includes unknown document IDs: {missing}.",
                    f"Unknown comparison target document ID(s): {', '.join(missing)}.",
                    target_doc_ids=doc_ids,
                )
            return _compare_selection(
                doc_ids,
                "explicit_targets",
                f"Using explicit {field_name} pair.",
                fallback_used=False,
            )

    single_explicit_targets = [
        doc_id
        for _, doc_ids in explicit_fields
        for doc_id in doc_ids
        if doc_id in available_set
    ]
    router_mentions = [
        doc_id
        for doc_id in _dedupe_doc_ids(decision.target_doc_ids)
        if doc_id in available_set
    ]
    active_doc_id = getattr(req, "doc_id_filter", None)
    active_doc_id = active_doc_id if active_doc_id in available_set else None

    if active_doc_id:
        for doc_id in single_explicit_targets + router_mentions:
            if doc_id != active_doc_id:
                return _compare_selection(
                    [active_doc_id, doc_id],
                    "active_doc_plus_explicit_or_id_match",
                    f"Using active document {active_doc_id} and mentioned document {doc_id}.",
                    fallback_used=False,
                )

        matches = _find_doc_mentions(req.query, papers, exclude={active_doc_id})
        if matches:
            selected = matches[0]["doc_id"]
            return _compare_selection(
                [active_doc_id, selected],
                "active_doc_plus_title_or_alias_match",
                f"Using active document {active_doc_id} and query-matched document {selected} via '{matches[0]['alias']}'.",
                fallback_used=False,
            )

        candidates = [doc_id for doc_id in available_docs if doc_id != active_doc_id]
        scores = _score_docs_by_retrieval(
            req.query,
            collection_name,
            candidates,
            hybrid_retriever,
        )
        if scores:
            selected = max(scores, key=scores.get)
            return _compare_selection(
                [active_doc_id, selected],
                "active_doc_plus_retrieval_fallback",
                f"Using active document {active_doc_id} and retrieval-scored candidate {selected}.",
                fallback_used=True,
                candidate_scores=scores,
            )

        selected = candidates[0]
        return _compare_selection(
            [active_doc_id, selected],
            "active_doc_plus_deterministic_fallback",
            f"Retrieval scoring unavailable; using active document {active_doc_id} and first available different document {selected}.",
            fallback_used=True,
        )

    mentions = _dedupe_doc_ids(single_explicit_targets + router_mentions)
    metadata_matches = [
        match["doc_id"] for match in _find_doc_mentions(req.query, papers)
    ]
    mentions = _dedupe_doc_ids(mentions + metadata_matches)
    if len(mentions) >= 2:
        selected = mentions[:2]
        return _compare_selection(
            selected,
            "title_doc_id_or_alias_match",
            f"Using two query-matched documents: {selected}.",
            fallback_used=False,
        )
    if len(mentions) == 1:
        primary = mentions[0]
        candidates = [doc_id for doc_id in available_docs if doc_id != primary]
        scores = _score_docs_by_retrieval(
            req.query,
            collection_name,
            candidates,
            hybrid_retriever,
        )
        if scores:
            selected = max(scores, key=scores.get)
            return _compare_selection(
                [primary, selected],
                "single_match_plus_retrieval_fallback",
                f"Using query-matched document {primary} and retrieval-scored candidate {selected}.",
                fallback_used=True,
                candidate_scores=scores,
            )
        selected = candidates[0]
        return _compare_selection(
            [primary, selected],
            "single_match_plus_deterministic_fallback",
            f"Retrieval scoring unavailable; using query-matched document {primary} and first available different document {selected}.",
            fallback_used=True,
        )

    scores = _score_docs_by_retrieval(
        req.query,
        collection_name,
        available_docs,
        hybrid_retriever,
    )
    if len(scores) >= 2:
        selected = sorted(scores, key=scores.get, reverse=True)[:2]
        return _compare_selection(
            selected,
            "retrieval_score_fallback",
            f"Using top two retrieval-scored documents: {selected}.",
            fallback_used=True,
            candidate_scores=scores,
        )

    selected = available_docs[:2]
    return _compare_selection(
        selected,
        "deterministic_available_docs_fallback",
        f"Retrieval scoring unavailable; using first two available documents: {selected}.",
        fallback_used=True,
    )


def _apply_explicit_compare_route(decision, req: QueryRequest):
    if _dedupe_doc_ids(getattr(req, "target_doc_ids", None)) or _dedupe_doc_ids(
        getattr(req, "compare_doc_ids", None)
    ):
        decision.route = RouteType.COMPARE
        decision.section_filter = None
        decision.confidence = max(decision.confidence, 1.0)
        decision.reasoning = "Explicit compare target IDs provided"
    return decision


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
@limiter.limit("200/minute")
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
    _ensure_generator_available(m)

    decision = _apply_explicit_compare_route(
        m.query_router.route(req.query, available_docs),
        req,
    )
    route_info = RouteInfo(
        route=decision.route.value,
        route_name=m.query_router.get_route_description(decision.route),
        section_filter=decision.section_filter,
        confidence=decision.confidence,
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
        generator=m.generator,
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
@limiter.limit("200/minute")
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
    _ensure_generator_available(m)

    decision = _apply_explicit_compare_route(
        m.query_router.route(req.query, available_docs),
        req,
    )
    route_info = {
        "route": decision.route.value,
        "route_name": m.query_router.get_route_description(decision.route),
        "section_filter": decision.section_filter,
        "confidence": decision.confidence,
    }

    def sse_event(event: str, payload: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    generation_gate_acquired = False
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
            metadata_payload = {
                "route": route_info,
                "sources": sources,
                "steps": steps,
                "pipeline": pipeline_name,
            }
            if pipeline_name == "C_compare":
                metadata_payload.update(
                    {
                        "compared_docs": result.get("compared_docs", []),
                        "target_selection_method": result.get(
                            "target_selection_method", ""
                        ),
                        "target_selection_reason": result.get(
                            "target_selection_reason", ""
                        ),
                        "fallback_used": bool(result.get("fallback_used", False)),
                        "candidate_scores": result.get("candidate_scores", {}),
                    }
                )

            answer_text = result.get("answer", "") or "No answer generated."
            follow_ups = generate_followups(
                query=req.query,
                answer=answer_text,
                route=decision.route.value,
                section_filter=decision.section_filter,
                generator=m.generator,
            )

            yield sse_event("metadata", metadata_payload)
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


@router.post("/judge", response_model=JudgeResponse)
@limiter.limit("600/minute")
async def judge_prompt(
    request: Request,
    req: JudgeRequest,
    _: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
):
    _ensure_generator_available(m)
    acquired = False
    try:
        await asyncio.wait_for(
            _generation_semaphore.acquire(),
            timeout=GENERATION_QUEUE_TIMEOUT_SECONDS,
        )
        acquired = True
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=429,
            detail=f"Generation queue is full. Retry after {GENERATION_QUEUE_TIMEOUT_SECONDS}s.",
        )

    try:
        if req.labels:
            text, scores = await asyncio.to_thread(
                m.generator.rank_labels,
                req.prompt,
                req.labels,
            )
        else:
            text = await asyncio.to_thread(
                m.generator.generate_judge,
                req.prompt,
                req.max_new_tokens,
            )
            scores = None
    finally:
        if acquired:
            _generation_semaphore.release()
    return JudgeResponse(text=text, scores=scores)


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
    doc_id_filter = getattr(req, "doc_id_filter", None)
    # req.section_filter overrides the router decision (evaluation explicit control)
    effective_section_filter = (
        getattr(req, "section_filter", None) or decision.section_filter
    )

    if decision.route == RouteType.SECTION:
        return pipeline_b_section.run(
            req.query,
            col,
            effective_section_filter,
            hr,
            rr,
            comp,
            gen,
            req.use_cad,
            req.cad_alpha,
            req.use_scd,
            req.scd_beta,
            doc_id_filter=doc_id_filter,
            query_expander=qe,
            use_hyde=req.use_hyde,
        )
    if decision.route == RouteType.COMPARE:
        target_selection = _select_compare_targets(
            decision,
            req,
            available_docs,
            papers,
            col,
            hr,
        )
        if target_selection.get("error"):
            return _compare_selection_error_response(target_selection)
        return pipeline_c_compare.run(
            req.query,
            col,
            target_selection["target_doc_ids"],
            hr,
            rr,
            comp,
            gen,
            req.use_cad,
            req.cad_alpha,
            req.use_scd,
            req.scd_beta,
            target_selection=target_selection,
        )
    if decision.route == RouteType.CITATION:
        target_doc_id = doc_id_filter if doc_id_filter in papers else available_docs[0]
        doc = papers[target_doc_id]
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
            patent_tracker=m.patent_tracker,
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
            doc_id_filter=doc_id_filter,
        )
    if decision.route == RouteType.QUIZ:
        return pipeline_f_quiz.run(
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
            doc_id_filter=doc_id_filter,
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
        doc_id_filter=doc_id_filter,
        section_filter=getattr(req, "section_filter", None),
    )
