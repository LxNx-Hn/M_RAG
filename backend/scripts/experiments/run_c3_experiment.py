"""
C3 핵심 실험: CAD on/off RAGAS 비교 (논문 Table 2 직접 사용)

Usage:
    python scripts/experiments/run_c3_experiment.py --paper-pdf data/paper_A_nlp.pdf --collection c3_eval
    python scripts/experiments/run_c3_experiment.py --paper-pdf data/paper_A_nlp.pdf --heuristic  # GPU 없이
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import CHROMA_DIR

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="C3 CAD Ablation Experiment")
    parser.add_argument("--paper-pdf", required=True, help="평가용 논문 PDF 경로")
    parser.add_argument("--collection", default="c3_eval", help="ChromaDB 컬렉션 이름")
    parser.add_argument(
        "--heuristic", action="store_true", help="GPU 없이 휴리스틱 모드 실행"
    )
    args = parser.parse_args()

    pdf_path = Path(args.paper_pdf)
    if not pdf_path.exists():
        logger.error(f"PDF 파일이 존재하지 않습니다: {pdf_path}")
        sys.exit(1)

    # 1. 모듈 로드
    logger.info("=== 모듈 로드 ===")
    from modules.pdf_parser import PDFParser
    from modules.section_detector import SectionDetector
    from modules.chunker import Chunker
    from modules.embedder import Embedder
    from modules.vector_store import VectorStore
    from modules.hybrid_retriever import HybridRetriever
    from modules.reranker import Reranker
    from modules.context_compressor import ContextCompressor
    from evaluation.ragas_eval import RAGASEvaluator, load_test_queries

    pdf_parser = PDFParser()
    section_detector = SectionDetector()
    chunker = Chunker()
    embedder = Embedder()
    vector_store = VectorStore(persist_dir=str(CHROMA_DIR))
    hybrid_retriever = HybridRetriever(embedder=embedder, vector_store=vector_store)
    reranker = Reranker()
    compressor = ContextCompressor()

    generator = None
    if not args.heuristic:
        try:
            from modules.generator import Generator

            generator = Generator()
            logger.info("Generator (LLM) 로드 완료")
        except Exception as e:
            logger.warning(f"Generator 로드 실패 — 휴리스틱 모드로 전환: {e}")

    # 2. 논문 인덱싱
    logger.info(f"=== 논문 인덱싱: {pdf_path} ===")
    parsed = pdf_parser.parse(str(pdf_path))
    parsed = section_detector.detect(parsed)
    chunks = chunker.chunk_document(parsed, strategy="section")

    if not chunks:
        logger.error("청크가 생성되지 않았습니다. PDF를 확인하세요.")
        sys.exit(1)

    embeddings = embedder.embed_texts([c.content for c in chunks])
    vector_store.add_chunks(args.collection, chunks, embeddings)
    hybrid_retriever.fit_bm25(args.collection)
    logger.info(f"인덱싱 완료: {len(chunks)} chunks")

    # 3. 평가 쿼리 로드
    logger.info("=== 평가 쿼리 로드 ===")
    query_types = ["cad_ablation", "crosslingual_mixed", "crosslingual_en"]
    samples = load_test_queries(
        filepath="evaluation/test_queries.json",
        query_types=query_types,
    )
    logger.info(f"로드된 샘플: {len(samples)}개 (types: {query_types})")

    empty_gt = sum(1 for s in samples if not s.ground_truth)
    if empty_gt > 0:
        logger.warning(
            f"ground_truth가 비어 있는 샘플 {empty_gt}개 — "
            f"context_recall은 N/A로 표시됩니다"
        )

    # 4. 실험 실행
    evaluator = RAGASEvaluator(generator=generator)

    if generator is not None:
        # GPU 모드: CAD on/off 비교
        logger.info("=== C3 CAD on/off 비교 실험 (GPU 모드) ===")
        from evaluation.ragas_eval import compare_cad_on_off

        results = compare_cad_on_off(
            evaluator=evaluator,
            samples=samples,
            generator=generator,
            collection_name=args.collection,
            retriever=hybrid_retriever,
            reranker=reranker,
            compressor=compressor,
            cad_alpha=0.5,
        )

        # Alpha 다단계 ablation
        logger.info("=== CAD Alpha 5단계 Ablation ===")
        from modules.query_expander import QueryExpander
        from evaluation.ablation_study import AblationStudy

        query_expander = QueryExpander(generator=generator)

        ablation = AblationStudy(
            pdf_parser=pdf_parser,
            section_detector=section_detector,
            chunker=chunker,
            embedder=embedder,
            vector_store=vector_store,
            hybrid_retriever=hybrid_retriever,
            reranker=reranker,
            compressor=compressor,
            generator=generator,
            query_router=None,
            query_expander=query_expander,
        )

        alpha_results = ablation.run_cad_korean_evaluation(
            test_samples=samples,
            collection_name=args.collection,
        )

        combined = {
            "cad_on_off": results,
            "alpha_ablation": alpha_results,
            "metadata": {
                "paper": str(pdf_path),
                "collection": args.collection,
                "n_samples": len(samples),
                "timestamp": datetime.now().isoformat(),
                "mode": "gpu",
            },
        }
    else:
        # 휴리스틱 모드
        logger.info("=== 휴리스틱 모드 실행 (참고용, 논문 인용 불가) ===")

        for sample in samples:
            search_results = hybrid_retriever.search(
                collection_name=args.collection, query=sample.query
            )
            reranked = reranker.rerank(sample.query, search_results)
            sample.contexts = [r["content"] for r in reranked[:5]]
            sample.answer = " ".join(sample.contexts[:2])[:500]

        eval_results = evaluator.evaluate(samples)
        combined = {
            "heuristic_eval": eval_results,
            "metadata": {
                "paper": str(pdf_path),
                "collection": args.collection,
                "n_samples": len(samples),
                "timestamp": datetime.now().isoformat(),
                "mode": "heuristic",
                "warning": "참고용 — 논문 인용 불가",
            },
        }

    # 5. 결과 저장
    results_dir = Path("evaluation/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"c3_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    logger.info(f"결과 저장: {output_path}")

    # 6. 마크다운 표 출력
    print("\n" + "=" * 60)
    print("C3 실험 결과")
    print("=" * 60)

    if "cad_on_off" in combined:
        r = combined["cad_on_off"]
        print(f"\n### CAD on/off 비교 (alpha={r['alpha']})")
        print("| Metric | CAD On | CAD Off | Delta |")
        print("| --- | --- | --- | --- |")
        for key in [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
            "overall",
        ]:
            on_val = r["cad_on"].get(key)
            off_val = r["cad_off"].get(key)
            if on_val is not None and off_val is not None:
                delta = on_val - off_val
                sign = "+" if delta > 0 else ""
                print(f"| {key} | {on_val:.3f} | {off_val:.3f} | {sign}{delta:.3f} |")

    if "alpha_ablation" in combined:
        a = combined["alpha_ablation"]
        print(f"\n### Alpha Ablation (best: alpha={a['summary']['best_alpha']})")
        print("| Alpha | Faithfulness Delta | Overall Delta |")
        print("| --- | --- | --- |")
        for key, val in a["per_alpha"].items():
            f_d = val["faithfulness_delta"]
            o_d = val["overall_delta"]
            f_sign = "+" if f_d > 0 else ""
            o_sign = "+" if o_d > 0 else ""
            print(f"| {key} | {f_sign}{f_d:.3f} | {o_sign}{o_d:.3f} |")

    if "heuristic_eval" in combined:
        avg = combined["heuristic_eval"]["average"]
        print("\n### 휴리스틱 평가 (참고용)")
        print("| Metric | Score |")
        print("| --- | --- |")
        for key, val in avg.items():
            val_str = f"{val:.3f}" if val is not None else "N/A"
            print(f"| {key} | {val_str} |")
        print(
            "\n** 이 결과는 LLM 없이 토큰 오버랩으로 계산되었으므로 논문 인용에 사용할 수 없습니다."
        )

    print(f"\n결과 파일: {output_path}")


if __name__ == "__main__":
    main()
