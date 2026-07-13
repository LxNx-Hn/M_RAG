"""Verify the numeric claims used by the current Korean and English manuscripts.

This script is read-only. It recomputes the controlled HyDE/CAD contrasts from
the retained 152-row gpt-4o score artifact, audits the CAD context identity, and
checks the direct SCD language-adherence values used in Tables 2 and 3.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SCORE_PATH = (
    ROOT / "experiments/results/evaluation/"
    "main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json"
)
GENERATION_PATH = (
    ROOT / "experiments/results/main_generation/"
    "main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
)
MANUSCRIPTS = [
    ROOT / "docs/PAPER/THESIS.md",
    ROOT / "docs/PAPER/THESIS_KO.md",
]
METRICS = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
)
CONTRASTS = (
    ("hyde_on__no_decoder_control", "hyde_off__no_decoder_control"),
    ("hyde_off__cad_only", "hyde_off__no_decoder_control"),
)
EXPECTED = {
    CONTRASTS[0]: {
        "faithfulness": (0.0734, -0.0248, 0.1777, (9, 6, 4)),
        "answer_relevancy": (0.0303, 0.0016, 0.0615, (9, 3, 7)),
        "context_precision": (-0.0679, -0.1702, 0.0194, (7, 6, 6)),
        "context_recall": (-0.0526, -0.1579, 0.0, (0, 1, 18)),
    },
    CONTRASTS[1]: {
        "faithfulness": (0.0023, -0.0903, 0.0952, (7, 9, 3)),
        "answer_relevancy": (-0.0715, -0.1792, 0.0004, (5, 12, 2)),
        "context_precision": (-0.0022, -0.0447, 0.0322, (2, 1, 16)),
        "context_recall": (-0.0526, -0.1579, 0.0, (0, 1, 18)),
    },
}
EXPECTED_LANGUAGE_CONFIGS = {
    "hyde_off__no_decoder_control": (0.5088, 8),
    "hyde_off__cad_only": (0.5175, 8),
    "hyde_off__scd_only": (0.7069, 4),
    "hyde_off__cad_scd": (0.7590, 3),
    "hyde_on__no_decoder_control": (0.6023, 3),
    "hyde_on__cad_only": (0.5099, 7),
    "hyde_on__scd_only": (0.8035, 2),
    "hyde_on__cad_scd": (0.7501, 3),
}


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def korean_ratio(text: str) -> float:
    hangul = sum(
        1
        for char in text
        if 0xAC00 <= ord(char) <= 0xD7A3
        or 0x1100 <= ord(char) <= 0x11FF
        or 0x3130 <= ord(char) <= 0x318F
    )
    latin = sum(1 for char in text if char.isascii() and char.isalpha())
    denominator = hangul + latin
    return round(hangul / denominator, 4) if denominator else 0.0


def verify_quality_contrasts() -> None:
    score_data = json.loads(SCORE_PATH.read_text(encoding="utf-8"))
    rows = score_data["per_sample"]
    assert len(rows) == 152
    assert all(row[metric] is not None for row in rows for metric in METRICS)
    by_key = {(row["query_id"], row["group"]): row for row in rows}
    query_ids = sorted({row["query_id"] for row in rows})
    assert len(query_ids) == 19

    rng = np.random.default_rng(20260713)
    resampling_index = rng.integers(0, 19, size=(200_000, 19))
    for contrast in CONTRASTS:
        on_group, off_group = contrast
        for metric in METRICS:
            delta = np.array(
                [
                    by_key[(query_id, on_group)][metric]
                    - by_key[(query_id, off_group)][metric]
                    for query_id in query_ids
                ],
                dtype=float,
            )
            boot_means = delta[resampling_index].mean(axis=1)
            lower, upper = np.quantile(boot_means, [0.025, 0.975], method="linear")
            wins = int((delta > 0.01).sum())
            losses = int((delta < -0.01).sum())
            ties = len(delta) - wins - losses
            observed = (
                round(float(delta.mean()), 4),
                round(float(lower), 4),
                round(float(upper), 4),
                (wins, losses, ties),
            )
            assert observed == EXPECTED[contrast][metric], (
                contrast,
                metric,
                observed,
                EXPECTED[contrast][metric],
            )


def verify_generation_and_language() -> None:
    rows = read_jsonl(GENERATION_PATH)
    assert len(rows) == 152
    by_key = {(row["query_id"], row["config_name"]): row for row in rows}
    query_ids = sorted({row["query_id"] for row in rows})

    for query_id in query_ids:
        baseline = by_key[(query_id, "hyde_off__no_decoder_control")]
        cad = by_key[(query_id, "hyde_off__cad_only")]
        assert cad["contexts"] == baseline["contexts"]
        assert cad["retrieved_chunk_ids"] == baseline["retrieved_chunk_ids"]
        assert cad["reranked_chunk_ids"] == baseline["reranked_chunk_ids"]

    ratios_by_config: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        ratios_by_config[row["config_name"]].append(
            korean_ratio(row["generated_answer"])
        )
    for config_name, (
        expected_mean,
        expected_drift,
    ) in EXPECTED_LANGUAGE_CONFIGS.items():
        ratios = ratios_by_config[config_name]
        assert len(ratios) == 19
        assert round(float(np.mean(ratios)), 4) == expected_mean
        assert sum(ratio < 0.5 for ratio in ratios) == expected_drift


def verify_manuscript_values() -> None:
    required = (
        "+0.0303",
        "+0.0016",
        "+0.0615",
        "+0.0023",
        "−0.0903",
        "+0.0952",
        "+0.2203",
        "+0.2198",
        "26/76",
        "12/76",
    )
    for path in MANUSCRIPTS:
        text = path.read_text(encoding="utf-8")
        for value in required:
            assert value in text, (path, value)


def main() -> None:
    verify_quality_contrasts()
    verify_generation_and_language()
    verify_manuscript_values()
    print("PASS: current thesis results reproduce from retained final artifacts.")


if __name__ == "__main__":
    main()
