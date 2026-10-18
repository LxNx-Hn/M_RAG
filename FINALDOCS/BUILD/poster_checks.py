"""Native poster protocol groups, source coverage, statistics and case content."""

import json
import re
import zipfile
from pathlib import Path
from lxml import etree as ET

A = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
STATS = Path(__file__).resolve().parents[1] / "DATA/TTEST_ANOVA_60Q.json"
# The thesis reports paired t-tests and RM ANOVA without multiplicity adjustment.
RETIRED_STATISTICS = [
    "Holm",
    "보정 p",
    "보정 전",
    "보정 후",
    "Wilcoxon",
    "윌콕슨",
    "부호순열",
    "부호 순열",
    "sign-flip",
    "permutation",
]


def expected_statistics_tables(stats):
    """Poster ANOVA and paired-comparison cells derived from the thesis table rows."""
    from build_ttest_anova_tables import build

    tables = {t["sheet"]: t["rows"] for t in build(stats)}
    korean, runtime = (
        tables["T5-4_Korean_ANOVA"][1:],
        tables["T5-5_Runtime_ANOVA"][1:],
    )
    anova = [["요인", "한국어 비율\nF", "p", "실행 시간\nF", "p"]] + [
        [k[0], k[2], k[3], t[2], t[3]] for k, t in zip(korean, runtime)
    ]
    labels = ["HyDE\n답변 관련성", "CAD\n근거 충실도", "SCD H0\n한국어 비율"]
    paired = [["비교", "차이\n(SD)", "t(df)", "p", "dz"]] + [
        [label, row[5].replace(" ", "\n"), row[6].replace(" ", "\n"), row[7], row[8]]
        for label, row in zip(labels, tables["T5-3_RQ_Paired"][1:])
    ]
    return anova, paired


def table_cells(table):
    return [
        [
            "\n".join(
                "".join(p.xpath(".//a:t/text()", namespaces=A))
                for p in cell.findall("a:txBody/a:p", A)
            )
            for cell in row.findall("a:tc", A)
        ]
        for row in table.findall("a:tr", A)
    ]


def svg_table_cells(document, index):
    cells = {}
    for node in document.xpath("//*[@data-table-cell]"):
        t, r, c, k = map(int, node.get("data-table-cell").split(":"))
        if t == index:
            cells.setdefault((r, c), {})[k] = node.text or ""
    rows = 1 + max(r for r, _ in cells)
    cols = 1 + max(c for _, c in cells)
    return [
        ["\n".join(v for _, v in sorted(cells[(r, c)].items())) for c in range(cols)]
        for r in range(rows)
    ]


def poster_statistics(slide, document, stats):
    joined = "\n".join(slide.xpath(".//a:t/text()", namespaces=A))
    joined += "\n" + "\n".join(document.itertext())
    retired = [token for token in RETIRED_STATISTICS if token in joined]
    if retired:
        raise AssertionError("Retired poster statistics wording: " + ", ".join(retired))
    tables = slide.findall(".//a:tbl", A)
    for index, expected in zip((3, 4), expected_statistics_tables(stats)):
        for name, actual in [
            ("PPTX", table_cells(tables[index - 1])),
            ("SVG", svg_table_cells(document, index)),
        ]:
            if actual != expected:
                raise AssertionError(
                    f"{name} poster table {index} differs from TTEST_ANOVA_60Q tables"
                )
    return {"anova_rows": 7, "paired_rows": 3, "multiplicity_adjustment": None}


def protocol_order(codes):
    expected = [f"H{h}C{c}S{s}" for s in (0, 1) for h in (0, 1) for c in (0, 1)]
    if codes != expected:
        raise AssertionError("S0/S1 protocol groups must each contain four conditions")


def poster_headings(labels):
    """Report an optional poster abstract; its presence is a design decision."""
    return any(
        re.fullmatch(
            r"\s*(?:\d{2}\s*)?(?:국문)?초록\s*|\s*(?:\d{2}\s*)?Abstract\s*", value, re.I
        )
        for value in labels
    )


