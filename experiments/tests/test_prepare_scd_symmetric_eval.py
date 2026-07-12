import copy

import pytest

from experiments.evaluators.prepare_scd_symmetric_eval import (
    LOCKED_LITERAL_RE,
    NormalizationError,
    TextTask,
    _acquire_execution_lock,
    _load_selected_records,
    _is_validated_identity,
    _normalize_tasks_by_segments,
    _normalize_segment_with_retries,
    _parse_passages,
    _protect_integrity,
    _restore_integrity,
    _replace_context_chunks,
    _repair_combined_normalization,
    _release_execution_lock,
    _split_for_lossless_normalization,
    _validate_normalized,
)


class KoreanResponseModel:
    def invoke(self, _messages):
        return type(
            "Response",
            (),
            {
                "content": (
                    "[[1]]\n이것은 충분히 자세한 한국어 번역문이며 "
                    "원문의 내용을 그대로 보존합니다."
                )
            },
        )()


class AdaptiveEnglishResponseModel:
    def invoke(self, messages):
        prompt = messages[-1][1]
        passage = prompt.rsplit("[[1]]", 1)[-1].strip()
        output = (
            "번역되지 않은 긴 응답입니다."
            if len(passage) > 80
            else "A short English translation."
        )
        return type("Response", (), {"content": f"[[1]]\n{output}"})()


class ResidualHangulRepairModel:
    def invoke(self, messages):
        system_prompt = messages[0][1]
        prompt = messages[-1][1]
        passage = prompt.rsplit("[[1]]", 1)[-1].strip()
        if "still contains Hangul" in system_prompt:
            passage = passage.replace("번", "No.")
        return type("Response", (), {"content": f"[[1]]\n{passage}"})()


def test_parse_passages_requires_exact_order() -> None:
    assert _parse_passages("[[1]]\n하나\n[[2]]\n둘", 2) == ["하나", "둘"]
    with pytest.raises(NormalizationError, match="marker mismatch"):
        _parse_passages("[[2]]\n둘\n[[1]]\n하나", 2)


def test_validation_preserves_numbers_and_citations() -> None:
    task = TextTask("key", "answer", "ko", "Score 87.3% [12].")
    _validate_normalized(task, "점수는 87.3%이다 [12].")
    with pytest.raises(NormalizationError, match="number preservation"):
        _validate_normalized(task, "점수는 88.0%이다 [12].")


def test_validation_requires_target_language_dominance() -> None:
    english = TextTask("key-en", "question", "en", "질문입니다.")
    _validate_normalized(english, "This is a question.")
    with pytest.raises(NormalizationError, match="no Hangul"):
        _validate_normalized(english, "This is 질문.")

    korean = TextTask("key-ko", "answer", "ko", "This is a long answer.")
    _validate_normalized(korean, "이것은 충분히 자세한 한국어 답변입니다. API")
    with pytest.raises(NormalizationError, match="script ratio"):
        _validate_normalized(korean, "짧음 This is still mostly an English answer.")


def test_validated_identity_is_symmetric_and_fail_closed() -> None:
    assert _is_validated_identity(
        TextTask("en", "answer", "en", "Already English with 42 facts.")
    )
    assert _is_validated_identity(
        TextTask("ko", "answer", "ko", "이미 충분히 자연스러운 한국어 답변입니다.")
    )
    assert _is_validated_identity(
        TextTask(
            "ko-question",
            "question",
            "ko",
            "Mi:dm K 2.5 Pro 모델의 컨텍스트 윈도우(context window) 길이는 얼마인가요?",
        )
    )
    assert not _is_validated_identity(
        TextTask("translate", "answer", "en", "번역이 필요한 답변입니다.")
    )


