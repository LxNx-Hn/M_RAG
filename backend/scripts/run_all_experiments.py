"""
M-RAG 전체 실험 스크립트 — 논문 Table 1~4 한 번에 실행

Usage:
    # MIDM Mini (로컬, RTX 3080 Ti 12GB)
    LOAD_GPU_MODELS=true python scripts/run_all_experiments.py \
        --paper-pdf data/1810.04805_bert.pdf

    # MIDM Base (RunPod, A100 40GB+)
    GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct \
    LOAD_GPU_MODELS=true python scripts/run_all_experiments.py \
        --paper-pdf data/1810.04805_bert.pdf

    # 쿼리 수 조절 (기본 10개, 빠른 테스트는 5개)
    python scripts/run_all_experiments.py --paper-pdf data/paper.pdf --max-queries 5

    # 특정 테이블만 실행
    python scripts/run_all_experiments.py --paper-pdf data/paper.pdf --tables 2,3

예상 소요 시간:
    ┌──────────────┬────────────┬────────────┬────────────┐
    │              │ 10 queries │ A100 (Base)│ 3080Ti(Mini)│
    │ Table 1 (6c) │ 240 calls  │  ~12분     │  ~40분     │
    │ Table 2 (6c) │ 240 calls  │  ~12분     │  ~40분     │
    │ Table 3 (4c) │ 160 calls  │   ~8분     │  ~27분     │
    │ Table 4 (4c) │ 160 calls  │   ~8분     │  ~27분     │
    │ 합계         │ 800 calls  │  ~40분     │ ~134분     │
    └──────────────┴────────────┴────────────┴────────────┘
    * calls = 생성(1) + RAGAS평가(3) = 쿼리당 4회 LLM 호출
    * A100: ~3초/call, RTX 3080 Ti Mini: ~10초/call
"""
import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CHROMA_DIR, GENERATION_MODEL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def index_paper(pdf_path: str, collection_name: str):
    """논문 PDF 인덱싱"""
    from modules.pdf_parser import PDFParser
    from modules.section_detector import SectionDetector
    from modules.chunker import Chunker
    from modules.embedder import Embedder
    from modules.vector_store import VectorStore
    from modules.hybrid_retriever import HybridRetriever

    pdf_parser = PDFParser()
    section_detector = SectionDetector()
    chunker = Chunker()
    embedder = Embedder()
    vector_store = VectorStore(persist_dir=str(CHROMA_DIR))
    hybrid_retriever = HybridRetriever(embedder=embedder, vector_store=vector_store)

    logger.info(f"=== 논문 인덱싱: {pdf_path} ===")
    parsed = pdf_parser.parse(pdf_path)
    parsed = section_detector.detect(parsed)
    chunks = chunker.chunk_document(parsed, strategy="section")

    if not chunks:
        logger.error("청크 생성 실패. PDF를 확인하세요.")
        sys.exit(1)

    embeddings = embedder.embed_texts([c.content for c in chunks])
    vector_store.add_chunks(collection_name, chunks, embeddings)
    hybrid_retriever.fit_bm25(collection_name)
    logger.info(f"인덱싱 완료: {len(chunks)} chunks")

    return embedder, vector_store, hybrid_retriever


def build_ablation_study(embedder, vector_store, hybrid_retriever):
    """AblationStudy 인스턴스 생성"""
    from modules.reranker import Reranker
    from modules.context_compressor import ContextCompressor
    from modules.generator import Generator
    from modules.query_expander import QueryExpander
    from evaluation.ablation_study import AblationStudy

    generator = Generator()
    _ = generator.model
    _ = generator.tokenizer
    logger.info(f"Generator 로드 완료: {generator.model_name}")

    query_expander = QueryExpander(generator=generator)
    reranker = Reranker()
    compressor = ContextCompressor()

    ablation = AblationStudy(
        pdf_parser=None,
        section_detector=None,
        chunker=None,
        embedder=embedder,
        vector_store=vector_store,
        hybrid_retriever=hybrid_retriever,
        reranker=reranker,
        compressor=compressor,
        generator=generator,
        query_router=None,
        query_expander=query_expander,
    )
    return ablation


