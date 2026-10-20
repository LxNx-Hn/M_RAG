"""Figures for chapter 5, drawn from the stored measurements and records.

Performance is shown only as parallel coordinates of the raw scores of all 60
questions, one condition per row. Two non-performance figures explain the
evaluation design and show one stored input/output example.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from analyze_questions import (
    CONDITIONS,
    HERE,
    NAMES,
    QUALITY,
    ROOT,
    TYPES,
)  # noqa: E402

for name in ["malgun.ttf", "malgunbd.ttf"]:
    if (Path("C:/Windows/Fonts") / name).exists():
        font_manager.fontManager.addfont(str(Path("C:/Windows/Fonts") / name))
plt.rcParams.update(
    {
        "font.family": "Malgun Gothic",
        "font.size": 11,
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
    }
)
OUT = ROOT / "FINALDOCS/FIGURES"
INK = "#263044"
COLORS = dict(zip(TYPES, ["#8c510a", "#2166ac", "#b2182b", "#1b7837"]))
AXES = QUALITY + ["korean_ratio"]
LABELS = [
    "근거\n충실도",
    "답변\n관련성",
    "문맥\n정밀도",
    "문맥\n재현율",
    "한국어\n문자 비율",
]


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=300, facecolor="white")
    fig.savefig(OUT / f"{name}.svg", facecolor="white")
    plt.close(fig)


def parallel(data, codes, name, language):
    """One condition per row; every question is one translucent line coloured by type."""
    fig, axes = plt.subplots(len(codes), 1, figsize=(6.3, 8.6), sharey=True)
    x = np.arange(len(AXES))
    for ax, code in zip(axes, codes):
        g = data[data.condition == code]
        assert len(g) == 60
        for typ in TYPES:
            for r in g[g.question_type == typ].itertuples():
                ax.plot(
                    x,
                    [getattr(r, m) for m in AXES],
                    color=COLORS[typ],
                    alpha=0.35,
                    lw=0.9,
                )
        for k in x:
            ax.axvline(k, color="#9aa0aa", lw=0.8, zorder=0)
        ax.set_xlim(-0.3, len(AXES) - 0.7)
        ax.set_ylim(-0.04, 1.04)
        ax.set_yticks([0, 0.5, 1.0], ["0", "0.5", "1"])
        ax.set_xticks(x, LABELS)
        ax.tick_params(labelsize=10, length=0)
        for side in ["top", "right", "bottom"]:
            ax.spines[side].set_visible(False)
        ax.set_title(
            f"조건 {CONDITIONS.index(code) + 1}  {NAMES[code]}",
            loc="left",
            fontsize=11.5,
            fontweight="bold",
            color=INK,
            pad=4,
        )
    handles = [plt.Line2D([], [], color=COLORS[t], lw=2.4) for t in TYPES]
    fig.legend(
        handles,
        [f"{t.replace(' 및 ', '·')} {n}개" for t, n in zip(TYPES, [8, 29, 20, 3])],
        loc="upper center",
        ncol=4,
        frameon=False,
        fontsize=9.5,
        bbox_to_anchor=(0.5, 1.0),
        handlelength=1.6,
        columnspacing=1.2,
    )
    fig.text(
        0.5,
        0.958,
        f"품질 지표는 {language}로 평가 · 선 하나가 질문 하나",
        ha="center",
        fontsize=9.5,
        color="#555b66",
    )
    fig.subplots_adjust(left=0.07, right=0.985, top=0.915, bottom=0.05, hspace=0.75)
    save(fig, name)


def box(ax, x, y, w, h, text, edge, size=12.5, bold=False):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.008,rounding_size=0.02",
            fc="#f8f8fb",
            ec=edge,
            lw=1.8,
        )
    )
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=size,
        color=INK,
        fontweight="bold" if bold else "normal",
        linespacing=1.45,
    )


def arrow(ax, a, b):
    ax.annotate(
        "",
        xy=b,
        xytext=a,
        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, mutation_scale=16),
    )


def evaluation_design():
    fig, ax = plt.subplots(figsize=(6.3, 3.9))
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(0, 1)
    ax.axis("off")
    purple, green = "#695184", "#1b7837"
    box(ax, 0.00, 0.76, 0.28, 0.2, "한국어 질문\n60개", purple, bold=True)
    box(ax, 0.36, 0.76, 0.28, 0.2, "기법 적용 조건\n8개", purple, bold=True)
    box(ax, 0.72, 0.76, 0.28, 0.2, "생성 답변\n480개", purple, bold=True)
    arrow(ax, (0.285, 0.86), (0.355, 0.86))
    arrow(ax, (0.645, 0.86), (0.715, 0.86))
    box(
        ax,
        0.00,
        0.40,
        0.47,
        0.26,
        "RAGAS 품질 지표 4개\n조건 1~4: 영어 근거로 평가\n조건 5~8: 한국어 번역 근거로 평가",
        purple,
        size=11,
    )
    box(
        ax,
        0.53,
        0.40,
        0.47,
        0.26,
        "한국어 문자 비율 · 처리 시간\n저장된 답변과 실행 기록에서 계산",
        green,
        size=11,
    )
    arrow(ax, (0.86, 0.755), (0.30, 0.665))
    arrow(ax, (0.86, 0.755), (0.765, 0.665))
    box(
        ax,
        0.00,
        0.06,
        0.47,
        0.24,
        "같은 평가 언어의 두 조건을\n같은 질문끼리 비교",
        purple,
        size=11,
    )
    box(
        ax,
        0.53,
        0.06,
        0.47,
        0.24,
        "SCD 추가 전후와\n단일 기법 적용 전후를 비교",
        green,
        size=11,
    )
    arrow(ax, (0.235, 0.395), (0.235, 0.305))
    arrow(ax, (0.765, 0.395), (0.765, 0.305))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, "fig5_0_evaluation_design")


def wrap_evidence(text, limit=32):
    lines = []
    line = ""
    width = 0
    clean = re.sub(r"\s+", " ", text).replace("**", "")
    for token in re.findall(r"\S+\s*", clean):
        units = sum(0.55 if ord(ch) < 128 else 1 for ch in token)
        if width + units > limit and line:
            lines.append(line.rstrip())
            line = ""
            width = 0
        line += token
        width += units
    if line:
        lines.append(line.rstrip())
    return lines


def io_example():
    """Measurement example selected from the completed, reviewed retrieval recoveries."""
    cases = json.loads((HERE / "REVIEWED_CASES.json").read_text(encoding="utf-8"))
    recoveries = [
        c
        for c in cases
        if c["base"] == "H0C0S0"
        and c["applied"] == "H1C0S0"
        and c["scores"]["context_recall"]["base"] == 0
        and c["scores"]["context_recall"]["applied"] == 1
    ]
    assert recoveries, "Complete case analysis before selecting the measurement example"
    case = recoveries[0]
    needle = next(
        text
        for side, field, text, presence in case["checks"]
        if side == "applied" and field == "contexts" and presence
    )
    passages = re.sub(r"\s+", " ", " ".join(case["applied_record"]["contexts"]))
    sentence = next(
        x for x in re.split(r"(?<=[.!?])\s+", passages) if needle.lower() in x.lower()
    )
    quotes = json.loads((HERE / "CASE_EXCERPTS.json").read_text(encoding="utf-8"))
    quote = next(e for e in quotes if e["title"] == case["title"])["applied"][0]
    assert quote in case["applied_record"]["answer"]
    rows = [
        ("질문", case["query"]),
        ("참조 답변", case["answer_span"] + f" (원문 {case['source_page']}쪽)"),
        ("입력 구간", sentence),
        ("생성 답변", quote),
    ]
    score = case["scores"]
    metrics = f"근거 충실도 {score['faithfulness']['applied']:.3f} · 답변 관련성 {score['answer_relevancy']['applied']:.3f} / 문맥 정밀도 {score['context_precision']['applied']:.3f} · 문맥 재현율 {score['context_recall']['applied']:.3f}"
    rows.append(("평가값", metrics))
    wrapped = [(label, wrap_evidence(body)) for label, body in rows]
    row_heights = [len(lines) * 15.5 + 16 for _, lines in wrapped]
    height = sum(row_heights) + 10
    fig, ax = plt.subplots(figsize=(6.3, height / 72))
    ax.set_xlim(0, 453.6)
    ax.set_ylim(0, height)
    ax.axis("off")
    y = height - 5
    for (label, lines), rh in zip(wrapped, row_heights):
        ax.text(2, y, label, fontsize=11, fontweight="bold", color="#695184", va="top")
        ax.text(
            84,
            y,
            "\n".join(lines),
            fontsize=10.5,
            color=INK,
            va="top",
            linespacing=1.45,
        )
        y -= rh
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in ax.texts:
        bounds = text.get_window_extent(renderer)
        assert (
            bounds.x0 >= 0
            and bounds.x1 <= fig.bbox.x1
            and bounds.y0 >= 0
            and bounds.y1 <= fig.bbox.y1
        ), "I/O card text overflow"
    save(fig, "fig5_2_io_example")
    write_path = HERE / "MEASUREMENT_EXAMPLE.json"
    write_path.write_text(
        json.dumps(
            {
                "query_id": case["query_id"],
                "title": case["title"],
                "applied": case["applied"],
                "selection": "전체 질문 분석 후 재현된 검색 근거 회복 사례",
                "passage": sentence,
                "answer_quote": quote,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    data = pd.read_csv(HERE / "QUERY_LEVEL_RESULTS.csv", encoding="utf-8-sig")
    parallel(data, CONDITIONS[:4], "fig5_3_parallel_english", "영어 근거")
    parallel(data, CONDITIONS[4:], "fig5_4_parallel_korean", "한국어 번역 근거")
    evaluation_design()
    io_example()
    print(
        "PASS: 2 parallel-coordinate figures (60 questions x 4 conditions each), design and I/O figures"
    )


if __name__ == "__main__":
    main()
