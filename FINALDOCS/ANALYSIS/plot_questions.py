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


# Each panel: (condition shown, base condition, metric used to pick extremes, metric label)
SINGLE_PANELS = [
    ("H0C0S0", None, None, None),
    ("H1C0S0", "H0C0S0", "answer_relevancy", "답변 관련성"),
    ("H0C1S0", "H0C0S0", "faithfulness", "근거 충실도"),
    ("H0C0S1", "H0C0S0", "korean_ratio", "한국어 문자 비율"),
]
COMBINED_PANELS = [
    ("H1C1S0", "H1C0S0", "answer_relevancy", "답변 관련성"),
    ("H1C1S1", "H1C0S1", "answer_relevancy", "답변 관련성"),
    ("H1C1S0", "H0C1S0", "answer_relevancy", "답변 관련성"),
    ("H1C1S1", "H0C1S1", "answer_relevancy", "답변 관련성"),
]
UP, DOWN, GREY = "#1f5fa8", "#c0392b", "#b8bcc4"
TOP = 3


def extremes(data, code, base, metric):
    """Select extremes from nonzero, observed values on the ranking axis."""
    w = data.pivot(index="query_id", columns="condition", values=metric)
    pair = w[[base, code]].dropna()
    pair = pair[(pair[base] != 0) & (pair[code] != 0)]
    d = (pair[code] - pair[base]).sort_values()
    ups = [q for q in d.index[::-1][:TOP] if d[q] > 0.05]
    downs = [q for q in d.index[:TOP] if d[q] < -0.05]
    return ups, downs


def display_values(values):
    """Hide zero-valued points without changing stored scores or bridging gaps."""
    shown = np.asarray(values, dtype=float).copy()
    shown[shown == 0] = np.nan
    return shown


TIME_AXIS_SECONDS = 180
PROFILE_AXES = AXES + ["duration_seconds"]
PROFILE_LABELS = LABELS + ["처리 시간\n(초)"]
PROFILE_CASES = {
    "H1C0S0": {"ext_raptor_004": "BIC가 결정하는 항목"},
    "H0C1S0": {"ext_cad_009": "XSUM 수치 비교"},
}


def profile_coordinates(values):
    """Position the seconds axis on its own inverted, explicitly labelled scale."""
    shown = display_values(values)
    assert len(shown) == 6
    assert np.isnan(shown[-1]) or 0 < shown[-1] <= TIME_AXIS_SECONDS
    shown[-1] = 1 - shown[-1] / TIME_AXIS_SECONDS
    return shown


def type_profiles(data, code, name, size=(6.3, 9.2), scale=1, save_to=None):
    """One question per line, four question-type panels, one condition per figure."""
    subset = data[data.condition == code]
    assert subset.query_id.is_unique and len(subset) == 60
    fig, axes = plt.subplots(4, 1, figsize=size, sharey=True)
    x = np.arange(6)
    labels = (
        PROFILE_LABELS if scale == 1 else [s.replace("\n", " ") for s in PROFILE_LABELS]
    )
    selected = PROFILE_CASES.get(code, {})
    for ax, typ in zip(axes, TYPES):
        group = subset[subset.question_type == typ]
        names = []
        for r in group.itertuples():
            highlighted = r.query_id in selected
            ax.plot(
                x,
                profile_coordinates([getattr(r, m) for m in PROFILE_AXES]),
                color="#1b5f97" if highlighted else "#87929e",
                alpha=1 if highlighted else 0.6,
                lw=(2.2 if highlighted else 0.85) * scale,
                marker=".",
                markersize=(3 if highlighted else 1.8) * scale,
                zorder=3 if highlighted else 1,
            )
            if highlighted:
                names.append(selected[r.query_id])
        ax.set_title(
            typ.replace(" 및 ", "·") + f" 질문 {len(group)}개",
            loc="left",
            fontsize=11 * scale,
            fontweight="bold",
            pad=5 * scale,
        )
        if names:
            ax.text(
                1,
                1.11,
                "굵은 선은 " + ", ".join(names),
                transform=ax.transAxes,
                ha="right",
                fontsize=8.5 * scale,
                color="#1b5f97",
            )
        for k in x:
            ax.axvline(k, color="#d1d7de", lw=0.7 * scale, zorder=0)
        for y, seconds in [(1, 0), (0.5, 90), (0, 180)]:
            ax.text(5.07, y, str(seconds), va="center", fontsize=8 * scale, color=INK)
        ax.set_xlim(-0.15, 5.45)
        ax.set_ylim(-0.03, 1.04)
        ax.set_yticks([0, 0.5, 1], ["0", "0.5", "1"])
        ax.set_xticks(x, labels)
        ax.tick_params(length=0, labelsize=9.5 * scale)
        ax.spines[["top", "right", "bottom"]].set_visible(False)
    if scale == 1:
        fig.suptitle(
            f"{NAMES[code]} 적용 후 질문 유형별 개별 점수",
            y=0.986,
            fontsize=12,
            fontweight="bold",
        )
        language = "한국어 번역" if code[-1] == "1" else "영어"
        fig.text(
            0.5,
            0.95,
            f"{language} 근거 평가. 한 선은 실제 질문 하나",
            ha="center",
            fontsize=9,
        )
        fig.text(
            0.5,
            0.018,
            "0점과 결측값은 해당 축에 표시하지 않음\n시간축은 초 단위이며 위쪽일수록 짧음",
            ha="center",
            fontsize=8.5,
        )
    fig.subplots_adjust(
        left=0.065,
        right=0.975,
        top=0.9 if scale == 1 else 0.95,
        bottom=0.09 if scale == 1 else 0.08,
        hspace=0.9 if scale == 1 else 1.05,
    )
    if save_to:
        fig.savefig(save_to, dpi=200, facecolor="white")
        plt.close(fig)
    else:
        save(fig, name)


