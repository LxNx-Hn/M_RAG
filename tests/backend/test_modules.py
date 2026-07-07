import math

import pytest
import torch

from modules.query_router import QueryRouter, RouteType
from modules.query_expander import QueryExpander
from modules.scd_decoder import (
    SCDDecoder,
    create_combined_processor,
    create_scd_processor,
    extract_scd_metadata,
)


class MockTokenizer:
    def __init__(self):
        self.vocab_size = 1000
        self.all_special_ids = [999]

    def decode(self, token_ids):
        # Return Korean for some tokens, English for others
        if isinstance(token_ids, list):
            token_id = token_ids[0]
        else:
            token_id = token_ids
        if token_id == 350:
            return "RAG"
        if token_id < 100:
            return "가"
        elif token_id < 200:
            return "a"
        return "1"

    def __call__(self, text, add_special_tokens=False):
        del add_special_tokens
        term_ids = {
            "RAG": 350,
            " RAG": 350,
            "(RAG": 350,
            "/RAG": 350,
        }
        return (
            {"input_ids": [term_ids[text]]} if text in term_ids else {"input_ids": []}
        )


class MockGenerator:
    def __init__(self, tokenizer):
        self.model = object()
        self.tokenizer = tokenizer

    def get_empty_context_inputs(self, query):
        del query
        return {
            "input_ids": torch.ones((1, 3), dtype=torch.long),
            "attention_mask": torch.ones((1, 3), dtype=torch.long),
        }


class MockTextGenerator:
    model_name = "mock-model"
    max_new_tokens = 123

    def generate_simple(self, prompt):
        if "Translate the following Korean academic question" in prompt:
            return "translated question"
        return "hypothetical HyDE passage"


@pytest.fixture(scope="module")
def mock_tokenizer():
    return MockTokenizer()


def test_query_router_section():
    router = QueryRouter()
    # Test keywords that should route to section
    decision = router.route("이 논문의 방법론은 무엇인가요?", ["doc1"])
    assert decision.route == RouteType.SECTION
    assert decision.section_filter == "method"

    decision = router.route("실험 결과를 알려줘", ["doc1"])
    assert decision.route == RouteType.SECTION
    assert decision.section_filter == "result"


def test_query_router_compare():
    router = QueryRouter()
    decision = router.route("doc1과 doc2를 비교해줘", ["doc1", "doc2"])
    assert decision.route == RouteType.COMPARE
    assert len(decision.target_doc_ids) == 2


def test_query_expander_records_hyde_provenance():
    expander = QueryExpander(MockTextGenerator())
    expansion = expander.expand(
        "한국어 질문",
        use_hyde=True,
        use_multi=False,
        corpus_lang="en",
    )

    assert expansion["translated"] == "translated question"
    assert expansion["hyde_query"] == "translated question"
    assert expansion["hyde_doc"] == "hypothetical HyDE passage"
    assert expansion["hyde_corpus_lang"] == "en"
    assert expansion["hyde_generation_settings"]["method"] == "generate_simple"
    assert expansion["hyde_generation_settings"]["model_name"] == "mock-model"
    assert expansion["hyde_generation_settings"]["max_new_tokens"] == 123
    assert expansion["hyde_generation_settings"]["temperature"] == pytest.approx(0.1)
    assert expansion["hyde_generation_settings"]["top_p"] == pytest.approx(0.9)
    assert expansion["hyde_generation_settings"]["do_sample"]
    assert not expansion["hyde_generation_settings"]["force_greedy"]


def test_scd_decoder_is_korean(mock_tokenizer):
    scd = SCDDecoder(tokenizer=mock_tokenizer, target_lang="ko", beta=0.3)
    # Valid Korean/Common tokens
    assert scd._is_target_or_common("가")
    assert scd._is_target_or_common("ㄱ")
    assert scd._is_target_or_common("\ua960")
    assert scd._is_target_or_common("\ud7b0")
    assert scd._is_target_or_common("\uffa1")
    assert scd._is_target_or_common(" ")
    assert scd._is_target_or_common("1")
    assert scd._is_target_or_common(".")

    # Invalid (should be suppressed by SCD)
    assert not scd._is_target_or_common("a")
    assert not scd._is_target_or_common("A")
    assert not scd._is_target_or_common("α")


