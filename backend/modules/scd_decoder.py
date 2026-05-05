"""
MODULE 13B: Korean-target Soft Constrained Decoding.

SCD applies a soft beta penalty to non-target-language tokens while preserving
Korean tokens, neutral symbols, numbers, citations, and whitelisted technical
terms that are common in paper QA.
"""

import logging

import torch
from transformers import LogitsProcessor, LogitsProcessorList

from config import SCD_BETA, SCD_TARGET_LANG

logger = logging.getLogger(__name__)

TECHNICAL_TERM_WHITELIST = (
    "RAG",
    "CAD",
    "SCD",
    "BM25",
    "RRF",
    "BGE-M3",
    "HyDE",
    "RAGAS",
    "Transformer",
    "CrossEncoder",
    "Mi:dm",
    "arXiv",
    "DOI",
    "BERT",
    "RoBERTa",
    "LLaMA",
    "GPT",
    "FLAN",
    "XSUM",
    "CNN-DM",
)

NEUTRAL_CHARS = frozenset(
    " \n\t\r"
    ".,!?;:\"'`"
    "()[]{}<>"
    "-_+/\\|"
    "0123456789"
    "%‰°"
    "=≈≠<>≤≥±×÷∑∏√∞∂∆∇"
    "·…•"
    "#@$&*^~"
)


class SCDDecoder(LogitsProcessor):
    """Korean-target Soft Constrained Decoding.

    This is Korean-only for the thesis. Full multilingual SCD is future work.
    """

    def __init__(
        self,
        tokenizer,
        target_lang: str = SCD_TARGET_LANG,
        beta: float = SCD_BETA,
        technical_terms: tuple[str, ...] = TECHNICAL_TERM_WHITELIST,
    ):
        if target_lang != "ko":
            raise ValueError(
                "This SCD implementation is Korean-target only; "
                "full multilingual SCD is future work."
            )
        self.tokenizer = tokenizer
        self.target_lang = target_lang
        self.beta = beta
        self.technical_terms = technical_terms
        self._non_target_ids: torch.Tensor | None = None
        self._whitelist_ids: set[int] | None = None
        self.metadata = {
            "mode": "Korean-target Soft Constrained Decoding",
            "target_lang": self.target_lang,
            "beta": self.beta,
            "technical_term_whitelist": list(self.technical_terms),
            "neutral_policy": "whitespace, punctuation, numbers, math symbols, citation markers, brackets, academic symbols",
            "penalized_token_count": None,
        }

    def _build_non_target_ids(self, device: torch.device) -> torch.Tensor:
        """비목표 언어 토큰 ID 집합 구축 (첫 호출 시 1회만 실행)"""
        non_target = []
        vocab_size = self.tokenizer.vocab_size
        whitelist_ids = self._build_whitelist_ids()
        for token_id in range(vocab_size):
            if token_id in getattr(self.tokenizer, "all_special_ids", []):
                continue
            token = self._decode_token(token_id)
            if token and not self._is_allowed_token(token_id, token, whitelist_ids):
                non_target.append(token_id)
        self.metadata["penalized_token_count"] = len(non_target)
        if non_target:
            return torch.tensor(non_target, dtype=torch.long, device=device)
        return torch.empty(0, dtype=torch.long, device=device)

    def _build_whitelist_ids(self) -> set[int]:
        """Token IDs for mandatory technical terms and common spacing variants."""
        if self._whitelist_ids is not None:
            return self._whitelist_ids

        whitelist_ids: set[int] = set()
        for term in self.technical_terms:
            for variant in (term, f" {term}", f"({term}", f"/{term}"):
                try:
                    tokenized = self.tokenizer(
                        variant,
                        add_special_tokens=False,
                    )
                except Exception:
                    continue
                ids = tokenized.get("input_ids", [])
                if ids and isinstance(ids[0], list):
                    ids = ids[0]
                whitelist_ids.update(int(token_id) for token_id in ids)

        self._whitelist_ids = whitelist_ids
        return whitelist_ids

    def _decode_token(self, token_id: int) -> str:
        try:
            return self.tokenizer.decode(
                [token_id],
                skip_special_tokens=False,
                clean_up_tokenization_spaces=False,
            )
        except TypeError:
            return self.tokenizer.decode([token_id])

    def _normalize_token(self, token: str) -> str:
        normalized = token.replace("##", "")
        normalized = normalized.replace("▁", " ")
        normalized = normalized.replace("Ġ", " ")
        normalized = normalized.replace("Ċ", "\n")
        return normalized.strip()

    def _is_allowed_token(
        self,
        token_id: int,
        token: str,
        whitelist_ids: set[int],
    ) -> bool:
        if token_id in whitelist_ids:
            return True

        normalized = self._normalize_token(token)
        if not normalized:
            return True

        lowered = normalized.casefold()
        whitelist_terms = {term.casefold() for term in self.technical_terms}
        if lowered in whitelist_terms:
            return True

        has_hangul = False
        for ch in normalized:
            if self._is_hangul(ch):
                has_hangul = True
                continue
            if not self._is_neutral_char(ch):
                return False
        return has_hangul or all(self._is_neutral_char(ch) for ch in normalized)

    @staticmethod
    def _is_hangul(ch: str) -> bool:
        code = ord(ch)
        return (
            0xAC00 <= code <= 0xD7A3  # 한글 음절 (가-힣)
            or 0x1100 <= code <= 0x11FF  # 한글 자모
            or 0x3130 <= code <= 0x318F  # 호환 자모
        )

    @staticmethod
    def _is_neutral_char(ch: str) -> bool:
        if ch in NEUTRAL_CHARS:
            return True
        # Treat additional Unicode punctuation/symbol ranges as neutral.
        code = ord(ch)
        return (
            0x2000 <= code <= 0x206F
            or 0x2070 <= code <= 0x209F
            or 0x2190 <= code <= 0x21FF
            or 0x2200 <= code <= 0x22FF
            or 0x3000 <= code <= 0x303F
        )

    def _is_target_or_common(self, token: str) -> bool:
        """Backward-compatible policy helper for existing tests."""
        return self._is_allowed_token(-1, token, set())

    def get_metadata(self) -> dict:
        """Expose decoder metadata for later evaluator adapters."""
        return dict(self.metadata)

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        """Apply beta penalty to non-target token logits."""
        if self._non_target_ids is None:
            self._non_target_ids = self._build_non_target_ids(scores.device)
        elif self._non_target_ids.device != scores.device:
            self._non_target_ids = self._non_target_ids.to(scores.device)

        if len(self._non_target_ids) > 0:
            scores[:, self._non_target_ids] -= self.beta

        return scores

    def _legacy_is_target_or_common(self, token: str) -> bool:
        """Deprecated helper retained only to avoid external test breakage."""
        for ch in token:
            if not (self._is_hangul(ch) or self._is_neutral_char(ch)):
                return False
        return True


