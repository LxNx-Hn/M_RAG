"""Analyze missing RAGAS score cells for the main HyDE x CAD x SCD run.

The official judge output can contain null metric cells. This analyzer does not
call any model or API; it reads an existing ``*.ragas_scores.json`` file and the
matching generation JSONL, then reports:

- null cell counts by config and query_id
- complete-case paired axis deltas
- null-as-0 and null-as-1 sensitivity for config means and axis deltas
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]  # experiments/
DEFAULT_OUT_DIR = ROOT / "results" / "analysis"

CONFIG_ORDER = [
    "hyde_off__no_decoder_control",
    "hyde_off__cad_only",
    "hyde_off__scd_only",
    "hyde_off__cad_scd",
    "hyde_on__no_decoder_control",
    "hyde_on__cad_only",
    "hyde_on__scd_only",
    "hyde_on__cad_scd",
]
AXES = ("use_hyde", "use_cad", "use_scd")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def _metric_value(
    row: dict[str, Any] | None,
    metric: str,
    *,
    null_value: float | None,
) -> float | None:
    if row is None:
        return null_value
    value = row.get(metric)
    if _is_number(value):
        return float(value)
    return null_value


def load_generation_axes(generation_path: Path) -> dict[str, dict[str, bool]]:
    axis_by_config: dict[str, dict[str, bool]] = {}
    for line in generation_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        config = record["config_name"]
        axis_by_config.setdefault(
            config,
            {axis: bool(record[axis]) for axis in AXES},
        )
    return axis_by_config


def null_counts_by_config(
    rows: list[dict[str, Any]],
    metrics: list[str],
) -> dict[str, dict[str, Any]]:
    by_config: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_config[row["group"]].append(row)

    counts: dict[str, dict[str, Any]] = {}
    for config in CONFIG_ORDER:
        group = by_config.get(config, [])
        metric_nulls = {
            metric: sum(1 for row in group if row.get(metric) is None)
            for metric in metrics
        }
        counts[config] = {
            "rows": len(group),
            "total_cells": len(group) * len(metrics),
            "null_cells": sum(metric_nulls.values()),
            "metric_nulls": metric_nulls,
        }
    return counts


def null_counts_by_query(
    rows: list[dict[str, Any]],
    metrics: list[str],
) -> dict[str, dict[str, Any]]:
    by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_query[str(row["query_id"])].append(row)

    counts: dict[str, dict[str, Any]] = {}
    for query_id in sorted(by_query):
        group = by_query[query_id]
        metric_nulls = {
            metric: sum(1 for row in group if row.get(metric) is None)
            for metric in metrics
        }
        counts[query_id] = {
            "rows": len(group),
            "total_cells": len(group) * len(metrics),
            "null_cells": sum(metric_nulls.values()),
            "metric_nulls": metric_nulls,
        }
    return counts


def config_metric_means(
    rows: list[dict[str, Any]],
    metrics: list[str],
    *,
    null_value: float | None,
) -> dict[str, dict[str, Any]]:
    by_config: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_config[row["group"]].append(row)

    means: dict[str, dict[str, Any]] = {}
    for config in CONFIG_ORDER:
        group = by_config.get(config, [])
        metric_means: dict[str, Any] = {}
        for metric in metrics:
            values = [
                value
                for row in group
                if (value := _metric_value(row, metric, null_value=null_value))
                is not None
            ]
            metric_means[metric] = {
                "mean": _mean(values),
                "n": len(values),
                "nulls": sum(1 for row in group if row.get(metric) is None),
            }
        means[config] = metric_means
    return means


def paired_axis_effects(
    rows: list[dict[str, Any]],
    metrics: list[str],
    axis_by_config: dict[str, dict[str, bool]],
    *,
    null_value: float | None,
) -> dict[str, dict[str, Any]]:
    cell = {(row["group"], str(row["query_id"])): row for row in rows}
    qids_by_config: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        qids_by_config[row["group"]].add(str(row["query_id"]))

    effects: dict[str, dict[str, Any]] = {}
    for axis in AXES:
        per_metric: dict[str, Any] = {}
        for metric in metrics:
            deltas: list[float] = []
            null_pair_count = 0
            for cfg_on, axes_on in axis_by_config.items():
                if not axes_on[axis]:
                    continue
                target_axes = dict(axes_on)
                target_axes[axis] = False
                cfg_off = next(
                    (
                        config
                        for config, axes in axis_by_config.items()
                        if axes == target_axes
                    ),
                    None,
                )
                if cfg_off is None:
                    continue
                qids = qids_by_config[cfg_on] | qids_by_config[cfg_off]
                for qid in qids:
                    row_on = cell.get((cfg_on, qid))
                    row_off = cell.get((cfg_off, qid))
                    raw_on = None if row_on is None else row_on.get(metric)
                    raw_off = None if row_off is None else row_off.get(metric)
                    if raw_on is None or raw_off is None:
                        null_pair_count += 1
                    value_on = _metric_value(row_on, metric, null_value=null_value)
                    value_off = _metric_value(row_off, metric, null_value=null_value)
                    if value_on is None or value_off is None:
                        continue
                    deltas.append(value_on - value_off)

            per_metric[metric] = {
                "paired_mean_delta": _mean(deltas),
                "paired_n": len(deltas),
                "null_pairs": null_pair_count,
                "paired_wins": sum(1 for delta in deltas if delta > 0.01),
                "paired_losses": sum(1 for delta in deltas if delta < -0.01),
                "paired_ties": sum(1 for delta in deltas if -0.01 <= delta <= 0.01),
            }
        effects[axis] = per_metric
    return effects


def analyze_null_sensitivity(
    scores: dict[str, Any],
    axis_by_config: dict[str, dict[str, bool]],
) -> dict[str, Any]:
    metrics: list[str] = list(scores["metrics"])
    rows: list[dict[str, Any]] = list(scores["per_sample"])
    total_cells = len(rows) * len(metrics)
    null_cells = sum(1 for row in rows for metric in metrics if row.get(metric) is None)

    return {
        "metrics": metrics,
        "row_count": len(rows),
        "total_cells": total_cells,
        "scored_cells": total_cells - null_cells,
        "null_cells": null_cells,
        "null_cell_rate": round(null_cells / total_cells, 4) if total_cells else None,
        "nulls_by_config": null_counts_by_config(rows, metrics),
        "nulls_by_query_id": null_counts_by_query(rows, metrics),
        "complete_case": {
            "config_means": config_metric_means(rows, metrics, null_value=None),
            "axis_effects": paired_axis_effects(
                rows,
                metrics,
                axis_by_config,
                null_value=None,
            ),
        },
        "sensitivity": {
            "null_as_0": {
                "config_means": config_metric_means(rows, metrics, null_value=0.0),
                "axis_effects": paired_axis_effects(
                    rows,
                    metrics,
                    axis_by_config,
                    null_value=0.0,
                ),
            },
            "null_as_1": {
                "config_means": config_metric_means(rows, metrics, null_value=1.0),
                "axis_effects": paired_axis_effects(
                    rows,
                    metrics,
                    axis_by_config,
                    null_value=1.0,
                ),
            },
        },
    }


def write_config_null_csv(report: dict[str, Any], path: Path) -> None:
    metrics = report["metrics"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["config", "rows", "total_cells", "null_cells", *metrics])
        for config in CONFIG_ORDER:
            item = report["nulls_by_config"].get(config, {})
            metric_nulls = item.get("metric_nulls", {})
            writer.writerow(
                [
                    config,
                    item.get("rows", 0),
                    item.get("total_cells", 0),
                    item.get("null_cells", 0),
                    *(metric_nulls.get(metric, 0) for metric in metrics),
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", required=True, help="Merged ragas_scores.json")
    parser.add_argument("--generation", required=True, help="Main generation JSONL")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    scores_path = Path(args.scores)
    generation_path = Path(args.generation)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scores = json.loads(scores_path.read_text(encoding="utf-8"))
    axis_by_config = load_generation_axes(generation_path)
    report = analyze_null_sensitivity(scores, axis_by_config)
    report.update(
        {
            "source_scores": str(scores_path),
            "source_generation": str(generation_path),
            "judge": scores.get("judge"),
        }
    )

    json_path = out_dir / "main_null_cell_sensitivity.json"
    csv_path = out_dir / "main_null_cells_by_config.csv"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
    write_config_null_csv(report, csv_path)

    print(f"wrote {json_path}")
    print(f"wrote {csv_path}")
    print(
        "null cells: "
        f"{report['null_cells']}/{report['total_cells']} "
        f"({report['null_cell_rate']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