def print_table1(results: dict):
    """Table 1: 모듈별 Ablation 마크다운 출력"""
    print("\n### Table 1: 모듈별 Ablation Study")
    print("| System | Faithfulness | Answer Rel. | Context Prec. | Context Recall | Overall |")
    print("|---|---|---|---|---|---|")
    for name, result in results.items():
        avg = result.get("average", {})
        cr = avg.get("context_recall")
        cr_str = f"{cr:.3f}" if cr is not None else "N/A"
        print(
            f"| {name} "
            f"| {avg.get('faithfulness', 0):.3f} "
            f"| {avg.get('answer_relevancy', 0):.3f} "
            f"| {avg.get('context_precision', 0):.3f} "
            f"| {cr_str} "
            f"| {avg.get('overall', 0):.3f} |"
        )


def print_table2(results: dict):
    """Table 2: CAD α Ablation 마크다운 출력"""
    print("\n### Table 2: CAD α Ablation")
    print(f"Best α = {results['summary']['best_alpha']}")
    print("| Alpha | Faithfulness Delta | Overall Delta |")
    print("|---|---|---|")
    for key, val in results["per_alpha"].items():
        fd = val["faithfulness_delta"]
        od = val["overall_delta"]
        print(f"| {key} | {'+' if fd >= 0 else ''}{fd:.3f} | {'+' if od >= 0 else ''}{od:.3f} |")


def print_table3(results: dict):
    """Table 3: SCD β Ablation 마크다운 출력"""
    print("\n### Table 3: SCD β Ablation")
    print(f"Best β = {results['summary']['best_beta']}")
    print("| Beta | Faithfulness Delta | Overall Delta |")
    print("|---|---|---|")
    for key, val in results["per_beta"].items():
        fd = val["faithfulness_delta"]
        od = val["overall_delta"]
        print(f"| {key} | {'+' if fd >= 0 else ''}{fd:.3f} | {'+' if od >= 0 else ''}{od:.3f} |")


def print_table4(results: dict):
    """Table 4: CAD+SCD 결합 효과 마크다운 출력"""
    print("\n### Table 4: CAD+SCD 결합 효과")
    print("| Config | Faithfulness | Answer Rel. | Context Prec. | Overall |")
    print("|---|---|---|---|---|")
    for name, avg in results["configs"].items():
        print(
            f"| {name} "
            f"| {avg.get('faithfulness', 0):.3f} "
            f"| {avg.get('answer_relevancy', 0):.3f} "
            f"| {avg.get('context_precision', 0):.3f} "
            f"| {avg.get('overall', 0):.3f} |"
        )


