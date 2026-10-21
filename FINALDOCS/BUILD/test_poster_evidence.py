"""Mutations reject a changed poster number, a moved bold value and a removed table."""

import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree as ET

from poster_checks import A, ROOT, validate_poster

PPTX = ROOT / "FINALDOCS/POSTER/FINAL/M_RAG_A1_FINAL_EDITABLE.pptx"


class PosterEvidenceTests(unittest.TestCase):
    def trial(self, operation):
        with tempfile.TemporaryDirectory() as work:
            target = Path(work) / "broken.pptx"
            with zipfile.ZipFile(PPTX) as src, zipfile.ZipFile(target, "w") as dst:
                for entry in src.infolist():
                    data = src.read(entry.filename)
                    if entry.filename == "ppt/slides/slide1.xml":
                        slide = ET.fromstring(data)
                        operation(slide)
                        data = ET.tostring(slide)
                    dst.writestr(entry, data)
            validate_poster(target)

    def cell(self, slide, table, row, col):
        return slide.findall(".//a:tbl", A)[table].findall("a:tr", A)[row].findall("a:tc", A)[col]

    def test_current_poster(self):
        self.assertEqual(validate_poster(PPTX)["decimals"], 2)

    def test_changed_value(self):
        def change(slide):
            self.cell(slide, 2, 2, 4).find(".//a:t", A).text = "+0.99"

        with self.assertRaisesRegex(AssertionError, "Poster value differs"):
            self.trial(change)

    def test_bold_on_non_maximum(self):
        def change(slide):
            for r in self.cell(slide, 4, 1, 2).findall(".//a:rPr", A):
                r.set("b", "1")

        with self.assertRaisesRegex(AssertionError, "bold differs"):
            self.trial(change)

    def test_removed_table(self):
        def change(slide):
            frame = slide.findall(".//a:tbl", A)[4].getparent().getparent().getparent()
            frame.getparent().remove(frame)

        with self.assertRaises(AssertionError):
            self.trial(change)
