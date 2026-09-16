"""Analyze the retained 19-query final run plus the 41-query held-out extension.

This script is intentionally conservative:
- HyDE quality: hyde_on__no_decoder_control vs hyde_off__no_decoder_control.
- CAD quality: hyde_off__cad_only vs hyde_off__no_decoder_control.
- SCD target effect: direct Korean-character ratio from RAW generated answers.
- SCD language analysis reports both all four matched config pairs and the two
  HyDE-off pairs whose retrieved contexts must be byte-identical.
- The independent bootstrap unit is query, not generation/config cell.
- SCD RAGAS quality is not promoted to a causal effect here because the retained
  final thesis documents the translation/judge confound and handles it through
  a separate symmetric bilingual sensitivity analysis.

No model/API/network calls are made.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OLD_GENERATION = (
    ROOT / "results/main_generation/"
    "main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
)
DEFAULT_NEW_GENERATION = (
    ROOT / "results/extended_validation/"
    "extended-hyde-cad-scd-reference-scd__extended_validation_questions__"
    "extended_validation_generation.jsonl"
)
DEFAULT_OLD_SCORES = (
    ROOT / "results/evaluation/"
    "main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json"
)
DEFAULT_NEW_SCORES = (
    ROOT / "results/evaluation/"
    "extended-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json"
)
DEFAULT_OUT = ROOT / "results/analysis/extended_validation_60_analysis.json"

CONFIGS = [
    "hyde_off__no_decoder_control",
    "hyde_off__cad_only",
    "hyde_off__scd_only",
    "hyde_off__cad_scd",
    "hyde_on__no_decoder_control",
    "hyde_on__cad_only",
    "hyde_on__scd_only",
    "hyde_on__cad_scd",
]
QUALITY_CONTRASTS = {
    "hyde": ("hyde_on__no_decoder_control", "hyde_off__no_decoder_control"),
    "cad": ("hyde_off__cad_only", "hyde_off__no_decoder_control"),
}
SCD_PAIRS = [
    ("hyde_off__no_decoder_control", "hyde_off__scd_only"),
    ("hyde_off__cad_only", "hyde_off__cad_scd"),
    ("hyde_on__no_decoder_control", "hyde_on__scd_only"),
    ("hyde_on__cad_only", "hyde_on__cad_scd"),
]
SCD_HYDE_OFF_PAIRS = SCD_PAIRS[:2]
METRICS = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
)
MODEL = "K-intelligence/Midm-2.0-Base-Instruct"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def korean_ratio(text: str) -> float:
    hangul = sum(
        1
        for c in text
        if 0xAC00 <= ord(c) <= 0xD7A3
        or 0x1100 <= ord(c) <= 0x11FF
        or 0x3130 <= ord(c) <= 0x318F
    )
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    denom = hangul + latin
    return hangul / denom if denom else 0.0


def validate_generation(rows: list[dict[str, Any]], expected_queries: int) -> set[str]:
    expected_records = expected_queries * 8
    if len(rows) != expected_records:
        raise ValueError(
            f"expected {expected_records} generation rows, found {len(rows)}"
        )
    qids = {str(r["query_id"]) for r in rows}
    if len(qids) != expected_queries:
        raise ValueError(f"expected {expected_queries} query ids, found {len(qids)}")
    counts = Counter(str(r["config_name"]) for r in rows)
    if counts != Counter({name: expected_queries for name in CONFIGS}):
        raise ValueError(f"config counts mismatch: {counts}")
    for r in rows:
        if r.get("status") != "succeeded" or r.get("error") is not None:
            raise ValueError(
                f"failed generation row: {r.get('query_id')} {r.get('config_name')}"
            )
        if r.get("generation_model") != MODEL:
            raise ValueError("generation model mismatch")
        if r.get("decoding_mode") != "deterministic_greedy":
            raise ValueError("decoding mode mismatch")
        if len(r.get("contexts") or []) != 5:
            raise ValueError("context count mismatch")
        if r.get("use_cad") and float(r.get("cad_alpha")) != 0.5:
            raise ValueError("CAD alpha mismatch")
        if r.get("use_scd"):
            observed = (
                r.get("scd_mode"),
                float(r.get("scd_alpha")),
                float(r.get("scd_beta")),
                int(r.get("scd_t_start")),
            )
            if observed != ("reference_scd", 1.1, 0.9, 5):
                raise ValueError(f"reference_scd mismatch: {observed}")
        if r.get("use_hyde"):
            settings = (
                r.get("retrieval_reformulation", {}).get("hyde_generation_settings")
                or {}
            )
            observed = (
                float(settings.get("temperature", -1)),
                float(settings.get("top_p", -1)),
                bool(settings.get("do_sample")),
            )
            if observed != (0.1, 0.9, True):
                raise ValueError(f"HyDE settings mismatch: {observed}")

    by_key = {(str(r["query_id"]), str(r["config_name"])): r for r in rows}
    for qid in qids:
        base = by_key[(qid, "hyde_off__no_decoder_control")]
        cad = by_key[(qid, "hyde_off__cad_only")]
        if cad.get("contexts") != base.get("contexts"):
            raise ValueError(f"CAD context identity failed for {qid}")
        for off_cfg, on_cfg in SCD_HYDE_OFF_PAIRS:
            off = by_key[(qid, off_cfg)]
            on = by_key[(qid, on_cfg)]
            if on.get("contexts") != off.get("contexts"):
                raise ValueError(
                    f"HyDE-off SCD context identity failed for {qid}: "
                    f"{off_cfg} vs {on_cfg}"
                )
    return qids


def validate_scores(
    data: dict[str, Any], qids: set[str]
) -> dict[tuple[str, str], dict]:
    judge = data.get("judge") or {}
    if (judge.get("provider"), judge.get("model")) != ("openai", "gpt-4o"):
        raise ValueError(f"judge mismatch: {judge}")
    metrics = tuple(data.get("metrics") or ())
    if metrics != METRICS:
        raise ValueError(f"metric mismatch: {metrics}")
    rows = data.get("per_sample") or []
    expected_rows = len(qids) * 8
    if len(rows) != expected_rows:
        raise ValueError(f"score rows: expected {expected_rows}, found {len(rows)}")
    by_key: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = (str(row.get("query_id")), str(row.get("group")))
        if key[0] not in qids:
            raise ValueError(f"unexpected score query id: {key[0]}")
        if key in by_key:
            raise ValueError(f"duplicate score key: {key}")
        for metric in METRICS:
            value = row.get(metric)
            # RAGAS faithfulness can intentionally yield NaN when its
            # statement-generation stage returns an empty statement set.  The
            # raw evaluator serializes that value as JSON null.  Preserve the
            # row and handle coverage at the paired contrast level rather
            # than inventing a score or discarding its valid companion
            # metrics.
            if value is not None and (
                not isinstance(value, (int, float)) or not math.isfinite(float(value))
            ):
                raise ValueError(f"non-finite score cell: {key} {metric}={value!r}")
        by_key[key] = row
    return by_key


def bootstrap_mean_ci(
    values: np.ndarray, *, iterations: int, seed: int
) -> tuple[float, float, float]:
    if values.ndim != 1 or values.size == 0:
        raise ValueError("bootstrap requires a non-empty 1D vector")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(iterations, values.size))
    means = values[indices].mean(axis=1)
    lower, upper = np.quantile(means, [0.025, 0.975], method="linear")
    return float(values.mean()), float(lower), float(upper)


def quality_panel(
    score_maps: list[dict[tuple[str, str], dict]],
    qid_sets: list[set[str]],
    *,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    merged: dict[tuple[str, str], dict] = {}
    qids: set[str] = set()
    for score_map, qset in zip(score_maps, qid_sets):
        overlap = qids & qset
        if overlap:
            raise ValueError(f"query-id overlap across panels: {sorted(overlap)[:5]}")
        qids |= qset
        merged.update(score_map)

    out: dict[str, Any] = {"query_units": len(qids), "contrasts": {}}
    ordered_qids = sorted(qids)
    for name, (on_cfg, off_cfg) in QUALITY_CONTRASTS.items():
        metric_out: dict[str, Any] = {}
        for metric in METRICS:
            included_qids = [
                qid
                for qid in ordered_qids
                if merged[(qid, on_cfg)].get(metric) is not None
                and merged[(qid, off_cfg)].get(metric) is not None
            ]
            excluded_qids = [qid for qid in ordered_qids if qid not in included_qids]
            delta = np.array(
                [
                    float(merged[(qid, on_cfg)][metric])
                    - float(merged[(qid, off_cfg)][metric])
                    for qid in included_qids
                ],
                dtype=float,
            )
            mean, lower, upper = bootstrap_mean_ci(
                delta, iterations=iterations, seed=seed
            )
            wins = int(np.sum(delta > 0.01))
            losses = int(np.sum(delta < -0.01))
            metric_out[metric] = {
                "mean_delta_on_minus_off": round(mean, 4),
                "bootstrap_mean_95_ci": {
                    "lower": round(lower, 4),
                    "upper": round(upper, 4),
                },
                "wins_gt_0.01": wins,
                "losses_lt_neg_0.01": losses,
                "ties_abs_le_0.01": int(delta.size - wins - losses),
                "n_queries": int(delta.size),
                "excluded_query_ids_due_to_missing_score": excluded_qids,
            }
        out["contrasts"][name] = {
            "on": on_cfg,
            "off": off_cfg,
            "metrics": metric_out,
        }
    return out


def score_coverage(score_maps: list[dict[tuple[str, str], dict]]) -> dict[str, Any]:
    """Report metric-cell coverage without assigning values to empty cells."""
    missing_cells: list[dict[str, str]] = []
    expected = 0
    for score_map in score_maps:
        for (query_id, group), row in score_map.items():
            for metric in METRICS:
                expected += 1
                if row.get(metric) is None:
                    missing_cells.append(
                        {
                            "query_id": query_id,
                            "group": group,
                            "metric": metric,
                        }
                    )
    return {
        "expected_metric_cells": expected,
        "scored_metric_cells": expected - len(missing_cells),
        "missing_metric_cells": len(missing_cells),
        "missing_cells": missing_cells,
        "policy": (
            "Missing RAGAS cells remain explicit. Controlled contrasts use "
            "complete paired observations for the affected metric only."
        ),
    }


def _language_stats(
    *,
    by_key: dict[tuple[str, str], dict[str, Any]],
    qids: set[str],
    pairs: list[tuple[str, str]],
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    per_query_mean: list[float] = []
    pair_deltas: list[float] = []
    rescue_05 = 0
    drift_05 = 0
    harm = 0
    good = 0

    for qid in sorted(qids):
        local: list[float] = []
        for off_cfg, on_cfg in pairs:
            off = korean_ratio(by_key[(qid, off_cfg)]["generated_answer"])
            on = korean_ratio(by_key[(qid, on_cfg)]["generated_answer"])
            delta = on - off
            local.append(delta)
            pair_deltas.append(delta)
            if off < 0.5:
                drift_05 += 1
                if on >= 0.5:
                    rescue_05 += 1
            if off >= 0.7:
                good += 1
                if on < 0.65:
                    harm += 1
        per_query_mean.append(float(np.mean(local)))

    query_delta = np.array(per_query_mean, dtype=float)
    mean, lower, upper = bootstrap_mean_ci(
        query_delta, iterations=iterations, seed=seed
    )
    pair_arr = np.array(pair_deltas, dtype=float)
    wins = int(np.sum(pair_arr > 0.02))
    losses = int(np.sum(pair_arr < -0.02))
    return {
        "query_units": len(qids),
        "matched_scd_pairs": int(pair_arr.size),
        "pairs_per_query": len(pairs),
        "pair_level_mean_delta": round(float(pair_arr.mean()), 4),
        "query_clustered_mean_delta": round(mean, 4),
        "query_clustered_bootstrap_95_ci": {
            "lower": round(lower, 4),
            "upper": round(upper, 4),
        },
        "pair_wins_gt_0.02": wins,
        "pair_losses_lt_neg_0.02": losses,
        "pair_ties_abs_le_0.02": int(pair_arr.size - wins - losses),
        "drift_pairs_below_0.5": drift_05,
        "rescued_to_0.5": rescue_05,
        "already_korean_pairs_ge_0.7": good,
        "dragged_below_0.65": harm,
    }


def language_panel(
    generation_groups: list[list[dict[str, Any]]],
    qid_sets: list[set[str]],
    *,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    rows = [row for group in generation_groups for row in group]
    qids = set().union(*qid_sets)
    by_key = {(str(r["query_id"]), str(r["config_name"])): r for r in rows}
    return {
        "all_four_config_pairs": _language_stats(
            by_key=by_key,
            qids=qids,
            pairs=SCD_PAIRS,
            iterations=iterations,
            seed=seed,
        ),
        "hyde_off_same_context_pairs": _language_stats(
            by_key=by_key,
            qids=qids,
            pairs=SCD_HYDE_OFF_PAIRS,
            iterations=iterations,
            seed=seed,
        ),
        "metric_scope": "generated-text Korean character ratio; no LLM judge",
        "interpretation": (
            "hyde_off_same_context_pairs is the stricter controlled SCD language "
            "contrast because retrieval contexts are asserted identical."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-generation", default=str(DEFAULT_OLD_GENERATION))
    parser.add_argument("--new-generation", default=str(DEFAULT_NEW_GENERATION))
    parser.add_argument("--old-scores", default=str(DEFAULT_OLD_SCORES))
    parser.add_argument("--new-scores", default=str(DEFAULT_NEW_SCORES))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--bootstrap-iterations", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=20260713)
    args = parser.parse_args()

    old_gen = read_jsonl(Path(args.old_generation))
    new_gen = read_jsonl(Path(args.new_generation))
    old_qids = validate_generation(old_gen, 19)
    new_qids = validate_generation(new_gen, 41)
    if old_qids & new_qids:
        raise ValueError("original and extension query ids are not disjoint")

    old_scores_data = json.loads(Path(args.old_scores).read_text(encoding="utf-8"))
    new_scores_data = json.loads(Path(args.new_scores).read_text(encoding="utf-8"))
    old_scores = validate_scores(old_scores_data, old_qids)
    new_scores = validate_scores(new_scores_data, new_qids)

    report = {
        "method_contract": {
            "model": MODEL,
            "configs": CONFIGS,
            "reference_scd": {"alpha": 1.1, "beta": 0.9, "t_start": 5},
            "cad_alpha": 0.5,
            "judge_for_quality": "gpt-4o",
            "independent_statistical_unit": "query",
            "quality_scope": (
                "Only controlled HyDE and CAD contrasts are promoted. SCD RAGAS "
                "quality remains a separate sensitivity question."
            ),
        },
        "counts": {
            "original_queries": 19,
            "extension_queries": 41,
            "pooled_queries": 60,
            "original_generations": 152,
            "extension_generations": 328,
            "pooled_generations": 480,
        },
        "score_coverage": {
            "original_19": score_coverage([old_scores]),
            "extension_41": score_coverage([new_scores]),
            "pooled_60": score_coverage([old_scores, new_scores]),
        },
        "quality": {
            "original_19": quality_panel(
                [old_scores],
                [old_qids],
                iterations=args.bootstrap_iterations,
                seed=args.seed,
            ),
            "extension_41": quality_panel(
                [new_scores],
                [new_qids],
                iterations=args.bootstrap_iterations,
                seed=args.seed,
            ),
            "pooled_60": quality_panel(
                [old_scores, new_scores],
                [old_qids, new_qids],
                iterations=args.bootstrap_iterations,
                seed=args.seed,
            ),
        },
        "scd_language_adherence": {
            "original_19": language_panel(
                [old_gen],
                [old_qids],
                iterations=args.bootstrap_iterations,
                seed=args.seed,
            ),
            "extension_41": language_panel(
                [new_gen],
                [new_qids],
                iterations=args.bootstrap_iterations,
                seed=args.seed,
            ),
            "pooled_60": language_panel(
                [old_gen, new_gen],
                [old_qids, new_qids],
                iterations=args.bootstrap_iterations,
                seed=args.seed,
            ),
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
