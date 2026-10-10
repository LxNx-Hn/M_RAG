"""Rebuild editorial figure labels; preserve source plots and experimental data."""

from __future__ import annotations

import importlib.util
import json
import shutil
import statistics
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "FINALDOCS/FIGURES"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    font = Path("C:/Windows/Fonts/malgun.ttf")
    if not font.exists():
        raise FileNotFoundError("Reviewed Korean figure font is missing")
    font_manager.fontManager.addfont(str(font))
    family = font_manager.FontProperties(fname=font).get_name()
    project = load_module(ROOT / "cli/finalize_thesis_figures.py", "project_figures")
    plt.rcParams["font.family"] = family
    # Render into a separate directory so unrelated metric plots keep their bytes.
    with tempfile.TemporaryDirectory(prefix="mrag_labels_") as temporary:
        project.FIG = Path(temporary)
        project.render_project_figures()
        for name in (
            "fig4_1_pipeline.png",
            "fig4_2_artifact_flow.png",
            "fig5_0_evaluation_design.png",
        ):
            shutil.copy2(project.FIG / name, FIG / name)
    literature = load_module(
        ROOT / "FINALDOCS/BUILD/build_submission_literature.py", "literature_figures"
    )
    literature.original_rag(font, FIG / "LITERATURE")

    fig, ax = plt.subplots(figsize=(21, 10), dpi=240)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    colors = ["#2f6df6", "#23866f", "#cc6400"]
    x_positions = [0.08, 0.40, 0.72]
    top = ["언어와 표현 차이", "검색 근거의 생성 반영", "출력 언어 유지"]
    bottom = ["한국어 질의\nq", "영어 학술 문서와\n기술 문서\nD", "한국어 답변\ny"]
    for x, color, label, value in zip(x_positions, colors, top, bottom):
        for y, h, text, face in (
            (0.75, 0.12, label, "white"),
            (0.35, 0.26, value, "#f7f9fc"),
        ):
            ax.add_patch(
                FancyBboxPatch(
                    (x, y),
                    0.20,
                    h,
                    boxstyle="round,pad=0.01",
                    edgecolor=color,
                    facecolor=face,
                    linewidth=2,
                )
            )
            ax.text(x + 0.10, y + h / 2, text, ha="center", va="center", fontsize=19)
        ax.add_patch(
            FancyArrowPatch(
                (x + 0.10, 0.74),
                (x + 0.10, 0.63),
                arrowstyle="-|>",
                mutation_scale=18,
                color=color,
            )
        )
    for x in (0.28, 0.60):
        ax.add_patch(
            FancyArrowPatch(
                (x, 0.48),
                (x + 0.12, 0.48),
                arrowstyle="-|>",
                mutation_scale=20,
                linewidth=2,
            )
        )
    ax.text(
        0.50,
        0.15,
        "고정 Paper-RAG 백본에서 HyDE, CAD, SCD를 독립 실험 요인으로 적용",
        ha="center",
        fontsize=17,
    )
    fig.savefig(
        FIG / "fig1_1_research_setting.png", bbox_inches="tight", pad_inches=0.15
    )
    plt.close(fig)

    manifest = json.loads(
        (ROOT / "FINALDOCS/DATA/evidence_manifest_60q.json").read_text("utf-8")
    )
    rows = []
    for name in list(manifest["sources"])[:2]:
        rows += [
            json.loads(line)
            for line in (ROOT / name).read_text("utf-8").splitlines()
            if line
        ]
    order = [
        "H0C0S0",
        "H0C1S0",
        "H0C0S1",
        "H0C1S1",
        "H1C0S0",
        "H1C1S0",
        "H1C0S1",
        "H1C1S1",
    ]
    means = [
        statistics.mean(
            row["duration_seconds"]
            for row in rows
            if f"H{int(row['use_hyde'])}C{int(row['use_cad'])}S{int(row['use_scd'])}"
            == name
        )
        for name in order
    ]
    assert [round(value, 3) for value in means] == [
        20.792,
        63.867,
        18.898,
        55.159,
        23.440,
        73.532,
        24.892,
        64.125,
    ]
    fig, ax = plt.subplots(figsize=(19.8, 10.3), dpi=240)
    bars = ax.bar(
        range(8),
        means,
        width=0.7,
        color=[
            "#aab2bc",
            "#23866f",
            "#aab2bc",
            "#23866f",
            "#2f6df6",
            "#23866f",
            "#2f6df6",
            "#23866f",
        ],
    )
    ax.bar_label(
        bars, labels=[f"{value:.1f}" for value in means], padding=5, fontsize=18
    )
    ax.set_xticks(
        range(8),
        [f"{name[:2]} {name[2:4]} {name[4:]}" for name in order],
        rotation=30,
        ha="right",
        fontsize=18,
    )
    ax.set_ylabel("평균 조건 실행 시간(초)", fontsize=20)
    ax.tick_params(axis="y", labelsize=18)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig5_10_runtime.png", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(
        "Rebuilt six editorial diagrams/plots; runtime values recomputed from 480 source records"
    )


if __name__ == "__main__":
    main()
