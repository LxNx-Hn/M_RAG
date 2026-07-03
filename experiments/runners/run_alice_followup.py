"""Phase 7.6B-3 (40GB worst-case memory probe) + Phase 7.6C (small tuning
comparison) follow-up runner for Alice.

This is a NARROWLY SCOPED adapter. It REUSES existing components only:
- fixed-backbone retrieval: HybridRetriever.search_with_trace (BGE-M3 dense +
  BM25 sparse + RRF) + CrossEncoder reranker + ContextCompressor
- HyDE: modules.query_expander.QueryExpander
- CAD + SCD: modules.scd_decoder.create_combined_processor (CADDecoder + SCDDecoder)
- generation: modules.generator.Generator (instantiated ONCE and reused)

It NEVER uses run_generation.py / decoder_main / the 8-config main matrix, never
runs final evaluation or parameter freeze, never imports or calls OpenAI/RAGAS,
never regenerates GT, and never creates or duplicates queries. Hard scope guards
fail closed.

Modes:
- memory-probe : exactly ONE sample, HyDE on + CAD on + SCD on (heaviest path),
                 captures peak VRAM. Hard-limited to 1 record.
- tuning-7c    : fixed-backbone BASELINE axis (no HyDE/CAD/SCD), exactly 5 tuning
                 queries x up to 3 allow-listed profiles, hard-limited to 15
                 records. Tuning evidence only -- NOT parameter freeze.
"""

from __future__ import annotations

import argparse
import json
import os
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

QUERY_SPLITS_DIR = REPO / "experiments" / "data" / "query_splits"
DEFAULT_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"
DEFAULT_COLLECTION = "local_gt__papers"
EXPECTED_SPLIT = "tuning_queries"
DOC_ID = "paper_nlp_bge"

REFUSED_SPLITS = {
    "decoder_main_queries",
    "candidate_final_eval_queries",
    "query_type_analysis_queries",
    "service_route_queries",
    "query_templates",
}

# Profiles allowed for the 7.6C tuning comparison. Subset of
# experiments/configs/tuning_plan.yaml staged_candidate_profiles. Baseline-axis
# retrieval-breadth variants only; no invented names or values.
ALLOWED_PROFILES: dict[str, dict[str, int]] = {
    "current_defaults": {
        "retrieval_pool_top_k": 20,
        "rerank_top_n": 5,
        "context_chunk_count": 5,
    },
    "retrieval_conservative": {
        "retrieval_pool_top_k": 3,
        "rerank_top_n": 3,
        "context_chunk_count": 3,
    },
    "retrieval_recall_oriented": {
        "retrieval_pool_top_k": 8,
        "rerank_top_n": 8,
        "context_chunk_count": 5,
    },
    "retrieval_broad_then_default_rerank": {
        "retrieval_pool_top_k": 8,
        "rerank_top_n": 5,
        "context_chunk_count": 5,
    },
}