def main():
    parser = argparse.ArgumentParser(description="M-RAG 전체 실험 (Table 1~4)")
    parser.add_argument("--paper-pdf", required=True, help="평가용 논문 PDF 경로")
    parser.add_argument("--collection", default="full_eval", help="ChromaDB 컬렉션")
    parser.add_argument(
        "--tables", default="1,2,3,4",
        help="실행할 테이블 번호 (기본: 1,2,3,4)",
    )
    parser.add_argument(
        "--max-queries", type=int, default=10,
        help="사용할 최대 쿼리 수 (기본: 10, 빠른 테스트: 5)",
    )
    args = parser.parse_args()

    pdf_path = Path(args.paper_pdf)
    if not pdf_path.exists():
        logger.error(f"PDF 파일 없음: {pdf_path}")
        sys.exit(1)

    tables = [int(t.strip()) for t in args.tables.split(",")]
    start_time = time.time()

    # 1. 인덱싱
    embedder, vector_store, hybrid_retriever = index_paper(
        str(pdf_path), args.collection
    )

    # 2. AblationStudy 생성
    ablation = build_ablation_study(embedder, vector_store, hybrid_retriever)

    # 3. 쿼리 로드 (max-queries로 제한)
    from evaluation.ragas_eval import load_test_queries

    all_samples = load_test_queries(
        filepath="evaluation/test_queries.json",
        query_types=["cad_ablation", "crosslingual_en", "crosslingual_mixed",
                     "simple_qa", "section_result"],
    )
    samples = all_samples[:args.max_queries]
    logger.info(f"평가 쿼리: {len(samples)}개 (전체 {len(all_samples)}개 중 --max-queries={args.max_queries})")

    # LLM 호출 수 예측
    n_configs = {"1": 6, "2": 6, "3": 4, "4": 4}
    total_configs = sum(n_configs.get(str(t), 0) for t in tables)
    calls_per_query = 4  # 생성(1) + RAGAS(3: faithfulness, relevancy, precision)
    total_calls = total_configs * len(samples) * calls_per_query
    logger.info(f"예상 LLM 호출: {total_configs} configs × {len(samples)} queries × {calls_per_query} = {total_calls}회")

    all_results = {
        "metadata": {
            "paper": str(pdf_path),
            "collection": args.collection,
            "model": GENERATION_MODEL,
            "n_samples": len(samples),
            "max_queries": args.max_queries,
            "tables": tables,
            "timestamp": datetime.now().isoformat(),
        }
    }

    # Table 1: 모듈별 Ablation
    if 1 in tables:
        logger.info("=" * 60)
        logger.info("=== Table 1: 모듈별 Ablation Study ===")
        t1_start = time.time()
        table1 = ablation.run_ablation(samples, args.collection)
        t1_elapsed = time.time() - t1_start
        all_results["table1_module_ablation"] = table1
        logger.info(f"Table 1 완료: {t1_elapsed:.0f}초 ({t1_elapsed/60:.1f}분)")

    # Table 2: CAD α Ablation
    if 2 in tables:
        logger.info("=" * 60)
        logger.info("=== Table 2: CAD α Ablation ===")
        t2_start = time.time()
        table2 = ablation.run_cad_korean_evaluation(samples, args.collection)
        t2_elapsed = time.time() - t2_start
        all_results["table2_cad_alpha"] = table2
        logger.info(f"Table 2 완료: {t2_elapsed:.0f}초 ({t2_elapsed/60:.1f}분)")

    # Table 3: SCD β Ablation
    if 3 in tables:
        logger.info("=" * 60)
        logger.info("=== Table 3: SCD β Ablation ===")
        t3_start = time.time()
        table3 = ablation.run_scd_beta_ablation(samples, args.collection)
        t3_elapsed = time.time() - t3_start
        all_results["table3_scd_beta"] = table3
        logger.info(f"Table 3 완료: {t3_elapsed:.0f}초 ({t3_elapsed/60:.1f}분)")

    # Table 4: CAD+SCD 결합
    if 4 in tables:
        logger.info("=" * 60)
        logger.info("=== Table 4: CAD+SCD 결합 효과 ===")
        t4_start = time.time()
        table4 = ablation.run_combined_ablation(samples, args.collection)
        t4_elapsed = time.time() - t4_start
        all_results["table4_combined"] = table4
        logger.info(f"Table 4 완료: {t4_elapsed:.0f}초 ({t4_elapsed/60:.1f}분)")

    total_elapsed = time.time() - start_time
    all_results["metadata"]["total_seconds"] = round(total_elapsed)

    # 결과 저장
    results_dir = Path("evaluation/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"full_experiment_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 마크다운 표 출력
    print("\n" + "=" * 60)
    print(f"M-RAG 전체 실험 결과 (모델: {GENERATION_MODEL})")
    print(f"총 소요 시간: {total_elapsed / 60:.1f}분")
    print(f"쿼리 수: {len(samples)}개, LLM 호출: {total_calls}회")
    print("=" * 60)

    if "table1_module_ablation" in all_results:
        print_table1(all_results["table1_module_ablation"])
    if "table2_cad_alpha" in all_results:
        print_table2(all_results["table2_cad_alpha"])
    if "table3_scd_beta" in all_results:
        print_table3(all_results["table3_scd_beta"])
    if "table4_combined" in all_results:
        print_table4(all_results["table4_combined"])

    print(f"\n결과 파일: {output_path}")


if __name__ == "__main__":
    main()
