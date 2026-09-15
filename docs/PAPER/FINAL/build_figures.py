"""Build the seven thesis figures from retained evidence; no model calls."""

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
OUT = BASE / "figures"
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
        "svg.hashsalt": "mrag-final-figures",
        "savefig.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.7,
    }
)
BLUE, GREEN, ORANGE = "#2F6BFF", "#25836A", "#C66A20"
GRAY, LIGHT, DARK = "#A8B0B8", "#F5F7FA", "#222222"
spec = importlib.util.spec_from_file_location(
    "evidence", ROOT / "docs/PAPER/scripts/verify_current_thesis_results.py"
)
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)
ev.verify_quality_contrasts()
sources = [ev.GENERATION_PATH, ev.SCORE_PATH]
checks = {}


def save(fig, name):
    for label in fig.findobj(matplotlib.text.Text):
        label.set_text(label.get_text().replace("\u2212", "-"))
    svg_path = OUT / f"{name}.svg"
    fig.savefig(svg_path, metadata={"Date": None})
    svg_path.write_text(
        "\n".join(
            line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()
        )
        + "\n",
        encoding="utf-8",
    )
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)


def canvas(w=7.1, h=3.5):
    f, a = plt.subplots(figsize=(w, h))
    f.subplots_adjust(0, 0, 1, 1)
    a.set(xlim=(0, 100), ylim=(0, 100))
    a.axis("off")
    return f, a


def txt(a, x, y, s, size=9, color=DARK, weight="normal", ha="center"):
    return a.text(
        x,
        y,
        s,
        fontsize=size,
        color=color,
        weight=weight,
        ha=ha,
        va="center",
        linespacing=1.55,
    )


def box(a, x, y, w, h, s, color=GRAY, fill=LIGHT, size=9):
    a.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0,rounding_size=1.5",
            linewidth=1.2,
            edgecolor=color,
            facecolor=fill,
        )
    )
    txt(a, x + w / 2, y + h / 2, s, size)


def arrow(a, p, q, color=GRAY, style="-", width=1.3):
    a.add_patch(
        FancyArrowPatch(
            p,
            q,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=width,
            color=color,
            linestyle=style,
            shrinkA=0,
            shrinkB=0,
        )
    )


def head(a, n, title):
    txt(a, 5, 94, f"{n:02d}  {title}", 11, weight="bold", ha="left")


