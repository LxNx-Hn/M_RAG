"""
Pipeline C: pairwise document comparison.
"""
import logging
from concurrent.futures import ThreadPoolExecutor

from config import CAD_ALPHA, SCD_BETA
from modules.scd_decoder import create_combined_processor

logger = logging.getLogger(__name__)


def _fallback_response(steps: list[dict], reason: str) -> dict:
    return {
        "answer": "Comparison context was insufficient. Please upload clearer source documents and try again.",
        "sources": "",
        "source_documents": [],
        "pipeline": "C_compare",
        "steps": steps + [{"step": "fallback", "reason": reason, "fallback": True}],
    }


def run(
    query: str,
    collection_name: str,
    target_doc_ids: list[str],
    hybrid_retriever,
    reranker,
    compressor,
    generator,
    use_cad: bool = True,
    cad_alpha: float = CAD_ALPHA,
    use_scd: bool = True,
    scd_beta: float = SCD_BETA,
) -> dict:
    """Run pairwise comparison pipeline."""
    steps = []
    try:
        if len(target_doc_ids) < 2:
            return {
                "answer": "At least two documents are required for comparison.",
                "sources": "",
                "source_documents": [],
                "pipeline": "C_compare",
                "steps": [{"step": "error", "reason": "insufficient_docs"}],
            }
        if len(target_doc_ids) > 2:
            return {
                "answer": "Comparison currently supports exactly two documents. Please specify two targets.",
                "sources": "",
                "source_documents": [],
                "pipeline": "C_compare",
                "steps": [{"step": "error", "reason": "too_many_docs", "max_supported": 2}],
            }

        doc_contexts: dict[str, list[dict]] = {}

        def search_for_doc(doc_id: str):
            results = hybrid_retriever.search(
                collection_name=collection_name,
                query=query,
                doc_id_filter=doc_id,
            )
            reranked = reranker.rerank(query, results)
            compressed = compressor.compress(reranked, query)
            return doc_id, compressed

        search_doc_ids = target_doc_ids[:2]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(search_for_doc, doc_id) for doc_id in search_doc_ids]
            for future in futures:
                doc_id, docs = future.result()
                doc_contexts[doc_id] = docs

        steps.append(
            {
                "step": "parallel_search",
                "docs_searched": list(doc_contexts.keys()),
                "results_per_doc": {k: len(v) for k, v in doc_contexts.items()},
            }
        )

        if not doc_contexts:
            return _fallback_response(steps, "no_doc_contexts")

        all_docs = []
        context_parts = {}
        for doc_id, docs in doc_contexts.items():
            if docs:
                context_parts[doc_id] = "\n\n".join(d["content"] for d in docs)
                all_docs.extend(docs)

        if len(context_parts) < 2:
            return _fallback_response(steps, "insufficient_contexts")

        doc_ids = list(context_parts.keys())
        context_a = context_parts.get(doc_ids[0], "")
        context_b = context_parts.get(doc_ids[1], "")

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
            context=context_a,
            template="compare",
            logits_processor=logits_processor if (use_cad or use_scd) else None,
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
    except Exception as exc:
        logger.error("pipeline_c_compare failed: %s", exc, exc_info=True)
        return {
            "answer": "A temporary error occurred while generating a comparison answer.",
            "sources": "",
            "source_documents": [],
            "pipeline": "C_compare",
            "steps": steps + [{"step": "error", "detail": str(exc)[:200]}],
            "error": True,
        }

