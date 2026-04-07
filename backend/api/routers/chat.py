"""
/api/chat — 질의응답 (핵심 RAG 파이프라인)
"""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from config import DATA_DIR
from api.dependencies import ModuleManager, get_modules
from api.schemas import (
    QueryRequest, QueryResponse, RouteInfo, SourceDocument,
    SearchRequest, SearchResponse,
)
from api.routers.papers import get_papers
from modules.query_router import RouteType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/query", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    m: ModuleManager = Depends(get_modules),
):
    """쿼리 → 라우터 → 파이프라인 → 답변"""

    papers = get_papers()
    available_docs = list(papers.keys())

    if not available_docs:
        raise HTTPException(400, "업로드된 논문이 없습니다. 먼저 PDF를 업로드하세요.")

    # 1. 쿼리 라우팅
    decision = m.query_router.route(req.query, available_docs)
    route_info = RouteInfo(
        route=decision.route.value,
        route_name=m.query_router.get_route_description(decision.route),
        section_filter=decision.section_filter,
        confidence=decision.confidence,
    )

    # 2. 생성 모델 없으면 검색 결과만 반환
    if not m.has_generator:
        search_results = m.hybrid_retriever.search(
            collection_name=req.collection_name,
            query=req.query,
            top_k=req.top_k,
        )
        reranked = m.reranker.rerank(req.query, search_results, top_k=req.top_k)

        sources = [
            SourceDocument(
                chunk_id=doc.get("chunk_id", ""),
                content=doc["content"],
                section_type=doc.get("metadata", {}).get("section_type", "unknown"),
                doc_id=doc.get("metadata", {}).get("doc_id", ""),
                page=doc.get("metadata", {}).get("page", 0),
                score=doc.get("rerank_score", 0.0),
            )
            for doc in reranked
        ]

        return QueryResponse(
            answer="[생성 모델 미로드] 검색 결과만 반환합니다.\n\n"
                   + "\n\n---\n\n".join(
                       f"**[{s.section_type}]** (p.{s.page})\n{s.content[:300]}"
                       for s in sources
                   ),
            route=route_info,
            sources=sources,
            steps=[{"step": "search_only", "reason": "no_generator"}],
            pipeline=f"{decision.route.value}_search_only",
        )

    # 3. 전체 파이프라인 실행
    result = _run_pipeline(
        decision, req, m, available_docs, papers
    )

    sources = [
        SourceDocument(
            chunk_id=doc.get("chunk_id", ""),
            content=doc["content"][:500],
            section_type=doc.get("metadata", {}).get("section_type", "unknown"),
            doc_id=doc.get("metadata", {}).get("doc_id", ""),
            page=doc.get("metadata", {}).get("page", 0),
            score=doc.get("rerank_score", doc.get("rrf_score", 0.0)),
        )
        for doc in result.get("source_documents", [])
    ]

    return QueryResponse(
        answer=result.get("answer", ""),
        route=route_info,
        sources=sources,
        steps=result.get("steps", []),
        pipeline=result.get("pipeline", ""),
    )


