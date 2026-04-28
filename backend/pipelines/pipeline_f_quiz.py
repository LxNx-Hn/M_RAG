"""
Pipeline F: quiz/flashcard generation.
"""

import logging

from config import CAD_ALPHA, SCD_BETA
from modules.scd_decoder import create_combined_processor

logger = logging.getLogger(__name__)

QUIZ_PROMPT = """당신은 학술 논문 기반 퀴즈 출제자입니다.
아래 컨텍스트만을 근거로 객관식 5문제를 출제해 주세요.

규칙:
- 컨텍스트에 명시된 사실만 사용하세요.
- 정답은 컨텍스트에서 직접 확인 가능해야 합니다.
- 아래 형식을 유지하세요.

**문제 1.** [질문]
(A) 선택지1
(B) 선택지2
(C) 선택지3
(D) 선택지4
**정답:** (X)
**해설:** [근거]

---

[컨텍스트]
{context}

[출제 의도]
{query}
"""

FLASHCARD_PROMPT = """당신은 학술 논문 기반 학습 카드 생성기입니다.
아래 컨텍스트만을 근거로 플래시카드 10개를 JSON으로 생성하세요.

[FLASHCARD_START]
[{{"front": "질문", "back": "답변"}}, ...]
[FLASHCARD_END]

[컨텍스트]
{context}

[학습 주제]
{query}
"""

FLASHCARD_KEYWORDS = ["플래시카드", "카드", "flashcard", "암기"]


def _detect_mode(query: str) -> str:
    q_lower = query.lower()
    for keyword in FLASHCARD_KEYWORDS:
        if keyword in q_lower:
            return "flashcard"
    return "quiz"


def _fallback_response(mode: str, steps: list[dict], reason: str) -> dict:
    return {
        "answer": "문제 생성을 위한 근거가 부족합니다. 문서를 추가하거나 질문 범위를 좁혀 주세요.",
        "sources": "",
        "source_documents": [],
        "pipeline": f"F_{mode}",
        "steps": steps + [{"step": "fallback", "reason": reason, "fallback": True}],
    }


def run(
    query: str,
    collection_name: str,
    hybrid_retriever,
    reranker,
    compressor,
    generator,
    query_expander=None,
    use_cad: bool = True,
    cad_alpha: float = CAD_ALPHA,
    use_scd: bool = True,
    scd_beta: float = SCD_BETA,
    doc_id_filter: str | None = None,
) -> dict:
    """Run quiz/flashcard generation pipeline."""
    mode = _detect_mode(query)
    steps = []
    try:
        search_results = hybrid_retriever.search(
            collection_name=collection_name,
            query=query,
            top_k=10,
            doc_id_filter=doc_id_filter,
        )
        steps.append({"step": "hybrid_search", "results_count": len(search_results)})
        if not search_results:
            return _fallback_response(mode, steps, "no_search_results")

        reranked = reranker.rerank(query, search_results, top_k=7)
        steps.append({"step": "reranking", "top_k": len(reranked)})
        if not reranked:
            return _fallback_response(mode, steps, "no_rerank_results")

        compressed = compressor.compress(reranked, query, strategy="extractive")
        compressed = compressor.truncate_to_limit(compressed)
        steps.append({"step": "compression", "docs_count": len(compressed)})
        if not compressed:
            return _fallback_response(mode, steps, "no_context_after_compression")

        context = "\n\n---\n\n".join(doc["content"] for doc in compressed)
        logits_processor = create_combined_processor(
            generator=generator,
            query=query,
            use_cad=use_cad,
            cad_alpha=cad_alpha,
            use_scd=use_scd,
            scd_beta=scd_beta,
        )
        steps.append(
            {
                "step": "decoder",
                "cad_enabled": use_cad,
                "cad_alpha": cad_alpha,
                "scd_enabled": use_scd,
                "scd_beta": scd_beta,
                "mode": mode,
            }
        )

        prompt = (
            FLASHCARD_PROMPT.format(context=context, query=query)
            if mode == "flashcard"
            else QUIZ_PROMPT.format(context=context, query=query)
        )
        answer = generator.generate(
            query=query,
            context=context,
            template="raw",
            raw_prompt=prompt,
            logits_processor=logits_processor,
            force_greedy=use_cad,
        )
        sources = generator.format_sources(compressed)

        return {
            "answer": answer,
            "sources": sources,
            "source_documents": compressed,
            "pipeline": f"F_{mode}",
            "steps": steps,
        }
    except Exception as exc:
        logger.error("pipeline_f_quiz failed: %s", exc, exc_info=True)
        return {
            "answer": "문제 생성 중 일시적 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
            "sources": "",
            "source_documents": [],
            "pipeline": f"F_{mode}",
            "steps": steps + [{"step": "error", "detail": str(exc)[:200]}],
            "error": True,
        }
