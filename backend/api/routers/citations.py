"""
/api/citations — 인용 논문 추적
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import ModuleManager, get_modules
from api.schemas import (
    CitationRequest, CitationResponse, CitationItem,
    CitationListRequest, CitationDownloadRequest, CitationDownloadResponse,
)
from api.routers.papers import get_papers

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/citations", tags=["citations"])


def _build_citation_item(c) -> CitationItem:
    """CitationInfo → CitationItem 변환 헬퍼"""
    return CitationItem(
        ref_id=c.ref_id,
        title=c.title,
        authors=", ".join(c.authors[:3]),
        year=c.year,
        arxiv_id=c.arxiv_id,
        fetched=c.fetched,
        has_pdf=c.pdf_url is not None,
        fetch_error=c.fetch_error,
    )


@router.post("/list", response_model=CitationResponse)
async def list_citations(
    req: CitationListRequest,
    m: ModuleManager = Depends(get_modules),
):
    """Reference 파싱 + arXiv 메타데이터 조회 (PDF 다운로드 없음)"""

    papers = get_papers()
    if req.doc_id not in papers:
        raise HTTPException(404, f"논문 '{req.doc_id}'을 찾을 수 없습니다.")

    doc = papers[req.doc_id]

    # Reference 섹션 추출
    ref_text = m.section_detector.get_section_text(doc, "references")
    if not ref_text:
        ref_text = "\n".join(
            b.content for b in doc.blocks
            if "reference" in b.content.lower()[:50]
        )

    if not ref_text:
        return CitationResponse(citations=[], fetched_count=0, indexed_count=0)

    # 파싱
    citations = m.citation_tracker.parse_references(ref_text)

    # arXiv 메타데이터만 수집 (PDF 다운로드 X)
    fetched = m.citation_tracker.fetch_all_citations(
        max_total=len(citations), delay=1.0
    )

    citation_items = [_build_citation_item(c) for c in citations]

    return CitationResponse(
        citations=citation_items,
        fetched_count=len(fetched),
        indexed_count=0,
    )


@router.post("/download", response_model=CitationDownloadResponse)
async def download_citation(
    req: CitationDownloadRequest,
    m: ModuleManager = Depends(get_modules),
):
    """단일 인용 논문 PDF 다운로드 + 인덱싱"""

    if req.citation_index >= len(m.citation_tracker.citations):
        raise HTTPException(
            400,
            f"인용 인덱스 {req.citation_index}이 범위를 벗어났습니다. "
            f"먼저 /api/citations/list를 호출하세요.",
        )

    citation = m.citation_tracker.citations[req.citation_index]

    if not citation.pdf_url:
        error_msg = "arXiv 미등록 — PDF 직접 업로드 필요"
        if citation.fetch_error:
            error_msg = f"{citation.fetch_error} — PDF 직접 업로드 필요"
        return CitationDownloadResponse(
            success=False,
            citation=_build_citation_item(citation),
            indexed=False,
            message=error_msg,
        )

    # PDF 다운로드
    pdf_path = m.citation_tracker.download_pdf(citation, "data")
    if not pdf_path:
        return CitationDownloadResponse(
            success=False,
            citation=_build_citation_item(citation),
            indexed=False,
            message="PDF 다운로드 실패",
        )

    # 인덱싱
    indexed = False
    try:
        parsed = m.pdf_parser.parse(pdf_path)
        parsed = m.section_detector.detect(parsed)
        chunks = m.chunker.chunk_document(parsed, strategy="section")
        if chunks:
            embeddings = m.embedder.embed_texts([c.content for c in chunks])
            m.vector_store.add_chunks(req.collection_name, chunks, embeddings)
            m.hybrid_retriever.fit_bm25(req.collection_name)
            indexed = True
    except Exception as e:
        logger.warning(f"Citation indexing failed: {e}")
        return CitationDownloadResponse(
            success=True,
            citation=_build_citation_item(citation),
            indexed=False,
            message=f"PDF 다운로드 성공, 인덱싱 실패: {e}",
        )

    return CitationDownloadResponse(
        success=True,
        citation=_build_citation_item(citation),
        indexed=indexed,
        message="다운로드 + 인덱싱 완료" if indexed else "다운로드 완료 (청크 없음)",
    )


@router.post("/track", response_model=CitationResponse)
async def track_citations(
    req: CitationRequest,
    m: ModuleManager = Depends(get_modules),
):
    """논문의 Reference 파싱 → arXiv API 수집 (기존 호환)"""

    papers = get_papers()
    if req.doc_id not in papers:
        raise HTTPException(404, f"논문 '{req.doc_id}'을 찾을 수 없습니다.")

    doc = papers[req.doc_id]

    # Reference 섹션 추출
    ref_text = m.section_detector.get_section_text(doc, "references")
    if not ref_text:
        ref_text = "\n".join(
            b.content for b in doc.blocks
            if "reference" in b.content.lower()[:50]
        )

    if not ref_text:
        return CitationResponse(citations=[], fetched_count=0, indexed_count=0)

    # 파싱
    citations = m.citation_tracker.parse_references(ref_text)

    # arXiv API 수집
    fetched = m.citation_tracker.fetch_all_citations(
        max_total=req.max_citations, delay=1.0
    )

    # 수집된 논문 인덱싱
    indexed = 0
    for citation in fetched:
        if citation.pdf_url:
            pdf_path = m.citation_tracker.download_pdf(citation, "data")
            if pdf_path:
                try:
                    parsed = m.pdf_parser.parse(pdf_path)
                    parsed = m.section_detector.detect(parsed)
                    chunks = m.chunker.chunk_document(parsed, strategy="section")
                    if chunks:
                        embeddings = m.embedder.embed_texts([c.content for c in chunks])
                        m.vector_store.add_chunks(req.collection_name, chunks, embeddings)
                        indexed += 1
                except Exception as e:
                    logger.warning(f"Citation indexing failed: {e}")

    if indexed > 0:
        m.hybrid_retriever.fit_bm25(req.collection_name)

    # 응답
    citation_items = [_build_citation_item(c) for c in citations]

    return CitationResponse(
        citations=citation_items,
        fetched_count=len(fetched),
        indexed_count=indexed,
    )
