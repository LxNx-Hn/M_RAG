"""Render editable, independently drawn technical diagrams at print-readable size."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
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
    parser.add_argument("--inkscape", type=Path, required=True)
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
    d = Drawing(1800, 630)
    d.text(900, 74, "한국어 질의로 영어 자료를 이용하는 질의응답")
    for x, label, color in [
        (35, "한국어 질의\n질문 60개", BLUE),
        (665, "영어 학술·기술 문서\n4종에서 근거 검색", PURPLE),
        (1295, "생성 답변\n품질·출력 언어 평가", GREEN),
    ]:
        d.box(x, 200, 470, 195, label, color, 42)
    d.arrow("515,295 645,295")
    d.arrow("1145,295 1275,295")
    d.text(900, 505, "HyDE: 검색 표현   CAD: 근거 활용   SCD: 출력 언어", 42)
    drawings[FIG / "fig1_1_research_setting.svg"] = d.svg()
    d = Drawing(1800, 650)
    d.box(40, 180, 400, 180, "질문 q\n외부 문서 집합 D", BLUE)
    d.box(680, 180, 430, 180, "검색기\n관련 문서 구간 선택", PURPLE)
    d.box(1350, 180, 400, 180, "생성 모델\n질문 + 검색 텍스트", GREEN)
    d.arrow("450,270 660,270")
    d.arrow("1120,270 1330,270")
    d.text(900, 95, "RAG: 외부 자료의 검색 결과를 답변 생성에 활용")
    d.text(900, 485, "검색 문맥 = 생성 모델에 제공하는 검색 결과의 텍스트")
    d.text(900, 565, "출력: 질문에 대한 생성 답변 y")
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
    d.text(900, 505, "본 실험: 한국어 질의 → 영어 번역 → 가상 문서 → BGE-M3", 42)
    d.text(900, 585, "BM25 검색과 CrossEncoder 재정렬에는 한국어 원질의 사용", 42)
    drawings[FIG / "LITERATURE/fig2_2_hyde_independent.svg"] = d.svg()
    d = Drawing(1800, 850)
    d.text(900, 75, "CAD: 문맥 포함·제외 입력에서 계산한 로짓의 결합")
    d.box(
        70,
        150,
        650,
        200,
        "질문 + 검색 문맥\n+ 생성 접두 시퀀스\n문맥 포함 로짓 z_ctx",
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
        "z_CAD = (1+α) z_ctx − α z_noctx\n본 실험: α=0.5",
        GREEN,
        40,
    )
    d.arrow("735,245 890,245 890,330 980,330")
    d.arrow("735,485 890,485 890,410 980,410")
    d.text(900, 700, "CAD 적용 시 각 토큰의 최종 점수에 검색 문맥의 영향을 반영", 42)
    drawings[FIG / "LITERATURE/fig2_3_cad_independent.svg"] = d.svg()
    d = Drawing(1800, 900)
    d.text(900, 80, "SCD: 토큰 그룹별 로짓 계수 적용")
    for x, label, color in [
        (40, "한국어 목표 토큰\nz′ = 1.1 × z", BLUE),
        (655, "비목표 언어 토큰\nz′ = 0.9 × z", ORANGE),
        (1270, "중립 토큰\nz′ = z", PURPLE),
    ]:
        d.box(x, 210, 490, 190, label, color, 42)
    d.text(900, 535, "이미 생성한 토큰 5개부터 적용, 그 이전에는 기본 로짓 유지", 42)
    d.text(900, 635, "CAD와 함께 적용할 때: CAD 로짓 결합 후 SCD 계수 적용", 42)
    d.text(900, 755, "출력 특성의 측정: 한글 / (한글 + ASCII 영문자)", 44)
    drawings[FIG / "LITERATURE/fig2_4_scd_independent.svg"] = d.svg()
    d = Drawing(1800, 1040)
    d.text(900, 75, "질의 60개를 같은 8조건에서 반복측정")
    for x, label in [
        (30, "한국어 질의\n60개"),
        (650, "H·C·S 적용 조합\n8조건"),
        (1270, "저장 생성 기록\n480개"),
    ]:
        d.box(x, 140, 490, 150, label, size=44)
    d.arrow("535,215 625,215")
    d.arrow("1155,215 1245,215")
    d.box(
        80,
        405,
        740,
        190,
        "RAGAS 품질 지표\nS0 영어 / S1 한국어 번역 검색 결과",
        PURPLE,
        42,
    )
    d.box(
        980,
        405,
        740,
        190,
        "한국어 문자 비율·조건 실행 시간\n생성 답변과 실행 로그에서 계산",
        GREEN,
        42,
    )
    d.arrow("1515,300 1515,340 450,340 450,390")
    d.arrow("1515,340 1350,340 1350,390")
    d.box(
        80,
        700,
        740,
        155,
        "S0·S1별 H×C 반복측정 ANOVA\n충실도 n=58/57, 다른 지표 n=60",
        PURPLE,
        40,
    )
    d.box(980, 700, 740, 155, "H×C×S 반복측정 ANOVA\n문자 비율·시간 n=60", GREEN, 40)
    d.arrow("450,610 450,680")
    d.arrow("1350,610 1350,680")
    d.text(900, 965, "질의별 대응 t-검정 · 반복측정 ANOVA · 평균(SD) · 효과크기", 42)
    drawings[FIG / "fig5_0_evaluation_design.svg"] = d.svg()
    poster = args.poster_svg.read_text(encoding="utf-8")
    import re

    poster = re.sub(
        r'width="594mm" height="841mm" viewBox="[^"]+"',
        'width="159mm" height="81.847mm" viewBox="68 831 1033.52 532"',
        poster,
        count=1,
    )
    drawings[FIG / "fig4_1_pipeline.svg"] = poster
    for target, svg in drawings.items():
        target.write_text(svg, encoding="utf-8")
        subprocess.run(
            [
                str(args.inkscape),
                str(target),
                "--export-type=png",
                "--export-width=2400",
                "--export-filename=" + str(target.with_suffix(".png")),
            ],
            check=True,
            capture_output=True,
        )
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
        object_text = concept + ("를" if concept.endswith("구조") else "을")
        caption = f"본 연구에서 작성한 도식이며, {author} 외[{ref}]의 {object_text} 참고하였다."
        if n == "2-1":
            caption = (
                "본 연구에서 작성한 도식이며, Lewis 외[1]의 RAG 구조를 참고하였다."
            )
        usage = f"그림 {n} — 본 연구 작성. {author} 외[{ref}]의 {object_text} 참고하여 독립 도식을 작성하였다."
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
