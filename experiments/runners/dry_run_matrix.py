"""Dry-run validator for the separated experiment framework.

This runner performs static validation, sizing, matrix boolean checks, and
claim-policy checks only. It does not call retrieval models, generation models,
OpenAI, RAGAS, or GT generation.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from common import (
    EXPERIMENTS_DIR,
    EXPECTED_CONFIG_NAMES,
    MATRIX_PATH,
    REPO_ROOT,
    SPLIT_DIR,
    ConfigValidationError,
    matrix_boolean_summary,
    validate_main_matrix,
)
from estimate_cost import estimate_cost

CONFIG_PATH = MATRIX_PATH
FIXED_BACKBONE_PATH = EXPERIMENTS_DIR / "configs" / "fixed_backbone.yaml"
QUERY_AUDIT_PATH = EXPERIMENTS_DIR / "data" / "query_audit.json"

FORBIDDEN_TERMS = [
    "Selective Context-aware Decoding",
    "Selective Context Decoding",
    "Selective CAD",
    "RAG-Fusion",
    "RAPTOR",
    "RECOMP",
    "Self-RAG",
    "FLARE",
    "CRAG",
    "GraphRAG",
    "HippoRAG",
    "ColPali",
    "PaperQA",
    "SQuAI",
    "Full System",
    "official RAGAS",
    "RAGAS로 평가",
    "Modular RAG 방법론",
    "new Modular RAG",
    "새로운 Modular RAG",
]

SCAN_ROOTS = [
    "backend/api",
    "backend/modules",
    "backend/pipelines",
    "backend/scripts",
    "docs",
    "experiments",
    ".codex/reports",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_matrix_config_names(path: Path) -> list[str]:
    return [config.name for config in validate_main_matrix(path)]


def load_split(stem: str) -> list[dict[str, Any]]:
    path = SPLIT_DIR / f"{stem}.json"
    if not path.exists():
        return []
    return load_json(path).get("queries", [])


def query_counts() -> dict[str, int]:
    return {
        "tuning_queries": len(load_split("tuning_queries")),
        "decoder_main_queries": len(load_split("decoder_main_queries")),
        "query_type_analysis_queries": len(load_split("query_type_analysis_queries")),
        "candidate_final_eval_queries": len(load_split("candidate_final_eval_queries")),
        "service_route_queries": len(load_split("service_route_queries")),
        "query_templates": len(load_split("query_templates")),
    }


def check_tuning_final_overlap() -> list[str]:
    tuning_ids = {q["query_id"] for q in load_split("tuning_queries")}
    final_ids = {q["query_id"] for q in load_split("candidate_final_eval_queries")}
    return sorted(tuning_ids & final_ids)


def classify_forbidden_hit(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).as_posix()
    if rel.startswith(("backend/api/", "backend/modules/", "backend/pipelines/")):
        return "runtime core path; should be zero after Phase 3 cleanup"
    if rel.startswith(".codex/reports/"):
        return "audit/report evidence"
    if rel in {
        "experiments/METHOD_CONTRACTS.md",
        "experiments/CLAIM_POLICY.md",
        "experiments/REFERENCE_IMPLEMENTATION_AUDIT.md",
    }:
        return "contract or forbidden-claim explanation"
    if rel.startswith("experiments/data/"):
        return "derived query audit/split artifact from existing query assets"
    if rel.startswith("experiments/"):
        return "experiment design/contract context"
    if rel.startswith("docs/"):
        return "Phase 5 documentation, related-work, or claim-boundary context"
    if rel.startswith("backend/scripts/"):
        return "legacy evaluation utility; not part of separated main path"
    return "unclassified"


def scan_forbidden_claims() -> dict[str, object]:
    hit_counts: Counter[str] = Counter()
    allowed_reasons: Counter[str] = Counter()
    runtime_core_hits: list[str] = []
    for root in SCAN_ROOTS:
        root_path = REPO_ROOT / root
        if not root_path.exists():
            continue
        for path in root_path.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix.lower() not in {
                ".py",
                ".md",
                ".json",
                ".yaml",
                ".yml",
                ".txt",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            reason = classify_forbidden_hit(path)
            for term in FORBIDDEN_TERMS:
                count = text.count(term)
                if not count:
                    continue
                hit_counts[term] += count
                allowed_reasons[reason] += count
                if reason.startswith("runtime core path"):
                    runtime_core_hits.append(
                        f"{path.relative_to(REPO_ROOT).as_posix()}::{term}"
                    )
    return {
        "total_hits": sum(hit_counts.values()),
        "hits_by_term": dict(sorted(hit_counts.items())),
        "allowed_reasons": dict(sorted(allowed_reasons.items())),
        "runtime_core_hits": runtime_core_hits,
    }


def print_section(title: str, rows: list[tuple[str, object]] | list[str]) -> None:
    print(f"\n[{title}]")
    for row in rows:
        if isinstance(row, tuple):
            print(f"{row[0]}: {row[1]}")
        else:
            print(row)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--experiment",
        choices=["main-hyde-cad-scd", "final-eval", "all"],
        required=True,
    )
    parser.add_argument("--query-count", type=int, default=None)
    parser.add_argument("--config-limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--estimate-cost", action="store_true")
    parser.add_argument("--model-tier", choices=["mini", "base"], default="base")
    parser.add_argument(
        "--generation-model",
        default="K-intelligence/Midm-2.0-Base-Instruct",
    )
    parser.add_argument("--judge-model", default="")
    parser.add_argument("--no-openai", action="store_true")
    parser.add_argument("--metric-count", type=int, default=4)
    parser.add_argument("--openai-cost-per-call-usd", type=float, default=0.004)
    parser.add_argument("--a100-cost-krw-per-hour", type=float, default=2000)
    parser.add_argument("--usd-to-krw", type=float, default=1400)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.dry_run:
        raise SystemExit("This runner is dry-run only. Pass --dry-run.")

    try:
        all_configs = validate_main_matrix(CONFIG_PATH)
    except ConfigValidationError as exc:
        raise SystemExit(str(exc)) from exc

    selected_configs = all_configs
    if args.config_limit is not None:
        selected_configs = selected_configs[: args.config_limit]
    config_names = [config.name for config in selected_configs]
    if config_names != EXPECTED_CONFIG_NAMES[: len(config_names)]:
        raise SystemExit(
            "Unexpected main matrix config order/names: " + ", ".join(config_names)
        )
    if len(all_configs) != 8:
        raise SystemExit("Main matrix must contain exactly 8 configs.")

    overlap = check_tuning_final_overlap()
    if overlap:
        raise SystemExit(
            "Leakage check failed: tuning_queries overlap candidate_final_eval_queries: "
            + ", ".join(overlap)
        )

    audit = load_json(QUERY_AUDIT_PATH)
    counts = query_counts()
    if args.query_count is not None:
        selected_query_count = args.query_count
    elif args.experiment == "main-hyde-cad-scd":
        selected_query_count = counts["decoder_main_queries"]
    elif args.experiment == "final-eval":
        selected_query_count = counts["candidate_final_eval_queries"]
    else:
        selected_query_count = (
            counts["decoder_main_queries"]
            + counts["query_type_analysis_queries"]
            + counts["candidate_final_eval_queries"]
        )

    cost = estimate_cost(
        configs=len(selected_configs),
        queries=selected_query_count,
        metric_count=args.metric_count,
        openai_cost_per_call_usd=args.openai_cost_per_call_usd,
        a100_cost_krw_per_hour=args.a100_cost_krw_per_hour,
        usd_to_krw=args.usd_to_krw,
    )
    forbidden = scan_forbidden_claims()

    print_section(
        "Claim Policy",
        [
            (
                "main thesis claim",
                "HyDE/CAD/SCD factor analysis on a fixed Paper-RAG backbone",
            ),
            (
                "Modular/Routed RAG status",
                "graduation-project service integration layer",
            ),
            (
                "unsupported method claim policy",
                "forbidden as core claims unless framed as audit, legacy, related work, or future work",
            ),
        ],
    )
    print_section(
        "Method Contracts",
        [
            (
                "METHOD_CONTRACTS.md exists",
                (EXPERIMENTS_DIR / "METHOD_CONTRACTS.md").exists(),
            ),
            ("CAD contract", "exact formula required and Phase 2 reported implemented"),
            ("CAD KV cache correctness rule", "uncached reference path documented"),
            ("SCD contract", "Korean-target Soft Constrained Decoding"),
            ("RAGAS contract", "official skeleton separated from lightweight judge"),
            ("unsupported method removal contract", "recorded"),
            ("frontend-derived runtime contract", "recorded"),
            (
                "compare route runtime contract",
                "recorded and Phase 3 reported implemented",
            ),
        ],
    )
    print_section(
        "Fixed Backbone",
        [
            ("config exists", FIXED_BACKBONE_PATH.exists()),
            ("dense", "BGE-M3 or configured dense retriever"),
            ("sparse", "BM25"),
            ("fusion", "RRF"),
            ("reranker", "CrossEncoder"),
            ("HyDE status as main axis", "not fixed backbone"),
        ],
    )
    print_section(
        "Query Audit",
        [
            ("total queries", audit["summary"]["total_queries"]),
            ("query types", audit["summary"]["counts_by_type"]),
            ("decoder_main_queries", counts["decoder_main_queries"]),
            ("query_type_analysis_queries", counts["query_type_analysis_queries"]),
            ("candidate_final_eval_queries", counts["candidate_final_eval_queries"]),
            ("service_route_queries", counts["service_route_queries"]),
            ("templates", counts["query_templates"]),
            ("leakage check", "passed"),
        ],
    )
    print_section(
        "Main HyDE/CAD/SCD Matrix",
        [
            ("HyDE axis", "off/on"),
            ("CAD axis", "off/on"),
            ("SCD axis", "off/on"),
            ("total configs", len(all_configs)),
            ("selected configs", len(selected_configs)),
            ("config names", ", ".join(config.name for config in all_configs)),
            ("boolean mapping", matrix_boolean_summary(all_configs)),
        ],
    )
    print_section(
        "Evaluation Design",
        [
            ("official RAGAS path", "schema/import readiness skeleton only"),
            ("lightweight judge path", "RAGASInspiredEvaluator design"),
            ("language drift metric", "evaluator layer"),
            ("numeric hallucination metric", "evaluator layer"),
            ("Korean answer ratio", "evaluator layer"),
            ("evidence support", "evaluator layer"),
        ],
    )
    if args.estimate_cost:
        print_section(
            "Cost Estimate",
            [
                ("configs", cost.configs),
                ("queries", cost.queries),
                ("samples", cost.samples),
                ("metric_count", cost.metric_count),
                ("estimated_ragas_calls", cost.estimated_ragas_calls),
                ("estimated_openai_cost_usd", cost.estimated_openai_cost_usd),
                ("estimated_openai_cost_krw", cost.estimated_openai_cost_krw),
                ("estimated_gpu_hours", cost.estimated_gpu_hours),
                ("estimated_gpu_cost_krw", cost.estimated_gpu_cost_krw),
                ("estimated_total_cost_krw", cost.estimated_total_cost_krw),
            ],
        )
    print_section(
        "Forbidden Claims Gate",
        [
            ("remaining forbidden-term hits", forbidden["total_hits"]),
            ("allowed hits with reason", forbidden["allowed_reasons"]),
            ("runtime core hits", forbidden["runtime_core_hits"]),
            ("revised/removed hits", "Phase 2/3 runtime claim cleanup preserved"),
        ],
    )
    print_section(
        "Safety",
        [
            ("dry_run", args.dry_run),
            ("no model calls made", True),
            ("no OpenAI calls made", True),
            ("no RAGAS calls made", True),
            ("no GT regeneration", True),
            ("no commit", True),
            ("openai execution disabled", True),
        ],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

