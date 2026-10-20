"""Cases chosen after the full 60-question analysis, with machine-checked evidence.

Each case illustrates one finding from QUESTION_TYPE_SUMMARY.csv and
ZERO_RELEVANCY_AUDIT.json. Every statement about what the input passages or
the answer contain is written as a check against the stored generation
record, so the thesis text and the raw runs cannot drift apart.
"""

from __future__ import annotations

import json

import pandas as pd

from analyze_questions import HERE, METRICS, NAMES, ROOT, run_records, write_json


def check(record, field, text, expected):
    body = (
        "\n".join(record["contexts"])
        if field == "contexts"
        else record["generated_answer"]
    )
    found = text.lower() in body.lower()
    assert (
        found == expected
    ), f"{record['query_id']} {field} {text!r}: expected {expected}"


def scores(obs, q, base, applied):
    out = {}
    for m in METRICS:
        a, b = obs.loc[(q, base), m], obs.loc[(q, applied), m]
        out[m] = {
            "base": None if pd.isna(a) else float(a),
            "applied": None if pd.isna(b) else float(b),
            "delta": (
                None if pd.isna(a) or pd.isna(b) else round(float(b) - float(a), 6)
            ),
        }
    return out


def main():
    plan = json.loads((HERE / "CASE_REVIEW_PLAN.json").read_text(encoding="utf-8"))
    from analyze_questions import sha

    for name, digest in plan["inputs"].items():
        assert sha(HERE / name) == digest, (
            "Recheck case selection after changed analysis: " + name
        )
    findings, cases = plan["findings"], plan["cases"]

    obs = pd.read_csv(ROOT / "FINALDOCS/DATA/FACTORIAL_OBSERVATIONS_60Q.csv").set_index(
        ["query_id", "condition"]
    )
    questions = {
        r["query_id"]: r
        for r in json.loads(
            (ROOT / "FINALDOCS/DATA/QUESTIONS_60Q.json").read_text(encoding="utf-8")
        )
    }
    raw = run_records()
    out = []
    for case in cases:
        q, base, applied = case["query_id"], case["base"], case["applied"]
        for side, field, text, expected in case["checks"]:
            check(raw[q, base if side == "base" else applied], field, text, expected)
        meta = questions[q]
        assert meta["short_title"] == case["title"]
        out.append(
            {
                **{k: v for k, v in case.items() if k != "checks"},
                "finding_text": findings[case["finding"]],
                "checks": [list(c) for c in case["checks"]],
                "query": meta["query"],
                "question_type": meta["question_type"],
                "document": meta["document_label"],
                "source_page": meta["source_page"],
                "answer_span": meta["answer_span"],
                "required_information": meta["required_information"],
                "comparison": f"{NAMES[base]} → {NAMES[applied]}",
                "same_input_passages": raw[q, base]["contexts"]
                == raw[q, applied]["contexts"],
                "same_ordered_chunk_ids": raw[q, base]["reranked_chunk_ids"]
                == raw[q, applied]["reranked_chunk_ids"],
                "scores": scores(obs, q, base, applied),
                "related_scores": [
                    {**r, "scores": scores(obs, q, r["base"], r["applied"])}
                    for r in case.get("related", [])
                ],
                "base_record": {
                    "answer": raw[q, base]["generated_answer"],
                    "contexts": raw[q, base]["contexts"],
                    "chunk_ids": raw[q, base]["reranked_chunk_ids"],
                },
                "applied_record": {
                    "answer": raw[q, applied]["generated_answer"],
                    "contexts": raw[q, applied]["contexts"],
                    "chunk_ids": raw[q, applied]["reranked_chunk_ids"],
                },
            }
        )
    write_json(HERE / "REVIEWED_CASES.json", out)
    write_json(
        HERE / "CASE_SELECTION.json",
        {
            "findings": findings,
            "cases": [
                {
                    "finding": c["finding"],
                    "title": c["title"],
                    "query_id": c["query_id"],
                    "comparison": f"{NAMES[c['base']]} → {NAMES[c['applied']]}",
                }
                for c in cases
            ],
        },
    )
    print(
        f"PASS: {len(out)} cases, {sum(len(c['checks']) for c in cases)} evidence checks"
    )


if __name__ == "__main__":
    main()
