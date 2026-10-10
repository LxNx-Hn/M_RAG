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
            ("최종 검색 문맥은 서로 달랐다", "최종 검색 문맥가 달라졌다"),
            ("95% 신뢰구간은 [+0.1880", "95% 신뢰구간는 [+0.1880"),
            ("HyDE와 CAD의 주 대응 비교", "HyDE와 CAD의 통제 비교"),
            ("그림 5-3, 5-5, 5-7, 5-8, 5-10", "그림 5-3~5-10"),
            ("\t증가\t감소\t동률\tn", "\tWin\tLoss\tTie\tn"),
            (
                "RAGAS 지표의 대응 차이가 +0.01을 초과",
                "RAGAS 지표의 대응 차이가 +0.02를 초과",
            ),
            ("출처: Es 외[10], 표 2에서", "출처: Es 외[10], 그림 2에서"),
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
        correct = "[그림 5-4] HyDE와 CAD의 주 대응 비교 ····"
        self.assertIn(correct, self.text)
        with self.assertRaisesRegex(AssertionError, "full titles differ"):
            validate_academic_text(
                self.text.replace(correct, "[그림 5-4] 다른 제목 ····", 1)
            )

    def test_duplicate_caption(self):
        caption = "[그림 5-4] HyDE와 CAD의 주 대응 비교 [스타일=그림제목]"
        with self.assertRaises(AssertionError):
            validate_academic_text(self.text + "\n" + caption)


if __name__ == "__main__":
    unittest.main()
