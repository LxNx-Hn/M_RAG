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
import numpy as np  # noqa: E402
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
from analyze_questions import CONDITIONS, NAMES, QUALITY, TYPES  # noqa: E402

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
SHORT = {t: t.replace(" 및 ", "·") for t in TYPES}


def summary():
    s = pd.read_csv(ROOT / "FINALDOCS/ANALYSIS/QUESTION_TYPE_SUMMARY.csv")
    s.loc[s.grouping == "전체", "level"] = "전체"
    return s


def pick(s, level, base, applied, metric):
    g = s[(s.level == level) & (s.base == base) & (s.applied == applied) & (s.metric == metric) & s.grouping.isin(["question_type", "전체"])]
    assert len(g) == 1, (level, base, applied, metric)
    return g.iloc[0]


def f2(v, sign=False):
    return f"{v:+.2f}" if sign else f"{v:.2f}"


# ---------------------------------------------------------------- figures
def pipeline_png(path):
    fig, ax = plt.subplots(figsize=(10.5, 4.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 44)
    ax.axis("off")
    ink = "#263044"

    def node(x, y, w, h, title, sub, edge):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc="white", ec=edge, lw=2.2))
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center", fontsize=22, fontweight="bold", color=ink)
        ax.text(x + w / 2, y + h * 0.27, sub, ha="center", va="center", fontsize=16, color=ink)

    def arrow(a, b):
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", lw=2.2, color=ink, mutation_scale=20))

    node(1, 26, 22, 15, "한국어 질문", "60개", "#695184")
    node(30, 26, 32, 15, "검색 · 재정렬", "밀집 + BM25 → 융합 → 재정렬", "#695184")
    node(69, 26, 30, 15, "답변 생성", "영어 구간 5개 + 질문", "#695184")
    arrow((23.5, 33.5), (29.5, 33.5))
    arrow((62.5, 33.5), (68.5, 33.5))
    tags = [
        (30, "HyDE", "가상 문서로\n검색 입력 변경", "#2166ac"),
        (66, "CAD", "근거 포함·제외\n로짓 결합", "#b2182b"),
        (84, "SCD", "한국어 토큰\n로짓 조정", "#1b7837"),
    ]
    for x, name, desc, col in tags:
        w = 32 if name == "HyDE" else 15.5
        ax.add_patch(FancyBboxPatch((x, 2), w, 16, boxstyle="round,pad=0.3,rounding_size=1.2", fc=col, ec=col, alpha=0.12))
        ax.text(x + w / 2, 14.2, name, ha="center", va="center", fontsize=21, fontweight="bold", color=col)
        ax.text(x + w / 2, 6.6, desc, ha="center", va="center", fontsize=15.5, color=ink, linespacing=1.2)
        ax.annotate("", xy=(x + w / 2, 25.5), xytext=(x + w / 2, 18.5), arrowprops=dict(arrowstyle="-|>", lw=1.8, color=col, mutation_scale=16))
    fig.subplots_adjust(0.005, 0.01, 0.995, 0.99)
    fig.savefig(path, dpi=250, facecolor="white")
    plt.close(fig)


