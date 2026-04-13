"""
Pipeline F: 퀴즈 생성
컨텍스트 기반 객관식 문제 생성 — CAD 강제 적용 (꾸며낸 문제 방지)
"""
import logging

from config import CAD_ALPHA, SCD_BETA
from modules.scd_decoder import create_combined_processor

logger = logging.getLogger(__name__)

QUIZ_PROMPT = """아래 컨텍스트를 바탕으로 객관식 5문제를 생성하세요.
각 문제는 컨텍스트에 근거한 사실만 사용하세요. 추측하지 마세요.

형식:
**문제 1.** [질문]
(A) 선택지1
(B) 선택지2
(C) 선택지3
(D) 선택지4
**정답:** (X)
**해설:** [컨텍스트 근거 설명]

---

컨텍스트:
{context}

질문 의도: {query}

위 형식으로 객관식 5문제를 생성하세요:"""

FLASHCARD_PROMPT = """아래 컨텍스트를 바탕으로 플래시카드 10장을 생성하세요.
각 카드는 컨텍스트에 근거한 사실만 사용하세요. 추측하지 마세요.

반드시 아래 JSON 형식으로만 답하세요:
[FLASHCARD_START]
[{{"front": "질문 또는 개념", "back": "답변 또는 설명"}}, ...]
[FLASHCARD_END]

컨텍스트:
{context}

질문 의도: {query}

플래시카드 10장을 JSON 형식으로 생성하세요:"""

# 플래시카드 감지 키워드
FLASHCARD_KEYWORDS = ["플래시카드", "카드", "flashcard", "암기"]


def _detect_mode(query: str) -> str:
    """쿼리에서 quiz / flashcard 모드 자동 감지"""
    q_lower = query.lower()
    for kw in FLASHCARD_KEYWORDS:
        if kw in q_lower:
            return "flashcard"
    return "quiz"


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
) -> dict:
    """퀴즈/플래시카드 생성 파이프라인 실행"""
    mode = _detect_mode(query)
    steps = []

    # 1. 하이브리드 검색
    search_results = hybrid_retriever.search(
        collection_name=collection_name,
        query=query,
        top_k=10,
    )
    steps.append({"step": "hybrid_search", "results_count": len(search_results)})

    # 2. 재랭킹
    reranked = reranker.rerank(query, search_results, top_k=7)
    steps.append({"step": "reranking", "top_k": len(reranked)})

    # 3. 컨텍스트 압축
    compressed = compressor.compress(reranked, query, strategy="extractive")
    compressed = compressor.truncate_to_limit(compressed)
    steps.append({"step": "compression", "docs_count": len(compressed)})

    # 4. 컨텍스트 조합
    context = "\n\n---\n\n".join(doc["content"] for doc in compressed)

    # 5. CAD 강제 적용
    logits_processor = create_combined_processor(
        generator=generator,
        query=query,
        use_cad=True,
        cad_alpha=max(cad_alpha, 0.5),
        use_scd=use_scd,
        scd_beta=scd_beta,
    )
    steps.append({
        "step": "decoder",
        "cad_enabled": True, "cad_alpha": max(cad_alpha, 0.5),
        "scd_enabled": use_scd, "scd_beta": scd_beta,
        "mode": mode,
        "note": f"CAD forced for {mode} fidelity",
    })

    # 6. 프롬프트 선택 + 생성
    if mode == "flashcard":
        prompt = FLASHCARD_PROMPT.format(context=context, query=query)
    else:
        prompt = QUIZ_PROMPT.format(context=context, query=query)

    answer = generator.generate(
        query=query,
        context=context,
        template="raw",
        raw_prompt=prompt,
        logits_processor=logits_processor,
    )

    sources = generator.format_sources(compressed)

    return {
        "answer": answer,
        "sources": sources,
        "source_documents": compressed,
        "pipeline": f"F_{mode}",
        "steps": steps,
    }
