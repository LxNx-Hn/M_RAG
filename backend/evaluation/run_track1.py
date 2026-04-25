"""CLI runner for Track 1 evaluation experiments."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_ablation_module = import_module("evaluation.ablation_study")
_decoder_module = import_module("evaluation.decoder_ablation")
_ragas_module = import_module("evaluation.ragas_eval")

ABLATION_CONFIGS = _ablation_module.ABLATION_CONFIGS
CAD_ALPHA_VALUES = _ablation_module.CAD_ALPHA_VALUES
SCD_BETA_VALUES = _ablation_module.SCD_BETA_VALUES
DECODER_CONFIGS = _decoder_module.DECODER_CONFIGS
compute_language_drift_rate = _decoder_module.compute_language_drift_rate
compute_numeric_hallucination_rate = _decoder_module.compute_numeric_hallucination_rate
EvalSample = _ragas_module.EvalSample
RAGASEvaluator = _ragas_module.RAGASEvaluator

DEFAULT_API_BASE = os.environ.get("MRAG_API_BASE", "http://127.0.0.1:8000")
DEFAULT_OUTPUTS = {
    "ablation": "evaluation/results/table1_track1.json",
    "decoder": "evaluation/results/table2_decoder.json",
    "alpha-sweep": "evaluation/results/table2_alpha.json",
    "beta-sweep": "evaluation/results/table2_beta.json",
}

LOGGER = logging.getLogger("run_track1")


@dataclass
class RunContext:
    api_base: str
    token: str
    collection_name: str
    timeout: float
    checkpoint_every: int
    max_retries: int
    retry_backoff: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Track 1 evaluation modes against the local M-RAG API."
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["ablation", "decoder", "alpha-sweep", "beta-sweep"],
        help="Track 1 evaluation mode to execute.",
    )
    parser.add_argument(
        "--queries",
        default="evaluation/data/track1_queries.json",
        help="Path to Track 1 query JSON.",
    )
    parser.add_argument(
        "--papers",
        nargs="+",
        required=True,
        help="Document ids to evaluate. Results are produced per paper.",
    )
    parser.add_argument(
        "--collection-name",
        default="papers",
        help="API collection name containing the indexed papers.",
    )
    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help=f"API base URL. Default: {DEFAULT_API_BASE}",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("MRAG_API_TOKEN", ""),
        help="Bearer token for the API. Can also be provided via MRAG_API_TOKEN.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path. Defaults to a mode-specific file in evaluation/results/.",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=10,
        help="Save intermediate results every N queries.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=6,
        help="Maximum retries for transient HTTP errors like 429.",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=2.0,
        help="Base backoff seconds used for retrying 429 responses.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_queries(path_str: str) -> list[dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Query file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, dict):
        items = data.get("queries") or data.get("samples") or []
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("Unsupported query JSON format")

    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict) or not item.get("query"):
            continue
        normalized.append(item)
    return normalized


def ensure_api_available(ctx: RunContext) -> None:
    health_url = f"{ctx.api_base.rstrip('/')}/health"
    try:
        response = requests.get(health_url, timeout=min(ctx.timeout, 15))
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(
            f"API server is unavailable at {ctx.api_base}. Start it before running evaluations. {exc}"
        ) from exc


def build_headers(token: str) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def call_json_api(
    method: str,
    url: str,
    *,
    token: str,
    timeout: float,
    max_retries: int,
    retry_backoff: float,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    attempts = max(0, max_retries) + 1
    for attempt in range(attempts):
        response = requests.request(
            method=method,
            url=url,
            json=payload,
            headers=build_headers(token),
            timeout=timeout,
        )
        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}

        if response.status_code == 401:
            raise SystemExit(
                "API request failed with 401. Provide --token or MRAG_API_TOKEN."
            )
        if response.status_code == 429 and attempt < attempts - 1:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    sleep_seconds = max(float(retry_after), retry_backoff)
                except ValueError:
                    sleep_seconds = retry_backoff * (2**attempt)
            else:
                sleep_seconds = retry_backoff * (2**attempt)
            LOGGER.warning(
                "429 received from %s. Retrying in %.1fs (%s/%s)",
                url,
                sleep_seconds,
                attempt + 1,
                attempts - 1,
            )
            time.sleep(sleep_seconds)
            continue
        if response.status_code >= 400:
            detail = data.get("detail") if isinstance(data, dict) else data
            raise RuntimeError(f"{response.status_code} {url}: {detail}")
        if not isinstance(data, dict):
            raise RuntimeError(f"Unexpected API response from {url}")
        return data
    raise RuntimeError(f"Exceeded retry budget for {url}")


def warn_missing_papers(ctx: RunContext, papers: list[str]) -> None:
    url = f"{ctx.api_base.rstrip('/')}/api/papers/list"
    try:
        data = call_json_api(
            "GET",
            url,
            token=ctx.token,
            timeout=ctx.timeout,
            max_retries=ctx.max_retries,
            retry_backoff=ctx.retry_backoff,
        )
    except Exception as exc:
        LOGGER.warning("Could not validate indexed papers: %s", exc)
        return

    available = {item.get("name") for item in data.get("collections", [])}
    for paper in papers:
        if paper not in available:
            LOGGER.warning("Paper '%s' was not found in /api/papers/list.", paper)


def choose_queries_for_paper(
    queries: list[dict[str, Any]], paper: str
) -> list[dict[str, Any]]:
    selected = []
    for item in queries:
        applicable = item.get("applicable_papers") or []
        if not applicable or any(paper in str(entry) for entry in applicable):
            selected.append(item)
    return selected


def evaluate_samples(samples: list[EvalSample]) -> dict[str, Any]:
    evaluator = RAGASEvaluator(generator=None)
    return evaluator.evaluate(samples)


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    widths = [len(header) for header in headers]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))

    def _line(values: list[str]) -> str:
        return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(values))

    print(_line(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(_line(row))


def save_json(path_str: str, payload: dict[str, Any]) -> None:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def track1_query_payload(
    query: str, paper: str, config: dict[str, Any], collection_name: str
) -> dict[str, Any]:
    return {
        "query": query,
        "collection_name": collection_name,
        "use_hyde": bool(config.get("use_hyde", False)),
        "use_cad": bool(config.get("use_cad", False)),
        "cad_alpha": float(config.get("cad_alpha", 0.5)),
        "use_scd": bool(config.get("use_scd", False)),
        "scd_beta": float(config.get("scd_beta", 0.3)),
        "top_k": 5,
        "doc_id_filter": paper,
    }


def query_answer(
    ctx: RunContext,
    query_item: dict[str, Any],
    paper: str,
    config: dict[str, Any],
) -> tuple[str, list[str], dict[str, Any]]:
    base = ctx.api_base.rstrip("/")
    payload = track1_query_payload(
        query_item["query"], paper, config, ctx.collection_name
    )
    search_payload = {
        "query": query_item["query"],
        "collection_name": ctx.collection_name,
        "top_k": 5,
        "doc_id_filter": paper,
    }
    if config.get("section_filter"):
        search_payload["section_filter"] = config["section_filter"]

    search_data = call_json_api(
        "POST",
        f"{base}/api/chat/search",
        token=ctx.token,
        timeout=ctx.timeout,
        max_retries=ctx.max_retries,
        retry_backoff=ctx.retry_backoff,
        payload=search_payload,
    )
    query_data = call_json_api(
        "POST",
        f"{base}/api/chat/query",
        token=ctx.token,
        timeout=ctx.timeout,
        max_retries=ctx.max_retries,
        retry_backoff=ctx.retry_backoff,
        payload=payload,
    )
    contexts = [
        item.get("content", "")
        for item in search_data.get("results", [])
        if item.get("content")
    ]
    return query_data.get("answer", ""), contexts, query_data


def run_ragas_mode(
    *,
    ctx: RunContext,
    queries: list[dict[str, Any]],
    papers: list[str],
    configs: list[dict[str, Any]],
    mode: str,
    output_path: str,
) -> dict[str, Any]:
    results: dict[str, Any] = {
        "meta": {
            "mode": mode,
            "api_base": ctx.api_base,
            "collection_name": ctx.collection_name,
            "papers": papers,
            "queries_path": None,
            "generated_at": datetime.now().isoformat(),
        },
        "results": {},
    }

    total_queries = 0
    for paper in papers:
        paper_queries = choose_queries_for_paper(queries, paper)
        paper_result: dict[str, Any] = {}
        for config in configs:
            config_name = config["name"]
            samples: list[EvalSample] = []
            for index, query_item in enumerate(paper_queries, start=1):
                total_queries += 1
                LOGGER.info(
                    "[%s] %s | paper=%s | query %s/%s",
                    mode,
                    config_name,
                    paper,
                    index,
                    len(paper_queries),
                )
                answer, contexts, api_data = query_answer(
                    ctx, query_item, paper, config
                )
                samples.append(
                    EvalSample(
                        query=query_item["query"],
                        ground_truth=query_item.get("ground_truth", ""),
                        answer=answer,
                        contexts=contexts,
                        pipeline=api_data.get("pipeline", ""),
                    )
                )
                if (
                    ctx.checkpoint_every > 0
                    and total_queries % ctx.checkpoint_every == 0
                ):
                    partial = dict(results)
                    partial["results"] = {**results["results"], paper: {**paper_result}}
                    save_json(output_path, partial)
                    LOGGER.info("Saved checkpoint to %s", output_path)

            evaluation = evaluate_samples(samples)
            evaluation["config"] = config_name
            evaluation["paper"] = paper
            paper_result[config_name] = evaluation
        results["results"][paper] = paper_result

    save_json(output_path, results)
    return results


def build_decoder_configs(mode: str) -> list[dict[str, Any]]:
    if mode == "decoder":
        return [asdict(config) for config in DECODER_CONFIGS]
    if mode == "alpha-sweep":
        return [
            {
                "name": f"CAD alpha={alpha}",
                "use_cad": True,
                "use_scd": False,
                "cad_alpha": alpha,
                "scd_beta": 0.3,
            }
            for alpha in CAD_ALPHA_VALUES
        ]
    if mode == "beta-sweep":
        return [
            {
                "name": f"SCD beta={beta}",
                "use_cad": True,
                "use_scd": True,
                "cad_alpha": 0.5,
                "scd_beta": beta,
            }
            for beta in SCD_BETA_VALUES
        ]
    raise ValueError(f"Unsupported decoder mode: {mode}")


def run_decoder_mode(
    *,
    ctx: RunContext,
    queries: list[dict[str, Any]],
    papers: list[str],
    mode: str,
    output_path: str,
) -> dict[str, Any]:
    configs = build_decoder_configs(mode)
    results: dict[str, Any] = {
        "meta": {
            "mode": mode,
            "api_base": ctx.api_base,
            "collection_name": ctx.collection_name,
            "papers": papers,
            "generated_at": datetime.now().isoformat(),
        },
        "results": {},
    }

    total_queries = 0
    for paper in papers:
        paper_queries = choose_queries_for_paper(queries, paper)
        paper_result: dict[str, Any] = {}
        for config in configs:
            answers: list[str] = []
            gts: list[str] = []
            samples: list[EvalSample] = []
            for index, query_item in enumerate(paper_queries, start=1):
                total_queries += 1
                LOGGER.info(
                    "[%s] %s | paper=%s | query %s/%s",
                    mode,
                    config["name"],
                    paper,
                    index,
                    len(paper_queries),
                )
                answer, contexts, api_data = query_answer(
                    ctx, query_item, paper, config
                )
                answers.append(answer)
                gts.append(query_item.get("ground_truth", ""))
                samples.append(
                    EvalSample(
                        query=query_item["query"],
                        ground_truth=query_item.get("ground_truth", ""),
                        answer=answer,
                        contexts=contexts,
                        pipeline=api_data.get("pipeline", ""),
                    )
                )
                if (
                    ctx.checkpoint_every > 0
                    and total_queries % ctx.checkpoint_every == 0
                ):
                    partial = dict(results)
                    partial["results"] = {**results["results"], paper: {**paper_result}}
                    save_json(output_path, partial)
                    LOGGER.info("Saved checkpoint to %s", output_path)

            ragas_result = evaluate_samples(samples)
            paper_result[config["name"]] = {
                "config": config["name"],
                "paper": paper,
                "language_drift_rate": compute_language_drift_rate(answers),
                "numeric_hallucination_rate": compute_numeric_hallucination_rate(
                    answers, gts
                ),
                "faithfulness": ragas_result["average"]["faithfulness"],
                "answer_relevancy": ragas_result["average"]["answer_relevancy"],
                "context_precision": ragas_result["average"]["context_precision"],
                "context_recall": ragas_result["average"]["context_recall"],
                "overall": ragas_result["average"]["overall"],
            }
        results["results"][paper] = paper_result

    save_json(output_path, results)
    return results


def summarise_track1(results: dict[str, Any], mode: str) -> None:
    if mode in {"ablation"}:
        rows: list[list[str]] = []
        for paper, configs in results.get("results", {}).items():
            for name, result in configs.items():
                avg = result.get("average", {})
                rows.append(
                    [
                        paper,
                        name,
                        f"{avg.get('faithfulness', 0.0):.3f}",
                        f"{avg.get('context_precision', 0.0):.3f}",
                        f"{avg.get('answer_relevancy', 0.0):.3f}",
                        f"{avg.get('overall', 0.0):.3f}",
                    ]
                )
        print_table(
            [
                "Paper",
                "System",
                "Faithfulness",
                "Context Precision",
                "Answer Rel.",
                "Overall",
            ],
            rows,
        )
        return

    rows = []
    for paper, configs in results.get("results", {}).items():
        for name, result in configs.items():
            rows.append(
                [
                    paper,
                    name,
                    f"{result.get('numeric_hallucination_rate', 0.0):.3f}",
                    f"{result.get('language_drift_rate', 0.0):.3f}",
                    f"{result.get('faithfulness', 0.0):.3f}",
                ]
            )
    print_table(
        ["Paper", "Config", "Num Halluc.", "Lang Drift", "Faithfulness"],
        rows,
    )


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    if not args.token:
        LOGGER.warning("No API token provided. Requests will likely fail with 401.")

    output_path = args.output or DEFAULT_OUTPUTS[args.mode]
    ctx = RunContext(
        api_base=args.api_base,
        token=args.token,
        collection_name=args.collection_name,
        timeout=args.timeout,
        checkpoint_every=args.checkpoint_every,
        max_retries=args.max_retries,
        retry_backoff=args.retry_backoff,
    )

    ensure_api_available(ctx)
    warn_missing_papers(ctx, args.papers)
    queries = load_queries(args.queries)
    if not queries:
        raise SystemExit("No queries found in the provided file.")

    if args.mode == "ablation":
        configs = [asdict(config) for config in ABLATION_CONFIGS]
        results = run_ragas_mode(
            ctx=ctx,
            queries=queries,
            papers=args.papers,
            configs=configs,
            mode=args.mode,
            output_path=output_path,
        )
    else:
        results = run_decoder_mode(
            ctx=ctx,
            queries=queries,
            papers=args.papers,
            mode=args.mode,
            output_path=output_path,
        )

    summarise_track1(results, args.mode)
    LOGGER.info("Saved results to %s", output_path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
