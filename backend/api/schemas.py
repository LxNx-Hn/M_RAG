"""
FastAPI 요청/응답 스키마 (Pydantic v2)
"""
from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────
# 공통
# ─────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"
    modules_loaded: bool = False
    gpu_available: bool = False
    collections: list[str] = []


# ─────────────────────────────────────────
# PDF 업로드
# ─────────────────────────────────────────
class PaperInfo(BaseModel):
    doc_id: str
    title: str
    total_pages: int
    num_chunks: int
    sections: dict[str, int]  # {section_type: block_count}


class UploadResponse(BaseModel):
    success: bool
    paper: Optional[PaperInfo] = None
    message: str = ""


# ─────────────────────────────────────────
# 질의응답
# ─────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="질의 텍스트")
    collection_name: str = Field(default="papers", description="검색 컬렉션 이름")
    # MODULE 13A: CAD (파라메트릭 지식 개입 억제)
    use_cad: bool = Field(default=True, description="CAD 환각 억제 사용 여부")
    cad_alpha: float = Field(default=0.5, ge=0.0, le=1.0, description="CAD 억제 강도 (Table 2 ablation)")
    # MODULE 13B: SCD (Language Drift 억제)
    use_scd: bool = Field(default=True, description="SCD Language Drift 억제 사용 여부")
    scd_beta: float = Field(default=0.3, ge=0.0, le=1.0, description="SCD 패널티 강도 (Table 2 ablation)")
    use_hyde: bool = Field(default=True, description="HyDE 쿼리 확장 사용 여부")
    top_k: int = Field(default=5, ge=1, le=20, description="최종 반환 문서 수")


class SourceDocument(BaseModel):
    chunk_id: str
    content: str
    section_type: str = "unknown"
    doc_id: str = ""
    page: int = 0
    score: float = 0.0


class RouteInfo(BaseModel):
    route: str            # A, B, C, D, E, F
    route_name: str       # 한국어 설명
    section_filter: Optional[str] = None
    confidence: float = 0.0


class QueryResponse(BaseModel):
    answer: str
    route: RouteInfo
    sources: list[SourceDocument] = []
    steps: list[dict] = []
    pipeline: str = ""
    follow_ups: list[str] = []


# ─────────────────────────────────────────
# 검색 전용 (생성 없이)
# ─────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    collection_name: str = "papers"
    section_filter: Optional[str] = None
    doc_id_filter: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResponse(BaseModel):
    results: list[SourceDocument] = []
    total: int = 0
    bm25_fitted: bool = False


# ─────────────────────────────────────────
# 컬렉션 관리
# ─────────────────────────────────────────
class CollectionInfo(BaseModel):
    name: str
    count: int
    doc_ids: list[str] = []


class CollectionListResponse(BaseModel):
    collections: list[CollectionInfo] = []


# ─────────────────────────────────────────
# 인용 추적
# ─────────────────────────────────────────
class CitationRequest(BaseModel):
    doc_id: str
    collection_name: str = "papers"
    max_citations: int = Field(default=5, ge=1, le=20)


class CitationItem(BaseModel):
    ref_id: str
    title: str
    authors: str = ""
    year: Optional[str] = None
    arxiv_id: Optional[str] = None
    fetched: bool = False
    has_pdf: bool = False
    fetch_error: Optional[str] = None


class CitationResponse(BaseModel):
    citations: list[CitationItem] = []
    fetched_count: int = 0
    indexed_count: int = 0


class CitationListRequest(BaseModel):
    doc_id: str
    collection_name: str = "papers"


class CitationDownloadRequest(BaseModel):
    doc_id: str
    citation_index: int = Field(..., ge=0, description="인용 목록 내 인덱스")
    collection_name: str = "papers"


class CitationDownloadResponse(BaseModel):
    success: bool
    citation: Optional[CitationItem] = None
    indexed: bool = False
    message: str = ""


# ─────────────────────────────────────────
# PPT 내보내기
# ─────────────────────────────────────────
class PPTExportRequest(BaseModel):
    answer: str = Field(..., min_length=1, description="요약 답변 텍스트")
    title: str = Field(default="M-RAG Summary", description="PPT 타이틀")
    subtitle: str = Field(default="", description="서브타이틀")
