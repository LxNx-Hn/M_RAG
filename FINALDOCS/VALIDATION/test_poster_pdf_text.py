"""PDF encoding aliases must not conceal missing content or changed numbers."""

import importlib.util
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "POSTER/FINAL/rebuild_exports.py"
SPEC = importlib.util.spec_from_file_location("poster_pdf_export", SOURCE)
EXPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXPORT)


class PosterPdfTextTests(unittest.TestCase):
    def test_cairo_en_dash_alias(self):
        EXPORT.validate_pdf_text(
            ["한국어 질의–영어 근거", "평균 0.080"],
            "한국어질의\u00ad영어근거\n평균 0.080",
        )

    def test_missing_word_rejected(self):
        with self.assertRaisesRegex(AssertionError, "PDF mismatch"):
            EXPORT.validate_pdf_text(["한국어 질의–영어 근거"], "한국어 질의\u00ad근거")

    def test_changed_number_rejected(self):
        with self.assertRaisesRegex(AssertionError, "PDF mismatch"):
            EXPORT.validate_pdf_text(["평균 0.080"], "평균 0.800")


if __name__ == "__main__":
    unittest.main()
