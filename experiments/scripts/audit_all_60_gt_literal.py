"""Fail-closed literal GT audit for all 60 thesis query units.

This combines the retained 19-query main split with the held-out 41-query
extension and applies one final acceptance rule: every reference must occur as
a contiguous normalized extract in the checked-in source PDF.

The construction history of the two sets is intentionally not rewritten here.
The retained 19 references are the existing verified ``answer_span`` values;
the 41 extension references are the manually extracted literal sidecar. What is
standardized is the *final acceptance criterion*, not how a candidate span was
first proposed.

No model, API, retrieval system, or judge is called by this script.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

import fitz

ROOT = Path(__file__).resolve().parents[2]
MAIN_SPLIT = ROOT / "experiments/data/query_splits/decoder_main_queries.json"
EXT_QUESTIONS = ROOT / "experiments/data/query_splits/extended_validation_questions.json"
EXT_GT = ROOT / "experiments/data/query_splits/extended_validation_literal_gt.json"
EXT_AUDIT = ROOT / "experiments/scripts/audit_extended_gt_literal.py"
DEFAULT_REPORT = ROOT / "experiments/results/analysis/all_60_gt_literal_audit.json"
EXPECTED_COMBINED_PAPERS = {
    "paper_nlp_rag": 15,
    "paper_nlp_cad": 15,
    "paper_nlp_raptor": 15,
    "paper_midm": 15,
}


def _load_extended_audit_module():
    spec = importlib.util.spec_from_file_location("extended_gt_audit", EXT_AUDIT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {EXT_AUDIT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _paper_path(paper: str) -> Path:
    return ROOT / "experiments/data/source_papers" / f"{paper}.pdf"


def _scan_all_pages(
    pdf: fitz.Document,
    span: str,
    page_contains_literal_span,
) -> list[int]:
    matches: list[int] = []
    for page_index in range(len(pdf)):
        if page_contains_literal_span(pdf, page_index, span):
            matches.append(page_index)
    return matches


def audit_main_19(page_contains_literal_span) -> dict[str, Any]:
    data = json.loads(MAIN_SPLIT.read_text(encoding="utf-8"))
    rows = data.get("queries") or []
    failures: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    if data.get("count") != 19 or len(rows) != 19:
        failures.append(
            {"type": "main_record_count", "observed": len(rows), "expected": 19}
        )

    ids = [str(row.get("query_id")) for row in rows]
    if len(ids) != len(set(ids)):
        failures.append({"type": "duplicate_main_query_id"})

    pdf_cache: dict[Path, fitz.Document] = {}
    try:
        for row in rows:
            qid = str(row.get("query_id"))
            papers = row.get("applicable_papers") or []
            span = str(row.get("answer_span") or "").strip()

            structural_error = None
            if len(papers) != 1:
                structural_error = "paper_cardinality"
            elif row.get("has_answer_span") is not True:
                structural_error = "has_answer_span_not_true"
            elif not span:
                structural_error = "empty_answer_span"
            elif row.get("gt_status") != "valid":
                structural_error = "gt_status_not_valid"
            elif row.get("answerability_status") != "answerable":
                structural_error = "not_answerable"

            if structural_error:
                failures.append({"query_id": qid, "type": structural_error})
                continue

            paper = str(papers[0])
            pdf_path = _paper_path(paper)
            if not pdf_path.is_file():
                failures.append(
                    {"query_id": qid, "paper": paper, "type": "source_pdf_missing"}
                )
                continue
            if pdf_path not in pdf_cache:
                pdf_cache[pdf_path] = fitz.open(pdf_path)

            page_matches = _scan_all_pages(
                pdf_cache[pdf_path], span, page_contains_literal_span
            )
            result = {
                "query_id": qid,
                "paper": paper,
                "span_chars": len(span),
                "literal_match": bool(page_matches),
                "matched_pages_zero_based": page_matches,
                "matched_pages_human": [page + 1 for page in page_matches],
            }
            results.append(result)
            if not page_matches:
                failures.append(
                    {
                        **result,
                        "type": "main_literal_span_not_found_in_source_pdf",
                        "answer_span": span,
                    }
                )
    finally:
        for pdf in pdf_cache.values():
            pdf.close()

    return {
        "split": "decoder_main_queries",
        "records": len(rows),
        "matched": sum(1 for item in results if item["literal_match"]),
        "failures": failures,
        "results": results,
        "passed": not failures and len(results) == 19,
        "paper_counts": dict(
            Counter((row.get("applicable_papers") or [None])[0] for row in rows)
        ),
    }


def audit_all_60() -> dict[str, Any]:
    module = _load_extended_audit_module()
    main_report = audit_main_19(module.page_contains_literal_span)
    ext_report = module.audit(EXT_GT, EXT_QUESTIONS)

    main_data = json.loads(MAIN_SPLIT.read_text(encoding="utf-8"))
    ext_data = json.loads(EXT_GT.read_text(encoding="utf-8"))
    main_rows = main_data.get("queries") or []
    ext_rows = ext_data.get("queries") or []

    failures: list[dict[str, Any]] = []
    failures.extend({"subset": "main19", **f} for f in main_report["failures"])
    failures.extend({"subset": "extension41", **f} for f in ext_report["failures"])

    main_ids = {str(row.get("query_id")) for row in main_rows}
    ext_ids = {str(row.get("query_id")) for row in ext_rows}
    overlap = sorted(main_ids & ext_ids)
    if overlap:
        failures.append({"type": "cross_split_query_id_overlap", "query_ids": overlap})

    combined_counts = Counter(
        (row.get("applicable_papers") or [None])[0]
        for row in [*main_rows, *ext_rows]
    )
    if dict(combined_counts) != EXPECTED_COMBINED_PAPERS:
        failures.append(
            {
                "type": "combined_paper_allocation",
                "observed": dict(combined_counts),
                "expected": EXPECTED_COMBINED_PAPERS,
            }
        )

    total_records = len(main_rows) + len(ext_rows)
    total_matched = main_report["matched"] + ext_report["matched"]
    if total_records != 60:
        failures.append(
            {"type": "combined_record_count", "observed": total_records, "expected": 60}
        )

    return {
        "schema_version": "all_60_gt_literal_audit.v1",
        "status": "passed" if not failures and total_matched == 60 else "failed",
        "policy": {
            "final_acceptance_rule": (
                "every RAGAS reference must be a contiguous normalized extract "
                "from one text block in its checked-in source PDF"
            ),
            "candidate_construction_history": (
                "not required to be identical; existing main references are retained "
                "and the extension uses the frozen literal sidecar"
            ),
            "model_or_api_calls_in_this_audit": False,
            "normalization": (
                "same Unicode-alphanumeric normalization and block-level "
                "source membership as audit_extended_gt_literal.py"
            ),
        },
        "records": total_records,
        "matched": total_matched,
        "paper_allocation": dict(combined_counts),
        "main_19": main_report,
        "extension_41": {
            "split": ext_report["gt_split"],
            "records": ext_report["records"],
            "matched": ext_report["matched"],
            "failures": ext_report["failures"],
            "results": ext_report["results"],
            "passed": ext_report["passed"],
        },
        "failures": failures,
        "passed": not failures and total_records == 60 and total_matched == 60,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    report = audit_all_60()
    if not args.no_write_report:
        out = Path(args.report)
        if not out.is_absolute():
            out = (ROOT / out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        "ALL-60 literal GT audit: "
        f"main={report['main_19']['matched']}/19 "
        f"extension={report['extension_41']['matched']}/41 "
        f"total={report['matched']}/{report['records']} "
        f"failures={len(report['failures'])} "
        f"passed={str(report['passed']).lower()}"
    )
    if report["failures"]:
        for failure in report["failures"]:
            print(json.dumps(failure, ensure_ascii=False))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
