"""Replay selected 60-query thesis evidence from immutable stored excerpts.

This utility is read-only.  It does not load models, run retrieval, call a
judge, or edit experiment artifacts.  Its terminal output is the provenance
source for the terminal-style evidence panels in the final thesis package.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
MANIFEST = BASE / "generated" / "evidence_manifest_60q.json"


def load_cases() -> dict[str, dict[str, Any]]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {str(case["selection_rule"]): case for case in data["cases"]}


def score_text(score: dict[str, Any]) -> str:
    keys = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
    return ", ".join(
        (
            f"{key}={float(score[key]):.4f}"
            if score.get(key) is not None
            else f"{key}=missing"
        )
        for key in keys
    )


def record_block(case: dict[str, Any], side: str) -> list[str]:
    suffix = "a" if side == "A" else "b"
    config = case[f"config_{suffix}"]
    score = case[f"score_{suffix}"]
    answer = case[f"answer_{suffix}_exact_excerpt"]
    lines = [
        f"[{side}] config          : {config}",
        f"[{side}] stored RAGAS    : {score_text(score)}",
        f"[{side}] answer excerpt  :",
        answer,
    ]
    return lines


def show(case: dict[str, Any]) -> str:
    lines = [
        "=" * 72,
        "M-RAG 60-query stored-artifact replay",
        "=" * 72,
        f"selection rule   : {case['selection_rule']}",
        f"query ID         : {case['query_id']}",
        f"target paper     : {case['target_paper']}",
        f"question         : {case['query']}",
        f"source artifact  : {case['source_artifact']}",
    ]
    if case.get("config_b"):
        lines.extend(
            (
                f"contexts identical : {case['context_identity']}",
                f"retrieved IDs identical : {case['retrieved_identity']}",
                f"reranked IDs identical  : {case['reranked_identity']}",
            )
        )
    lines.extend(("", *record_block(case, "A")))
    if case.get("config_b"):
        lines.extend(("", *record_block(case, "B")))
    lines.append("=" * 72)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    show_parser = sub.add_parser("show")
    show_parser.add_argument("selection_rule")
    args = parser.parse_args()
    cases = load_cases()
    if args.command == "list":
        for key in cases:
            print(key)
        return 0
    case = cases.get(args.selection_rule)
    if not case:
        parser.error(f"unknown selection rule: {args.selection_rule}")
    print(show(case))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