def poster_reference_coverage(labels):
    joined = "\n".join(labels)
    body, bibliography = joined.split("08 주요 참고문헌", 1)
    cited = set(re.findall(r"\[([MD]?\d+)\]", body))
    listed = set(re.findall(r"\[([MD]?\d+)\]", bibliography))
    missing = cited - listed
    if missing:
        raise AssertionError(
            "Unlisted poster references: " + ", ".join(sorted(missing))
        )

    def order(value):
        return (
            bool(value[0].isalpha()),
            value[0] if value[0].isalpha() else "",
            int(re.search(r"\d+", value)[0]),
        )

    return {"cited": sorted(cited, key=order), "listed": sorted(listed, key=order)}


def validate_poster(pptx: Path, svg: Path, stats_path: Path = STATS):
    with zipfile.ZipFile(pptx) as package:
        slide = ET.fromstring(package.read("ppt/slides/slide1.xml"))
    labels = slide.xpath(".//a:t/text()", namespaces=A)
    poster_headings(labels)
    references = poster_reference_coverage(labels)
    document = ET.fromstring(svg.read_bytes())
    poster_headings(list(document.itertext()))
    table = slide.findall(".//a:tbl", A)[1]
    protocol_order(
        [
            "".join(row.findall("a:tc", A)[0].xpath(".//a:t/text()", namespaces=A))
            for row in table.findall("a:tr", A)[1:]
        ]
    )
    # A visible, editable boundary spans the means table in both representations.
    boundary = document.xpath("//*[local-name()='rect' and @height='3']")
    if not any(abs(float(node.get("y")) - 842.5) < 0.01 for node in boundary):
        raise AssertionError("Missing S0/S1 group separator")
    joined = "\n".join(labels)
    for token in [
        "Retrieval-Augmented Generation",
        "가상 문서 검색",
        "검색 근거의 영향 조정",
        "출력 언어 제어",
        "By providing both the original text and higher-level summaries",
        "노드를 선택할 수 있습니다",
        "반복측정 분산분석(ANOVA)",
        "대응 t-검정",
        "관련성이 유의하게 높았으나(p=0.029)",
        "추가 비교에서는 p=0.114",
        "충실도 차이는 작았고(p=0.393)",
        "+21.8%p",
        "추가 시간이 약 8.8초 줄었다(C×S, p<0.001)",
        "한국어 비율 S·H×C / 실행 시간 H·C·S·C×S",
        "p: 양측 p",
        "시간(초)",
        "세 기법의",
        "입력 길이 관리",
        "검색 결과가 모두 지지",
        "평가 언어: S0 영어 / S1 한국어 번역, 생성 입력은 모두 영어",
        "S0: 영어로 평가 / S1: 한국어 번역으로 평가",
        "한국어 답변이 필요하면 SCD가 비용이 작은 선택지다.",
        "시간 비용이 커서(약 2.9배; SCD 미적용 3.1배, 적용 2.7배)",
        "효과가 기대될 때 선택적으로 검토한다",
        "논문의 참고문헌에 수록",
        "SCD 대응쌍은 질의별 평균(n=60)",
        "차이 = ON − OFF 평균.",
        "언어 이탈",
        "검색 결과가 뒷받침하는 답변 주장",
        "15개 단위로 요약해 단위별 질의",
        "RAGAS를 거치지 않고 직접 계산",
    ]:
        if token not in joined:
            raise AssertionError("Missing reviewed poster content: " + token)
    # Wording aligned with the latest manuscript replaces these phrases.
    for token in [
        "평가 문맥",
        "생성 문맥",
        "문맥 길이",
        "REFERENCES.md",
        "동봉 상세표",
        "두 SCD 상태 모두에서",
        "21.822%p",
        "120·240쌍",
        "한국어 사용 비중",
        "생성 기록에서 직접 계산",
        "답변과 실행 시간에서 직접 계산",
        "평균 차이다.",
        "탐색적 결과",
        "보정 없는",
        "선택이었다.",
    ]:
        if token in joined:
            raise AssertionError("Retired poster wording: " + token)
    statistics = poster_statistics(
        slide, document, json.loads(stats_path.read_text("utf-8"))
    )
    return {
        "statistics": statistics,
        "protocol_groups": [4, 4],
        "independent_abstract": poster_headings(labels),
        "abstract_required": False,
        "case_claim_evidence": True,
        "references": references,
    }
