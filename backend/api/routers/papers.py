"""
/api/papers - document upload and metadata management
"""
import logging
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import delete, select

from api.auth import get_current_user_id
from api.database import get_db
from api.dependencies import ModuleManager, get_modules
from api.limiter import limiter
from api.models import Paper
from api.schemas import CollectionInfo, CollectionListResponse, PaperInfo, UploadResponse
from config import DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/papers", tags=["papers"])

MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_DOC_TYPES = {"paper", "lecture", "patent"}


def _is_text_like(data: bytes) -> bool:
    if not data:
        return True
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _detect_mime_type(content: bytes) -> str:
    try:
        import magic  # type: ignore

        detected = magic.from_buffer(content[:4096], mime=True)
        if detected:
            return str(detected)
    except Exception:
        pass

    if content.startswith(b"%PDF-"):
        return "application/pdf"
    if content.startswith(b"PK\x03\x04"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if _is_text_like(content[:4096]):
        return "text/plain"
    return "application/octet-stream"


def _validate_upload_signature(ext: str, content: bytes) -> None:
    detected_mime = _detect_mime_type(content)
    if ext == ".pdf":
        if not content.startswith(b"%PDF-") or detected_mime not in {"application/pdf"}:
            raise HTTPException(400, "PDF 파일 형식이 올바르지 않습니다.")
    elif ext == ".docx":
        allowed = {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/zip",
        }
        if not content.startswith(b"PK\x03\x04") or detected_mime not in allowed:
            raise HTTPException(400, "DOCX 파일 형식이 올바르지 않습니다.")
    elif ext == ".txt":
        if detected_mime not in {"text/plain", "text/markdown", "application/octet-stream"}:
            raise HTTPException(400, "TXT 파일 형식이 올바르지 않습니다.")
        if not _is_text_like(content[:4096]):
            raise HTTPException(400, "텍스트 파일 검증에 실패했습니다.")


def namespace_collection_name(user_id: str, collection_name: str) -> str:
    """Namespace collection name per user for multi-tenant isolation."""
    base = (collection_name or "papers").strip()
    return f"{user_id}__{base}"


def _serialize_document(document) -> dict:
    return {
        "doc_id": document.doc_id,
        "title": document.title,
        "total_pages": document.total_pages,
        "metadata": document.metadata,
        "blocks": [asdict(block) for block in document.blocks],
    }


def _deserialize_document(document_json: dict):
    from modules.pdf_parser import ParsedDocument, TextBlock

    blocks = [TextBlock(**block_data) for block_data in document_json.get("blocks", [])]
    return ParsedDocument(
        doc_id=document_json["doc_id"],
        title=document_json["title"],
        total_pages=document_json.get("total_pages", 0),
        metadata=document_json.get("metadata", {}),
        blocks=blocks,
    )


async def get_papers(db, user_id: str, collection_name: str | None = None):
    if db is None:
        return {}

    stmt = select(Paper).where(Paper.user_id == user_id)
    if collection_name:
        namespaced = namespace_collection_name(user_id, collection_name)
        stmt = stmt.where(Paper.collection_name == namespaced)

    result = await db.execute(stmt.order_by(Paper.created_at.desc()))
    papers = result.scalars().all()
    return {
        paper.doc_id: _deserialize_document(paper.document_json)
        for paper in papers
        if paper.document_json
    }


@router.post("/upload", response_model=UploadResponse)
@limiter.limit("5/minute")
async def upload_paper(
    request: Request,
    file: UploadFile = File(...),
    collection_name: str = "papers",
    doc_type: str = "paper",
    user_id: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
    db=Depends(get_db),
):
    """Upload, parse, chunk, index, and persist a document."""
    if db is None:
        raise HTTPException(503, "Database not available")
    if not file.filename:
        raise HTTPException(400, "Filename is required.")

    internal_collection_name = namespace_collection_name(user_id, collection_name)

    safe_filename = Path(file.filename).name
    ext = Path(safe_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(400, f"Unsupported file type. Allowed: {allowed}")
    if doc_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(400, "doc_type must be one of: paper, lecture, patent")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(413, "File too large. Maximum supported size is 50MB.")
    _validate_upload_signature(ext, content)

    user_data_dir = DATA_DIR / user_id
    user_data_dir.mkdir(parents=True, exist_ok=True)

    temp_path = user_data_dir / f".upload_{uuid4().hex}{ext}"
    final_path = user_data_dir / safe_filename

    document = None
    chunks = []
    vector_added = False
    try:
        temp_path.write_bytes(content)

        if ext == ".pdf":
            document = m.pdf_parser.parse(temp_path)
            document = m.section_detector.detect(document)
        elif ext == ".docx":
            from modules.docx_parser import DocxParser
            from modules.pdf_parser import ParsedDocument, TextBlock

            parsed = DocxParser().parse(str(temp_path))
            blocks = [
                TextBlock(
                    content=block["text"],
                    page=block["page"],
                    font_size=block["font_size"],
                    bbox=tuple(block["bbox"]),
                    is_bold=block.get("is_bold", False),
                )
                for block in parsed["blocks"]
            ]
            doc_id = Path(safe_filename).stem.replace(" ", "_").lower()
            document = ParsedDocument(
                doc_id=doc_id,
                title=parsed["title"],
                total_pages=parsed["total_pages"],
                blocks=blocks,
            )
            document = m.section_detector.detect(document)
        else:
            from modules.docx_parser import TextFileParser
            from modules.pdf_parser import ParsedDocument, TextBlock

            parsed = TextFileParser().parse(str(temp_path))
            blocks = [
                TextBlock(
                    content=block["text"],
                    page=block["page"],
                    font_size=block["font_size"],
                    bbox=tuple(block["bbox"]),
                    is_bold=block.get("is_bold", False),
                )
                for block in parsed["blocks"]
            ]
            doc_id = Path(safe_filename).stem.replace(" ", "_").lower()
            document = ParsedDocument(
                doc_id=doc_id,
                title=parsed["title"],
                total_pages=parsed["total_pages"],
                blocks=blocks,
            )
            document = m.section_detector.detect(document)

        chunks = m.chunker.chunk_document(document, strategy="section")
        if not chunks:
            raise HTTPException(400, "Document parsing produced no chunks.")

        # Re-upload safety: remove old chunks for same document before adding new ones.
        m.vector_store.delete_by_doc_id(internal_collection_name, document.doc_id)

        embeddings = m.embedder.embed_texts([chunk.content for chunk in chunks])
        m.vector_store.add_chunks(internal_collection_name, chunks, embeddings)
        vector_added = True
        m.hybrid_retriever.fit_bm25(internal_collection_name)

        section_summary = m.section_detector.get_section_summary(document)
        serialized_document = _serialize_document(document)

        result = await db.execute(
            select(Paper).where(
                Paper.doc_id == document.doc_id,
                Paper.user_id == user_id,
                Paper.collection_name == internal_collection_name,
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            record = Paper(
                user_id=user_id,
                doc_id=document.doc_id,
                title=document.title,
                collection_name=internal_collection_name,
                doc_type=doc_type,
                file_name=safe_filename,
                file_path=str(final_path),
                file_type=ext.lstrip("."),
                total_pages=document.total_pages,
                num_chunks=len(chunks),
                sections_json=section_summary,
                document_json=serialized_document,
            )
            db.add(record)
        else:
            record.title = document.title
            record.collection_name = internal_collection_name
            record.doc_type = doc_type
            record.file_name = safe_filename
            record.file_path = str(final_path)
            record.file_type = ext.lstrip(".")
            record.total_pages = document.total_pages
            record.num_chunks = len(chunks)
            record.sections_json = section_summary
            record.document_json = serialized_document

        await db.commit()
        temp_path.replace(final_path)

        return UploadResponse(
            success=True,
            paper=PaperInfo(
                doc_id=document.doc_id,
                title=document.title,
                total_pages=document.total_pages,
                num_chunks=len(chunks),
                sections=section_summary,
            ),
            message=f"Indexed {len(chunks)} chunks successfully.",
        )
    except HTTPException:
        await db.rollback()
        if vector_added and document is not None:
            m.vector_store.delete_by_doc_id(internal_collection_name, document.doc_id)
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        await db.rollback()
        if vector_added and document is not None:
            m.vector_store.delete_by_doc_id(internal_collection_name, document.doc_id)
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        logger.error("Document processing failed: %s", exc, exc_info=True)
        raise HTTPException(500, "Document processing failed.")


@router.get("/list", response_model=CollectionListResponse)
async def list_collections(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Return user-owned persisted paper metadata for the UI document list."""
    if db is None:
        raise HTTPException(503, "Database not available")

    result = await db.execute(
        select(Paper)
        .where(Paper.user_id == user_id)
        .order_by(Paper.created_at.desc())
    )
    papers = result.scalars().all()
    collections = [
        CollectionInfo(
            name=paper.doc_id,
            count=paper.num_chunks,
            doc_ids=[paper.doc_id],
        )
        for paper in papers
    ]
    return CollectionListResponse(collections=collections)


@router.get("/{doc_id}")
async def get_paper_info(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Return stored metadata for a user-owned document."""
    if db is None:
        raise HTTPException(503, "Database not available")

    result = await db.execute(
        select(Paper).where(
            Paper.doc_id == doc_id,
            Paper.user_id == user_id,
        )
    )
    paper = result.scalar_one_or_none()
    if paper is None:
        raise HTTPException(404, "Paper not found.")

    document = _deserialize_document(paper.document_json)
    return {
        "doc_id": document.doc_id,
        "title": document.title,
        "total_pages": document.total_pages,
        "num_blocks": document.metadata.get("num_blocks", 0),
        "sections": paper.sections_json or {},
    }


@router.delete("/{collection_name}")
async def delete_collection(
    collection_name: str,
    user_id: str = Depends(get_current_user_id),
    m: ModuleManager = Depends(get_modules),
    db=Depends(get_db),
):
    """Delete user-owned documents in a collection and related resources."""
    if db is None:
        raise HTTPException(503, "Database not available")

    internal_collection_name = namespace_collection_name(user_id, collection_name)

    result = await db.execute(
        select(Paper).where(
            Paper.collection_name == internal_collection_name,
            Paper.user_id == user_id,
        )
    )
    papers = result.scalars().all()
    if not papers:
        raise HTTPException(404, "Collection not found.")

    for paper in papers:
        if paper.file_path:
            try:
                Path(paper.file_path).unlink(missing_ok=True)
            except Exception:
                logger.warning("Failed to remove file during collection delete: %s", paper.file_path)
        m.vector_store.delete_by_doc_id(internal_collection_name, paper.doc_id)

    await db.execute(
        delete(Paper).where(
            Paper.collection_name == internal_collection_name,
            Paper.user_id == user_id,
        )
    )
    await db.commit()

    try:
        remaining_doc_ids = m.vector_store.get_all_doc_ids(internal_collection_name)
        if not remaining_doc_ids:
            m.vector_store.delete_collection(internal_collection_name)
    except Exception:
        logger.warning("Failed to evaluate empty collection cleanup: %s", internal_collection_name)

    try:
        m.hybrid_retriever.fit_bm25(internal_collection_name)
    except Exception:
        logger.warning("BM25 rebuild failed after collection delete: %s", internal_collection_name)

    return {"message": "Collection deleted successfully."}
