"""
Pipeline C: pairwise document comparison.
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from config import CAD_ALPHA, SCD_BETA
from modules.scd_decoder import create_combined_processor

logger = logging.getLogger(__name__)


def _selection_fields(target_selection: dict | None) -> dict:
    if not target_selection:
        return {}
    return {
        "target_selection_method": target_selection.get("target_selection_method", ""),
        "target_selection_reason": target_selection.get("target_selection_reason", ""),
        "fallback_used": bool(target_selection.get("fallback_used", False)),
        "candidate_scores": target_selection.get("candidate_scores", {}),
    }


def _target_selection_step(target_selection: dict | None) -> dict | None:
    if not target_selection:
        return None
    step = {
        "step": "target_selection",
        "target_doc_ids": target_selection.get("target_doc_ids", []),
        "target_selection_method": target_selection.get("target_selection_method", ""),
        "target_selection_reason": target_selection.get("target_selection_reason", ""),
        "selection_reason": target_selection.get("target_selection_reason", ""),
        "fallback_used": bool(target_selection.get("fallback_used", False)),
    }
    candidate_scores = target_selection.get("candidate_scores")
    if candidate_scores:
        step["candidate_scores"] = candidate_scores
    return step


def _fallback_response(
    steps: list[dict],
    reason: str,
    target_selection: dict | None = None,
    compared_docs: list[str] | None = None,
) -> dict:
    return {
        "answer": "Comparison context was insufficient. Please upload clearer source documents and try again.",
        "sources": "",
        "source_documents": [],
        "pipeline": "C_compare",
        "compared_docs": compared_docs or [],
        "steps": steps + [{"step": "fallback", "reason": reason, "fallback": True}],
        **_selection_fields(target_selection),
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
    target_selection: dict | None = None,
) -> dict:
    """Run pairwise comparison pipeline."""
    steps = []
    selection_step = _target_selection_step(target_selection)
    if selection_step:
        steps.append(selection_step)
    try:
        if len(target_doc_ids) < 2:
            return {
                "answer": "At least two uploaded documents are required for comparison. Upload another paper or choose two compare targets.",
                "sources": "",
                "source_documents": [],
                "pipeline": "C_compare",
                "compared_docs": target_doc_ids,
                "steps": steps + [{"step": "error", "reason": "insufficient_docs"}],
                **_selection_fields(target_selection),
            }
        if len(target_doc_ids) > 2:
            return {
                "answer": "Comparison requires exactly two target documents. Please provide exactly two IDs.",
                "sources": "",
                "source_documents": [],
                "pipeline": "C_compare",
                "compared_docs": target_doc_ids,
                "steps": steps
                + [{"step": "error", "reason": "too_many_docs", "max_supported": 2}],
                **_selection_fields(target_selection),
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
            futures = [
                executor.submit(search_for_doc, doc_id) for doc_id in search_doc_ids
            ]
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
            return _fallback_response(
                steps,
                "no_doc_contexts",
                target_selection=target_selection,
                compared_docs=search_doc_ids,
            )

        all_docs = []
        context_parts = {}
        for doc_id, docs in doc_contexts.items():
            if docs:
                context_parts[doc_id] = "\n\n".join(d["content"] for d in docs)
                all_docs.extend(docs)

        if len(context_parts) < 2:
            return _fallback_response(
                steps,
                "insufficient_contexts",
                target_selection=target_selection,
                compared_docs=search_doc_ids,
            )

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
            force_greedy=use_cad,
        )
        sources = generator.format_sources(all_docs)

        return {
            "answer": answer,
            "sources": sources,
            "source_documents": all_docs,
            "pipeline": "C_compare",
            "compared_docs": doc_ids,
            "steps": steps,
            **_selection_fields(target_selection),
        }
    except Exception as exc:
        logger.error("pipeline_c_compare failed: %s", exc, exc_info=True)
        return {
            "answer": "A temporary error occurred while generating a comparison answer.",
            "sources": "",
            "source_documents": [],
            "pipeline": "C_compare",
            "compared_docs": target_doc_ids[:2],
            "steps": steps + [{"step": "error", "detail": str(exc)[:200]}],
            "error": True,
            **_selection_fields(target_selection),
        }
