"""Aggregate official judge scores for the main HyDE x CAD x SCD run.

Reads the merged scored file (per_sample rows carry group=config_name) plus the
generation JSONL (axis metadata), and writes:
  - main_config_scores.csv   : per-config metric means + scored-cell counts
  - main_axis_effects.json   : per-axis ON/OFF means and paired per-query deltas
  - stdout summary            : compact tables for the report

Descriptive aggregation only — no API, no model, no GT touch.
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


def _mean(xs: list[Any]) -> float | None:
    vals = [x for x in xs if isinstance(x, (int, float))]
    return round(sum(vals) / len(vals), 4) if vals else None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scores", required=True, help="Merged ragas_scores.json")
    p.add_argument("--generation", required=True, help="Main generation JSONL")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = p.parse_args()

    scores = json.loads(Path(args.scores).read_text(encoding="utf-8"))
    metrics: list[str] = list(scores["metrics"])
    rows: list[dict[str, Any]] = scores["per_sample"]

    axis_by_config: dict[str, dict[str, bool]] = {}
    for line in Path(args.generation).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        axis_by_config.setdefault(r["config_name"], {a: bool(r[a]) for a in AXES})

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- per-config table ----
    by_cfg: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for s in rows:
        by_cfg[s["group"]].append(s)

    csv_path = out_dir / "main_config_scores.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = ["config", *AXES]
        for m in metrics:
            header += [m, f"{m}_n_scored"]
        w.writerow(header)
        for cfg in CONFIG_ORDER:
            group = by_cfg.get(cfg, [])
            axes = axis_by_config.get(cfg, {})
            row: list[Any] = [cfg, *(axes.get(a) for a in AXES)]
            for m in metrics:
                vals = [s.get(m) for s in group]
                row += [_mean(vals), sum(1 for v in vals if v is not None)]
            w.writerow(row)

    # ---- axis effects with paired per-query deltas ----
    # value lookup: (config, query_id) -> metric row
    cell = {(s["group"], s["query_id"]): s for s in rows}

    def paired_deltas(axis: str, metric: str) -> list[float]:
        """ON-minus-OFF deltas over configs identical except for `axis`."""
        deltas: list[float] = []
        for cfg_on, ax_on in axis_by_config.items():
            if not ax_on[axis]:
                continue
            target = dict(ax_on)
            target[axis] = False
            cfg_off = next((c for c, a in axis_by_config.items() if a == target), None)
            if cfg_off is None:
                continue
            qids = {q for c, q in cell if c == cfg_on}
            for q in qids:
                v_on = cell.get((cfg_on, q), {}).get(metric)
                v_off = cell.get((cfg_off, q), {}).get(metric)
                if isinstance(v_on, (int, float)) and isinstance(v_off, (int, float)):
                    deltas.append(v_on - v_off)
        return deltas

    axis_effects: dict[str, Any] = {}
    for axis in AXES:
        on_rows = [
            s for s in rows if axis_by_config.get(s["group"], {}).get(axis) is True
        ]
        off_rows = [
            s for s in rows if axis_by_config.get(s["group"], {}).get(axis) is False
        ]
        per_metric: dict[str, Any] = {}
        for m in metrics:
            deltas = paired_deltas(axis, m)
            wins = sum(1 for d in deltas if d > 0.01)
            losses = sum(1 for d in deltas if d < -0.01)
            per_metric[m] = {
                "on_mean": _mean([s.get(m) for s in on_rows]),
                "off_mean": _mean([s.get(m) for s in off_rows]),
                "paired_mean_delta": _mean(deltas),
                "paired_n": len(deltas),
                "paired_wins": wins,
                "paired_losses": losses,
                "paired_ties": len(deltas) - wins - losses,
            }
        axis_effects[axis] = per_metric

    effects_path = out_dir / "main_axis_effects.json"
    effects_path.write_text(
        json.dumps(
            {
                "source_scores": args.scores,
                "source_generation": args.generation,
                "judge": scores.get("judge"),
                "metrics": metrics,
                "axis_effects": axis_effects,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"wrote {csv_path}")
    print(f"wrote {effects_path}")
    print()
    for axis in AXES:
        print(f"=== {axis} ===")
        for m in metrics:
            e = axis_effects[axis][m]
            print(
                f"  {m:18s} on={e['on_mean']} off={e['off_mean']} "
                f"paired_delta={e['paired_mean_delta']} "
                f"(n={e['paired_n']}, +{e['paired_wins']}/-{e['paired_losses']})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
