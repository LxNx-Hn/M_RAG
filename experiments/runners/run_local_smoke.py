"""Phase 7.5A local smoke runner.

This runner is intentionally narrow: it can only prepare and attempt the
approved 1-query x 1-profile x 1-axis-config smoke sample. It does not enable
the broader tuning or generation runners.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

OUTPUT_PATH = ROOT / "experiments/results/smoke/phase7_5A_smoke_local_1sample.jsonl"
TUNING_SPLIT_PATH = ROOT / "experiments/data/query_splits/tuning_queries.json"
EXPECTED_PROFILE = "current_defaults"
EXPECTED_CONFIG = "hyde_off__no_decoder_control"
EXPECTED_FLAGS = {"use_hyde": False, "use_cad": False, "use_scd": False}
DEFAULT_COLLECTION = "local_gt__papers"
DEFAULT_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"


class SmokeBlockedError(RuntimeError):
    """Raised when the approved smoke run cannot proceed safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Phase 7.5A one-sample local smoke path."
    )
    parser.add_argument(
        "--execute-smoke",
        action="store_true",
        help="Required. Confirms this is the approved one-sample smoke attempt.",
    )
    parser.add_argument("--output-file", default=str(OUTPUT_PATH))
    parser.add_argument("--collection-name", default=DEFAULT_COLLECTION)
    parser.add_argument("--generation-model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--model-variant",
        choices=["base", "mini"],
        default="base",
        help="Model variant metadata for smoke trace safety.",
    )
    parser.add_argument(
        "--model-role",
        default="local_validation_only",
        help="Model role metadata written to the smoke record.",
    )
    parser.add_argument(
        "--phase-label",
        default="phase7_5A",
        help="Phase label metadata written to the smoke record.",
    )
    parser.add_argument(
        "--alice-mode",
        action="store_true",
        help="Mark this smoke as an Alice Cloud execution path.",
    )
    parser.add_argument(
        "--confirm-alice-base",
        action="store_true",
        help="Required with --alice-mode before MIDM BASE smoke is allowed.",
    )
    parser.add_argument(
        "--require-mini",
        action="store_true",
        help="Block unless the selected generation model is the MIDM Mini variant.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow Hugging Face model download. Do not use in Phase 7.5A.",
    )
    parser.add_argument(
        "--require-context",
        action="store_true",
        help="Fail closed before generation when no vector-store context chunks are retrieved.",
    )
    parser.add_argument(
        "--context-limit",
        type=int,
        default=3,
        help="Maximum vector-store chunks to include for the single sample.",
    )
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_first_tuning_query() -> dict[str, Any]:
    payload = json.loads(TUNING_SPLIT_PATH.read_text(encoding="utf-8"))
    queries = payload.get("queries", [])
    if not queries:
        raise SmokeBlockedError("tuning_queries.json contains no queries.")

    record = queries[0]
    if record.get("gt_status") != "valid":
        raise SmokeBlockedError(
            f"first tuning query is not valid GT: {record.get('gt_status')}"
        )
    if not (record.get("answer_span") or record.get("has_answer_span")):
        raise SmokeBlockedError("first tuning query has no answer_span.")
    return record


def find_cached_model_snapshot(model_name: str) -> Path | None:
    cache_roots = []
    for env_name in ("HF_HOME", "TRANSFORMERS_CACHE", "HF_HUB_CACHE"):
        value = os.environ.get(env_name)
        if value:
            cache_roots.append(Path(value))
    cache_roots.append(Path.home() / ".cache" / "huggingface")

    model_dir_name = "models--" + model_name.replace("/", "--")
    for root in cache_roots:
        for candidate in (root / "hub" / model_dir_name, root / model_dir_name):
            snapshots = candidate / "snapshots"
            if not snapshots.exists():
                continue
            for snapshot in sorted(snapshots.iterdir()):
                if (snapshot / "config.json").exists() and any(
                    snapshot.glob("*.safetensors")
                ):
                    return snapshot
    return None


def snapshot_model_size_gb(snapshot: Path) -> float:
    total_bytes = sum(path.stat().st_size for path in snapshot.glob("*.safetensors"))
    return round(total_bytes / 1024**3, 2)


def current_free_vram_gb() -> float | None:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.free",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None
    first_line = result.stdout.strip().splitlines()[0].strip()
    try:
        return round(float(first_line) / 1024, 2)
    except ValueError:
        return None


def load_context_chunks(
    collection_name: str,
    doc_id: str | None,
    limit: int,
) -> tuple[str, list[dict[str, Any]]]:
    if not doc_id:
        return "", []

    try:
        from modules.vector_store import VectorStore

        store = VectorStore()
        collection = store.get_or_create_collection(collection_name)
        result = collection.get(
            where={"doc_id": doc_id},
            limit=max(1, limit),
            include=["documents", "metadatas"],
        )
    except Exception as exc:
        return "", [
            {
                "error": "context_load_failed",
                "detail": str(exc)[:500],
            }
        ]

    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []
    ids = result.get("ids") or []
    chunks: list[dict[str, Any]] = []
    for index, content in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        chunk_id = ids[index] if index < len(ids) else ""
        chunks.append(
            {
                "chunk_id": chunk_id,
                "doc_id": metadata.get("doc_id", doc_id) if metadata else doc_id,
                "section_type": metadata.get("section_type", "") if metadata else "",
                "page": metadata.get("page", None) if metadata else None,
                "snippet": (content or "")[:500],
            }
        )

    context = "\n\n---\n\n".join(chunk.get("snippet", "") for chunk in chunks)
    return context, chunks


