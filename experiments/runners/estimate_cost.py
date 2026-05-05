"""Planning-only cost estimator for dry-run experiment sizing."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass


DEFAULT_OPENAI_COST_PER_CALL_USD = 0.004
DEFAULT_A100_COST_KRW_PER_HOUR = 2000
DEFAULT_USD_TO_KRW = 1400
DEFAULT_METRIC_COUNT = 4


@dataclass(frozen=True)
class CostEstimate:
    configs: int
    queries: int
    samples: int
    metric_count: int
    estimated_ragas_calls: int
    estimated_openai_cost_usd: float
    estimated_openai_cost_krw: float
    estimated_gpu_hours: float
    estimated_gpu_cost_krw: float
    estimated_total_cost_krw: float


def estimate_cost(
    configs: int,
    queries: int,
    metric_count: int = DEFAULT_METRIC_COUNT,
    openai_cost_per_call_usd: float = DEFAULT_OPENAI_COST_PER_CALL_USD,
    a100_cost_krw_per_hour: float = DEFAULT_A100_COST_KRW_PER_HOUR,
    usd_to_krw: float = DEFAULT_USD_TO_KRW,
) -> CostEstimate:
    samples = configs * queries
    estimated_ragas_calls = samples * metric_count
    estimated_openai_cost_usd = estimated_ragas_calls * openai_cost_per_call_usd
    estimated_openai_cost_krw = estimated_openai_cost_usd * usd_to_krw
    # Conservative planning placeholder: 45 seconds per sample on one A100.
    estimated_gpu_hours = round(samples * 45 / 3600, 4)
    estimated_gpu_cost_krw = estimated_gpu_hours * a100_cost_krw_per_hour
    return CostEstimate(
        configs=configs,
        queries=queries,
        samples=samples,
        metric_count=metric_count,
        estimated_ragas_calls=estimated_ragas_calls,
        estimated_openai_cost_usd=round(estimated_openai_cost_usd, 4),
        estimated_openai_cost_krw=round(estimated_openai_cost_krw, 2),
        estimated_gpu_hours=estimated_gpu_hours,
        estimated_gpu_cost_krw=round(estimated_gpu_cost_krw, 2),
        estimated_total_cost_krw=round(
            estimated_openai_cost_krw + estimated_gpu_cost_krw,
            2,
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configs", type=int, default=8)
    parser.add_argument("--queries", type=int, default=0)
    parser.add_argument("--metric-count", type=int, default=DEFAULT_METRIC_COUNT)
    parser.add_argument(
        "--openai-cost-per-call-usd",
        type=float,
        default=DEFAULT_OPENAI_COST_PER_CALL_USD,
    )
    parser.add_argument(
        "--a100-cost-krw-per-hour",
        type=float,
        default=DEFAULT_A100_COST_KRW_PER_HOUR,
    )
    parser.add_argument("--usd-to-krw", type=float, default=DEFAULT_USD_TO_KRW)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    estimate = estimate_cost(
        configs=args.configs,
        queries=args.queries,
        metric_count=args.metric_count,
        openai_cost_per_call_usd=args.openai_cost_per_call_usd,
        a100_cost_krw_per_hour=args.a100_cost_krw_per_hour,
        usd_to_krw=args.usd_to_krw,
    )
    for key, value in asdict(estimate).items():
        print(f"{key}: {value}")
    print("planning_only: true")
    print("model_calls_made: false")
    print("openai_calls_made: false")
    print("ragas_calls_made: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
