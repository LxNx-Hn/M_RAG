"""Fail-closed literal-GT audit for the held-out extended validation references.

Every ``answer_span`` must be a contiguous extract from the declared page of the
checked-in source PDF after normalization of Unicode, whitespace, punctuation,
and PDF line-wrap artifacts. This script does not call any model or API and
never generates or rewrites GT.
"""

from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GT = ROOT / "experiments/data/query_splits/extended_validation_literal_gt.json"
DEFAULT_QUESTIONS = ROOT / "experiments/data/query_splits/extended_validation_questions.json"
DEFAULT_REPORT = ROOT / "experiments/results/analysis/extended_validation_gt_literal_audit.json"
EXPECTED_PAPERS = {
    "paper_nlp_rag": 10,
    "paper_nlp_cad": 11,
    "paper_nlp_raptor": 11,
    "paper_midm": 9,
}


def normalize_literal(text: str) -> str:
    """Canonical form used only for literal-source membership testing.

    Keeping only Unicode alphanumeric characters makes the check insensitive to
    PDF line wrapping, discretionary hyphens, smart punctuation, superscript
    rendering, and whitespace. Word/number order and wording still have to be a
    contiguous source substring; semantic paraphrases do not pass.
    """
    text = unicodedata.normalize("NFKC", text).casefold()
    return "".join(ch for ch in text if ch.isalnum())


def audit(gt_path: Path = DEFAULT_GT, questions_path: Path = DEFAULT_QUESTIONS) -> dict:
    gt_data = json.loads(gt_path.read_text(encoding="utf-8"))
    question_data = json.loads(questions_path.read_text(encoding="utf-8"))
    rows = gt_data.get("queries") or []
    question_rows = question_data.get("queries") or []
    failures: list[dict] = []
    results: list[dict] = []

    if gt_data.get("count") != 41 or len(rows) != 41:
        failures.append({"type": "record_count", "observed": len(rows), "expected": 41})
    if len(question_rows) != 41:
        failures.append({"type": "question_record_count", "observed": len(question_rows), "expected": 41})

    ids = [str(row.get("query_id")) for row in rows]
    question_ids = [str(row.get("query_id")) for row in question_rows]
    if len(ids) != len(set(ids)):
        failures.append({"type": "duplicate_gt_query_id"})
    if set(ids) != set(question_ids):
        failures.append(
            {
                "type": "gt_question_id_mismatch",
                "gt_only": sorted(set(ids) - set(question_ids)),
                "questions_only": sorted(set(question_ids) - set(ids)),
            }
        )

    paper_counts = Counter((row.get("applicable_papers") or [None])[0] for row in rows)
    if dict(paper_counts) != EXPECTED_PAPERS:
        failures.append(
            {
                "type": "paper_allocation",
                "observed": dict(paper_counts),
                "expected": EXPECTED_PAPERS,
            }
        )

    if gt_data.get("policy", {}).get("openai_or_llm_gt_generation") is not False:
        failures.append({"type": "gt_generation_policy_not_manual"})

    pdf_cache: dict[Path, fitz.Document] = {}
    try:
        for row in rows:
            qid = str(row.get("query_id"))
            papers = row.get("applicable_papers") or []
            span = str(row.get("answer_span") or "").strip()
            page_index = row.get("source_page")

            if len(papers) != 1:
                failures.append({"query_id": qid, "type": "paper_cardinality"})
                continue
            paper = str(papers[0])
            pdf_path = ROOT / "experiments/data/source_papers" / f"{paper}.pdf"

            structural_error = None
            if not span:
                structural_error = "empty_answer_span"
            elif row.get("gt_status") != "valid":
                structural_error = "gt_status_not_valid"
            elif row.get("answerability_status") != "answerable":
                structural_error = "not_answerable"
            elif row.get("validation_status") != "literal_span_human_audited":
                structural_error = "not_human_audited_literal"
            elif not isinstance(page_index, int) or page_index < 0:
                structural_error = "invalid_zero_based_source_page"
            elif not pdf_path.is_file():
                structural_error = "source_pdf_missing"

            if structural_error:
                failures.append({"query_id": qid, "type": structural_error})
                continue

            if pdf_path not in pdf_cache:
                pdf_cache[pdf_path] = fitz.open(pdf_path)
            pdf = pdf_cache[pdf_path]
            if page_index >= len(pdf):
                failures.append(
                    {
                        "query_id": qid,
                        "type": "source_page_out_of_range",
                        "source_page": page_index,
                        "pdf_pages": len(pdf),
                    }
                )
                continue

            page_text = pdf[page_index].get_text("text", sort=True)
            page_norm = normalize_literal(page_text)
            span_norm = normalize_literal(span)
            matched = bool(span_norm) and span_norm in page_norm
            result = {
                "query_id": qid,
                "paper": paper,
                "source_page_zero_based": page_index,
                "source_page_human": page_index + 1,
                "span_chars": len(span),
                "literal_match": matched,
            }
            results.append(result)
            if not matched:
                failures.append(
                    {
                        **result,
                        "type": "literal_span_not_found_on_declared_page",
                        "answer_span": span,
                    }
                )
    finally:
        for pdf in pdf_cache.values():
            pdf.close()

    return {
        "schema_version": "extended_validation_gt_literal_audit.v1",
        "gt_split": str(gt_path.relative_to(ROOT)),
        "question_split": str(questions_path.relative_to(ROOT)),
        "policy": {
            "gt_generation": "manual_source_extraction_only",
            "llm_or_openai_gt_generation": False,
            "source_page_indexing": "zero_based",
            "match": "contiguous alphanumeric-normalized substring on declared PDF page",
        },
        "records": len(rows),
        "matched": sum(1 for item in results if item["literal_match"]),
        "failures": failures,
        "results": results,
        "passed": not failures and len(results) == 41,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gt", default=str(DEFAULT_GT))
    parser.add_argument("--questions", default=str(DEFAULT_QUESTIONS))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    report = audit(Path(args.gt).resolve(), Path(args.questions).resolve())
    if not args.no_write_report:
        out = Path(args.report)
        if not out.is_absolute():
            out = (ROOT / out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"GT literal audit: matched={report['matched']}/{report['records']} "
        f"failures={len(report['failures'])} passed={str(report['passed']).lower()}"
    )
    if report["failures"]:
        for failure in report["failures"]:
            print(json.dumps(failure, ensure_ascii=False))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
