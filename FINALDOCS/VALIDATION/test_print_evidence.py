"""Regression checks for fabricated or accidentally modified evidence."""

import copy
import json
import unittest

from print_evidence_checks import MANIFEST, PLAN, validate


class PrintEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.plan = json.loads(PLAN.read_text(encoding="utf-8"))

    def test_baseline(self):
        validate(self.manifest, self.plan)

    def test_changed_metric(self):
        self.manifest["cases"][0]["panels"][0]["metrics"]["faithfulness"] = 0.5
        with self.assertRaisesRegex(AssertionError, "Stored evidence mismatch"):
            validate(self.manifest, self.plan)

    def test_changed_quote(self):
        plan = copy.deepcopy(self.plan)
        plan["E01"]["hyde_off__no_decoder_control"][0]["text"] += " fabricated"
        with self.assertRaisesRegex(ValueError, "Changed source excerpt"):
            validate(self.manifest, plan)

    def test_changed_case(self):
        self.manifest["cases"][0]["query_id"] = "ext_midm_001"
        with self.assertRaisesRegex(AssertionError, "Stored evidence mismatch"):
            validate(self.manifest, self.plan)

    def test_changed_image_hash(self):
        self.manifest["cases"][0]["image_sha256"] = "0" * 64
        with self.assertRaisesRegex(AssertionError, "Print image changed"):
            validate(self.manifest, self.plan)


if __name__ == "__main__":
    unittest.main()
