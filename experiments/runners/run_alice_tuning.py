"""Alice tuning execution adapter.

This runner is intentionally narrow. It supports:
1. Phase 7.6A one-sample adapter smoke.
2. Phase 7.6B limited current-defaults tuning with at most five tuning queries.

It refuses decoder_main/final/service/template splits and never imports OpenAI or RAGAS.
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
    parser = argparse.ArgumentParser(description="Run guarded Alice tuning modes.")
    parser.add_argument("--execute-tuning-smoke", action="store_true")
    parser.add_argument("--confirm-alice-base", action="store_true")
    parser.add_argument("--execute-limited-tuning", action="store_true")
    parser.add_argument("--confirm-alice-limited-tuning", action="store_true")
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
        help="Model role metadata written to output records.",
    )
    parser.add_argument("--collection-name", default=DEFAULT_COLLECTION)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--context-limit", type=int, default=3)
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
    return selected


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
    context_chunks: list[dict[str, Any]] = []

    try:
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
    limited_mode = mode == "limited"
    return {
        "phase": (
            "phase7_6B_limited_tuning_current_defaults"
            if limited_mode
            else "phase7_6A_alice_tuning_adapter_smoke"
        ),
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
        "parameter_freeze_evidence": bool(limited_mode),
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
            "mode": mode,
            "query_split": args.query_split,
            "query_limit": args.query_limit,
            "max_samples": args.max_samples,
            "generation_model": args.generation_model,
            "model_variant": args.model_variant,
            "allow_download": False,
            "execution_guard": (
                "phase7_6B_limited_tuning_current_defaults_max_5"
                if limited_mode
                else "phase7_6A_one_sample_tuning_adapter_smoke_only"
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


def default_output_for_mode(mode: str) -> Path:
    return DEFAULT_LIMITED_OUTPUT if mode == "limited" else DEFAULT_SMOKE_OUTPUT


def main() -> int:
    args = parse_args()
    mode = validate_mode_args(args)
    records = selected_queries(args, mode)
    output_path = Path(args.output_file) if args.output_file else default_output_for_mode(mode)
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
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in output_records),
        encoding="utf-8",
    )
    print(f"Alice tuning output: {output_path}")
    return 0 if len(output_records) == len(records) and all(
        record.get("status") == "succeeded" for record in output_records
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
