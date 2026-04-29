"""
Pipeline B: section-focused QA.
"""

import logging

from config import CAD_ALPHA, SCD_BETA
from modules.scd_decoder import create_combined_processor

logger = logging.getLogger(__name__)


def _fallback_response(pipeline: str, steps: list[dict], reason: str) -> dict:
    return {
        "answer": "제공된 문서에서 해당 섹션의 근거를 찾지 못했습니다. 섹션 키워드를 바꿔 다시 시도해 주세요.",
        "sources": "",
        "source_documents": [],
        "pipeline": pipeline,
        "steps": steps + [{"step": "fallback", "reason": reason, "fallback": True}],
    }


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
    doc_id_filter: str | None = None,
    query_expander=None,
    use_hyde: bool = False,
) -> dict:
    """Run section-specific pipeline."""
    steps = []
    pipeline_name = f"B_section_{section_filter}"
    try:
        hyde_doc = None
        if query_expander and use_hyde:
            corpus_lang = hybrid_retriever.get_collection_lang(
                collection_name,
                doc_id_filter=doc_id_filter,
            )
            expansion = query_expander.expand(
                query,
                use_hyde=True,
                use_multi=False,
                corpus_lang=corpus_lang,
            )
            hyde_doc = expansion.get("hyde_doc")
            steps.append(
                {
                    "step": "query_expansion",
                    "hyde_used": hyde_doc is not None,
                    "corpus_lang": corpus_lang,
                }
            )
        else:
            steps.append({"step": "query_expansion", "hyde_used": False})

        search_results = hybrid_retriever.search(
            collection_name=collection_name,
            query=query,
            hyde_doc=hyde_doc,
            section_filter=section_filter,
            doc_id_filter=doc_id_filter,
        )
        steps.append(
            {
                "step": "section_filtered_search",
                "section": section_filter,
                "results_count": len(search_results),
            }
        )

        if len(search_results) < 3:
            fallback_results = hybrid_retriever.search(
                collection_name=collection_name,
                query=query,
                hyde_doc=hyde_doc,
                doc_id_filter=doc_id_filter,
            )
            existing_ids = {r["chunk_id"] for r in search_results}
            for result in fallback_results:
                if result["chunk_id"] not in existing_ids:
                    search_results.append(result)
            steps.append({"step": "fallback_search", "total": len(search_results)})

        if not search_results:
            return _fallback_response(pipeline_name, steps, "no_search_results")

        reranked = reranker.rerank(
            query,
            search_results,
            section_boost=section_filter,
            section_boost_weight=0.15,
        )
        steps.append({"step": "reranking_with_section_boost", "top_k": len(reranked)})
        if not reranked:
            return _fallback_response(pipeline_name, steps, "no_rerank_results")

        compressed = compressor.compress(reranked, query)
        compressed = compressor.truncate_to_limit(compressed)
        if not compressed:
            return _fallback_response(
                pipeline_name, steps, "no_context_after_compression"
            )

        context = "\n\n---\n\n".join(doc["content"] for doc in compressed)
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
            force_greedy=use_cad,
        )
        sources = generator.format_sources(compressed)

        return {
            "answer": answer,
            "sources": sources,
            "source_documents": compressed,
            "pipeline": pipeline_name,
            "steps": steps,
        }
    except Exception as exc:
        logger.error("pipeline_b_section failed: %s", exc, exc_info=True)
        return {
            "answer": "답변 생성 중 일시적 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
            "sources": "",
            "source_documents": [],
            "pipeline": pipeline_name,
            "steps": steps + [{"step": "error", "detail": str(exc)[:200]}],
            "error": True,
        }
