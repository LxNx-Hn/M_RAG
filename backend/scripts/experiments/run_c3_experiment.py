"""
C3 thesis experiment runner for CAD on/off and alpha ablation.

Usage:
    python scripts/experiments/run_c3_experiment.py --paper-pdf data/paper_nlp_cad.pdf --collection c3_eval
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import CHROMA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="C3 CAD ablation experiment")
    parser.add_argument("--paper-pdf", required=True, help="Path to the evaluation PDF")
    parser.add_argument(
        "--collection",
        default="c3_eval",
        help="Collection name used for local indexing",
    )
    args = parser.parse_args()

    pdf_path = Path(args.paper_pdf)
    if not pdf_path.exists():
        logger.error("PDF file not found: %s", pdf_path)
        sys.exit(1)

    logger.info("=== Loading modules ===")
    from evaluation.ablation_study import AblationStudy
    from evaluation.ragas_eval import RAGASEvaluator, compare_cad_on_off, load_test_queries
    from modules.chunker import Chunker
    from modules.context_compressor import ContextCompressor
    from modules.embedder import Embedder
    from modules.generator import Generator
    from modules.hybrid_retriever import HybridRetriever
    from modules.pdf_parser import PDFParser
    from modules.query_expander import QueryExpander
    from modules.reranker import Reranker
    from modules.section_detector import SectionDetector
    from modules.vector_store import VectorStore

    pdf_parser = PDFParser()
    section_detector = SectionDetector()
    chunker = Chunker()
    embedder = Embedder()
    vector_store = VectorStore(persist_dir=str(CHROMA_DIR))
    hybrid_retriever = HybridRetriever(embedder=embedder, vector_store=vector_store)
    reranker = Reranker()
    generator = Generator()
    compressor = ContextCompressor(generator=generator)
    evaluator = RAGASEvaluator(generator=generator)

    logger.info("=== Indexing document %s ===", pdf_path)
    parsed = pdf_parser.parse(str(pdf_path))
    parsed = section_detector.detect(parsed)
    chunks = chunker.chunk_document(parsed, strategy="section")
    if not chunks:
        logger.error("No chunks were created from the input PDF.")
        sys.exit(1)

    embeddings = embedder.embed_texts([chunk.content for chunk in chunks])
    vector_store.add_chunks(args.collection, chunks, embeddings)
    hybrid_retriever.fit_bm25(args.collection)
    logger.info("Indexed %s chunks", len(chunks))

    logger.info("=== Loading evaluation queries ===")
    samples = load_test_queries(
        filepath="evaluation/data/track2_queries.json",
        query_types=["cad_ablation"],
    )
    logger.info("Loaded %s CAD evaluation samples", len(samples))
    if not samples:
        logger.error("No cad_ablation samples found in evaluation/data/track2_queries.json")
        sys.exit(1)

    logger.info("=== Running CAD on/off comparison ===")
    cad_on_off = compare_cad_on_off(
        evaluator=evaluator,
        samples=samples,
        generator=generator,
        collection_name=args.collection,
        retriever=hybrid_retriever,
        reranker=reranker,
        compressor=compressor,
        cad_alpha=0.5,
    )

    logger.info("=== Running CAD alpha ablation ===")
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
        "cad_on_off": cad_on_off,
        "alpha_ablation": alpha_results,
        "metadata": {
            "paper": str(pdf_path),
            "collection": args.collection,
            "n_samples": len(samples),
            "timestamp": datetime.now().isoformat(),
            "mode": "generator",
        },
    }

    results_dir = Path("evaluation/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"c3_{timestamp}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(combined, handle, ensure_ascii=False, indent=2)

    logger.info("Saved results to %s", output_path)
    print("\n=== C3 Results ===")
    print(f"CAD alpha baseline: {cad_on_off['alpha']}")
    print(
        f"Faithfulness delta (CAD on - off): {cad_on_off['faithfulness_delta']:.3f}"
    )
    print(
        f"Best alpha: {alpha_results['summary']['best_alpha']} "
        f"(delta={alpha_results['summary']['max_faithfulness_delta']:.3f})"
    )
    print(f"Result file: {output_path}")


if __name__ == "__main__":
    main()
