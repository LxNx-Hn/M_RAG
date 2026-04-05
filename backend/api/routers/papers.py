"""
/api/papers — PDF 업로드 및 논문 관리
"""
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

from config import DATA_DIR
from api.dependencies import ModuleManager, get_modules
from api.schemas import UploadResponse, PaperInfo, CollectionListResponse, CollectionInfo

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/papers", tags=["papers"])

# 인메모리 논문 저장소 (프로세스 수명 동안 유지)
_papers: dict = {}


def get_papers():
    return _papers


@router.post("/upload", response_model=UploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    collection_name: str = "papers",
    m: ModuleManager = Depends(get_modules),
):
    """PDF/DOCX/TXT/MD 업로드 → 파싱 → 섹션 인식 → 청킹 → 임베딩 → 벡터DB 저장"""

    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
    if not file.filename:
        raise HTTPException(400, "파일명이 없습니다.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"지원하는 파일: {', '.join(ALLOWED_EXTENSIONS)}")

    # 파일 저장
    pdf_path = DATA_DIR / file.filename
    content = await file.read()
    pdf_path.write_bytes(content)

    try:
        # 파일 타입별 파싱
        if ext == ".pdf":
            document = m.pdf_parser.parse(pdf_path)
            document = m.section_detector.detect(document)
        elif ext == ".docx":
            from modules.docx_parser import DocxParser
            parsed = DocxParser().parse(str(pdf_path))
            # ParsedDocument 호환 래퍼
            from modules.pdf_parser import ParsedDocument, TextBlock
            blocks = [
                TextBlock(
                    content=b["text"], page=b["page"],
                    font_size=b["font_size"], bbox=tuple(b["bbox"]),
                    is_bold=b.get("is_bold", False),
                )
                for b in parsed["blocks"]
            ]
            doc_id = Path(file.filename).stem.replace(" ", "_").lower()
            document = ParsedDocument(
                doc_id=doc_id,
                title=parsed["title"],
                total_pages=parsed["total_pages"],
                blocks=blocks,
            )
            document = m.section_detector.detect(document)
        else:
            from modules.docx_parser import TextFileParser
            parsed = TextFileParser().parse(str(pdf_path))
            from modules.pdf_parser import ParsedDocument, TextBlock
            blocks = [
                TextBlock(
                    content=b["text"], page=b["page"],
                    font_size=b["font_size"], bbox=tuple(b["bbox"]),
                    is_bold=b.get("is_bold", False),
                )
                for b in parsed["blocks"]
            ]
            doc_id = Path(file.filename).stem.replace(" ", "_").lower()
            document = ParsedDocument(
                doc_id=doc_id,
                title=parsed["title"],
                total_pages=parsed["total_pages"],
                blocks=blocks,
            )
            document = m.section_detector.detect(document)

        # 청킹
        chunks = m.chunker.chunk_document(document, strategy="section")
        if not chunks:
            return UploadResponse(success=False, message="청크 생성 실패 (빈 문서일 수 있음)")

        # 임베딩 + 인덱싱
        embeddings = m.embedder.embed_texts([c.content for c in chunks])
        m.vector_store.add_chunks(collection_name, chunks, embeddings)

        # BM25 인덱스 재구축
        m.hybrid_retriever.fit_bm25(collection_name)

        # 인메모리 저장
        _papers[document.doc_id] = document

        section_summary = m.section_detector.get_section_summary(document)

        return UploadResponse(
            success=True,
            paper=PaperInfo(
                doc_id=document.doc_id,
                title=document.title,
                total_pages=document.total_pages,
                num_chunks=len(chunks),
                sections=section_summary,
            ),
            message=f"{len(chunks)}개 청크 인덱싱 완료",
        )

    except Exception as e:
        logger.error(f"PDF processing failed: {e}", exc_info=True)
        raise HTTPException(500, f"PDF 처리 실패: {str(e)}")


@router.get("/list", response_model=CollectionListResponse)
async def list_collections(m: ModuleManager = Depends(get_modules)):
    """벡터DB 컬렉션 목록"""
    names = m.vector_store.list_collections()
    collections = []
    for name in names:
        info = m.vector_store.get_collection_info(name)
        doc_ids = m.vector_store.get_all_doc_ids(name)
        collections.append(CollectionInfo(
            name=name,
            count=info.get("count", 0),
            doc_ids=doc_ids,
        ))
    return CollectionListResponse(collections=collections)


@router.get("/{doc_id}")
async def get_paper_info(doc_id: str):
    """논문 메타데이터 조회"""
    if doc_id not in _papers:
        raise HTTPException(404, f"논문 '{doc_id}'을 찾을 수 없습니다.")
    doc = _papers[doc_id]
    from modules.section_detector import SectionDetector
    summary = SectionDetector().get_section_summary(doc)
    return {
        "doc_id": doc.doc_id,
        "title": doc.title,
        "total_pages": doc.total_pages,
        "num_blocks": doc.metadata.get("num_blocks", 0),
        "sections": summary,
    }


@router.delete("/{collection_name}")
async def delete_collection(
    collection_name: str,
    m: ModuleManager = Depends(get_modules),
):
    """컬렉션 삭제"""
    m.vector_store.delete_collection(collection_name)
    return {"message": f"컬렉션 '{collection_name}' 삭제 완료"}