def test_scd_decoder_logit_penalty(mock_tokenizer):
    scd = SCDDecoder(tokenizer=mock_tokenizer, target_lang="ko", beta=0.5)

    # Mock logits (batch_size=1, vocab_size=mock_tokenizer.vocab_size)
    vocab_size = mock_tokenizer.vocab_size
    scores = torch.zeros((1, vocab_size))

    # Apply SCD
    processed_scores = scd(input_ids=torch.tensor([[1]]), scores=scores.clone())

    # Check that non-Korean tokens have penalty applied
    non_target_ids = scd._non_target_ids
    assert len(non_target_ids) > 0
    # Score should be exactly -0.5 (0 - beta)
    assert processed_scores[0, non_target_ids[0]].item() == -0.5


def test_scd_reference_scd_uses_generated_token_warmup(mock_tokenizer):
    scd = SCDDecoder(
        tokenizer=mock_tokenizer,
        target_lang="ko",
        alpha=1.1,
        beta=0.9,
        t_start=2,
        mode="reference_scd",
    )
    scores = torch.ones((1, mock_tokenizer.vocab_size))

    # First call records the prompt length; no generated tokens yet.
    first = scd(input_ids=torch.ones((1, 5), dtype=torch.long), scores=scores.clone())
    assert first[0, 1].item() == pytest.approx(1.0)
    assert first[0, 150].item() == pytest.approx(1.0)

    # One generated token is still inside the warm-up window.
    second = scd(input_ids=torch.ones((1, 6), dtype=torch.long), scores=scores.clone())
    assert second[0, 1].item() == pytest.approx(1.0)
    assert second[0, 150].item() == pytest.approx(1.0)

    # Two generated tokens activates constraints.
    third = scd(input_ids=torch.ones((1, 7), dtype=torch.long), scores=scores.clone())
    assert third[0, 1].item() == pytest.approx(1.1)
    assert third[0, 150].item() == pytest.approx(0.9)
    assert third[0, 250].item() == pytest.approx(1.0)


def test_scd_reference_scd_applies_literal_negative_logit_scaling(mock_tokenizer):
    scd = SCDDecoder(
        tokenizer=mock_tokenizer,
        target_lang="ko",
        alpha=1.1,
        beta=0.9,
        t_start=0,
        mode="reference_scd",
    )
    scores = torch.full((1, mock_tokenizer.vocab_size), 2.0)
    scores[0, 1] = -2.0
    scores[0, 150] = -2.0
    scores[0, 250] = -2.0

    processed = scd(
        input_ids=torch.ones((1, 5), dtype=torch.long), scores=scores.clone()
    )

    assert processed[0, 1].item() == pytest.approx(-2.2)
    assert processed[0, 150].item() == pytest.approx(-1.8)
    assert processed[0, 250].item() == pytest.approx(-2.0)


def test_scd_reference_scd_positive_logits_and_neutral(mock_tokenizer):
    scd = SCDDecoder(
        tokenizer=mock_tokenizer,
        target_lang="ko",
        alpha=1.1,
        beta=0.9,
        t_start=0,
        mode="reference_scd",
    )
    scores = torch.full((1, mock_tokenizer.vocab_size), 2.0)

    processed = scd(
        input_ids=torch.ones((1, 5), dtype=torch.long), scores=scores.clone()
    )

    assert processed[0, 1].item() == pytest.approx(2.2)
    assert processed[0, 150].item() == pytest.approx(1.8)
    assert processed[0, 250].item() == pytest.approx(2.0)


def test_scd_prob_scale_logit_offset_is_not_reference_scd(mock_tokenizer):
    scd = SCDDecoder(
        tokenizer=mock_tokenizer,
        target_lang="ko",
        alpha=1.1,
        beta=0.9,
        t_start=0,
        mode="prob_scale_logit_offset",
    )
    scores = torch.zeros((1, mock_tokenizer.vocab_size))
    scores[0, 1] = -2.0
    scores[0, 150] = -2.0
    scores[0, 250] = -2.0

    processed = scd(
        input_ids=torch.ones((1, 5), dtype=torch.long), scores=scores.clone()
    )
    metadata = scd.get_metadata()

    assert processed[0, 1].item() == pytest.approx(scores[0, 1].item() + math.log(1.1))
    assert processed[0, 150].item() == pytest.approx(
        scores[0, 150].item() + math.log(0.9)
    )
    assert processed[0, 250].item() == pytest.approx(scores[0, 250].item())
    assert metadata["scd_mode"] == "prob_scale_logit_offset"
    assert not metadata["scd_reference_formula_applied"]


