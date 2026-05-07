"""Phase 7.6A Alice tuning execution adapter smoke.

This runner intentionally supports only a one-sample Alice tuning adapter smoke.
It is not the full tuning runner and must not be used for decoder_main/final_eval
or main experiment generation.
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

DEFAULT_OUTPUT = (
    ROOT
    / "experiments/results/tuning/phase7_6A_alice_tuning_adapter_smoke_1sample.jsonl"
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


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Phase 7.6A Alice tuning adapter one-sample smoke."
    )
    parser.add_argument("--execute-tuning-smoke", action="store_true")
    parser.add_argument("--confirm-alice-base", action="store_true")
    parser.add_argument("--query-split", default=EXPECTED_SPLIT)
    parser.add_argument("--query-limit", type=int, default=1)
    parser.add_argument("--max-samples", type=int, default=1)
    parser.add_argument("--profile", default=EXPECTED_PROFILE)
    parser.add_argument("--axis-config", default=EXPECTED_AXIS_CONFIG)
    parser.add_argument("--generation-model", default=DEFAULT_MODEL)
    parser.add_argument("--model-variant", choices=["base"], default="base")
    parser.add_argument(
        "--model-role",
        default="alice_thesis_tuning_smoke",
        help="Model role metadata written to the tuning adapter smoke record.",
    )
    parser.add_argument("--collection-name", default=DEFAULT_COLLECTION)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--context-limit", type=int, default=3)
    parser.add_argument("--output-file", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if not args.execute_tuning_smoke:
        raise SmokeBlockedError("--execute-tuning-smoke is required.")
    if not args.confirm_alice_base:
        raise SmokeBlockedError("--confirm-alice-base is required for Alice MIDM BASE.")
    if args.query_split in REFUSED_SPLITS:
        raise SmokeBlockedError(f"refusing forbidden query split: {args.query_split}")
    if args.query_split != EXPECTED_SPLIT:
        raise SmokeBlockedError("Phase 7.6A adapter smoke only allows tuning_queries.")
    if args.query_limit != 1 or args.max_samples != 1:
        raise SmokeBlockedError("Phase 7.6A adapter smoke is hard-limited to one sample.")
    if args.profile != EXPECTED_PROFILE:
        raise SmokeBlockedError("Phase 7.6A adapter smoke only allows current_defaults.")
    if args.axis_config != EXPECTED_AXIS_CONFIG:
        raise SmokeBlockedError(
            "Phase 7.6A adapter smoke only allows hyde_off__no_decoder_control."
        )
    if args.generation_model != DEFAULT_MODEL or args.model_variant != "base":
        raise SmokeBlockedError("Phase 7.6A adapter smoke requires MIDM BASE.")


def load_tuning_query(query_split: str) -> dict[str, Any]:
    path = QUERY_SPLITS_DIR / f"{query_split}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("queries") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not rows:
        raise SmokeBlockedError(f"{query_split}.json contains no queries.")
    record = rows[0]
    if record.get("gt_status") == "not_found":
        raise SmokeBlockedError("first tuning query has gt_status:not_found.")
    if not record.get("answer_span"):
        raise SmokeBlockedError("first tuning query has no answer_span.")
    return record


def build_record(args: argparse.Namespace) -> dict[str, Any]:
    query_record = load_tuning_query(args.query_split)
    doc_ids = query_record.get("applicable_papers") or []
    doc_id = doc_ids[0] if doc_ids else query_record.get("paper")
    start_time = now_iso()
    start = time.perf_counter()
    answer = ""
    error = None
    status = "succeeded"
    context = ""
    context_chunks: list[dict[str, Any]] = []

    try:
        validate_args(args)
        context, context_chunks = load_context_chunks(
            args.collection_name,
            doc_id,
            args.context_limit,
        )
        if not context or not context_chunks:
            raise SmokeBlockedError(
                "context_required_but_empty: context is required but no "
                "vector-store chunks were retrieved."
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

    duration_seconds = round(time.perf_counter() - start, 3)
    return {
        "phase": "phase7_6A_alice_tuning_adapter_smoke",
        "sample_index": 1,
        "sample_count": 1,
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
        "model_role": args.model_role,
        "thesis_grade_result": False,
        "selected_model_path_or_name": args.generation_model,
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "decoding_mode": "deterministic_greedy",
        "generated_answer": answer,
        "context": {
            "collection_name": args.collection_name,
            "doc_id_filter": doc_id,
            "source": "vector_store_doc_filter_sample",
            "chunks": context_chunks,
            "context_available": bool(context),
        },
        "backend_metadata": {
            "runner": "experiments/runners/run_alice_tuning.py",
            "query_split": args.query_split,
            "query_limit": args.query_limit,
            "max_samples": args.max_samples,
            "generation_model": args.generation_model,
            "model_variant": args.model_variant,
            "model_role": args.model_role,
            "allow_download": False,
            "execution_guard": "phase7_6A_one_sample_tuning_adapter_smoke_only",
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


def main() -> int:
    args = parse_args()
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    record = build_record(args)
    output_path.write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(f"Alice tuning adapter smoke output: {output_path}")
    return 0 if record.get("status") == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
