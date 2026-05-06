"""
Decoder ablation study utilities.
"""

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

CAD_ALPHA_VALUES = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
SCD_BETA_VALUES = [0.1, 0.3, 0.5]


@dataclass
class DecoderConfig:
    """Single decoder ablation configuration."""

    name: str
    use_cad: bool = False
    use_scd: bool = False
    cad_alpha: float = 0.5
    scd_beta: float = 0.3


DECODER_CONFIGS = [
    DecoderConfig(name="Baseline (no decoder)"),
    DecoderConfig(name="CAD only (alpha=0.5)", use_cad=True, cad_alpha=0.5),
    DecoderConfig(name="SCD only (beta=0.3)", use_scd=True, scd_beta=0.3),
    DecoderConfig(
        name="CAD+SCD (alpha=0.5, beta=0.3)",
        use_cad=True,
        use_scd=True,
        cad_alpha=0.5,
        scd_beta=0.3,
    ),
]


def compute_language_drift_rate(answers: list[str]) -> float:
    """Compute the share of answers with low Korean-character ratio."""
    if not answers:
        return 0.0

    drifted = 0
    for answer in answers:
        if not answer.strip():
            continue
        non_ws = [c for c in answer if not c.isspace()]
        korean = [c for c in non_ws if 0xAC00 <= ord(c) <= 0xD7A3]
        ratio = len(korean) / max(len(non_ws), 1)
        if ratio < 0.3:
            drifted += 1

    return drifted / len(answers)


def compute_numeric_hallucination_rate(
    answers: list[str],
    ground_truths: list[str],
) -> float:
    """Compute the rate of extra numbers in answers that are absent from ground truth."""
    if not answers:
        return 0.0

    unit_pattern = r"(?:%|개|명|건|만|천|[KMBTG]B?|gb|mb|kb)"

    def extract_numbers(text: str) -> set[str]:
        raw = re.findall(
            r"\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)" + unit_pattern + r"?\b",
            text,
            re.IGNORECASE,
        )
        normalized = set()
        for num_str in raw:
            clean = num_str.replace(",", "")
            try:
                val = float(clean)
            except ValueError:
                continue
            if val < 10 and val == int(val):
                continue
            normalized.add(clean)
        return normalized

    hallucinated = 0
    for answer, gt in zip(answers, ground_truths):
        if not gt.strip():
            continue
        gt_nums = extract_numbers(gt)
        if not gt_nums:
            continue
        answer_nums = extract_numbers(answer)
        if answer_nums - gt_nums:
            hallucinated += 1

    evaluated = sum(1 for gt in ground_truths if gt.strip() and extract_numbers(gt))
    return hallucinated / max(evaluated, 1)


class DecoderAblationStudy:
    """Run decoder ablations over a single collection."""

    def __init__(
        self,
        generator,
        hybrid_retriever,
        reranker,
        compressor,
        collection_name: str = "papers",
        results_dir: str = "results",
    ):
        self.generator = generator
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker
        self.compressor = compressor
        self.collection_name = collection_name
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def run_single(self, config: DecoderConfig, test_samples: list[dict]) -> dict:
        """Run one decoder configuration across all samples."""
        from modules.scd_decoder import create_combined_processor

        answers = []
        for sample in test_samples:
            query = sample["query"]
            ground_truth = sample.get("ground_truth", "")

            results = self.hybrid_retriever.search(
                collection_name=self.collection_name,
                query=query,
            )
            reranked = self.reranker.rerank(query, results)
            compressed = self.compressor.compress(reranked, query)
            compressed = self.compressor.truncate_to_limit(compressed)
            context = "\n\n---\n\n".join(doc["content"] for doc in compressed)

            lp = create_combined_processor(
                generator=self.generator,
                query=query,
                use_cad=config.use_cad,
                cad_alpha=config.cad_alpha,
                use_scd=config.use_scd,
                scd_beta=config.scd_beta,
            )

            try:
                answer = self.generator.generate(
                    query=query,
                    context=context,
                    template="qa",
                    logits_processor=lp if (config.use_cad or config.use_scd) else None,
                )
            except Exception as exc:
                logger.warning("Generation failed for '%s': %s", query, exc)
                answer = ""

            answers.append(
                {
                    "query": query,
                    "answer": answer,
                    "ground_truth": ground_truth,
                }
            )

        answer_texts = [a["answer"] for a in answers]
        gt_texts = [a["ground_truth"] for a in answers]

        return {
            "config": config.name,
            "language_drift_rate": compute_language_drift_rate(answer_texts),
            "numeric_hallucination_rate": compute_numeric_hallucination_rate(
                answer_texts, gt_texts
            ),
            "answers": answers,
        }

    def run_table2(self, test_samples: list[dict]) -> dict:
        """Run the four default decoder configurations."""
        results = {}
        for config in DECODER_CONFIGS:
            logger.info("[Table 2] Running: %s", config.name)
            results[config.name] = self.run_single(config, test_samples)
        self._save(results, "table2_decoder_ablation.json")
        return results

    def run_alpha_sweep(self, test_samples: list[dict]) -> dict:
        """Run a CAD alpha sweep with SCD fixed."""
        results = {}
        for alpha in CAD_ALPHA_VALUES:
            config = DecoderConfig(
                name=f"CAD+SCD (alpha={alpha}, beta=0.3)",
                use_cad=True,
                use_scd=True,
                cad_alpha=alpha,
                scd_beta=0.3,
            )
            logger.info("[Alpha sweep] Running: %s", config.name)
            results[config.name] = self.run_single(config, test_samples)
        self._save(results, "table2_alpha_sweep.json")
        return results

    def run_beta_sweep(self, test_samples: list[dict]) -> dict:
        """Run an SCD beta sweep with CAD fixed."""
        results = {}
        for beta in SCD_BETA_VALUES:
            config = DecoderConfig(
                name=f"CAD+SCD (alpha=0.5, beta={beta})",
                use_cad=True,
                use_scd=True,
                cad_alpha=0.5,
                scd_beta=beta,
            )
            logger.info("[Beta sweep] Running: %s", config.name)
            results[config.name] = self.run_single(config, test_samples)
        self._save(results, "table2_beta_sweep.json")
        return results

    def _save(self, results: dict, filename: str):
        out_path = self.results_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info("Saved: %s", out_path)

    def print_summary(self, results: dict):
        """Print a compact decoder summary table."""
        print("\n" + "=" * 70)
        print("Table 2: CAD / SCD / Combined Ablation")
        print("=" * 70)
        print(f"{'Config':<35} {'Num Hall.':>10} {'Lang Drift':>10}")
        print("-" * 70)
        for name, result in results.items():
            drift = result.get("language_drift_rate", 0.0)
            halluc = result.get("numeric_hallucination_rate", 0.0)
            print(f"{name:<35} {halluc:>9.1%} {drift:>9.1%}")
        print("=" * 70)


