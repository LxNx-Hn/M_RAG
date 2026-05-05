"""
MODULE 13A: CAD (Context-Aware Decoding).

Exact CAD scoring rule:

    cad_scores = (1 + alpha) * context_scores - alpha * no_context_scores

`context_scores` are supplied by HuggingFace generation for the prompt with
retrieved context. `no_context_scores` are recomputed from the same instruction
and query without retrieved context, plus the exact generated prefix y_<t.
"""

import logging

import torch
from transformers import LogitsProcessor, LogitsProcessorList

from config import CAD_ALPHA

logger = logging.getLogger(__name__)


class CADDecoder(LogitsProcessor):
    """Exact Context-Aware Decoding logits processor.

    The context branch is the normal generation call. The no-context branch is
    an uncached reference path for correctness: each step concatenates the
    no-context prompt and the generated prefix observed in `input_ids`.

    Batch and beam modes are blocked until a cached parity-tested path exists.
    """

    def __init__(
        self,
        model,
        tokenizer,
        empty_input_ids: torch.Tensor,
        empty_attention_mask: torch.Tensor | None = None,
        alpha: float = CAD_ALPHA,
        adaptive: bool = False,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.empty_input_ids = empty_input_ids
        self.empty_attention_mask = (
            empty_attention_mask
            if empty_attention_mask is not None
            else torch.ones_like(empty_input_ids)
        )
        self.alpha = alpha
        self.adaptive = adaptive
        self._context_prompt_length: int | None = None

    def set_no_context_inputs(
        self,
        *,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
    ) -> None:
        """Set the template-matched no-context prompt before generation."""
        self.empty_input_ids = input_ids
        self.empty_attention_mask = (
            attention_mask if attention_mask is not None else torch.ones_like(input_ids)
        )
        self.reset()

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        """Apply exact CAD to context-conditioned generation scores.

        `scores` are raw context-conditioned logits from the model.generate
        context branch. The returned logits follow:
        `(1 + alpha) * scores - alpha * no_context_logits`.
        """
        self._validate_supported_shape(input_ids, scores)
        if self._context_prompt_length is None:
            self._context_prompt_length = input_ids.shape[1]
        if input_ids.shape[1] < self._context_prompt_length:
            raise ValueError("CAD input_ids shorter than initial context prompt.")

        generated_prefix = input_ids[:, self._context_prompt_length :]
        with torch.no_grad():
            no_context_logits = self._compute_no_context_logits(
                generated_prefix=generated_prefix,
                device=scores.device,
            ).to(dtype=scores.dtype)

        if self.adaptive:
            alpha = self._compute_adaptive_alpha(scores, no_context_logits)
        else:
            alpha = self.alpha

        return (1.0 + alpha) * scores - alpha * no_context_logits

    def _validate_supported_shape(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> None:
        """Block unsupported batch/beam modes for CAD prefix correctness."""
        if input_ids.shape[0] != 1 or scores.shape[0] != 1:
            raise ValueError(
                "Exact CAD currently supports batch_size=1 and num_beams=1 only. "
                "Batch/beam modes need a parity-tested no-context cache path."
            )
        if self.empty_input_ids.shape[0] != 1:
            raise ValueError("CAD no-context prompt must have batch_size=1.")

    def _compute_no_context_logits(
        self,
        *,
        generated_prefix: torch.LongTensor,
        device: torch.device,
    ) -> torch.FloatTensor:
        """Reference no-context branch for p(y_t | x, y_<t)."""
        empty_ids = self.empty_input_ids.to(device)
        empty_mask = self.empty_attention_mask.to(device)
        if generated_prefix.numel() > 0:
            prefix = generated_prefix.to(device)
            prefix_mask = torch.ones(
                prefix.shape,
                dtype=empty_mask.dtype,
                device=device,
            )
            no_context_ids = torch.cat([empty_ids, prefix], dim=1)
            no_context_mask = torch.cat([empty_mask, prefix_mask], dim=1)
        else:
            no_context_ids = empty_ids
            no_context_mask = empty_mask

        outputs = self.model(
            input_ids=no_context_ids,
            attention_mask=no_context_mask,
            use_cache=False,
        )
        return outputs.logits[:, -1, :]

    def _compute_adaptive_alpha(
        self, context_logits: torch.FloatTensor, no_context_logits: torch.FloatTensor
    ) -> float:
        """적응적 alpha 계산
        두 분포의 Jensen-Shannon Divergence가 클수록 (= 컨텍스트가 중요할수록)
        alpha를 높여서 파라메트릭 지식을 더 강하게 억제
        """
        context_probs = torch.softmax(context_logits, dim=-1)
        empty_probs = torch.softmax(no_context_logits, dim=-1)

        m = 0.5 * (context_probs + empty_probs)
        kl_cm = torch.sum(
            context_probs * torch.log(context_probs / (m + 1e-10) + 1e-10), dim=-1
        )
        kl_em = torch.sum(
            empty_probs * torch.log(empty_probs / (m + 1e-10) + 1e-10), dim=-1
        )
        jsd = 0.5 * (kl_cm + kl_em)

        adaptive_alpha = torch.clamp(
            jsd * self.alpha * 2, min=0.1, max=self.alpha
        ).item()
        return adaptive_alpha

    def reset(self):
        """생성 세션 리셋"""
        self._context_prompt_length = None


def create_cad_processor(
    generator,
    query: str,
    alpha: float = CAD_ALPHA,
    adaptive: bool = False,
) -> LogitsProcessorList:
    """CAD LogitsProcessor 생성 헬퍼"""
    empty_inputs = generator.get_empty_context_inputs(query)

    cad = CADDecoder(
        model=generator.model,
        tokenizer=generator.tokenizer,
        empty_input_ids=empty_inputs["input_ids"],
        empty_attention_mask=empty_inputs.get("attention_mask"),
        alpha=alpha,
        adaptive=adaptive,
    )

    return LogitsProcessorList([cad])
