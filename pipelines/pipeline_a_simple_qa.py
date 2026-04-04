"""
Pipeline A: 단순 QA
쿼리 → HyDE 확장 → 하이브리드 검색 → 재랭킹 → 압축 → 생성 → CAD 억제 → 답변
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
    query_expander=None,
    use_cad: bool = True,
    cad_alpha: float = 0.5,
) -> dict:
    """단순 QA 파이프라인 실행"""
    steps = []

    # 1. 쿼리 확장 (HyDE)
    hyde_doc = None
    if query_expander:
        expansion = query_expander.expand(query, use_hyde=True, use_multi=False)
        hyde_doc = expansion.get("hyde_doc")
        steps.append({"step": "query_expansion", "hyde_used": hyde_doc is not None})

    # 2. 하이브리드 검색
    search_results = hybrid_retriever.search(
        collection_name=collection_name,
        query=query,
        hyde_doc=hyde_doc,
    )
    steps.append({"step": "hybrid_search", "results_count": len(search_results)})

    # 3. 재랭킹
    reranked = reranker.rerank(query, search_results)
    steps.append({"step": "reranking", "top_k": len(reranked)})

    # 4. 컨텍스트 압축
    compressed = compressor.compress(reranked, query, strategy="extractive")
    compressed = compressor.truncate_to_limit(compressed)
    steps.append({"step": "compression", "docs_count": len(compressed)})

    # 5. 컨텍스트 조합
    context = "\n\n---\n\n".join(doc["content"] for doc in compressed)

    # 6. 생성 (+ CAD 환각 억제)
    logits_processor = None
    if use_cad:
        logits_processor = create_cad_processor(generator, query, alpha=cad_alpha)
        steps.append({"step": "cad_enabled", "alpha": cad_alpha})

    answer = generator.generate(
        query=query,
        context=context,
        template="qa",
        logits_processor=logits_processor,
    )

    # 출처 정보
    sources = generator.format_sources(compressed)

    return {
        "answer": answer,
        "sources": sources,
        "source_documents": compressed,
        "pipeline": "A_simple_qa",
        "steps": steps,
    }
