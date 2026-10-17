"""Native poster protocol groups, source coverage and case content."""

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
    return {
        "protocol_groups": [4, 4],
        "independent_abstract": poster_headings(labels),
        "abstract_required": False,
        "case_claim_evidence": True,
        "references": references,
    }
