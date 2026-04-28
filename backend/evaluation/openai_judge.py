from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpenAIJudgeConfig:
    model: str
    api_key: str
    timeout: float = 120.0


def judge_with_openai(
    *,
    config: OpenAIJudgeConfig,
    prompt: str,
    labels: list[str] | None = None,
) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=config.api_key, timeout=config.timeout)

    system_prompt = (
        "You are an evaluation judge for RAG experiments. "
        "Return concise outputs only."
    )
    if labels:
        label_text = " / ".join(labels)
        system_prompt = (
            "You are an evaluation judge for RAG experiments. "
            f"Return exactly one label from this set and nothing else: {label_text}."
        )

    response = client.chat.completions.create(
        model=config.model,
        temperature=0.0,
        max_tokens=32,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise ValueError("OpenAI judge returned an empty response.")

    if labels:
        normalized = text.upper()
        for label in labels:
            if label.upper() in normalized:
                return label
    return text