def compare_cad_on_off(
    study: DecoderAblationStudy,
    test_samples: list[dict],
    cad_alpha: float = 0.5,
) -> dict:
    """Compare baseline (no decoder) vs CAD-only and return delta metrics.

    Returns dict with keys: baseline, cad_on, faithfulness_delta, alpha.
    """
    baseline_config = DecoderConfig(name="Baseline (no decoder)")
    cad_config = DecoderConfig(
        name=f"CAD only (alpha={cad_alpha})",
        use_cad=True,
        cad_alpha=cad_alpha,
    )
    baseline_result = study.run_single(baseline_config, test_samples)
    cad_result = study.run_single(cad_config, test_samples)

    baseline_halluc = baseline_result.get("numeric_hallucination_rate", 0.0)
    cad_halluc = cad_result.get("numeric_hallucination_rate", 0.0)

    return {
        "alpha": cad_alpha,
        "baseline": baseline_result,
        "cad_on": cad_result,
        "hallucination_delta": cad_halluc - baseline_halluc,
        "drift_delta": (
            cad_result.get("language_drift_rate", 0.0)
            - baseline_result.get("language_drift_rate", 0.0)
        ),
    }


def _load_cli_queries(queries_path: str) -> list[dict]:
    path = Path(queries_path)
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    if isinstance(payload, dict):
        items = payload.get("queries", payload.get("samples", []))
    else:
        items = payload

    return [
        {
            "query": item["query"],
            "ground_truth": item.get("ground_truth", ""),
        }
        for item in items
    ]


def _build_cli_study(collection_name: str) -> DecoderAblationStudy:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from config import CHROMA_DIR
    from modules.context_compressor import ContextCompressor
    from modules.embedder import Embedder
    from modules.generator import Generator
    from modules.hybrid_retriever import HybridRetriever
    from modules.reranker import Reranker
    from modules.vector_store import VectorStore

    embedder = Embedder()
    vector_store = VectorStore(persist_dir=str(CHROMA_DIR))
    hybrid_retriever = HybridRetriever(vector_store=vector_store, embedder=embedder)
    reranker = Reranker()
    generator = Generator()
    compressor = ContextCompressor(generator=generator)

    return DecoderAblationStudy(
        generator=generator,
        hybrid_retriever=hybrid_retriever,
        reranker=reranker,
        compressor=compressor,
        collection_name=collection_name,
    )


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Run decoder ablation from a query JSON file."
    )
    parser.add_argument(
        "--mode",
        choices=["decoder", "alpha-sweep", "beta-sweep"],
        default="decoder",
        help="Decoder ablation mode to run.",
    )
    parser.add_argument("--queries", required=True, help="Path to query JSON file.")
    parser.add_argument(
        "--papers",
        nargs="+",
        required=True,
        help="One or more ChromaDB collection names.",
    )
    parser.add_argument("--output", required=True, help="Output JSON path.")
    args = parser.parse_args()

    samples = _load_cli_queries(args.queries)
    results = {}

    for paper in args.papers:
        logger.info("Running %s for collection '%s'", args.mode, paper)
        study = _build_cli_study(paper)
        if args.mode == "alpha-sweep":
            results[paper] = study.run_alpha_sweep(samples)
        elif args.mode == "beta-sweep":
            results[paper] = study.run_beta_sweep(samples)
        else:
            results[paper] = study.run_table2(samples)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info("Saved results to %s", output_path)
