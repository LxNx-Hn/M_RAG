from experiments.evaluators.official_ragas_runner_skeleton import (
    OfficialRAGASSample,
    validate_official_ragas_samples,
)


def _sample(*, ground_truth: str | None) -> OfficialRAGASSample:
    return OfficialRAGASSample(
        question="질문",
        answer="답변",
        contexts=["context"],
        ground_truth=ground_truth,
    )


def test_context_precision_requires_reference() -> None:
    errors = validate_official_ragas_samples(
        [_sample(ground_truth=None)], ["context_precision"]
    )

    assert errors == [
        "context_precision/context_recall require ground_truth/reference "
        "for sample indexes: 0"
    ]


def test_answer_relevancy_does_not_require_reference() -> None:
    errors = validate_official_ragas_samples(
        [_sample(ground_truth=None)], ["answer_relevancy"]
    )

    assert errors == []
