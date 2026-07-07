"""
MODULE 13B: Korean-target Soft Constrained Decoding.

The default mode is the Phase 8 terminology-preserving variant: it applies a
small additive beta penalty to non-target-language tokens while preserving
Korean tokens, neutral symbols, numbers, citations, and whitelisted technical
terms that are common in paper QA.

Additional modes are available for corrective SCD experiments, but they are
opt-in so existing service behavior and Phase 8 provenance remain reproducible.
"""

import logging
import math

import torch
from transformers import LogitsProcessor, LogitsProcessorList

from config import SCD_BETA, SCD_TARGET_LANG

logger = logging.getLogger(__name__)

SCD_MODE_PENALTY_ADDITIVE = "penalty_additive"
SCD_MODE_REFERENCE_SCD = "reference_scd"
SCD_MODE_PROB_SCALE_LOGIT_OFFSET = "prob_scale_logit_offset"
SCD_MODES = frozenset(
    {
        SCD_MODE_PENALTY_ADDITIVE,
        SCD_MODE_REFERENCE_SCD,
        SCD_MODE_PROB_SCALE_LOGIT_OFFSET,
    }
)
SCD_DEFAULT_ALPHA = 1.1
SCD_REFERENCE_BETA = 0.9
SCD_REFERENCE_T_START = 5
SCD_VARIANTS = {
    SCD_MODE_PENALTY_ADDITIVE: "penalty_additive_v1",
    SCD_MODE_REFERENCE_SCD: "raw_logit_multiplicative_reference",
    SCD_MODE_PROB_SCALE_LOGIT_OFFSET: "probability_scale_logit_offset_experimental",
}

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

    Modes:
    - penalty_additive: Phase 8 application variant, ``distractor -= beta``.
    - reference_scd: original-paper raw-logit scaling, ``target *= alpha`` and
      ``distractor *= beta`` after warm-up. It deliberately applies the formula
      literally, including on negative logits.
    - prob_scale_logit_offset: probability-prior engineering alternative,
      ``target += log(alpha)`` and ``distractor += log(beta)`` after warm-up.
      This is not the original-paper SCD formula.

    This remains Korean-only for the thesis. Full multilingual SCD is future
    work.
    """

    def __init__(
        self,
        tokenizer,
        target_lang: str = SCD_TARGET_LANG,
        beta: float | None = None,
        alpha: float = SCD_DEFAULT_ALPHA,
        t_start: int | None = None,
        mode: str = SCD_MODE_PENALTY_ADDITIVE,
        technical_terms: tuple[str, ...] = TECHNICAL_TERM_WHITELIST,
    ):
        if target_lang != "ko":
            raise ValueError(
                "This SCD implementation is Korean-target only; "
                "full multilingual SCD is future work."
            )
        if mode not in SCD_MODES:
            raise ValueError(f"unsupported SCD mode: {mode!r}")
        if beta is None:
            beta = SCD_BETA if mode == SCD_MODE_PENALTY_ADDITIVE else SCD_REFERENCE_BETA
        if t_start is None:
            t_start = 0 if mode == SCD_MODE_PENALTY_ADDITIVE else SCD_REFERENCE_T_START
        if t_start < 0:
            raise ValueError("t_start must be >= 0")
        if mode == SCD_MODE_PENALTY_ADDITIVE and beta < 0:
            raise ValueError("additive SCD beta must be >= 0")
        if mode in {SCD_MODE_REFERENCE_SCD, SCD_MODE_PROB_SCALE_LOGIT_OFFSET}:
            if alpha <= 0:
                raise ValueError("SCD alpha must be > 0")
            if beta <= 0:
                raise ValueError("SCD beta must be > 0")
        self.tokenizer = tokenizer
        self.target_lang = target_lang
        self.beta = beta
        self.alpha = alpha
        self.t_start = int(t_start)
        self.mode = mode
        self.technical_terms = technical_terms
        self.scd_project_whitelist_used = self.mode != SCD_MODE_REFERENCE_SCD and bool(
            self.technical_terms
        )
        self._non_target_ids: torch.Tensor | None = None
        self._target_ids: torch.Tensor | None = None
        self._whitelist_ids: set[int] | None = None
        self._prompt_length: int | None = None
        self.metadata = {
            "mode": "Korean-target Soft Constrained Decoding",
            "adjustment_mode": self.mode,
            "scd_mode": self.mode,
            "scd_variant": SCD_VARIANTS[self.mode],
            "target_lang": self.target_lang,
            "alpha": self.alpha,
            "beta": self.beta,
            "t_start": self.t_start,
            "scd_alpha": self.alpha,
            "scd_beta": self.beta,
            "scd_t_start": self.t_start,
            "scd_warmup_basis": "generated_token_count",
            "scd_reference_formula_applied": self.mode == SCD_MODE_REFERENCE_SCD,
            "scd_project_whitelist_used": self.scd_project_whitelist_used,
            "scd_processor_order": "SCDDecoder",
            "technical_term_whitelist": list(self.technical_terms),
            "neutral_policy": "whitespace, punctuation, numbers, math symbols, citation markers, brackets, academic symbols",
            "scd_vocab_partition": {
                "target_count": None,
                "neutral_count": None,
                "distractor_count": None,
            },
            "target_token_count": None,
            "penalized_token_count": None,
            "neutral_or_whitelist_token_count": None,
        }

    def _build_non_target_ids(self, device: torch.device) -> torch.Tensor:
        """비목표 언어 토큰 ID 집합 구축 (첫 호출 시 1회만 실행)"""
        self._ensure_token_sets(device)
        if self._non_target_ids is None:
            return torch.empty(0, dtype=torch.long, device=device)
        return self._non_target_ids

    def _ensure_token_sets(self, device: torch.device) -> None:
        if (
            self._target_ids is not None
            and self._non_target_ids is not None
            and self._target_ids.device == device
            and self._non_target_ids.device == device
        ):
            return

        target = []
        non_target = []
        neutral = 0
        vocab_size = self.tokenizer.vocab_size
        whitelist_ids = (
            self._build_whitelist_ids() if self.scd_project_whitelist_used else set()
        )
        for token_id in range(vocab_size):
            if token_id in getattr(self.tokenizer, "all_special_ids", []):
                neutral += 1
                continue
            token = self._decode_token(token_id)
            token_class = self._classify_token(token_id, token, whitelist_ids)
            if token_class == "target":
                target.append(token_id)
            elif token_class == "distractor":
                non_target.append(token_id)
            else:
                neutral += 1
        self.metadata["target_token_count"] = len(target)
        self.metadata["penalized_token_count"] = len(non_target)
        self.metadata["neutral_or_whitelist_token_count"] = neutral
        self.metadata["scd_vocab_partition"] = {
            "target_count": len(target),
            "neutral_count": neutral,
            "distractor_count": len(non_target),
        }
        self._target_ids = (
            torch.tensor(target, dtype=torch.long, device=device)
            if target
            else torch.empty(0, dtype=torch.long, device=device)
        )
        self._non_target_ids = (
            torch.tensor(non_target, dtype=torch.long, device=device)
            if non_target
            else torch.empty(0, dtype=torch.long, device=device)
        )

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
        return self._classify_token(token_id, token, whitelist_ids) != "distractor"

    def _classify_token(
        self,
        token_id: int,
        token: str,
        whitelist_ids: set[int],
    ) -> str:
        """Classify a token as target, neutral, or distractor."""
        if token_id in whitelist_ids:
            return "neutral"

        normalized = self._normalize_token(token)
        if not normalized:
            return "neutral"

        lowered = normalized.casefold()
        if self.scd_project_whitelist_used:
            whitelist_terms = {term.casefold() for term in self.technical_terms}
            if lowered in whitelist_terms:
                return "neutral"

        has_hangul = False
        has_non_neutral = False
        for ch in normalized:
            if self._is_hangul(ch):
                has_hangul = True
                has_non_neutral = True
                continue
            if not self._is_neutral_char(ch):
                return "distractor"
        if has_hangul:
            return "target"
        if not has_non_neutral:
            return "neutral"
        return "neutral"

    @staticmethod
    def _is_hangul(ch: str) -> bool:
        code = ord(ch)
        return (
            0xAC00 <= code <= 0xD7A3  # 한글 음절 (가-힣)
            or 0x1100 <= code <= 0x11FF  # 한글 자모
            or 0x3130 <= code <= 0x318F  # 호환 자모
            or 0xA960 <= code <= 0xA97F  # 한글 자모 확장-A
            or 0xD7B0 <= code <= 0xD7FF  # 한글 자모 확장-B
            or 0xFFA0 <= code <= 0xFFDC  # 반각 한글
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
        partition = self.metadata.get("scd_vocab_partition", {})
        if partition.get("target_count") is None:
            self._ensure_token_sets(torch.device("cpu"))
        return dict(self.metadata)

    def _generated_token_count(self, input_ids: torch.LongTensor) -> int:
        current_length = int(input_ids.shape[-1])
        if self._prompt_length is None:
            self._prompt_length = current_length
            self.metadata["prompt_length"] = self._prompt_length
        return max(0, current_length - self._prompt_length)

    def _constraints_active(self, input_ids: torch.LongTensor) -> bool:
        return self._generated_token_count(input_ids) >= self.t_start

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        """Apply the configured Korean-target SCD logit adjustment."""
        if not self._constraints_active(input_ids):
            return scores

        self._ensure_token_sets(scores.device)
        assert self._target_ids is not None
        assert self._non_target_ids is not None

        if self.mode == SCD_MODE_PENALTY_ADDITIVE:
            if len(self._non_target_ids) > 0:
                scores[:, self._non_target_ids] -= self.beta
            return scores

        if self.mode == SCD_MODE_REFERENCE_SCD:
            if len(self._target_ids) > 0:
                scores[:, self._target_ids] *= self.alpha
            if len(self._non_target_ids) > 0:
                scores[:, self._non_target_ids] *= self.beta
            return scores

        if self.mode == SCD_MODE_PROB_SCALE_LOGIT_OFFSET:
            if len(self._target_ids) > 0:
                scores[:, self._target_ids] += math.log(self.alpha)
            if len(self._non_target_ids) > 0:
                scores[:, self._non_target_ids] += math.log(self.beta)
            return scores

        # Unreachable after __init__ validation.
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
    beta: float | None = None,
    target_lang: str = SCD_TARGET_LANG,
    alpha: float = SCD_DEFAULT_ALPHA,
    t_start: int | None = None,
    mode: str = SCD_MODE_PENALTY_ADDITIVE,
) -> LogitsProcessorList:
    """SCD LogitsProcessor 생성 헬퍼"""
    scd = SCDDecoder(
        tokenizer=tokenizer,
        target_lang=target_lang,
        beta=beta,
        alpha=alpha,
        t_start=t_start,
        mode=mode,
    )
    return LogitsProcessorList([scd])


def create_combined_processor(
    generator,
    query: str,
    use_cad: bool = True,
    cad_alpha: float = 0.5,
    use_scd: bool = True,
    scd_beta: float | None = None,
    scd_alpha: float = SCD_DEFAULT_ALPHA,
    scd_t_start: int | None = None,
    scd_mode: str = SCD_MODE_PENALTY_ADDITIVE,
    cad_adaptive: bool = False,
) -> LogitsProcessorList:
    """Create CAD + Korean-target SCD processors.

    1. CAD: exact context-aware scoring
       `(1 + alpha) * context_scores - alpha * no_context_scores`
    2. SCD: beta penalty for non-Korean/non-neutral/non-whitelisted tokens
       by default, or an explicitly selected corrective SCD mode.
    """
    from modules.cad_decoder import CADDecoder

    processors = []
    processor_order: list[str] = []

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
        processor_order.append("CADDecoder")

    if use_scd:
        scd = SCDDecoder(
            tokenizer=generator.tokenizer,
            beta=scd_beta,
            alpha=scd_alpha,
            t_start=scd_t_start,
            mode=scd_mode,
        )
        processor_order.append("SCDDecoder")
        scd.metadata["scd_processor_order"] = " -> ".join(processor_order)
        processors.append(scd)

    return LogitsProcessorList(processors)


def extract_scd_metadata(logits_processor) -> dict:
    """Extract normalized SCD metadata from a processor list, if present."""
    if not logits_processor:
        return {}

    processors = (
        logits_processor
        if isinstance(logits_processor, list)
        else (
            list(logits_processor)
            if isinstance(logits_processor, LogitsProcessorList)
            else [logits_processor]
        )
    )
    for processor in processors:
        getter = getattr(processor, "get_metadata", None)
        if getter is None:
            continue
        metadata = getter()
        if "scd_mode" not in metadata:
            continue
        return {
            "scd_mode": metadata["scd_mode"],
            "scd_variant": metadata["scd_variant"],
            "scd_alpha": metadata["scd_alpha"],
            "scd_beta": metadata["scd_beta"],
            "scd_t_start": metadata["scd_t_start"],
            "scd_warmup_basis": metadata["scd_warmup_basis"],
            "scd_vocab_partition": metadata["scd_vocab_partition"],
            "scd_reference_formula_applied": metadata["scd_reference_formula_applied"],
            "scd_project_whitelist_used": metadata["scd_project_whitelist_used"],
            "scd_processor_order": metadata["scd_processor_order"],
        }
    return {}
