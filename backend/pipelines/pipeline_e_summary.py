"""
Pipeline E: 전체 요약
쿼리 → RAPTOR 계층 트리 검색 → 섹션별 핵심 추출 → 압축 → 구조화 요약 생성
"""
import logging

from modules.contrastive_decoder import create_cad_processor

logger = logging.getLogger(__name__)


def run(
    query: str,
    collection_name: str,
    hybrid_retriever,
    reranker,
    compressor,
    generator,
    use_cad: bool = True,
    cad_alpha: float = 0.5,
) -> dict:
    """전체 요약 파이프라인 실행"""
    steps = []

    # 1. 주요 섹션별 검색
    sections = ["abstract", "introduction", "method", "result", "conclusion"]
    all_results = []

    for section in sections:
        results = hybrid_retriever.search(
            collection_name=collection_name,
            query=query,
            section_filter=section,
            top_k=3,
        )
        all_results.extend(results)
        steps.append({
            "step": f"section_search_{section}",
            "results_count": len(results),
        })

    # 섹션 필터 검색 결과가 부족하면 전체 검색 보완
    if len(all_results) < 5:
        full_results = hybrid_retriever.search(
            collection_name=collection_name,
            query="summarize the paper main contributions results",
            top_k=10,
        )
        existing_ids = {r["chunk_id"] for r in all_results}
        for r in full_results:
            if r["chunk_id"] not in existing_ids:
                all_results.append(r)

    # 2. 재랭킹
    summary_query = "논문 전체 요약: 목적, 방법론, 결과, 의의"
    reranked = reranker.rerank(summary_query, all_results, top_k=8)
    steps.append({"step": "reranking", "top_k": len(reranked)})

    # 3. 압축
    compressed = compressor.compress(reranked, summary_query)
    compressed = compressor.truncate_to_limit(compressed)

    # 4. 컨텍스트 조합 (섹션 순서대로 정렬)
    section_order = {s: i for i, s in enumerate(sections)}
    compressed.sort(
        key=lambda d: section_order.get(
            d.get("metadata", {}).get("section_type", ""), 99
        )
    )
    context = "\n\n---\n\n".join(doc["content"] for doc in compressed)

    # 5. 구조화 요약 생성
    logits_processor = None
    if use_cad:
        logits_processor = create_cad_processor(generator, query, alpha=cad_alpha)

    answer = generator.generate(
        query=query,
        context=context,
        template="summary",
        logits_processor=logits_processor,
    )

    sources = generator.format_sources(compressed)

    return {
        "answer": answer,
        "sources": sources,
        "source_documents": compressed,
        "pipeline": "E_summary",
        "steps": steps,
    }
