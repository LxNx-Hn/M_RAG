"""Official RAGAS runner skeleton.

Phase 2 intentionally provides dependency readiness and input validation only.
It must not execute RAGAS, OpenAI, external judges, or model inference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib.util import find_spec
from typing import Any


SUPPORTED_OFFICIAL_RAGAS_METRICS = (
    "faithfulness",
    "answer_relevancy",
    "response_relevancy",
    "context_precision",
    "context_recall",
)


@dataclass(frozen=True)
class OfficialRAGASSample:
    """Validated sample shape for a future official RAGAS execution path."""

    question: str
    answer: str
    contexts: list[str]
    ground_truth: str | None = None

    def to_ragas_record(self) -> dict[str, Any]:
        """Return records with both older and newer RAGAS field names."""
        record: dict[str, Any] = {
            "question": self.question,
            "user_input": self.question,
            "answer": self.answer,
            "response": self.answer,
            "contexts": self.contexts,
            "retrieved_contexts": self.contexts,
        }
        if self.ground_truth is not None:
            record["ground_truth"] = self.ground_truth
            record["reference"] = self.ground_truth
        return record


@dataclass(frozen=True)
class RAGASDependencyStatus:
    """Static dependency readiness result."""

    available: bool
    missing: list[str] = field(default_factory=list)
    message: str = ""


def check_ragas_dependency() -> RAGASDependencyStatus:
    """Check whether official RAGAS dependencies are importable.

    This function uses `find_spec` only. It does not import or execute RAGAS.
    """
    missing = [name for name in ("ragas", "datasets") if find_spec(name) is None]
    if missing:
        return RAGASDependencyStatus(
            available=False,
            missing=missing,
            message=(
                "Official RAGAS dependencies are not importable: "
                + ", ".join(missing)
                + ". Install them in an explicitly approved setup phase before "
                "running official RAGAS evaluation."
            ),
        )
    return RAGASDependencyStatus(
        available=True,
        message="Official RAGAS dependencies appear importable.",
    )


def validate_official_ragas_samples(
    samples: list[OfficialRAGASSample],
    metrics: list[str] | tuple[str, ...],
) -> list[str]:
    """Return validation errors without running RAGAS."""
    errors: list[str] = []
    if not samples:
        errors.append("At least one sample is required.")

    unsupported = sorted(set(metrics) - set(SUPPORTED_OFFICIAL_RAGAS_METRICS))
    if unsupported:
        errors.append("Unsupported official RAGAS metrics: " + ", ".join(unsupported))

    needs_reference = {"context_recall"}
    if needs_reference.intersection(metrics):
        missing_reference = [
            idx for idx, sample in enumerate(samples) if not sample.ground_truth
        ]
        if missing_reference:
            errors.append(
                "context_recall requires ground_truth/reference for sample indexes: "
                + ", ".join(str(idx) for idx in missing_reference)
            )

    for idx, sample in enumerate(samples):
        if not sample.question.strip():
            errors.append(f"sample {idx}: question/user_input is required.")
        if not sample.answer.strip():
            errors.append(f"sample {idx}: answer/response is required.")
        if not sample.contexts:
            errors.append(f"sample {idx}: contexts/retrieved_contexts are required.")
    return errors


def build_official_ragas_records(
    samples: list[OfficialRAGASSample],
) -> list[dict[str, Any]]:
    """Build official RAGAS-compatible records without executing evaluation."""
    return [sample.to_ragas_record() for sample in samples]


def run_official_ragas_evaluation(*_: Any, **__: Any) -> None:
    """Execution placeholder intentionally disabled in Phase 2."""
    raise RuntimeError(
        "Official RAGAS execution is disabled in Phase 2. "
        "Use check_ragas_dependency(), validate_official_ragas_samples(), and "
        "build_official_ragas_records() for dry validation only."
    )
