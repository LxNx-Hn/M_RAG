"""Independently check the A1 poster tables against the question analysis.

Every number in the four result tables is recomputed from
QUESTION_TYPE_SUMMARY.csv at two decimals; bold marks only column maxima;
statistical-test terms, standard deviations and internal question IDs are
absent from the poster text.
"""

import re
import zipfile
from pathlib import Path

import pandas as pd
from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[2]
A = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
TYPES = ["사실 및 정의", "방법 및 절차", "결과 및 비교", "목적 및 기여"]
NAMES = dict(zip(["H0C0S0", "H0C1S0", "H1C0S0", "H1C1S0", "H0C0S1", "H0C1S1", "H1C0S1", "H1C1S1"], ["미적용", "CAD", "HyDE", "HyDE+CAD", "SCD", "CAD+SCD", "HyDE+SCD", "HyDE+CAD+SCD"]))
FORBIDDEN = re.compile(r"ANOVA|t-검정|p값|p<|표준편차|\bSD\b|ext_|track1_|H[01]C[01]S[01]|중앙값")


def cell_rows(table):
    rows = []
    for tr in table.findall("a:tr", A):
        row = []
        for tc in tr.findall("a:tc", A):
            runs = tc.findall(".//a:r", A)
            text = "\n".join("".join(r.findtext("a:t", "", A) for r in p.findall("a:r", A)) for p in tc.findall("a:txBody/a:p", A))
            bold = any(r.find("a:rPr", A) is not None and r.find("a:rPr", A).get("b") == "1" for r in runs)
            row.append((text, bold))
        rows.append(row)
    return rows


def f2(v, sign=False):
    return f"{v:+.2f}" if sign else f"{v:.2f}"


def check_bold(rows, cols, label, skip_last=False):
    body = rows[1 : len(rows) - (1 if skip_last else 0)]
    for c in cols:
        top = max(float(r[c][0]) for r in body)
        for i, r in enumerate(body, 1):
            assert r[c][1] == (float(r[c][0]) == top), f"{label} bold differs at row {i} col {c}"


def validate_poster(pptx, svg=None):
    s = pd.read_csv(ROOT / "FINALDOCS/ANALYSIS/QUESTION_TYPE_SUMMARY.csv")
    s.loc[s.grouping == "전체", "level"] = "전체"

    def pick(level, base, applied, metric):
        g = s[(s.level == level) & (s.base == base) & (s.applied == applied) & (s.metric == metric) & s.grouping.isin(["question_type", "전체"])]
        assert len(g) == 1
        return g.iloc[0]

    with zipfile.ZipFile(pptx) as z:
        slide = ET.fromstring(z.read("ppt/slides/slide1.xml"))
        media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    tables = [cell_rows(t) for t in slide.findall(".//a:tbl", A)]
    assert len(tables) == 6, "Expected six native tables"
    assert len(media) >= 2, "Pipeline diagram or parallel-coordinate image missing"
    text = "".join(slide.xpath("//*[local-name()='t']/text()"))
    hit = FORBIDDEN.search(text)
    assert not hit, f"Forbidden poster text: {hit.group(0)}"

    hyde = tables[2]
    for i, t in enumerate(TYPES + ["전체"], 1):
        a, b = pick(t, "H0C0S0", "H1C0S0", "answer_relevancy"), pick(t, "H0C0S1", "H1C0S1", "answer_relevancy")
        expect = [str(a.n), f2(a.base_mean), f2(a.applied_mean), f2(a.mean_delta, True), f2(b.base_mean), f2(b.applied_mean), f2(b.mean_delta, True)]
        assert [c[0] for c in hyde[i][1:]] == expect, f"Poster value differs: HyDE table row {i}"
    check_bold(hyde, [3, 4, 6, 7], "HyDE table", skip_last=True)

    combos = [("H0C0S0", "H1C0S0"), ("H0C1S0", "H1C1S0"), ("H0C0S1", "H1C0S1"), ("H0C1S1", "H1C1S1"), ("H0C0S0", "H0C1S0"), ("H1C0S0", "H1C1S0"), ("H0C0S1", "H0C1S1"), ("H1C0S1", "H1C1S1")]
    for i, (b0, a0) in enumerate(combos, 1):
        r = pick("전체", b0, a0, "answer_relevancy")
        row = tables[3][i]
        assert row[1][0] == f"{NAMES[b0]} → {NAMES[a0]}", "Combination label differs"
        assert [row[2][0], row[3][0]] == [f2(r.mean_delta, True), f"{r.improved}/{r.worse}/{r.similar}"], f"Poster value differs: combination row {i}"
    check_bold(tables[3], [2], "Combination table")

    for i, (b0, a0) in enumerate([("H0C0S0", "H0C0S1"), ("H1C0S0", "H1C0S1"), ("H0C1S0", "H0C1S1"), ("H1C1S0", "H1C1S1")], 1):
        r = pick("전체", b0, a0, "korean_ratio")
        assert [c[0] for c in tables[4][i][1:]] == [f2(r.base_mean), f2(r.applied_mean), f2(r.mean_delta, True), f"{r.improved}/60"], f"Poster value differs: Korean row {i}"
    check_bold(tables[4], [2, 3], "Korean table")

    for i, a0 in enumerate(["H1C0S0", "H0C1S0", "H0C0S1"], 1):
        r = pick("전체", "H0C0S0", a0, "duration_seconds")
        assert [c[0] for c in tables[5][i][1:]] == [f2(r.base_mean), f2(r.applied_mean), f2(r.mean_delta, True), f"{r.improved}/60"], f"Poster value differs: time row {i}"
    check_bold(tables[5], [2, 3], "Time table")
    return {"tables": 6, "result_rows_checked": 5 + 8 + 4 + 3, "decimals": 2}


def protocol_order(codes):
    expected = [f"H{h}C{c}S{s}" for s in (0, 1) for h in (0, 1) for c in (0, 1)]
    if codes != expected:
        raise AssertionError("S0/S1 protocol groups must each contain four conditions")


def poster_headings(labels):
    return any(
        re.fullmatch(r"\s*(?:\d{2}\s*)?(?:국문)?초록\s*|\s*(?:\d{2}\s*)?Abstract\s*", value, re.I)
        for value in labels
    )
