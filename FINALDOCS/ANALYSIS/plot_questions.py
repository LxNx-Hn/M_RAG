"""Figures for chapter 5, drawn from the stored measurements and records.

Performance is shown only as parallel coordinates of raw scores. One figure
per question group stacks four conditions (no technique, HyDE, CAD, SCD) from
top to bottom; every question of the group is one line. In each technique
panel the question whose key score rose most and the one that fell most
against no technique are coloured, with their no-technique scores dashed.
Two non-performance figures explain the evaluation design and show one stored
input/output example.
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

from analyze_questions import (  # noqa: E402
    BASE,
    CONDITIONS,
    GROUPS,
    HERE,
    NAMES,
    QUALITY,
    ROOT,
    TYPES,
)

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
UP, DOWN, GREY = "#c0392b", "#1f5fa8", "#b8bcc4"
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


# (condition, metric whose change against no technique selects the coloured lines)
GROUP_PANELS = [
    ("H0C0S0", None),
    ("H1C0S0", "answer_relevancy"),
    ("H0C1S0", "faithfulness"),
    ("H0C0S1", "korean_ratio"),
]
METRIC_LABEL = {
    "answer_relevancy": "답변 관련성",
    "faithfulness": "근거 충실도",
    "korean_ratio": "한국어 문자 비율",
}
GROUP_FIGURES = dict(
    zip(
        GROUPS,
        [
            "fig5_3_parallel_numeric",
            "fig5_4_parallel_method",
            "fig5_5_parallel_concept",
        ],
    )
)


def group_extremes(data, group, code, metric):
    """Largest rise and fall of `metric` against no technique inside one group.

    Pairs with a zero on either side are left out, as in the paired counts.
    """
    g = data[data.question_group == group]
    w = g.pivot(index="query_id", columns="condition", values=metric)
    pair = w[[BASE, code]].dropna()
    pair = pair[(pair[BASE] != 0) & (pair[code] != 0)]
    d = (pair[code] - pair[BASE]).sort_values()
    up = d.index[-1] if d.iloc[-1] > 0.05 else None
    down = d.index[0] if d.iloc[0] < -0.05 else None
    return up, down, d


def group_profiles(
    data, group, size=(6.3, 7.4), scale=1.0, save_to=None, highlights=None, compact=False
):
    """Four condition panels for one question group (stacked, or 2 x 2 when compact)."""
    by = data.set_index(["query_id", "condition"])
    members = data[(data.question_group == group) & (data.condition == BASE)]
    if compact:
        fig, axes = plt.subplots(2, 2, figsize=size, sharey=True)
        axes = list(axes.flatten())
    else:
        fig, axes = plt.subplots(len(GROUP_PANELS), 1, figsize=size, sharey=True)
    x = np.arange(len(AXES))
    labels = LABELS if (scale == 1.0 or compact) else [s.replace("\n", " ") for s in LABELS]
    for ax, (code, metric) in zip(axes, GROUP_PANELS):
        for q in members.query_id:
            ax.plot(
                x,
                display_values([by.loc[(q, code), m] for m in AXES]),
                color=GREY,
                alpha=0.75,
                lw=0.9 * scale,
                marker=".",
                markersize=2.2 * scale,
                zorder=1,
            )
        title = f"조건 {CONDITIONS.index(code) + 1}  {NAMES[code]}"
        if metric:
            up, down, d = group_extremes(data, group, code, metric)
            for q, colour in [(up, UP), (down, DOWN)]:
                if q is None:
                    continue
                ax.plot(
                    x,
                    display_values([by.loc[(q, BASE), m] for m in AXES]),
                    color=colour,
                    lw=1.2 * scale,
                    ls=(0, (3, 2)),
                    zorder=3,
                    marker=".",
                    markersize=2.2 * scale,
                )
                ax.plot(
                    x,
                    display_values([by.loc[(q, code), m] for m in AXES]),
                    color=colour,
                    lw=2.4 * scale,
                    zorder=4,
                    marker="^" if colour == UP else "v",
                    markersize=5.5 * scale,
                    markeredgewidth=0,
                )
                if highlights is not None:
                    highlights.append(
                        {
                            "group": group,
                            "condition": code,
                            "metric": metric,
                            "direction": "up" if colour == UP else "down",
                            "query_id": q,
                            "base": float(by.loc[(q, BASE), metric]),
                            "applied": float(by.loc[(q, code), metric]),
                            "delta": float(d[q]),
                        }
                    )
            if compact:
                ax.set_title(
                    f"색 선 기준 {METRIC_LABEL[metric]}",
                    loc="right",
                    fontsize=8.5 * scale,
                    color=INK,
                    pad=7 * scale,
                )
            else:
                ax.text(
                    1,
                    1.06,
                    f"색 선은 미적용 대비 {METRIC_LABEL[metric]} 변화가 가장 큰 질문",
                    transform=ax.transAxes,
                    ha="right",
                    fontsize=8.5 * scale,
                    color=INK,
                )
        for k in x:
            ax.axvline(k, color="#c9cfd6", lw=0.8 * scale, zorder=0)
        ax.set_xlim(-0.2, len(AXES) - 0.8)
        ax.set_ylim(-0.04, 1.04)
        ax.set_yticks([0, 0.5, 1.0], ["0", "0.5", "1"])
        ax.set_xticks(x, labels if (not compact or ax in axes[-2:]) else [""] * len(labels))
        ax.tick_params(labelsize=9.5 * scale, length=0)
        ax.spines[["top", "right", "bottom"]].set_visible(False)
        ax.set_title(title, loc="left", fontsize=10.5 * scale, fontweight="bold", color=INK, pad=(7 if compact else 4) * scale)
    handles = [
        plt.Line2D([], [], color=GREY, lw=2.2),
        plt.Line2D([], [], color=UP, lw=2.4, marker="^", markersize=6, markeredgewidth=0),
        plt.Line2D([], [], color=DOWN, lw=2.4, marker="v", markersize=6, markeredgewidth=0),
        plt.Line2D([], [], color=INK, lw=1.2, ls=(0, (3, 2))),
    ]
    fig.legend(
        handles,
        ["질문별 점수", "가장 크게 오른 질문", "가장 크게 내린 질문", "같은 질문의 미적용 점수"],
        loc="upper center",
        ncol=2 if compact else 4,
        frameon=False,
        fontsize=9 * scale,
        bbox_to_anchor=(0.5, 1.0),
        handlelength=1.8,
        columnspacing=1.2,
    )
    if compact:
        fig.text(0.99, 0.005, "0점과 결측값은 선으로 잇지 않음", ha="right", va="bottom", fontsize=8.5 * scale, color=INK)
    else:
        fig.text(0.5, 0.008, "0점과 결측값은 선으로 잇지 않음", ha="center", fontsize=8.5 * scale, color=INK)
    if compact:
        h = size[1]
        fig.subplots_adjust(
            left=0.06, right=0.97, top=1 - 0.75 * scale / h, bottom=0.62 * scale / h, hspace=0.62 * 5.6 / h, wspace=0.16
        )
    else:
        fig.subplots_adjust(left=0.07, right=0.985, top=0.925 if scale == 1.0 else 0.9, bottom=0.075, hspace=0.85 if scale == 1.0 else 0.95)
    if save_to:
        fig.savefig(save_to, dpi=200, facecolor="white")
        plt.close(fig)
    else:
        save(fig, GROUP_FIGURES[group])


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
        0.38,
        0.47,
        0.28,
        "RAGAS 품질 지표 4개\nSCD 미적용 조건은 영어 근거\nSCD 적용 조건은 한국어 번역 근거",
        purple,
        size=10.5,
    )
    box(
        ax,
        0.53,
        0.38,
        0.47,
        0.28,
        "한국어 문자 비율과 처리 시간\n저장된 답변과 실행 기록에서 계산",
        green,
        size=10.5,
    )
    arrow(ax, (0.86, 0.755), (0.30, 0.665))
    arrow(ax, (0.86, 0.755), (0.765, 0.665))
    box(
        ax,
        0.00,
        0.04,
        1.00,
        0.24,
        "질문과 조건으로 연결한 분석\n조건별 평균과 표준편차, 질문 유형별 평균, 질문별 원점수와 미적용 대비 변화",
        INK,
        size=10.5,
    )
    arrow(ax, (0.235, 0.375), (0.235, 0.285))
    arrow(ax, (0.765, 0.375), (0.765, 0.285))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, "fig5_0_evaluation_design")


def wrap_evidence(text, limit=35):
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
    metrics = (
        f"근거 충실도 {score['faithfulness']['applied']:.2f}, 답변 관련성 {score['answer_relevancy']['applied']:.2f}\n"
        f"문맥 정밀도 {score['context_precision']['applied']:.2f}, 문맥 재현율 {score['context_recall']['applied']:.2f}"
    )
    rows.append(("평가값", metrics))
    wrapped = [
        (label, body.split("\n") if label == "평가값" else wrap_evidence(body))
        for label, body in rows
    ]
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


GENERATION = (
    ROOT
    / "experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
)
EXAMPLE_ID = "track1_0033"


def _clause(text, needle):
    """Shortest sentence part of ``text`` that ends with ``needle``."""
    clean = re.sub(r"\s+", " ", text)
    for sentence in re.split(r"(?<=[.!?])\s+", clean):
        at = sentence.find(needle)
        if at >= 0:
            return sentence[: at + len(needle)]
    raise AssertionError(f"Example phrase missing: {needle}")


def mechanism_record():
    """Stored record of one numeric question under no technique, HyDE, CAD and SCD."""
    runs = {}
    with GENERATION.open(encoding="utf-8") as handle:
        for line in handle:
            if EXAMPLE_ID not in line:
                continue
            row = json.loads(line)
            if row["query_id"] != EXAMPLE_ID:
                continue
            code = "H{}C{}S{}".format(*(int(bool(row[k])) for k in ("use_hyde", "use_cad", "use_scd")))
            runs[code] = row
    assert set(runs) == set(CONDITIONS), "Example question must have all eight runs"
    data = pd.read_csv(HERE / "QUERY_LEVEL_RESULTS.csv", encoding="utf-8-sig")
    scores = data[data.query_id == EXAMPLE_ID].set_index("condition")
    base, hyde, cad, scd = (runs[c] for c in ("H0C0S0", "H1C0S0", "H0C1S0", "H0C0S1"))
    reform = hyde["retrieval_reformulation"]
    passage = _clause(" ".join(hyde["contexts"]), "32B parameters")
    record = {
        "query_id": EXAMPLE_ID,
        "query": scores.loc[BASE, "query"],
        "question_group": scores.loc[BASE, "question_group"],
        "answer_span": scores.loc[BASE, "answer_span"],
        "source_page": int(scores.loc[BASE, "source_page"]),
        "translated_query": reform["translated_query"],
        "hyde_clause": _clause(reform["hyde_document"], "13 billion parameters"),
        "retrieved_clause": passage,
        "base_unit": "3.2 billion",
        "cad_unit": "32 billion parameters",
        "base_quote": "This model is configured with 32B parameters",
        "scd_quote": "모델은 32B 파라미터로 구성되어 있으며",
        "scores": {
            "answer_relevancy": [scores.loc[BASE, "answer_relevancy"], scores.loc["H1C0S0", "answer_relevancy"]],
            "faithfulness": [scores.loc[BASE, "faithfulness"], scores.loc["H0C1S0", "faithfulness"]],
            "korean_ratio": [scores.loc[BASE, "korean_ratio"], scores.loc["H0C0S1", "korean_ratio"]],
        },
    }
    assert record["base_unit"] in base["generated_answer"]
    assert record["base_quote"] in base["generated_answer"]
    assert record["cad_unit"] in cad["generated_answer"]
    assert record["scd_quote"] in scd["generated_answer"]
    assert record["answer_span"] in passage
    return record


RETRIEVE, GENERATE = "#695184", "#1b7837"


def example_mechanism(save_to=None, scale=1.0):
    """Diagram of one numeric question passing through HyDE, CAD and SCD.

    Quoted answers and score changes come from the stored run; the embedding
    dots and the candidate word sizes illustrate how each technique works.
    """
    rec = mechanism_record()
    s = rec["scores"]
    fig = plt.figure(figsize=(6.3 * scale, 2.885 * scale))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 45.9)
    ax.axis("off")
    f = scale * 1.06
    MUTED, FAINT = "#5f6470", "#9aa0a8"

    def rbox(x, y, w, h, fc, ec, lw=1.0, r=1.0, ls="-"):
        ax.add_patch(
            FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw * f, ls=ls)
        )

    def flow(a, b, colour=INK, ls="-", lw=1.0):
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=colour, lw=lw * f, ls=ls, mutation_scale=8 * f))

    def label(x, y, text, size=6.4, colour=INK, bold=False, ha="left", va="center"):
        ax.text(x, y, text, fontsize=size * f, color=colour, fontweight="bold" if bold else "normal", ha=ha, va=va, linespacing=1.35)

    def result(x, key, name):
        before, after = s[key]
        up = after > before
        label(x, 2.6, f"{name} {before:.2f}에서 {after:.2f} {'▲' if up else '▼'}", 6.6, UP if up else DOWN, True, "center")

    def document(x, y, w, h, ec, missing=False):
        c = w * 0.32
        ls = "--" if missing else "-"
        ax.add_patch(
            plt.Polygon([(x, y), (x + w, y), (x + w, y + h - c), (x + w - c, y + h), (x, y + h)], fc="#ffffff", ec=ec, lw=0.9 * f, ls=ls)
        )
        ax.plot([x + w - c, x + w - c, x + w], [y + h, y + h - c, y + h - c], color=ec, lw=0.7 * f, ls=ls)
        for k in range(2):
            ax.plot([x + 0.5, x + w - 0.5 - (c if k == 0 else 0)], [y + h - 1.0 - k * 0.8] * 2, color=ec, lw=0.6 * f)
        if missing:
            ax.plot([x - 0.4, x + w + 0.4], [y - 0.4, y + h + 0.4], color=FAINT, lw=0.9 * f)
            ax.plot([x - 0.4, x + w + 0.4], [y + h + 0.4, y - 0.4], color=FAINT, lw=0.9 * f)
        else:
            label(x + w / 2, y + 1.0, "32B", 4.6, GENERATE, True, "center")

    def answer(x, y, w, h, name, quote, ok, note=None):
        colour = GENERATE if ok else DOWN
        rbox(x, y, w, h, "#ffffff", colour, 0.9)
        label(x + 0.9, y + h - 1.3, name, 5.6, colour, True)
        label(x + 0.9, y + h / 2 - (0.3 if note else 0.8), quote, 5.3, INK)
        if note:
            label(x + 0.9, y + 1.1, note, 5.0, colour, True)
        mx, my = x + w - 1.5, y + h - 1.4
        if ok:
            ax.plot([mx - 0.7, mx - 0.2, mx + 0.8], [my, my - 0.6, my + 0.7], color=colour, lw=1.5 * f, solid_capstyle="round")
        else:
            for d in (1, -1):
                ax.plot([mx - 0.6, mx + 0.6], [my - 0.6 * d, my + 0.6 * d], color=colour, lw=1.5 * f, solid_capstyle="round")

    # question
    rbox(0.3, 39.9, 99.4, 5.6, "#ffffff", INK, 1.1)
    label(2.0, 42.7, "예시 질문", 7.2, RETRIEVE, True)
    label(13.5, 42.7, rec["query"], 7.4, INK)
    label(98.2, 42.7, f"정답 근거 {rec['answer_span']}(원문 {rec['source_page']}쪽)", 6.2, MUTED, ha="right")

    panels = [
        (0.3, "HyDE", "Gao 외, ACL 2023", "검색 단계", "가상 답변으로 실제 구간을 찾음", RETRIEVE, "#f4f1f8"),
        (34.0, "CAD", "Shi 외, NAACL 2024", "생성 단계", "문서가 있을 때 오르는 토큰을 키움", GENERATE, "#eef6ef"),
        (67.7, "SCD", "Li 외, AAAI 2026", "생성 단계", "한국어 토큰의 점수를 키움", GENERATE, "#eef6ef"),
    ]
    pw, py, ph = 32.0, 6.0, 31.5
    for x0, name, who, stage, idea, ec, fc in panels:
        rbox(x0, py, pw, ph, fc, ec, 1.1)
        label(x0 + 1.5, py + ph - 2.5, name, 9.5, INK, True)
        label(x0 + 1.5 + len(name) * 2.3, py + ph - 2.8, who, 6.0, MUTED)
        label(x0 + pw - 1.3, py + ph - 2.5, stage, 6.0, ec, True, "right")
        label(x0 + 1.5, py + ph - 6.3, idea, 6.4, INK, True)

    # HyDE: hypothetical passage written by the LLM, real passage found near it
    rbox(1.5, 19.6, 14.6, 9.4, "#ffffff", RETRIEVE, 0.9, ls="--")
    label(2.5, 27.4, "LLM이 쓴 가상 구간", 5.8, RETRIEVE, True)
    label(2.5, 23.0, "“… approximately 13\nbillion parameters …”", 5.3, INK)
    rbox(1.5, 8.6, 14.6, 9.4, "#ffffff", INK, 0.9)
    label(2.5, 16.4, "원문의 실제 구간", 5.8, INK, True)
    label(2.5, 12.0, "“… configured with\n32B parameters …”", 5.3, INK)
    rbox(17.3, 8.6, 13.8, 20.0, "#ffffff", "#c9c3d6", 0.7)
    label(18.1, 27.3, "임베딩 공간", 5.2, MUTED)
    star, near = (23.4, 19.9), (24.8, 18.6)
    rng = np.random.default_rng(11)
    pts = rng.uniform([18.4, 11.8], [30.2, 25.8], size=(18, 2))
    keep = np.array([p for p in pts if np.hypot(p[0] - 24.2, p[1] - 18.9) > 4.0])
    ax.scatter(keep[:, 0], keep[:, 1], s=6 * f * f, color="#b8bcc4", zorder=2)
    ax.add_patch(plt.Circle(star, 3.0, fill=False, ls="--", ec=RETRIEVE, lw=0.7 * f))
    ax.scatter(*star, s=60 * f * f, marker="*", color=RETRIEVE, zorder=5)
    ax.scatter(*near, s=24 * f * f, color=INK, zorder=4)
    flow((16.2, 24.0), (22.3, 20.5), RETRIEVE)
    flow((24.2, 18.1), (16.3, 13.4), INK)
    label(24.2, 9.7, "가까운 구간 검색", 5.2, INK, ha="center")

    # CAD: the model reads the question with and without the document,
    # then leans toward what the document adds
    for yc, missing in ((25.4, False), (18.6, True)):
        document(35.6, yc - 1.9, 3.0, 3.8, FAINT if missing else GENERATE, missing)
        if not missing:
            label(39.6, yc, "+", 6.4, INK, True, "center")
        rbox(40.5, yc - 1.4, 3.8, 2.8, "#ffffff", INK, 0.8, r=0.8)
        label(42.4, yc, "질문", 5.4, INK, True, "center")
        flow((44.5, yc), (47.4, yc))
        rbox(47.5, yc - 1.7, 3.6, 3.4, "#ffffff", GENERATE, 1.0, r=0.6)
        label(49.3, yc, "LM", 6.0, GENERATE, True, "center")
    hub = (57.9, 21.9)
    flow((51.4, 25.4), (56.2, 22.7), GENERATE, lw=1.8)
    flow((51.4, 18.6), (56.2, 21.1), FAINT)
    label(55.2, 25.4, "키움", 5.2, GENERATE, True, "center")
    label(55.2, 18.6, "뺌", 5.2, MUTED, True, "center")
    ax.add_patch(plt.Circle(hub, 1.8, fc="#ffffff", ec=GENERATE, lw=1.0 * f))
    label(hub[0], hub[1], "결합", 5.0, GENERATE, True, "center")
    flow((hub[0], hub[1] - 1.9), (hub[0], 15.2), GENERATE)
    answer(35.3, 7.4, 13.6, 7.6, "미적용", f"“… {rec['base_unit']} …”", False, "틀린 수치")
    answer(51.1, 7.4, 13.6, 7.6, "CAD 적용", "“… 32 billion\nparameters …”", True, "원문과 같은 수치")

    # SCD: while the answer is written in Korean, Korean candidates are scaled
    # up and English ones down, so the Korean word fills the slot
    label(69.2, 28.7, "생성 중인 답변", 5.2, MUTED)
    rbox(69.0, 23.4, 29.4, 4.2, "#ffffff", GENERATE, 0.9)
    label(70.0, 25.5, "모델은 32B", 6.2, INK, True)
    rbox(77.9, 24.0, 8.4, 3.0, "#ffffff", GENERATE, 0.8, r=0.6, ls="--")
    label(86.8, 25.5, "로 구성되어 …", 6.2, INK, True)
    rbox(70.8, 17.4, 11.2, 4.0, "#d9eed9", GENERATE, 1.0, r=0.8)
    label(76.4, 19.4, "파라미터", 7.6, GENERATE, True, "center")
    label(76.4, 16.2, "한국어 ×1.1", 5.4, GENERATE, True, "center")
    rbox(86.2, 18.2, 9.4, 2.4, "#f3f4f6", FAINT, 0.7, r=0.6)
    label(90.9, 19.4, "parameters", 5.0, MUTED, False, "center")
    label(90.9, 16.2, "영어 ×0.9", 5.4, DOWN, True, "center")
    flow((75.8, 21.6), (80.4, 23.9), GENERATE, lw=1.6)
    answer(69.0, 7.4, 14.2, 7.6, "미적용", "“This model is\nconfigured with\n32B parameters”", False)
    answer(84.2, 7.4, 14.2, 7.6, "SCD 적용", "“모델은 32B\n파라미터로 구성되어\n있으며”", True)

    result(16.3, "answer_relevancy", "답변 관련성")
    result(50.0, "faithfulness", "근거 충실도")
    result(83.7, "korean_ratio", "한국어 문자 비율")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in ax.texts:
        b = text.get_window_extent(renderer)
        assert b.x0 >= -1 and b.x1 <= fig.bbox.x1 + 1 and b.y0 >= -1 and b.y1 <= fig.bbox.y1 + 1, "Mechanism figure text overflow"
    if save_to:
        fig.savefig(save_to, dpi=250, facecolor="white")
        plt.close(fig)
    else:
        save(fig, "fig4_2_example_mechanism")
    (HERE / "EXAMPLE_MECHANISM.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2, default=float) + "\n", encoding="utf-8"
    )
    return rec


def main():
    data = pd.read_csv(HERE / "QUERY_LEVEL_RESULTS.csv", encoding="utf-8-sig")
    highlights = []
    for group in GROUPS:
        group_profiles(data, group, highlights=highlights)
    (HERE / "FIGURE_HIGHLIGHTS.json").write_text(
        json.dumps(highlights, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    evaluation_design()
    io_example()
    example_mechanism()
    print(
        f"PASS: 3 group figures x 4 condition panels; {len(highlights)} highlighted questions; design, I/O and example mechanism figures"
    )


if __name__ == "__main__":
    main()
