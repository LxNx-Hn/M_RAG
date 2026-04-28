"""
MODULE 12: Generator

Context-grounded answer generation for M-RAG using the Mi:dm instruct models.
"""

from __future__ import annotations

import logging
from threading import Thread
from typing import Generator as Gen
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from config import GENERATION_MODEL, MAX_NEW_TOKENS, TEMPERATURE, TOP_P

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """당신은 학술 논문 분석 전문 AI 어시스턴트입니다.

응답 지침:
1. 반드시 주어진 컨텍스트만을 근거로 답변하세요. 컨텍스트에 없는 내용은 추측하거나 사전 지식으로 보완하지 마세요.
2. 수치, 실험 결과, 비교 데이터는 가능한 한 컨텍스트에 있는 정확한 값을 인용하세요.
3. 컨텍스트에서 답을 찾을 수 없으면 "해당 정보는 제공된 논문에서 찾을 수 없습니다."라고 명확하게 답하세요."""

JUDGE_SYSTEM_PROMPT = """You are an evaluation judge.
Return only the final label requested by the user.
Do not explain and do not output any extra text."""

QA_TEMPLATE = """다음 논문 컨텍스트를 참고하여 질문에 답변하세요.
답변은 컨텍스트의 구체적인 내용(수치, 방법, 결과)을 근거로 제시하세요.

[컨텍스트]
{context}

[질문]
{query}

[답변]"""

COMPARE_TEMPLATE = """두 논문의 컨텍스트를 비교 분석하세요. 각 항목마다 구체적인 수치와 방법의 차이를 명시하세요.

[논문 A 컨텍스트]
{context_a}

[논문 B 컨텍스트]
{context_b}

[비교 질문]
{query}

아래 형식으로 비교한 뒤 핵심 차이점을 요약하세요.
| 항목 | 논문 A | 논문 B |
|---|---|---|

[비교 분석]"""

SUMMARY_TEMPLATE = """다음 논문 컨텍스트를 구조화하여 요약하세요. 각 항목에서 구체적인 수치와 결과를 반드시 포함하세요.

[논문 컨텍스트]
{context}

아래 구조로 요약하세요.
1. 연구 목적: 어떤 문제를 해결하려는가
2. 핵심 방법론: 제안 기법의 구조와 특징
3. 주요 결과: 정량적 성능 수치 포함
4. 의의 및 한계

[구조화 요약]"""


