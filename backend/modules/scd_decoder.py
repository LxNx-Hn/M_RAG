"""
MODULE 13B: SCD (Selective Context-aware Decoding) 언어 이탈 억제기
Language Drift 억제 — 영문 논문 청크가 컨텍스트로 들어와도 한국어 답변 강제
기반 논문: Language Drift & SCD (Li et al., arXiv 2025) [34]

문제: 영문 컨텍스트가 입력되면 MIDM-2.0이 영어로 답변하거나
      한국어 답변 중 영어 구간을 우선 참조하는 Language Drift 발생
해결: 비목표 언어(영어 등) 토큰에 beta 패널티를 부여하여 한국어 생성 강제

Table 2 ablation 대상: beta ∈ {0.1, 0.3, 0.5}
"""

import logging

import torch
from transformers import LogitsProcessor, LogitsProcessorList

from config import SCD_BETA, SCD_TARGET_LANG

logger = logging.getLogger(__name__)


class SCDDecoder(LogitsProcessor):
    """Selective Context-aware Decoding
    Li et al. (2025) [34] 기반 구현
    한국어 범위 외 토큰 ID에 beta 패널티 부여

    주의사항:
    - 영어 고유명사(모델명, 기술 용어)도 패널티를 받을 수 있음
    - 숫자/공백/구두점은 허용하여 수치 표현 보존
    """

    def __init__(
        self,
        tokenizer,
        target_lang: str = SCD_TARGET_LANG,
        beta: float = SCD_BETA,
    ):
        self.tokenizer = tokenizer
        self.target_lang = target_lang
        self.beta = beta
        self._non_target_ids: torch.Tensor | None = None

    def _build_non_target_ids(self, device: torch.device) -> torch.Tensor:
        """비목표 언어 토큰 ID 집합 구축 (첫 호출 시 1회만 실행)"""
        non_target = []
        vocab_size = self.tokenizer.vocab_size
        for token_id in range(vocab_size):
            token = self.tokenizer.decode([token_id])
            if token and not self._is_target_or_common(token):
                non_target.append(token_id)
        if non_target:
            return torch.tensor(non_target, dtype=torch.long, device=device)
        return torch.empty(0, dtype=torch.long, device=device)

    def _is_target_or_common(self, token: str) -> bool:
        """한국어 + 숫자/공백/구두점은 허용 (True = 패널티 제외)"""
        for ch in token:
            code = ord(ch)
            is_hangul = (
                0xAC00 <= code <= 0xD7A3  # 한글 음절 (가-힣)
                or 0x1100 <= code <= 0x11FF  # 한글 자모
                or 0x3130 <= code <= 0x318F  # 호환 자모
            )
            is_common = ch in " \n\t\r.,!?()[]{}:;\"'-·…%_/\\0123456789"
            if not (is_hangul or is_common):
                return False
        return True

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        """LogitsProcessor 인터페이스 구현
        비목표 언어 토큰의 logit에서 beta를 빼서 생성 확률 낮춤
        """
        if self._non_target_ids is None:
            self._non_target_ids = self._build_non_target_ids(scores.device)
        elif self._non_target_ids.device != scores.device:
            self._non_target_ids = self._non_target_ids.to(scores.device)

        if len(self._non_target_ids) > 0:
            scores[:, self._non_target_ids] -= self.beta

        return scores


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
    """CAD + SCD 통합 LogitsProcessorList 생성
    GuideV2 §3.3 MODULE 13 통합 사용법 기반

    두 모듈은 독립적으로 scores를 수정하므로 순서대로 적용:
    1. CAD: 파라메트릭 지식 억제 (scores - alpha * empty_logits)
    2. SCD: 비목표 언어 패널티 (scores[:, non_ko] -= beta)
    """
    from modules.cad_decoder import CADDecoder

    processors = []

    if use_cad:
        empty_ids = generator.get_empty_context_input_ids(query)
        cad = CADDecoder(
            model=generator.model,
            tokenizer=generator.tokenizer,
            empty_input_ids=empty_ids,
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