def test_scd_reference_scd_does_not_use_project_whitelist(mock_tokenizer):
    legacy = SCDDecoder(tokenizer=mock_tokenizer, target_lang="ko", beta=0.5)
    reference = SCDDecoder(
        tokenizer=mock_tokenizer,
        target_lang="ko",
        alpha=1.1,
        beta=0.9,
        t_start=0,
        mode="reference_scd",
    )
    scores = torch.ones((1, mock_tokenizer.vocab_size))

    legacy_processed = legacy(
        input_ids=torch.ones((1, 5), dtype=torch.long), scores=scores.clone()
    )
    reference_processed = reference(
        input_ids=torch.ones((1, 5), dtype=torch.long), scores=scores.clone()
    )

    assert legacy_processed[0, 350].item() == pytest.approx(1.0)
    assert legacy.get_metadata()["scd_project_whitelist_used"]
    assert reference_processed[0, 350].item() == pytest.approx(0.9)
    assert not reference.get_metadata()["scd_project_whitelist_used"]


def test_scd_reference_scd_metadata(mock_tokenizer):
    scd = SCDDecoder(
        tokenizer=mock_tokenizer,
        target_lang="ko",
        alpha=1.1,
        beta=0.9,
        mode="reference_scd",
    )
    _ = scd(
        input_ids=torch.ones((1, 5), dtype=torch.long), scores=torch.ones((1, 1000))
    )
    metadata = scd.get_metadata()

    assert metadata["scd_mode"] == "reference_scd"
    assert metadata["scd_variant"] == "raw_logit_multiplicative_reference"
    assert metadata["scd_reference_formula_applied"]
    assert not metadata["scd_project_whitelist_used"]
    assert metadata["scd_warmup_basis"] == "generated_token_count"
    assert metadata["scd_vocab_partition"]["target_count"] > 0
    assert metadata["scd_vocab_partition"]["neutral_count"] > 0
    assert metadata["scd_vocab_partition"]["distractor_count"] > 0


def test_scd_mode_defaults_by_variant(mock_tokenizer):
    legacy = SCDDecoder(tokenizer=mock_tokenizer, target_lang="ko")
    reference = SCDDecoder(
        tokenizer=mock_tokenizer,
        target_lang="ko",
        mode="reference_scd",
    )
    offset = SCDDecoder(
        tokenizer=mock_tokenizer,
        target_lang="ko",
        mode="prob_scale_logit_offset",
    )

    assert legacy.get_metadata()["scd_beta"] == pytest.approx(0.3)
    assert legacy.get_metadata()["scd_t_start"] == 0
    assert reference.get_metadata()["scd_beta"] == pytest.approx(0.9)
    assert reference.get_metadata()["scd_t_start"] == 5
    assert offset.get_metadata()["scd_beta"] == pytest.approx(0.9)
    assert offset.get_metadata()["scd_t_start"] == 5


def test_extract_scd_metadata_from_processor_list(mock_tokenizer):
    processors = create_scd_processor(
        tokenizer=mock_tokenizer,
        mode="reference_scd",
    )
    metadata = extract_scd_metadata(processors)

    assert metadata["scd_mode"] == "reference_scd"
    assert metadata["scd_variant"] == "raw_logit_multiplicative_reference"
    assert metadata["scd_beta"] == pytest.approx(0.9)
    assert metadata["scd_t_start"] == 5
    assert metadata["scd_warmup_basis"] == "generated_token_count"
    assert metadata["scd_reference_formula_applied"]
    assert not metadata["scd_project_whitelist_used"]
    assert metadata["scd_vocab_partition"]["target_count"] > 0


def test_combined_processor_records_cad_scd_order(mock_tokenizer):
    processors = create_combined_processor(
        generator=MockGenerator(mock_tokenizer),
        query="RAG가 무엇인가요?",
        use_cad=True,
        use_scd=True,
        scd_mode="reference_scd",
    )
    metadata = extract_scd_metadata(processors)

    assert metadata["scd_processor_order"] == "CADDecoder -> SCDDecoder"
