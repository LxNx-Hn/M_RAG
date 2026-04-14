"""
/api/citations - citation paper tracking
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user_id
from api.database import get_db
from api.dependencies import ModuleManager, get_modules
from api.routers.papers import get_papers, namespace_collection_name
from api.schemas import (
    CitationDownloadRequest,
    CitationDownloadResponse,
    CitationItem,
    CitationListRequest,
    CitationRequest,
    CitationResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/citations", tags=["citations"])


def _build_citation_item(citation) -> CitationItem:
    return CitationItem(
        ref_id=citation.ref_id,
        title=citation.title,
        authors=", ".join(citation.authors[:3]),
        year=citation.year,
        arxiv_id=citation.arxiv_id,
        fetched=citation.fetched,
        has_pdf=citation.pdf_url is not None,
        fetch_error=citation.fetch_error,
    )


def _extract_reference_text(m: ModuleManager, doc) -> str:
    ref_text = m.section_detector.get_section_text(doc, "references")
    if not ref_text:
        ref_text = "\n".join(
            block.content for block in doc.blocks if "reference" in block.content.lower()[:50]
        )
    return ref_text


@router.post("/list", response_model=CitationResponse)
async def list_citations(
    req: CitationListRequest,
    user_id: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
    db=Depends(get_db),
):
    """Parse references and fetch arXiv metadata only."""
    papers = await get_papers(db, user_id, req.collection_name)
    if req.doc_id not in papers:
        raise HTTPException(404, "Paper not found.")

    doc = papers[req.doc_id]
    ref_text = _extract_reference_text(m, doc)
    if not ref_text:
        return CitationResponse(citations=[], fetched_count=0, indexed_count=0)

    citations = m.citation_tracker.parse_references(ref_text)
    fetched = m.citation_tracker.fetch_all_citations(max_total=len(citations), delay=1.0)
    items = [_build_citation_item(c) for c in citations]
    return CitationResponse(citations=items, fetched_count=len(fetched), indexed_count=0)


@router.post("/download", response_model=CitationDownloadResponse)
async def download_citation(
    req: CitationDownloadRequest,
    user_id: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
    db=Depends(get_db),
):
    """Download and index a single citation PDF."""
    internal_collection_name = namespace_collection_name(user_id, req.collection_name)
    papers = await get_papers(db, user_id, req.collection_name)
    if req.doc_id not in papers:
        raise HTTPException(404, "Paper not found.")

    doc = papers[req.doc_id]
    ref_text = _extract_reference_text(m, doc)
    if not ref_text:
        raise HTTPException(400, "No reference section found in the selected paper.")

    citations = m.citation_tracker.parse_references(ref_text)
    m.citation_tracker.fetch_all_citations(max_total=len(citations), delay=1.0)

    if req.citation_index >= len(citations):
        raise HTTPException(400, "Citation index out of range.")

    citation = citations[req.citation_index]
    if not citation.pdf_url:
        message = "No downloadable PDF URL. Please upload the paper manually."
        if citation.fetch_error:
            message = f"{citation.fetch_error} - upload manually."
        return CitationDownloadResponse(
            success=False,
            citation=_build_citation_item(citation),
            indexed=False,
            message=message,
        )

    pdf_path = m.citation_tracker.download_pdf(citation, "data")
    if not pdf_path:
        return CitationDownloadResponse(
            success=False,
            citation=_build_citation_item(citation),
            indexed=False,
            message="PDF download failed.",
        )

    indexed = False
    try:
        parsed = m.pdf_parser.parse(pdf_path)
        parsed = m.section_detector.detect(parsed)
        chunks = m.chunker.chunk_document(parsed, strategy="section")
        if chunks:
            embeddings = m.embedder.embed_texts([chunk.content for chunk in chunks])
            m.vector_store.add_chunks(internal_collection_name, chunks, embeddings)
            m.hybrid_retriever.fit_bm25(internal_collection_name)
            indexed = True
    except Exception as exc:
        logger.warning("Citation indexing failed: %s", exc)
        return CitationDownloadResponse(
            success=True,
            citation=_build_citation_item(citation),
            indexed=False,
            message="PDF downloaded but indexing failed.",
        )

    return CitationDownloadResponse(
        success=True,
        citation=_build_citation_item(citation),
        indexed=indexed,
        message="Downloaded and indexed." if indexed else "Downloaded without chunks.",
    )


@router.post("/track", response_model=CitationResponse)
async def track_citations(
    req: CitationRequest,
    user_id: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
    db=Depends(get_db),
):
    """Parse references, fetch arXiv papers, and index fetched PDFs."""
    internal_collection_name = namespace_collection_name(user_id, req.collection_name)
    papers = await get_papers(db, user_id, req.collection_name)
    if req.doc_id not in papers:
        raise HTTPException(404, "Paper not found.")

    doc = papers[req.doc_id]
    ref_text = _extract_reference_text(m, doc)
    if not ref_text:
        return CitationResponse(citations=[], fetched_count=0, indexed_count=0)

    citations = m.citation_tracker.parse_references(ref_text)
    fetched = m.citation_tracker.fetch_all_citations(max_total=req.max_citations, delay=1.0)

    indexed = 0
    for citation in fetched:
        if not citation.pdf_url:
            continue
        pdf_path = m.citation_tracker.download_pdf(citation, "data")
        if not pdf_path:
            continue
        try:
            parsed = m.pdf_parser.parse(pdf_path)
            parsed = m.section_detector.detect(parsed)
            chunks = m.chunker.chunk_document(parsed, strategy="section")
            if chunks:
                embeddings = m.embedder.embed_texts([chunk.content for chunk in chunks])
                m.vector_store.add_chunks(internal_collection_name, chunks, embeddings)
                indexed += 1
        except Exception as exc:
            logger.warning("Citation indexing failed: %s", exc)

    if indexed > 0:
        m.hybrid_retriever.fit_bm25(internal_collection_name)

    items = [_build_citation_item(c) for c in citations]
    return CitationResponse(citations=items, fetched_count=len(fetched), indexed_count=indexed)
