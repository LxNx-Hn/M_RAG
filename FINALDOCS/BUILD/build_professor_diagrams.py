"""Render editable, independently drawn technical diagrams at print-readable size."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "FINALDOCS/FIGURES"
INK = "#24324A"
BLUE = "#2F6DF6"
GREEN = "#16846F"
ORANGE = "#CF6800"
PURPLE = "#695184"


class Drawing:
    def __init__(self, width=1800, height=900):
        self.width, self.height = width, height
        self.parts = []

    def text(self, x, y, value, size=44, center=True):
        anchor = "middle" if center else "start"
        for i, line in enumerate(value.split("\n")):
            self.parts.append(
                f'<text x="{x}" y="{y+i*size*1.35}" font-family="Malgun Gothic" font-size="{size}" text-anchor="{anchor}" fill="{INK}">{html.escape(line)}</text>'
            )

    def box(self, x, y, w, h, label, color=PURPLE, size=44):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#FAF9FC" stroke="{color}" stroke-width="4"/>'
        )
        lines = label.count("\n") + 1
        self.text(
            x + w / 2, y + h / 2 - (lines - 1) * size * 0.675 + size * 0.35, label, size
        )

    def arrow(self, points, color=INK):
        self.parts.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="4" marker-end="url(#arrow)"/>'
        )

    def svg(self):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="159mm" height="{159*self.height/self.width}mm" viewBox="0 0 {self.width} {self.height}"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="{INK}"/></marker></defs><rect width="100%" height="100%" fill="white"/>{"".join(self.parts)}</svg>'


def main():
    global FIG
    parser = argparse.ArgumentParser(description=__doc__)
    renderer = parser.add_mutually_exclusive_group(required=True)
    renderer.add_argument("--inkscape", type=Path)
    renderer.add_argument("--chrome", type=Path, help="headless Chrome/Edge executable")
    parser.add_argument(
        "--poster-svg",
        type=Path,
        default=ROOT / "FINALDOCS/POSTER/FINAL/M_RAG_A1_FINAL_EDITABLE.svg",
    )
    parser.add_argument("--output", type=Path, default=ROOT / "tmp/finaldocs/figures")
    args = parser.parse_args()
    FIG = args.output
    (FIG / "LITERATURE").mkdir(parents=True, exist_ok=True)
    drawings = {}
    # Figure 1-1 shows where each technique switches on; Figure 4-1 keeps the
    # model names and parameters of the implemented pipeline.
    d = Drawing(1800, 650)
    # Printed at 150 mm wide: 40 units = 9.5 pt, close to the 10 pt table titles.
    for y, w, h, label in [(10, 1760, 330, "검색 단계"), (355, 1250, 285, "생성 단계")]:
        d.parts.append(
            f'<rect x="20" y="{y}" width="{w}" height="{h}" rx="16" fill="#F5F6FA" stroke="none"/>'
        )
        d.text(44, y + 44, label, 38, center=False)
    d.box(40, 120, 300, 160, "한국어 질의\n60개", BLUE, 42)
    d.box(410, 62, 620, 130, "HyDE 적용 시\n영어 번역 후 가상 문서 생성", ORANGE, 40)
    d.text(720, 236, "미적용 시 원래 질의를 그대로 사용", 36)
    d.box(1080, 62, 280, 130, "밀집 검색", PURPLE, 42)
    d.box(1080, 205, 280, 130, "BM25 검색\n한국어 질의", PURPLE, 40)
    d.box(1440, 105, 330, 185, "융합과 재정렬\n상위 5개 구간", PURPLE, 42)
    d.arrow("340,200 380,200 380,127 395,127")
    d.arrow("1030,127 1065,127")
    d.arrow("380,200 380,270 1065,270")
    d.arrow("1360,127 1400,127 1400,172 1425,172")
    d.arrow("1360,270 1400,270 1400,225 1425,225")
    d.parts.append(
        f'<rect x="40" y="410" width="1205" height="220" rx="12" fill="#FFFFFF" stroke="{GREEN}" stroke-width="4"/>'
    )
    d.text(642, 455, "Mi:dm 2.0 답변 생성 (토큰마다 로짓 처리)", 38)
    d.box(70, 470, 540, 152, "CAD 적용 시\n문맥 포함 로짓과\n제외 로짓의 결합", ORANGE, 36)
    d.box(680, 470, 540, 152, "SCD 적용 시\n언어별 로짓 조정", ORANGE, 40)
    d.arrow("610,545 665,545")
    d.arrow("1605,290 1605,345 642,345 642,395")
    d.box(1325, 400, 445, 240, "평가\n검색과 생성 품질(RAGAS)\n한국어 문자 비율\n처리 시간", GREEN, 38)
    d.arrow("1245,520 1310,520")
    drawings[FIG / "fig1_1_research_setting.svg"] = d.svg()
    d = Drawing(1800, 650)
    d.box(40, 180, 400, 180, "질문 q\n외부 문서 집합 D", BLUE)
    d.box(680, 180, 430, 180, "검색기\n관련 문서 구간 선택", PURPLE)
    d.box(1350, 180, 400, 180, "생성 모델\n질문 + 검색 텍스트", GREEN)
    d.arrow("450,270 660,270")
    d.arrow("1120,270 1330,270")
    d.text(900, 95, "RAG는 외부 자료의 검색 결과를 답변 생성에 활용")
    d.text(900, 485, "검색 결과 = 생성 모델에 입력하는 문서 구간의 텍스트")
    d.text(900, 565, "출력은 질문에 대한 생성 답변 y")
    drawings[FIG / "LITERATURE/fig2_1_rag_independent.svg"] = d.svg()
    d = Drawing(1800, 730)
    d.text(900, 80, "HyDE의 가상 문서 기반 검색")
    for x, label, color in [
        (35, "입력 질의", BLUE),
        (485, "언어 모델\n가상 문서 생성", BLUE),
        (935, "가상 문서\n임베딩 벡터", PURPLE),
        (1385, "실제 문서 집합\n유사 구간 검색", GREEN),
    ]:
        d.box(x, 200, 380, 180, label, color, 42)
    for x in [425, 875, 1325]:
        d.arrow(f"{x},290 {x+45},290")
    d.text(900, 505, "본 실험은 영어로 번역한 질의로 가상 문서를 생성해 BGE-M3로 검색", 42)
    d.text(900, 585, "BM25 검색과 CrossEncoder 재정렬에는 한국어 원래 질의 사용", 42)
    drawings[FIG / "LITERATURE/fig2_2_hyde_independent.svg"] = d.svg()
    d = Drawing(1800, 850)
    d.text(900, 75, "CAD는 문맥 포함 입력과 제외 입력의 로짓을 결합")
    d.box(
        70,
        150,
        650,
        200,
        "질문 + 검색 결과\n+ 생성 접두 시퀀스\n문맥 포함 로짓 z_ctx",
        GREEN,
        40,
    )
    d.box(
        70, 410, 650, 200, "질문 + 생성 접두 시퀀스\n문맥 제외 로짓 z_noctx", PURPLE, 40
    )
    d.box(
        1000,
        270,
        720,
        190,
        "z_CAD = (1+α) z_ctx − α z_noctx\n본 실험의 α=0.5",
        GREEN,
        40,
    )
    d.arrow("735,245 890,245 890,330 980,330")
    d.arrow("735,485 890,485 890,410 980,410")
    d.text(900, 700, "CAD 적용 시 각 토큰의 최종 점수에 검색 결과의 영향을 반영", 42)
    drawings[FIG / "LITERATURE/fig2_3_cad_independent.svg"] = d.svg()
    d = Drawing(1800, 900)
    d.text(900, 80, "SCD는 토큰 그룹별로 로짓에 계수를 곱함")
    for x, label, color in [
        (40, "한국어 목표 토큰\nz′ = 1.1 × z", BLUE),
        (655, "비목표 언어 토큰\nz′ = 0.9 × z", ORANGE),
        (1270, "중립 토큰\nz′ = z", PURPLE),
    ]:
        d.box(x, 210, 490, 190, label, color, 42)
    d.text(900, 535, "이미 생성한 토큰 5개부터 적용, 그 이전에는 기본 로짓 유지", 42)
    d.text(900, 635, "CAD와 함께 적용하면 CAD 로짓 결합 뒤에 SCD 계수 적용", 42)
    d.text(900, 755, "출력 언어는 한글 / (한글 + ASCII 영문자)로 측정", 44)
    drawings[FIG / "LITERATURE/fig2_4_scd_independent.svg"] = d.svg()
    # Pipeline figure 4-1 is a standalone SVG source.
    # Analysis/plot_questions.py owns evaluation figure 5-1.
    for target, svg in drawings.items():
        target.write_text(svg, encoding="utf-8")
        if args.inkscape:
            command = [
                str(args.inkscape),
                str(target),
                "--export-type=png",
                "--export-width=2400",
                "--export-filename=" + str(target.with_suffix(".png")),
            ]
        else:
            width, height = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())
            page = target.with_suffix(".render.html")
            page.write_text(
                f'<html><body style="margin:0"><img src="{target.name}" '
                f'style="display:block;width:{width}px;height:{height}px"></body></html>',
                encoding="utf-8",
            )
            command = [
                str(args.chrome),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--force-device-scale-factor={2400 / width}",
                f"--window-size={width},{height}",
                "--user-data-dir=" + str((target.parent / ".chrome-render").resolve()),
                "--screenshot=" + str(target.with_suffix(".png").resolve()),
                page.resolve().as_uri(),
            ]
        subprocess.run(command, check=True, capture_output=True)
        if not args.inkscape:
            page.unlink()
    source_info = [
        (
            "2-1",
            "fig2_1_rag_independent",
            "Lewis",
            1,
            "RAG 구조",
            "https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf",
        ),
        (
            "2-2",
            "fig2_2_hyde_independent",
            "Gao",
            2,
            "HyDE 구조",
            "https://aclanthology.org/2023.acl-long.99/",
        ),
        (
            "2-3",
            "fig2_3_cad_independent",
            "Shi",
            3,
            "CAD 로짓 결합",
            "https://aclanthology.org/2024.naacl-short.69/",
        ),
        (
            "2-4",
            "fig2_4_scd_independent",
            "Li",
            4,
            "SCD 토큰별 점수 조정",
            "https://ojs.aaai.org/index.php/AAAI/article/view/40417",
        ),
    ]
    records = []
    for n, stem, author, ref, concept, url in source_info:
        png = FIG / "LITERATURE" / f"{stem}.png"
        titles = {
            "2-1": "RAG의 검색기와 생성기 구조",
            "2-2": "HyDE의 가상 문서 기반 검색 구조",
            "2-3": "CAD의 문맥 포함 로짓과 제외 로짓의 결합",
            "2-4": "SCD의 토큰 그룹별 로짓 조정",
        }
        caption = f"{titles[n]}[{ref}]"
        usage = f"그림 {n} — {author} 외[{ref}]의 {concept}"
        records.append(
            {
                "figure": n,
                "file": png.name,
                "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
                "status": "INDEPENDENT_DIAGRAM",
                "creator": "본 연구",
                "reference": ref,
                "caption_source": caption,
                "usage_entry": usage,
                "submission_source_url": url,
                "source_version": "Original research concept; independently drawn 2026-10-15",
                "uses_source_art": False,
            }
        )
    (FIG / "LITERATURE/SUBMISSION_PROVENANCE.json").write_text(
        json.dumps(
            {
                "review_date": "2026-10-15",
                "figures": records,
                "retained_legacy": "Previous source-art crops are recoverable from Git tag pre-finaldocs-cleanup-20261018; not embedded in current manuscript.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"PASS: {len(drawings)} editable SVG diagrams and print PNGs; 4 independently drawn literature concepts"
    )


if __name__ == "__main__":
    main()
