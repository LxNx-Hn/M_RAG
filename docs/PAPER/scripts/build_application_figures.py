"""Build editable SVG diagrams of the applied-experiment path (no model calls)."""

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/PAPER/output/application_study/figures"


def start(width, height):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        "<style>text{font-family:Malgun Gothic,Noto Sans KR,sans-serif;fill:#202020;paint-order:stroke;stroke:white;stroke-width:4px;stroke-linejoin:round} .box{fill:white;stroke:#444;stroke-width:1.5} .link{fill:none;stroke:#444;stroke-width:1.5}</style>",
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L7 4 L0 8" fill="none" stroke="#444"/></marker></defs>',
    ]


def text(parts, x, y, value, size=20, anchor="middle"):
    parts.append(
        f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def box(parts, x, y, w, h, lines, size=20):
    parts.append(f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}"/>')
    for i, line in enumerate(lines):
        text(
            parts,
            x + w / 2,
            y + h / 2 + 7 + (i - (len(lines) - 1) / 2) * 29,
            line,
            size,
        )


def link(parts, path, arrow=True, dashed=False):
    extra = ' marker-end="url(#arrow)"' if arrow else ""
    if dashed:
        extra += ' stroke-dasharray="6 5"'
    parts.append(f'<path class="link" d="{path}"{extra}/>')


def save(name, parts):
    (OUT / name).write_text("\n".join(parts + ["</svg>"]) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    p = start(1100, 380)
    p.append('<rect class="box" x="320" y="20" width="730" height="340"/>')
    text(p, 685, 53, "기법 적용 실험 프로그램", 23)
    p.append('<circle class="box" cx="145" cy="115" r="21"/>')
    link(p, "M145 136 V216 M102 167 H188 M145 216 L107 270 M145 216 L183 270", False)
    text(p, 145, 312, "실험 수행자", 23)
    for y, name in [
        (108, "UC1 입력과 조건 확인"),
        (208, "UC2 조건별 검색·생성"),
        (308, "UC3 결과 분석·검증"),
    ]:
        p.append(f'<ellipse class="box" cx="695" cy="{y}" rx="265" ry="34"/>')
        text(p, 695, y + 7, name, 22)
        link(p, f"M188 167 L430 {y}", False)
    save("usecases.svg", p)

    p = start(1200, 400)
    box(p, 25, 140, 190, 100, ["질문·대상 논문", "모듈 적용 조건"])
    p.append('<rect class="box" x="260" y="25" width="605" height="335"/>')
    text(p, 562, 61, "Alice Cloud · Python 실험 실행기", 23)
    box(p, 285, 98, 220, 105, ["자료·검색", "SQLite / 문서 색인", "BM25 / RRF"], 19)
    box(
        p,
        545,
        98,
        295,
        105,
        ["GPU · Transformers", "BGE-M3 / CrossEncoder", "Mi:dm 2.0 Base"],
        19,
    )
    box(p, 370, 264, 385, 65, ["답변·문맥·설정 → JSONL 저장"], 20)
    link(p, "M215 185 H285")
    link(p, "M505 150 H545")
    link(p, "M692 203 V240 H562 V264")
    box(p, 905, 98, 265, 105, ["품질 평가", "RAGAS / BGE-M3", "OpenAI 평가 모델"], 19)
    box(p, 905, 264, 265, 65, ["언어 분석·대응 비교"], 20)
    link(p, "M755 296 H882 V150 H905")
    link(p, "M755 296 H905")
    link(p, "M1037 203 V264")
    save("architecture.svg", p)

    p = start(1200, 575)
    box(
        p,
        385,
        20,
        430,
        87,
        [
            "«module» main_generation_executor",
            "build_components() / execute_main_generation()",
        ],
        18,
    )
    classes = [
        (
            25,
            185,
            260,
            "QueryExpander",
            ["expand()", "translate_ko_to_en()", "expand_hyde()"],
        ),
        (325, 185, 250, "HybridRetriever", ["search_with_trace()"]),
        (620, 185, 250, "Reranker", ["rerank()"]),
        (915, 185, 260, "ContextCompressor", ["compress()", "truncate_to_limit()"]),
        (100, 385, 280, "Generator", ["generate()", "get_empty_context_inputs()"]),
        (510, 385, 260, "CADDecoder", ["__call__()"]),
        (870, 385, 270, "SCDDecoder", ["__call__()"]),
    ]
    for x, y, w, name, methods in classes:
        h = 125
        p.append(f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}"/>')
        text(p, x + w / 2, y + 30, name, 22)
        link(p, f"M{x} {y+43} H{x+w}", False)
        for i, method in enumerate(methods):
            text(p, x + 14, y + 68 + i * 22, method, 17, "start")
    for x in [155, 450, 745, 1045]:
        link(p, f"M600 107 V142 H{x} V185", True, True)
    link(p, "M155 310 V350 H240 V385", True, True)
    text(p, 243, 343, "생성에 사용", 16)
    link(p, "M385 65 H10 V368 H240 V385", True, True)
    link(p, "M815 65 H1188 V350 H640 V385", True, True)
    link(p, "M1188 350 H1005 V385", True, True)
    link(p, "M510 446 H380", True, True)
    text(p, 444, 431, "모델 사용", 16)
    text(
        p,
        600,
        553,
        "점선은 사용 관계를 나타낸다. CAD와 SCD는 토큰 생성 중 차례로 적용된다.",
        19,
    )
    save("modules.svg", p)

    p = start(1200, 650)
    lanes = [
        (120, "실험 수행자"),
        (340, "생성 실행기"),
        (570, "검색·문맥 구성"),
        (800, "Generator"),
        (1060, "저장·평가"),
    ]
    for x, label in lanes:
        box(p, x - 100, 20, 200, 58, [label], 20)
        link(p, f"M{x} 78 V610", False, True)
    messages = [
        (120, 340, 125, "UC1 질문·대상 논문·조건 선택"),
        (340, 800, 195, "HyDE-on: 번역·가상 문서 생성"),
        (800, 340, 245, "검색 표현 반환"),
        (340, 570, 310, "UC2 검색·재정렬·압축"),
        (570, 340, 360, "실제 논문 문맥 반환"),
        (340, 800, 435, "질문·문맥·CAD/SCD 설정"),
        (800, 340, 485, "답변 반환"),
        (340, 1060, 555, "답변·문맥·설정 저장 → UC3 평가·분석"),
    ]
    for x1, x2, y, label in messages:
        link(p, f"M{x1} {y} H{x2}")
        text(p, (x1 + x2) / 2, y - 12, label, 17)
    text(p, 990, 425, "토큰 생성 중", 17)
    text(p, 990, 450, "CAD → SCD 적용", 17)
    text(
        p,
        600,
        635,
        "각 질문과 조건에 반복 적용하며, 저장된 답변의 평가는 생성 후 별도로 수행한다.",
        18,
    )
    save("sequence.svg", p)


if __name__ == "__main__":
    main()
