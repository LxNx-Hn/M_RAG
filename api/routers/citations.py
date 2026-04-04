"""
/api/citations — 인용 논문 추적
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import ModuleManager, get_modules
from api.schemas import CitationRequest, CitationResponse, CitationItem
from api.routers.papers import get_papers

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/citations", tags=["citations"])


@router.post("/track", response_model=CitationResponse)
async def track_citations(
    req: CitationRequest,
    m: ModuleManager = Depends(get_modules),
):
    """논문의 Reference 파싱 → arXiv API 수집"""

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
    citation_items = [
        CitationItem(
            ref_id=c.ref_id,
            title=c.title,
            authors=", ".join(c.authors[:3]),
            year=c.year,
            arxiv_id=c.arxiv_id,
            fetched=c.fetched,
            has_pdf=c.pdf_url is not None,
        )
        for c in citations
    ]

    return CitationResponse(
        citations=citation_items,
        fetched_count=len(fetched),
        indexed_count=indexed,
    )