def diagrams():
    f, a = canvas(7.1, 3)
    head(a, 1, "Research Setting")
    for x, label in [
        (5, "한국어 질의"),
        (38, "영어 학술·기술 문서"),
        (71, "답변\n목표 언어: 한국어"),
    ]:
        box(a, x, 32, 24, 25, label)
    arrow(a, (29, 44.5), (38, 44.5), DARK)
    arrow(a, (62, 44.5), (71, 44.5), DARK)
    for x, target, label in [
        (30, 33.5, "언어·표현 차이"),
        (57, 66.5, "근거 반영"),
        (83, 83, "언어 이탈"),
    ]:
        box(a, x - 11, 69, 22, 11, label, BLUE, "white", 8)
        arrow(a, (x, 69), (target, 59), BLUE, width=0.8)
    txt(a, 50, 14, "질의와 근거 문서의 언어, 근거 활용, 답변의 출력 언어", 8)
    save(f, "fig01_research_setting")

    f, a = canvas(5.9, 4.6)
    head(a, 2, "RAG-Cube")
    # Oblique isometric-style projection keeps all eight vertices distinct.
    origin = np.array([48.0, 22.0])
    vectors = [np.array([32.0, 14.0]), np.array([-25.0, 19.0]), np.array([0.0, 35.0])]
    pts = {
        bits: origin + sum((vectors[i] * bits[i] for i in range(3)), np.zeros(2))
        for bits in itertools.product([0, 1], repeat=3)
    }
    for b, p in pts.items():
        for i in range(3):
            if b[i] == 0:
                c = list(b)
                c[i] = 1
                q = pts[tuple(c)]
                a.plot([p[0], q[0]], [p[1], q[1]], color=GRAY, lw=1.2, zorder=1)
    for i, (color, marker, label) in enumerate(
        zip([BLUE, GREEN, ORANGE], ["o", "s", "^"], ["HyDE", "CAD", "SCD"])
    ):
        q = origin + vectors[i]
        arrow(a, origin, q, color, width=2)
        mid = origin + vectors[i] * 0.53
        shifts = [(7, -5), (-8, -4), (-7, 0)]
        txt(a, mid[0] + shifts[i][0], mid[1] + shifts[i][1], label, 9, color, "bold")
    for b, p in pts.items():
        a.plot(*p, "o", ms=4, color=DARK, zorder=3)
        dx = 3 if b[0] else -3
        label = txt(
            a,
            p[0] + dx,
            p[1] + 3,
            f"H{b[0]}C{b[1]}S{b[2]}",
            8,
            ha="left" if dx > 0 else "right",
        )
        label.set_bbox({"facecolor": "white", "edgecolor": "none", "pad": 1})
    txt(a, 50, 9, "H = HyDE    C = CAD    S = SCD      0 = OFF · 1 = ON", 8)
    save(f, "fig02_rag_cube")

    f, a = canvas(8.4, 4.1)
    head(a, 3, "Experimental Pipeline")
    txt(a, 50, 83, "고정 Paper-RAG backbone · 질의별 지정 문서에서 검색", 9)
    for x, w, label in [
        (3, 67, "RETRIEVAL"),
        (73, 11, "GENERATION"),
        (87, 11, "EVALUATION"),
    ]:
        a.plot([x, x + w], [74, 74], color=GRAY, lw=1)
        txt(a, x + w / 2, 78, label, 8, weight="bold")
    box(a, 2, 42, 11, 17, "한국어\n질의", size=8)
    box(a, 16, 54, 12, 14, "HyDE\nOFF / ON", BLUE, size=8)
    box(a, 31, 55, 11, 13, "BGE-M3", size=8)
    box(a, 31, 33, 11, 13, "BM25", size=8)
    box(a, 45, 42, 10, 17, "weighted\nRRF", size=8)
    box(a, 58, 42, 12, 17, "CrossEncoder\n문맥 구성", size=8)
    box(a, 73, 42, 11, 17, "Mi:dm\n토큰 생성", size=8)
    box(a, 87, 42, 11, 17, "답변\n평가", size=8)
    arrow(a, (13, 53), (16, 60))
    arrow(a, (28, 61), (31, 61))
    arrow(a, (13, 46), (31, 39))
    txt(a, 22, 35, "원질의", 8)
    arrow(a, (42, 61), (45, 54))
    arrow(a, (42, 39), (45, 47))
    arrow(a, (55, 50), (58, 50))
    arrow(a, (70, 50), (73, 50))
    arrow(a, (84, 50), (87, 50))
    txt(a, 71.5, 64, "영어 근거", 8)
    box(a, 67, 13, 12, 14, "CAD\nOFF / ON", GREEN, size=8)
    box(a, 82, 13, 12, 14, "SCD\nOFF / ON", ORANGE, size=8)
    arrow(a, (79, 20), (82, 20), DARK)
    arrow(a, (88, 27), (81, 42), ORANGE)
    arrow(a, (77, 42), (73, 27), GREEN)
    txt(a, 81, 6, "토큰마다 적용", 8)
    txt(a, 47, 18, "문맥: 순서 재배치 → 5개 선택\n추출형 압축 · 길이 제한", 8)
    txt(a, 22, 17, "HyDE ON: 영어 번역 · 가상 문서\nHyDE OFF: 원질의 dense 검색", 8)
    save(f, "fig03_experimental_pipeline")

    f, a = canvas(7.1, 4.7)
    head(a, 4, "Evaluation Design")
    cards = [
        (4, 49, "HyDE", BLUE, "19", "H0 ↔ H1", "C0 · S0", "4 RAGAS metrics"),
        (
            52,
            49,
            "CAD",
            GREEN,
            "19",
            "C0 ↔ C1",
            "H0 · S0 · 동일 문맥",
            "4 RAGAS metrics",
        ),
        (
            4,
            6,
            "SCD · Language",
            ORANGE,
            "76",
            "S0 ↔ S1",
            "동일 질의 · H · C",
            "한국어 문자 비율 · 언어 이탈",
        ),
        (
            52,
            6,
            "Symmetric Evaluation",
            ORANGE,
            "38",
            "S0 ↔ S1",
            "H0 · 동일 문맥",
            "Faithfulness · Answer relevancy",
        ),
    ]
    for x, y, title, color, n, compare, fixed, metrics in cards:
        box(a, x, y, 44, 36, "", color, "white")
        txt(a, x + 3, y + 30, title, 10, color, "bold", ha="left")
        txt(a, x + 36, y + 28, n, 17, color, "bold")
        txt(a, x + 36, y + 21, "pairs", 8)
        txt(a, x + 3, y + 21, compare, 9, ha="left")
        txt(a, x + 3, y + 13, fixed, 8, ha="left")
        txt(a, x + 3, y + 5, metrics, 8, ha="left")
    save(f, "fig04_evaluation_design")


