from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
TEST_QUERIES_PATH = PROJECT_ROOT / "evaluation" / "data" / "track1_queries.json"
OUTPUT_PATH = PROJECT_ROOT / "evaluation" / "data" / "pseudo_gt_track1.json"

PLACEHOLDER_PAPER_RE = re.compile(
    r"(paper_[A-Z]_[A-Za-z0-9_]+|doc_[A-Z]_[A-Za-z0-9_]+|lecture_[A-Z]_[A-Za-z0-9_]+|patent_[A-Z]_[A-Za-z0-9_]+)"
)

_OPENAI_GT_PROMPT = (
    "You are an expert academic assistant. "
    "Answer the question using ONLY information from the provided document excerpts. "
    "Be concise and factual. If the answer is not in the excerpts, write 'Not found in document.'\n\n"
    "Document excerpts:\n{contexts}\n\n"
    "Question: {query}\n\n"
    "Answer:"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate ground truth answers for evaluation queries. "
        "Default mode calls the local M-RAG API (Naive RAG). "
        "Use --gt-model to generate from an external OpenAI model instead."
    )
    parser.add_argument(
        "--collection", required=True, help="Collection name passed to /api/chat/query."
    )
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--input", type=Path, default=TEST_QUERIES_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--max-retries",
        type=int,
        default=6,
        help="Maximum retries for transient API/network errors.",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=2.0,
        help="Base backoff seconds for retries (exponential).",
    )
    parser.add_argument(
        "--min-interval",
        type=float,
        default=0.0,
        help="Minimum delay in seconds between query attempts.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("MRAG_API_TOKEN", ""),
        help="Bearer token for authenticated APIs. Can also be set via MRAG_API_TOKEN.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List target queries without calling the API or modifying files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Regenerate pseudo ground truth even when ground_truth fields are already "
            "filled in the input file."
        ),
    )
    # ── External GT generation ──────────────────────────────────────────────
    parser.add_argument(
        "--gt-model",
        default=None,
        choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        help=(
            "Use an external OpenAI model to generate ground truth from retrieved "
            "paper contexts instead of the local M-RAG generation model. "
            "Requires OPENAI_API_KEY env variable or --openai-api-key."
        ),
    )
    parser.add_argument(
        "--openai-api-key",
        default=os.environ.get("OPENAI_API_KEY", ""),
        help="OpenAI API key. Prefer setting OPENAI_API_KEY env variable over this flag.",
    )
    parser.add_argument(
        "--search-top-k",
        type=int,
        default=5,
        help="Number of contexts retrieved per paper when using --gt-model (default: 5).",
    )
    parser.add_argument(
        "--update-source",
        action="store_true",
        help=(
            "Also write generated ground_truth values back into the input query file. "
            "Disabled by default so evaluation source files stay clean."
        ),
    )
    return parser.parse_args()


