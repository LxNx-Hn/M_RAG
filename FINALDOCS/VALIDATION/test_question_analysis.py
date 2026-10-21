"""Reject altered research evidence, lost pairs, and rejected submission prose."""

import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "FINALDOCS/ANALYSIS"))
from analyze_questions import deltas, load, annotate, source_questions  # noqa: E402
from verify_question_analysis import (  # noqa: E402
    validate_observations,
    validate_pairs,
    FORBIDDEN,
)  # noqa: E402


class QuestionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs, cls.ann = load()

    def test_original_values(self):
        validate_observations(self.obs)

    def test_changed_quality_value(self):
        bad = self.obs.copy()
        bad.loc[0, "faithfulness"] += 0.01
        with self.assertRaisesRegex(AssertionError, "Original score changed"):
            validate_observations(bad)

    def test_missing_condition(self):
        with self.assertRaisesRegex(AssertionError, "60 x 8"):
            validate_observations(self.obs.iloc[1:])

    def test_duplicate_condition(self):
        bad = self.obs.copy()
        bad.loc[1] = bad.loc[0]
        with self.assertRaisesRegex(AssertionError, "Duplicate"):
            validate_observations(bad)

    def test_four_types_preserved(self):
        a = annotate(self.ann, source_questions())
        self.assertEqual(
            a.question_type.value_counts().to_dict(),
            {
                "방법 및 절차": 29,
                "결과 및 비교": 20,
                "사실 및 정의": 8,
                "목적 및 기여": 3,
            },
        )

    def test_missing_pair_remains_missing(self):
        a = annotate(self.ann, source_questions())
        d = deltas(self.obs, a)
        x = d[
            (d.comparison == "미적용 → CAD")
            & (d.metric == "faithfulness")
            & (d.query_id == "ext_rag_003")
        ]
        self.assertTrue(pd.isna(x.delta.iat[0]))

    def test_exact_threshold_is_similar(self):
        a = annotate(self.ann, source_questions())
        d = deltas(self.obs, a)
        x = d[
            (d.comparison == "미적용 → CAD")
            & (d.metric == "faithfulness")
            & (d.query_id == "ext_cad_007")
        ]
        self.assertEqual(x.delta.iat[0], -0.05)

    def test_zero_exclusion_preserves_original_score(self):
        d = deltas(self.obs, annotate(self.ann, source_questions()))
        validate_pairs(self.obs, d)
        excluded = d[d.relevancy_zero_excluded]
        self.assertGreater(len(excluded), 0)
        self.assertTrue(excluded.delta.isna().all())
        self.assertTrue(
            ((excluded.base_value == 0) | (excluded.applied_value == 0)).all()
        )
        bad = d.copy()
        index = excluded.index[0]
        bad.loc[index, "delta"] = (
            bad.loc[index, "applied_value"] - bad.loc[index, "base_value"]
        )
        with self.assertRaisesRegex(AssertionError, "Excluded or missing"):
            validate_pairs(self.obs, bad)

    def test_user_rejected_content(self):
        for text in [
            "중앙값",
            "Delta",
            "검색 개선을 단정하지 않는다",
            "품질을 보장하지 않는다",
        ]:
            self.assertIsNotNone(FORBIDDEN.search(text))


if __name__ == "__main__":
    unittest.main()
