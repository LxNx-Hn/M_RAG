"""Independently validate native-table paragraph and SVG numeric alignment."""

import zipfile
from pathlib import Path
from lxml import etree

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
SCHEMAS = [
    ["code"] * 4,
    ["code"] + ["number"] * 6,
    ["code"] + ["number"] * 4,
    ["description"] + ["number"] * 4,
]


def validate_alignment(pptx: Path, svg: Path) -> dict:
    with zipfile.ZipFile(pptx) as package:
        slide = etree.fromstring(package.read("ppt/slides/slide1.xml"))
    tables = slide.findall(".//a:tbl", NS)
    assert len(tables) == 4, "Expected four native tables"
    document = etree.fromstring(svg.read_bytes())
    checked = 0
    right = 0
    for ti, (table, types) in enumerate(zip(tables, SCHEMAS), 1):
        for ri, row in enumerate(table.findall("a:tr", NS)):
            cells = row.findall("a:tc", NS)
            assert len(cells) == len(types), "Table schema width differs"
            for ci, cell in enumerate(cells):
                kind = "code" if ri == 0 else types[ci]
                native = {"code": "ctr", "number": "r", "description": "l"}[kind]
                anchor = {"code": "middle", "number": "end", "description": "start"}[
                    kind
                ]
                paras = cell.findall("a:txBody/a:p", NS)
                assert paras
                for para in paras:
                    props = para.find("a:pPr", NS)
                    assert (
                        props is not None and props.get("algn") == native
                    ), f"PPTX table {ti} row {ri} col {ci}: expected {native}"
                labels = document.xpath(
                    f'//*[@data-table-cell and starts-with(@data-table-cell,"{ti}:{ri}:{ci}:")]'
                )
                assert labels, f"Missing SVG table label {ti}:{ri}:{ci}"
                assert all(
                    label.get("text-anchor") == anchor for label in labels
                ), f"SVG table {ti} row {ri} col {ci}: expected {anchor}"
                checked += 1
                right += kind == "number"
    return {
        "cells_checked": checked,
        "numeric_cells_right_aligned": right,
        "native_and_svg_alignment_match": True,
    }
