"""Current prose, explicit comparison labels and source-art regressions."""

import json
import unittest
from pathlib import Path
from verify_question_analysis import FORBIDDEN
from manuscript_checks import validate_submission_assets

ROOT = Path(__file__).resolve().parents[2]


class ManuscriptTests(unittest.TestCase):
    def setUp(self):
        self.text = (
            ROOT / "FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
        ).read_text(encoding="utf-8")

    def test_rejected_prose_and_unrequested_methods_absent(self):
        self.assertIsNone(FORBIDDEN.search(self.text))

    def test_literature_sources(self):
        validate_submission_assets(ROOT, self.text)

    def test_comparison_names_are_explicit(self):
        tables = json.loads(
            (ROOT / "FINALDOCS/DATA/THESIS_TABLES_60Q.json").read_text(encoding="utf-8")
        )
        for t in tables:
            if t["sheet"].startswith("T5-"):
                groups = [t["rows"][r0][0] for r0, _, _, _ in t["merges"]]
                self.assertTrue(groups)
                self.assertTrue(all("기준 " in g and " → 적용 " in g for g in groups))

    def test_only_raw_score_parallel_result_figures(self):
        self.assertNotIn("fig5_5", self.text)
        self.assertNotIn("fig5_6", self.text)
        self.assertIn("fig5_3_parallel_english", self.text)
        self.assertIn("fig5_4_parallel_korean", self.text)

    def test_appendices(self):
        self.assertIn("# 부록 A.", self.text)
        self.assertIn("# 부록 B.", self.text)
        self.assertNotIn("# 부록 C.", self.text)


if __name__ == "__main__":
    unittest.main()