def test_validation_rejects_long_untranslated_english_prose_span() -> None:
    task = TextTask("key-ko", "context", "ko", "source context")
    output = (
        "이 문장은 한국어이지만 충분한 문자 비율을 맞추기 위해 반복됩니다. " * 8
        + "This is a long section of English prose that should have been translated "
        "into Korean and it remains in the output with enough function words for "
        "the validator to identify the untranslated natural language passage."
    )
    with pytest.raises(NormalizationError, match="untranslated English prose"):
        _validate_normalized(task, output)


def test_answer_rejects_shorter_untranslated_english_quotation() -> None:
    task = TextTask("answer", "answer", "ko", "source answer")
    output = (
        "이 답변은 충분한 한국어 설명을 포함하고 있습니다. " * 6
        + '"CAD provides more reliable outputs for models of various sizes and tasks."'
    )
    with pytest.raises(NormalizationError, match="untranslated English prose"):
        _validate_normalized(task, output)


def test_answer_allows_number_dense_benchmark_row() -> None:
    output = (
        "이 답변은 표의 결과를 한국어로 충분히 설명하고 있습니다. " * 6
        + "LiveCodeBench V6 Solar-open-100B Off On 96.00 "
        "HyperCLOVAX-SEED-Think-32B Off On 95.00 "
        "Qwen-3-30B-A3B Off On 94.00 Mi:dm K 2.5 Pro 92.07"
    )
    task = TextTask("table", "answer", "ko", output)
    _validate_normalized(task, output)


def test_korean_segment_allows_acronym_heavy_fragment_but_parent_does_not() -> None:
    fragment = "- RGB, RECALL, CRUD [167]-[169] 등의 핵심"
    _validate_normalized(
        TextTask("segment", "answer_segment", "ko", fragment), fragment
    )
    with pytest.raises(NormalizationError, match="script ratio"):
        _validate_normalized(TextTask("parent", "answer", "ko", fragment), fragment)

    technical_only = "RGB RECALL CRUD [167]-[169]"
    _validate_normalized(
        TextTask("technical", "answer_segment", "ko", technical_only),
        technical_only,
    )
    with pytest.raises(NormalizationError, match="script ratio"):
        _validate_normalized(
            TextTask("technical-parent", "answer", "ko", technical_only),
            technical_only,
        )


def test_korean_segment_rejects_untranslated_bibliographic_title() -> None:
    fragment = (
        '[26] Jia, Y., et al. "Evaluation of Retrieval-Augmented Generation Models." '
        "arXiv:2305.06236 (2023)."
    )
    with pytest.raises(NormalizationError, match="bibliographic title"):
        _validate_normalized(
            TextTask("bibliography", "answer_segment", "ko", fragment), fragment
        )


def test_integrity_placeholders_round_trip_exact_tokens() -> None:
    source = "Scores 1978,1986 and 87.3% [12]."
    protected, mapping = _protect_integrity(source)
    assert list(mapping.values()) == ["1978,1986", "87.3%", "[12]"]
    assert _restore_integrity(source, f"번역: {protected}") == f"번역: {source}"


def test_integrity_placeholders_protect_circled_numbers() -> None:
    source = "① 1번 ② 2번 ⑦"
    protected, mapping = _protect_integrity(source)
    assert list(mapping.values()) == ["①", "1", "②", "2", "⑦"]
    assert _restore_integrity(source, protected) == source
    with pytest.raises(NormalizationError, match="circled-number preservation"):
        _validate_normalized(
            TextTask("key", "answer", "en", "① First option"),
            "First option",
        )


def test_integrity_placeholders_lock_month_names_that_could_add_numbers() -> None:
    source = "(Feb.’26) and March ‘26"
    protected, mapping = _protect_integrity(source)
    assert list(mapping.values()) == ["Feb.", "26", "March", "26"]
    assert not LOCKED_LITERAL_RE.findall("Models may suffer from prior bias.")
    assert not LOCKED_LITERAL_RE.findall("Market analysis and Marching orders.")
    assert _restore_integrity(source, protected) == source
    with pytest.raises(NormalizationError, match="locked-literal preservation"):
        _validate_normalized(
            TextTask("month", "answer", "en", source),
            "(February ’26) and March ‘26",
        )


