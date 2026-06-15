"""Alice tuning execution adapter.

This runner is intentionally narrow. It supports:
1. Phase 7.6A one-sample adapter smoke.
2. Phase 7.6B limited current-defaults tuning with at most five tuning queries.
3. Phase 7.6B-2A one-sample query-aware fixed-backbone retrieval smoke.

It refuses decoder_main/final/service/template splits and never imports OpenAI or RAGAS.

Retrieval modes
---------------
- ``doc_filter_sample``: metadata-only vector-store sample
  (``collection.get(where={doc_id})``). This is NOT query-aware retrieval. The
  query text is ignored and the first N chunks of the document are returned.
  Evidence grade is ``execution_smoke_only``.
- ``fixed_backbone``: the real query-aware Paper-RAG backbone, i.e. BGE-M3 dense
  retrieval + BM25 sparse retrieval + RRF fusion + CrossEncoder reranking, using
  the query text and an applicable-paper ``doc_id`` filter. It fails closed
  before generation when the BM25 index is missing or retrieval is empty. It
  never silently falls back to dense-only. Evidence grade is
  ``retrieval_backbone_smoke``.

No retrieval, embedding, reranking, or generation is executed at import time.
Heavy backend modules are imported lazily only when a real run is requested.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from run_local_smoke import SmokeBlockedError, generate_answer, load_context_chunks

DEFAULT_SMOKE_OUTPUT = (
    ROOT
    / "experiments/results/tuning/phase7_6A_alice_tuning_adapter_smoke_1sample.jsonl"
)
DEFAULT_LIMITED_OUTPUT = (
    ROOT
    / "experiments/results/tuning/phase7_6B_limited_tuning_current_defaults_5samples.jsonl"
)
DEFAULT_FIXED_BACKBONE_SMOKE_OUTPUT = (
    ROOT
    / "experiments/results/tuning/phase7_6B2A_fixed_backbone_retrieval_smoke_1sample.jsonl"
)
QUERY_SPLITS_DIR = ROOT / "experiments/data/query_splits"
DEFAULT_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"
DEFAULT_COLLECTION = "local_gt__papers"
EXPECTED_SPLIT = "tuning_queries"
EXPECTED_PROFILE = "current_defaults"
EXPECTED_AXIS_CONFIG = "hyde_off__no_decoder_control"
EXPECTED_FLAGS = {"use_hyde": False, "use_cad": False, "use_scd": False}
REFUSED_SPLITS = {
    "decoder_main_queries",
    "candidate_final_eval_queries",
    "query_templates",
    "service_route_queries",
}

# Retrieval mode contract.
DOC_FILTER_SAMPLE = "doc_filter_sample"
FIXED_BACKBONE = "fixed_backbone"
RETRIEVAL_MODES = {DOC_FILTER_SAMPLE, FIXED_BACKBONE}
EVIDENCE_CLASS_BY_MODE = {
    DOC_FILTER_SAMPLE: "execution_smoke_only",
    FIXED_BACKBONE: "retrieval_backbone_smoke",
}

# Parameter semantics (kept distinct on purpose):
# - retrieval_pool_top_k: initial dense + BM25 candidate pool (backend TOP_K_RETRIEVAL).
# - rerank_top_n: number of documents kept after CrossEncoder reranking (backend TOP_K_RERANK).
# - context_chunk_count: number of final chunks handed to generation.
DEFAULT_RETRIEVAL_POOL_TOP_K = 20
DEFAULT_RERANK_TOP_N = 5
DEFAULT_CONTEXT_CHUNK_COUNT = 5


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run guarded Alice tuning modes.")
    parser.add_argument("--execute-tuning-smoke", action="store_true")
    parser.add_argument("--confirm-alice-base", action="store_true")
    parser.add_argument("--execute-limited-tuning", action="store_true")
    parser.add_argument("--confirm-alice-limited-tuning", action="store_true")
    parser.add_argument("--query-split", default=EXPECTED_SPLIT)
    parser.add_argument("--query-limit", type=int, default=1)
    parser.add_argument("--max-samples", type=int, default=1)
    parser.add_argument(
        "--query-id",
        default=None,
        help="If set, the selected query must match this id.",
    )
    parser.add_argument("--profile", default=EXPECTED_PROFILE)
    parser.add_argument("--axis-config", default=EXPECTED_AXIS_CONFIG)
    parser.add_argument("--generation-model", default=DEFAULT_MODEL)
    parser.add_argument("--model-variant", choices=["base"], default="base")
    parser.add_argument(
        "--model-role",
        default="alice_thesis_tuning_smoke",
        help="Model role metadata written to output records.",
    )
    parser.add_argument("--collection-name", default=DEFAULT_COLLECTION)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    # Retrieval mode + parameter semantics.
    parser.add_argument(
        "--retrieval-mode",
        choices=sorted(RETRIEVAL_MODES),
        default=DOC_FILTER_SAMPLE,
        help="doc_filter_sample (metadata sample, not query-aware) or fixed_backbone (real backbone).",
    )
    parser.add_argument(
        "--context-limit",
        type=int,
        default=3,
        help="doc_filter_sample only: max metadata-sample chunks (collection.get limit).",
    )
    parser.add_argument(
        "--retrieval-pool-top-k",
        type=int,
        default=DEFAULT_RETRIEVAL_POOL_TOP_K,
        help="fixed_backbone only: initial dense + BM25 candidate pool size.",
    )
    parser.add_argument(
        "--rerank-top-n",
        type=int,
        default=DEFAULT_RERANK_TOP_N,
        help="fixed_backbone only: documents kept after CrossEncoder reranking.",
    )
    parser.add_argument(
        "--context-chunk-count",
        type=int,
        default=DEFAULT_CONTEXT_CHUNK_COUNT,
        help="fixed_backbone only: final chunks handed to generation.",
    )
    parser.add_argument("--output-file")
    return parser.parse_args()


def mode_name(args: argparse.Namespace) -> str:
    if args.execute_tuning_smoke and args.execute_limited_tuning:
        raise SmokeBlockedError("choose only one execution mode")
    if args.execute_limited_tuning:
        return "limited"
    if args.execute_tuning_smoke:
        return "smoke"
    raise SmokeBlockedError("an explicit execution mode is required")


def validate_common_args(args: argparse.Namespace) -> None:
    if args.query_split in REFUSED_SPLITS:
        raise SmokeBlockedError(f"refusing forbidden query split: {args.query_split}")
    if args.query_split != EXPECTED_SPLIT:
        raise SmokeBlockedError("Alice tuning adapter only allows tuning_queries.")
    if args.profile != EXPECTED_PROFILE:
        raise SmokeBlockedError("Alice tuning adapter only allows current_defaults.")
    if args.axis_config != EXPECTED_AXIS_CONFIG:
        raise SmokeBlockedError(
            "Alice tuning adapter only allows hyde_off__no_decoder_control."
        )
    if args.generation_model != DEFAULT_MODEL or args.model_variant != "base":
        raise SmokeBlockedError("Alice tuning adapter requires MIDM BASE.")
    if args.collection_name != DEFAULT_COLLECTION:
        raise SmokeBlockedError("Alice tuning adapter requires local_gt__papers.")
    if args.retrieval_mode not in RETRIEVAL_MODES:
        raise SmokeBlockedError(f"unknown retrieval mode: {args.retrieval_mode}")
    if args.retrieval_mode == FIXED_BACKBONE:
        if not (
            args.retrieval_pool_top_k
            >= args.rerank_top_n
            >= args.context_chunk_count
            >= 1
        ):
            raise SmokeBlockedError(
                "fixed_backbone requires retrieval_pool_top_k >= rerank_top_n "
                ">= context_chunk_count >= 1."
            )


def validate_mode_args(args: argparse.Namespace) -> str:
    mode = mode_name(args)
    validate_common_args(args)
    if mode == "smoke":
        if not args.confirm_alice_base:
            raise SmokeBlockedError("--confirm-alice-base is required for smoke mode.")
        if args.query_limit != 1 or args.max_samples != 1:
            raise SmokeBlockedError("Phase 7.6A smoke is hard-limited to one sample.")
        return mode
    if not args.confirm_alice_limited_tuning:
        raise SmokeBlockedError(
            "--confirm-alice-limited-tuning is required for limited tuning."
        )
    if args.query_limit < 1 or args.query_limit > 5:
        raise SmokeBlockedError("limited tuning query_limit must be between 1 and 5.")
    if args.max_samples < 1 or args.max_samples > 5:
        raise SmokeBlockedError("limited tuning max_samples must be between 1 and 5.")
    return mode


def load_queries(query_split: str) -> list[dict[str, Any]]:
    path = QUERY_SPLITS_DIR / f"{query_split}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("queries") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not rows:
        raise SmokeBlockedError(f"{query_split}.json contains no queries.")
    return rows


def validate_query(record: dict[str, Any]) -> None:
    if record.get("gt_status") == "not_found":
        raise SmokeBlockedError(f"{record.get('query_id')} has gt_status:not_found.")
    if not record.get("answer_span"):
        raise SmokeBlockedError(f"{record.get('query_id')} has no answer_span.")
    if record.get("recommended_split") != "tuning":
        raise SmokeBlockedError(f"{record.get('query_id')} is not marked for tuning.")


def selected_queries(args: argparse.Namespace, mode: str) -> list[dict[str, Any]]:
    rows = load_queries(args.query_split)
    limit = 1 if mode == "smoke" else min(args.query_limit, args.max_samples, 5)
    selected = rows[:limit]
    for record in selected:
        validate_query(record)
    if len(selected) != limit:
        raise SmokeBlockedError("query split did not contain enough selected records.")
    if args.query_id is not None:
        ids = [record.get("query_id") for record in selected]
        if args.query_id not in ids:
            raise SmokeBlockedError(
                f"--query-id {args.query_id} not in selected query ids {ids}."
            )
    return selected


def build_fixed_backbone_components(collection_name: str):
    """Construct the real Paper-RAG backbone components (lazy, GPU-backed).

    Imported lazily so that importing this module (and the static unit tests)
    never requires torch / sentence-transformers.
    """
    from modules.embedder import Embedder
    from modules.hybrid_retriever import HybridRetriever
    from modules.reranker import Reranker
    from modules.vector_store import VectorStore

    vector_store = VectorStore()
    embedder = Embedder()
    hybrid_retriever = HybridRetriever(vector_store, embedder)
    reranker = Reranker()
    return embedder, vector_store, hybrid_retriever, reranker


def run_fixed_backbone_retrieval(
    *,
    embedder,
    vector_store,
    hybrid_retriever,
    reranker,
    collection_name: str,
    query: str,
    doc_id: str | None,
    retrieval_pool_top_k: int,
    rerank_top_n: int,
    context_chunk_count: int,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """Run query-aware fixed-backbone retrieval and return (context, chunks, meta).

    Pure orchestration over injected components so it is unit-testable without
    GPU. Mirrors the production HybridRetriever.search path but captures the
    intermediate dense/sparse/fused counts for evidence metadata.

    Fails closed (raises SmokeBlockedError) when:
    - the query text is empty,
    - the BM25 index for the collection is missing (no silent dense-only fallback),
    - retrieval produces no usable context chunks.
    """
    if not query or not query.strip():
        raise SmokeBlockedError(
            "fixed_backbone_requires_query_text: query text is required for "
            "query-aware retrieval."
        )

    bm25_available = bool(hybrid_retriever.has_bm25_for_collection(collection_name))
    if not bm25_available:
        raise SmokeBlockedError(
            "fixed_backbone_bm25_index_missing: BM25 index is not built for "
            f"collection '{collection_name}'. fixed_backbone must not fall back "
            "to dense-only; build the BM25 index first."
        )

    query_embedding = embedder.embed_query(query)
    dense_results = vector_store.search(
        collection_name,
        query_embedding,
        top_k=retrieval_pool_top_k,
        doc_id_filter=doc_id,
    )

    bm25_index = hybrid_retriever.bm25_map.get(collection_name)
    if bm25_index is None:
        # Defensive: has_bm25_for_collection said True but the map lacks it.
        raise SmokeBlockedError(
            "fixed_backbone_bm25_index_missing: BM25 index unavailable at retrieval time."
        )
    sparse_results = bm25_index.search(query, top_k=retrieval_pool_top_k)
    if doc_id:
        sparse_results = [
            r
            for r in sparse_results
            if (r.get("metadata") or {}).get("doc_id") == doc_id
        ]

    # Real RRF fusion from the backbone (single retrieval pass, exact counts).
    fused = hybrid_retriever._rrf_fusion(
        dense_results, sparse_results, retrieval_pool_top_k
    )
    reranked = reranker.rerank(query, fused, top_k=rerank_top_n)
    context_chunks = reranked[:context_chunk_count]

    if not context_chunks:
        raise SmokeBlockedError(
            "retrieval_context_required_but_empty: fixed_backbone retrieval "
            "produced no context chunks; refusing to generate."
        )

    chunk_records: list[dict[str, Any]] = []
    for chunk in context_chunks:
        metadata = chunk.get("metadata") or {}
        chunk_records.append(
            {
                "chunk_id": chunk.get("chunk_id", ""),
                "doc_id": metadata.get("doc_id", doc_id),
                "section_type": metadata.get("section_type", ""),
                "page": metadata.get("page", None),
                "rerank_score": chunk.get("rerank_score"),
                "rrf_score": chunk.get("rrf_score"),
                "snippet": (chunk.get("content") or "")[:500],
            }
        )

    context = "\n\n---\n\n".join(
        (chunk.get("content") or "") for chunk in context_chunks
    )
    if not context.strip():
        raise SmokeBlockedError(
            "retrieval_context_required_but_empty: fixed_backbone context is "
            "empty after assembly; refusing to generate."
        )

    def _doc_ids(items: list[dict[str, Any]]) -> list[str]:
        ids = []
        for item in items:
            did = (item.get("metadata") or {}).get("doc_id", doc_id)
            if did and did not in ids:
                ids.append(did)
        return ids

    retrieval_meta = {
        "retrieval_mode": FIXED_BACKBONE,
        "retrieval_backend": "bge_m3_dense+bm25_sparse+rrf+crossencoder_rerank",
        "query_used": True,
        "retrieval_pool_top_k": retrieval_pool_top_k,
        "rerank_top_n": rerank_top_n,
        "context_chunk_count": len(context_chunks),
        "dense_result_count": len(dense_results),
        "sparse_result_count": len(sparse_results),
        "fused_result_count": len(fused),
        "retrieved_chunk_ids": [c.get("chunk_id") for c in fused],
        "reranked_chunk_ids": [c.get("chunk_id") for c in reranked],
        "retrieved_doc_ids": _doc_ids(fused),
        "bm25_index_available": True,
        "fallback_used": False,
    }
    return context, chunk_records, retrieval_meta


def load_fixed_backbone_context(
    *,
    collection_name: str,
    query: str,
    doc_id: str | None,
    retrieval_pool_top_k: int,
    rerank_top_n: int,
    context_chunk_count: int,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """Build real components and run query-aware fixed-backbone retrieval."""
    embedder, vector_store, hybrid_retriever, reranker = (
        build_fixed_backbone_components(collection_name)
    )
    return run_fixed_backbone_retrieval(
        embedder=embedder,
        vector_store=vector_store,
        hybrid_retriever=hybrid_retriever,
        reranker=reranker,
        collection_name=collection_name,
        query=query,
        doc_id=doc_id,
        retrieval_pool_top_k=retrieval_pool_top_k,
        rerank_top_n=rerank_top_n,
        context_chunk_count=context_chunk_count,
    )


def doc_filter_sample_meta(
    chunk_records: list[dict[str, Any]], doc_id: str | None
) -> dict[str, Any]:
    """Retrieval metadata for the non-query-aware doc_id-filtered sample."""
    return {
        "retrieval_mode": DOC_FILTER_SAMPLE,
        "retrieval_backend": "vector_store_doc_filter_sample",
        "query_used": False,
        "retrieval_pool_top_k": None,
        "rerank_top_n": None,
        "context_chunk_count": len(chunk_records),
        "dense_result_count": None,
        "sparse_result_count": None,
        "fused_result_count": None,
        "retrieved_chunk_ids": [c.get("chunk_id") for c in chunk_records],
        "reranked_chunk_ids": [],
        "retrieved_doc_ids": [doc_id] if doc_id else [],
        "bm25_index_available": None,
        "fallback_used": False,
    }


def gather_context(
    args: argparse.Namespace, query: str, doc_id: str | None
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """Return (context, chunk_records, retrieval_meta) for the selected mode."""
    if args.retrieval_mode == FIXED_BACKBONE:
        return load_fixed_backbone_context(
            collection_name=args.collection_name,
            query=query,
            doc_id=doc_id,
            retrieval_pool_top_k=args.retrieval_pool_top_k,
            rerank_top_n=args.rerank_top_n,
            context_chunk_count=args.context_chunk_count,
        )
    context, chunk_records = load_context_chunks(
        args.collection_name, doc_id, args.context_limit
    )
    if not context or not chunk_records:
        raise SmokeBlockedError(
            "context_required_but_empty: context is required but no vector-store "
            "chunks were retrieved."
        )
    return context, chunk_records, doc_filter_sample_meta(chunk_records, doc_id)


def phase_label(args: argparse.Namespace, mode: str) -> str:
    if args.retrieval_mode == FIXED_BACKBONE:
        return "phase7_6B2A_fixed_backbone_retrieval_smoke"
    if mode == "limited":
        return "phase7_6B_limited_tuning_current_defaults"
    return "phase7_6A_alice_tuning_adapter_smoke"


def build_record(
    *,
    args: argparse.Namespace,
    mode: str,
    query_record: dict[str, Any],
    sample_index: int,
    sample_count: int,
) -> dict[str, Any]:
    doc_ids = query_record.get("applicable_papers") or []
    doc_id = doc_ids[0] if doc_ids else query_record.get("paper")
    start_time = now_iso()
    start = time.perf_counter()
    answer = ""
    error = None
    status = "succeeded"
    context = ""
    retrieval_meta: dict[str, Any] = {}
    context_chunks: list[dict[str, Any]] = []

    try:
        context, context_chunks, retrieval_meta = gather_context(
            args, query_record["query"], doc_id
        )
        answer = generate_answer(
            query=query_record["query"],
            context=context,
            generation_model=args.generation_model,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            allow_download=False,
        )
    except Exception as exc:
        status = "failed"
        error = {"type": type(exc).__name__, "message": str(exc)[:1000]}
        if not retrieval_meta:
            retrieval_meta = {
                "retrieval_mode": args.retrieval_mode,
                "fallback_used": False,
            }

    duration_seconds = round(time.perf_counter() - start, 3)
    limited_mode = mode == "limited"
    evidence_class = EVIDENCE_CLASS_BY_MODE[args.retrieval_mode]
    return {
        "phase": phase_label(args, mode),
        "sample_index": sample_index,
        "sample_count": sample_count,
        "status": status,
        "query_id": query_record.get("query_id"),
        "query": query_record.get("query"),
        "query_type": query_record.get("normalized_query_type")
        or query_record.get("query_type"),
        "paper": doc_id,
        "paper_language": query_record.get("paper_language"),
        "selected_profile": args.profile,
        "selected_axis_config": args.axis_config,
        **EXPECTED_FLAGS,
        "model_family": "MIDM",
        "model_variant": args.model_variant,
        "model_role": (
            "alice_thesis_limited_tuning" if limited_mode else args.model_role
        ),
        # No single-config smoke (doc-filter or fixed-backbone) is parameter-freeze
        # evidence. Freeze evidence requires a parameter sweep on tuning_queries.
        "parameter_freeze_evidence": False,
        "evidence_class": evidence_class,
        "fixed_backbone_validation": args.retrieval_mode == FIXED_BACKBONE
        and status == "succeeded",
        "thesis_grade_result": False,
        "selected_model_path_or_name": args.generation_model,
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "decoding_mode": "deterministic_greedy",
        "generated_answer": answer,
        "retrieval_mode": args.retrieval_mode,
        "retrieval_backend": retrieval_meta.get("retrieval_backend"),
        "retrieval_pool_top_k": retrieval_meta.get("retrieval_pool_top_k"),
        "rerank_top_n": retrieval_meta.get("rerank_top_n"),
        "context_chunk_count": retrieval_meta.get("context_chunk_count"),
        "dense_result_count": retrieval_meta.get("dense_result_count"),
        "sparse_result_count": retrieval_meta.get("sparse_result_count"),
        "fused_result_count": retrieval_meta.get("fused_result_count"),
        "retrieved_chunk_ids": retrieval_meta.get("retrieved_chunk_ids"),
        "reranked_chunk_ids": retrieval_meta.get("reranked_chunk_ids"),
        "retrieved_doc_ids": retrieval_meta.get("retrieved_doc_ids"),
        "bm25_index_available": retrieval_meta.get("bm25_index_available"),
        "fallback_used": retrieval_meta.get("fallback_used", False),
        "context": {
            "collection_name": args.collection_name,
            "doc_id_filter": doc_id,
            "source": retrieval_meta.get(
                "retrieval_backend", "vector_store_doc_filter_sample"
            ),
            "chunks": context_chunks,
            "context_available": bool(context),
        },
        "backend_metadata": {
            "runner": "experiments/runners/run_alice_tuning.py",
            "mode": mode,
            "retrieval_mode": args.retrieval_mode,
            "query_split": args.query_split,
            "query_limit": args.query_limit,
            "max_samples": args.max_samples,
            "generation_model": args.generation_model,
            "model_variant": args.model_variant,
            "allow_download": False,
            "execution_guard": (
                "phase7_6B2A_fixed_backbone_retrieval_smoke"
                if args.retrieval_mode == FIXED_BACKBONE
                else (
                    "phase7_6B_limited_tuning_current_defaults_max_5"
                    if limited_mode
                    else "phase7_6A_one_sample_tuning_adapter_smoke_only"
                )
            ),
        },
        "start_time": start_time,
        "end_time": now_iso(),
        "duration_seconds": duration_seconds,
        "error": error,
        "alice_mode": True,
        "local_only": False,
        "openai_used": False,
        "ragas_used": False,
        "gt_regenerated": False,
        "decoder_main_used": False,
        "final_eval_used": False,
    }


def default_output_for_mode(args: argparse.Namespace, mode: str) -> Path:
    if args.retrieval_mode == FIXED_BACKBONE:
        return DEFAULT_FIXED_BACKBONE_SMOKE_OUTPUT
    return DEFAULT_LIMITED_OUTPUT if mode == "limited" else DEFAULT_SMOKE_OUTPUT


def main() -> int:
    args = parse_args()
    try:
        mode = validate_mode_args(args)
        records = selected_queries(args, mode)
    except SmokeBlockedError as exc:
        print(f"REFUSED: {exc}")
        return 2
    output_path = (
        Path(args.output_file)
        if args.output_file
        else default_output_for_mode(args, mode)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_records = []
    for index, query_record in enumerate(records, 1):
        record = build_record(
            args=args,
            mode=mode,
            query_record=query_record,
            sample_index=index,
            sample_count=len(records),
        )
        output_records.append(record)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        if record.get("status") != "succeeded":
            break
    output_path.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False) + "\n" for record in output_records
        ),
        encoding="utf-8",
    )
    print(f"Alice tuning output: {output_path}")
    return (
        0
        if len(output_records) == len(records)
        and all(record.get("status") == "succeeded" for record in output_records)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
