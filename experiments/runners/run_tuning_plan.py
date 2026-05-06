"""Safe tuning-plan runner for future parameter-freeze preparation.

This script does not tune parameters or call models. It only creates the
planned sample grid that a later explicit tuning phase can use to freeze
non-axis parameters before the main HyDE x CAD x SCD matrix.
"""

from __future__ import annotations

import argparse
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", default=DEFAULT_EXPERIMENT)
    parser.add_argument(
        "--query-split",
        choices=sorted(QUERY_SPLITS),
        default="tuning_queries",
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
        "--no-openai",
        action="store_true",
        default=True,
        help="Keep OpenAI disabled. This is true by default in Phase 6.5.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.execute:
        raise SystemExit("Real execution is disabled in Phase 6.5.")

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

    print("[Tuning Plan Runner]")
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
    print(
        "parameter_freeze_rule: tune only on tuning_queries, then freeze top_k, rerank_top_n, cad_alpha, scd_beta, HyDE template, and generation settings"
    )
    print(f"model_calls_made: false")
    print(f"openai_calls_made: false")
    print(f"ragas_calls_made: false")
    print(f"gt_regeneration: false")
    print(
        f"plan_jsonl: {relative_posix(plan_path) if should_write_plan else 'not_written'}"
    )
    print(f"matrix_boolean_mapping: {matrix_boolean_summary(validate_main_matrix())}")
    print("[Planned Samples JSONL]")
    print_jsonl(samples)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
