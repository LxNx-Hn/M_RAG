"""Mutation tests for the errors found during academic review."""

import unittest
from pathlib import Path

from academic_language_checks import validate_academic_text

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md"
)


class AcademicRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")

    def test_reviewed_source(self):
        validate_academic_text(self.text)

    def test_reintroduced_errors(self):
        for correct, error in (
            ("검색 문맥으로 지칭한다", "검색 문맥가 달라졌다"),
            ("보정 후 p=0.117", "신뢰구간는 [+0.1880"),
            ("Holm 보정을 적용하였다", "HyDE와 CAD의 통제 비교"),
            ("100,000회", "200,000회"),
            ("Shi 외[3]의 CAD 로짓 결합을", "Shi 외[3]의 CAD 점수 합산을"),
            ("Lewis 외[1]는", "Lewis 외[1]은"),
            ("Li 외[4]는", "Li 외[4]은"),
        ):
            with self.subTest(error=error):
                self.assertIn(correct, self.text)
                with self.assertRaises(AssertionError):
                    validate_academic_text(self.text.replace(correct, error, 1))

    def test_shi_particle_regression(self):
        # The revised figure paragraph describes the actual example directly.
        # Keep this particle regression without forcing old prose into it.
        invalid = self.text + "\nShi 외[3]은 제시한 사례이다.\n"
        with self.assertRaisesRegex(AssertionError, "reviewed author particle error"):
            validate_academic_text(invalid)

    def test_caption_title_mismatch(self):
        correct = "[그림 5-2] RAPTOR 질의의 검색 근거, 생성 답변 및 평가 예시 ····"
        self.assertIn(correct, self.text)
        with self.assertRaisesRegex(AssertionError, "full titles differ"):
            validate_academic_text(
                self.text.replace(correct, "[그림 5-2] 다른 제목 ····", 1)
            )

    def test_duplicate_caption(self):
        caption = "[그림 5-2] RAPTOR 질의의 검색 근거, 생성 답변 및 평가 예시 [스타일=그림제목]"
        with self.assertRaises(AssertionError):
            validate_academic_text(self.text + "\n" + caption)


if __name__ == "__main__":
    unittest.main()
