"""
Deployment sanity checks.
Usage:
    cd backend && python scripts/verify_deployment.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent.parent))

CHECKS: list[tuple[str, Callable[[], str]]] = []


def check(name: str) -> Callable[[Callable[[], str]], Callable[[], str]]:
    """Decorator to register a check item."""

    def decorator(func: Callable[[], str]) -> Callable[[], str]:
        CHECKS.append((name, func))
        return func

    return decorator


@check("config import")
def check_config() -> str:
    from config import ROUTE_MAP, SECTION_PATTERNS, LECTURE_PATTERNS, PATENT_PATTERNS

    assert "quiz" in ROUTE_MAP, "ROUTE_MAP must include 'quiz'"
    assert len(SECTION_PATTERNS) > 0, "SECTION_PATTERNS is empty"
    assert len(LECTURE_PATTERNS) > 0, "LECTURE_PATTERNS is empty"
    assert len(PATENT_PATTERNS) > 0, "PATENT_PATTERNS is empty"
    return f"ROUTE_MAP keys: {list(ROUTE_MAP.keys())}"


@check("module imports")
def check_modules() -> str:
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

    assert hasattr(RouteType, "QUIZ"), "RouteType.QUIZ is missing"
    assert all(
        item is not None
        for item in (
            PDFParser,
            SectionDetector,
            Chunker,
            Embedder,
            VectorStore,
            HybridRetriever,
            Reranker,
            ContextCompressor,
            QueryRouter,
            QueryExpander,
            CitationTracker,
            generate_followups,
        )
    )
    return "core modules imported"


@check("decoder imports")
def check_decoders() -> str:
    from modules.cad_decoder import create_cad_processor
    from modules.scd_decoder import create_combined_processor

    assert create_cad_processor is not None
    assert create_combined_processor is not None
    return "CAD + SCD imports OK"


@check("pipeline imports")
def check_pipelines() -> str:
    from pipelines import pipeline_a_simple_qa
    from pipelines import pipeline_b_section
    from pipelines import pipeline_c_compare
    from pipelines import pipeline_d_citation
    from pipelines import pipeline_e_summary
    from pipelines import pipeline_f_quiz

    assert all(
        pipeline is not None
        for pipeline in (
            pipeline_a_simple_qa,
            pipeline_b_section,
            pipeline_c_compare,
            pipeline_d_citation,
            pipeline_e_summary,
            pipeline_f_quiz,
        )
    )
    return "pipeline imports OK"


@check("evaluation imports")
def check_evaluation() -> str:
    from evaluation.ragas_eval import RAGASEvaluator, load_test_queries
    from evaluation.decoder_ablation import (
        DecoderAblationStudy,
        compare_cad_on_off,
    )
    from evaluation.ablation_study import (
        AblationConfig,
        ABLATION_CONFIGS,
        CAD_ALPHA_VALUES,
        SCD_BETA_VALUES,
    )

    assert all(
        item is not None
        for item in (
            RAGASEvaluator,
            load_test_queries,
            DecoderAblationStudy,
            compare_cad_on_off,
            AblationConfig,
            ABLATION_CONFIGS,
            CAD_ALPHA_VALUES,
            SCD_BETA_VALUES,
        )
    )
    return "evaluation imports OK"


@check("API routers + schemas")
def check_api() -> str:
    if not os.environ.get("JWT_SECRET_KEY"):
        return "WARN: JWT_SECRET_KEY not set - skipping API router import check"

    from api.routers.chat import router as chat_router
    from api.routers.papers import router as papers_router
    from api.routers.citations import router as citations_router
    from api.schemas import (
        QueryResponse,
        CitationItem,
        CitationDownloadResponse,
        CitationListRequest,
        CitationDownloadRequest,
    )

    assert all(
        router is not None for router in (chat_router, papers_router, citations_router)
    )
    assert all(
        schema is not None
        for schema in (
            QueryResponse,
            CitationItem,
            CitationDownloadResponse,
            CitationListRequest,
            CitationDownloadRequest,
        )
    )
    return "API router/schema imports OK"


@check("pymupdf4llm installed")
def check_pymupdf4llm() -> str:
    try:
        import pymupdf4llm

        version = (
            pymupdf4llm.__version__
            if hasattr(pymupdf4llm, "__version__")
            else "installed"
        )
        return f"pymupdf4llm {version}"
    except ImportError:
        return "WARN: pymupdf4llm missing (fallback mode)"


@check("ChromaDB writable")
def check_chroma() -> str:
    from config import CHROMA_DIR

    assert CHROMA_DIR.exists(), f"ChromaDB directory not found: {CHROMA_DIR}"
    test_file = CHROMA_DIR / ".write_test"
    test_file.write_text("test", encoding="utf-8")
    test_file.unlink()
    return f"{CHROMA_DIR} writable"


@check("BGE-M3 cache")
def check_bge_cache() -> str:
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    bge_dirs = list(cache_dir.glob("*bge*m3*")) if cache_dir.exists() else []
    if bge_dirs:
        return f"BGE-M3 cache found: {bge_dirs[0].name}"
    return "WARN: BGE-M3 cache not found (will download on first run)"


@check("LOAD_GPU_MODELS env")
def check_gpu_env() -> str:
    val = os.environ.get("LOAD_GPU_MODELS", "true")
    if val.lower() == "true":
        return "LOAD_GPU_MODELS=true (generator runtime enabled)"
    raise RuntimeError(
        "LOAD_GPU_MODELS must be true for supported service/experiment runs."
    )


@check("track query files validity")
def check_track_queries() -> str:
    import json
    from pathlib import Path as _Path

    from evaluation.ragas_eval import load_test_queries

    # track1: runtime-generated placeholder — empty [] is allowed (WARN)
    track1_status = "missing"
    track1_path = _Path("evaluation/data/track1_queries.json")
    if track1_path.exists():
        try:
            with track1_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            items = (
                data
                if isinstance(data, list)
                else (data.get("queries") or data.get("samples") or [])
            )
            if not items:
                track1_status = "warn(empty runtime-generated placeholder)"
            else:
                track1_status = str(len(items))
        except Exception:
            track1_status = "warn(parse error)"

    # track2: checked-in evaluation asset — must exist and be populated
    track2_samples = load_test_queries("evaluation/data/track2_queries.json")
    track2_status = str(len(track2_samples))

    if track1_status.startswith("warn") or track1_status == "missing":
        return f"WARN: track1={track1_status}, track2={track2_status}"
    return f"track1={track1_status}, track2={track2_status}"


def main() -> None:
    print("=" * 50)
    print("M-RAG Deployment Verification")
    print("=" * 50)

    passed = 0
    warned = 0
    failed = 0

    for name, func in CHECKS:
        try:
            result = func()
            if result.startswith("WARN:"):
                print(f"  [WARN] {name}: {result}")
                warned += 1
            else:
                print(f"  [OK]   {name}: {result}")
                passed += 1
        except Exception as exc:
            print(f"  [FAIL] {name}: {exc}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Result: {passed} passed, {warned} warnings, {failed} failed")

    if failed > 0:
        print("Deployment blocked: resolve failed checks.")
        sys.exit(1)

    print("Deployment verification passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
