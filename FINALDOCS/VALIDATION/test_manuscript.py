"""Mutation regressions for manuscript content, provenance and protocol."""

import copy
import hashlib
import json
import unittest
from pathlib import Path
from manuscript_checks import (
    REVIEW,
    units,
    validate_prose,
    validate_academic_text,
    validate_submission_assets,
    validate_manuscript,
)
from poster_checks import (
    poster_headings,
    poster_reference_coverage,
    protocol_order,
    validate_poster,
)

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
        entry = next((e for e in review["final_review"] if e["candidate"]))
        for occurrence in review["final_review"]:
            if occurrence["sha256"] == entry["sha256"]:
                occurrence["reason"] = ""
        with self.assertRaisesRegex(AssertionError, "unreviewed"):
            validate_prose(self.text, review)

    def test_scientific_negatives_are_retained(self):
        for phrase in (
            "p값은 유의수준 0.05보다 컸다",
            "p=0.393",
            "분모가 0인 답변",
            "ON−OFF",
        ):
            self.assertIn(phrase, self.text)
        validate_prose(self.text)

    def test_new_unreviewed_causal_explanation(self):
        with self.assertRaisesRegex(AssertionError, "unreviewed prose unit"):
            validate_prose(self.text + "\n\n질문 복잡도가 이 차이의 원인이다.")

    def test_editorial_history_cannot_be_manifest_approved(self):
        sentence = "초기 질문과 LLM 요약 대화 원본은 미보관 상태다."
        text = self.text + "\n\n" + sentence
        review = copy.deepcopy(self.review)
        review["final_review"].extend(
            (
                dict(u, decision="retain", type="F", reason="approved")
                for u in units(sentence)
            )
        )
        with self.assertRaisesRegex(AssertionError, "forbidden editorial"):
            validate_prose(text, review)

    def test_code_equations_and_original_bibliography_excluded(self):
        addition = "\n```text\n원자료: 측정하지 않았다.\n```\n$$ 값이 없다 $$\n# 참고문헌 [스타일=참고문헌제목]\n[99] Original title: What is not implemented.\n"
        validate_prose(self.text + addition)

    def test_initials_and_numeric_section_sentence_boundary(self):
        text = "Nelson F. Liu의 연구를 참고하였다. 5.5절에서 설명한다."
        self.assertEqual(
            [unit["text"] for unit in units(text)],
            ["Nelson F. Liu의 연구를 참고하였다.", "5.5절에서 설명한다."],
        )

    def test_approval_is_for_exact_sentence(self):
        entry = next((e for e in self.review["final_review"] if e["candidate"]))
        replacement = entry["text"] + " 이 분석으로 전체 성능은 판단할 수 없다."
        self.assertNotEqual(
            entry["sha256"], hashlib.sha256(replacement.encode("utf-8")).hexdigest()
        )
        with self.assertRaisesRegex(AssertionError, "unreviewed"):
            validate_prose(self.text.replace(entry["text"], replacement, 1))


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
            ("검색 결과와 답변이 함께", "검색 문맥과 답변이 함께"),
            (
                "대응 t-검정과 반복측정 ANOVA를 적용하였다.",
                "대응 t-검정과 반복측정 ANOVA를 적용하고 Holm 보정을 적용하였다.",
            ),
            (
                "모든 검정의 유의수준은 0.05로 정하였다.",
                "모든 검정의 유의수준은 0.05로 정하였다. Wilcoxon 검정을 추가하였다.",
            ),
            (
                "p값은 유의수준 0.05보다 컸다(t(57)=0.862, p=0.393",
                "유의하였다(t(57)=0.862, p=0.393",
            ),
            (
                "CAD의 문맥 포함·제외 로짓 결합[3] [스타일=그림제목]",
                "CAD의 문맥 포함·제외 로짓 결합 [스타일=그림제목]",
            ),
            ("Lewis 외의 RAG는", "Lewis 외[1]은"),
            ("Li 외는 이 현상을", "Li 외[4]은"),
        ):
            with self.subTest(error=error):
                self.assertIn(correct, self.text)
                with self.assertRaises(AssertionError):
                    validate_academic_text(self.text.replace(correct, error, 1))

    def test_defensive_negative_prose_rejected(self):
        broken = self.text.replace(
            "질의 하나가 표본 하나가 되도록 하였다(n=60).",
            "질의 하나가 표본 하나가 되도록 하였다(n=60). 각 쌍은 독립 표본이 아니다.",
            1,
        )
        self.assertNotEqual(broken, self.text)
        with self.assertRaisesRegex(AssertionError, "defensive negative prose"):
            validate_academic_text(broken)

    def test_shi_particle_regression(self):
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

    def test_reported_cross_reference_and_particle_errors(self):
        for correct, broken in (
            ("실제 문서 구간이다(그림 2-2).", "실제 문서 구간이다. 그림 2-2은 이를 나타낸다."),
            ("Shi 외는 요약 과제와", "Shi 외[3]은 요약 과제와"),
        ):
            with self.subTest(broken=broken):
                self.assertIn(correct, self.text)
                with self.assertRaises(AssertionError):
                    validate_academic_text(self.text.replace(correct, broken, 1))


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

    def test_missing_source_or_authorship_disclosure(self):
        for value in (
            self.manifest["figures"][0]["submission_source_url"],
            self.manifest["figures"][1]["usage_entry"],
            self.manifest["figures"][2]["caption_source"],
        ):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                broken = (
                    self.text.replace(f"{value} [스타일=그림제목]", "누락 [스타일=그림제목]")
                    if value.endswith("]")
                    else self.text.replace(value, "누락", 1)
                )
                validate_submission_assets(ROOT, broken, self.manifest)

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
                    "fig2_2_hyde_independent.png", "fig2_3_hyde_original.png"
                ),
                self.manifest,
            )

    def test_duplicate_source_record(self):
        changed = copy.deepcopy(self.manifest)
        changed["figures"].append(changed["figures"][0])
        with self.assertRaises(AssertionError):
            validate_submission_assets(ROOT, self.text, changed)

    def test_caption_manifest_must_match(self):
        source = self.manifest["figures"][0]["caption_source"]
        with self.assertRaisesRegex(AssertionError, "caption"):
            validate_submission_assets(
                ROOT, self.text.replace(source, "누락"), self.manifest
            )

    def test_independent_caption_role_cannot_change_in_both_files(self):
        changed = copy.deepcopy(self.manifest)
        source = changed["figures"][0]["caption_source"]
        changed["figures"][0]["caption_source"] = "출처: Lewis 외[1]의 그림 발췌."
        with self.assertRaisesRegex(AssertionError, "reference/object"):
            validate_submission_assets(
                ROOT,
                self.text.replace(source, changed["figures"][0]["caption_source"]),
                changed,
            )

    def test_usage_source_version_and_changes_cannot_be_omitted(self):
        for record in self.manifest["figures"]:
            for value in (record["usage_entry"], record["submission_source_url"]):
                with self.subTest(
                    figure=record["figure"], value=value
                ), self.assertRaises(AssertionError):
                    validate_submission_assets(
                        ROOT, self.text.replace(value, "누락", 1), self.manifest
                    )

    def test_source_reference_and_object_cannot_change_in_both_files(self):
        for index in (1, 2):
            changed = copy.deepcopy(self.manifest)
            old = changed["figures"][index]["caption_source"]
            new = old.replace("[2]", "[11]").replace("[3]", "[11]")
            changed["figures"][index]["caption_source"] = new
            with self.subTest(index=index), self.assertRaisesRegex(
                AssertionError, "reference/object"
            ):
                validate_submission_assets(ROOT, self.text.replace(old, new), changed)

    def test_long_url_below_figure_is_rejected(self):
        record = self.manifest["figures"][3]
        changed = copy.deepcopy(self.manifest)
        new = record["caption_source"] + " 원본: " + record["submission_source_url"]
        changed["figures"][3]["caption_source"] = new
        with self.assertRaises(AssertionError):
            validate_submission_assets(
                ROOT, self.text.replace(record["caption_source"], new), changed
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
            .replace("(표 3-1)", "")
        )
        with self.assertRaisesRegex(AssertionError, "Missing body object reference"):
            validate_manuscript(
                text,
                json.loads((FINAL / "DATA/THESIS_TABLES_60Q.json").read_text("utf-8")),
            )

    def test_current_manuscript(self):
        validate_manuscript(
            (FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md").read_text(
                "utf-8"
            ),
            json.loads((FINAL / "DATA/THESIS_TABLES_60Q.json").read_text("utf-8")),
        )

    def test_current_native_poster(self):
        folder = FINAL / "POSTER/FINAL"
        validate_poster(
            folder / "M_RAG_A1_FINAL_EDITABLE.pptx",
            folder / "M_RAG_A1_FINAL_EDITABLE.svg",
        )

    def test_poster_statistics_follow_ttest_anova(self):
        import tempfile

        folder = FINAL / "POSTER/FINAL"
        pptx = folder / "M_RAG_A1_FINAL_EDITABLE.pptx"
        svg = (folder / "M_RAG_A1_FINAL_EDITABLE.svg").read_text("utf-8")
        cases = {
            "differs from TTEST_ANOVA_60Q": svg.replace(">0.029</text>", ">0.117</text>"),
            "Retired poster statistics wording": svg.replace(
                "p: 양측 p", "p: Holm 보정 p"
            ),
        }
        for message, mutated in cases.items():
            with self.subTest(message=message), tempfile.TemporaryDirectory() as d:
                self.assertNotEqual(mutated, svg)
                path = Path(d) / "poster.svg"
                path.write_text(mutated, "utf-8")
                with self.assertRaisesRegex(AssertionError, message):
                    validate_poster(pptx, path)

    def test_interleaved_protocol_is_rejected(self):
        with self.assertRaises(AssertionError):
            protocol_order(
                [f"H{h}C{c}S{s}" for h in (0, 1) for c in (0, 1) for s in (0, 1)]
            )

    def test_poster_abstract_is_optional(self):
        for heading in ["초록", "01 Abstract", "국문초록"]:
            with self.subTest(heading=heading):
                self.assertTrue(poster_headings([heading]))

    def test_background_is_allowed(self):
        poster_headings(["01 연구 배경과 목적", "08 주요 참고문헌"])

    def test_returned_abstract_is_rejected_in_thesis(self):
        text = (FINAL / "MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md").read_text(
            "utf-8"
        ) + "\n# 국문초록 [스타일=목차제목]\n"
        with self.assertRaises(AssertionError):
            validate_manuscript(
                text,
                json.loads((FINAL / "DATA/THESIS_TABLES_60Q.json").read_text("utf-8")),
            )