def forest(name, num, title, sections, labels, xlim, foot):
    f = plt.figure(figsize=(8.4, 5.2))
    f.text(0.025, 0.95, f"{num:02d}  {title}", size=11, weight="bold")
    for k, (section, data, color, marker) in enumerate(sections):
        y0 = 0.56 if k == 0 else 0.17
        a = f.add_axes([0.31, y0, 0.29, 0.27])
        a.set_xlim(*xlim)
        a.set_ylim(-0.6, 3.6)
        a.axvline(0, color="#666666", ls="--", lw=1)
        a.set_yticks(range(4), labels[::-1], fontsize=8)
        a.tick_params(axis="y", length=0, pad=10)
        a.spines["left"].set_visible(False)
        a.set_xticks(
            [-0.2, -0.1, 0, 0.1, 0.2] if xlim[1] > 0.15 else [-0.2, -0.1, 0, 0.1]
        )
        a.tick_params(axis="x", labelsize=8)
        f.text(0.025, y0 + 0.3, section, size=10, color=color, weight="bold")
        f.text(0.64, y0 + 0.3, "Mean Δ [95% CI]", size=8, weight="bold")
        for j, (m, lo, hi) in enumerate(data):
            y = 3 - j
            a.errorbar(
                m,
                y,
                xerr=[[m - lo], [hi - m]],
                fmt=marker,
                color=color,
                capsize=3,
                ms=5,
                lw=1.4,
            )
            a.text(
                1.13,
                y,
                f"{m:+.4f} [{lo:+.4f}, {hi:+.4f}]",
                transform=a.get_yaxis_transform(),
                fontsize=8,
                va="center",
            )
        if k == 1:
            a.set_xlabel("Mean difference (ON − OFF)", fontsize=8)
    f.text(0.025, 0.025, foot, size=8)
    save(f, name)