def test_long_text_splits_on_safe_boundaries() -> None:
    source = ("첫 문장입니다. " * 100) + "\n\n마지막 문단입니다."
    parts = _split_for_lossless_normalization(source, max_chars=100)
    assert len(parts) > 2
    assert all(len(part) <= 100 for part in parts)
    assert all(part.strip() for part in parts)
    assert parts[-1].endswith("마지막 문단입니다.")


def test_many_short_paragraphs_are_packed_into_bounded_segments() -> None:
    source = "\n\n".join(f"짧은 문단 {index}." for index in range(40))
    parts = _split_for_lossless_normalization(source, max_chars=100)
    assert 1 < len(parts) < 40
    assert all(len(part) <= 100 for part in parts)
    assert "짧은 문단 0." in parts[0]
    assert "짧은 문단 39." in parts[-1]


def test_decimal_period_is_not_used_as_sentence_boundary() -> None:
    source = ("The gain was 5.5 percent in this benchmark. " * 30).strip()
    parts = _split_for_lossless_normalization(source, max_chars=120)
    assert all("5.\n\n5" not in part for part in parts)
    assert sum(part.count("5.5") for part in parts) == 30


def test_long_boundary_free_sentence_splits_only_at_whitespace() -> None:
    source = " ".join(f"token{index}" for index in range(100))
    parts = _split_for_lossless_normalization(source, max_chars=80)
    assert len(parts) > 2
    assert all(len(part) <= 80 for part in parts)
    assert " ".join(parts).split() == source.split()


def test_number_dense_table_respects_integrity_budget() -> None:
    source = "Model " + " ".join(f"{index}.0" for index in range(100))
    parts = _split_for_lossless_normalization(
        source, max_chars=900, max_integrity_tokens=10
    )
    assert len(parts) == 10
    assert all(len(__import__("re").findall(r"\d+\.\d+", part)) <= 10 for part in parts)
    assert (
        sum(len(__import__("re").findall(r"\d+\.\d+", part)) for part in parts) == 100
    )


def test_segment_fallback_keeps_base_kind_for_language_validation() -> None:
    task = TextTask("parent", "answer", "ko", "word " * 400)
    result = _normalize_tasks_by_segments(KoreanResponseModel(), [task], 0)
    assert result["parent"].count("한국어 번역문") > 1


def test_combined_repair_revalidates_against_original_parent() -> None:
    task = TextTask("parent", "answer", "ko", "English prose that needs translation.")
    repaired = _repair_combined_normalization(
        KoreanResponseModel(), task, task.source, max_retries=0
    )
    _validate_normalized(task, repaired)


def test_adaptive_segment_fallback_subdivides_validation_failures() -> None:
    task = TextTask("parent", "answer", "en", "긴 한국어 문장 " * 30)
    result = _normalize_segment_with_retries(
        AdaptiveEnglishResponseModel(), task, max_retries=0
    )
    assert "A short English translation." in result
    assert not any(0xAC00 <= ord(char) <= 0xD7A3 for char in result)


def test_residual_hangul_repair_preserves_protected_option_symbols() -> None:
    task = TextTask("parent", "answer", "en", "① 1번 ② 2번 ⑦")
    result = _normalize_segment_with_retries(
        ResidualHangulRepairModel(), task, max_retries=0
    )
    assert result == "① 1No. ② 2No. ⑦"


