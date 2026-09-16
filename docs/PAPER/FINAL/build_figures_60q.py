"""Build the final 60-query thesis figures from retained experiment artifacts."""

import csv
import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
DATA = BASE / "generated"
OUT = BASE / "figures_60q"
OUT.mkdir(exist_ok=True)

FONT = Path("C:/Windows/Fonts/malgun.ttf")
font_manager.fontManager.addfont(str(FONT))
plt.rcParams.update(
    {
        "font.family": "Malgun Gothic",
        "font.size": 9,
        "text.color": "#222222",
        "axes.labelcolor": "#222222",
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
        "svg.hashsalt": "mrag-thesis-60q",
        "savefig.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

DARK, GRAY, LIGHT = "#222222", "#AAB2BA", "#F5F7FA"
BLUE, GREEN, ORANGE, RED = "#2F6BFF", "#24866D", "#C86A1B", "#B54747"
CONFIGS = [
    "H0C0S0",
    "H0C1S0",
    "H0C0S1",
    "H0C1S1",
    "H1C0S0",
    "H1C1S0",
    "H1C0S1",
    "H1C1S1",
]


def rows(name):
    with (DATA / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def save(fig, name):
    for label in fig.findobj(matplotlib.text.Text):
        label.set_text(label.get_text().replace("−", "-"))
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": None}, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def diagram_canvas(width=8.0, height=4.5):
    fig, ax = plt.subplots(figsize=(width, height))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set(xlim=(0, 100), ylim=(0, 100))
    ax.axis("off")
    return fig, ax


def text(ax, x, y, value, size=9, color=DARK, weight="normal", ha="center"):
    return ax.text(
        x,
        y,
        value,
        fontsize=size,
        color=color,
        weight=weight,
        ha=ha,
        va="center",
        linespacing=1.4,
    )


def box(ax, x, y, w, h, value, edge=GRAY, face=LIGHT, size=9):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.5,rounding_size=2",
            linewidth=1.2,
            edgecolor=edge,
            facecolor=face,
        )
    )
    text(ax, x + w / 2, y + h / 2, value, size=size)


def arrow(ax, start, end, color=GRAY, width=1.2):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=width,
            color=color,
            shrinkA=3,
            shrinkB=3,
        )
    )


def title(fig, label):
    """Captions belong in the manuscript; never place figure numbers or titles inside art."""


def read_ci(value):
    parsed = value.strip("{}").replace("'", "").split(",")
    return float(parsed[0].split(":")[1]), float(parsed[1].split(":")[1])


