"""Fail-closed runner for the 41-query held-out extended validation matrix.

The original 19-query main split and manuscript/document files remain untouched.
Execution matches the retained FINAL reference-SCD generation method: the same
fixed Paper-RAG backbone, exact eight HyDE x CAD x SCD configurations, Mi:dm
2.0 Base, deterministic greedy answer generation, CAD alpha 0.5, and the
paper-faithful reference_scd settings alpha=1.1, beta=0.9, T_start=5.

The Phase-8 frozen parameter file is reused for retrieval, CAD and generation
settings. Its legacy SCD beta=0.3 belongs to the superseded penalty_additive v1
run and is deliberately NOT reused for SCD-on cells here.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

from common import REPO_ROOT, ConfigValidationError, resolve_output_dir, validate_main_matrix
from run_generation import (
    APPROVED_COLLECTION,
    APPROVED_MODEL,
    DEFAULT_FROZEN_PARAMS,
    RESULTS_ROOT,
    read_frozen_params,
)

APPROVED_EXTENDED_SPLIT = "extended_validation_questions"
DEFAULT_EXTENDED_EXPERIMENT = "extended-hyde-cad-scd-reference-scd"
CONFIRM_ENV = "CONFIRM_EXTENDED_VALIDATION_8CONFIG"
CONFIRM_SCD_ENV = "CONFIRM_SCD_V2_GENERATION"
REFERENCE_SCD_MODE = "reference_scd"
REFERENCE_SCD_ALPHA = 1.1
REFERENCE_SCD_BETA = 0.9
REFERENCE_SCD_T_START = 5
SPLIT_PATH = (
    REPO_ROOT
    / "experiments"
    / "data"
    / "query_splits"
    / f"{APPROVED_EXTENDED_SPLIT}.json"
)
EXPECTED_PAPER_COUNTS = {
    "paper_nlp_rag": 10,
    "paper_nlp_cad": 11,
    "paper_nlp_raptor": 11,
    "paper_midm": 9,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--experiment", default=DEFAULT_EXTENDED_EXPERIMENT)
    parser.add_argument("--query-split", default=APPROVED_EXTENDED_SPLIT)
    parser.add_argument(
        "--output-dir", default="experiments/results/extended_validation"
    )
    parser.add_argument("--generation-model", default=APPROVED_MODEL)
    parser.add_argument("--collection-name", default=APPROVED_COLLECTION)
    parser.add_argument("--frozen-params", default=str(DEFAULT_FROZEN_PARAMS))
    parser.add_argument("--scd-beta", type=float, default=REFERENCE_SCD_BETA)
    parser.add_argument("--scd-alpha", type=float, default=REFERENCE_SCD_ALPHA)
    parser.add_argument("--scd-t-start", type=int, default=REFERENCE_SCD_T_START)
    parser.add_argument("--scd-mode", default=REFERENCE_SCD_MODE)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--config-limit", type=int, default=None)
    return parser


def _env_disabled(name: str) -> bool:
    return os.environ.get(name, "0") == "0"


def load_and_validate_split() -> list[dict]:
    if not SPLIT_PATH.exists():
        raise RuntimeError(f"missing split: {SPLIT_PATH}")
    data = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    if data.get("status") != "validated_ready":
        raise RuntimeError("extended validation split is not validated_ready")
    if data.get("count") != 41 or len(queries) != 41:
        raise RuntimeError(
            f"extended validation must contain exactly 41 queries; found {len(queries)}"
        )
    ids = [q.get("query_id") for q in queries]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate query_id in extended validation split")
    missing = [
        q.get("query_id")
        for q in queries
        if not q.get("query")
        or not q.get("answer_span")
        or q.get("gt_status") != "valid"
        or q.get("answerability_status") != "answerable"
    ]
    if missing:
        raise RuntimeError(f"invalid query records: {missing}")
    paper_counts = Counter(
        q["applicable_papers"][0]
        for q in queries
        if isinstance(q.get("applicable_papers"), list)
        and len(q["applicable_papers"]) == 1
    )
    if dict(paper_counts) != EXPECTED_PAPER_COUNTS:
        raise RuntimeError(
            f"paper allocation mismatch: expected {EXPECTED_PAPER_COUNTS}, "
            f"found {dict(paper_counts)}"
        )
    return queries


def check_extended_generation_guards(args: argparse.Namespace) -> str | None:
    if os.environ.get(CONFIRM_ENV) != "1":
        return f"{CONFIRM_ENV}=1 is required for --execute."
    if os.environ.get(CONFIRM_SCD_ENV) != "1":
        return f"{CONFIRM_SCD_ENV}=1 is required for reference_scd execution."
    if not _env_disabled("OPENAI_ENABLED"):
        return "OpenAI must be disabled (OPENAI_ENABLED=0)."
    if not _env_disabled("RAGAS_ENABLED"):
        return "RAGAS must be disabled (RAGAS_ENABLED=0)."
    if not _env_disabled("GT_REGENERATION_ENABLED"):
        return "GT regeneration must be disabled (GT_REGENERATION_ENABLED=0)."
    if args.collection_name != APPROVED_COLLECTION:
        return f"collection must be {APPROVED_COLLECTION}."
    if args.generation_model != APPROVED_MODEL:
        return f"generation model must be {APPROVED_MODEL} (MIDM Base)."
    if args.query_split != APPROVED_EXTENDED_SPLIT:
        return f"query split must be {APPROVED_EXTENDED_SPLIT!r}."
    if args.experiment != DEFAULT_EXTENDED_EXPERIMENT:
        return f"experiment id must be {DEFAULT_EXTENDED_EXPERIMENT!r}."
    if args.scd_mode != REFERENCE_SCD_MODE:
        return f"extended validation must use scd_mode={REFERENCE_SCD_MODE!r}."
    if args.scd_beta != REFERENCE_SCD_BETA:
        return f"extended validation must use scd_beta={REFERENCE_SCD_BETA}."
    if args.scd_alpha != REFERENCE_SCD_ALPHA:
        return f"extended validation must use scd_alpha={REFERENCE_SCD_ALPHA}."
    if args.scd_t_start != REFERENCE_SCD_T_START:
        return f"extended validation must use scd_t_start={REFERENCE_SCD_T_START}."
    if args.config_limit is not None or args.limit is not None:
        return "--limit/--config-limit are not allowed for the full extended run."
    try:
        configs = validate_main_matrix()
    except ConfigValidationError as exc:
        return f"main matrix invalid: {exc}"
    if len(configs) != 8:
        return f"main matrix must have exactly 8 configs; found {len(configs)}."
    try:
        load_and_validate_split()
    except Exception as exc:  # noqa: BLE001
        return f"extended split invalid: {exc}"
    out_dir = resolve_output_dir(Path(args.output_dir))
    try:
        out_dir.resolve().relative_to(RESULTS_ROOT.resolve())
    except ValueError:
        return "output path must be under experiments/results/."
    params, blocker = read_frozen_params(Path(args.frozen_params))
    if blocker:
        return blocker
    expected = {
        "retrieval_pool_top_k": 8.0,
        "rerank_top_n": 8.0,
        "context_chunk_count": 5.0,
        "cad_alpha": 0.5,
        "max_new_tokens": 512.0,
    }
    for key, value in expected.items():
        if params is None or float(params.get(key, -1)) != value:
            return f"frozen parameter mismatch for {key}: expected {value}"
    return None


def print_preflight(args: argparse.Namespace) -> int:
    try:
        queries = load_and_validate_split()
        configs = validate_main_matrix()
        params, blocker = read_frozen_params(Path(args.frozen_params))
        if blocker:
            raise RuntimeError(blocker)
    except Exception as exc:  # noqa: BLE001
        print(f"PREFLIGHT FAILED: {exc}")
        return 2

    print("[Extended Validation Preflight]")
    print(f"query_split: {APPROVED_EXTENDED_SPLIT}")
    print(f"queries: {len(queries)}")
    print(f"configs: {len(configs)}")
    print(f"planned_samples: {len(queries) * len(configs)}")
    print(f"paper_counts: {EXPECTED_PAPER_COUNTS}")
    print(f"frozen_non_scd_params: {params}")
    print(f"generation_model: {args.generation_model}")
    print("decoding_mode: deterministic_greedy")
    print(f"scd_mode: {REFERENCE_SCD_MODE}")
    print(
        "reference_scd_params: "
        f"alpha={REFERENCE_SCD_ALPHA}, beta={REFERENCE_SCD_BETA}, "
        f"t_start={REFERENCE_SCD_T_START}"
    )
    print("openai_calls_made: false")
    print("ragas_calls_made: false")
    print("gt_regeneration: false")
    return 0


def run_extended_generation_execute(args: argparse.Namespace) -> int:
    blocker = check_extended_generation_guards(args)
    if blocker:
        print(f"REFUSED: {blocker}")
        return 2
    from extended_validation_executor import execute_extended_validation  # noqa: E402

    params, _ = read_frozen_params(Path(args.frozen_params))
    return execute_extended_validation(args, params or {})


def main() -> int:
    args = build_parser().parse_args()
    if args.execute:
        return run_extended_generation_execute(args)
    return print_preflight(args)


if __name__ == "__main__":
    raise SystemExit(main())
