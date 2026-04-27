"""Pydantic schemas for FastAPI request/response payloads."""

from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    modules_loaded: bool = False
    gpu_available: bool = False
    collections: list[str] = []
    database_connected: bool = False
    chroma_connected: bool = False
    generator_loaded: bool = False
    embedder_loaded: bool = False


class PaperInfo(BaseModel):
    doc_id: str
    title: str
    total_pages: int
    num_chunks: int
    sections: dict[str, int]


class UploadResponse(BaseModel):
    success: bool
    paper: Optional[PaperInfo] = None
    message: str = ""


class QueryRequest(BaseModel):
    query: str = Field(
        ..., min_length=1, max_length=2000, description="User question text"
    )
    collection_name: str = Field(default="papers", min_length=1, max_length=100)
    use_cad: bool = Field(default=True, description="Enable CAD decoding")
    cad_alpha: float = Field(default=0.5, ge=0.0, le=1.0)
    use_scd: bool = Field(default=True, description="Enable SCD decoding")
    scd_beta: float = Field(default=0.3, ge=0.0, le=1.0)
    use_hyde: bool = Field(default=True, description="Enable HyDE query expansion")
    top_k: int = Field(default=5, ge=1, le=20)


class SourceDocument(BaseModel):
    chunk_id: str
    content: str
    section_type: str = "unknown"
    doc_id: str = ""
    page: int = 0
    score: float = 0.0


class RouteInfo(BaseModel):
    route: str
    route_name: str
    section_filter: Optional[str] = None
    confidence: float = 0.0


class QueryResponse(BaseModel):
    answer: str
    route: RouteInfo
    sources: list[SourceDocument] = []
    steps: list[dict] = []
    pipeline: str = ""
    follow_ups: list[str] = []


class JudgeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=12000)
    max_new_tokens: int = Field(default=64, ge=1, le=256)
    labels: Optional[list[str]] = Field(default=None, max_length=8)


class JudgeResponse(BaseModel):
    text: str
    scores: Optional[dict[str, float]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    collection_name: str = Field(default="papers", min_length=1, max_length=100)
    section_filter: Optional[str] = Field(default=None, max_length=100)
    doc_id_filter: Optional[str] = Field(default=None, max_length=255)
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResponse(BaseModel):
    results: list[SourceDocument] = []
    total: int = 0
    bm25_fitted: bool = False


class CollectionInfo(BaseModel):
    name: str
    count: int
    doc_ids: list[str] = []


class CollectionListResponse(BaseModel):
    collections: list[CollectionInfo] = []


class CitationRequest(BaseModel):
    doc_id: str = Field(..., min_length=1, max_length=255)
    collection_name: str = Field(default="papers", min_length=1, max_length=100)
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
    doc_id: str = Field(..., min_length=1, max_length=255)
    collection_name: str = Field(default="papers", min_length=1, max_length=100)


class CitationDownloadRequest(BaseModel):
    doc_id: str = Field(..., min_length=1, max_length=255)
    citation_index: int = Field(..., ge=0)
    collection_name: str = Field(default="papers", min_length=1, max_length=100)


class CitationDownloadResponse(BaseModel):
    success: bool
    citation: Optional[CitationItem] = None
    indexed: bool = False
    message: str = ""


class PPTExportRequest(BaseModel):
    answer: str = Field(..., min_length=1)
    title: str = Field(default="M-RAG Summary")
    subtitle: str = Field(default="")
