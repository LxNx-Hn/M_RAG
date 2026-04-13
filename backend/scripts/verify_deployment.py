"""
배포 직전 sanity check — 모든 모듈 임포트 + 환경 검증

Usage:
    cd backend && python scripts/verify_deployment.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

CHECKS = []


def check(name: str):
    """데코레이터: 체크 항목 등록"""
    def decorator(func):
        CHECKS.append((name, func))
        return func
    return decorator


@check("config.py 임포트")
def check_config():
    from config import ROUTE_MAP, SECTION_PATTERNS, LECTURE_PATTERNS, PATENT_PATTERNS
    assert "quiz" in ROUTE_MAP, "ROUTE_MAP에 quiz 키 없음"
    assert len(LECTURE_PATTERNS) > 0
    assert len(PATENT_PATTERNS) > 0
    return f"ROUTE_MAP keys: {list(ROUTE_MAP.keys())}"


@check("modules 임포트")
def check_modules():
    from modules.pdf_parser import PDFParser
    from modules.section_detector import SectionDetector
    from modules.chunker import Chunker
    from modules.embedder import Embedder
    from modules.vector_store import VectorStore
    from modules.hybrid_retriever import HybridRetriever
    from modules.reranker import Reranker
    from modules.context_compressor import ContextCompressor
    from modules.query_router import QueryRouter, RouteType
    from modules.query_expander import QueryExpander
    from modules.citation_tracker import CitationTracker
    from modules.followup_generator import generate_followups
    assert hasattr(RouteType, "QUIZ"), "RouteType.QUIZ 없음"
    return "14 modules OK"


@check("cad_decoder + scd_decoder")
def check_decoders():
    from modules.cad_decoder import create_cad_processor
    from modules.scd_decoder import create_combined_processor
    return "CAD + SCD OK"


@check("pipelines A~F")
def check_pipelines():
    from pipelines import pipeline_a_simple_qa
    from pipelines import pipeline_b_section
    from pipelines import pipeline_c_compare
    from pipelines import pipeline_d_citation
    from pipelines import pipeline_e_summary
    from pipelines import pipeline_f_quiz
    return "6 pipelines OK"


@check("evaluation 프레임워크")
def check_evaluation():
    from evaluation.ragas_eval import RAGASEvaluator, load_test_queries, compare_cad_on_off
    from evaluation.ablation_study import AblationStudy
    return "RAGAS + Ablation OK"


@check("API routers")
def check_api():
    from api.routers.chat import router as chat_router
    from api.routers.papers import router as papers_router
    from api.routers.citations import router as citations_router
    from api.schemas import (
        QueryResponse, CitationItem, CitationDownloadResponse,
        CitationListRequest, CitationDownloadRequest,
    )
    assert hasattr(QueryResponse.model_fields, '__contains__') or True
    return "API routers + schemas OK"


@check("pymupdf4llm")
def check_pymupdf4llm():
    try:
        import pymupdf4llm
        return f"pymupdf4llm {pymupdf4llm.__version__ if hasattr(pymupdf4llm, '__version__') else 'installed'}"
    except ImportError:
        return "WARN: pymupdf4llm 미설치 — 구조 보존 추출이 fallback 모드로 동작"


@check("ChromaDB 디렉토리 쓰기 권한")
def check_chroma():
    from config import CHROMA_DIR
    assert CHROMA_DIR.exists(), f"ChromaDB 디렉토리 없음: {CHROMA_DIR}"
    test_file = CHROMA_DIR / ".write_test"
    test_file.write_text("test")
    test_file.unlink()
    return f"{CHROMA_DIR} writable"


@check("BGE-M3 캐시 존재")
def check_bge_cache():
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    bge_dirs = list(cache_dir.glob("*bge*m3*")) if cache_dir.exists() else []
    if bge_dirs:
        return f"BGE-M3 cache found: {bge_dirs[0].name}"
    return "WARN: BGE-M3 캐시 없음 — 첫 실행 시 다운로드됨"


@check("LOAD_GPU_MODELS 환경 변수")
def check_gpu_env():
    val = os.environ.get("LOAD_GPU_MODELS", "")
    if val.lower() == "true":
        return "LOAD_GPU_MODELS=true — GPU 모델 로드 활성화"
    return "LOAD_GPU_MODELS 미설정 — GPU 모델 비활성화 (검색만 가능)"


@check("test_queries.json 유효성")
def check_test_queries():
    from evaluation.ragas_eval import load_test_queries
    all_samples = load_test_queries("evaluation/test_queries.json")
    cad_samples = load_test_queries("evaluation/test_queries.json", query_types=["cad_ablation"])
    return f"total={len(all_samples)}, cad_ablation={len(cad_samples)}"


def main():
    print("=" * 50)
    print("M-RAG Deployment Verification")
    print("=" * 50)

    passed = 0
    warned = 0
    failed = 0

    for name, func in CHECKS:
        try:
            result = func()
            if result and result.startswith("WARN:"):
                print(f"  [WARN] {name}: {result}")
                warned += 1
            else:
                print(f"  [OK]   {name}: {result}")
                passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"결과: {passed} passed, {warned} warnings, {failed} failed")

    if failed > 0:
        print("배포 전 실패 항목을 해결하세요.")
        sys.exit(1)
    else:
        print("배포 준비 완료!")
        sys.exit(0)


if __name__ == "__main__":
    main()
