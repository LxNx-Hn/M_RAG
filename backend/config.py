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
# HuggingFace cache: 환경변수 우선, 미설정 시 backend/.cache/huggingface로 fallback
# Alice Cloud / RunPod 등 외부 환경에서는 export HF_HOME=...로 영구볼륨 경로 지정 권장
# ─────────────────────────────────────────────
_HF_CACHE_DEFAULT = str(Path.home() / ".cache" / "huggingface")
os.environ.setdefault("HF_HOME", _HF_CACHE_DEFAULT)
os.environ.setdefault("TRANSFORMERS_CACHE", os.environ["HF_HOME"])
os.environ.setdefault("HF_HUB_CACHE", os.environ["HF_HOME"])

# ─────────────────────────────────────────────
# Embedding
# ─────────────────────────────────────────────
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_BATCH_SIZE = 32
EMBEDDING_DIMENSION = 1024

# ─────────────────────────────────────────────
# LLM Generation
# ─────────────────────────────────────────────
GENERATION_MODEL = os.environ.get(
    "GENERATION_MODEL",
    "K-intelligence/Midm-2.0-Base-Instruct",  # Thesis baseline default
    # Mini fallback for local smoke runs: GENERATION_MODEL=K-intelligence/Midm-2.0-Mini-Instruct
)
BASELINE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
MAX_NEW_TOKENS = 1024
TEMPERATURE = 0.1
TOP_P = 0.9

# ─────────────────────────────────────────────
# MODULE 13A: CAD (파라메트릭 지식 개입 억제)
# ─────────────────────────────────────────────
CAD_ALPHA = (
    0.5  # suppression strength (0~1), Table 2 ablation: {0.1, 0.3, 0.5, 0.7, 1.0}
)

# ─────────────────────────────────────────────
# MODULE 13B: SCD (Language Drift 억제)
# ─────────────────────────────────────────────
SCD_BETA = 0.3  # non-target language penalty (0~1), Table 2 ablation: {0.1, 0.3, 0.5}
SCD_TARGET_LANG = "ko"  # 목표 언어

# ─────────────────────────────────────────────
# Chunking
# ─────────────────────────────────────────────
CHUNK_SIZE = 512  # tokens
CHUNK_OVERLAP = 64  # tokens
MIN_CHUNK_SIZE = 50  # tokens

# ─────────────────────────────────────────────
# Retrieval
# ─────────────────────────────────────────────
TOP_K_RETRIEVAL = 20  # initial retrieval count
TOP_K_RERANK = 5  # after reranking
RRF_K = 60  # RRF constant
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
    "section_result": [
        "결과",
        "성능",
        "result",
        "performance",
        "accuracy",
        "f1",
        "score",
        "실험",
    ],
    "section_method": [
        "방법론",
        "어떻게",
        "method",
        "approach",
        "architecture",
        "모델 구조",
        "알고리즘",
    ],
    "section_abstract": ["초록", "abstract", "개요", "overview"],
    "section_conclusion": ["결론", "conclusion", "시사점", "의의"],
    "section_limit": ["한계", "limitation", "future work", "단점", "제한"],
    "compare": ["비교", "차이", "vs", "compare", "versus", "다른 점", "공통점"],
    "citation": [
        "인용",
        "참고문헌",
        "reference",
        "cited by",
        "레퍼런스",
        "유사 특허",
        "인용 특허",
        "선행 기술",
        "similar patent",
        "prior art",
    ],
    "quiz": [
        "문제",
        "퀴즈",
        "연습",
        "시험",
        "quiz",
        "exercise",
        "출제",
        "플래시카드",
        "카드",
        "flashcard",
        "암기",
    ],
    "summary": ["요약", "summarize", "전체", "overview", "정리해", "설명해"],
}

# ─────────────────────────────────────────────
# Section Detection Patterns (학술 논문)
# ─────────────────────────────────────────────
SECTION_PATTERNS = {
    "abstract": [r"(?i)^abstract\b", r"(?i)^요약\b", r"(?i)^초록\b"],
    "introduction": [
        r"(?i)^1[\.\s]+introduction",
        r"(?i)^introduction\b",
        r"(?i)^서론",
        r"(?i)^들어가",
    ],
    "related_work": [
        r"(?i)related\s*work",
        r"(?i)background",
        r"(?i)관련\s*연구",
        r"(?i)선행\s*연구",
    ],
    "method": [
        r"(?i)method",
        r"(?i)approach",
        r"(?i)model\b",
        r"(?i)proposed",
        r"(?i)^방법\b",
        r"(?i)방법론",
        r"(?i)연구\s*방법",
        r"(?i)data\s*foundations?",
        r"(?i)pre-?training",
        r"(?i)post-?training",
    ],
    "experiment": [r"(?i)experiment", r"(?i)setup", r"(?i)실험", r"(?i)연구\s*설계"],
    "result": [
        r"(?i)result",
        r"(?i)evaluation",
        r"(?i)결과",
        r"(?i)성능",
        r"(?i)분석\s*결과",
    ],
    "discussion": [r"(?i)discussion", r"(?i)analysis", r"(?i)논의", r"(?i)고찰"],
    "conclusion": [r"(?i)conclusion", r"(?i)결론", r"(?i)summary", r"(?i)마치며"],
    "references": [r"(?i)^references?\b", r"(?i)^bibliography", r"(?i)^참고\s*문헌"],
}

