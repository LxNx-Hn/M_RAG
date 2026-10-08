"""Context review regressions for defensiveness and genuine scientific negatives."""

import copy
import hashlib
import json
import unittest
from pathlib import Path

from prose_audit_checks import REVIEW, units, validate_prose

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
)


class ProseReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        cls.review = json.loads(REVIEW.read_text(encoding="utf-8"))

    def test_reviewed_manuscript(self):
        validate_prose(self.text)
        self.assertEqual(
            [u["sha256"] for u in units(self.text)],
            [u["sha256"] for u in self.review["final_review"]],
        )

    def test_each_retired_defensive_sentence(self):
        self.assertGreaterEqual(len(self.review["retired_defensive_sentences"]), 11)
        for sentence in self.review["retired_defensive_sentences"]:
            with self.subTest(sentence=sentence):
                with self.assertRaisesRegex(AssertionError, "retired defensive"):
                    validate_prose(self.text + "\n\n" + sentence)

    def test_new_unreviewed_defense(self):
        for sentence in (
            "다른 모델에서의 성능을 판단할 수 없다.",
            "문장의 자연스러움은 측정하지 않았다.",
            "모든 방법을 구현한 것이 아니다.",
            "새 도메인으로의 일반화는 어렵다.",
            "이 결과는 향상을 보장하지 않는다.",
            "This study did not evaluate other models.",
        ):
            with self.subTest(sentence=sentence):
                with self.assertRaisesRegex(AssertionError, "unreviewed"):
                    validate_prose(self.text + "\n\n" + sentence)

    def test_reason_required_for_scientific_negative(self):
        review = copy.deepcopy(self.review)
        entry = next(e for e in review["final_review"] if e["candidate"])
        entry["reason"] = ""
        with self.assertRaisesRegex(AssertionError, "unreviewed"):
            validate_prose(self.text, review)

    def test_scientific_negatives_are_retained(self):
        for phrase in ("0을 포함", "-0.0343", "지지하지 않는", "ON/OFF"):
            self.assertIn(phrase, self.text)
        validate_prose(self.text)

    def test_new_unreviewed_causal_explanation(self):
        with self.assertRaisesRegex(AssertionError, "unreviewed prose unit"):
            validate_prose(self.text + "\n\n질문 복잡도가 이 차이의 원인이다.")

    def test_code_equations_and_original_bibliography_excluded(self):
        addition = (
            "\n```text\n원자료: 측정하지 않았다.\n```\n"
            "$$ 값이 없다 $$\n"
            "# 참고문헌 [스타일=참고문헌제목]\n"
            "[99] Original title: What is not implemented.\n"
        )
        validate_prose(self.text + addition)

    def test_approval_is_for_exact_sentence(self):
        entry = next(e for e in self.review["final_review"] if e["candidate"])
        replacement = entry["text"] + " 이 분석으로 전체 성능은 판단할 수 없다."
        self.assertNotEqual(
            entry["sha256"], hashlib.sha256(replacement.encode("utf-8")).hexdigest()
        )
        with self.assertRaisesRegex(AssertionError, "unreviewed"):
            validate_prose(self.text.replace(entry["text"], replacement, 1))


if __name__ == "__main__":
    unittest.main()