def architecture_figures():
    fig, ax = diagram_canvas(8.2, 3.8)
    title(fig, "그림 1-1. 한국어 질의 기반 영어 학술문서 RAG 연구 환경")
    box(ax, 6, 35, 22, 26, "한국어 질의\nq", BLUE, "#F4F7FF")
    box(ax, 39, 35, 22, 26, "영어 학술·기술 문서\nD", GRAY)
    box(ax, 72, 35, 22, 26, "한국어 답변\ny", GREEN, "#F2FAF6")
    arrow(ax, (28, 48), (39, 48), DARK)
    arrow(ax, (61, 48), (72, 48), DARK)
    box(ax, 6, 76, 22, 11, "언어·표현 차이", BLUE, "white", 8)
    box(ax, 39, 76, 22, 11, "검색 근거의 생성 반영", GREEN, "white", 8)
    box(ax, 72, 76, 22, 11, "출력 언어 유지", ORANGE, "white", 8)
    arrow(ax, (17, 76), (17, 62), BLUE, 0.8)
    arrow(ax, (50, 76), (50, 62), GREEN, 0.8)
    arrow(ax, (83, 76), (83, 62), ORANGE, 0.8)
    text(
        ax,
        50,
        16,
        "고정 Paper-RAG backbone에서 HyDE, CAD, SCD를 독립 실험 요인으로 적용",
        8,
    )
    save(fig, "fig1_1_research_setting")

    fig, ax = diagram_canvas(8.2, 4.2)
    title(fig, "그림 3-1. RAG-Cube의 2×2×2 실험 조건")
    origin = np.array([42.0, 19.0])
    vectors = [np.array([35.0, 15.0]), np.array([-27.0, 20.0]), np.array([0.0, 42.0])]
    points = {
        bits: origin + sum((vectors[i] * bits[i] for i in range(3)), np.zeros(2))
        for bits in [(h, c, s) for h in range(2) for c in range(2) for s in range(2)]
    }
    for bits, point in points.items():
        for i in range(3):
            if bits[i] == 0:
                changed = list(bits)
                changed[i] = 1
                other = points[tuple(changed)]
                ax.plot(
                    [point[0], other[0]],
                    [point[1], other[1]],
                    color=GRAY,
                    lw=1.3,
                    zorder=1,
                )
    for vector, color, label, offset in zip(
        vectors,
        [BLUE, GREEN, ORANGE],
        ["HyDE", "CAD", "SCD"],
        [(5, -5), (-8, -4), (-7, 0)],
    ):
        arrow(ax, origin, origin + vector, color, 2)
        mid = origin + vector * 0.52
        text(ax, mid[0] + offset[0], mid[1] + offset[1], label, 9, color, "bold")
    for bits, point in points.items():
        ax.plot(*point, "o", color=DARK, ms=4, zorder=2)
        text(
            ax,
            point[0] + (4 if bits[0] else -4),
            point[1] + 4,
            f"H{bits[0]}C{bits[1]}S{bits[2]}",
            8,
            ha="left" if bits[0] else "right",
        )
    text(
        ax,
        50,
        7,
        "H = HyDE, C = CAD, S = SCD     0 = OFF, 1 = ON     60 질의 × 8 조건 = 480 생성",
        8,
    )
    save(fig, "fig3_1_rag_cube")

    fig, ax = diagram_canvas(10.0, 4.5)
    title(fig, "그림 4-1. Paper-RAG 실험 파이프라인")
    stages = [
        (4, "한국어 질의"),
        (20, "HyDE\n(선택)"),
        (36, "Hybrid retrieval\nBGE-M3 + BM25"),
        (54, "Weighted RRF\n+ reranking"),
        (72, "CAD\n(선택)"),
        (86, "SCD\n(선택)"),
    ]
    for x, label in stages:
        edge = (
            BLUE
            if "HyDE" in label
            else GREEN if "CAD" in label else ORANGE if "SCD" in label else GRAY
        )
        box(
            ax,
            x,
            43,
            11,
            22,
            label,
            edge,
            (
                "#F4F7FF"
                if edge == BLUE
                else (
                    "#F2FAF6"
                    if edge == GREEN
                    else "#FFF7F0" if edge == ORANGE else LIGHT
                )
            ),
            8,
        )
    for x in [15, 31, 49, 67, 81]:
        arrow(ax, (x, 54), (x + 5, 54), DARK)
    box(
        ax,
        39,
        15,
        22,
        14,
        "상위 5개 문맥 + Mi:dm 2.0\nDeterministic greedy answer",
        DARK,
        "white",
        8,
    )
    arrow(ax, (77, 43), (61, 29), DARK)
    text(
        ax,
        50,
        82,
        "고정 요소: retrieval pool 8, rerank top-N 8, context 5, max new tokens 512",
        8,
    )
    save(fig, "fig4_1_pipeline")


