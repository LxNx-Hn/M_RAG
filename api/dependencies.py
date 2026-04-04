"""
FastAPI 의존성 관리
모든 모듈을 싱글턴으로 초기화하고 요청 간 공유
"""
import logging
from functools import lru_cache

from modules.pdf_parser import PDFParser
from modules.section_detector import SectionDetector
from modules.chunker import Chunker
from modules.embedder import Embedder
from modules.vector_store import VectorStore
from modules.query_router import QueryRouter
from modules.hybrid_retriever import HybridRetriever
from modules.reranker import Reranker
from modules.context_compressor import ContextCompressor
from modules.citation_tracker import CitationTracker

logger = logging.getLogger(__name__)


class ModuleManager:
    """모든 RAG 모듈을 싱글턴으로 관리
    FastAPI의 lifespan에서 초기화, 요청 간 공유
    """

    def __init__(self):
        self._initialized = False
        self.pdf_parser: PDFParser | None = None
        self.section_detector: SectionDetector | None = None
        self.chunker: Chunker | None = None
        self.embedder: Embedder | None = None
        self.vector_store: VectorStore | None = None
        self.query_router: QueryRouter | None = None
        self.hybrid_retriever: HybridRetriever | None = None
        self.reranker: Reranker | None = None
        self.compressor: ContextCompressor | None = None
        self.citation_tracker: CitationTracker | None = None
        self.generator = None
        self.query_expander = None

    def initialize(self, load_gpu_models: bool = False):
        """모듈 초기화 (서버 시작 시 1회)"""
        if self._initialized:
            return

        logger.info("Initializing RAG modules...")

        self.pdf_parser = PDFParser()
        self.section_detector = SectionDetector()
        self.chunker = Chunker()
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.query_router = QueryRouter()
        self.hybrid_retriever = HybridRetriever(self.vector_store, self.embedder)
        self.reranker = Reranker()
        self.compressor = ContextCompressor()
        self.citation_tracker = CitationTracker()

        # GPU 모델 (선택적)
        if load_gpu_models:
            try:
                from modules.generator import Generator
                from modules.query_expander import QueryExpander
                self.generator = Generator()
                self.query_expander = QueryExpander(generator=self.generator)
                self.compressor.generator = self.generator
                logger.info("GPU models loaded successfully")
            except Exception as e:
                logger.warning(f"GPU models not available: {e}")

        self._initialized = True
        logger.info("All modules initialized")

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def has_generator(self) -> bool:
        return self.generator is not None


# 글로벌 싱글턴
modules = ModuleManager()


def get_modules() -> ModuleManager:
    """FastAPI Depends()용"""
    if not modules.is_initialized:
        modules.initialize()
    return modules
