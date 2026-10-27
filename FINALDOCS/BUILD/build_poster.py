"""Build the A1 poster (editable PPTX) from the question-level analysis.

All numbers are read from FINALDOCS/ANALYSIS outputs and rounded to two
decimals. Text and tables are native PowerPoint objects; the pipeline diagram
and the parallel-coordinate panels are images drawn here with Matplotlib.
Rendering to PDF/PNG uses the installed PowerPoint (export_poster.ps1 step in
main), so the printed file is PowerPoint's own rendering of the PPTX.

Usage: python FINALDOCS/BUILD/build_poster.py [--output DIR] [--no-export]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from lxml import etree  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Mm, Pt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "FINALDOCS/ANALYSIS"))
from analyze_questions import CONDITIONS, NAMES  # noqa: E402
from svg_export import reencode_svg_pngs  # noqa: E402

FONT = "Malgun Gothic"
for name in ["malgun.ttf", "malgunbd.ttf"]:
    if (Path("C:/Windows/Fonts") / name).exists():
        font_manager.fontManager.addfont(str(Path("C:/Windows/Fonts") / name))
plt.rcParams.update({"font.family": FONT, "axes.unicode_minus": False})

INK = RGBColor(0x26, 0x30, 0x44)
PURPLE = RGBColor(0x69, 0x51, 0x84)
GREY = RGBColor(0x77, 0x77, 0x77)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
W, H = 594, 841  # mm, A1 portrait
L, G = 22, 16
C = (W - 2 * L - G) / 2
R = L + C + G


def summary():
    s = pd.read_csv(ROOT / "FINALDOCS/ANALYSIS/QUESTION_TYPE_SUMMARY.csv")
    s.loc[s.grouping == "전체", "level"] = "전체"
    return s


def condition_summary():
    return pd.read_csv(
        ROOT / "FINALDOCS/ANALYSIS/CONDITION_SUMMARY.csv", encoding="utf-8-sig"
    )


def stat(cs, level, code, metric):
    g = cs[(cs.level == level) & (cs.condition == code) & (cs.metric == metric)]
    assert len(g) == 1, (level, code, metric)
    return g.iloc[0]


def pick(s, level, base, applied, metric):
    g = s[
        (s.level == level)
        & (s.base == base)
        & (s.applied == applied)
        & (s.metric == metric)
        & s.grouping.isin(["question_group", "전체"])
    ]
    assert len(g) == 1, (level, base, applied, metric)
    return g.iloc[0]


def f2(v, sign=False):
    if sign and round(v, 2) == 0:
        return "0.00"
    return f"{v:+.2f}".replace("-", "−") if sign else f"{v:.2f}"


# ---------------------------------------------------------------- figures
def pipeline_png(path):
    fig, ax = plt.subplots(figsize=(10.5, 3.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 33)
    ax.axis("off")
    ink = "#263044"

    def node(x, y, w, h, title, sub, edge):
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.3,rounding_size=1.2",
                fc="white",
                ec=edge,
                lw=2.2,
            )
        )
        ax.text(
            x + w / 2,
            y + h * 0.66,
            title,
            ha="center",
            va="center",
            fontsize=22,
            fontweight="bold",
            color=ink,
        )
        ax.text(
            x + w / 2,
            y + h * 0.27,
            sub,
            ha="center",
            va="center",
            fontsize=16,
            color=ink,
        )

    def arrow(a, b):
        ax.annotate(
            "",
            xy=b,
            xytext=a,
            arrowprops=dict(arrowstyle="-|>", lw=2.2, color=ink, mutation_scale=20),
        )

    node(1, 19, 22, 12, "한국어 질문", "60개", "#695184")
    node(30, 19, 32, 12, "검색과 재정렬", "밀집과 BM25 검색의 융합", "#695184")
    node(69, 19, 30, 12, "답변 생성", "영어 구간 5개 + 질문", "#695184")
    arrow((23.5, 25.0), (29.5, 25.0))
    arrow((62.5, 25.0), (68.5, 25.0))
    tags = [
        (30, "HyDE", "가상 문서로\n검색 입력 변경", "#2166ac"),
        (66, "CAD", "문맥 포함과\n제외 로짓 결합", "#b2182b"),
        (84, "SCD", "한국어 토큰\n로짓 조정", "#1b7837"),
    ]
    for x, name, desc, col in tags:
        w = 32 if name == "HyDE" else 15.5
        ax.add_patch(
            FancyBboxPatch(
                (x, 1),
                w,
                12.5,
                boxstyle="round,pad=0.3,rounding_size=1.2",
                fc=col,
                ec=col,
                alpha=0.12,
            )
        )
        ax.text(
            x + w / 2,
            10.4,
            name,
            ha="center",
            va="center",
            fontsize=21,
            fontweight="bold",
            color=col,
        )
        ax.text(
            x + w / 2,
            4.3,
            desc,
            ha="center",
            va="center",
            fontsize=15.5,
            color=ink,
            linespacing=1.2,
        )
        ax.annotate(
            "",
            xy=(x + w / 2, 18.5),
            xytext=(x + w / 2, 14.0),
            arrowprops=dict(arrowstyle="-|>", lw=1.8, color=col, mutation_scale=16),
        )
    fig.subplots_adjust(0.005, 0.01, 0.995, 0.99)
    fig.savefig(path, dpi=250, facecolor="white")
    plt.close(fig)


def mechanism_png(path):
    """The example question through HyDE, CAD and SCD (same drawing as Figure 4-2)."""
    from plot_questions import example_mechanism

    example_mechanism(save_to=path, scale=3.44)


def parallel_png(path, height_in=6.1, width_in=21.7):
    """The 25 method questions in four condition panels, side by side."""
    from plot_questions import group_profiles

    data = pd.read_csv(
        ROOT / "FINALDOCS/ANALYSIS/QUERY_LEVEL_RESULTS.csv", encoding="utf-8-sig"
    )
    group_profiles(
        data, "방법 질문", size=(width_in, height_in), scale=1.75, save_to=path, compact=True, ncols=4
    )


# ---------------------------------------------------------------- pptx helpers
class Poster:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Mm(W), Mm(H)
        self.slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.texts = []

    def rect(self, x, y, w, h, fill):
        s = self.slide.shapes.add_shape(1, Mm(x), Mm(y), Mm(w), Mm(h))
        s.fill.solid()
        s.fill.fore_color.rgb = fill
        s.line.fill.background()
        s.shadow.inherit = False
        return s

    def text(
        self,
        x,
        y,
        w,
        h,
        lines,
        size=22,
        bold=False,
        color=INK,
        align=PP_ALIGN.LEFT,
        spacing=1.15,
    ):
        box = self.slide.shapes.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        if isinstance(lines, str):
            lines = [lines]
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = spacing
            runs = line if isinstance(line, list) else [(line, bold)]
            for t, b in runs:
                r = p.add_run()
                r.text = t
                r.font.name = FONT
                r.font.size = Pt(size)
                r.font.bold = b
                r.font.color.rgb = color
                rpr = r._r.get_or_add_rPr()
                ea = rpr.find(qn("a:ea"))
                if ea is None:
                    ea = etree.SubElement(rpr, qn("a:ea"))
                ea.set("typeface", FONT)
            self.texts.append("".join(t for t, _ in runs))
        return box

    def heading(self, x, y, w, label):
        self.rect(x, y, w, 13, PURPLE)
        self.text(x + 4, y + 0.7, w - 8, 10, label, size=27, bold=True, color=WHITE)
        return y + 17

    def bullets(self, x, y, w, items, size=21, gap=2.5):
        line_h = size * 0.3528 * 1.32
        h = 0
        for it in items:
            n = 1 + it.count("\n")
            self.text(
                x, y + h, w, line_h * n, "- " + it.replace("\n", "\n  "), size=size
            )
            h += line_h * n + gap
        return y + h

    def table(
        self,
        x,
        y,
        w,
        rows,
        widths,
        bold=(),
        size=19,
        row_h=9.2,
        header_h=None,
        aligns=None,
        header_rows=1,
        merges=(),
    ):
        nr, nc = len(rows), len(rows[0])
        line = size * 0.3528 * 1.22
        heights = [
            max(row_h, max(str(v).count(chr(10)) + 1 for v in r) * line + 2.4)
            for r in rows
        ]
        if header_h:
            heights[0] = max(heights[0], header_h)
        shape = self.slide.shapes.add_table(
            nr, nc, Mm(x), Mm(y), Mm(w), Mm(sum(heights))
        )
        tbl = shape.table
        tblpr = tbl._tbl.tblPr
        tblpr.set("firstRow", "0")
        tblpr.set("bandRow", "0")
        style = tblpr.find(qn("a:tableStyleId"))
        if style is not None:
            style.text = (
                "{5940675A-B579-460E-94D1-54222C63F5DA}"  # No Style, Table Grid
            )
        total = sum(widths)
        for j, wd in enumerate(widths):
            tbl.columns[j].width = Mm(w * wd / total)
        for i in range(nr):
            tbl.rows[i].height = Mm(heights[i])
            for j in range(nc):
                cell = tbl.cell(i, j)
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE
                cell.margin_left = cell.margin_right = Mm(1.6)
                cell.margin_top = cell.margin_bottom = Mm(0.6)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf = cell.text_frame
                tf.word_wrap = True
                lines = str(rows[i][j]).split("\n")
                for k, t in enumerate(lines):
                    p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                    p.text = ""
                    r = p.add_run()
                    r.text = t
                    r.font.name = FONT
                    r.font.size = Pt(size)
                    r.font.bold = i < header_rows or (i, j) in bold
                    r.font.color.rgb = INK
                    a = (
                        "center"
                        if i < header_rows
                        else (aligns[j] if aligns else ("left" if j == 0 else "right"))
                    )
                    p.alignment = {
                        "left": PP_ALIGN.LEFT,
                        "right": PP_ALIGN.RIGHT,
                        "center": PP_ALIGN.CENTER,
                    }[a]
                tcpr = cell._tc.get_or_add_tcPr()
                for side in ["a:lnL", "a:lnR", "a:lnT", "a:lnB"]:
                    ln = etree.SubElement(tcpr, qn(side), w=str(int(0.75 * 12700)))
                    sf = etree.SubElement(ln, qn("a:solidFill"))
                    etree.SubElement(sf, qn("a:srgbClr"), val="777777")
                self.texts.append(str(rows[i][j]))
        for r0, c0, r1, c1 in merges:
            tbl.cell(r0, c0).merge(tbl.cell(r1, c1))
        return y + sum(heights)

    def picture(self, path, x, y, w):
        pic = self.slide.shapes.add_picture(str(path), Mm(x), Mm(y), width=Mm(w))
        return y + pic.height / 36000


def bold_max(rows, scopes):
    """Displayed maxima per (column, rows) scope; equal displayed values share bold."""
    out = []
    for c, body in scopes:
        vals = [float(rows[i][c].replace("−", "-")) for i in body]
        m = max(vals)
        out += [(i, c) for i, v in zip(body, vals) if v == m]
    return out


# ---------------------------------------------------------------- content
METRIC_SHORT = {
    "faithfulness": "근거\n충실도",
    "answer_relevancy": "답변\n관련성",
    "context_precision": "문맥\n정밀도",
    "context_recall": "문맥\n재현율",
    "korean_ratio": "한국어\n문자 비율",
}
SCORE_METRICS = list(METRIC_SHORT)
# Section 04 definitions, same order and names as the 05 table (thesis 5.2).
METRIC_DEFINITIONS = [
    ["지표", "측정 내용", "값의 방향"],
    ["근거 충실도", "답변의 주장 중 검색 구간이 뒷받침하는 비율", "높을수록 근거에 충실"],
    [
        "답변 관련성",
        "답변에서 역으로 만든 질문과 원래 질문의 유사도\n모호하거나 회피하는 답변은 0",
        "높을수록 질문에 부합",
    ],
    ["문맥 정밀도", "참조 답변에 유용한 구간의 순위가 높은 정도", "높을수록 순위가 적절"],
    ["문맥 재현율", "참조 답변의 주장을 검색 구간이 뒷받침하는 비율", "높을수록 정답 근거 확보"],
    [
        "한국어 문자 비율",
        "출력 언어, 한글 ÷ (한글 + ASCII 영문자)",
        "높을수록 한국어 출력",
    ],
]


def condition_label(code):
    return f"{CONDITIONS.index(code) + 1} {NAMES[code]}"


def build(out_dir: Path, personal=None, layout="b"):
    """layout "b" puts the pipeline diagram beside 01; layout "a" keeps 01 as
    two bullet columns and shows only the example-question figure."""
    assert layout in ("a", "b")
    numbers = iter(range(1, 10))

    def section(label):
        return f"{next(numbers):02d} {label}"

    cs = condition_summary()
    out_dir.mkdir(parents=True, exist_ok=True)
    mech, par = out_dir / "poster_mechanism.png", out_dir / "poster_parallel.png"
    mechanism_png(mech)
    P = Poster()

    def mean(level, code, metric):
        return stat(cs, level, code, metric)["mean"]

    TOP = 90  # first section heading below the title band
    P.rect(0, 0, W, TOP - 10, PURPLE)
    P.text(
        L,
        9,
        W - 2 * L,
        50,
        [
            "한국어 질의로 영어 학술 및 기술 문서를 검색하는",
            "RAG에서의 HyDE, CAD, SCD 조합 실험",
        ],
        size=62,
        bold=True,
        color=WHITE,
        align=PP_ALIGN.CENTER,
        spacing=1.05,
    )
    f = personal or {}
    identity = "{} {} {}, 지도교수 {}".format(
        f.get("department", "[학과]"),
        f.get("student_id", "[학번]"),
        f.get("name", "[이름]"),
        f.get("advisor", "[지도교수]"),
    )
    P.text(L, 66, W - 2 * L, 10, identity, size=24, color=WHITE, align=PP_ALIGN.CENTER)

    FW = W - 2 * L

    # ---------------- background, beside the pipeline (b) or in two columns (a)
    background = [
        "한국어 질문으로 영어 논문을 찾아 한국어로 답하는 RAG",
        "질문과 원문의 어휘가 달라 근거 구간을 찾기 어려움",
        "영어 근거를 한국어 답변에 충실히 옮기기 어려움",
        "답변이 근거를 따라 영어로 바뀌는 언어 이탈",
        "세 문제에 맞춘 HyDE, CAD, SCD를 같은 질문 60개에 조합",
        "질문 유형마다 각 기법의 이득과 손실을 비교",
    ]
    if layout == "b":
        pipe = out_dir / "poster_pipeline.png"
        pipeline_png(pipe)
        y = P.heading(L, TOP, C, section("연구 배경과 목적"))
        yl = P.bullets(L, y, C, background)
        y = P.heading(R, TOP, C, section("파이프라인"))
        yr = P.picture(pipe, R, y, C)
    else:
        y = P.heading(L, TOP, FW, section("연구 배경과 목적"))
        yl = P.bullets(L, y, C, background[:3])
        yr = P.bullets(R, y, C, background[3:])

    # ---------------- 03 example question, each technique against no technique
    y = P.heading(L, max(yl, yr) + 3, FW, section("예시 질문으로 본 단독 기법의 작동"))
    y = P.picture(mech, L, y + 1, FW)
    P.text(
        L,
        y + 1,
        FW,
        8,
        "HyDE Hypothetical Document Embeddings   CAD Context-Aware Decoding   SCD Soft Constrained Decoding   패널마다 미적용과 단독 적용 조건을 비교, 점 위치와 글자 크기는 원리를 보인 개념도",
        size=16,
        color=GREY,
    )
    y += 10

    # ---------------- 04 questions and metrics, definitions above the 05 columns
    y = P.heading(L, y + 2, FW, section("질문과 평가"))
    yl = P.bullets(
        L,
        y,
        C,
        [
            "영어 문서 4종에서 15개씩, 한국어 질문 60개",
            "수치 18개, 방법 25개, 개념과 결과 17개",
            "세 기법의 적용 여부를 조합한 조건 8개, 답변 480개",
            "관측값은 모두 0에서 1, 앞의 네 지표는 RAGAS로 계산",
            "SCD 조건 4, 6, 7, 8의 충실도, 정밀도, 재현율은\n한국어 번역 근거로 평가해 같은 언어 조건끼리 비교",
        ],
        size=20,
        gap=2.0,
    )
    yr = P.table(
        R,
        y,
        C,
        METRIC_DEFINITIONS,
        [1.0, 2.75, 1.45],
        size=17,
        row_h=8.6,
        aligns=["left", "left", "left"],
    )
    y = max(yl, yr)

    # ---------------- 05 question-type means (wide table)
    y = P.heading(L, y + 4, FW, section("질문 유형별 평균 점수"))
    groups = [
        ("수치 질문", "수치"),
        ("방법 질문", "방법"),
        ("개념과 결과 질문", "개념과\n결과"),
    ]
    block = [
        ("faithfulness", "근거 충실도"),
        ("answer_relevancy", "답변 관련성"),
        ("context_precision", "문맥 정밀도"),
        ("context_recall", "문맥 재현율"),
        ("korean_ratio", "한국어 문자 비율"),
    ]
    top = ["조건"]
    for _, label in block:
        top += [label, "", ""]
    rows = [top, [""] + [short for _ in block for _, short in groups]]
    for c in CONDITIONS:
        rows.append(
            [condition_label(c)] + [f2(mean(g, c, m)) for m, _ in block for g, _ in groups]
        )
    body = list(range(2, len(rows)))
    scopes = []
    for k, (m, _) in enumerate(block):
        if m in ("faithfulness", "context_precision", "context_recall"):
            groups_of_rows = [
                [r for r, c in zip(body, CONDITIONS) if c[-1] == s] for s in "01"
            ]
        else:
            groups_of_rows = [body]
        for j in range(3):
            scopes += [(1 + 3 * k + j, rows_) for rows_ in groups_of_rows]
    merges = [(0, 0, 1, 0)] + [(0, 1 + 3 * k, 0, 3 + 3 * k) for k in range(len(block))]
    y = P.table(
        L,
        y,
        FW,
        rows,
        [1.75] + [1.0] * (len(rows[0]) - 1),
        bold=set(bold_max(rows, scopes)),
        size=17,
        row_h=7.0,
        header_rows=2,
        merges=merges,
    )
    y = P.bullets(
        L,
        y + 3,
        FW,
        [
            "충실도, 정밀도, 재현율의 굵은 값은 SCD 미적용 조건과 적용 조건 안에서 각각 구한 최댓값",
            "관련성은 방법 질문에서 HyDE가 0.57에서 0.74로, 충실도는 수치 질문에서 CAD가 0.83에서 0.90으로 높임",
        ],
        size=19,
    )

    # ---------------- 06 parallel coordinates, then 07 conclusions, both full width
    refs_h = 13
    conclusions = [
        "관련성과 응답 시간이 중요하면 HyDE 하나(개념과 결과 질문 포함)",
        "수치 질문은 정답 구간의 검색을 확인하고 충실도는 HyDE+CAD",
        "한국어 답변은 세 기법(방법 질문 세 지표가 SCD 단독보다 높음)",
        "조합은 HyDE 단독보다 관련성이 낮고 일관된 이득은 SCD의 한국어 비율",
    ]
    size_c, gap_c = 22, 2.0
    conclusion_h = 17 + 2 * (size_c * 0.3528 * 1.32 + gap_c)
    caption_h = 19 * 0.3528 * 1.32 + 2.5
    y = P.heading(L, y + 4, FW, section("방법 질문 25개의 원점수 평행좌표"))
    chart_h = (H - 6 - refs_h) - y - 1 - caption_h - 4 - conclusion_h
    parallel_png(par, chart_h / 25.4, FW / 25.4)
    y = P.picture(par, L, y, FW)
    y = P.bullets(
        L,
        y + 1,
        FW,
        ["HyDE 적용 후 관련성 축의 선이 위로 모이고 관련성 0점 답변이 5개에서 1개로 줄어듦"],
        size=19,
    )
    y = P.heading(L, y + 4, FW, section("결론"))
    yl = P.bullets(L, y, C, conclusions[:2], size=size_c, gap=gap_c)
    yr = P.bullets(R, y, C, conclusions[2:], size=size_c, gap=gap_c)
    y = max(yl, yr) + 2
    P.text(
        L,
        y,
        W - 2 * L,
        9,
        "[1] Lewis et al., RAG, NeurIPS 2020   [2] Gao et al., HyDE, ACL 2023   [3] Shi et al., CAD, NAACL 2024   [4] Li et al., SCD, AAAI 2026   [5] Es et al., RAGAs, EACL 2024",
        size=17,
        color=INK,
    )
    y += 9
    bottom = y
    assert bottom <= H - 6, f"poster overflows: {bottom:.1f} mm"
    pptx = out_dir / "M_RAG_A1_FINAL_EDITABLE.pptx"
    P.prs.save(pptx)
    (out_dir / "POSTER_TEXT.json").write_text(
        json.dumps(P.texts, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"PASS: A1 poster, bottom {bottom:.1f} mm of {H}; {len(P.texts)} text units")
    return pptx


def export(pptx: Path):
    import win32com.client

    app = win32com.client.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(str(pptx.resolve()), WithWindow=False)
    try:
        pres.SaveAs(str(pptx.with_name("M_RAG_A1_FINAL_PRINT.pdf").resolve()), 32)
        pres.Slides(1).Export(
            str(pptx.with_name("M_RAG_A1_FINAL_PREVIEW.png").resolve()),
            "PNG",
            2400,
            3398,
        )
    finally:
        pres.Close()
    import fitz

    with fitz.open(pptx.with_name("M_RAG_A1_FINAL_PRINT.pdf")) as doc:
        pptx.with_name("M_RAG_A1_FINAL_EDITABLE.svg").write_text(
            reencode_svg_pngs(doc[0].get_svg_image(text_as_path=False)),
            encoding="utf-8",
        )
    print("PASS: PowerPoint-rendered PDF, PNG and SVG")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=ROOT / "tmp/poster")
    ap.add_argument("--no-export", action="store_true")
    ap.add_argument(
        "--layout",
        choices=["a", "b"],
        default="b",
        help="b: pipeline diagram beside 01 (submitted poster); a: example figure only",
    )
    ap.add_argument(
        "--personal-fields",
        type=Path,
        help="Local personal_fields.json (department, student_id, name, advisor are used); output must stay outside the repository",
    )
    a = ap.parse_args()
    personal = None
    if a.personal_fields:
        fields = json.loads(a.personal_fields.read_text(encoding="utf-8"))
        used = ("department", "student_id", "name", "advisor")
        if any(not str(fields.get(k, "")).strip() for k in used):
            raise ValueError("Personal fields need department, student_id, name, advisor")
        personal = {k: fields[k] for k in used}
        if a.output.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Personal poster output must stay outside the repository")
    pptx = build(a.output, personal, a.layout)
    if not a.no_export:
        export(pptx)


if __name__ == "__main__":
    main()
