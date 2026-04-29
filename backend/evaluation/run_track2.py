"""CLI runner for Track 2 evaluation experiments."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_ragas_module = import_module("evaluation.ragas_eval")
EvalSample = _ragas_module.EvalSample
RAGASEvaluator = _ragas_module.RAGASEvaluator
_openai_judge_module = import_module("evaluation.openai_judge")
OpenAIJudgeConfig = _openai_judge_module.OpenAIJudgeConfig
judge_with_openai = _openai_judge_module.judge_with_openai

PLACEHOLDER_PAPER_RE = re.compile(
    r"(paper_[A-Z]_[A-Za-z0-9_]+|doc_[A-Z]_[A-Za-z0-9_]+|lecture_[A-Z]_[A-Za-z0-9_]+|patent_[A-Z]_[A-Za-z0-9_]+)"
)

DEFAULT_API_BASE = os.environ.get("MRAG_API_BASE", "http://127.0.0.1:8000")
DEFAULT_OUTPUT = "evaluation/results/table3_domain.json"
LOGGER = logging.getLogger("run_track2")

TRACK2_CONFIGS = [
    {
        "name": "General RAG (Track 1 Full)",
        "use_hyde": True,
        "use_cad": True,
        "use_scd": True,
        "section_filter": None,
        "track_citations": False,
    },
    {
        "name": "+ Section-aware Chunking",
        "use_hyde": True,
        "use_cad": True,
        "use_scd": True,
        "section_filter": "method",
        "track_citations": False,
    },
    {
        "name": "+ Query Router Section Filter",
        "use_hyde": True,
        "use_cad": True,
        "use_scd": True,
        "section_filter": "result",
        "track_citations": False,
    },
    {
        "name": "+ RAPTOR-style Retrieval",
        "use_hyde": True,
        "use_cad": True,
        "use_scd": True,
        "section_filter": "abstract",
        "track_citations": False,
    },
    {
        "name": "+ Citation Tracker",
        "use_hyde": True,
        "use_cad": True,
        "use_scd": True,
        "section_filter": None,
        "track_citations": True,
    },
    {
        "name": "Full Track 2 System",
        "use_hyde": True,
        "use_cad": True,
        "use_scd": True,
        "section_filter": "result",
        "track_citations": True,
    },
]


@dataclass
class RunContext:
    api_base: str
    token: str
    collection_name: str
    timeout: float
    checkpoint_every: int
    max_retries: int
    retry_backoff: float
    resume: bool
    config_names: set[str]
    judge_model: str | None
    openai_api_key: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Track 2 domain evaluation against the local M-RAG API."
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["domain"],
        help="Track 2 evaluation mode.",
    )
    parser.add_argument(
        "--queries",
        default=str(PROJECT_ROOT / "evaluation/data/track2_queries.json"),
        help="Path to Track 2 query JSON.",
    )
    parser.add_argument(
        "--papers",
        nargs="+",
        required=True,
        help="Document ids to evaluate.",
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
        default=DEFAULT_OUTPUT,
        help=f"Output JSON path. Default: {DEFAULT_OUTPUT}",
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
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing output JSON and skip completed configs.",
    )
    parser.add_argument(
        "--config-names",
        nargs="+",
        default=None,
        help="Optional config names to run. Matching configs are re-run and overwrite existing results.",
    )
    parser.add_argument(
        "--judge-model",
        default=os.environ.get("OPENAI_JUDGE_MODEL", ""),
        help="Optional OpenAI judge model for RAGAS-style evaluation, e.g. gpt-4o.",
    )
    parser.add_argument(
        "--openai-api-key",
        default=os.environ.get("OPENAI_API_KEY", ""),
        help="OpenAI API key used when --judge-model is set.",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


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
        try:
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                headers=build_headers(token),
                timeout=timeout,
            )
        except requests.RequestException as exc:
            if attempt < attempts - 1:
                sleep_seconds = retry_backoff * (2**attempt)
                LOGGER.warning(
                    "Request error from %s: %s. Retrying in %.1fs (%s/%s)",
                    url,
                    exc,
                    sleep_seconds,
                    attempt + 1,
                    attempts - 1,
                )
                time.sleep(sleep_seconds)
                continue
            raise RuntimeError(f"Request failed for {url}: {exc}") from exc

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


def ensure_api_available(ctx: RunContext) -> None:
    health_url = f"{ctx.api_base.rstrip('/')}/health"
    try:
        response = requests.get(health_url, timeout=min(ctx.timeout, 15))
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(
            f"API server is unavailable at {ctx.api_base}. Start it before running evaluations. {exc}"
        ) from exc


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

    return [item for item in items if isinstance(item, dict) and item.get("query")]


def judge_text(ctx: RunContext, prompt: str, labels: list[str] | None = None) -> str:
    if ctx.judge_model and ctx.openai_api_key:
        return judge_with_openai(
            config=OpenAIJudgeConfig(
                model=ctx.judge_model,
                api_key=ctx.openai_api_key,
                timeout=ctx.timeout,
            ),
            prompt=prompt,
            labels=labels,
        )
    # Prefer label ranking when candidate labels are provided for deterministic scoring.
    payload: dict[str, Any] = {"prompt": prompt, "max_new_tokens": 32}
    if labels:
        payload["labels"] = labels
    data = call_json_api(
        "POST",
        f"{ctx.api_base.rstrip('/')}/api/chat/judge",
        token=ctx.token,
        timeout=ctx.timeout,
        max_retries=ctx.max_retries,
        retry_backoff=ctx.retry_backoff,
        payload=payload,
    )
    text = str(data.get("text", "")).strip()
    if not text:
        raise RuntimeError("Judge endpoint returned an empty response.")
    return text


def evaluate_samples(ctx: RunContext, samples: list[EvalSample]) -> dict[str, Any]:
    evaluator = RAGASEvaluator(
        judge_fn=lambda prompt, labels=None: judge_text(ctx, prompt, labels)
    )
    return evaluator.evaluate(samples)


def load_existing_results(output_path: str, resume: bool) -> dict[str, Any]:
    if not resume:
        return {}
    path = Path(output_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return {}
    LOGGER.info("Resuming from %s", output_path)
    return data


def is_domain_config_completed(result: Any) -> bool:
    if not isinstance(result, dict):
        return False
    return result.get("status") == "completed"


def select_requested_configs(
    configs: list[dict[str, Any]],
    requested_names: set[str],
) -> list[dict[str, Any]]:
    if not requested_names:
        return configs

    selected = [config for config in configs if config["name"] in requested_names]
    missing = sorted(requested_names - {config["name"] for config in selected})
    if missing:
        raise SystemExit("Unknown config names: " + ", ".join(missing))
    return selected


def save_json(path_str: str, payload: dict[str, Any]) -> None:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


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


def resolve_ground_truth(query_item: dict[str, Any], paper: str) -> str:
    by_paper = query_item.get("ground_truth_by_paper")
    if isinstance(by_paper, dict):
        value = by_paper.get(paper, "")
        if isinstance(value, str):
            return value
    return str(query_item.get("ground_truth", ""))


def select_queries_or_fail(
    queries: list[dict[str, Any]],
    paper: str,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    unresolved_tokens: list[str] = []

    for item in queries:
        applicable = item.get("applicable_papers") or []
        if not applicable:
            continue

        normalized_entries = [
            str(entry).strip() for entry in applicable if str(entry).strip()
        ]
        for entry in normalized_entries:
            unresolved_tokens.extend(PLACEHOLDER_PAPER_RE.findall(entry))

        if paper in normalized_entries:
            selected.append(item)

    if unresolved_tokens:
        unresolved_text = ", ".join(dict.fromkeys(unresolved_tokens))
        raise SystemExit(
            f"Placeholder paper ids are not supported in Track 2 runs: {unresolved_text}. "
            "Rewrite the query file with actual doc ids."
        )
    if not selected:
        raise SystemExit(
            f"No paper-specific queries matched '{paper}'. "
            "This run would be invalid. Fix applicable_papers with actual doc ids."
        )
    return selected


def track_citations_if_needed(
    ctx: RunContext,
    paper: str,
    config: dict[str, Any],
) -> dict[str, Any] | None:
    if not config.get("track_citations"):
        return None

    try:
        return call_json_api(
            "POST",
            f"{ctx.api_base.rstrip('/')}/api/citations/track",
            token=ctx.token,
            # Citation fetch can block on external sources. Keep this bounded
            # so Track 2 evaluation itself does not stall for tens of minutes.
            timeout=min(ctx.timeout, 60.0),
            max_retries=min(ctx.max_retries, 1),
            retry_backoff=max(ctx.retry_backoff, 2.0),
            payload={
                "doc_id": paper,
                "collection_name": ctx.collection_name,
                "max_citations": 3,
            },
        )
    except Exception as exc:
        LOGGER.warning(
            "Citation tracking failed for paper=%s config=%s: %s",
            paper,
            config.get("name"),
            exc,
        )
        return {
            "fetched_count": 0,
            "indexed_count": 0,
            "error": str(exc),
        }


def run_query(
    ctx: RunContext,
    paper: str,
    query_item: dict[str, Any],
    config: dict[str, Any],
) -> tuple[str, list[str], dict[str, Any]]:
    base = ctx.api_base.rstrip("/")
    search_payload = {
        "query": query_item["query"],
        "collection_name": ctx.collection_name,
        "top_k": 5,  # thesis default; see config.TOP_K_RERANK
        "doc_id_filter": paper,
    }
    if config.get("section_filter"):
        search_payload["section_filter"] = config["section_filter"]

    query_payload = {
        "query": query_item["query"],
        "collection_name": ctx.collection_name,
        "use_hyde": bool(config.get("use_hyde", True)),
        "use_cad": bool(config.get("use_cad", True)),
        "cad_alpha": 0.5,
        "use_scd": bool(config.get("use_scd", True)),
        "scd_beta": 0.3,
        "top_k": 5,  # thesis default; see config.TOP_K_RERANK
        "doc_id_filter": paper,
        "section_filter": config.get("section_filter"),
    }

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
        payload=query_payload,
    )
    contexts = [
        item.get("content", "")
        for item in search_data.get("results", [])
        if item.get("content")
    ]
    return query_data.get("answer", ""), contexts, query_data


def run_domain_mode(
    ctx: RunContext,
    queries: list[dict[str, Any]],
    papers: list[str],
    output_path: str,
) -> dict[str, Any]:
    existing = load_existing_results(output_path, ctx.resume or bool(ctx.config_names))
    results: dict[str, Any] = {
        "meta": {
            "mode": "domain",
            "api_base": ctx.api_base,
            "collection_name": ctx.collection_name,
            "papers": papers,
            "generated_at": datetime.now().isoformat(),
            "resume": ctx.resume,
            "config_names": sorted(ctx.config_names),
        },
        "results": (
            existing.get("results", {})
            if isinstance(existing.get("results"), dict)
            else {}
        ),
    }

    for paper in papers:
        paper_queries = select_queries_or_fail(queries, paper)
        paper_result: dict[str, Any] = dict(results["results"].get(paper, {}))
        for config in select_requested_configs(TRACK2_CONFIGS, ctx.config_names):
            if not ctx.config_names and is_domain_config_completed(
                paper_result.get(config["name"])
            ):
                LOGGER.info(
                    "Skipping completed config=%s paper=%s",
                    config["name"],
                    paper,
                )
                continue
            LOGGER.info("[domain] %s | paper=%s", config["name"], paper)
            citation_data = track_citations_if_needed(ctx, paper, config)
            samples: list[EvalSample] = []
            query_failures = 0
            for index, query_item in enumerate(paper_queries, start=1):
                LOGGER.info(
                    "[domain] %s | paper=%s | query %s/%s",
                    config["name"],
                    paper,
                    index,
                    len(paper_queries),
                )
                try:
                    answer, contexts, api_data = run_query(
                        ctx, paper, query_item, config
                    )
                except Exception as exc:
                    LOGGER.warning(
                        "Query %s/%s skipped after all retries (%s: %s)",
                        index,
                        len(paper_queries),
                        type(exc).__name__,
                        exc,
                    )
                    query_failures += 1
                    continue
                samples.append(
                    EvalSample(
                        query=query_item["query"],
                        ground_truth=resolve_ground_truth(query_item, paper),
                        answer=answer,
                        contexts=contexts,
                        pipeline=api_data.get("pipeline", ""),
                    )
                )
            if not samples:
                LOGGER.error(
                    "All %s queries failed for config=%s paper=%s. Skipping config.",
                    len(paper_queries),
                    config["name"],
                    paper,
                )
                continue
            if query_failures:
                LOGGER.warning(
                    "%s/%s queries failed for config=%s paper=%s. "
                    "Evaluation continues with %s samples.",
                    query_failures,
                    len(paper_queries),
                    config["name"],
                    paper,
                    len(samples),
                )

            try:
                evaluation = evaluate_samples(ctx, samples)
                average = evaluation["average"]
                per_sample = evaluation["per_sample"]
                status = "completed"
                error = None
            except Exception as exc:
                LOGGER.error(
                    "evaluate_samples failed for config=%s paper=%s: %s",
                    config["name"],
                    paper,
                    exc,
                    exc_info=True,
                )
                average = {}
                per_sample = []
                status = "failed"
                error = str(exc)
            paper_result[config["name"]] = {
                "config": config["name"],
                "paper": paper,
                "average": average,
                "per_sample": per_sample,
                "citation_tracking": {
                    "enabled": bool(config.get("track_citations")),
                    "fetched_count": (citation_data or {}).get("fetched_count", 0),
                    "indexed_count": (citation_data or {}).get("indexed_count", 0),
                },
                "section_filter": config.get("section_filter"),
                "status": status,
                **({"error": error} if error else {}),
            }
            results["results"][paper] = paper_result
            if ctx.checkpoint_every > 0:
                save_json(output_path, results)
                LOGGER.info(
                    "Saved checkpoint after config=%s paper=%s to %s",
                    config["name"],
                    paper,
                    output_path,
                )
        results["results"][paper] = paper_result

    save_json(output_path, results)
    return results


def print_summary(results: dict[str, Any]) -> None:
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
                ]
            )
    print_table(
        ["Paper", "System", "Faithfulness", "Context Precision", "Answer Relevancy"],
        rows,
    )


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    if not args.token:
        LOGGER.warning("No API token provided. Requests will likely fail with 401.")

    ctx = RunContext(
        api_base=args.api_base,
        token=args.token,
        collection_name=args.collection_name,
        timeout=args.timeout,
        checkpoint_every=args.checkpoint_every,
        max_retries=args.max_retries,
        retry_backoff=args.retry_backoff,
        resume=args.resume,
        config_names=set(args.config_names or []),
        judge_model=(args.judge_model or "").strip() or None,
        openai_api_key=(args.openai_api_key or "").strip(),
    )

    if ctx.judge_model and not ctx.openai_api_key:
        raise SystemExit(
            "--judge-model was provided but no OpenAI API key is available. "
            "Set OPENAI_API_KEY or pass --openai-api-key."
        )

    ensure_api_available(ctx)
    queries = load_queries(args.queries)
    if not queries:
        raise SystemExit("No queries found in the provided file.")

    results = run_domain_mode(ctx, queries, args.papers, args.output)
    print_summary(results)
    LOGGER.info("Saved results to %s", args.output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
