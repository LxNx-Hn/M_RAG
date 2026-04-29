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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
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
    from evaluation.decoder_ablation import (
        DecoderAblationStudy,
        compare_cad_on_off,
    )
    from evaluation.ragas_eval import load_test_queries
    from modules.chunker import Chunker
    from modules.context_compressor import ContextCompressor
    from modules.embedder import Embedder
    from modules.generator import Generator
    from modules.hybrid_retriever import HybridRetriever
    from modules.pdf_parser import PDFParser
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
    eval_samples = load_test_queries(
        filepath="evaluation/data/track2_queries.json",
        query_types=["cad_ablation"],
    )
    logger.info("Loaded %s CAD evaluation samples", len(eval_samples))
    if not eval_samples:
        logger.error(
            "No cad_ablation samples found in evaluation/data/track2_queries.json"
        )
        sys.exit(1)

    # Convert EvalSample objects to dicts expected by DecoderAblationStudy.run_single
    test_samples = [
        {"query": s.query, "ground_truth": s.ground_truth} for s in eval_samples
    ]

    study = DecoderAblationStudy(
        generator=generator,
        hybrid_retriever=hybrid_retriever,
        reranker=reranker,
        compressor=compressor,
        collection_name=args.collection,
    )

    logger.info("=== Running CAD on/off comparison ===")
    cad_on_off = compare_cad_on_off(
        study=study, test_samples=test_samples, cad_alpha=0.5
    )

    logger.info("=== Running CAD alpha ablation ===")
    alpha_results = study.run_alpha_sweep(test_samples)

    # Build summary from alpha sweep
    best_alpha = None
    best_delta = float("-inf")
    baseline_halluc = cad_on_off.get("baseline", {}).get(
        "numeric_hallucination_rate", 0.0
    )
    for name, result in alpha_results.items():
        delta = result.get("numeric_hallucination_rate", 0.0) - baseline_halluc
        if delta < best_delta or best_alpha is None:
            best_delta = delta
            best_alpha = name

    combined = {
        "cad_on_off": cad_on_off,
        "alpha_ablation": {
            "results": alpha_results,
            "summary": {
                "best_alpha": best_alpha,
                "max_hallucination_reduction": abs(best_delta),
            },
        },
        "metadata": {
            "paper": str(pdf_path),
            "collection": args.collection,
            "n_samples": len(test_samples),
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
        f"Hallucination delta (CAD on - off): {cad_on_off['hallucination_delta']:.3f}"
    )
    print(f"Best alpha config: {best_alpha}")
    print(f"Result file: {output_path}")


if __name__ == "__main__":
    main()
