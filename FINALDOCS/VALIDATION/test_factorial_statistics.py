"""Regression checks for scientific units, missingness and stored evidence."""

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FactorialStatisticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(
            (ROOT / "FINALDOCS/DATA/FACTORIAL_STATISTICS_60Q.json").read_text(
                encoding="utf-8"
            )
        )

    def test_original_artifacts_unchanged(self):
        for relative, expected in self.data["source_sha256"].items():
            self.assertEqual(
                hashlib.sha256(
                    (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
                ).hexdigest(),
                expected,
            )

    def test_missingness_and_statistical_unit(self):
        self.assertEqual(
            self.data["counts"],
            {"queries": 60, "records": 480, "valid_quality_cells": 1915},
        )
        self.assertEqual(len(self.data["missing_cells"]), 5)
        for result in self.data["paired"]:
            self.assertLessEqual(result["n"], 60)
        for result in self.data["anova"]:
            if result["metric"] == "faithfulness":
                self.assertEqual(
                    result["n"], 58 if result["protocol"].startswith("S0") else 57
                )
            else:
                self.assertEqual(result["n"], 60)

    def test_contrasts_are_not_main_effects(self):
        paired = next(
            r
            for r in self.data["paired"]
            if r["factor"] == "HyDE" and r["metric"] == "answer_relevancy"
        )
        main = next(
            r
            for r in self.data["anova"]
            if r["protocol"].startswith("S0")
            and r["effect"] == "H"
            and r["metric"] == "answer_relevancy"
        )
        self.assertAlmostEqual(paired["mean"], 0.080495, places=10)
        self.assertAlmostEqual(paired["p"], 0.029125256359383164, places=10)
        self.assertAlmostEqual(paired["p_holm"], 0.11650102543753266, places=10)
        self.assertGreater(main["p"], 0.05)

    def test_scd_is_not_tested_with_120_or_240_independent_queries(self):
        result = [r for r in self.data["paired"] if r["factor"].startswith("SCD")]
        self.assertEqual([r["raw_pairs"] for r in result], [120, 240])
        self.assertEqual([r["df"] for r in result], [59, 59])
        self.assertAlmostEqual(result[0]["mean"], 0.2182239417373891)
        self.assertAlmostEqual(result[1]["mean"], 0.22894148599301442)
        self.assertEqual(len(self.data["zero_denominator_answers"]), 1)
        self.assertTrue(
            all(r["n"] == 59 for r in self.data["zero_denominator_sensitivity"])
        )


if __name__ == "__main__":
    unittest.main()
