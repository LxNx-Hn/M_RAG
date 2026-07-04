"""Merge two scoring passes of the SAME judge over the SAME dataset.

Purpose: NIM endpoint judge calls occasionally fail transiently (timeouts /
5xx), leaving null metric cells. A second identical pass retries those calls;
this tool fills pass-1 nulls from pass 2 and recomputes the aggregates.

This is a retry mechanism, NOT judge mixing: it refuses unless both passes
used the same judge provider, judge model, metric set, and record count.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _mean_ignoring_none(values: list[Any]) -> float | None:
    xs = [v for v in values if isinstance(v, (int, float))]
    return round(sum(xs) / len(xs), 4) if xs else None


def _null_cells(per_sample: list[dict[str, Any]], metrics: list[str]) -> int:
    return sum(1 for s in per_sample for m in metrics if s.get(m) is None)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pass1", required=True)
    p.add_argument("--pass2", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    d1 = json.loads(Path(args.pass1).read_text(encoding="utf-8"))
    d2 = json.loads(Path(args.pass2).read_text(encoding="utf-8"))

    for key in ("provider", "model"):
        if (d1.get("judge") or {}).get(key) != (d2.get("judge") or {}).get(key):
            print(
                f"REFUSED: judge {key} differs between passes; merging would mix judges."
            )
            return 2
    if d1.get("metrics") != d2.get("metrics"):
        print("REFUSED: metric sets differ between passes.")
        return 2
    s1, s2 = d1["per_sample"], d2["per_sample"]
    if len(s1) != len(s2) or any(
        a.get("query_id") != b.get("query_id") or a.get("group") != b.get("group")
        for a, b in zip(s1, s2)
    ):
        print("REFUSED: per-sample rows do not align between passes.")
        return 2

    metrics = list(d1["metrics"])
    before = _null_cells(s1, metrics)
    merged_samples: list[dict[str, Any]] = []
    filled = 0
    for a, b in zip(s1, s2):
        row = dict(a)
        for m in metrics:
            if row.get(m) is None and b.get(m) is not None:
                row[m] = b[m]
                filled += 1
        merged_samples.append(row)
    after = _null_cells(merged_samples, metrics)

    scores = {m: _mean_ignoring_none([s[m] for s in merged_samples]) for m in metrics}
    groups = sorted({s["group"] for s in merged_samples})
    per_group = {
        g: {
            "n": sum(1 for s in merged_samples if s["group"] == g),
            **{
                m: _mean_ignoring_none(
                    [s[m] for s in merged_samples if s["group"] == g]
                )
                for m in metrics
            },
        }
        for g in groups
    }

    out = dict(d1)
    out["per_sample"] = merged_samples
    out["scores"] = scores
    out["per_group"] = per_group
    out["merge"] = {
        "passes": [args.pass1, args.pass2],
        "rule": (
            "pass1 values preferred; null cells (transient judge timeouts/5xx) "
            "filled from the identical pass2 retry. Same judge provider/model/"
            "metric set enforced."
        ),
        "null_cells_before": before,
        "null_cells_filled": filled,
        "null_cells_after": after,
    }
    Path(args.out).write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"merged -> {args.out}")
    print(f"null cells: {before} -> {after} (filled {filled})")
    print("aggregate:", json.dumps(scores, ensure_ascii=False))
    for g, v in per_group.items():
        print(f"{g}: {json.dumps(v, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