def parallel_png(path):
    data = pd.read_csv(ROOT / "FINALDOCS/ANALYSIS/QUERY_LEVEL_RESULTS.csv", encoding="utf-8-sig")
    axes_m = QUALITY + ["korean_ratio"]
    labels = ["근거 충실도", "답변 관련성", "문맥 정밀도", "문맥 재현율", "한국어 비율"]
    colors = {"방법 및 절차": "#2166ac", "결과 및 비교": "#b2182b", "사실 및 정의": "#8c510a", "목적 및 기여": "#1b7837"}
    codes = ["H0C0S0", "H1C0S0"]
    fig, axs = plt.subplots(len(codes), 1, figsize=(21.7, 6.6))
    x = np.arange(5)
    for ax, code in zip(axs, codes):
        g = data[data.condition == code]
        assert len(g) == 60
        for typ in ["사실 및 정의", "결과 및 비교", "목적 및 기여", "방법 및 절차"]:
            for r in g[g.question_type == typ].itertuples():
                ax.plot(x, [getattr(r, m) for m in axes_m], color=colors[typ], alpha=0.6 if typ == "방법 및 절차" else 0.4, lw=1.6 if typ == "방법 및 절차" else 1.1)
        for k in x:
            ax.axvline(k, color="#8a909a", lw=1.2, zorder=0)
        ax.set_xlim(-0.2, 4.2)
        ax.set_ylim(-0.04, 1.04)
        ax.set_yticks([0, 0.5, 1], ["0", "0.5", "1"])
        ax.set_xticks(x, labels)
        ax.tick_params(labelsize=19, length=0)
        for side in ["top", "right", "bottom"]:
            ax.spines[side].set_visible(False)
        ax.set_title(f"조건 {CONDITIONS.index(code) + 1}  {NAMES[code]} · 영어 근거 평가 · 60개 질문", loc="left", fontsize=21, fontweight="bold", color="#263044", pad=8)
    handles = [plt.Line2D([], [], color=c, lw=4) for c in colors.values()]
    fig.legend(handles, ["방법·절차 29개", "결과·비교 20개", "사실·정의 8개", "목적·기여 3개"], loc="upper right", ncol=4, frameon=False, fontsize=18)
    fig.subplots_adjust(left=0.035, right=0.99, top=0.87, bottom=0.1, hspace=0.75)
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)


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

    def text(self, x, y, w, h, lines, size=22, bold=False, color=INK, align=PP_ALIGN.LEFT, spacing=1.15):
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
            self.text(x, y + h, w, line_h * n, "- " + it.replace("\n", "\n  "), size=size)
            h += line_h * n + gap
        return y + h

    def table(self, x, y, w, rows, widths, bold=(), size=19, row_h=9.2, header_h=None, aligns=None):
        nr, nc = len(rows), len(rows[0])
        line = size * 0.3528 * 1.22
        heights = [max(row_h, max(str(v).count(chr(10)) + 1 for v in r) * line + 2.4) for r in rows]
        if header_h:
            heights[0] = max(heights[0], header_h)
        shape = self.slide.shapes.add_table(nr, nc, Mm(x), Mm(y), Mm(w), Mm(sum(heights)))
        tbl = shape.table
        tblpr = tbl._tbl.tblPr
        tblpr.set("firstRow", "0")
        tblpr.set("bandRow", "0")
        style = tblpr.find(qn("a:tableStyleId"))
        if style is not None:
            style.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"  # No Style, Table Grid
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
                    r.font.bold = i == 0 or (i, j) in bold
                    r.font.color.rgb = INK
                    a = "center" if i == 0 else (aligns[j] if aligns else ("left" if j == 0 else "right"))
                    p.alignment = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}[a]
                tcpr = cell._tc.get_or_add_tcPr()
                for side in ["a:lnL", "a:lnR", "a:lnT", "a:lnB"]:
                    ln = etree.SubElement(tcpr, qn(side), w=str(int(0.75 * 12700)))
                    sf = etree.SubElement(ln, qn("a:solidFill"))
                    etree.SubElement(sf, qn("a:srgbClr"), val="777777")
                self.texts.append(str(rows[i][j]))
        return y + sum(heights)

    def picture(self, path, x, y, w):
        pic = self.slide.shapes.add_picture(str(path), Mm(x), Mm(y), width=Mm(w))
        return y + pic.height / 36000


def bold_max(rows, cols, skip_last=False):
    out = []
    body = range(1, len(rows) - (1 if skip_last else 0))
    for c in cols:
        vals = [float(rows[i][c]) for i in body]
        m = max(vals)
        out += [(i, c) for i in body if float(rows[i][c]) == m]
    return out