# ─────────────────────────────────────────────
# General Document Section Patterns (교재/보고서/기술문서)
# 논문 섹션 감지 실패 시 fallback으로 사용
# ─────────────────────────────────────────────
GENERAL_DOC_PATTERNS = {
    # 교재 챕터/절
    "chapter": [
        r"(?i)^chapter\s+\d+",
        r"^제\s*\d+\s*장",
        r"^\d+\.\s+[가-힣A-Za-z]",  # "1. 서론" 형태
        r"^[IVX]+\.\s+[가-힣A-Za-z]",  # "I. Introduction" 형태
    ],
    "section": [
        r"^제\s*\d+\s*절",
        r"^\d+\.\d+\s+[가-힣A-Za-z]",  # "1.1 배경" 형태
    ],
    # 보고서/기획서
    "overview": [
        r"(?i)^(개요|overview|executive\s*summary)",
        r"(?i)^(목적|purpose|배경)",
    ],
    "body": [
        r"(?i)^(본론|내용|주요\s*내용|main\s*body)",
    ],
    "recommendation": [
        r"(?i)^(권고|권장|제언|시사점|implications?)",
        r"(?i)^(제안|recommendations?)",
    ],
    # 기술 문서
    "requirements": [
        r"(?i)^(요구사항|requirements?|기능\s*명세)",
    ],
    "design": [
        r"(?i)^(설계|design|아키텍처|architecture)",
    ],
    "implementation": [
        r"(?i)^(구현|implementation|개발)",
    ],
    # 공통
    "conclusion": [
        r"(?i)^(결론|conclusion|마무리|마치며|결어)",
        r"(?i)^(종합|정리|요약\s*및\s*결론)",
    ],
    "appendix": [
        r"(?i)^(부록|appendix|별첨)",
    ],
}

# ─────────────────────────────────────────────
# Lecture/Textbook Section Patterns (강의/교재)
# ─────────────────────────────────────────────
LECTURE_PATTERNS = {
    "definition": [r"(?i)^(definition|정의|정\.|def\.)\s*\d*"],
    "theorem": [r"(?i)^(theorem|정리|thm\.)\s*\d*", r"(?i)^lemma\s*\d*"],
    "proof": [r"(?i)^(proof|증명)\b"],
    "example": [r"(?i)^(example|예제|예\.|보기)\s*\d*"],
    "exercise": [r"(?i)^(exercise|연습\s*문제|문제|practice)\s*\d*"],
    "code_block": [r"(?i)^(코드|예제\s*코드|listing|algorithm)\s*\d*"],
    "chapter": [r"(?i)^chapter\s+\d+", r"^제\s*\d+\s*장"],
    "section": [r"^\d+\.\d+\s+", r"^제\s*\d+\s*절"],
}

# ─────────────────────────────────────────────
# Patent Section Patterns (특허 명세서)
# ─────────────────────────────────────────────
PATENT_PATTERNS = {
    "title": [r"(?i)^(발명의\s*명칭|title\s*of\s*(the\s*)?invention)"],
    "abstract": [r"(?i)^(요약|초록|abstract)\s*$"],
    "technical_field": [r"(?i)^(기술\s*분야|technical\s*field)"],
    "background": [r"(?i)^(배경\s*기술|background\s*art|prior\s*art)"],
    "summary": [r"(?i)^(발명의\s*요약|summary\s*of\s*(the\s*)?invention)"],
    "problem": [r"(?i)^(해결하려는\s*과제|problems?\s*to\s*be\s*solved)"],
    "solution": [
        r"(?i)^(과제의\s*해결\s*수단|means?\s*of\s*solving|solution\s*to\s*problem)"
    ],
    "detailed_description": [
        r"(?i)^(발명의\s*상세한\s*설명|detailed\s*description|description\s*of\s*embodiments?)",
        r"(?i)^(발명을\s*실시하기\s*위한\s*구체적인\s*내용)",
    ],
    "drawings": [
        r"(?i)^(도면의\s*간단한\s*설명|brief\s*description\s*of\s*(the\s*)?drawings?)"
    ],
    "claims": [r"(?i)^(청구(의)?\s*범위|청구항|claims?)\s*$", r"^【청구항\s*\d+】"],
    "cited_patents": [
        r"(?i)^(인용\s*문헌|선행\s*기술\s*문헌|references?\s*cited|cited\s*patents?)"
    ],
}

# ─────────────────────────────────────────────
# Google Patents / KIPRIS (특허 추적)
# ─────────────────────────────────────────────
GOOGLE_PATENTS_BASE = "https://patents.google.com/patent"
KIPRIS_API_KEY = os.environ.get("KIPRIS_API_KEY", "")  # 선택적