class Generator:
    """LLM generation module."""

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

    def _tokenize_for_generation(self, prompt: str) -> dict[str, torch.Tensor]:
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        )
        return {
            key: value.to(self.device)
            for key, value in inputs.items()
            if key in {"input_ids", "attention_mask"}
        }

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            logger.info("Loading tokenizer: %s", self.model_name)
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
            logger.info("Loading model: %s", self.model_name)
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True,
            )
            self._model.eval()
        return self._model

    def _format_chat(self, user_content: str, system_prompt: str = "") -> str:
        if self._has_chat_template is None:
            self._has_chat_template = (
                hasattr(self.tokenizer, "chat_template")
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
            except Exception as exc:
                logger.warning(
                    "apply_chat_template failed, falling back to raw prompt: %s", exc
                )

        if system_prompt:
            return f"{system_prompt}\n\n{user_content}"
        return user_content

    def generate(
        self,
        query: str,
        context: str,
        template: str = "qa",
        logits_processor=None,
        force_greedy: bool = False,
        **kwargs,
    ) -> str:
        if template == "compare":
            prompt = COMPARE_TEMPLATE.format(
                context_a=kwargs.get("context_a", context),
                context_b=kwargs.get("context_b", ""),
                query=query,
            )
        elif template == "summary":
            prompt = SUMMARY_TEMPLATE.format(context=context)
        elif template == "raw":
            prompt = kwargs.get(
                "raw_prompt",
                QA_TEMPLATE.format(context=context, query=query),
            )
        else:
            prompt = QA_TEMPLATE.format(context=context, query=query)

        full_prompt = self._format_chat(prompt, SYSTEM_PROMPT)
        return self._generate(
            full_prompt,
            logits_processor=logits_processor,
            force_greedy=force_greedy,
        )

    def generate_stream(
        self,
        query: str,
        context: str,
        template: str = "qa",
        logits_processor=None,
        force_greedy: bool = False,
        **kwargs,
    ) -> Gen[str, None, None]:
        if template == "compare":
            prompt = COMPARE_TEMPLATE.format(
                context_a=kwargs.get("context_a", context),
                context_b=kwargs.get("context_b", ""),
                query=query,
            )
        elif template == "summary":
            prompt = SUMMARY_TEMPLATE.format(context=context)
        elif template == "raw":
            prompt = kwargs.get(
                "raw_prompt",
                QA_TEMPLATE.format(context=context, query=query),
            )
        else:
            prompt = QA_TEMPLATE.format(context=context, query=query)

        full_prompt = self._format_chat(prompt, SYSTEM_PROMPT)
        inputs = self._tokenize_for_generation(full_prompt)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )
        resolved_temperature, resolved_top_p, resolved_do_sample = (
            self._resolve_sampling_params(force_greedy=force_greedy)
        )

        gen_kwargs = {
            **inputs,
            "max_new_tokens": self.max_new_tokens,
            "temperature": resolved_temperature,
            "top_p": resolved_top_p,
            "do_sample": resolved_do_sample,
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

    def generate_simple(
        self,
        prompt: str,
        max_new_tokens: int | None = None,
        *,
        system_prompt: str = "",
        temperature: float | None = None,
        top_p: float | None = None,
        do_sample: bool | None = None,
        force_greedy: bool = False,
    ) -> str:
        formatted = self._format_chat(prompt, system_prompt)
        return self._generate(
            formatted,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample,
            force_greedy=force_greedy,
        )

    def generate_judge(self, prompt: str, max_new_tokens: int = 32) -> str:
        return self.generate_simple(
            prompt,
            max_new_tokens=max_new_tokens,
            system_prompt=JUDGE_SYSTEM_PROMPT,
            temperature=0.0,
            top_p=1.0,
            do_sample=False,
            force_greedy=True,
        )

    def rank_labels(
        self,
        prompt: str,
        labels: list[str],
        *,
        system_prompt: str = JUDGE_SYSTEM_PROMPT,
    ) -> tuple[str, dict[str, float]]:
        if not labels:
            raise ValueError("rank_labels requires at least one candidate label.")

        formatted = self._format_chat(prompt, system_prompt)
        prompt_inputs = self._tokenize_for_generation(formatted)
        prompt_ids = prompt_inputs["input_ids"]
        prompt_mask = prompt_inputs["attention_mask"]
        prompt_len = prompt_ids.shape[1]

        scores: dict[str, float] = {}
        for label in labels:
            label_ids = self.tokenizer(
                label,
                return_tensors="pt",
                add_special_tokens=False,
            )["input_ids"].to(self.device)
            label_mask = torch.ones_like(label_ids, device=self.device)

            input_ids = torch.cat([prompt_ids, label_ids], dim=1)
            attention_mask = torch.cat([prompt_mask, label_mask], dim=1)

            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

            logits = outputs.logits[0]
            total_logprob = 0.0
            for idx in range(label_ids.shape[1]):
                token_id = int(label_ids[0, idx].item())
                pred_pos = prompt_len - 1 + idx
                log_probs = torch.log_softmax(logits[pred_pos], dim=-1)
                total_logprob += float(log_probs[token_id].item())

            scores[label] = total_logprob

        best_label = max(scores, key=scores.get)
        return best_label, scores

    def _generate(
        self,
        prompt: str,
        logits_processor=None,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        do_sample: bool | None = None,
        force_greedy: bool = False,
    ) -> str:
        inputs = self._tokenize_for_generation(prompt)
        resolved_temperature, resolved_top_p, resolved_do_sample = (
            self._resolve_sampling_params(
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                force_greedy=force_greedy,
            )
        )

        gen_kwargs = {
            "max_new_tokens": max_new_tokens or self.max_new_tokens,
            "temperature": resolved_temperature,
            "top_p": resolved_top_p,
            "do_sample": resolved_do_sample,
            "pad_token_id": self.tokenizer.pad_token_id,
        }
        if logits_processor:
            gen_kwargs["logits_processor"] = logits_processor

        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        input_len = inputs["input_ids"].shape[1]
        if outputs[0].shape[0] <= input_len:
            return ""

        generated = outputs[0][input_len:]
        response = self.tokenizer.decode(generated, skip_special_tokens=True)
        return response.strip()

    def _resolve_sampling_params(
        self,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
        do_sample: bool | None = None,
        force_greedy: bool = False,
    ) -> tuple[float, float, bool]:
        if force_greedy:
            return 0.0, 1.0, False

        resolved_temperature = TEMPERATURE if temperature is None else temperature
        resolved_top_p = TOP_P if top_p is None else top_p
        resolved_do_sample = TEMPERATURE > 0 if do_sample is None else do_sample
        return resolved_temperature, resolved_top_p, resolved_do_sample

    def get_empty_context_input_ids(self, query: str) -> torch.Tensor:
        formatted = self._format_chat(query.strip(), "")
        inputs = self._tokenize_for_generation(formatted)
        return inputs["input_ids"]

    def format_sources(self, documents: list[dict]) -> str:
        sources = []
        for i, doc in enumerate(documents):
            meta = doc.get("metadata", {})
            source = (
                f"[{i + 1}] {meta.get('doc_id', 'unknown')} "
                f"- {meta.get('section_type', 'unknown')} "
                f"(p.{meta.get('page', '?')})"
            )
            sources.append(source)
        return "\n".join(sources)