def quality_figures():
    configs = rows("rag_cube_config_scores_60q.csv")
    values = np.array(
        [
            [
                float(row[key])
                for key in [
                    "faithfulness_mean",
                    "answer_relevancy_mean",
                    "context_precision_mean",
                    "context_recall_mean",
                ]
            ]
            for row in configs
        ]
    )
    labels = [
        "H0 C0 S0",
        "H0 C1 S0",
        "H0 C0 S1",
        "H0 C1 S1",
        "H1 C0 S0",
        "H1 C1 S0",
        "H1 C0 S1",
        "H1 C1 S1",
    ]
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    image = ax.imshow(values, cmap="Blues", vmin=0.45, vmax=1.0, aspect="auto")
    ax.set_xticks(
        range(4),
        ["Faithfulness", "Answer\nrelevancy", "Context\nprecision", "Context\nrecall"],
    )
    ax.set_yticks(range(8), labels)
    for i in range(8):
        for j in range(4):
            ax.text(
                j,
                i,
                f"{values[i, j]:.3f}",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if values[i, j] < 0.68 else DARK,
            )
    bar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03)
    bar.set_label("평균 점수")
    fig.tight_layout()
    save(fig, "fig5_1_quality_matrix")

    data = [("HyDE", row) for row in rows("hyde_primary_60q.csv")] + [
        ("CAD", row) for row in rows("cad_primary_60q.csv")
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    y = np.arange(len(data))[::-1]
    colors = [BLUE] * 4 + [GREEN] * 4
    for ypos, (_, row), color in zip(y, data, colors):
        low, high = read_ci(row["bootstrap_mean_95_ci"])
        mean = float(row["mean_delta_on_minus_off"])
        ax.hlines(ypos, low, high, color=color, lw=2)
        ax.plot(mean, ypos, "o", color=color, ms=6)
        ax.text(
            0.17,
            ypos,
            f"{mean:+.4f} [{low:+.4f}, {high:+.4f}]",
            va="center",
            fontsize=8,
        )
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set(
        yticks=y,
        yticklabels=[
            f"{factor} · {row['metric']} (n={row['n_queries']})" for factor, row in data
        ],
        xlim=(-0.13, 0.28),
        xlabel="평균 대응 차이 (ON - OFF)",
    )
    fig.tight_layout()
    save(fig, "fig5_2_primary_forest")

    scd = rows("scd_language_summary_60q.csv")
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    x = np.arange(len(scd))
    delta = [float(row["mean_delta"]) for row in scd]
    lower = [float(row["mean_delta"]) - float(row["ci95_lower"]) for row in scd]
    upper = [float(row["ci95_upper"]) - float(row["mean_delta"]) for row in scd]
    ax.bar(x, delta, color=ORANGE, width=0.62)
    ax.errorbar(
        x, delta, yerr=[lower, upper], fmt="none", color=DARK, capsize=4, lw=1.2
    )
    ax.set_xticks(x, ["H0 C0", "H0 C1", "H1 C0", "H1 C1"])
    ax.set_ylim(0, 0.36)
    ax.set_ylabel("한국어 문자 비율 평균 변화 (SCD ON - OFF)")
    for xpos, value, row in zip(x, delta, scd):
        ax.text(
            xpos,
            value + 0.018,
            f"{value:+.4f}\nn={row['n_pairs']}",
            ha="center",
            fontsize=8,
        )
    ax.text(
        0.99,
        -0.2,
        "오차막대: query-clustered bootstrap 95% CI",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
    )
    fig.tight_layout()
    save(fig, "fig5_3_scd_language")


def evidence_panel(name, figure_title, case, left_label, right_label=None):
    fig, axes = plt.subplots(
        1, 2 if right_label else 1, figsize=(11.5 if right_label else 8.2, 6.2)
    )
    axes = np.atleast_1d(axes)
    panels = [(left_label, "answer_a_exact_excerpt", "score_a")]
    if right_label:
        panels.append((right_label, "answer_b_exact_excerpt", "score_b"))
    for ax, (label, answer_key, score_key) in zip(axes, panels):
        ax.axis("off")
        ax.set_title(
            label,
            loc="left",
            color=BLUE if answer_key.endswith("a_exact_excerpt") else ORANGE,
            fontweight="bold",
            fontsize=10,
        )
        answer = case.get(answer_key, "")
        wrapped = "\n".join(
            textwrap.fill(line, width=53 if right_label else 87, break_long_words=False)
            for line in answer.splitlines()
        )
        ax.text(
            0.01,
            0.95,
            wrapped,
            transform=ax.transAxes,
            va="top",
            fontsize=7.8,
            linespacing=1.45,
            clip_on=True,
        )
        score = case.get(score_key, {})
        if score:
            ax.text(
                0.01,
                0.02,
                " · ".join(
                    f"{key}={value}"
                    for key, value in score.items()
                    if key not in {"query_id", "group"}
                ),
                transform=ax.transAxes,
                fontsize=7.5,
                color=DARK,
            )
    fig.tight_layout()
    save(fig, name)


def evidence_figures():
    manifest = json.loads(
        (DATA / "evidence_manifest_60q.json").read_text(encoding="utf-8")
    )
    cases = {case["selection_rule"]: case for case in manifest["cases"]}
    evidence_panel(
        "fig5_4_normal_answer",
        "그림 5-4. 저장된 정상 응답 사례",
        cases["normal_qa"],
        "H0C0S0 저장 답변",
    )
    evidence_panel(
        "fig5_5_scd_language_pair",
        "그림 5-5. 동일 문맥 SCD ON/OFF 응답 사례",
        cases["language_rescue"],
        "SCD OFF",
        "SCD ON",
    )
    evidence_panel(
        "fig5_6_hyde_retrieval_pair",
        "그림 5-6. HyDE 조건의 검색 변화 응답 사례",
        cases["hyde_retrieval_change"],
        "HyDE OFF",
        "HyDE ON",
    )
    evidence_panel(
        "fig5_7_cad_pair",
        "그림 5-7. 동일 문맥 CAD ON/OFF 응답 사례",
        cases["cad_higher_faithfulness_delta"],
        "CAD OFF",
        "CAD ON",
    )


def supplementary_figures():
    """Additional data-backed panels; captions and numbering remain in the manuscript."""
    manifest = json.loads(
        (DATA / "evidence_manifest_60q.json").read_text(encoding="utf-8")
    )
    cases = {case["selection_rule"]: case for case in manifest["cases"]}
    evidence_panel(
        "fig1_2_language_drift_case_a",
        "",
        cases["language_rescue"],
        "SCD OFF 저장 답변",
    )
    evidence_panel(
        "fig1_3_language_drift_case_b",
        "",
        cases["language_rescue"],
        "SCD OFF",
        "SCD ON",
    )
    evidence_panel(
        "fig5_8_cad_lower_case",
        "",
        cases["cad_lower_faithfulness_delta"],
        "CAD OFF",
        "CAD ON",
    )

    fig, ax = diagram_canvas(9.0, 3.8)
    for x, label, edge, face in [
        (5, "generation\nrecord", BLUE, "#F4F7FF"),
        (28, "RAGAS·language\nanalysis", GREEN, "#F2FAF6"),
        (51, "derived CSV\nvalidation", GRAY, LIGHT),
        (74, "tables·figures\nmanuscript", ORANGE, "#FFF7F0"),
    ]:
        box(ax, x, 40, 16, 22, label, edge, face, 9)
    for x in (21, 44, 67):
        arrow(ax, (x, 51), (x + 7, 51), DARK)
    text(
        ax,
        50,
        21,
        "source artifact hash · query ID · configuration · stored answer provenance",
        8,
    )
    save(fig, "fig4_2_artifact_flow")

    fig, ax = diagram_canvas(9.0, 4.2)
    groups = [
        (8, "60 query-document\npairs", BLUE),
        (30, "8 configs\n480 records", GREEN),
        (52, "HyDE 60\nCAD 58/60", GRAY),
        (74, "SCD 240\nsame-context 120", ORANGE),
    ]
    for x, label, color in groups:
        box(ax, x, 40, 16, 22, label, color, "white", 9)
    for x in (24, 46, 68):
        arrow(ax, (x, 51), (x + 6, 51), DARK)
    text(
        ax,
        50,
        22,
        "quality: paired bootstrap 95% CI     language: Korean-character ratio",
        8,
    )
    save(fig, "fig5_0_evaluation_design")

    rows_h = rows("hyde_strata_deltas_60q.csv")
    rows_c = rows("cad_strata_deltas_60q.csv")
    selected = [
        r
        for r in [*rows_h, *rows_c]
        if r["metric"] in {"faithfulness", "answer_relevancy"}
    ]
    labels = [
        f"{r['factor']}\n{r['off_config'].replace('hyde_', 'H').replace('__', ' ')}"
        for r in selected
    ]
    values = np.array([float(r["mean_delta_on_minus_off"]) for r in selected])[:, None]
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    image = ax.imshow(values, cmap="RdBu", vmin=-0.16, vmax=0.16, aspect="auto")
    ax.set_xticks([0], ["평균 대응 차이\n(ON - OFF)"])
    ax.set_yticks(range(len(labels)), labels)
    for i, value in enumerate(values[:, 0]):
        ax.text(
            0,
            i,
            f"{value:+.4f}",
            ha="center",
            va="center",
            fontsize=8,
            color="white" if abs(value) > 0.09 else DARK,
        )
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03).set_label("평균 대응 차이")
    fig.tight_layout()
    save(fig, "fig5_9_hyde_cad_strata")

    runtime = rows("runtime_summary_60q.csv")
    labels = [
        r["config"]
        .replace("hyde_", "H")
        .replace("__", " ")
        .replace("no_decoder_control", "C0 S0")
        .replace("cad_only", "C1 S0")
        .replace("scd_only", "C0 S1")
        .replace("cad_scd", "C1 S1")
        .replace("off", "0")
        .replace("on", "1")
        for r in runtime
    ]
    values = [float(r["duration_mean_seconds"]) for r in runtime]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    colors = [
        GREEN if "cad" in r["config"] else BLUE if "hyde_on" in r["config"] else GRAY
        for r in runtime
    ]
    ax.bar(range(len(values)), values, color=colors, width=0.7)
    ax.set_xticks(range(len(values)), labels, rotation=30, ha="right")
    ax.set_ylabel("평균 generation time (seconds)")
    for i, value in enumerate(values):
        ax.text(i, value + 1.5, f"{value:.1f}", ha="center", fontsize=8)
    fig.tight_layout()
    save(fig, "fig5_10_runtime")


def main():
    architecture_figures()
    quality_figures()
    evidence_figures()
    supplementary_figures()
    expected = sorted(
        path.name for path in OUT.iterdir() if path.suffix in {".png", ".svg"}
    )
    if len(expected) != 34:
        raise RuntimeError(f"expected 34 visual files, got {len(expected)}")
    print(
        json.dumps({"out": str(OUT), "files": expected}, ensure_ascii=False, indent=2)
    )


if __name__ == "__main__":
    main()
