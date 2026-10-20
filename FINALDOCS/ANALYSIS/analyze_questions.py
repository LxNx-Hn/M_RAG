"""Question-level descriptive analysis of the stored 60 x 8 runs.

Inputs are the immutable observation table, the stored generation records and
the question annotations. The script computes only what the thesis reports:
raw scores, paired changes, type means and improved/worse/similar counts.
No model, API, median or significance test is used.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import fitz
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OBS = ROOT / "FINALDOCS/DATA/FACTORIAL_OBSERVATIONS_60Q.csv"
ANN = HERE / "QUERY_TYPE_ANNOTATIONS.csv"
TABLES = ROOT / "FINALDOCS/DATA/THESIS_TABLES_60Q.json"
QUESTIONS = ROOT / "FINALDOCS/DATA/QUESTIONS_60Q.json"

TYPES = ["사실 및 정의", "방법 및 절차", "결과 및 비교", "목적 및 기여"]
SHORT_TYPES = dict(zip(TYPES, ["사실·정의", "방법·절차", "결과·비교", "목적·기여"]))
CONDITIONS = [
    "H0C0S0",
    "H0C1S0",
    "H1C0S0",
    "H1C1S0",
    "H0C0S1",
    "H0C1S1",
    "H1C0S1",
    "H1C1S1",
]
NAMES = dict(
    zip(
        CONDITIONS,
        [
            "미적용",
            "CAD",
            "HyDE",
            "HyDE+CAD",
            "SCD",
            "CAD+SCD",
            "HyDE+SCD",
            "HyDE+CAD+SCD",
        ],
    )
)
NUMBERS = {c: i + 1 for i, c in enumerate(CONDITIONS)}
QUALITY = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
METRICS = QUALITY + ["korean_ratio", "duration_seconds"]
METRIC_NAMES = {
    "faithfulness": "근거 충실도",
    "answer_relevancy": "답변 관련성",
    "context_precision": "문맥 정밀도",
    "context_recall": "문맥 재현율",
    "korean_ratio": "한국어 문자 비율",
    "duration_seconds": "처리 시간",
}
SCORE_THRESHOLD = 0.05
TIME_THRESHOLD = 1.0

# Quality is compared only inside one evaluation language.
QUALITY_COMPARISONS = [
    ("영어", "H0C0S0", "H1C0S0"),
    ("영어", "H0C0S0", "H0C1S0"),
    ("영어", "H1C0S0", "H1C1S0"),
    ("영어", "H0C1S0", "H1C1S0"),
    ("한국어 번역", "H0C0S1", "H1C0S1"),
    ("한국어 번역", "H0C0S1", "H0C1S1"),
    ("한국어 번역", "H1C0S1", "H1C1S1"),
    ("한국어 번역", "H0C1S1", "H1C1S1"),
]
# Output language and time: SCD added to each HyDE/CAD state.
SCD_COMPARISONS = [
    ("H0C0S0", "H0C0S1"),
    ("H1C0S0", "H1C0S1"),
    ("H0C1S0", "H0C1S1"),
    ("H1C1S0", "H1C1S1"),
]


def label(base, applied):
    return f"{NAMES[base]} → {NAMES[applied]}"


def comparisons():
    """(label, base, applied, metrics, evaluation language) for every reported pair."""
    out = []
    for lang, base, applied in QUALITY_COMPARISONS:
        out.append((label(base, applied), base, applied, METRICS, lang))
    for base, applied in SCD_COMPARISONS:
        out.append(
            (
                label(base, applied),
                base,
                applied,
                ["korean_ratio", "duration_seconds"],
                None,
            )
        )
    return out


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def write_json(path, obj):
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def load():
    obs, ann = pd.read_csv(OBS), pd.read_csv(ANN, encoding="utf-8-sig")
    assert len(obs) == 480 and obs.query_id.nunique() == 60
    assert not obs.duplicated(["query_id", "condition"]).any()
    assert (obs.groupby("query_id").condition.nunique() == 8).all()
    assert set(obs.condition) == set(CONDITIONS)
    assert ann.query_id.is_unique and set(ann.query_id) == set(obs.query_id)
    assert ann.original_type.value_counts().to_dict() == {
        "방법 및 절차": 29,
        "결과 및 비교": 20,
        "사실 및 정의": 8,
        "목적 및 기여": 3,
    }
    return obs, ann


def source_questions():
    rows = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    return {r["query_id"]: r for r in rows}


def annotate(ann, questions):
    rows = []
    for r in ann.to_dict("records"):
        q = questions[r["query_id"]]
        assert q["question_type"] == r["original_type"]
        rows.append(
            {
                "query_id": q["query_id"],
                "query": q["query"],
                "document": r["document"],
                "question_type": q["question_type"],
                "source_page": q["source_page"],
                "answer_span": q["answer_span"],
                "required_information": q["required_information"],
                "short_title": q["short_title"],
                "answer_form": r["answer_form"],
                "information_units": (
                    "복수 항목" if r["element_count"] == "복수 요소" else "단일 항목"
                ),
                "type_review": q["type_review"],
            }
        )
    return pd.DataFrame(rows)


def _delta(a, b):
    if pd.isna(a) or pd.isna(b):
        return float("nan")
    return float(Decimal(str(b)) - Decimal(str(a)))


def deltas(obs, annotations):
    wide = obs.pivot(index="query_id", columns="condition", values=METRICS)
    rows = []
    for name, base, applied, metrics, lang in comparisons():
        for metric in metrics:
            if metric in QUALITY:
                assert (
                    base[-1] == applied[-1]
                ), "quality must stay in one evaluation language"
            for q in wide.index:
                a, b = wide.loc[q, (metric, base)], wide.loc[q, (metric, applied)]
                # Exclude stored zero-relevancy pairs from this comparison.
                # Preserve the raw values; judge flags are not in the records.
                zero = metric == "answer_relevancy" and (a == 0 or b == 0)
                rows.append(
                    {
                        "comparison": name,
                        "base": base,
                        "applied": applied,
                        "evaluation_language": lang or "",
                        "metric": metric,
                        "query_id": q,
                        "base_value": a,
                        "applied_value": b,
                        "delta": float("nan") if zero else _delta(a, b),
                        "relevancy_zero_excluded": bool(zero),
                    }
                )
    return pd.DataFrame(rows).merge(annotations, on="query_id", validate="many_to_one")


def direction_counts(x, metric):
    threshold = TIME_THRESHOLD if metric == "duration_seconds" else SCORE_THRESHOLD
    return (
        int((x > threshold).sum()),
        int((x < -threshold).sum()),
        int((x.abs() <= threshold).sum()),
    )


def summarize(d):
    rows = []
    d = d.assign(전체="전체 60개")
    for grouping in [
        "전체",
        "question_type",
        "document",
        "answer_form",
        "information_units",
    ]:
        for (comparison, metric, level), g in d.groupby(
            ["comparison", "metric", grouping], sort=False
        ):
            v = g.dropna(subset=["delta"])
            up, down, same = direction_counts(v.delta, metric)
            rows.append(
                {
                    "grouping": grouping,
                    "level": str(level),
                    "comparison": comparison,
                    "metric": metric,
                    "base": g.base.iat[0],
                    "applied": g.applied.iat[0],
                    "evaluation_language": g.evaluation_language.iat[0],
                    "n_questions": len(g),
                    "n": len(v),
                    "missing_pairs": len(g) - len(v),
                    "relevancy_zero_excluded": int(g.relevancy_zero_excluded.sum()),
                    "base_mean": v.base_value.mean(),
                    "applied_mean": v.applied_value.mean(),
                    "mean_delta": v.delta.mean(),
                    "improved": up,
                    "worse": down,
                    "similar": same,
                }
            )
    return pd.DataFrame(rows)


def run_records():
    manifest = json.loads(
        (ROOT / "FINALDOCS/DATA/evidence_manifest_60q.json").read_text(encoding="utf-8")
    )
    records = {}
    for name in manifest["sources"]:
        if not (name.endswith(".jsonl") and "generation" in name):
            continue
        for line in (
            (ROOT / name.replace("\\", "/")).read_text(encoding="utf-8").splitlines()
        ):
            r = json.loads(line)
            code = f"H{int(r['use_hyde'])}C{int(r['use_cad'])}S{int(r['use_scd'])}"
            key = (r["query_id"], code)
            assert key not in records
            records[key] = {**r, "source_artifact": name}
    assert len(records) == 480
    return records


def zero_relevancy(obs, annotations):
    """RAGAS 0.2.15 sets answer relevancy to 0 when the judge marks the answer noncommittal."""
    t = annotations.set_index("query_id").question_type
    w = obs.pivot(index="query_id", columns="condition", values="answer_relevancy")
    counts = []
    for c in CONDITIONS:
        row = {"condition": c, "name": NAMES[c], "전체": int((w[c] == 0).sum())}
        for typ in TYPES:
            row[typ] = int((w[c][t == typ] == 0).sum())
        counts.append(row)
    transitions = []
    for lang, base, applied in QUALITY_COMPARISONS:
        for typ in ["전체"] + TYPES:
            g = w if typ == "전체" else w[t == typ]
            x, y = g[base], g[applied]
            rest = (x > 0) & (y > 0)
            transitions.append(
                {
                    "comparison": label(base, applied),
                    "evaluation_language": lang,
                    "level": typ,
                    "n": len(g),
                    "zero_to_positive": int(((x == 0) & (y > 0)).sum()),
                    "positive_to_zero": int(((x > 0) & (y == 0)).sum()),
                    "zero_to_zero": int(((x == 0) & (y == 0)).sum()),
                    "zero_to_positive_ids": sorted(g.index[(x == 0) & (y > 0)]),
                    "positive_to_zero_ids": sorted(g.index[(x > 0) & (y == 0)]),
                    "mean_delta": float((y - x).mean()),
                    "n_both_positive": int(rest.sum()),
                    "mean_delta_both_positive": float((y[rest] - x[rest]).mean()),
                }
            )
    return counts, transitions


def retrieval_audit(records):
    """Which comparisons share the same five input passages, and why HyDE runs differ."""
    qs = sorted({k[0] for k in records})
    out = []
    pairs = [(b, a) for _, b, a in QUALITY_COMPARISONS] + SCD_COMPARISONS
    for base, applied in pairs:
        ctx = sum(
            records[q, base]["contexts"] == records[q, applied]["contexts"] for q in qs
        )
        both_hyde = base[1] == "1" and applied[1] == "1"
        row = {
            "comparison": label(base, applied),
            "n": len(qs),
            "same_input_passages": ctx,
            "same_ordered_chunk_ids": sum(
                records[q, base]["reranked_chunk_ids"]
                == records[q, applied]["reranked_chunk_ids"]
                for q in qs
            ),
        }
        if both_hyde:
            rf = [
                (
                    records[q, base]["retrieval_reformulation"],
                    records[q, applied]["retrieval_reformulation"],
                )
                for q in qs
            ]
            row["same_translation"] = sum(
                a["translated_query"] == b["translated_query"] for a, b in rf
            )
            row["same_hypothetical_document"] = sum(
                a["hyde_document"] == b["hyde_document"] for a, b in rf
            )
        out.append(row)
    settings = {
        json.dumps(
            records[q, code]["retrieval_reformulation"]["hyde_generation_settings"],
            sort_keys=True,
        )
        for q in qs
        for code in CONDITIONS
        if code[1] == "1"
    }
    sparse = (
        pd.Series([records[q, "H0C0S0"]["sparse_result_count"] for q in qs])
        .value_counts()
        .sort_index()
    )
    return {
        "pairs": out,
        "hyde_generation_settings": [json.loads(s) for s in settings],
        "cause": "HyDE의 번역문과 가상 문서는 조건마다 표본추출(do_sample=True, temperature=0.1, top_p=0.9)로 새로 생성되어 저장되었다. HyDE를 포함한 두 조건의 밀집 검색 입력이 달라지므로 재정렬 후 입력 구간도 달라질 수 있다.",
        "bm25_candidates_per_question": {str(k): int(v) for k, v in sparse.items()},
    }


def main():
    obs, ann = load()
    annotations = annotate(ann, source_questions())
    annotations.to_csv(
        HERE / "QUESTION_CLASSIFICATION_60Q.csv", index=False, encoding="utf-8-sig"
    )
    obs.merge(annotations, on="query_id", validate="many_to_one").to_csv(
        HERE / "QUERY_LEVEL_RESULTS.csv", index=False, encoding="utf-8-sig"
    )
    d = deltas(obs, annotations)
    d.to_csv(HERE / "QUERY_LEVEL_DELTAS.csv", index=False, encoding="utf-8-sig")
    s = summarize(d)
    s.to_csv(HERE / "QUESTION_TYPE_SUMMARY.csv", index=False, encoding="utf-8-sig")
    counts, transitions = zero_relevancy(obs, annotations)
    write_json(
        HERE / "ZERO_RELEVANCY_AUDIT.json",
        {
            "rule": "RAGAS 0.2.15 ResponseRelevancy: score = mean cosine x int(not noncommittal)",
            "counts": counts,
            "transitions": transitions,
        },
    )
    records = run_records()
    write_json(HERE / "CONTEXT_IDENTITY_AUDIT.json", retrieval_audit(records))
    missing = obs[obs[QUALITY].isna().any(axis=1)][["query_id", "condition"]]
    write_json(
        HERE / "MISSINGNESS_AUDIT.json",
        {
            "records": 480,
            "ragas_cells": 1920,
            "missing_cells": int(obs[QUALITY].isna().sum().sum()),
            "missing_rows": missing.to_dict("records"),
            "rule": "결측이 있는 질문은 해당 비교의 기준·적용 평균 모두에서 제외하며 값을 대체하지 않는다",
        },
    )
    pdfs = {
        "CAD": "paper_nlp_cad",
        "RAPTOR": "paper_nlp_raptor",
        "RAG Survey": "paper_nlp_rag",
        "Mi:dm": "paper_midm",
    }
    pages = []
    for r in annotations.itertuples():
        name = pdfs[r.document]
        with fitz.open(ROOT / f"experiments/data/source_papers/{name}.pdf") as pdf:
            page = int(r.source_page)
            assert 1 <= page <= len(pdf)
            pages.append(
                {
                    "query_id": r.query_id,
                    "source_pdf": f"experiments/data/source_papers/{name}.pdf",
                    "source_page": page,
                    "answer_span": r.answer_span,
                    "page_text": pdf[page - 1].get_text(),
                }
            )
    write_json(HERE / "SOURCE_PAGE_AUDIT.json", pages)
    write_json(
        HERE / "ANALYSIS_PROVENANCE.json",
        {
            "inputs": {
                p.relative_to(ROOT).as_posix(): sha(p) for p in [OBS, ANN, QUESTIONS]
            },
            "classification_sha256": sha(HERE / "QUESTION_CLASSIFICATION_60Q.csv"),
            "question_types": {
                t: int((annotations.question_type == t).sum()) for t in TYPES
            },
            "comparisons": [[c[0], c[1], c[2], c[4]] for c in comparisons()],
            "delta_rows": len(d),
            "rules": {
                "quality": "같은 평가 언어(SCD 미적용끼리, SCD 적용끼리)의 두 조건만 비교",
                "score_change": "0.05 초과 개선, -0.05 미만 악화, 경계 포함 사이는 비슷함",
                "time_change": "1초 초과 증가, -1초 미만 감소, 사이는 비슷함",
                "missing": "결측 질문은 해당 비교의 두 평균에서 함께 제외",
            },
            "status": "저장된 측정값의 질문별 기술 분석",
        },
    )
    print(
        f"PASS: 60 questions x 8 conditions; {len(d)} paired changes; {len(s)} summaries"
    )


if __name__ == "__main__":
    main()
