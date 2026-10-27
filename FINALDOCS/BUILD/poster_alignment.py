"""Validate native-table alignment of the A1 poster and its SVG text.

Header cells are centred, numbers right-aligned and descriptions left-aligned
in the editable PPTX. The SVG (rendered from PowerPoint's PDF) must contain
every table cell text.
"""

import zipfile
from pathlib import Path

from lxml import etree

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
# c: centred short code, d: description (left), n: number (right)
# each schema is (column kinds, number of header rows)
SCHEMAS = [
    (["d", "d", "d"], 1),  # 04 metric definitions
    (["d"] + ["n"] * 15, 2),  # 05 question-type means
]


def validate_alignment(pptx: Path, svg: Path) -> dict:
    with zipfile.ZipFile(pptx) as package:
        slide = etree.fromstring(package.read("ppt/slides/slide1.xml"))
    tables = slide.findall(".//a:tbl", NS)
    assert len(tables) == len(SCHEMAS), "Expected the definition and result tables"
    vector = "".join("".join(etree.fromstring(svg.read_bytes()).itertext()).split())
    checked = right = 0
    for ti, (table, (kinds, heads)) in enumerate(zip(tables, SCHEMAS), 1):
        for ri, row in enumerate(table.findall("a:tr", NS)):
            cells = row.findall("a:tc", NS)
            assert len(cells) == len(kinds), "Table schema width differs"
            for ci, cell in enumerate(cells):
                kind = "c" if ri < heads else kinds[ci]
                expected = {"c": "ctr", "n": "r", "d": "l"}[kind]
                for para in cell.findall("a:txBody/a:p", NS):
                    props = para.find("a:pPr", NS)
                    assert (
                        props is not None and props.get("algn") == expected
                    ), f"PPTX table {ti} row {ri} col {ci}: expected {expected}"
                label = "".join(
                    "".join(cell.xpath(".//a:t/text()", namespaces=NS)).split()
                )
                assert (
                    label in vector
                ), f"SVG table {ti} row {ri} col {ci}: text missing"
                checked += 1
                right += kind == "n"
    return {
        "cells_checked": checked,
        "numeric_cells_right_aligned": right,
        "svg_text_matches": True,
    }
