"""
MODULE 12: Generator
컨텍스트 + 질의 → 최종 답변 생성 (MIDM-2.0 Base Instruct)
기반 논문: Speculative RAG [16], RAG (Original) [20]

모델: K-intelligence/Midm-2.0-Base-Instruct (11.5B, bfloat16)
요구사항: transformers >= 4.45.0, GPU 24GB+ VRAM
"""
import logging
from threading import Thread
from typing import Generator as Gen, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from config import (
    GENERATION_MODEL,
    MAX_NEW_TOKENS,
    TEMPERATURE,
    TOP_P,
)

logger = logging.getLogger(__name__)


# 프롬프트 템플릿
SYSTEM_PROMPT = """당신은 학술 논문 분석 전문 AI 어시스턴트입니다.
주어진 논문 컨텍스트만을 기반으로 질문에 답변하세요.
컨텍스트에 없는 내용은 "해당 정보는 제공된 논문에서 찾을 수 없습니다"라고 답하세요.
답변은 한국어로 작성하되, 전문 용어는 영어를 괄호 안에 병기하세요."""

QA_TEMPLATE = """[컨텍스트]
{context}

[질문]
{query}

[답변]"""

COMPARE_TEMPLATE = """[논문 A 컨텍스트]
{context_a}

[논문 B 컨텍스트]
{context_b}

[비교 질문]
{query}

다음 형식으로 비교 분석하세요:
| 항목 | 논문 A | 논문 B |
|---|---|---|

[비교 분석]"""

SUMMARY_TEMPLATE = """[논문 컨텍스트]
{context}

위 논문의 내용을 다음 구조로 요약해주세요:
1. 연구 목적
2. 핵심 방법론
3. 주요 결과
4. 의의 및 한계

[구조화 요약]"""


class Generator:
    """LLM 생성 모듈"""

    def __init__(
        self,
        model_name: str = GENERATION_MODEL,
        device: Optional[str] = None,
        max_new_tokens: int = MAX_NEW_TOKENS,
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_new_tokens = max_new_tokens
        self._model = None
        self._tokenizer = None

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            logger.info(f"Loading tokenizer: {self.model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
            )
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
        return self._tokenizer

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Loading model: {self.model_name}")
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,  # MIDM-2.0 권장 dtype
                device_map="auto",
                trust_remote_code=True,
            )
            self._model.eval()
        return self._model

    def generate(
        self,
        query: str,
        context: str,
        template: str = "qa",
        logits_processor=None,
        **kwargs,
    ) -> str:
        """컨텍스트 기반 답변 생성"""
        # 템플릿 선택
        if template == "compare":
            # context should be pre-formatted with A/B sections
            prompt = COMPARE_TEMPLATE.format(
                context_a=kwargs.get("context_a", context),
                context_b=kwargs.get("context_b", ""),
                query=query,
            )
        elif template == "summary":
            prompt = SUMMARY_TEMPLATE.format(context=context)
        else:
            prompt = QA_TEMPLATE.format(context=context, query=query)

        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        return self._generate(full_prompt, logits_processor=logits_processor)

    def generate_stream(
        self,
        query: str,
        context: str,
        template: str = "qa",
        logits_processor=None,
        **kwargs,
    ) -> Gen[str, None, None]:
        """토큰 단위 스트리밍 생성 (SSE용)"""
        if template == "compare":
            prompt = COMPARE_TEMPLATE.format(
                context_a=kwargs.get("context_a", context),
                context_b=kwargs.get("context_b", ""),
                query=query,
            )
        elif template == "summary":
            prompt = SUMMARY_TEMPLATE.format(context=context)
        else:
            prompt = QA_TEMPLATE.format(context=context, query=query)

        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        inputs = self.tokenizer(
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        ).to(self.device)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        gen_kwargs = {
            **inputs,
            "max_new_tokens": self.max_new_tokens,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "do_sample": TEMPERATURE > 0,
            "pad_token_id": self.tokenizer.pad_token_id,
            "streamer": streamer,
        }
        if logits_processor:
            gen_kwargs["logits_processor"] = logits_processor

        thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
        thread.start()

        for token_text in streamer:
            if token_text:
                yield token_text

        thread.join()

    def generate_simple(self, prompt: str) -> str:
        """단순 프롬프트 생성 (내부 용도: HyDE, 요약 등)"""
        return self._generate(prompt)

    def _generate(self, prompt: str, logits_processor=None) -> str:
        """내부 생성 함수"""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        ).to(self.device)

        gen_kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "do_sample": TEMPERATURE > 0,
            "pad_token_id": self.tokenizer.pad_token_id,
        }

        if logits_processor:
            gen_kwargs["logits_processor"] = logits_processor

        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        # 입력 부분 제외하고 디코딩
        input_len = inputs["input_ids"].shape[1]
        if outputs[0].shape[0] <= input_len:
            return ""
        generated = outputs[0][input_len:]
        response = self.tokenizer.decode(generated, skip_special_tokens=True)
        return response.strip()

    def get_empty_context_input_ids(self, query: str) -> torch.Tensor:
        """CAD용: 문서 없는 프롬프트의 input_ids 반환"""
        empty_prompt = f"{SYSTEM_PROMPT}\n\n[컨텍스트]\n(없음)\n\n[질문]\n{query}\n\n[답변]"
        inputs = self.tokenizer(
            empty_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        ).to(self.device)
        return inputs["input_ids"]

    def format_sources(self, documents: list[dict]) -> str:
        """출처 정보 포맷팅"""
        sources = []
        for i, doc in enumerate(documents):
            meta = doc.get("metadata", {})
            source = (
                f"[{i+1}] {meta.get('doc_id', 'unknown')} "
                f"- {meta.get('section_type', 'unknown')} "
                f"(p.{meta.get('page', '?')})"
            )
            sources.append(source)
        return "\n".join(sources)
