"""Independently check the A1 poster table against the question analysis.

Every number in the question-group table (five metrics by question group for
the eight conditions) is recomputed from CONDITION_SUMMARY.csv at two
decimals; bold marks displayed maxima (passage-based metrics within the SCD-off
and SCD-on rows separately); statistical-test terms, standard
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
    return f"{v:+.2f}".replace("-", "−") if sign else f"{v:.2f}"


def check_bold(rows_all, cols, label, skip_last=False, start=1, rows=None):
    """Bold marks exactly the displayed maxima of each column within the given rows."""
    body = (
        [rows_all[i] for i in rows]
        if rows is not None
        else rows_all[start : len(rows_all) - (1 if skip_last else 0)]
    )
    for c in cols:
        top = max(float(r[c][0].replace("−", "-")) for r in body)
        for i, r in enumerate(body, 1):
            assert r[c][1] == (
                float(r[c][0].replace("−", "-")) == top
            ), f"{label} bold differs at row {i} col {c}"


def validate_poster(pptx, svg=None):
    cs = pd.read_csv(
        ROOT / "FINALDOCS/ANALYSIS/CONDITION_SUMMARY.csv", encoding="utf-8-sig"
    )

    def mean(level, code, metric):
        g = cs[(cs.level == level) & (cs.condition == code) & (cs.metric == metric)]
        assert len(g) == 1
        return g["mean"].iat[0]

    with zipfile.ZipFile(pptx) as z:
        slide = ET.fromstring(z.read("ppt/slides/slide1.xml"))
        media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    tables = [cell_rows(t) for t in slide.findall(".//a:tbl", A)]
    assert len(tables) == 1, "Expected one native table"
    assert len(media) >= 2, "Example figure or parallel-coordinate image missing"
    text = "".join(slide.xpath("//*[local-name()='t']/text()"))
    hit = FORBIDDEN.search(text)
    assert not hit, f"Forbidden poster text: {hit.group(0)}"

    labels = [f"{i} {NAMES[c]}" for i, c in enumerate(CONDITIONS, 1)]
    groups = tables[0]
    for i, code in enumerate(CONDITIONS, 1):
        expect = [labels[i - 1]] + [
            f2(mean(g, code, m)) for m in SCORE_METRICS for g in GROUPS
        ]
        assert [c[0] for c in groups[i + 1]] == expect, (
            f"Poster value differs: group table row {i}"
        )
    # Passage-based metrics: maxima inside SCD-off rows and SCD-on rows separately.
    for k, m in enumerate(SCORE_METRICS):
        cols = list(range(1 + 3 * k, 4 + 3 * k))
        if m in ("faithfulness", "context_precision", "context_recall"):
            for s in "01":
                rows_ = [i + 1 for i, c in enumerate(CONDITIONS, 1) if c[-1] == s]
                check_bold(groups, cols, "Question group table", rows=rows_)
        else:
            check_bold(groups, cols, "Question group table", start=2)
    return {"tables": 1, "result_rows_checked": 8, "decimals": 2}


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