def test_selected_records_reject_context_mismatch(tmp_path) -> None:
    records = []
    for query_index in range(19):
        query_id = f"q{query_index}"
        for config, use_cad, use_scd in (
            ("hyde_off__no_decoder_control", False, False),
            ("hyde_off__cad_only", True, False),
            ("hyde_off__scd_only", False, True),
            ("hyde_off__cad_scd", True, True),
        ):
            records.append(
                {
                    "query_id": query_id,
                    "query": "질문",
                    "generated_answer": "답변",
                    "contexts": ["same"],
                    "config_name": config,
                    "use_hyde": False,
                    "use_cad": use_cad,
                    "use_scd": use_scd,
                    "experiment": "main-hyde-cad-scd-reference-scd",
                    "generation_model": "K-intelligence/Midm-2.0-Base-Instruct",
                    "phase": "main_hyde_cad_scd_generation",
                    "decoding_mode": "deterministic_greedy",
                    "status": "succeeded",
                    "error": None,
                    "fallback_used": False,
                    "decoder_main_used": True,
                    "cad_alpha": 0.5 if use_cad else None,
                    "scd_mode": "reference_scd" if use_scd else None,
                    "scd_variant": (
                        "raw_logit_multiplicative_reference" if use_scd else None
                    ),
                    "scd_reference_formula_applied": True if use_scd else None,
                    "scd_project_whitelist_used": False if use_scd else None,
                }
            )
    broken = copy.deepcopy(records)
    broken[2]["contexts"] = ["different"]
    path = tmp_path / "records.jsonl"
    path.write_text(
        "\n".join(__import__("json").dumps(row) for row in broken),
        encoding="utf-8",
    )
    with pytest.raises(NormalizationError, match="context mismatch"):
        _load_selected_records(path)


def test_selected_records_reject_noncanonical_scd_provenance(tmp_path) -> None:
    records = []
    for query_index in range(19):
        query_id = f"q{query_index}"
        for config, use_cad, use_scd in (
            ("hyde_off__no_decoder_control", False, False),
            ("hyde_off__cad_only", True, False),
            ("hyde_off__scd_only", False, True),
            ("hyde_off__cad_scd", True, True),
        ):
            records.append(
                {
                    "query_id": query_id,
                    "query": "질문",
                    "generated_answer": "답변",
                    "contexts": ["same"],
                    "config_name": config,
                    "use_hyde": False,
                    "use_cad": use_cad,
                    "use_scd": use_scd,
                    "experiment": "main-hyde-cad-scd-reference-scd",
                    "generation_model": "K-intelligence/Midm-2.0-Base-Instruct",
                    "phase": "main_hyde_cad_scd_generation",
                    "decoding_mode": "deterministic_greedy",
                    "status": "succeeded",
                    "error": None,
                    "fallback_used": False,
                    "decoder_main_used": True,
                    "cad_alpha": 0.5 if use_cad else None,
                    "scd_mode": "penalty_additive" if use_scd else None,
                    "scd_variant": (
                        "raw_logit_multiplicative_reference" if use_scd else None
                    ),
                    "scd_reference_formula_applied": True if use_scd else None,
                    "scd_project_whitelist_used": False if use_scd else None,
                }
            )
    path = tmp_path / "records.jsonl"
    path.write_text(
        "\n".join(__import__("json").dumps(row) for row in records),
        encoding="utf-8",
    )
    with pytest.raises(NormalizationError, match="scd_mode"):
        _load_selected_records(path)


def test_context_projection_updates_content_and_snippet() -> None:
    record = {
        "query_id": "q1",
        "config_name": "hyde_off__scd_only",
        "context": {"chunks": [{"content": "English full", "snippet": "English"}]},
    }
    _replace_context_chunks(record, ["한국어 전체 문맥"])
    chunk = record["context"]["chunks"][0]
    assert chunk["content"] == "한국어 전체 문맥"
    assert chunk["snippet"] == "한국어 전체 문맥"[: len("English")]


def test_execution_lock_refuses_concurrent_writer(tmp_path) -> None:
    first = _acquire_execution_lock(tmp_path)
    try:
        with pytest.raises(NormalizationError, match="another symmetric"):
            _acquire_execution_lock(tmp_path)
    finally:
        _release_execution_lock(first)
    second = _acquire_execution_lock(tmp_path)
    _release_execution_lock(second)
