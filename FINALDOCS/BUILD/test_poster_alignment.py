"""Mutation tests reject native numeric-alignment corruption and missing SVG text."""

import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree

from poster_alignment import NS, validate_alignment

FOLDER = Path(__file__).resolve().parents[1] / "POSTER/FINAL"
PPTX, SVG = (
    FOLDER / "M_RAG_A1_FINAL_EDITABLE.pptx",
    FOLDER / "M_RAG_A1_FINAL_EDITABLE.svg",
)


def mutate_slide(work, operation):
    path = Path(work) / "broken.pptx"
    with zipfile.ZipFile(PPTX) as src, zipfile.ZipFile(path, "w") as dst:
        for entry in src.infolist():
            data = src.read(entry.filename)
            if entry.filename == "ppt/slides/slide1.xml":
                xml = etree.fromstring(data)
                operation(xml)
                data = etree.tostring(xml)
            dst.writestr(entry, data)
    return path


class PosterAlignmentTests(unittest.TestCase):
    def test_current_files(self):
        result = validate_alignment(PPTX, SVG)
        self.assertEqual(result["numeric_cells_right_aligned"], 120)

    def test_native_numeric_center_rejected(self):
        def change(xml):
            xml.findall(".//a:tbl", NS)[1].findall("a:tr", NS)[2].findall("a:tc", NS)[
                1
            ].find("a:txBody/a:p/a:pPr", NS).set("algn", "ctr")

        with tempfile.TemporaryDirectory() as work:
            with self.assertRaisesRegex(AssertionError, "PPTX table 2 row 2 col 1"):
                validate_alignment(mutate_slide(work, change), SVG)

    def test_svg_missing_text_rejected(self):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "broken.svg"
            xml = etree.fromstring(SVG.read_bytes())
            for el in xml.iter():
                if el.text and "미적용" in el.text:
                    el.text = el.text.replace("미적용", "기준")
            path.write_bytes(etree.tostring(xml))
            with self.assertRaisesRegex(AssertionError, "text missing"):
                validate_alignment(PPTX, path)
