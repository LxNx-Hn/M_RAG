"""Execution body for the held-out 41-query extended validation matrix.

The generation path intentionally mirrors ``main_generation_executor.py``:
fixed Paper-RAG retrieval, the same eight HyDE/CAD/SCD configurations, frozen
parameters, Mi:dm 2.0 Base, and deterministic greedy decoding. The original main
split and its artifacts are not modified.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
BACKEND_DIR = REPO / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from common import resolve_output_dir, validate_main_matrix  # noqa: E402
from main_generation_executor import (  # noqa: E402
    APPROVED_COLLECTION,
    APPROVED_MODEL_NAME,
    _chunk_records,
    _doc_id_for_query,
    _now_iso,
    build_components,
    retrieve_fixed_backbone,
)

APPROVED_EXTENDED_SPLIT = "extended_validation_questions"
SPLIT_PATH = ROOT / "data" / "query_splits" / f"{APPROVED_EXTENDED_SPLIT}.json"


def _flags() -> dict[str, Any]:
    return {
        "openai_used": False,
        "ragas_used": False,
        "gt_regenerated": False,
        "decoder_main_used": False,
        "extended_validation_used": True,
        "final_eval_used": False,
        "parameter_freeze_evidence": False,
        "thesis_grade_result": False,
        "alice_mode": True,
    }


def execute_extended_validation(args, params: dict[str, float]) -> int:
    import torch
    from modules.scd_decoder import create_combined_processor, extract_scd_metadata

    rerank_n = int(params.get("rerank_top_n", 5))
    ctx_n = int(params.get("context_chunk_count", rerank_n))
    pool = int(params.get("retrieval_pool_top_k", 20))
    cad_alpha = float(params.get("cad_alpha", 0.5))
    scd_beta = float(getattr(args, "scd_beta", params.get("scd_beta", 0.3)))
    scd_alpha = float(getattr(args, "scd_alpha", 1.1))
    scd_t_start = int(getattr(args, "scd_t_start", 0))
    scd_mode = str(getattr(args, "scd_mode", "penalty_additive"))
    max_new_tokens = int(params.get("max_new_tokens", 512))

    configs = validate_main_matrix()
    split_data = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
    queries = split_data.get("queries", [])
    if len(queries) != 41:
        raise RuntimeError(
            f"extended validation split must contain exactly 41 queries; found {len(queries)}"
        )

    c = build_components(max_new_tokens)
    gen = c["generator"]

    out_dir = resolve_output_dir(Path(args.output_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = (
        out_dir
        / f"{args.experiment}__{APPROVED_EXTENDED_SPLIT}__extended_validation_generation.jsonl"
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
                hyde_doc = None
                hyde_query = None
                hyde_translated_query = None
                hyde_corpus_lang = None
                hyde_generation_settings = None
                meta: dict[str, Any] = {}
                chunk_recs: list[dict] = []
                scd_metadata: dict[str, Any] = {}
                start = time.time()
                try:
                    if doc_id is None:
                        raise RuntimeError("query has no resolvable doc_id.")
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
                        hyde_query = expansion.get("hyde_query")
                        hyde_translated_query = expansion.get("translated")
                        hyde_corpus_lang = expansion.get("hyde_corpus_lang")
                        hyde_generation_settings = expansion.get(
                            "hyde_generation_settings"
                        )
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
                            scd_alpha=scd_alpha,
                            scd_t_start=scd_t_start,
                            scd_mode=scd_mode,
                        )
                    answer = gen.generate(
                        query=query,
                        context=context,
                        template="qa",
                        logits_processor=proc,
                        force_greedy=True,
                    )
                    if config.use_scd:
                        scd_metadata = extract_scd_metadata(proc)
                except torch.cuda.OutOfMemoryError as exc:
                    status = "failed"
                    error = {
                        "type": "CudaOutOfMemoryError",
                        "message": str(exc)[:1000],
                    }
                except Exception as exc:  # noqa: BLE001
                    status = "failed"
                    error = {"type": type(exc).__name__, "message": str(exc)[:1000]}

                rec = {
                    "phase": "extended_validation_hyde_cad_scd_generation",
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
                    "retrieval_reformulation": {
                        "hyde": config.use_hyde,
                        "hyde_mode": "on" if config.use_hyde else "off",
                        "translated_query": hyde_translated_query,
                        "hyde_query": hyde_query,
                        "hyde_document": hyde_doc,
                        "hyde_corpus_lang": hyde_corpus_lang,
                        "hyde_generation_settings": hyde_generation_settings,
                    },
                    "use_cad": config.use_cad,
                    "cad_alpha": cad_alpha if config.use_cad else None,
                    "use_scd": config.use_scd,
                    "scd_beta": scd_beta if config.use_scd else None,
                    "scd_alpha": scd_alpha if config.use_scd else None,
                    "scd_t_start": scd_t_start if config.use_scd else None,
                    "scd_mode": scd_mode if config.use_scd else None,
                    "scd_variant": (
                        scd_metadata.get("scd_variant") if config.use_scd else None
                    ),
                    "scd_warmup_basis": (
                        scd_metadata.get("scd_warmup_basis") if config.use_scd else None
                    ),
                    "scd_vocab_partition": (
                        scd_metadata.get("scd_vocab_partition")
                        if config.use_scd
                        else None
                    ),
                    "scd_reference_formula_applied": (
                        scd_metadata.get("scd_reference_formula_applied")
                        if config.use_scd
                        else None
                    ),
                    "scd_project_whitelist_used": (
                        scd_metadata.get("scd_project_whitelist_used")
                        if config.use_scd
                        else None
                    ),
                    "scd_processor_order": (
                        scd_metadata.get("scd_processor_order")
                        if config.use_scd
                        else None
                    ),
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
                    "evidence_class": "extended_validation_hyde_cad_scd_generation",
                    "duration_seconds": round(time.time() - start, 3),
                    "error": error,
                    "note": (
                        "held-out extended validation generation; uses the frozen main "
                        "experiment settings and is scored only in the evaluation phase"
                    ),
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

    expected = len(configs) * len(queries)
    print(f"WROTE {written} records ({succeeded} succeeded) -> {out_path}")
    print(f"configs={len(configs)} queries={len(queries)} expected={expected}")
    return 0 if written == expected and succeeded == expected else 1
