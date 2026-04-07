"""
Pipeline B: 섹션 특화 검색
쿼리 → 섹션 필터 검색 → ColBERT 재랭킹 → 생성 (CAD+SCD) → 답변
"""
import logging

from config import CAD_ALPHA, SCD_BETA
from modules.scd_decoder import create_combined_processor

logger = logging.getLogger(__name__)


def run(
    query: str,
    collection_name: str,
    section_filter: str,
    hybrid_retriever,
    reranker,
    compressor,
    generator,
    use_cad: bool = True,
    cad_alpha: float = CAD_ALPHA,
    use_scd: bool = True,
    scd_beta: float = SCD_BETA,
) -> dict:
    """섹션 특화 파이프라인 실행"""
    steps = []

    # 1. 섹션 필터 하이브리드 검색
    search_results = hybrid_retriever.search(
        collection_name=collection_name,
        query=query,
        section_filter=section_filter,
    )
    steps.append({
        "step": "section_filtered_search",
        "section": section_filter,
        "results_count": len(search_results),
    })

    # 필터 결과가 부족하면 전체 검색으로 보완
    if len(search_results) < 3:
        fallback_results = hybrid_retriever.search(
            collection_name=collection_name,
            query=query,
        )
        existing_ids = {r["chunk_id"] for r in search_results}
        for r in fallback_results:
            if r["chunk_id"] not in existing_ids:
                search_results.append(r)
        steps.append({"step": "fallback_search", "total": len(search_results)})

    # 2. 재랭킹 (섹션 가중치 적용)
    reranked = reranker.rerank(
        query, search_results,
        section_boost=section_filter,
        section_boost_weight=0.15,
    )
    steps.append({"step": "reranking_with_section_boost", "top_k": len(reranked)})

    # 3. 압축
    compressed = compressor.compress(reranked, query)
    compressed = compressor.truncate_to_limit(compressed)

    # 4. 컨텍스트 조합
    context = "\n\n---\n\n".join(doc["content"] for doc in compressed)

    # 5. 생성 (CAD + SCD 병렬 적용)
    logits_processor = create_combined_processor(
        generator=generator,
        query=query,
        use_cad=use_cad,
        cad_alpha=cad_alpha,
        use_scd=use_scd,
        scd_beta=scd_beta,
    )

    answer = generator.generate(
        query=query,
        context=context,
        template="qa",
        logits_processor=logits_processor if (use_cad or use_scd) else None,
    )

    sources = generator.format_sources(compressed)

    return {
        "answer": answer,
        "sources": sources,
        "source_documents": compressed,
        "pipeline": f"B_section_{section_filter}",
        "steps": steps,
    }
