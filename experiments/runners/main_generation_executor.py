"""Execution body for the approved main 8-config HyDE x CAD x SCD generation.

Imported ONLY after every guard in ``run_generation.check_main_generation_guards``
passes, so this module's heavy backend/torch imports never load during planning,
``--help``, or a refused run.

It REUSES the proven fixed-backbone path from ``run_alice_followup.py``:
- retrieval: ``HybridRetriever.search_with_trace`` (BGE-M3 dense + BM25 + RRF)
  + CrossEncoder rerank + ``ContextCompressor``
- HyDE: ``QueryExpander``
- CAD + SCD: ``modules.scd_decoder.create_combined_processor``
- generation: ``modules.generator.Generator`` -- instantiated ONCE per run and
  reused across every (config, query) sample. It is never reloaded per sample.

Records are written with the schema ``experiments/evaluators/official_ragas_runner.py``
consumes (query_id, generated_answer, contexts, context.chunks, config/axis
metadata, retrieval trace, and OpenAI/RAGAS/GT flags all false).
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
BACKEND_DIR = REPO / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from common import (  # noqa: E402
    load_query_split,
    resolve_output_dir,
    validate_main_matrix,
)

APPROVED_COLLECTION = "local_gt__papers"
APPROVED_MAIN_SPLIT = "decoder_main_queries"
APPROVED_MODEL_NAME = "K-intelligence/Midm-2.0-Base-Instruct"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _doc_id_for_query(query: dict[str, Any]) -> str | None:
    for key in ("paper", "doc_id"):
        v = query.get(key)
        if isinstance(v, str) and v:
            return v
    applicable = query.get("applicable_papers")
    if isinstance(applicable, list) and applicable:
        return str(applicable[0])
    return None


def build_components(max_new_tokens: int) -> dict[str, Any]:
    """Construct reused backbone + generation components ONCE."""
    from config import CAD_ALPHA, SCD_BETA
    from modules.context_compressor import ContextCompressor
    from modules.embedder import Embedder
    from modules.generator import Generator
    from modules.hybrid_retriever import HybridRetriever
    from modules.query_expander import QueryExpander
    from modules.reranker import Reranker
    from modules.vector_store import VectorStore

    vector_store = VectorStore()
    embedder = Embedder()
    hybrid = HybridRetriever(vector_store, embedder)
    reranker = Reranker()
    compressor = ContextCompressor()
    generator = Generator(max_new_tokens=max_new_tokens)  # model loaded once, reused
    query_expander = QueryExpander(generator)
    return {
        "hybrid": hybrid,
        "reranker": reranker,
        "compressor": compressor,
        "generator": generator,
        "query_expander": query_expander,
        "default_cad_alpha": CAD_ALPHA,
        "default_scd_beta": SCD_BETA,
    }


def _chunk_records(chunks: list[dict], doc_id: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ch in chunks:
        content = ch.get("content", "") or ""
        meta = ch.get("metadata") or {}
        out.append(
            {
                "chunk_id": ch.get("chunk_id", ""),
                "doc_id": meta.get("doc_id", doc_id),
                "content": content,
                "snippet": content[:400],
            }
        )
    return out


def retrieve_fixed_backbone(
    c: dict[str, Any],
    query: str,
    doc_id: str,
    pool: int,
    rerank_n: int,
    ctx_n: int,
    hyde_doc,
) -> tuple[str, list[dict], dict[str, Any]]:
    hybrid = c["hybrid"]
    if not bool(hybrid.has_bm25_for_collection(APPROVED_COLLECTION)):
        raise RuntimeError("BM25 index missing for local_gt__papers.")
    trace = hybrid.search_with_trace(
        APPROVED_COLLECTION, query, top_k=pool, doc_id_filter=doc_id, hyde_doc=hyde_doc
    )
    if not trace.get("bm25_available"):
        raise RuntimeError("BM25 unavailable at retrieval time.")
    fused = trace.get("fused") or []
    reranked = c["reranker"].rerank(query, fused, top_k=rerank_n)
    ctx_chunks = reranked[:ctx_n]
    if not ctx_chunks:
        raise RuntimeError("no context chunks after rerank.")
    compressed = c["compressor"].compress(ctx_chunks, query, strategy="extractive")
    compressed = c["compressor"].truncate_to_limit(compressed)
    if not compressed:
        raise RuntimeError("no context after compression.")
    context = "\n\n---\n\n".join(d.get("content", "") for d in compressed)
    meta = {
        "retrieval_mode": "fixed_backbone",
        "retrieval_backend": "bge_m3_dense+bm25_sparse+rrf+crossencoder_rerank",
        "retrieval_pool_top_k": pool,
        "rerank_top_n": rerank_n,
        "context_chunk_count": len(compressed),
        "dense_result_count": trace.get("dense_count"),
        "sparse_result_count": trace.get("sparse_count"),
        "fused_result_count": trace.get("fused_count") or len(fused),
        "retrieved_chunk_ids": [x.get("chunk_id", "") for x in fused],
        "reranked_chunk_ids": [x.get("chunk_id", "") for x in compressed],
        "bm25_index_available": True,
        "fallback_used": False,
    }
    return context, compressed, meta


def _flags() -> dict[str, Any]:
    return {
        "openai_used": False,
        "ragas_used": False,
        "gt_regenerated": False,
        "decoder_main_used": True,
        "final_eval_used": False,
        "parameter_freeze_evidence": False,
        # Generation outputs are inputs to the official scored evaluation phase;
        # this flag stays false until that phase produces scored results.
        "thesis_grade_result": False,
        "alice_mode": True,
    }


def execute_main_generation(args, params: dict[str, float]) -> int:
    import torch
    from modules.scd_decoder import create_combined_processor

    rerank_n = int(params.get("rerank_top_n", 5))
    ctx_n = rerank_n
    pool = int(params.get("retrieval_pool_top_k", 20))
    cad_alpha = float(params.get("cad_alpha", 0.5))
    scd_beta = float(params.get("scd_beta", 0.3))
    max_new_tokens = int(params.get("max_new_tokens", 512))

    configs = validate_main_matrix()
    queries = load_query_split(APPROVED_MAIN_SPLIT)
    c = build_components(max_new_tokens)
    gen = c["generator"]

    out_dir = resolve_output_dir(Path(args.output_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = (
        out_dir / f"{args.experiment}__{APPROVED_MAIN_SPLIT}__main_generation.jsonl"
    )

    written = 0
    succeeded = 0
    with out_path.open("w", encoding="utf-8") as f:
        for idx, config in enumerate(configs, start=1):
            for q in queries:
                query = str(q.get("query", ""))
                doc_id = _doc_id_for_query(q)
                status = "succeeded"
                error = None
                answer = ""
                hyde_used = False
                meta: dict[str, Any] = {}
                chunk_recs: list[dict[str, Any]] = []
                start = time.time()
                try:
                    if doc_id is None:
                        raise RuntimeError("query has no resolvable doc_id.")
                    hyde_doc = None
                    if config.use_hyde:
                        corpus_lang = c["hybrid"].get_collection_lang(
                            APPROVED_COLLECTION, doc_id_filter=doc_id
                        )
                        expansion = c["query_expander"].expand(
                            query,
                            use_hyde=True,
                            use_multi=False,
                            corpus_lang=corpus_lang,
                        )
                        hyde_doc = expansion.get("hyde_doc")
                        hyde_used = hyde_doc is not None
                    context, compressed, meta = retrieve_fixed_backbone(
                        c,
                        query,
                        doc_id,
                        pool=pool,
                        rerank_n=rerank_n,
                        ctx_n=ctx_n,
                        hyde_doc=hyde_doc,
                    )
                    chunk_recs = _chunk_records(compressed, doc_id)
                    proc = None
                    if config.use_cad or config.use_scd:
                        proc = create_combined_processor(
                            generator=gen,
                            query=query,
                            use_cad=config.use_cad,
                            cad_alpha=cad_alpha,
                            use_scd=config.use_scd,
                            scd_beta=scd_beta,
                        )
                    answer = gen.generate(
                        query=query,
                        context=context,
                        template="qa",
                        logits_processor=proc,
                        force_greedy=True,
                    )
                except torch.cuda.OutOfMemoryError as exc:
                    status = "failed"
                    error = {"type": "CudaOutOfMemoryError", "message": str(exc)[:1000]}
                except Exception as exc:  # noqa: BLE001
                    status = "failed"
                    error = {"type": type(exc).__name__, "message": str(exc)[:1000]}

                rec = {
                    "phase": "main_hyde_cad_scd_generation",
                    "experiment": args.experiment,
                    "config_id": f"{args.experiment}:{idx:02d}:{config.name}",
                    "config_name": config.name,
                    "status": status,
                    "query_id": q.get("query_id"),
                    "query": query,
                    "paper": doc_id,
                    "retrieval_mode": "fixed_backbone",
                    "use_hyde": config.use_hyde,
                    "hyde_used": hyde_used,
                    "use_cad": config.use_cad,
                    "cad_alpha": cad_alpha if config.use_cad else None,
                    "use_scd": config.use_scd,
                    "scd_beta": scd_beta if config.use_scd else None,
                    "decoding_mode": "deterministic_greedy",
                    "generation_model": APPROVED_MODEL_NAME,
                    "max_new_tokens": max_new_tokens,
                    "generated_answer": answer,
                    "contexts": [r["content"] for r in chunk_recs],
                    "context": {
                        "collection_name": APPROVED_COLLECTION,
                        "doc_id_filter": doc_id,
                        "chunks": chunk_recs,
                        "context_available": bool(answer) and status == "succeeded",
                    },
                    "evidence_class": "main_hyde_cad_scd_generation",
                    "duration_seconds": round(time.time() - start, 3),
                    "error": error,
                    "note": "main generation output; scored quality is produced by the official evaluation phase",
                    **(
                        meta
                        or {"retrieval_mode": "fixed_backbone", "fallback_used": False}
                    ),
                    **_flags(),
                    "start_time": _now_iso(),
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written += 1
                if status == "succeeded":
                    succeeded += 1

    print(f"WROTE {written} records ({succeeded} succeeded) -> {out_path}")
    print(
        f"configs={len(configs)} queries={len(queries)} expected={len(configs) * len(queries)}"
    )
    return 0 if written == len(configs) * len(queries) else 1
