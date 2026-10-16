"""Regressions detect meaningful feedback violations in supplied content."""

import json
import unittest
from pathlib import Path

from professor_acceptance_checks import (
    poster_headings,
    poster_reference_coverage,
    protocol_order,
    validate_manuscript,
    validate_poster,
)

FINAL = Path(__file__).resolve().parents[1]


class ProfessorAcceptanceTests(unittest.TestCase):
    def test_unlisted_pipeline_reference_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "Unlisted poster references: 18"):
            poster_reference_coverage(
                ["Mi:dm[18], HyDE[2]", "08 주요 참고문헌", "[2] Gao et al."]
            )

    def test_core_and_implementation_references_are_resolved(self):
        self.assertEqual(
            poster_reference_coverage(
                ["Mi:dm[18], HyDE[2]", "08 주요 참고문헌", "[2] Gao", "[18] Shin"]
            )["cited"],
            ["2", "18"],
        )

    def test_missing_body_reference_is_rejected(self):
        text = (
            (FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md")
            .read_text("utf-8")
            .replace("표 3-1의 요인", "실험 조건의 요인")
        )
        with self.assertRaisesRegex(AssertionError, "Missing body object reference"):
            validate_manuscript(
                text,
                json.loads((FINAL / "DATA/THESIS_TABLES_60Q.json").read_text("utf-8")),
            )

    def test_63_manual_criteria_are_traceable(self):
        register = json.loads(
            (FINAL / "VALIDATION/PROFESSOR_ACCEPTANCE_63.json").read_text("utf-8")
        )
        rows = register["criteria"]
        self.assertEqual([r["id"] for r in rows], [f"AC-{i:02}" for i in range(1, 64)])
        self.assertTrue(
            all(r["evidence"] and r["method"] and r["feedback_source"] for r in rows)
        )
        self.assertEqual(rows[-1]["status"], "추가 확인 필요")
        self.assertTrue(register["manual_status_is_not_automated_proof"])

    def test_current_manuscript(self):
        validate_manuscript(
            (FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md").read_text(
                "utf-8"
            ),
            json.loads((FINAL / "DATA/THESIS_TABLES_60Q.json").read_text("utf-8")),
        )

    def test_current_native_poster(self):
        folder = FINAL / "POSTER/A1_FINAL_TITLE_CONFIRMED_20261010"
        validate_poster(
            folder / "M_RAG_A1_FINAL_EDITABLE.pptx",
            folder / "M_RAG_A1_FINAL_EDITABLE.svg",
        )

    def test_interleaved_protocol_is_rejected(self):
        with self.assertRaises(AssertionError):
            protocol_order(
                [f"H{h}C{c}S{s}" for h in (0, 1) for c in (0, 1) for s in (0, 1)]
            )

    def test_abstract_heading_is_rejected(self):
        for heading in ["초록", "01 Abstract", "국문초록"]:
            with self.subTest(heading=heading), self.assertRaises(AssertionError):
                poster_headings([heading])

    def test_background_is_allowed(self):
        poster_headings(["01 연구 배경과 목적", "08 주요 참고문헌"])

    def test_missing_abstract_is_rejected_in_thesis(self):
        text = (
            (FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md")
            .read_text("utf-8")
            .replace("# 국문초록", "# 개요")
        )
        with self.assertRaises(AssertionError):
            validate_manuscript(
                text,
                json.loads((FINAL / "DATA/THESIS_TABLES_60Q.json").read_text("utf-8")),
            )
