"""
Pipeline C: 멀티 논문 비교
쿼리 → 논문A 병렬 검색 + 논문B 병렬 검색 → 합성 → 비교 생성 → 답변
"""
import logging
from concurrent.futures import ThreadPoolExecutor

from modules.contrastive_decoder import create_cad_processor

logger = logging.getLogger(__name__)


def run(
    query: str,
    collection_name: str,
    target_doc_ids: list[str],
    hybrid_retriever,
    reranker,
    compressor,
    generator,
    use_cad: bool = True,
    cad_alpha: float = 0.5,
) -> dict:
    """멀티 논문 비교 파이프라인 실행"""
    steps = []

    if len(target_doc_ids) < 2:
        return {
            "answer": "비교할 논문이 2개 이상 필요합니다. 업로드된 논문을 확인해주세요.",
            "sources": "",
            "source_documents": [],
            "pipeline": "C_compare",
            "steps": [{"step": "error", "reason": "insufficient_docs"}],
        }

    # 1. 각 논문별 병렬 검색
    doc_contexts = {}

    def search_for_doc(doc_id):
        results = hybrid_retriever.search(
            collection_name=collection_name,
            query=query,
            doc_id_filter=doc_id,
        )
        reranked = reranker.rerank(query, results)
        compressed = compressor.compress(reranked, query)
        return doc_id, compressed

    with ThreadPoolExecutor(max_workers=len(target_doc_ids)) as executor:
        futures = [executor.submit(search_for_doc, doc_id) for doc_id in target_doc_ids[:4]]
        for future in futures:
            doc_id, docs = future.result()
            doc_contexts[doc_id] = docs

    steps.append({
        "step": "parallel_search",
        "docs_searched": list(doc_contexts.keys()),
        "results_per_doc": {k: len(v) for k, v in doc_contexts.items()},
    })

    # 2. 컨텍스트 합성
    all_docs = []
    context_parts = {}
    for doc_id, docs in doc_contexts.items():
        context_text = "\n\n".join(d["content"] for d in docs)
        context_parts[doc_id] = context_text
        all_docs.extend(docs)

    # 3. 비교 생성
    doc_ids = list(context_parts.keys())
    context_a = context_parts.get(doc_ids[0], "")
    context_b = context_parts.get(doc_ids[1], "")

    logits_processor = None
    if use_cad:
        logits_processor = create_cad_processor(generator, query, alpha=cad_alpha)

    answer = generator.generate(
        query=query,
        context=context_a,
        template="compare",
        logits_processor=logits_processor,
        context_a=context_a,
        context_b=context_b,
    )

    sources = generator.format_sources(all_docs)

    return {
        "answer": answer,
        "sources": sources,
        "source_documents": all_docs,
        "pipeline": "C_compare",
        "compared_docs": doc_ids,
        "steps": steps,
    }
