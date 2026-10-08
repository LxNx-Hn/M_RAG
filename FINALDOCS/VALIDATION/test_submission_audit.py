"""Failure tests for final literature source/attribution contracts."""

import copy
import json
import unittest
from pathlib import Path

from submission_audit_checks import validate_submission_assets

ROOT = Path(__file__).resolve().parents[2]


class SubmissionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (
            ROOT / "FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
        ).read_text(encoding="utf-8")
        cls.manifest = json.loads(
            (
                ROOT / "FINALDOCS/FIGURES/LITERATURE/SUBMISSION_PROVENANCE.json"
            ).read_text(encoding="utf-8")
        )

    def test_current_assets(self):
        validate_submission_assets(ROOT, self.text, self.manifest)

    def test_missing_license_or_logo_disclosure(self):
        for value in (
            "https://creativecommons.org/licenses/by/4.0/",
            "OpenAI 로고 생략",
            "OpenAI·Ollama 로고 생략",
        ):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                validate_submission_assets(
                    ROOT, self.text.replace(value, "누락", 1), self.manifest
                )

    def test_changed_image_hash(self):
        changed = copy.deepcopy(self.manifest)
        changed["figures"][2]["png_sha256"] = "0" * 64
        with self.assertRaisesRegex(AssertionError, "hash mismatch"):
            validate_submission_assets(ROOT, self.text, changed)

    def test_unreviewed_version(self):
        with self.assertRaises(AssertionError):
            validate_submission_assets(
                ROOT,
                self.text.replace(
                    "fig2_2_lost_middle_tacl.png", "fig2_2_lost_middle_original.png"
                ),
                self.manifest,
            )

    def test_duplicate_source_record(self):
        changed = copy.deepcopy(self.manifest)
        changed["figures"].append(changed["figures"][0])
        with self.assertRaises(AssertionError):
            validate_submission_assets(ROOT, self.text, changed)


if __name__ == "__main__":
    unittest.main()