def create_scd_processor(
    tokenizer,
    beta: float = SCD_BETA,
    target_lang: str = SCD_TARGET_LANG,
) -> LogitsProcessorList:
    """SCD LogitsProcessor 생성 헬퍼"""
    scd = SCDDecoder(
        tokenizer=tokenizer,
        target_lang=target_lang,
        beta=beta,
    )
    return LogitsProcessorList([scd])


def create_combined_processor(
    generator,
    query: str,
    use_cad: bool = True,
    cad_alpha: float = 0.5,
    use_scd: bool = True,
    scd_beta: float = SCD_BETA,
    cad_adaptive: bool = False,
) -> LogitsProcessorList:
    """Create CAD + Korean-target SCD processors.

    1. CAD: exact context-aware scoring
       `(1 + alpha) * context_scores - alpha * no_context_scores`
    2. SCD: beta penalty for non-Korean/non-neutral/non-whitelisted tokens
    """
    from modules.cad_decoder import CADDecoder

    processors = []

    if use_cad:
        empty_inputs = generator.get_empty_context_inputs(query)
        cad = CADDecoder(
            model=generator.model,
            tokenizer=generator.tokenizer,
            empty_input_ids=empty_inputs["input_ids"],
            empty_attention_mask=empty_inputs.get("attention_mask"),
            alpha=cad_alpha,
            adaptive=cad_adaptive,
        )
        processors.append(cad)

    if use_scd:
        scd = SCDDecoder(
            tokenizer=generator.tokenizer,
            beta=scd_beta,
        )
        processors.append(scd)

    return LogitsProcessorList(processors)
