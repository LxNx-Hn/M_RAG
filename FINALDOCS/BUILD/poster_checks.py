"""Independently check the A1 poster tables against the question analysis.

The condition legend follows the thesis order; every number in the three
result tables (condition means, question-group means, single-technique time)
is recomputed from CONDITION_SUMMARY.csv and QUESTION_TYPE_SUMMARY.csv at two
decimals; bold marks only column maxima; statistical-test terms, standard
deviations, internal question IDs, middle dots, arrows and colon labels are
absent from the poster text.
"""

import re
import zipfile
from pathlib import Path

import pandas as pd
from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[2]
A = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
CONDITIONS = [
    "H0C0S0",
    "H1C0S0",
    "H0C1S0",
    "H0C0S1",
    "H1C1S0",
    "H1C0S1",
    "H0C1S1",
    "H1C1S1",
]
NAMES = dict(
    zip(
        CONDITIONS,
        [
            "미적용",
            "HyDE",
            "CAD",
            "SCD",
            "HyDE+CAD",
            "HyDE+SCD",
            "CAD+SCD",
            "HyDE+CAD+SCD",
        ],
    )
)
SCORE_METRICS = [
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
    "korean_ratio",
]
GROUPS = ["수치 질문", "방법 질문", "개념과 결과 질문"]
FORBIDDEN = re.compile(
    r"ANOVA|t-검정|p값|p<|표준편차|\bSD\b|ext_|track1_|H[01]C[01]S[01]|중앙값|·|→|[가-힣]: "
)


def cell_rows(table):
    rows = []
    for tr in table.findall("a:tr", A):
        row = []
        for tc in tr.findall("a:tc", A):
            runs = tc.findall(".//a:r", A)
            text = "\n".join(
                "".join(r.findtext("a:t", "", A) for r in p.findall("a:r", A))
                for p in tc.findall("a:txBody/a:p", A)
            )
            bold = any(
                r.find("a:rPr", A) is not None and r.find("a:rPr", A).get("b") == "1"
                for r in runs
            )
            row.append((text, bold))
        rows.append(row)
    return rows


def f2(v, sign=False):
    if sign and round(v, 2) == 0:
        return "0.00"
    return f"{v:+.2f}" if sign else f"{v:.2f}"


def check_bold(rows, cols, label, skip_last=False):
    body = rows[1 : len(rows) - (1 if skip_last else 0)]
    for c in cols:
        top = max(float(r[c][0]) for r in body)
        for i, r in enumerate(body, 1):
            assert r[c][1] == (
                float(r[c][0]) == top
            ), f"{label} bold differs at row {i} col {c}"


def validate_poster(pptx, svg=None):
    s = pd.read_csv(ROOT / "FINALDOCS/ANALYSIS/QUESTION_TYPE_SUMMARY.csv")
    s.loc[s.grouping == "전체", "level"] = "전체"
    cs = pd.read_csv(
        ROOT / "FINALDOCS/ANALYSIS/CONDITION_SUMMARY.csv", encoding="utf-8-sig"
    )

    def mean(level, code, metric):
        g = cs[(cs.level == level) & (cs.condition == code) & (cs.metric == metric)]
        assert len(g) == 1
        return g["mean"].iat[0]

    def pick(level, base, applied, metric):
        g = s[
            (s.level == level)
            & (s.base == base)
            & (s.applied == applied)
            & (s.metric == metric)
            & s.grouping.isin(["question_group", "전체"])
        ]
        assert len(g) == 1
        return g.iloc[0]

    with zipfile.ZipFile(pptx) as z:
        slide = ET.fromstring(z.read("ppt/slides/slide1.xml"))
        media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    tables = [cell_rows(t) for t in slide.findall(".//a:tbl", A)]
    assert len(tables) == 5, "Expected five native tables"
    assert len(media) >= 2, "Pipeline diagram or parallel-coordinate image missing"
    text = "".join(slide.xpath("//*[local-name()='t']/text()"))
    hit = FORBIDDEN.search(text)
    assert not hit, f"Forbidden poster text: {hit.group(0)}"

    labels = [f"{i} {NAMES[c]}" for i, c in enumerate(CONDITIONS, 1)]
    legend = tables[0]
    for i, code in enumerate(CONDITIONS, 1):
        expect = [
            labels[i - 1],
            "+" if code[1] == "1" else "−",
            "+" if code[3] == "1" else "−",
            "+" if code[5] == "1" else "−",
            "한국어 번역" if code[5] == "1" else "영어",
        ]
        assert [c[0] for c in legend[i]] == expect, f"Condition legend differs: row {i}"

    means = tables[2]
    for i, code in enumerate(CONDITIONS, 1):
        expect = [labels[i - 1]] + [f2(mean("전체", code, m)) for m in SCORE_METRICS]
        assert [c[0] for c in means[i]] == expect, f"Poster value differs: mean row {i}"
    check_bold(means, [1, 2, 3, 4, 5], "Condition mean table")

    groups = tables[3]
    for i, code in enumerate(CONDITIONS, 1):
        expect = [labels[i - 1]] + [
            f2(mean(g, code, m))
            for g in GROUPS
            for m in ("answer_relevancy", "faithfulness")
        ]
        assert [c[0] for c in groups[i]] == expect, f"Poster value differs: group row {i}"
    check_bold(groups, [1, 2, 3, 4, 5, 6], "Question group table")

    for i, a0 in enumerate(["H1C0S0", "H0C1S0", "H0C0S1"], 1):
        r = pick("전체", "H0C0S0", a0, "duration_seconds")
        assert [c[0] for c in tables[4][i]] == [
            NAMES[a0],
            f2(r.base_mean),
            f2(r.applied_mean),
            f2(r.mean_delta, True),
        ], f"Poster value differs: time row {i}"
    check_bold(tables[4], [2, 3], "Time table")
    return {"tables": 5, "result_rows_checked": 8 + 8 + 8 + 3, "decimals": 2}


def protocol_order(codes):
    expected = [f"H{h}C{c}S{s}" for s in (0, 1) for h in (0, 1) for c in (0, 1)]
    if codes != expected:
        raise AssertionError("S0/S1 protocol groups must each contain four conditions")


def poster_headings(labels):
    return any(
        re.fullmatch(
            r"\s*(?:\d{2}\s*)?(?:국문)?초록\s*|\s*(?:\d{2}\s*)?Abstract\s*", value, re.I
        )
        for value in labels
    )