# ---------------------------------------------------------------- content
def build(out_dir: Path):
    s = summary()
    out_dir.mkdir(parents=True, exist_ok=True)
    pipe, par = out_dir / "poster_pipeline.png", out_dir / "poster_parallel.png"
    pipeline_png(pipe)
    parallel_png(par)
    P = Poster()

    P.rect(0, 0, W, 92, PURPLE)
    P.text(L, 13, W - 2 * L, 50, ["한국어 질의로 영어 학술·기술 문서를 검색하는", "RAG에서의 HyDE·CAD·SCD 조합 실험"], size=64, bold=True, color=WHITE, align=PP_ALIGN.CENTER, spacing=1.05)
    P.text(L, 70, W - 2 * L, 12, "질문 유형별 점수 변화와 실제 검색·답변 분석", size=30, color=WHITE, align=PP_ALIGN.CENTER)

    # ---------------- left column
    y = P.heading(L, 102, C, "01 연구 배경과 목적")
    y = P.bullets(L, y, C, [
        "한국어 질문으로 영어 논문을 검색해 한국어로 답하는 RAG",
        "검색 입력(HyDE), 근거 반영(CAD), 출력 언어(SCD)를 조정하는 세 기법",
        "같은 질문 60개에 여덟 조건을 적용해 질문 유형별 변화를 비교",
    ])
    y = P.heading(L, y + 4, C, "02 파이프라인과 기법 적용 위치")
    y = P.picture(pipe, L, y, C) + 3
    rows = [["조건", "HyDE", "CAD", "SCD", "조건 이름"]]
    for c in CONDITIONS:
        rows.append([str(CONDITIONS.index(c) + 1), "+" if c[1] == "1" else "−", "+" if c[3] == "1" else "−", "+" if c[5] == "1" else "−", NAMES[c]])
    y = P.table(L, y, C, rows, [1.1, 1.1, 1.1, 1.1, 3.0], size=16, row_h=7.5, aligns=["center", "center", "center", "center", "left"])
    y = P.bullets(L, y + 3, C, [
        "HyDE: Hypothetical Document Embeddings\nCAD: Context-Aware Decoding · SCD: Soft Constrained Decoding",
        "품질 평가 근거: 조건 1~4 영어, 조건 5~8 한국어 번역",
    ], size=19)
    y = P.heading(L, y + 4, C, "03 질문 60개와 평가 지표")
    y = P.bullets(L, y, C, [
        "영어 문서 4종 × 15문항, 질문 60개 × 조건 8개 = 답변 480개",
        "사실·정의 8 · 방법·절차 29 · 결과·비교 20 · 목적·기여 3",
    ])
    rows = [["지표", "무엇을 측정하는가", "값의 방향"],
            ["근거 충실도", "답변 주장 중 입력 구간이 뒷받침하는 비율", "높을수록 근거 일치"],
            ["답변 관련성", "답변에서 만든 질문과 원질문의 유사도\n회피·모호 응답은 0", "높을수록 질문에 부합"],
            ["문맥 정밀도", "유용한 검색 구간이 상위에 있는 정도", "높을수록 순위 정확"],
            ["문맥 재현율", "참조 답변을 검색 구간이 뒷받침하는 비율", "높을수록 근거 확보"],
            ["한국어 문자 비율", "한글 ÷ (한글 + ASCII 영문자)", "높을수록 한국어 출력"],
            ["처리 시간", "질문 하나의 검색·생성 시간(초)", "낮을수록 비용 감소"]]
    y = P.table(L, y + 1, C, rows, [1.55, 3.35, 1.7], size=17, row_h=10.2, aligns=["left", "left", "left"])
    P.text(L, y + 2, C, 8, "점수 지표는 0~1 범위(관련성의 이론 범위는 −1~1, 관측값은 0~1)", size=16, color=GREY)
    left_end = y + 10

    # ---------------- right column
    y = P.heading(R, 102, C, "04 질문 유형별 HyDE의 답변 관련성")
    rows = [["질문 유형", "질문\n수", "미적용", "HyDE", "변화", "SCD", "HyDE\n+SCD", "변화"]]
    for t in TYPES + ["전체"]:
        a = pick(s, t, "H0C0S0", "H1C0S0", "answer_relevancy")
        b = pick(s, t, "H0C0S1", "H1C0S1", "answer_relevancy")
        rows.append([SHORT.get(t, "전체"), str(a.n), f2(a.base_mean), f2(a.applied_mean), f2(a.mean_delta, True), f2(b.base_mean), f2(b.applied_mean), f2(b.mean_delta, True)])
    bold = bold_max(rows, [3, 4, 6, 7], skip_last=True)
    P.text(R, y - 1, C, 8, [[("영어 근거 평가", True), ("(미적용 → HyDE)  ·  ", False), ("한국어 번역 근거 평가", True), ("(SCD → HyDE+SCD)", False)]], size=17)
    y = P.table(R, y + 7, C, rows, [2.0, 1.0, 1.25, 1.2, 1.2, 1.15, 1.25, 1.2], bold=set(bold), size=18, row_h=8.6, header_h=14)
    m = pick(s, "방법 및 절차", "H0C0S0", "H1C0S0", "answer_relevancy")
    y = P.bullets(R, y + 3, C, [
        f"방법·절차: 두 평가 언어 모두 가장 크게 상승(+{m.mean_delta:.2f}, +0.16), 개선 {m.improved} · 악화 {m.worse}",
        "방법·절차 6개는 회피 응답(0점)에서 답변으로 바뀜 · 결과·비교는 −0.02",
    ], size=19)

    y = P.heading(R, y + 4, C, "05 기법을 더했을 때의 변화 (60개)")
    rows = [["추가한 기법", "기준 → 적용 조건", "관련성\n변화", "개선/악화\n/비슷"]]
    plan = [("HyDE", "H0C0S0", "H1C0S0"), ("HyDE", "H0C1S0", "H1C1S0"), ("HyDE", "H0C0S1", "H1C0S1"), ("HyDE", "H0C1S1", "H1C1S1"),
            ("CAD", "H0C0S0", "H0C1S0"), ("CAD", "H1C0S0", "H1C1S0"), ("CAD", "H0C0S1", "H0C1S1"), ("CAD", "H1C0S1", "H1C1S1")]
    for tech, b0, a0 in plan:
        r = pick(s, "전체", b0, a0, "answer_relevancy")
        rows.append([tech, f"{NAMES[b0]} → {NAMES[a0]}", f2(r.mean_delta, True), f"{r.improved}/{r.worse}/{r.similar}"])
    bold = bold_max(rows, [2])
    y = P.table(R, y, C, rows, [1.3, 3.6, 1.3, 1.6], bold=set(bold), size=18, row_h=8.4, header_h=14, aligns=["left", "left", "right", "right"])
    y = P.bullets(R, y + 3, C, [
        "HyDE를 더한 네 비교는 개선이 악화보다 많음",
        "CAD를 더한 네 비교는 모두 악화가 더 많음(예: HyDE → HyDE+CAD 7/22)",
    ], size=19)

    y = P.heading(R, y + 4, C, "06 SCD의 한국어 문자 비율")
    rows = [["설정", "SCD 전", "SCD 후", "변화", "증가 질문"]]
    for b0, a0 in [("H0C0S0", "H0C0S1"), ("H1C0S0", "H1C0S1"), ("H0C1S0", "H0C1S1"), ("H1C1S0", "H1C1S1")]:
        r = pick(s, "전체", b0, a0, "korean_ratio")
        rows.append([NAMES[b0], f2(r.base_mean), f2(r.applied_mean), f2(r.mean_delta, True), f"{r.improved}/60"])
    y = P.table(R, y, C, rows, [2.2, 1.3, 1.3, 1.2, 1.5], bold=set(bold_max(rows, [2, 3])), size=18, row_h=8.6)
    y = P.bullets(R, y + 3, C, ["네 설정 모두 한국어 비율 상승, HyDE+SCD가 0.81로 최고", "영어 원문을 이어 쓴 답변은 SCD 후에도 영어로 남음"], size=19)

    y = P.heading(R, y + 4, C, "07 단일 기법의 처리 시간 (60개)")
    rows = [["기법", "미적용(초)", "적용(초)", "변화(초)", "증가 질문"]]
    for a0 in ["H1C0S0", "H0C1S0", "H0C0S1"]:
        r = pick(s, "전체", "H0C0S0", a0, "duration_seconds")
        rows.append([NAMES[a0], f2(r.base_mean), f2(r.applied_mean), f2(r.mean_delta, True), f"{r.improved}/60"])
    y = P.table(R, y, C, rows, [1.5, 1.6, 1.5, 1.5, 1.5], bold=set(bold_max(rows, [2, 3])), size=18, row_h=8.6)
    y = P.bullets(R, y + 3, C, ["CAD는 토큰마다 로짓을 두 번 계산해 약 3.1배 · 굵은 값은 가장 긴 시간"], size=19)
    right_end = y

    # ---------------- full width
    y = max(left_end, right_end) + 4
    y = P.heading(L, y, W - 2 * L, "08 질문 60개의 원점수 평행좌표: 미적용과 HyDE")
    y = P.picture(par, L, y, W - 2 * L)
    y = P.bullets(L, y + 2, W - 2 * L, ["선 하나가 질문 하나 · 미적용에서 답변 관련성 0에 모인 방법·절차 질문이 HyDE 적용 후 위로 이동"], size=19)

    y = P.heading(L, y + 3, C, "09 결론")
    yl = P.bullets(L, y, C, [
        "방법·절차 질문: HyDE 적용",
        "한국어 답변이 필요할 때: SCD 추가",
        "수치 질문: 정답 수치가 담긴 구간이 입력됐는지 확인",
        "CAD: 시간 3.1배, 관련성 변화 −0.01 → 지식 충돌 질문에서 별도 검토",
    ], size=20)
    P.heading(R, y - 17, C, "10 실제 답변에서 확인한 점")
    yr = P.bullets(R, y, C, [
        "BIC 질문: HyDE가 근거 구간을 찾아 관련성 0.00→0.89",
        "QuALITY 질문: 73.68이 빠져 관련성 0.87→0.00",
        "XSUM 질문: 다른 행 수치를 옮겼는데 충실도 0.53→0.87",
    ], size=20)
    y = max(yl, yr) + 3
    P.text(L, y, W - 2 * L, 14, ["[1] Lewis et al., RAG, NeurIPS 2020  [2] Gao et al., HyDE, ACL 2023  [3] Shi et al., CAD, NAACL 2024",
                                 "[4] Li et al., Language Drift and SCD, AAAI 2026  [5] Es et al., RAGAs, EACL 2024"], size=15, color=GREY)
    bottom = y + 14
    assert bottom <= H - 6, f"poster overflows: {bottom:.1f} mm"
    pptx = out_dir / "M_RAG_A1_FINAL_EDITABLE.pptx"
    P.prs.save(pptx)
    (out_dir / "POSTER_TEXT.json").write_text(json.dumps(P.texts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"PASS: A1 poster, bottom {bottom:.1f} mm of {H}; {len(P.texts)} text units")
    return pptx


def export(pptx: Path):
    import win32com.client

    app = win32com.client.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(str(pptx.resolve()), WithWindow=False)
    try:
        pres.SaveAs(str(pptx.with_name("M_RAG_A1_FINAL_PRINT.pdf").resolve()), 32)
        pres.Slides(1).Export(str(pptx.with_name("M_RAG_A1_FINAL_PREVIEW.png").resolve()), "PNG", 2400, 3398)
    finally:
        pres.Close()
    import fitz

    with fitz.open(pptx.with_name("M_RAG_A1_FINAL_PRINT.pdf")) as doc:
        pptx.with_name("M_RAG_A1_FINAL_EDITABLE.svg").write_text(doc[0].get_svg_image(text_as_path=False), encoding="utf-8")
    print("PASS: PowerPoint-rendered PDF, PNG and SVG")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=ROOT / "tmp/poster")
    ap.add_argument("--no-export", action="store_true")
    a = ap.parse_args()
    pptx = build(a.output)
    if not a.no_export:
        export(pptx)


if __name__ == "__main__":
    main()
