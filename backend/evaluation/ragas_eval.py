"""
RAG evaluation helpers used across the evaluation scripts.
"""

from __future__ import annotations

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
EVALUATION_ROOT = Path(__file__).resolve().parents[1]


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
    """Lightweight evaluator backed by an LLM judge."""

    def __init__(self, generator=None, judge_fn=None):
        if generator is None and judge_fn is None:
            raise ValueError("RAGASEvaluator requires either generator or judge_fn.")
        self.generator = generator
        self.judge_fn = judge_fn

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
        if not sample.contexts or not sample.answer:
            return 0.0
        prompt = (
            "Evaluate faithfulness of a RAG answer.\n"
            "Output only one label: SUPPORTED / PARTIAL / UNSUPPORTED\n\n"
            "[Criteria]\n"
            "- SUPPORTED: Core claims are grounded in context\n"
            "- PARTIAL: Some support exists but key details are weak/incomplete\n"
            "- UNSUPPORTED: Core claims are not supported by context\n\n"
            f"[Context]\n{' '.join(sample.contexts)[:2000]}\n\n"
            f"[Answer]\n{sample.answer[:1000]}\n\n"
            "Label:"
        )
        return self._extract_score(
            self._ask_judge(prompt, ["SUPPORTED", "PARTIAL", "UNSUPPORTED"])
        )

    def _compute_answer_relevancy(self, sample: EvalSample) -> float:
        if not sample.answer:
            return 0.0
        prompt = (
            "Evaluate answer relevancy for the question.\n"
            "Output only one label: RELEVANT / PARTIAL / IRRELEVANT\n\n"
            "[Criteria]\n"
            "- RELEVANT: Directly addresses the question intent\n"
            "- PARTIAL: Related but incomplete for the main intent\n"
            "- IRRELEVANT: Mostly unrelated to the question\n\n"
            f"[Question]\n{sample.query}\n\n"
            f"[Answer]\n{sample.answer[:1000]}\n\n"
            "Label:"
        )
        return self._extract_score(
            self._ask_judge(prompt, ["RELEVANT", "PARTIAL", "IRRELEVANT"])
        )

    def _compute_context_precision(self, sample: EvalSample) -> float:
        if not sample.contexts:
            return 0.0
        ctx_block = ""
        for idx, ctx in enumerate(sample.contexts[:5], start=1):
            ctx_block += f"[Context {idx}]\n{ctx[:300]}\n\n"
        ref_block = (
            f"[Reference Answer]\n{sample.ground_truth[:500]}\n\n"
            if sample.ground_truth
            else ""
        )
        prompt = (
            "Evaluate context precision of retrieval results.\n"
            "Output only one label: USEFUL / PARTIAL / NOISY\n\n"
            "[Criteria]\n"
            "- USEFUL: Most context is directly useful to solve the question\n"
            "- PARTIAL: Mixed useful and noisy context\n"
            "- NOISY: Mostly irrelevant context\n\n"
            f"[Question]\n{sample.query}\n\n"
            f"{ref_block}"
            f"{ctx_block}"
            "Label:"
        )
        return self._extract_score(
            self._ask_judge(prompt, ["USEFUL", "PARTIAL", "NOISY"])
        )

    def _compute_context_recall(self, sample: EvalSample) -> float:
        if not sample.contexts or not sample.ground_truth:
            return 0.0
        prompt = (
            "Evaluate context recall against the reference answer.\n"
            "Output only one label: COVERED / PARTIAL / MISSING\n\n"
            "[Criteria]\n"
            "- COVERED: Key evidence is sufficiently covered by retrieved context\n"
            "- PARTIAL: Only part of key evidence is covered\n"
            "- MISSING: Key evidence is mostly absent\n\n"
            f"[Reference Answer]\n{sample.ground_truth[:500]}\n\n"
            f"[Retrieved Context]\n{' '.join(sample.contexts)[:2000]}\n\n"
            "Label:"
        )
        return self._extract_score(
            self._ask_judge(prompt, ["COVERED", "PARTIAL", "MISSING"])
        )

    def _ask_judge(self, prompt: str, labels: Optional[list[str]] = None) -> str:
        try:
            if self.generator is not None:
                if labels:
                    return self.generator.rank_labels(prompt, labels)[0]
                return self.generator.generate_judge(prompt, max_new_tokens=32)
            assert self.judge_fn is not None
            return str(self.judge_fn(prompt, labels))
        except Exception as exc:
            logger.warning(
                "Judge call failed (%s: %s) - falling back to PARTIAL",
                type(exc).__name__,
                exc,
            )
            return "PARTIAL"

    @staticmethod
    def _extract_score(text: str) -> float:
        import re

        normalized = text.strip().upper()
        label_scores = {
            "SUPPORTED": 1.0,
            "RELEVANT": 1.0,
            "USEFUL": 1.0,
            "COVERED": 1.0,
            "PARTIAL": 0.5,
            "UNSUPPORTED": 0.0,
            "IRRELEVANT": 0.0,
            "NOISY": 0.0,
            "MISSING": 0.0,
        }
        for label, score in label_scores.items():
            if label in normalized:
                return score

        matches = re.findall(r"(?<!\d)(?:0(?:\.\d+)?|1(?:\.0+)?)(?!\d)", text.strip())
        if matches:
            score = float(matches[-1])
            return min(max(score, 0.0), 1.0)
        return 0.5

    @staticmethod
    def _mean(values: list[Optional[float]]) -> float:
        valid = [v for v in values if v is not None]
        return sum(valid) / max(len(valid), 1)


def load_test_queries(
    filepath: str = "evaluation/data/track1_queries.json",
    query_types: Optional[list[str]] = None,
) -> list[EvalSample]:
    path = Path(filepath)
    if not path.is_absolute():
        path = EVALUATION_ROOT / path
    if not path.exists():
        raise FileNotFoundError(f"Test queries file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    items = data.get("queries", data) if isinstance(data, dict) else data
    samples: list[EvalSample] = []
    for item in items:
        if query_types and item.get("type") not in query_types:
            continue
        ground_truth = item.get("ground_truth", "")
        if isinstance(ground_truth, str) and ground_truth.startswith("PAPER_SPECIFIC"):
            ground_truth = ""
        samples.append(EvalSample(query=item["query"], ground_truth=ground_truth))

    if not samples:
        raise ValueError(f"No evaluation samples loaded from {filepath}")
    return samples
