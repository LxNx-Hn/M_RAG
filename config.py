"""
Modular RAG Paper Review Agent - Global Configuration
"""
import os
from pathlib import Path

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# Embedding
# ─────────────────────────────────────────────
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_BATCH_SIZE = 32
EMBEDDING_DIMENSION = 1024

# ─────────────────────────────────────────────
# LLM Generation
# ─────────────────────────────────────────────
GENERATION_MODEL = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"
BASELINE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
MAX_NEW_TOKENS = 1024
TEMPERATURE = 0.1
TOP_P = 0.9

# ─────────────────────────────────────────────
# Contrastive Decoding
# ─────────────────────────────────────────────
CAD_ALPHA = 0.5  # suppression strength (0~1)

# ─────────────────────────────────────────────
# Chunking
# ─────────────────────────────────────────────
CHUNK_SIZE = 512          # tokens
CHUNK_OVERLAP = 64        # tokens
MIN_CHUNK_SIZE = 50       # tokens

# ─────────────────────────────────────────────
# Retrieval
# ─────────────────────────────────────────────
TOP_K_RETRIEVAL = 20      # initial retrieval count
TOP_K_RERANK = 5          # after reranking
RRF_K = 60                # RRF constant
BM25_WEIGHT = 0.4
DENSE_WEIGHT = 0.6

# ─────────────────────────────────────────────
# Reranker
# ─────────────────────────────────────────────
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ─────────────────────────────────────────────
# Context Compression
# ─────────────────────────────────────────────
MAX_CONTEXT_TOKENS = 3072
COMPRESSION_RATIO = 0.5

# ─────────────────────────────────────────────
# Citation Tracker
# ─────────────────────────────────────────────
ARXIV_MAX_RESULTS = 5
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"

# ─────────────────────────────────────────────
# Query Router Keywords
# ─────────────────────────────────────────────
ROUTE_MAP = {
    "section_result": ["결과", "성능", "result", "performance", "accuracy", "f1", "score", "실험"],
    "section_method": ["방법론", "어떻게", "method", "approach", "architecture", "모델 구조", "알고리즘"],
    "section_abstract": ["초록", "abstract", "개요", "overview"],
    "section_conclusion": ["결론", "conclusion", "시사점", "의의"],
    "section_limit": ["한계", "limitation", "future work", "단점", "제한"],
    "compare": ["비교", "차이", "vs", "compare", "versus", "다른 점", "공통점"],
    "citation": ["인용", "참고문헌", "reference", "cited by", "레퍼런스"],
    "summary": ["요약", "summarize", "전체", "overview", "정리해", "설명해"],
}

# ─────────────────────────────────────────────
# Section Detection Patterns
# ─────────────────────────────────────────────
SECTION_PATTERNS = {
    "abstract": [r"(?i)^abstract\b", r"(?i)^요약\b"],
    "introduction": [r"(?i)^1[\.\s]+introduction", r"(?i)^introduction\b", r"(?i)^서론"],
    "related_work": [r"(?i)related\s*work", r"(?i)background", r"(?i)관련\s*연구"],
    "method": [r"(?i)method", r"(?i)approach", r"(?i)model\b", r"(?i)proposed", r"(?i)방법론"],
    "experiment": [r"(?i)experiment", r"(?i)setup", r"(?i)실험"],
    "result": [r"(?i)result", r"(?i)evaluation", r"(?i)결과", r"(?i)성능"],
    "discussion": [r"(?i)discussion", r"(?i)analysis", r"(?i)논의"],
    "conclusion": [r"(?i)conclusion", r"(?i)결론", r"(?i)summary"],
    "references": [r"(?i)^references?\b", r"(?i)^bibliography", r"(?i)^참고\s*문헌"],
}

# ─────────────────────────────────────────────
# Streamlit UI
# ─────────────────────────────────────────────
APP_TITLE = "📑 M-RAG: 모듈러 RAG 논문 리뷰 에이전트"
APP_DESCRIPTION = "학술 논문 PDF를 업로드하고 한국어로 질의응답하세요."
MAX_UPLOAD_SIZE_MB = 50