class FollowupBlocked(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_queries(limit: int) -> list[dict[str, Any]]:
    path = QUERY_SPLITS_DIR / f"{EXPECTED_SPLIT}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("queries", data)
    if not isinstance(items, list):
        raise FollowupBlocked("tuning_queries.json is not a list of queries")
    return items[:limit]


def assert_global_guards(args: argparse.Namespace) -> None:
    if os.environ.get("CONFIRM_ALICE_FOLLOWUP") != "1":
        raise FollowupBlocked("CONFIRM_ALICE_FOLLOWUP=1 is required.")
    if os.environ.get("OPENAI_ENABLED", "0") != "0":
        raise FollowupBlocked("OpenAI must be disabled (OPENAI_ENABLED=0).")
    if os.environ.get("RAGAS_ENABLED", "0") != "0":
        raise FollowupBlocked("RAGAS must be disabled (RAGAS_ENABLED=0).")
    if args.collection_name != DEFAULT_COLLECTION:
        raise FollowupBlocked("collection must be local_gt__papers.")
    if args.generation_model != DEFAULT_MODEL:
        raise FollowupBlocked("model must be MIDM BASE.")
    if args.query_split != EXPECTED_SPLIT or args.query_split in REFUSED_SPLITS:
        raise FollowupBlocked("only tuning_queries is allowed.")


def vram_snapshot(torch) -> dict[str, Any]:
    out: dict[str, Any] = {"gpu_name": None, "vram_total_gb": None}
    if torch.cuda.is_available():
        out["gpu_name"] = torch.cuda.get_device_name(0)
        try:
            free, total = torch.cuda.mem_get_info()
            out["vram_total_gb"] = round(total / 1e9, 3)
            out["vram_free_gb"] = round(free / 1e9, 3)
        except Exception as exc:
            out["vram_info_error"] = str(exc)[:200]
    return out


def build_components():
    """Construct the reused backbone + generation components ONCE."""
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
    generator = Generator()  # lazy model load; reused across all samples
    query_expander = QueryExpander(generator)
    return {
        "vector_store": vector_store,
        "embedder": embedder,
        "hybrid": hybrid,
        "reranker": reranker,
        "compressor": compressor,
        "generator": generator,
        "query_expander": query_expander,
        "cad_alpha": CAD_ALPHA,
        "scd_beta": SCD_BETA,
    }


def _chunk_ids(items: list[dict]) -> list[str]:
    return [c.get("chunk_id", "") for c in items]


def _chunk_records(items: list[dict]) -> list[dict[str, Any]]:
    """Full chunk texts for the record. Chunk IDs alone are NOT recoverable
    off-instance (extraction is environment-sensitive), so every scoreable
    record must inline the context contents the generator conditioned on."""
    out: list[dict[str, Any]] = []
    for c in items:
        content = c.get("content", "") or ""
        meta = c.get("metadata") or {}
        out.append(
            {
                "chunk_id": c.get("chunk_id", ""),
                "doc_id": meta.get("doc_id", DOC_ID),
                "content": content,
                "snippet": content[:400],
            }
        )
    return out


def _doc_ids(items: list[dict]) -> list[str]:
    ids: list[str] = []
    for it in items:
        did = (it.get("metadata") or {}).get("doc_id", DOC_ID)
        if did and did not in ids:
            ids.append(did)
    return ids


def retrieve_fixed_backbone(
    c, query: str, pool: int, rerank_n: int, ctx_n: int, hyde_doc
):
    hybrid = c["hybrid"]
    if not bool(hybrid.has_bm25_for_collection(DEFAULT_COLLECTION)):
        raise FollowupBlocked("BM25 index missing for local_gt__papers.")
    trace = hybrid.search_with_trace(
        DEFAULT_COLLECTION, query, top_k=pool, doc_id_filter=DOC_ID, hyde_doc=hyde_doc
    )
    if not trace.get("bm25_available"):
        raise FollowupBlocked("BM25 unavailable at retrieval time.")
    fused = trace.get("fused") or []
    reranked = c["reranker"].rerank(query, fused, top_k=rerank_n)
    ctx_chunks = reranked[:ctx_n]
    if not ctx_chunks:
        raise FollowupBlocked("no context chunks after rerank.")
    compressed = c["compressor"].compress(ctx_chunks, query, strategy="extractive")
    compressed = c["compressor"].truncate_to_limit(compressed)
    if not compressed:
        raise FollowupBlocked("no context after compression.")
    context = "\n\n---\n\n".join(d.get("content", "") for d in compressed)
    chunk_records = _chunk_records(compressed)
    meta = {
        "retrieval_mode": "fixed_backbone",
        "retrieval_backend": "bge_m3_dense+bm25_sparse+rrf+crossencoder_rerank",
        "retrieval_pool_top_k": pool,
        "rerank_top_n": rerank_n,
        "context_chunk_count": len(compressed),
        "dense_result_count": trace.get("dense_count"),
        "sparse_result_count": trace.get("sparse_count"),
        "fused_result_count": trace.get("fused_count") or len(fused),
        "retrieved_chunk_ids": _chunk_ids(fused),
        "reranked_chunk_ids": _chunk_ids(ctx_chunks),
        "retrieved_doc_ids": _doc_ids(ctx_chunks),
        # Inline context texts: required by official_ragas_runner and NOT
        # recoverable from chunk IDs off-instance.
        "contexts": [r["content"] for r in chunk_records],
        "context_chunks": chunk_records,
        "bm25_index_available": True,
        "fallback_used": False,
    }
    return context, compressed, meta


def base_flags() -> dict[str, Any]:
    return {
        "openai_used": False,
        "ragas_used": False,
        "gt_regenerated": False,
        "decoder_main_used": False,
        "final_eval_used": False,
        "parameter_freeze_evidence": False,
        "thesis_grade_result": False,
        "alice_mode": True,
    }


def run_memory_probe(args, c) -> list[dict[str, Any]]:
    import torch
    from modules.scd_decoder import create_combined_processor

    queries = load_queries(1)  # hard 1-sample
    q = queries[0]
    query = q["query"]
    gen = c["generator"]

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    start = time.time()
    cuda_oom = False
    status = "succeeded"
    error = None
    answer = ""
    meta: dict[str, Any] = {}
    hyde_used = False
    try:
        corpus_lang = c["hybrid"].get_collection_lang(
            DEFAULT_COLLECTION, doc_id_filter=DOC_ID
        )
        expansion = c["query_expander"].expand(
            query, use_hyde=True, use_multi=False, corpus_lang=corpus_lang
        )
        hyde_doc = expansion.get("hyde_doc")
        hyde_used = hyde_doc is not None
        context, compressed, meta = retrieve_fixed_backbone(
            c, query, pool=20, rerank_n=5, ctx_n=5, hyde_doc=hyde_doc
        )
        proc = create_combined_processor(
            generator=gen,
            query=query,
            use_cad=True,
            cad_alpha=c["cad_alpha"],
            use_scd=True,
            scd_beta=c["scd_beta"],
        )
        answer = gen.generate(
            query=query,
            context=context,
            template="qa",
            logits_processor=proc,
            force_greedy=True,
        )
    except torch.cuda.OutOfMemoryError as exc:
        cuda_oom = True
        status = "failed"
        error = {"type": "CudaOutOfMemoryError", "message": str(exc)[:1000]}
    except Exception as exc:
        status = "failed"
        error = {"type": type(exc).__name__, "message": str(exc)[:1000]}

    vram = vram_snapshot(torch)
    peak_alloc = peak_reserved = None
    if torch.cuda.is_available():
        peak_alloc = round(torch.cuda.max_memory_allocated() / 1e9, 3)
        peak_reserved = round(torch.cuda.max_memory_reserved() / 1e9, 3)

    rec = {
        "phase": "phase7_6B3_worstcase_memory_probe",
        "mode": "memory_probe",
        "status": status,
        "query_id": q.get("query_id"),
        "query": query,
        "paper": DOC_ID,
        "retrieval_mode": "fixed_backbone",
        "use_hyde": True,
        "hyde_used": hyde_used,
        "use_cad": True,
        "cad_alpha": c["cad_alpha"],
        "use_scd": True,
        "scd_beta": c["scd_beta"],
        "decoding_mode": "cad_scd_greedy",
        "generated_answer": answer,
        "context": {
            "collection_name": DEFAULT_COLLECTION,
            "doc_id_filter": DOC_ID,
            "context_available": bool(answer) and status == "succeeded",
        },
        "gpu_name": vram.get("gpu_name"),
        "vram_total_gb": vram.get("vram_total_gb"),
        "vram_free_gb_after": vram.get("vram_free_gb"),
        "peak_allocated_gb": peak_alloc,
        "peak_reserved_gb": peak_reserved,
        "cuda_oom": cuda_oom,
        "evidence_class": "retrieval_backbone_memory_probe",
        "duration_seconds": round(time.time() - start, 3),
        "error": error,
        "note": "worst-case HyDE+CAD+SCD feasibility probe; not parameter freeze or final result",
        **(meta or {"retrieval_mode": "fixed_backbone", "fallback_used": False}),
        **base_flags(),
        "start_time": now_iso(),
    }
    return [rec]


def run_tuning_7c(args, c) -> list[dict[str, Any]]:
    profiles = [p.strip() for p in args.profiles.split(",") if p.strip()]
    if "current_defaults" not in profiles:
        raise FollowupBlocked("7.6C must include current_defaults.")
    if len(profiles) > 3:
        raise FollowupBlocked("7.6C allows at most 3 profiles.")
    for p in profiles:
        if p not in ALLOWED_PROFILES:
            raise FollowupBlocked(f"profile not in allow-list: {p}")
    queries = load_queries(5)
    if len(queries) != 5:
        raise FollowupBlocked("7.6C requires exactly 5 tuning queries.")
    if len(profiles) * 5 > 15:
        raise FollowupBlocked("7.6C hard cap is 15 records.")

    gen = c["generator"]
    records: list[dict[str, Any]] = []
    for profile_id in profiles:
        params = ALLOWED_PROFILES[profile_id]
        for q in queries:
            query = q["query"]
            status = "succeeded"
            error = None
            answer = ""
            meta: dict[str, Any] = {}
            start = time.time()
            try:
                context, compressed, meta = retrieve_fixed_backbone(
                    c,
                    query,
                    pool=params["retrieval_pool_top_k"],
                    rerank_n=params["rerank_top_n"],
                    ctx_n=params["context_chunk_count"],
                    hyde_doc=None,
                )
                answer = gen.generate(
                    query=query,
                    context=context,
                    template="qa",
                    logits_processor=None,
                    force_greedy=True,
                )
            except Exception as exc:
                status = "failed"
                error = {"type": type(exc).__name__, "message": str(exc)[:1000]}
            rec = {
                "phase": "phase7_6C_small_tuning_comparison",
                "mode": "tuning_7c",
                "profile_id": profile_id,
                "profile_overrides": params,
                "status": status,
                "query_id": q.get("query_id"),
                "query": query,
                "paper": DOC_ID,
                "retrieval_mode": "fixed_backbone",
                "use_hyde": False,
                "use_cad": False,
                "use_scd": False,
                "decoding_mode": "deterministic_greedy",
                "generated_answer": answer,
                "context": {
                    "collection_name": DEFAULT_COLLECTION,
                    "doc_id_filter": DOC_ID,
                    "context_available": bool(answer) and status == "succeeded",
                },
                "evidence_class": "retrieval_backbone_tuning_comparison",
                "duration_seconds": round(time.time() - start, 3),
                "error": error,
                "note": "tuning evidence only; not parameter freeze or final result",
                **(
                    meta or {"retrieval_mode": "fixed_backbone", "fallback_used": False}
                ),
                **base_flags(),
                "start_time": now_iso(),
            }
            records.append(rec)
    if len(records) > 15:
        raise FollowupBlocked("record cap exceeded.")
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["memory-probe", "tuning-7c"], required=True)
    parser.add_argument("--query-split", default=EXPECTED_SPLIT)
    parser.add_argument("--collection-name", default=DEFAULT_COLLECTION)
    parser.add_argument("--generation-model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--profiles",
        default="current_defaults,retrieval_conservative,retrieval_recall_oriented",
    )
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()

    try:
        assert_global_guards(args)
        c = build_components()
        if args.mode == "memory-probe":
            records = run_memory_probe(args, c)
        else:
            records = run_tuning_7c(args, c)
    except FollowupBlocked as exc:
        print(f"REFUSED: {exc}")
        return 2

    out = Path(args.output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    succeeded = sum(1 for r in records if r.get("status") == "succeeded")
    print(f"WROTE {len(records)} records ({succeeded} succeeded) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
