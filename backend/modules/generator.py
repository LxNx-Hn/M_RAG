"""
MODULE 12: Generator
컨텍스트 + 질의 → 최종 답변 생성 (MIDM-2.0 Instruct)
기반 논문: Speculative RAG [16], RAG (Original) [20]

모델: K-intelligence/Midm-2.0-Mini-Instruct (2.3B, bfloat16, 12GB GPU)
     K-intelligence/Midm-2.0-Base-Instruct (11.5B, bfloat16 24GB+ / 4-bit ~7GB)
요구사항: transformers >= 4.45.0
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

핵심 원칙:
1. 반드시 주어진 컨텍스트만을 근거로 답변하세요. 컨텍스트에 없는 내용을 추측하거나 사전 지식으로 보충하지 마세요.
2. 수치, 실험 결과, 비교 데이터를 언급할 때는 컨텍스트에 있는 정확한 값을 인용하세요.
3. 컨텍스트에서 답을 찾을 수 없으면 "해당 정보는 제공된 논문에서 찾을 수 없습니다"라고 명확히 밝히세요."""

QA_TEMPLATE = """다음 논문 컨텍스트를 참고하여 질문에 답변하세요.
답변 시 컨텍스트의 구체적 내용(수치, 방법, 결과 등)을 근거로 제시하세요.

[컨텍스트]
{context}

[질문]
{query}

[답변]"""

COMPARE_TEMPLATE = """두 논문의 컨텍스트를 비교 분석하세요. 각 항목마다 구체적 수치나 방법의 차이를 명시하세요.

[논문 A 컨텍스트]
{context_a}

[논문 B 컨텍스트]
{context_b}

[비교 질문]
{query}

아래 형식의 표로 비교한 뒤, 핵심 차이를 요약하세요:
| 항목 | 논문 A | 논문 B |
|---|---|---|

[비교 분석]"""

SUMMARY_TEMPLATE = """다음 논문 컨텍스트를 구조화하여 요약하세요. 각 항목에서 핵심 수치와 결과를 반드시 포함하세요.

[논문 컨텍스트]
{context}

아래 구조로 요약하세요:
1. 연구 목적 — 어떤 문제를 해결하려 하는가
2. 핵심 방법론 — 제안 기법의 구조와 특징
3. 주요 결과 — 정량적 성능 수치 포함
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
        self._has_chat_template = None

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
            load_kwargs = dict(
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True,
            )
            # Base(11.5B)가 VRAM에 안 들어가면 4-bit 양자화 시도
            is_base = "Base" in self.model_name and "Mini" not in self.model_name
            if is_base and torch.cuda.is_available():
                vram_gb = torch.cuda.get_device_properties(0).total_mem / (1024**3)
                if vram_gb < 20:
                    try:
                        from transformers import BitsAndBytesConfig
                        logger.info(f"VRAM {vram_gb:.1f}GB < 20GB — Base 모델 4-bit 양자화 적용")
                        load_kwargs["quantization_config"] = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.bfloat16,
                            bnb_4bit_quant_type="nf4",
                        )
                        load_kwargs.pop("torch_dtype", None)
                    except ImportError:
                        logger.warning("bitsandbytes 미설치 — bfloat16으로 로드 시도")
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name, **load_kwargs,
            )
            self._model.eval()
        return self._model

    def _format_chat(self, user_content: str, system_prompt: str = "") -> str:
        """MIDM chat_template을 사용하여 프롬프트 포맷팅

        MIDM-2.0은 Llama-3 스타일 특수 토큰을 사용:
        <|start_header_id|>system<|end_header_id|> ... <|eot_id|>
        <|start_header_id|>user<|end_header_id|> ... <|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """
        if self._has_chat_template is None:
            self._has_chat_template = (
                hasattr(self.tokenizer, 'chat_template')
                and self.tokenizer.chat_template is not None
            )

        if self._has_chat_template:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_content})
            try:
                return self.tokenizer.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    tokenize=False,
                )
            except Exception as e:
                logger.warning(f"apply_chat_template 실패, raw fallback: {e}")

        # chat_template이 없는 토크나이저 fallback
        if system_prompt:
            return f"{system_prompt}\n\n{user_content}"
        return user_content

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
            prompt = COMPARE_TEMPLATE.format(
                context_a=kwargs.get("context_a", context),
                context_b=kwargs.get("context_b", ""),
                query=query,
            )
        elif template == "summary":
            prompt = SUMMARY_TEMPLATE.format(context=context)
        elif template == "raw":
            prompt = kwargs.get("raw_prompt", QA_TEMPLATE.format(context=context, query=query))
        else:
            prompt = QA_TEMPLATE.format(context=context, query=query)

        full_prompt = self._format_chat(prompt, SYSTEM_PROMPT)
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
        elif template == "raw":
            prompt = kwargs.get("raw_prompt", QA_TEMPLATE.format(context=context, query=query))
        else:
            prompt = QA_TEMPLATE.format(context=context, query=query)

        full_prompt = self._format_chat(prompt, SYSTEM_PROMPT)

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
        """단순 프롬프트 생성 (내부 용도: HyDE, RAGAS 평가 등)"""
        formatted = self._format_chat(prompt)
        return self._generate(formatted)

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
        empty_user_content = f"[컨텍스트]\n(없음)\n\n[질문]\n{query}\n\n[답변]"
        formatted = self._format_chat(empty_user_content, SYSTEM_PROMPT)
        inputs = self.tokenizer(
            formatted,
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