def parallel(
    data, panels, path_or_name, size=(6.3, 9.2), scale=1.0, save_to=None, top=None
):
    """One condition per row; 60 grey lines, extremes coloured (solid = shown, dashed = base)."""
    fig, axes = plt.subplots(len(panels), 1, figsize=size, sharey=True)
    x = np.arange(len(AXES))
    labels = LABELS if scale == 1.0 else [lab.replace(chr(10), " ") for lab in LABELS]
    by = data.set_index(["query_id", "condition"])
    for ax, (code, base, metric, metric_label) in zip(axes, panels):
        g = data[data.condition == code]
        assert len(g) == 60
        for r in g.itertuples():
            ax.plot(
                x,
                display_values([getattr(r, m) for m in AXES]),
                color=GREY,
                alpha=0.55,
                lw=0.8 * scale,
                zorder=1,
                marker=".",
                markersize=2 * scale,
            )
        title = f"조건 {CONDITIONS.index(code) + 1}  {NAMES[code]}"
        if base:
            ups, downs = extremes(data, code, base, metric)
            for qs, colour in [(ups, UP), (downs, DOWN)]:
                for q in qs:
                    ax.plot(
                        x,
                        display_values([by.loc[(q, base), m] for m in AXES]),
                        color=colour,
                        lw=1.3 * scale,
                        ls=(0, (3, 2)),
                        alpha=0.9,
                        zorder=3,
                        marker=".",
                        markersize=2 * scale,
                    )
                    ax.plot(
                        x,
                        display_values([by.loc[(q, code), m] for m in AXES]),
                        color=colour,
                        lw=2.3 * scale,
                        zorder=4,
                        marker=".",
                        markersize=2 * scale,
                    )
            title += f"  ·  기준 {NAMES[base]}, {metric_label} 변화 상·하위 {TOP}개"
        for k in x:
            ax.axvline(k, color="#8a909a", lw=0.8 * scale, zorder=0)
        ax.set_xlim(-0.3, len(AXES) - 0.7)
        ax.set_ylim(-0.04, 1.04)
        ax.set_yticks([0, 0.5, 1.0], ["0", "0.5", "1"])
        ax.set_xticks(x, labels)
        ax.tick_params(labelsize=10 * scale, length=0)
        for side in ["top", "right", "bottom"]:
            ax.spines[side].set_visible(False)
        ax.set_title(
            title,
            loc="left",
            fontsize=10.5 * scale,
            fontweight="bold",
            color=INK,
            pad=4,
        )
    handles = [
        plt.Line2D([], [], color=GREY, lw=2.5),
        plt.Line2D([], [], color=UP, lw=2.5),
        plt.Line2D([], [], color=DOWN, lw=2.5),
        plt.Line2D([], [], color=INK, lw=1.4, ls=(0, (3, 2))),
    ]
    fig.legend(
        handles,
        ["질문별 점수", "증가 상위", "감소 상위", "점선은 기준 조건의 같은 질문"],
        loc="upper center",
        ncol=4,
        frameon=False,
        fontsize=9.5 * scale,
        bbox_to_anchor=(0.5, 1.0),
        handlelength=1.8,
        columnspacing=1.4,
    )
    fig.subplots_adjust(
        left=0.07,
        right=0.985,
        top=top or (0.93 if scale == 1.0 else 0.9),
        bottom=0.05,
        hspace=0.8 if scale == 1.0 else 0.95,
    )
    fig.text(
        0.5, 0.012, "0점과 결측값은 표시하지 않음", ha="center", fontsize=9.5 * scale
    )
    if save_to:
        fig.savefig(save_to, dpi=200, facecolor="white")
        plt.close(fig)
    else:
        save(fig, path_or_name)


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
    for code, name in [
        ("H1C0S0", "fig5_3_parallel_hyde_types"),
        ("H0C1S0", "fig5_4_parallel_cad_types"),
        ("H0C0S1", "fig5_5_parallel_scd_types"),
    ]:
        type_profiles(data, code, name)
    evaluation_design()
    io_example()
    print(
        "PASS: 3 parallel-coordinate figures, each 60 questions in 4 type panels, 6 raw-unit axes; design and I/O figures"
    )


if __name__ == "__main__":
    main()
