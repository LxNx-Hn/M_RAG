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

    def test_condition_names_are_explicit(self):
        tables = json.loads(
            (ROOT / "FINALDOCS/DATA/THESIS_TABLES_60Q.json").read_text(encoding="utf-8")
        )
        names = ["1 미적용", "2 HyDE", "3 CAD", "4 SCD", "5 HyDE+CAD", "6 HyDE+SCD", "7 CAD+SCD", "8 HyDE+CAD+SCD"]
        for t in tables:
            if t["sheet"].startswith(("T3-", "T5-")):
                labels = [r[0] for r in t["rows"] if r[0] in names]
                self.assertEqual(labels[:8], names)
                text = json.dumps(t["rows"], ensure_ascii=False)
                self.assertNotIn("→", text)
                self.assertNotIn("·", text)
                self.assertNotRegex(text, r"H[01]C[01]S[01]")

    def test_only_raw_score_parallel_result_figures(self):
        self.assertNotIn("fig5_5_question_deltas", self.text)
        self.assertNotIn("fig5_6", self.text)
        for stem in ["fig5_3_parallel_numeric", "fig5_4_parallel_method", "fig5_5_parallel_concept"]:
            self.assertIn(stem, self.text)

    def test_appendices(self):
        self.assertIn("# 부록 A.", self.text)
        self.assertIn("# 부록 B.", self.text)
        self.assertNotIn("# 부록 C.", self.text)


if __name__ == "__main__":
    unittest.main()