def plots():
    data = []
    for c in ev.CONTRASTS:
        data.append([ev.EXPECTED[c][metric][:3] for metric in ev.METRICS])
    forest(
        "fig05_hyde_cad_contrasts",
        5,
        "HyDE / CAD Quality Contrasts",
        [
            ("HyDE · C0 / S0 · 19 pairs", data[0], BLUE, "o"),
            ("CAD · H0 / S0 · identical context · 19 pairs", data[1], GREEN, "s"),
        ],
        ["Faithfulness", "Answer relevancy", "Context precision", "Context recall"],
        (-0.21, 0.21),
        "Paired percentile bootstrap · 200,000 resamples · 19 query units · gpt-4o",
    )
    rows = ev.read_jsonl(ev.GENERATION_PATH)
    assert len(rows) == 152
    index = {(r["query_id"], r["config_name"]): r for r in rows}

    def ratio(t):
        h = sum(
            0xAC00 <= ord(c) <= 0xD7A3
            or 0x1100 <= ord(c) <= 0x11FF
            or 0x3130 <= ord(c) <= 0x318F
            for c in t
        )
        e = sum(c.isascii() and c.isalpha() for c in t)
        if h + e == 0:
            # Preserve the existing final verifier convention explicitly.
            checks.setdefault("zero_denominator_answers", []).append(
                {
                    "text_sha256": hashlib.sha256(t.encode()).hexdigest(),
                    "rule": "existing verifier korean_ratio",
                    "value": ev.korean_ratio(t),
                }
            )
            return ev.korean_ratio(t)
        return round(h / (h + e), 4)

    pairs = []
    records = []
    for q in sorted({r["query_id"] for r in rows}):
        for h, c in itertools.product([0, 1], repeat=2):
            prefix = "hyde_on__" if h else "hyde_off__"
            off = prefix + ("cad_only" if c else "no_decoder_control")
            on = prefix + ("cad_scd" if c else "scd_only")
            p = [ratio(index[(q, n)]["generated_answer"]) for n in [off, on]]
            pairs.append(p)
            records.append(
                {"query_id": q, "hyde": h, "cad": c, "off": p[0], "on": p[1]}
            )
    p = np.array(pairs)
    d = p[:, 1] - p[:, 0]
    drift = (p < 0.5).sum(axis=0)
    assert len(p) == 76 and list(drift) == [26, 12]
    assert round(float(d.mean()), 4) == 0.2203
    assert (int((d > 0.02).sum()), int((d < -0.02).sum())) == (68, 3)
    f = plt.figure(figsize=(7.1, 4.6))
    f.text(0.04, 0.94, "06  SCD Language Adherence", size=11, weight="bold")
    a = f.add_axes([0.12, 0.17, 0.47, 0.65])
    b = f.add_axes([0.72, 0.25, 0.23, 0.40])
    for x in p:
        a.plot([0, 1], x, color=GRAY, alpha=0.42, lw=0.65)
    means = p.mean(axis=0)
    a.plot([0, 1], means, color=ORANGE, marker="^", ms=8, lw=2.4, label="Mean")
    a.axhline(0.5, color=DARK, ls="--", lw=1)
    a.text(0.5, 0.515, "Drift threshold = 0.5", ha="center", size=8)
    a.set(
        xlim=(-0.2, 1.2),
        ylim=(0, 1.04),
        xticks=[0, 1],
        xticklabels=["SCD OFF", "SCD ON"],
        ylabel="Korean-character ratio",
    )
    for i, m in enumerate(means):
        a.annotate(
            f"{m:.4f}",
            (i, m),
            xytext=(-4, -19 if i == 0 else 12),
            textcoords="offset points",
            color=ORANGE,
            weight="bold",
        )
    a.legend(loc="upper left", frameon=False, fontsize=8)
    b.bar([0, 1], drift, color=[LIGHT, ORANGE], edgecolor=[GRAY, ORANGE], width=0.55)
    b.set(
        xticks=[0, 1],
        xticklabels=["OFF", "ON"],
        ylim=(0, 32),
        yticks=[0, 10, 20, 30],
        title="Language drift",
    )
    for i, v in enumerate(drift):
        b.text(i, v + 1, str(v), ha="center", size=11, weight="bold")
    f.text(0.72, 0.73, "26 → 12", size=19, color=ORANGE, weight="bold")
    f.text(
        0.04,
        0.055,
        "76 matched pairs · mean Δ +0.2203 · 68 increases / 3 decreases / 5 ties (±0.02)",
        size=8,
    )
    save(f, "fig06_scd_language_adherence")
    checks["scd"] = {
        "pairs": 76,
        "mean_delta": float(d.mean()),
        "drift": drift.tolist(),
        "pairs_data": records,
    }
    panels = []
    for name in [
        "reference_scd_symmetric_gpt4o.json",
        "reference_scd_symmetric_gpt41_2025_04_14.json",
    ]:
        path = ROOT / "experiments/results/analysis" / name
        sources.append(path)
        obj = json.loads(path.read_text(encoding="utf-8"))
        for lang in ["english_normalized", "korean_normalized"]:
            panels.append(obj["panels"][lang]["paired_results"]["overall"])
    sections = []
    for metric, marker in [("faithfulness", "o"), ("answer_relevancy", "^")]:
        values = [
            (
                p[metric]["mean_delta"],
                p[metric]["bootstrap_mean_95_ci"]["lower"],
                p[metric]["bootstrap_mean_95_ci"]["upper"],
            )
            for p in panels
        ]
        sections.append((metric.replace("_", " ").title(), values, ORANGE, marker))
    forest(
        "fig07_symmetric_quality",
        7,
        "Symmetric SCD Quality Evaluation",
        sections,
        [
            "gpt-4o / English",
            "gpt-4o / Korean",
            "gpt-4.1* / English",
            "gpt-4.1* / Korean",
        ],
        (-0.21, 0.12),
        "* gpt-4.1-2025-04-14 · 38 pairs / panel · 19 query clusters · 10,000 bootstrap resamples",
    )


def style():
    f, a = canvas(7.1, 4.7)
    head(a, 0, "Figure Style Guide")
    txt(a, 6, 80, "FONT  Malgun Gothic · 맑은 고딕", 10, ha="left")
    txt(a, 6, 71, "제목 11 pt · 본문 9 pt · 주석 8 pt · Regular / Bold", 9, ha="left")
    for x, color, marker, label in [
        (15, BLUE, "o", "HyDE"),
        (48, GREEN, "s", "CAD"),
        (81, ORANGE, "^", "SCD"),
    ]:
        a.plot(x, 55, marker, color=color, ms=9)
        txt(a, x, 43, label, 10, color, "bold")
        txt(a, x, 34, color, 8)
    box(a, 6, 10, 26, 14, "Box · #F5F7FA")
    arrow(a, (39, 17), (57, 17), DARK)
    txt(a, 77, 17, "1.2–1.5 pt · 흰 배경\nSVG + 300 dpi PNG", 8)
    save(f, "style_guide")


if __name__ == "__main__":
    style()
    diagrams()
    plots()
    checks["sources"] = [
        {
            "path": str(p.relative_to(ROOT)),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in sources
    ]
    (OUT / "evidence_manifest.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("PASS: 7 figures + style guide; SVG/PNG; evidence manifest")
