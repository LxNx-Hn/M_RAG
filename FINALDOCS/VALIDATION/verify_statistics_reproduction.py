"""Recompute all statistics in isolation and compare every reported value."""

from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = HERE.parent / "DATA/FACTORIAL_STATISTICS_60Q.json"


def compare(a, b, where="report"):
    if isinstance(a, dict):
        if set(a) != set(b):
            raise AssertionError("Key mismatch: " + where)
        for k in a:
            if k != "software":
                compare(a[k], b[k], where + "." + k)
    elif isinstance(a, list):
        if len(a) != len(b):
            raise AssertionError("Length mismatch: " + where)
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, where + f"[{i}]")
    elif isinstance(a, float):
        if not math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12):
            raise AssertionError(f"Statistical value differs: {where}: {a} != {b}")
    elif a != b:
        raise AssertionError(f"Value differs: {where}: {a!r} != {b!r}")


def main():
    with tempfile.TemporaryDirectory(prefix="mrag_statistics_") as temporary:
        out = Path(temporary) / "statistics.json"
        subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(HERE / "analyze_factorial_60q.py"),
                "--output",
                str(out),
            ],
            check=True,
        )
        compare(
            json.loads(EXPECTED.read_text(encoding="utf-8")),
            json.loads(out.read_text(encoding="utf-8")),
        )
        expected_csv = (
            EXPECTED.with_name("FACTORIAL_OBSERVATIONS_60Q.csv")
            .read_bytes()
            .replace(b"\r\n", b"\n")
        )
        actual_csv = (
            out.with_name("FACTORIAL_OBSERVATIONS_60Q.csv")
            .read_bytes()
            .replace(b"\r\n", b"\n")
        )
        if actual_csv != expected_csv:
            raise AssertionError(
                "Derived query-by-condition observations differ from source recomputation"
            )
    print(
        "PASS: every descriptive value, test statistic, p, Holm adjustment, effect size, missing ID and sensitivity result independently reproduced"
    )


if __name__ == "__main__":
    main()
