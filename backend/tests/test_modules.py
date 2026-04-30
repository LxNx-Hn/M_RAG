import pytest
import torch

from modules.query_router import QueryRouter, RouteType
from modules.scd_decoder import SCDDecoder


class MockTokenizer:
    def __init__(self):
        self.vocab_size = 1000

    def decode(self, token_ids):
        # Return Korean for some tokens, English for others
        if isinstance(token_ids, list):
            token_id = token_ids[0]
        else:
            token_id = token_ids
        if token_id < 100:
            return "가"
        elif token_id < 200:
            return "a"
        return "1"


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


def test_scd_decoder_is_korean(mock_tokenizer):
    scd = SCDDecoder(tokenizer=mock_tokenizer, target_lang="ko", beta=0.3)
    # Valid Korean/Common tokens
    assert scd._is_target_or_common("가")
    assert scd._is_target_or_common("ㄱ")
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
