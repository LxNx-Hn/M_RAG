"""HyDE x CAD x SCD main generation runner (planner by default; execution hard-guarded).

Default behaviour is unchanged: without ``--execute`` this script only builds
planned sample records (no model, no retrieval, no OpenAI/RAGAS/GT).

``--execute`` enters the approved main 8-config generation mode. It is hard
fail-closed: it refuses unless EVERY guard passes (see
``check_main_generation_guards``):

  - env ``CONFIRM_MAIN_8CONFIG_GENERATION=1``
  - collection == ``local_gt__papers``
  - query split == the approved main split (``decoder_main_queries``)
  - configs == exactly the 8 HyDE x CAD x SCD configs (``validate_main_matrix``)
  - OpenAI / RAGAS / GT regeneration disabled (env + flags)
  - frozen parameters exist and are actually frozen (no ``pending`` values)
  - output path under ``experiments/results/``

The execution body REUSES the proven fixed-backbone path from
``run_alice_followup.py``: ``HybridRetriever.search_with_trace`` (BGE-M3 dense +
BM25 + RRF) + CrossEncoder rerank + ContextCompressor, HyDE via
``QueryExpander``, CAD+SCD via ``create_combined_processor``. The ``Generator``
(MIDM Base) is instantiated ONCE per run and reused across all samples -- it is
never reloaded per sample (the legacy per-sample reload caused CPU offload in
2B). Records are written with the schema ``official_ragas_runner.py`` consumes.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from common import (
    DEFAULT_CAD_ALPHA,
    DEFAULT_EXPERIMENT,
    DEFAULT_GENERATION_MODEL,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_MODEL_TIER,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SCD_BETA,
    QUERY_SPLITS,
    REPO_ROOT,
    ConfigValidationError,
    apply_limit,
    build_plan,
    filter_existing_samples,
    load_query_split,
    matrix_boolean_summary,
    plan_jsonl_path,
    print_jsonl,
    relative_posix,
    resolve_output_dir,
    validate_main_matrix,
    write_jsonl,
)

# Approved main-experiment constants (must match tuning_plan holdout policy).
APPROVED_MAIN_SPLIT = "decoder_main_queries"
APPROVED_COLLECTION = "local_gt__papers"
APPROVED_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"
RESULTS_ROOT = REPO_ROOT / "experiments" / "results"
DEFAULT_FROZEN_PARAMS = REPO_ROOT / "experiments" / "configs" / "frozen_params.yaml"

# Frozen keys the main run binds before execution (flat machine-readable form).
REQUIRED_FROZEN_KEYS = (
    "rerank_top_n",
    "cad_alpha",
    "scd_beta",
    "max_new_tokens",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", default=DEFAULT_EXPERIMENT)
    parser.add_argument(
        "--query-split",
        choices=sorted(QUERY_SPLITS),
        default="decoder_main_queries",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--config-limit", type=int, default=None)
    parser.add_argument("--output-dir", default=relative_posix(DEFAULT_OUTPUT_DIR))
    parser.add_argument(
        "--model-tier",
        choices=["mini", "base"],
        default=DEFAULT_MODEL_TIER,
    )
    parser.add_argument("--generation-model", default=DEFAULT_GENERATION_MODEL)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--cad-alpha", type=float, default=DEFAULT_CAD_ALPHA)
    parser.add_argument("--scd-beta", type=float, default=DEFAULT_SCD_BETA)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--collection-name",
        default=APPROVED_COLLECTION,
        help="Execution collection. Must be local_gt__papers for the main run.",
    )
    parser.add_argument(
        "--frozen-params",
        default=str(DEFAULT_FROZEN_PARAMS),
        help="Frozen-parameter file required for --execute.",
    )
    parser.add_argument(
        "--no-openai",
        action="store_true",
        default=True,
        help="Keep OpenAI disabled. This is true by default.",
    )
    return parser


def _env_disabled(name: str) -> bool:
    """True when an enable-flag env var is unset or explicitly '0'."""
    return os.environ.get(name, "0") == "0"


def read_frozen_params(path: Path) -> tuple[dict[str, float] | None, str | None]:
    """Read a *frozen* parameter file. Returns (params, blocker).

    Fail-closed: the file must exist, must not contain any ``pending`` marker,
    must declare ``final_values_selected: true``, and must provide numeric
    values for every key in REQUIRED_FROZEN_KEYS. A draft (pending / not
    selected) is rejected.
    """
    if not path.exists():
        return None, f"frozen parameters file not found: {relative_posix(path)}"
    text = path.read_text(encoding="utf-8")
    if "pending" in text:
        return (
            None,
            "frozen parameters still contain 'pending' values; freeze incomplete",
        )
    if not re.search(r"^\s*final_values_selected:\s*true\s*$", text, re.MULTILINE):
        return None, "frozen parameters lack 'final_values_selected: true'"
    params: dict[str, float] = {}
    for key in REQUIRED_FROZEN_KEYS:
        m = re.search(
            rf"^\s*{re.escape(key)}:\s*([0-9]+(?:\.[0-9]+)?)\s*$", text, re.MULTILINE
        )
        if not m:
            return None, f"frozen parameters missing numeric '{key}'"
        params[key] = float(m.group(1))
    # retrieval pool is part of the fixed backbone; default to repo 20 if unset.
    pool_m = re.search(r"^\s*retrieval_pool_top_k:\s*([0-9]+)\s*$", text, re.MULTILINE)
    params["retrieval_pool_top_k"] = float(pool_m.group(1)) if pool_m else 20.0
    return params, None


def check_main_generation_guards(args: argparse.Namespace) -> str | None:
    """Return a blocker string if any main-generation guard fails, else None.

    Performs NO heavy imports so refusals are cheap and testable without a GPU.
    """
    if os.environ.get("CONFIRM_MAIN_8CONFIG_GENERATION") != "1":
        return "CONFIRM_MAIN_8CONFIG_GENERATION=1 is required for --execute."
    if not _env_disabled("OPENAI_ENABLED"):
        return "OpenAI must be disabled (OPENAI_ENABLED=0)."
    if not _env_disabled("RAGAS_ENABLED"):
        return "RAGAS must be disabled (RAGAS_ENABLED=0)."
    if not _env_disabled("GT_REGENERATION_ENABLED"):
        return "GT regeneration must be disabled (GT_REGENERATION_ENABLED=0)."
    if not args.no_openai:
        return "--no-openai must stay set for the main run."
    if args.collection_name != APPROVED_COLLECTION:
        return f"collection must be {APPROVED_COLLECTION}."
    if args.generation_model != APPROVED_MODEL:
        return f"generation model must be {APPROVED_MODEL} (MIDM Base)."
    if args.query_split != APPROVED_MAIN_SPLIT:
        return f"query split must be the approved main split {APPROVED_MAIN_SPLIT!r}."
    if args.config_limit is not None or args.limit is not None:
        return "--limit/--config-limit are not allowed for the full approved run."
    try:
        configs = validate_main_matrix()
    except ConfigValidationError as exc:
        return f"main matrix invalid: {exc}"
    if len(configs) != 8:
        return f"main matrix must have exactly 8 configs; found {len(configs)}."
    out_dir = resolve_output_dir(Path(args.output_dir))
    try:
        out_dir.resolve().relative_to(RESULTS_ROOT.resolve())
    except ValueError:
        return "output path must be under experiments/results/."
    _params, frozen_blocker = read_frozen_params(Path(args.frozen_params))
    if frozen_blocker:
        return frozen_blocker
    return None


def run_planner(args: argparse.Namespace) -> int:
    output_dir = resolve_output_dir(Path(args.output_dir))
    configs = validate_main_matrix()
    configs = apply_limit(configs, args.config_limit, "config")
    queries = load_query_split(args.query_split, allow_empty=args.allow_empty)
    queries = apply_limit(queries, args.limit, "query")
    samples = build_plan(
        configs=configs,
        queries=queries,
        experiment=args.experiment,
        output_dir=output_dir,
        model_tier=args.model_tier,
        model_name=args.generation_model,
        max_new_tokens=args.max_new_tokens,
        cad_alpha=args.cad_alpha,
        scd_beta=args.scd_beta,
    )
    samples, skipped_existing = filter_existing_samples(
        samples,
        output_dir=output_dir,
        enabled=args.resume or args.skip_existing,
    )

    plan_path = plan_jsonl_path(output_dir, args.experiment, args.query_split)
    should_write_plan = args.plan_only and not args.dry_run
    if should_write_plan:
        write_jsonl(plan_path, samples)

    print("[Generation Runner]")
    print(f"experiment: {args.experiment}")
    print(f"query_split: {args.query_split}")
    print(f"configs: {len(configs)}")
    print(f"queries: {len(queries)}")
    print(f"planned_samples: {len(samples)}")
    print(f"skipped_existing: {skipped_existing}")
    print(f"dry_run: {args.dry_run}")
    print(f"plan_only: {args.plan_only or not args.execute}")
    print(f"execute: {args.execute}")
    print(f"no_openai: {args.no_openai}")
    print("model_calls_made: false")
    print("openai_calls_made: false")
    print("ragas_calls_made: false")
    print("gt_regeneration: false")
    print(
        f"plan_jsonl: {relative_posix(plan_path) if should_write_plan else 'not_written'}"
    )
    print(f"matrix_boolean_mapping: {matrix_boolean_summary(validate_main_matrix())}")
    print("[Planned Samples JSONL]")
    print_jsonl(samples)
    return 0


def run_main_generation_execute(args: argparse.Namespace) -> int:
    """Hard-guarded approved main 8-config generation. Fail-closed."""
    blocker = check_main_generation_guards(args)
    if blocker:
        print(f"REFUSED: {blocker}")
        return 2
    # Only past every guard do we touch heavy backend/torch dependencies.
    from main_generation_executor import execute_main_generation  # noqa: E402

    params, _ = read_frozen_params(Path(args.frozen_params))
    return execute_main_generation(args, params or {})


def main() -> int:
    args = build_parser().parse_args()
    if args.execute:
        return run_main_generation_execute(args)
    return run_planner(args)


if __name__ == "__main__":
    raise SystemExit(main())
