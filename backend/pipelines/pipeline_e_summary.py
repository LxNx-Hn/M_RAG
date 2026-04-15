"""
Pipeline E: structured summary.
"""

import logging

from config import CAD_ALPHA, SCD_BETA
from modules.scd_decoder import create_combined_processor

logger = logging.getLogger(__name__)


def _fallback_response(steps: list[dict], reason: str) -> dict:
    return {
        "answer": "요약할 근거가 충분하지 않습니다. 문서를 다시 업로드하거나 질문 범위를 좁혀 주세요.",
        "sources": "",
        "source_documents": [],
        "pipeline": "E_summary",
        "steps": steps + [{"step": "fallback", "reason": reason, "fallback": True}],
    }


def run(
    query: str,
    collection_name: str,
    hybrid_retriever,
    reranker,
    compressor,
    generator,
    use_cad: bool = True,
    cad_alpha: float = CAD_ALPHA,
    use_scd: bool = True,
    scd_beta: float = SCD_BETA,
) -> dict:
    """Run summary pipeline."""
    steps = []
    all_results = []
    try:
        try:
            vs = hybrid_retriever.vector_store
            collection = vs.get_or_create_collection(collection_name)
            raptor_data = collection.get(
                where={"chunk_level": {"$gte": 1}},
                include=["documents", "metadatas"],
            )
            if raptor_data["ids"]:
                for i in range(len(raptor_data["ids"])):
                    level = raptor_data["metadatas"][i].get("chunk_level", 1)
                    all_results.append(
                        {
                            "chunk_id": raptor_data["ids"][i],
                            "content": raptor_data["documents"][i],
                            "metadata": raptor_data["metadatas"][i],
                            "score": 1.0 + level * 0.1,
                        }
                    )
                steps.append(
                    {"step": "raptor_chunks", "count": len(raptor_data["ids"])}
                )
        except Exception:
            pass

        sections = ["abstract", "introduction", "method", "result", "conclusion"]
        for section in sections:
            results = hybrid_retriever.search(
                collection_name=collection_name,
                query=query,
                section_filter=section,
                top_k=3,
            )
            all_results.extend(results)
            steps.append(
                {"step": f"section_search_{section}", "results_count": len(results)}
            )

        if len(all_results) < 5:
            full_results = hybrid_retriever.search(
                collection_name=collection_name,
                query="summarize the paper main contributions results",
                top_k=10,
            )
            existing_ids = {r["chunk_id"] for r in all_results}
            for result in full_results:
                if result["chunk_id"] not in existing_ids:
                    all_results.append(result)

        if not all_results:
            return _fallback_response(steps, "no_search_results")

        summary_query = "논문 전체 요약: 목적, 방법론, 결과, 의의"
        reranked = reranker.rerank(summary_query, all_results, top_k=8)
        steps.append({"step": "reranking", "top_k": len(reranked)})
        if not reranked:
            return _fallback_response(steps, "no_rerank_results")

        compressed = compressor.compress(reranked, summary_query)
        compressed = compressor.truncate_to_limit(compressed)
        if not compressed:
            return _fallback_response(steps, "no_context_after_compression")

        section_order = {section: idx for idx, section in enumerate(sections)}
        compressed.sort(
            key=lambda doc: section_order.get(
                doc.get("metadata", {}).get("section_type", ""),
                99,
            )
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
            template="summary",
            logits_processor=logits_processor if (use_cad or use_scd) else None,
        )
        sources = generator.format_sources(compressed)

        return {
            "answer": answer,
            "sources": sources,
            "source_documents": compressed,
            "pipeline": "E_summary",
            "steps": steps,
        }
    except Exception as exc:
        logger.error("pipeline_e_summary failed: %s", exc, exc_info=True)
        return {
            "answer": "요약 생성 중 일시적 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
            "sources": "",
            "source_documents": [],
            "pipeline": "E_summary",
            "steps": steps + [{"step": "error", "detail": str(exc)[:200]}],
            "error": True,
        }
