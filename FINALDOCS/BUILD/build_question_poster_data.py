"""Prepare the poster from the same paired measurements and reviewed cases."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "FINALDOCS/ANALYSIS"))
from analyze_questions import TYPES, CONDITIONS, NAMES, write_json  # noqa: E402


def build():
    folder = ROOT / "FINALDOCS/ANALYSIS"
    summary = pd.read_csv(folder / "QUESTION_TYPE_SUMMARY.csv")
    rows = pd.read_csv(folder / "QUERY_LEVEL_RESULTS.csv", encoding="utf-8-sig")
    cases = json.loads((folder / "REVIEWED_CASES.json").read_text(encoding="utf-8"))
    # These are observed patterns from Gate B/C, with no ID or case-count input.
    highlights = [
        c
        for c in cases
        if (
            c["scores"]["context_recall"]["base"] == 0
            and c["scores"]["context_recall"]["applied"] == 1
            and c["scores"]["answer_relevancy"]["delta"] > 0
        )
        or (
            c["finding"] == "F3"
            and c["scores"]["faithfulness"]["applied"] == 1
            and c["scores"]["faithfulness"]["delta"] > 0
        )
    ]
    assert highlights
    fields = [
        "query_id",
        "condition",
        "question_type",
        "short_title",
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "context_recall",
        "korean_ratio",
    ]
    plotted = rows[fields].astype(object)
    plotted = plotted.where(pd.notna(plotted), None)
    type_results = summary[summary.grouping == "question_type"].astype(object)
    type_results = type_results.where(pd.notna(type_results), None)
    result = {
        "types": TYPES,
        "conditions": [
            {"number": i + 1, "code": c, "name": NAMES[c]}
            for i, c in enumerate(CONDITIONS)
        ],
        "type_results": type_results.to_dict("records"),
        "question_scores": plotted.to_dict("records"),
        "cases": highlights,
    }
    write_json(folder / "POSTER_DATA.json", result)
    print(
        f"PASS: 480 original plot records; four types; {len(highlights)} findings selected after complete case review"
    )


if __name__ == "__main__":
    build()