def _load_payload(path: Path) -> tuple[dict | None, list[dict]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if isinstance(data, dict):
        return data, data.get("queries", [])
    return None, data


def _needs_pseudo_gt(item: dict) -> bool:
    gt = str(item.get("ground_truth", "")).strip()
    by_paper = item.get("ground_truth_by_paper")
    applicable = item.get("applicable_papers") or []
    if applicable:
        if not isinstance(by_paper, dict):
            return True
        return any(not str(by_paper.get(paper, "")).strip() for paper in applicable)
    return not gt


def _build_headers(token: str) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _search_contexts(
    api_url: str,
    collection_name: str,
    query: str,
    token: str,
    timeout: int,
    doc_id_filter: str | None,
    top_k: int,
) -> list[str]:
    """Retrieve document contexts from the M-RAG search endpoint."""
    payload: dict = {
        "query": query,
        "collection_name": collection_name,
        "top_k": top_k,
    }
    if doc_id_filter:
        payload["doc_id_filter"] = doc_id_filter
    try:
        resp = requests.post(
            f"{api_url.rstrip('/')}/api/chat/search",
            json=payload,
            headers=_build_headers(token),
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            item.get("content", "")
            for item in data.get("results", [])
            if item.get("content")
        ]
    except Exception as exc:
        print(f"  Search failed ({exc}); using empty context.", file=sys.stderr)
        return []


def _query_openai_gt(
    api_key: str,
    model: str,
    query: str,
    contexts: list[str],
) -> str:
    """Generate a ground truth answer using OpenAI, grounded in retrieved contexts."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "openai package not installed. Run: pip install openai>=1.30.0"
        )
    if not api_key:
        raise RuntimeError(
            "OpenAI API key required. Set OPENAI_API_KEY env variable or use --openai-api-key."
        )
    client = OpenAI(api_key=api_key)
    ctx_text = "\n\n".join(
        f"[Excerpt {i + 1}]\n{ctx[:600]}" for i, ctx in enumerate(contexts[:5])
    )
    prompt = _OPENAI_GT_PROMPT.format(
        contexts=ctx_text or "(no excerpts retrieved)", query=query
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.0,
    )
    answer = response.choices[0].message.content.strip()
    if not answer:
        raise ValueError("OpenAI returned an empty response.")
    return answer


def _query_api(
    api_url: str,
    collection_name: str,
    query: str,
    timeout: int,
    token: str,
    max_retries: int,
    retry_backoff: float,
    doc_id_filter: str | None = None,
) -> str:
    """Generate a ground truth answer via the local M-RAG query API (Naive RAG)."""
    attempts = max(0, max_retries) + 1
    for attempt in range(attempts):
        try:
            response = requests.post(
                f"{api_url.rstrip('/')}/api/chat/query",
                json={
                    "query": query,
                    "collection_name": collection_name,
                    "use_cad": False,
                    "use_scd": False,
                    "use_hyde": False,
                    "top_k": 5,
                    **({"doc_id_filter": doc_id_filter} if doc_id_filter else {}),
                },
                headers=_build_headers(token),
                timeout=timeout,
            )
        except requests.RequestException as exc:
            if attempt < attempts - 1:
                sleep_seconds = retry_backoff * (2**attempt)
                print(
                    f"  Retryable network error: {exc} (sleep {sleep_seconds:.1f}s)",
                    file=sys.stderr,
                )
                time.sleep(sleep_seconds)
                continue
            raise

        if response.status_code == 429 and attempt < attempts - 1:
            retry_after = response.headers.get("Retry-After")
            try:
                sleep_seconds = max(float(retry_after or 0), retry_backoff)
            except ValueError:
                sleep_seconds = retry_backoff * (2**attempt)
            print(f"  429 received. Retrying in {sleep_seconds:.1f}s", file=sys.stderr)
            time.sleep(sleep_seconds)
            continue

        response.raise_for_status()
        data = response.json()
        answer = str(data.get("answer", "")).strip()
        if not answer:
            raise ValueError("Empty answer returned from API.")
        return answer

    raise RuntimeError("Exceeded retry budget while generating pseudo ground truth.")


def _resolve_target_papers(item: dict) -> list[str]:
    applicable = item.get("applicable_papers") or []
    if not applicable:
        return []

    resolved_papers: list[str] = []
    unresolved_tokens: list[str] = []
    for entry in applicable:
        text = str(entry).strip()
        unresolved_tokens.extend(PLACEHOLDER_PAPER_RE.findall(text))
        if not text:
            continue
        if "+" in text or "(" in text or ")" in text:
            raise ValueError(
                f"Ambiguous applicable_papers entry '{entry}'. "
                "Use single actual doc ids for pseudo-GT generation."
            )
        resolved_papers.append(text)

    if unresolved_tokens:
        unresolved_text = ", ".join(dict.fromkeys(unresolved_tokens))
        raise ValueError(
            f"Unresolved placeholder paper ids: {unresolved_text}. "
            "Rewrite the query file with actual doc ids."
        )

    return list(dict.fromkeys(resolved_papers))


def _resolve_cli_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (Path.cwd() / path).resolve()


def _display_project_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _persist_state(
    *,
    source_path: Path,
    output_path: Path,
    root_payload: dict | None,
    queries: list[dict],
    failures: list[dict],
    collection_name: str,
    api_url: str,
    gt_model: str | None,
    attempted: int,
    success: int,
    failed: int,
    update_source: bool,
) -> None:
    output_payload = {
        "_meta": {
            "source_file": _display_project_path(source_path),
            "collection_name": collection_name,
            "api_url": api_url,
            "gt_model": gt_model or "local-naive-rag",
            "attempted": attempted,
            "succeeded": success,
            "failed": failed,
        },
        "queries": queries,
        "failures": failures,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if update_source:
        updated_payload = root_payload if root_payload is not None else queries
        if root_payload is not None:
            root_payload["queries"] = queries
        source_path.write_text(
            json.dumps(updated_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def main() -> int:
    args = parse_args()
    args.input = _resolve_cli_path(args.input)
    args.output = _resolve_cli_path(args.output)

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    use_openai = bool(args.gt_model)
    if use_openai:
        if not args.openai_api_key:
            print(
                "ERROR: --gt-model requires an OpenAI API key. "
                "Set OPENAI_API_KEY environment variable or use --openai-api-key.",
                file=sys.stderr,
            )
            return 1
        print(
            f"[gt-model] Using {args.gt_model} to generate ground truth from paper contexts."
        )
    else:
        print("[gt-model] Using local M-RAG API (Naive RAG) to generate ground truth.")

    root_payload, queries = _load_payload(args.input)
    targets = (
        queries if args.force else [item for item in queries if _needs_pseudo_gt(item)]
    )
    if args.force:
        print(
            f"Force mode enabled. Regenerating ground truth for {len(targets)} queries."
        )
    else:
        print(f"Found {len(targets)} queries with empty ground_truth.")
    if args.dry_run:
        for index, item in enumerate(targets, start=1):
            print(f"Query {index}/{len(targets)}: {item.get('query', '')}")
        print("Dry run complete. No API calls were made and no files were modified.")
        return 0

    if not args.token and not use_openai:
        print(
            "Warning: no token provided. Authenticated endpoints may fail with 401.",
            file=sys.stderr,
        )

    success = 0
    failed = 0
    failures: list[dict] = []
    last_attempt_at: float | None = None

    for index, item in enumerate(targets, start=1):
        query = str(item.get("query", "")).strip()
        print(f"Query {index}/{len(targets)}: {query}", flush=True)
        if not query:
            failed += 1
            failures.append({"query": query, "error": "Empty query field"})
            _persist_state(
                source_path=args.input,
                output_path=args.output,
                root_payload=root_payload,
                queries=queries,
                failures=failures,
                collection_name=args.collection,
                api_url=args.api_url,
                gt_model=args.gt_model,
                attempted=len(targets),
                success=success,
                failed=failed,
                update_source=args.update_source,
            )
            continue

        try:
            target_papers = _resolve_target_papers(item)
        except Exception as exc:
            failed += 1
            failures.append({"query": query, "error": str(exc)})
            print(f"  Failed: {exc}", file=sys.stderr)
            _persist_state(
                source_path=args.input,
                output_path=args.output,
                root_payload=root_payload,
                queries=queries,
                failures=failures,
                collection_name=args.collection,
                api_url=args.api_url,
                gt_model=args.gt_model,
                attempted=len(targets),
                success=success,
                failed=failed,
                update_source=args.update_source,
            )
            continue

        if args.min_interval > 0 and last_attempt_at is not None:
            elapsed = time.time() - last_attempt_at
            if elapsed < args.min_interval:
                time.sleep(args.min_interval - elapsed)

        try:
            if target_papers:
                by_paper = item.setdefault("ground_truth_by_paper", {})
                for paper in target_papers:
                    existing = str(by_paper.get(paper, "")).strip()
                    if existing and not args.force:
                        continue

                    if use_openai:
                        contexts = _search_contexts(
                            args.api_url,
                            args.collection,
                            query,
                            args.token,
                            args.timeout,
                            paper,
                            args.search_top_k,
                        )
                        answer = _query_openai_gt(
                            args.openai_api_key, args.gt_model, query, contexts
                        )
                        print(f"  [{paper}] GPT GT: {answer[:80]}...")
                    else:
                        answer = _query_api(
                            args.api_url,
                            args.collection,
                            query,
                            args.timeout,
                            args.token,
                            args.max_retries,
                            args.retry_backoff,
                            doc_id_filter=paper,
                        )

                    by_paper[paper] = answer
                    last_attempt_at = time.time()
                    if args.min_interval > 0:
                        time.sleep(args.min_interval)

                if (
                    args.force or not str(item.get("ground_truth", "")).strip()
                ) and by_paper:
                    first_paper = target_papers[0]
                    item["ground_truth"] = str(by_paper.get(first_paper, "")).strip()
            else:
                if use_openai:
                    contexts = _search_contexts(
                        args.api_url,
                        args.collection,
                        query,
                        args.token,
                        args.timeout,
                        None,
                        args.search_top_k,
                    )
                    answer = _query_openai_gt(
                        args.openai_api_key, args.gt_model, query, contexts
                    )
                else:
                    answer = _query_api(
                        args.api_url,
                        args.collection,
                        query,
                        args.timeout,
                        args.token,
                        args.max_retries,
                        args.retry_backoff,
                    )
                last_attempt_at = time.time()
                item["ground_truth"] = answer

            success += 1
            _persist_state(
                source_path=args.input,
                output_path=args.output,
                root_payload=root_payload,
                queries=queries,
                failures=failures,
                collection_name=args.collection,
                api_url=args.api_url,
                gt_model=args.gt_model,
                attempted=len(targets),
                success=success,
                failed=failed,
                update_source=args.update_source,
            )
        except Exception as exc:
            last_attempt_at = time.time()
            failed += 1
            failures.append({"query": query, "error": str(exc)})
            print(f"  Failed: {exc}", file=sys.stderr)
            _persist_state(
                source_path=args.input,
                output_path=args.output,
                root_payload=root_payload,
                queries=queries,
                failures=failures,
                collection_name=args.collection,
                api_url=args.api_url,
                gt_model=args.gt_model,
                attempted=len(targets),
                success=success,
                failed=failed,
                update_source=args.update_source,
            )

    print(f"Completed. Success: {success}, Failed: {failed}", flush=True)
    print(f"Saved GT results to {args.output}", flush=True)
    if args.update_source:
        print(f"Updated source file: {args.input}", flush=True)
    if success == 0 and len(targets) > 0:
        # Nothing at all was generated — downstream evaluation cannot proceed.
        print(
            "ERROR: 0 ground-truth answers were generated. "
            "Check API connectivity and model availability.",
            file=sys.stderr,
        )
        return 1
    if failed > 0:
        print(
            f"WARNING: {failed}/{len(targets)} queries could not be completed. "
            "Their ground_truth fields remain empty; context_recall will be skipped "
            "for those queries. All other metrics will be evaluated normally.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
