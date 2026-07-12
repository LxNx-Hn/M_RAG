"""Compare paired SCD effects in English- and Korean-normalized RAGAS panels.

The input panels must be official ``official_ragas_runner.py`` score JSON files
containing exactly the four HyDE-off configurations and the two requested
metrics.  This module performs analysis only; it never calls a model or API.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import statistics
import tempfile
from pathlib import Path
from typing import Any, Sequence

METRICS = ("faithfulness", "answer_relevancy")
PAIR_STRATA = {
    "cad_off": (
        "hyde_off__no_decoder_control",
        "hyde_off__scd_only",
    ),
    "cad_on": (
        "hyde_off__cad_only",
        "hyde_off__cad_scd",
    ),
}
EXPECTED_GROUPS = frozenset(group for pair in PAIR_STRATA.values() for group in pair)
EXPECTED_QUERIES_PER_GROUP = 19
EXPECTED_PAIRS = 38
PRACTICAL_THRESHOLD = 0.01
NORMALIZATION_PROTOCOL = "reference_scd.symmetric_normalization.gpt4o.v9"


class InputValidationError(ValueError):
    """Raised when a score panel cannot support the prescribed paired analysis."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InputValidationError(message)


def load_and_validate_panel(
    path: Path, panel_name: str, expected_target: str
) -> dict[str, Any]:
    """Load one official score panel and reject incomplete or ambiguous inputs."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputValidationError(
            f"{panel_name}: cannot read valid UTF-8 JSON: {exc}"
        ) from exc

    _require(isinstance(payload, dict), f"{panel_name}: top level must be an object")
    _require(
        payload.get("mode") == "official_scored_execution",
        f"{panel_name}: mode must be 'official_scored_execution'",
    )
    _require(
        payload.get("ragas_used") is True, f"{panel_name}: ragas_used must be true"
    )
    _require(
        payload.get("judge_api_used") is True,
        f"{panel_name}: judge_api_used must be true",
    )
    _require(
        payload.get("query_split") == "decoder_main_queries",
        f"{panel_name}: query_split must be decoder_main_queries",
    )

    metrics = payload.get("metrics")
    _require(isinstance(metrics, list), f"{panel_name}: metrics must be a list")
    _require(
        len(metrics) == len(METRICS) and set(metrics) == set(METRICS),
        f"{panel_name}: metrics must be exactly {list(METRICS)}",
    )

    judge = payload.get("judge")
    _require(isinstance(judge, dict), f"{panel_name}: judge metadata must be an object")
    for field in ("provider", "model"):
        _require(
            isinstance(judge.get(field), str) and bool(judge[field].strip()),
            f"{panel_name}: judge.{field} must be a non-empty string",
        )

    rows = payload.get("per_sample")
    _require(isinstance(rows, list), f"{panel_name}: per_sample must be a list")
    _require(
        payload.get("dataset_record_count") == len(rows),
        f"{panel_name}: dataset_record_count does not match per_sample length",
    )
    _require(
        len(rows) == len(EXPECTED_GROUPS) * EXPECTED_QUERIES_PER_GROUP,
        f"{panel_name}: expected 76 rows, found {len(rows)}",
    )

    generation_input = payload.get("generation_input")
    _require(
        isinstance(generation_input, dict),
        f"{panel_name}: generation_input provenance is required",
    )
    source_sha256 = generation_input.get("sha256")
    _require(
        isinstance(source_sha256, str)
        and len(source_sha256) == 64
        and all(char in "0123456789abcdef" for char in source_sha256),
        f"{panel_name}: generation_input.sha256 must be lowercase SHA-256",
    )
    _require(
        generation_input.get("record_count") == len(rows),
        f"{panel_name}: generation input record count does not match scores",
    )
    normalization = generation_input.get("symmetric_normalization")
    _require(
        isinstance(normalization, dict),
        f"{panel_name}: symmetric normalization provenance is required",
    )
    _require(
        normalization.get("present_records") == len(rows),
        f"{panel_name}: every generation record must carry normalization metadata",
    )
    _require(
        normalization.get("protocol_ids") == [NORMALIZATION_PROTOCOL],
        f"{panel_name}: protocol must be {NORMALIZATION_PROTOCOL}",
    )
    _require(
        normalization.get("target_languages") == [expected_target],
        f"{panel_name}: target language must be {expected_target}",
    )
    _require(
        normalization.get("all_selected_conditions_normalized_values") == [True],
        f"{panel_name}: all selected conditions must be symmetrically normalized",
    )
    _require(
        normalization.get("scopes") == ["hyde_off_identical_context_pairs"],
        f"{panel_name}: normalization scope is not the approved HyDE-off panel",
    )

    cells: dict[tuple[str, str], dict[str, float]] = {}
    groups: dict[str, set[str]] = {group: set() for group in EXPECTED_GROUPS}
    for index, row in enumerate(rows):
        _require(isinstance(row, dict), f"{panel_name}: row {index} must be an object")
        group = row.get("group")
        query_id = row.get("query_id")
        _require(
            isinstance(group, str) and group in EXPECTED_GROUPS,
            f"{panel_name}: row {index} has an unexpected group {group!r}",
        )
        _require(
            isinstance(query_id, str) and bool(query_id.strip()),
            f"{panel_name}: row {index} has an invalid query_id",
        )
        key = (group, query_id)
        _require(key not in cells, f"{panel_name}: duplicate cell {group}/{query_id}")

        scores: dict[str, float] = {}
        for metric in METRICS:
            value = row.get(metric)
            _require(
                isinstance(value, (int, float)) and not isinstance(value, bool),
                f"{panel_name}: {group}/{query_id}/{metric} is missing or null",
            )
            numeric = float(value)
            _require(
                math.isfinite(numeric) and 0.0 <= numeric <= 1.0,
                f"{panel_name}: {group}/{query_id}/{metric} must be finite in [0, 1]",
            )
            scores[metric] = numeric
        cells[key] = scores
        groups[group].add(query_id)

    observed_groups = {group for group, _ in cells}
    _require(
        observed_groups == EXPECTED_GROUPS,
        f"{panel_name}: expected exactly the four HyDE-off groups",
    )
    for group, query_ids in groups.items():
        _require(
            len(query_ids) == EXPECTED_QUERIES_PER_GROUP,
            f"{panel_name}: {group} must contain exactly 19 unique queries",
        )
    common_query_ids = next(iter(groups.values()))
    _require(
        all(query_ids == common_query_ids for query_ids in groups.values()),
        f"{panel_name}: all four groups must contain the same 19 query_ids",
    )

    return {
        "source": str(path),
        "score_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "generation_input": generation_input,
        "judge": {"provider": judge["provider"], "model": judge["model"]},
        "ragas_version": payload.get("ragas_version"),
        "embeddings": payload.get("embeddings"),
        "cells": cells,
        "query_ids": sorted(common_query_ids),
    }


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _bootstrap_mean_ci(
    clusters: list[list[float]], *, iterations: int, seed: int, key: str
) -> tuple[float, float]:
    digest = hashlib.sha256(f"{seed}:{key}".encode("utf-8")).digest()
    rng = random.Random(int.from_bytes(digest[:8], "big"))
    cluster_count = len(clusters)
    means: list[float] = []
    for _ in range(iterations):
        sample = [clusters[rng.randrange(cluster_count)] for _ in range(cluster_count)]
        flattened = [delta for cluster in sample for delta in cluster]
        means.append(statistics.mean(flattened))
    return _quantile(means, 0.025), _quantile(means, 0.975)


def _direction(value: float, tolerance: float = 1e-12) -> str:
    if value > tolerance:
        return "positive"
    if value < -tolerance:
        return "negative"
    return "zero"


def _ci_direction(lower: float, upper: float) -> str:
    if lower > 0:
        return "positive"
    if upper < 0:
        return "negative"
    return "overlaps_zero"


def _summarize_deltas(
    deltas: list[float],
    *,
    clusters: list[list[float]],
    iterations: int,
    seed: int,
    key: str,
) -> dict[str, Any]:
    lower, upper = _bootstrap_mean_ci(
        clusters, iterations=iterations, seed=seed, key=key
    )
    mean_delta = statistics.mean(deltas)
    tolerance = 1e-12
    return {
        "n": len(deltas),
        "bootstrap_clusters": len(clusters),
        "mean_delta": round(mean_delta, 6),
        "median_delta": round(statistics.median(deltas), 6),
        "wins": sum(delta > tolerance for delta in deltas),
        "losses": sum(delta < -tolerance for delta in deltas),
        "ties": sum(abs(delta) <= tolerance for delta in deltas),
        "practical_bands": {
            "gain_gt_0_01": sum(delta > PRACTICAL_THRESHOLD for delta in deltas),
            "loss_lt_minus_0_01": sum(delta < -PRACTICAL_THRESHOLD for delta in deltas),
            "within_plus_minus_0_01": sum(
                abs(delta) <= PRACTICAL_THRESHOLD for delta in deltas
            ),
        },
        "bootstrap_mean_95_ci": {
            "lower": round(lower, 6),
            "upper": round(upper, 6),
        },
        "direction": _direction(mean_delta),
        "ci_direction": _ci_direction(lower, upper),
    }


def analyze_panel(
    panel: dict[str, Any], *, panel_name: str, iterations: int, seed: int
) -> dict[str, Any]:
    """Compute SCD-on minus SCD-off effects overall and by CAD stratum."""
    cells = panel["cells"]
    query_ids = panel["query_ids"]
    deltas_by_stratum: dict[str, dict[str, list[float]]] = {}
    for stratum, (off_group, on_group) in PAIR_STRATA.items():
        deltas_by_stratum[stratum] = {
            metric: [
                cells[(on_group, query_id)][metric]
                - cells[(off_group, query_id)][metric]
                for query_id in query_ids
            ]
            for metric in METRICS
        }

    results: dict[str, Any] = {}
    for stratum in ("overall", *PAIR_STRATA):
        results[stratum] = {}
        for metric in METRICS:
            if stratum == "overall":
                deltas = [
                    delta
                    for item in PAIR_STRATA
                    for delta in deltas_by_stratum[item][metric]
                ]
                clusters = [
                    [
                        deltas_by_stratum["cad_off"][metric][index],
                        deltas_by_stratum["cad_on"][metric][index],
                    ]
                    for index in range(len(query_ids))
                ]
            else:
                deltas = deltas_by_stratum[stratum][metric]
                clusters = [[delta] for delta in deltas]
            results[stratum][metric] = _summarize_deltas(
                deltas,
                clusters=clusters,
                iterations=iterations,
                seed=seed,
                key=f"{panel_name}:{stratum}:{metric}",
            )

    _require(
        all(results["overall"][metric]["n"] == EXPECTED_PAIRS for metric in METRICS),
        f"{panel_name}: expected exactly 38 paired SCD contrasts",
    )
    return {
        "source": panel["source"],
        "score_sha256": panel["score_sha256"],
        "generation_input": panel["generation_input"],
        "judge": panel["judge"],
        "ragas_version": panel["ragas_version"],
        "embeddings": panel["embeddings"],
        "paired_results": results,
    }


def build_analysis(
    english_panel: dict[str, Any],
    korean_panel: dict[str, Any],
    *,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    """Analyze both panels and compare effect and confidence-interval directions."""
    _require(iterations > 0, "bootstrap iterations must be positive")
    _require(
        english_panel["judge"] == korean_panel["judge"],
        "English and Korean panels must use the same judge provider and model",
    )
    _require(
        english_panel["ragas_version"] == korean_panel["ragas_version"],
        "English and Korean panels must use the same RAGAS version",
    )
    _require(
        english_panel["embeddings"] == korean_panel["embeddings"],
        "English and Korean panels must use the same embeddings metadata",
    )
    _require(
        english_panel["query_ids"] == korean_panel["query_ids"],
        "English and Korean panels must contain the same 19 query_ids",
    )

    panels = {
        "english_normalized": analyze_panel(
            english_panel,
            panel_name="english_normalized",
            iterations=iterations,
            seed=seed,
        ),
        "korean_normalized": analyze_panel(
            korean_panel,
            panel_name="korean_normalized",
            iterations=iterations,
            seed=seed,
        ),
    }
    consistency: dict[str, Any] = {}
    for stratum in ("overall", *PAIR_STRATA):
        consistency[stratum] = {}
        for metric in METRICS:
            en = panels["english_normalized"]["paired_results"][stratum][metric]
            ko = panels["korean_normalized"]["paired_results"][stratum][metric]
            same_ci = en["ci_direction"] == ko["ci_direction"]
            consistency[stratum][metric] = {
                "english_direction": en["direction"],
                "korean_direction": ko["direction"],
                "direction_consistent": en["direction"] == ko["direction"],
                "english_ci_direction": en["ci_direction"],
                "korean_ci_direction": ko["ci_direction"],
                "ci_class_consistent": same_ci,
                "same_nonzero_ci_direction": same_ci
                and en["ci_direction"] in {"positive", "negative"},
            }

    return {
        "schema_version": 2,
        "effect": "SCD-on minus matched SCD-off",
        "settings": {
            "metrics": list(METRICS),
            "expected_pairs_per_panel": EXPECTED_PAIRS,
            "expected_pairs_per_cad_stratum": EXPECTED_QUERIES_PER_GROUP,
            "practical_band_threshold": PRACTICAL_THRESHOLD,
            "bootstrap": {
                "statistic": "query-clustered paired mean delta",
                "sampling_unit": "query_id",
                "clusters_per_panel": EXPECTED_QUERIES_PER_GROUP,
                "contrasts_per_cluster_overall": len(PAIR_STRATA),
                "iterations": iterations,
                "confidence_level": 0.95,
                "method": "percentile",
                "seed": seed,
            },
        },
        "panels": panels,
        "cross_language_consistency": consistency,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a compact human-readable summary from the JSON report."""
    lines = [
        "# SCD symmetric evaluation",
        "",
        "All deltas are paired `SCD-on - SCD-off` scores. Each panel contains "
        "38 pairs: 19 CAD-off and 19 CAD-on.",
        "",
        "| Stratum | Metric | EN mean delta [95% CI] | KO mean delta [95% CI] | "
        "Direction match | CI classes |",
        "|---|---|---:|---:|:---:|---|",
    ]
    panels = report["panels"]
    comparisons = report["cross_language_consistency"]
    for stratum in ("overall", *PAIR_STRATA):
        for metric in METRICS:
            en = panels["english_normalized"]["paired_results"][stratum][metric]
            ko = panels["korean_normalized"]["paired_results"][stratum][metric]
            comparison = comparisons[stratum][metric]
            en_ci = en["bootstrap_mean_95_ci"]
            ko_ci = ko["bootstrap_mean_95_ci"]
            lines.append(
                f"| {stratum} | {metric} | {en['mean_delta']:+.4f} "
                f"[{en_ci['lower']:+.4f}, {en_ci['upper']:+.4f}] | "
                f"{ko['mean_delta']:+.4f} "
                f"[{ko_ci['lower']:+.4f}, {ko_ci['upper']:+.4f}] | "
                f"{'yes' if comparison['direction_consistent'] else 'no'} | "
                f"{comparison['english_ci_direction']} / "
                f"{comparison['korean_ci_direction']} |"
            )
    settings = report["settings"]
    bootstrap = settings["bootstrap"]
    judge_model = panels["english_normalized"]["judge"]["model"]
    if judge_model == "gpt-4o":
        judge_boundary = (
            "The same `gpt-4o` model performed non-identity normalization and "
            "RAGAS judging."
        )
    else:
        judge_boundary = (
            "Non-identity normalization used `gpt-4o`, while RAGAS judging used "
            f"`{judge_model}`. This removes exact same-model judging but not "
            "same-provider or post-generation-normalization effects."
        )
    en_overall = panels["english_normalized"]["paired_results"]["overall"]
    ko_overall = panels["korean_normalized"]["paired_results"]["overall"]
    en_cad_on = panels["english_normalized"]["paired_results"]["cad_on"]
    ko_cad_on = panels["korean_normalized"]["paired_results"]["cad_on"]
    result_boundary = (
        "Overall faithfulness is "
        f"{en_overall['faithfulness']['mean_delta']:+.4f} "
        f"({en_overall['faithfulness']['ci_direction']}) in English and "
        f"{ko_overall['faithfulness']['mean_delta']:+.4f} "
        f"({ko_overall['faithfulness']['ci_direction']}) in Korean. Overall "
        f"answer relevancy is {en_overall['answer_relevancy']['mean_delta']:+.4f} "
        f"({en_overall['answer_relevancy']['ci_direction']}) in English and "
        f"{ko_overall['answer_relevancy']['mean_delta']:+.4f} "
        f"({ko_overall['answer_relevancy']['ci_direction']}) in Korean. The CAD-on "
        "answer-relevancy CI classes are "
        f"{en_cad_on['answer_relevancy']['ci_direction']} / "
        f"{ko_cad_on['answer_relevancy']['ci_direction']}."
    )
    lines.extend(
        [
            "",
            "Counts for exact wins/losses/ties and the `±0.01` practical bands "
            "are preserved in the JSON artifact.",
            "",
            f"Bootstrap: {bootstrap['iterations']} deterministic paired resamples, "
            f"seed {bootstrap['seed']}, percentile 95% CI.",
            "",
            "## Interpretation boundary",
            "",
            "This is a post-generation language-normalization sensitivity analysis, "
            "not an unbiased causal estimate of SCD. It improves on the earlier "
            "asymmetric panel by applying the same normalization policy to all four "
            "HyDE-off conditions and by comparing only matched identical-context "
            "SCD pairs.",
            "",
            result_boundary,
            "",
            judge_boundary
            + " In the Korean panel, validated identity was realized for 15/38 "
            "SCD-off answers and 27/38 SCD-on answers, so equal rules did not create "
            "equal transformation exposure. The panel contains 19 query clusters, "
            "and no human evaluation was run. Interpret this panel together with "
            "cross-judge robustness evidence; it is not a deployment or causal verdict.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english-scores", required=True, type=Path)
    parser.add_argument("--korean-scores", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    parser.add_argument("--bootstrap-iterations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260712)
    args = parser.parse_args(argv)

    english = load_and_validate_panel(
        args.english_scores, "english_normalized", expected_target="en"
    )
    korean = load_and_validate_panel(
        args.korean_scores, "korean_normalized", expected_target="ko"
    )
    report = build_analysis(
        english,
        korean,
        iterations=args.bootstrap_iterations,
        seed=args.seed,
    )
    json_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    markdown = render_markdown(report)
    _write_atomic(args.out_json, json_text)
    _write_atomic(args.out_md, markdown)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