def generate_answer(
    *,
    query: str,
    context: str,
    generation_model: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    allow_download: bool,
) -> str:
    if not allow_download:
        snapshot = find_cached_model_snapshot(generation_model)
        if snapshot is None:
            raise SmokeBlockedError(
                "generation model is not present in the local Hugging Face cache; "
                "refusing implicit download in Phase 7.5A"
            )
        model_size_gb = snapshot_model_size_gb(snapshot)
        free_vram_gb = current_free_vram_gb()
        if free_vram_gb is not None and model_size_gb > free_vram_gb:
            raise SmokeBlockedError(
                f"cached generation model files total {model_size_gb} GB, "
                f"which exceeds currently free VRAM {free_vram_gb} GB; "
                "refusing local 12GB smoke without an explicit offload or smaller-model plan"
            )

    if not allow_download:
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")

    from modules.generator import QA_TEMPLATE, SYSTEM_PROMPT, Generator

    generator = Generator(model_name=generation_model, max_new_tokens=max_new_tokens)
    prompt = QA_TEMPLATE.format(context=context, query=query)
    return generator.generate_simple(
        prompt,
        max_new_tokens=max_new_tokens,
        system_prompt=SYSTEM_PROMPT,
        temperature=temperature,
        top_p=top_p,
        do_sample=False,
        force_greedy=True,
    )


def build_record(args: argparse.Namespace) -> dict[str, Any]:
    query_record = load_first_tuning_query()
    doc_ids = query_record.get("applicable_papers") or []
    doc_id = doc_ids[0] if doc_ids else None
    start_time = now_iso()
    start = time.perf_counter()
    context, context_chunks = load_context_chunks(
        args.collection_name,
        doc_id,
        args.context_limit,
    )
    answer = ""
    error = None
    status = "succeeded"

    try:
        if not args.execute_smoke:
            raise SmokeBlockedError("--execute-smoke is required for Phase 7.5A.")
        if args.require_context and (not context or not context_chunks):
            raise SmokeBlockedError(
                "context_required_but_empty: context is required but no "
                "vector-store chunks were retrieved."
            )
        if args.require_mini and (
            args.model_variant != "mini" or "Mini" not in args.generation_model
        ):
            raise SmokeBlockedError(
                "--require-mini was set, but the selected model is not MIDM Mini."
            )
        selected_base = (
            args.model_variant == "base" or "Base" in args.generation_model
        )
        if selected_base and not (args.alice_mode and args.confirm_alice_base):
            raise SmokeBlockedError(
                "MIDM BASE smoke requires --alice-mode and --confirm-alice-base; "
                "local BASE remains blocked by VRAM policy."
            )
        answer = generate_answer(
            query=query_record["query"],
            context=context,
            generation_model=args.generation_model,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            allow_download=args.allow_download,
        )
    except Exception as exc:
        status = "failed"
        error = {
            "type": type(exc).__name__,
            "message": str(exc)[:1000],
        }

    end_time = now_iso()
    duration_seconds = round(time.perf_counter() - start, 3)
    return {
        "phase": args.phase_label,
        "sample_index": 1,
        "sample_count": 1,
        "status": status,
        "query_id": query_record.get("query_id"),
        "query": query_record.get("query"),
        "query_type": query_record.get("normalized_query_type")
        or query_record.get("query_type"),
        "paper": doc_id,
        "paper_language": query_record.get("paper_language"),
        "selected_profile": EXPECTED_PROFILE,
        "selected_axis_config": EXPECTED_CONFIG,
        "model_role": args.model_role,
        "model_family": "MIDM",
        "model_variant": args.model_variant,
        "thesis_grade_result": False,
        "selected_model_path_or_name": args.generation_model,
        **EXPECTED_FLAGS,
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
            "runner": "experiments/runners/run_local_smoke.py",
            "generation_model": args.generation_model,
            "model_variant": args.model_variant,
            "model_role": args.model_role,
            "require_mini": bool(args.require_mini),
            "alice_mode": bool(args.alice_mode),
            "confirm_alice_base": bool(args.confirm_alice_base),
            "allow_download": bool(args.allow_download),
            "execution_guard": "phase7_5A_one_sample_only",
        },
        "start_time": start_time,
        "end_time": end_time,
        "duration_seconds": duration_seconds,
        "error": error,
        "local_only": not bool(args.alice_mode),
        "alice_mode": bool(args.alice_mode),
        "openai_used": False,
        "ragas_used": False,
        "gt_regenerated": False,
        "decoder_main_used": False,
        "final_eval_used": False,
    }


def main() -> int:
    args = parse_args()
    output = Path(args.output_file)
    output.parent.mkdir(parents=True, exist_ok=True)
    record = build_record(args)
    output.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["status"] == "succeeded" else 2


if __name__ == "__main__":
    raise SystemExit(main())