@router.post("/query/stream")
async def query_stream(
    req: QueryRequest,
    m: ModuleManager = Depends(get_modules),
):
    """SSE 스트리밍 질의응답 — 프론트엔드용"""
    import asyncio

    papers = get_papers()
    available_docs = list(papers.keys())

    if not available_docs:
        raise HTTPException(400, "업로드된 논문이 없습니다. 먼저 PDF를 업로드하세요.")

    # 라우팅
    decision = m.query_router.route(req.query, available_docs)
    route_info = {
        "route": decision.route.value,
        "route_name": m.query_router.get_route_description(decision.route),
        "section_filter": decision.section_filter,
        "confidence": decision.confidence,
    }

    async def event_generator():
        # 1. 검색 + 리랭킹 (동기)
        search_results = m.hybrid_retriever.search(
            collection_name=req.collection_name,
            query=req.query,
            top_k=req.top_k,
        )
        reranked = m.reranker.rerank(req.query, search_results, top_k=req.top_k)

        sources = [
            {
                "chunk_id": doc.get("chunk_id", ""),
                "content": doc["content"][:500],
                "section_type": doc.get("metadata", {}).get("section_type", "unknown"),
                "doc_id": doc.get("metadata", {}).get("doc_id", ""),
                "page": doc.get("metadata", {}).get("page", 0),
                "score": doc.get("rerank_score", 0.0),
            }
            for doc in reranked
        ]

        # 메타데이터 이벤트 전송
        metadata = {"route": route_info, "sources": sources, "steps": []}
        yield f"event: metadata\ndata: {json.dumps(metadata, ensure_ascii=False)}\n\n"

        # 2. 생성 모델 없으면 검색 결과만
        if not m.has_generator:
            answer = "[생성 모델 미로드] 검색 결과만 반환합니다.\n\n" + "\n\n---\n\n".join(
                f"**[{s['section_type']}]** (p.{s['page']})\n{s['content'][:300]}"
                for s in sources
            )
            yield f"event: token\ndata: {json.dumps({'token': answer}, ensure_ascii=False)}\n\n"
            yield f"event: done\ndata: {json.dumps({'full_answer': answer}, ensure_ascii=False)}\n\n"
            return

        # 3. 스트리밍 생성
        context = "\n\n".join(doc["content"] for doc in reranked[:5])
        full_answer = ""

        try:
            for token_text in m.generator.generate_stream(
                query=req.query,
                context=context,
            ):
                full_answer += token_text
                yield f"event: token\ndata: {json.dumps({'token': token_text}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)  # yield control to event loop
        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
            if not full_answer:
                full_answer = f"생성 중 오류가 발생했습니다: {str(e)}"
                yield f"event: token\ndata: {json.dumps({'token': full_answer}, ensure_ascii=False)}\n\n"

        yield f"event: done\ndata: {json.dumps({'full_answer': full_answer}, ensure_ascii=False)}\n\n"

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
    m: ModuleManager = Depends(get_modules),
):
    """생성 없이 검색만 수행 (디버깅, 프론트엔드용)"""

    results = m.hybrid_retriever.search(
        collection_name=req.collection_name,
        query=req.query,
        top_k=req.top_k,
        section_filter=req.section_filter,
        doc_id_filter=req.doc_id_filter,
    )

    reranked = m.reranker.rerank(req.query, results, top_k=req.top_k)

    sources = [
        SourceDocument(
            chunk_id=doc.get("chunk_id", ""),
            content=doc["content"],
            section_type=doc.get("metadata", {}).get("section_type", "unknown"),
            doc_id=doc.get("metadata", {}).get("doc_id", ""),
            page=doc.get("metadata", {}).get("page", 0),
            score=doc.get("rerank_score", 0.0),
        )
        for doc in reranked
    ]

    return SearchResponse(
        results=sources,
        total=len(sources),
        bm25_fitted=m.hybrid_retriever._bm25_fitted,
    )


def _run_pipeline(decision, req, m, available_docs, papers) -> dict:
    """라우터 결정에 따라 파이프라인 실행"""
    from pipelines import (
        pipeline_a_simple_qa,
        pipeline_b_section,
        pipeline_c_compare,
        pipeline_e_summary,
    )
    from modules.section_detector import SectionDetector

    col = req.collection_name
    hr = m.hybrid_retriever
    rr = m.reranker
    comp = m.compressor
    gen = m.generator
    qe = m.query_expander

    if decision.route == RouteType.SECTION:
        return pipeline_b_section.run(
            req.query, col, decision.section_filter,
            hr, rr, comp, gen,
            req.use_cad, req.cad_alpha, req.use_scd, req.scd_beta,
        )
    elif decision.route == RouteType.COMPARE:
        return pipeline_c_compare.run(
            req.query, col, decision.target_doc_ids,
            hr, rr, comp, gen,
            req.use_cad, req.cad_alpha, req.use_scd, req.scd_beta,
        )
    elif decision.route == RouteType.CITATION:
        doc = papers[available_docs[0]]
        from modules.pdf_parser import PDFParser
        from modules.chunker import Chunker
        from pipelines import pipeline_d_citation
        return pipeline_d_citation.run(
            req.query, col, doc, hr, rr, comp, gen,
            m.citation_tracker, m.embedder, m.vector_store,
            SectionDetector(), PDFParser(), Chunker(),
            str(DATA_DIR),
            req.use_cad, req.cad_alpha, req.use_scd, req.scd_beta,
        )
    elif decision.route == RouteType.SUMMARY:
        return pipeline_e_summary.run(
            req.query, col, hr, rr, comp, gen,
            req.use_cad, req.cad_alpha, req.use_scd, req.scd_beta,
        )
    else:
        return pipeline_a_simple_qa.run(
            req.query, col, hr, rr, comp, gen, qe,
            req.use_cad, req.cad_alpha, req.use_scd, req.scd_beta,
        )
