"""Artifact checks for protocol grouping, definitions and professor feedback."""

import re
import zipfile
from pathlib import Path

from lxml import etree as ET

A = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


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


def validate_poster(pptx: Path, svg: Path):
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
        "+0.080",
        "+21.8%p",
        "시간(초)",
    ]:
        if token not in joined:
            raise AssertionError("Missing reviewed poster content: " + token)
    for title in ["06 결과 해석", "07 결론"]:
        index = labels.index(title)
        prose = labels[index + 1]
        if re.search(r"p\s*[=<]|t\(|F\(|\+0\.\d", prose):
            raise AssertionError("Duplicate test values in interpretation/conclusion")
    return {
        "protocol_groups": [4, 4],
        "independent_abstract": poster_headings(labels),
        "abstract_required": False,
        "case_claim_evidence": True,
        "references": references,
    }


def validate_manuscript(text, tables):
    if re.search(r"^# (국문초록|Abstract)|^(주제어|Keywords):", text, re.M):
        raise AssertionError("Thesis abstract/keywords returned")
    means = next(t for t in tables if t["sheet"] == "T5-1_Mean_SD")
    protocol_order([row[0] for row in means["rows"][1:]])
    for token in [
        "# 목    차",
        "한국어를 포함한",
        "원정밀도",
        "대응 차이의 SD를 사용",
        "구분선을 표시",
    ]:
        if token not in text:
            raise AssertionError(
                "Missing professor-reviewed manuscript content: " + token
            )
    primary = text.split("# 1. 서론", 1)[1].split("# 참고문헌", 1)[0]
    if "부트스트랩 신뢰구간" in primary:
        raise AssertionError(
            "Auxiliary confidence interval returned to primary results"
        )
    prose = "\n".join(
        line
        for line in text.splitlines()
        if not line.startswith(("[", "#", "```")) and "\t" not in line
    )
    for kind, number in re.findall(
        r"^\[(표|그림) ([\dA-Z]+-\d+)\].*\[스타일=(?:표|그림)제목\]$", text, re.M
    ):
        linked = f"{kind} {number}" in prose
        if kind == "그림" and number in [f"B-{i}" for i in range(1, 6)]:
            linked = linked or "그림 B-1~B-5" in prose
        if not linked:
            raise AssertionError(
                "Missing body object reference: " + kind + " " + number
            )
    return {
        "manuscript_abstracts": 2,
        "protocol_groups": [4, 4],
        "primary_bootstrap_sentence": False,
    }
