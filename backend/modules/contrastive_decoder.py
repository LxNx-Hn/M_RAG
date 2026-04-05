"""
MODULE 13: Contrastive Decoder ★ 차별화 포인트
Context-Aware Contrastive Decoding (CAD) 환각 억제기
파인튜닝 없이 LogitsProcessor 하나로 구현
기반 논문: CAD (Shi et al., 2023) [3], Contrastive Decoding (Li et al., 2023) [4]

수식: Logit_final = Logit(문서 포함) - α × Logit(문서 없음)
→ 파라메트릭 지식(사전 학습 기억) 개입을 실시간 억제
"""
import logging
from typing import Optional

import torch
from transformers import LogitsProcessor, LogitsProcessorList

from config import CAD_ALPHA

logger = logging.getLogger(__name__)


class ContrastiveDecoder(LogitsProcessor):
    """Context-Aware Contrastive Decoding
    Shi et al. (2023) 기반, 학습 불필요
    HuggingFace LogitsProcessor 인터페이스 활용

    모델이 다음 토큰을 예측할 때:
    - 문서 포함 프롬프트의 logit에서
    - 문서 없는 프롬프트의 logit을 빼서
    - 파라메트릭 지식의 개입을 억제
    """

    def __init__(
        self,
        model,
        tokenizer,
        empty_input_ids: torch.Tensor,
        alpha: float = CAD_ALPHA,
        adaptive: bool = True,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.empty_input_ids = empty_input_ids
        self.alpha = alpha
        self.adaptive = adaptive
        self._empty_past_key_values = None
        self._step = 0

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        """LogitsProcessor 인터페이스 구현
        scores: 문서 포함 프롬프트의 logit (batch_size, vocab_size)
        """
        with torch.no_grad():
            # 문서 없는 프롬프트로 logit 계산
            if self._step == 0:
                # 첫 스텝: 전체 empty prompt 처리
                empty_outputs = self.model(self.empty_input_ids)
                empty_logits = empty_outputs.logits[:, -1, :]
                self._empty_past_key_values = empty_outputs.past_key_values
            else:
                # 이후 스텝: KV cache 활용 (마지막 생성 토큰만 입력)
                last_token = input_ids[:, -1:]
                if self._empty_past_key_values is not None:
                    empty_outputs = self.model(
                        last_token,
                        past_key_values=self._empty_past_key_values,
                    )
                    empty_logits = empty_outputs.logits[:, -1, :]
                    self._empty_past_key_values = empty_outputs.past_key_values
                else:
                    empty_logits = torch.zeros_like(scores)

            self._step += 1

        # 적응적 alpha: 두 분포의 차이가 클 때만 강하게 억제
        if self.adaptive:
            alpha = self._compute_adaptive_alpha(scores, empty_logits)
        else:
            alpha = self.alpha

        # 핵심 수식: 파라메트릭 지식 억제
        # Logit_final = Logit(문서 포함) - α × Logit(문서 없음)
        scores = scores - alpha * empty_logits

        return scores

    def _compute_adaptive_alpha(
        self, context_logits: torch.FloatTensor, empty_logits: torch.FloatTensor
    ) -> float:
        """적응적 alpha 계산
        두 분포의 KL divergence가 클수록 (= 컨텍스트가 중요할수록)
        alpha를 높여서 파라메트릭 지식을 더 강하게 억제
        """
        context_probs = torch.softmax(context_logits, dim=-1)
        empty_probs = torch.softmax(empty_logits, dim=-1)

        # Jensen-Shannon Divergence (KL의 대칭 버전)
        m = 0.5 * (context_probs + empty_probs)
        kl_cm = torch.sum(context_probs * torch.log(context_probs / (m + 1e-10) + 1e-10), dim=-1)
        kl_em = torch.sum(empty_probs * torch.log(empty_probs / (m + 1e-10) + 1e-10), dim=-1)
        jsd = 0.5 * (kl_cm + kl_em)

        # JSD를 alpha 범위로 스케일 (0.1 ~ alpha_max)
        adaptive_alpha = torch.clamp(jsd * self.alpha * 2, min=0.1, max=self.alpha).item()
        return adaptive_alpha

    def reset(self):
        """생성 세션 리셋"""
        self._empty_past_key_values = None
        self._step = 0


def create_cad_processor(
    generator,
    query: str,
    alpha: float = CAD_ALPHA,
    adaptive: bool = True,
) -> LogitsProcessorList:
    """CAD LogitsProcessor 생성 헬퍼"""
    empty_ids = generator.get_empty_context_input_ids(query)

    cad = ContrastiveDecoder(
        model=generator.model,
        tokenizer=generator.tokenizer,
        empty_input_ids=empty_ids,
        alpha=alpha,
        adaptive=adaptive,
    )

    return LogitsProcessorList([cad])
