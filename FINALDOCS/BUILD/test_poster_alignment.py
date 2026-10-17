"""Mutation tests reject actual native and SVG numeric-alignment corruption."""

import tempfile
import unittest
import zipfile
from pathlib import Path
from lxml import etree
from poster_alignment import validate_alignment, NS

FOLDER = Path(__file__).resolve().parents[1] / "POSTER/FINAL"


class PosterAlignmentTests(unittest.TestCase):
    def test_current_files(self):
        result = validate_alignment(
            FOLDER / "M_RAG_A1_FINAL_EDITABLE.pptx",
            FOLDER / "M_RAG_A1_FINAL_EDITABLE.svg",
        )
        self.assertEqual(result["numeric_cells_right_aligned"], 88)

    def test_native_numeric_center_rejected(self):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "broken.pptx"
            with zipfile.ZipFile(
                FOLDER / "M_RAG_A1_FINAL_EDITABLE.pptx"
            ) as src, zipfile.ZipFile(path, "w") as dst:
                for entry in src.infolist():
                    data = src.read(entry.filename)
                    if entry.filename == "ppt/slides/slide1.xml":
                        xml = etree.fromstring(data)
                        xml.findall(".//a:tbl", NS)[1].findall("a:tr", NS)[1].findall(
                            "a:tc", NS
                        )[1].find("a:txBody/a:p/a:pPr", NS).set("algn", "ctr")
                        data = etree.tostring(xml)
                    dst.writestr(entry, data)
            with self.assertRaisesRegex(AssertionError, "PPTX table 2 row 1 col 1"):
                validate_alignment(path, FOLDER / "M_RAG_A1_FINAL_EDITABLE.svg")

    def test_svg_numeric_center_rejected(self):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "broken.svg"
            xml = etree.fromstring(
                (FOLDER / "M_RAG_A1_FINAL_EDITABLE.svg").read_bytes()
            )
            xml.xpath('//*[@data-table-cell="2:1:1:0"]')[0].set("text-anchor", "middle")
            path.write_bytes(etree.tostring(xml))
            with self.assertRaisesRegex(AssertionError, "SVG table 2 row 1 col 1"):
                validate_alignment(FOLDER / "M_RAG_A1_FINAL_EDITABLE.pptx", path)
