"""
RAG evaluation helpers used across the evaluation scripts.
"""

import copy
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from ragas.metrics import context_recall
except ImportError:
    context_recall = "context_recall"

logger = logging.getLogger(__name__)


@dataclass
class EvalSample:
    """Single evaluation sample."""

    query: str
    ground_truth: str
    answer: str = ""
    contexts: list[str] = field(default_factory=list)
    pipeline: str = ""


@dataclass
class EvalResult:
    """Per-sample evaluation scores."""

    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    context_recall: Optional[float] = 0.0

    @property
    def average(self) -> float:
        values = [self.faithfulness, self.answer_relevancy, self.context_precision]
        if self.context_recall is not None:
            values.append(self.context_recall)
        return sum(values) / max(len(values), 1)


class RAGASEvaluator:
    """Lightweight evaluator with LLM-based and heuristic scoring paths."""

    def __init__(self, generator=None):
        self.generator = generator

    def evaluate(self, samples: list[EvalSample]) -> dict:
        """Evaluate all samples and return aggregate and per-sample scores."""
        metrics = ["faithfulness", "answer_relevancy", "context_precision"]
        if all(s.ground_truth for s in samples):
            metrics.append(context_recall)
        include_context_recall = context_recall in metrics

        results = [self._evaluate_single(sample) for sample in samples]

        avg_result = EvalResult(
            faithfulness=self._mean([r.faithfulness for r in results]),
            answer_relevancy=self._mean([r.answer_relevancy for r in results]),
            context_precision=self._mean([r.context_precision for r in results]),
            context_recall=(
                self._mean([r.context_recall for r in results])
                if include_context_recall
                else None
            ),
        )

        return {
            "average": {
                "faithfulness": avg_result.faithfulness,
                "answer_relevancy": avg_result.answer_relevancy,
                "context_precision": avg_result.context_precision,
                "context_recall": avg_result.context_recall,
                "overall": avg_result.average,
            },
            "per_sample": [
                {
                    "query": sample.query,
                    "faithfulness": result.faithfulness,
                    "answer_relevancy": result.answer_relevancy,
                    "context_precision": result.context_precision,
                    "context_recall": (
                        result.context_recall if include_context_recall else None
                    ),
                }
                for sample, result in zip(samples, results)
            ],
        }

    def _evaluate_single(self, sample: EvalSample) -> EvalResult:
        """Evaluate one sample."""
        if not self.generator:
            return self._evaluate_heuristic(sample)

        faithfulness = self._compute_faithfulness(sample)
        answer_relevancy = self._compute_answer_relevancy(sample)
        context_precision = self._compute_context_precision(sample)
        sample_context_recall = (
            self._compute_context_recall(sample) if sample.ground_truth else None
        )

        return EvalResult(
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            context_precision=context_precision,
            context_recall=sample_context_recall,
        )

    def _compute_faithfulness(self, sample: EvalSample) -> float:
        """Score whether the answer is grounded in the retrieved context."""
        if not sample.contexts or not sample.answer:
            return 0.0

        prompt = (
            "You are evaluating the faithfulness of a RAG answer.\n\n"
            "Return only a score between 0.0 and 1.0.\n\n"
            f"[Context]\n{' '.join(sample.contexts)[:2000]}\n\n"
            f"[Answer]\n{sample.answer[:1000]}\n\n"
            "Score:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_answer_relevancy(self, sample: EvalSample) -> float:
        """Score whether the answer is relevant to the query."""
        if not sample.answer:
            return 0.0

        prompt = (
            "You are evaluating answer relevancy for a RAG system.\n\n"
            "Return only a score between 0.0 and 1.0.\n\n"
            f"[Question]\n{sample.query}\n\n"
            f"[Answer]\n{sample.answer[:1000]}\n\n"
            "Score:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_context_precision(self, sample: EvalSample) -> float:
        """Score how much of the retrieved context is useful."""
        if not sample.contexts:
            return 0.0

        ctx_block = ""
        for idx, ctx in enumerate(sample.contexts[:5], start=1):
            ctx_block += f"[Context {idx}]\n{ctx[:300]}\n\n"

        prompt = (
            "You are evaluating context precision for a RAG system.\n\n"
            "Return only a score between 0.0 and 1.0.\n\n"
            f"[Question]\n{sample.query}\n\n"
            f"[Reference Answer]\n{sample.ground_truth[:500]}\n\n"
            f"{ctx_block}"
            "Score:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _compute_context_recall(self, sample: EvalSample) -> float:
        """Score whether the retrieved context covers the reference answer."""
        if not sample.contexts or not sample.ground_truth:
            return 0.0

        prompt = (
            "You are evaluating context recall for a RAG system.\n\n"
            "Return only a score between 0.0 and 1.0.\n\n"
            f"[Reference Answer]\n{sample.ground_truth[:500]}\n\n"
            f"[Retrieved Context]\n{' '.join(sample.contexts)[:2000]}\n\n"
            "Score:"
        )
        return self._extract_score(self.generator.generate_simple(prompt))

    def _evaluate_heuristic(self, sample: EvalSample) -> EvalResult:
        """Fallback token-overlap evaluator."""
        answer_tokens = set(sample.answer.lower().split())
        query_tokens = set(sample.query.lower().split())
        ctx_tokens = set()
        for ctx in sample.contexts:
            ctx_tokens.update(ctx.lower().split())

        faithfulness = len(answer_tokens & ctx_tokens) / max(len(answer_tokens), 1)
        relevancy = len(answer_tokens & query_tokens) / max(len(query_tokens), 1)

        if sample.ground_truth:
            gt_tokens = set(sample.ground_truth.lower().split())
            precision = len(ctx_tokens & gt_tokens) / max(len(ctx_tokens), 1)
            recall = len(gt_tokens & ctx_tokens) / max(len(gt_tokens), 1)
        else:
            precision = 0.0
            recall = None

        return EvalResult(
            faithfulness=min(faithfulness, 1.0),
            answer_relevancy=min(relevancy, 1.0),
            context_precision=min(precision, 1.0),
            context_recall=min(recall, 1.0) if recall is not None else None,
        )

    @staticmethod
    def _extract_score(text: str) -> float:
        """Extract a numeric score from model output."""
        import re

        match = re.search(r"(\d+\.?\d*)", text.strip())
        if match:
            score = float(match.group(1))
            return min(max(score, 0.0), 1.0)
        return 0.5

    @staticmethod
    def _mean(values: list[Optional[float]]) -> float:
        """Average non-None values."""
        valid = [v for v in values if v is not None]
        return sum(valid) / max(len(valid), 1)


def load_test_queries(
    filepath: str = "evaluation/test_queries.json",
    query_types: Optional[list[str]] = None,
) -> list[EvalSample]:
    """Load evaluation queries from JSON."""
    path = Path(filepath)
    if not path.exists():
        logger.warning("Test queries file not found: %s", filepath)
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("queries", data) if isinstance(data, dict) else data

    samples = []
    for item in items:
        if query_types and item.get("type") not in query_types:
            continue
        ground_truth = item.get("ground_truth", "")
        if isinstance(ground_truth, str) and ground_truth.startswith("PAPER_SPECIFIC"):
            ground_truth = ""
        samples.append(
            EvalSample(
                query=item["query"],
                ground_truth=ground_truth,
            )
        )

    return samples


def compare_cad_on_off(
    evaluator: "RAGASEvaluator",
    samples: list[EvalSample],
    generator,
    collection_name: str,
    retriever,
    reranker,
    compressor,
    cad_alpha: float = 0.5,
) -> dict:
    """Compare CAD enabled vs disabled over the same sample set."""
    from modules.cad_decoder import create_cad_processor

    def run(use_cad: bool) -> dict:
        run_samples = copy.deepcopy(samples)
        for sample in run_samples:
            search_results = retriever.search(
                collection_name=collection_name,
                query=sample.query,
            )
            search_results = reranker.rerank(sample.query, search_results)
            search_results = compressor.truncate_to_limit(search_results)
            sample.contexts = [r["content"] for r in search_results]
            context = "\n\n---\n\n".join(sample.contexts)

            logits_processor = None
            if use_cad:
                logits_processor = create_cad_processor(
                    generator, sample.query, alpha=cad_alpha
                )

            sample.answer = generator.generate(
                query=sample.query,
                context=context,
                template="qa",
                logits_processor=logits_processor,
            )

        return evaluator.evaluate(run_samples)

    logger.info("compare_cad_on_off: running CAD-on (alpha=%s)...", cad_alpha)
    cad_on = run(use_cad=True)

    logger.info("compare_cad_on_off: running CAD-off (baseline)...")
    cad_off = run(use_cad=False)

    return {
        "cad_on": cad_on["average"],
        "cad_off": cad_off["average"],
        "faithfulness_delta": (
            cad_on["average"]["faithfulness"] - cad_off["average"]["faithfulness"]
        ),
        "answer_relevancy_delta": (
            cad_on["average"]["answer_relevancy"]
            - cad_off["average"]["answer_relevancy"]
        ),
        "alpha": cad_alpha,
        "n_samples": len(samples),
    }
