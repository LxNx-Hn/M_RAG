from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload PDFs from backend/data to the local M-RAG API for indexing."
    )
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--paper", help="Specific PDF filename in data/ to upload.")
    parser.add_argument("--collection", default="papers")
    parser.add_argument("--doc-type", default="paper")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--max-retries",
        type=int,
        default=8,
        help="Maximum retries for transient API/network errors.",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=12.5,
        help="Base backoff seconds for retries.",
    )
    parser.add_argument(
        "--min-interval",
        type=float,
        default=12.5,
        help="Minimum delay in seconds between upload attempts.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("MRAG_API_TOKEN", ""),
        help="Bearer token for authenticated APIs. Can also be set via MRAG_API_TOKEN.",
    )
    return parser.parse_args()


def _build_headers(token: str) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _collect_pdfs(target_name: str | None) -> list[Path]:
    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    if target_name:
        pdfs = [path for path in pdfs if path.name == target_name]
    return pdfs


def _upload_pdf(
    api_url: str,
    pdf_path: Path,
    collection_name: str,
    doc_type: str,
    timeout: int,
    token: str,
    max_retries: int,
    retry_backoff: float,
) -> tuple[bool, str]:
    attempts = max(0, max_retries) + 1
    for attempt in range(attempts):
        try:
            with pdf_path.open("rb") as file:
                response = requests.post(
                    f"{api_url.rstrip('/')}/api/papers/upload",
                    params={"collection_name": collection_name, "doc_type": doc_type},
                    files={"file": (pdf_path.name, file, "application/pdf")},
                    headers=_build_headers(token),
                    timeout=timeout,
                )
        except requests.RequestException as exc:
            if attempt < attempts - 1:
                sleep_seconds = retry_backoff * (attempt + 1)
                print(
                    f"  Retryable network error: {exc} (sleep {sleep_seconds:.1f}s)",
                    file=sys.stderr,
                )
                time.sleep(sleep_seconds)
                continue
            raise

        if response.status_code == 429 and attempt < attempts - 1:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    sleep_seconds = max(float(retry_after), retry_backoff)
                except ValueError:
                    sleep_seconds = retry_backoff * (attempt + 1)
            else:
                sleep_seconds = retry_backoff * (attempt + 1)
            print(
                f"  429 received for {pdf_path.name}. Retrying in {sleep_seconds:.1f}s",
                file=sys.stderr,
            )
            time.sleep(sleep_seconds)
            continue

        response.raise_for_status()
        data = response.json()
        paper = data.get("paper", {}) if isinstance(data, dict) else {}
        num_chunks = int(paper.get("num_chunks", 0) or 0)
        sections = paper.get("sections", {})
        message = f"{pdf_path.name}: num_chunks={num_chunks}, sections={sections}"
        if num_chunks < 10:
            message += " [warning: num_chunks < 10]"
        return True, message

    raise RuntimeError(f"Exceeded retry budget while uploading {pdf_path.name}.")


def _list_indexed(api_url: str, timeout: int, token: str) -> list[dict]:
    response = requests.get(
        f"{api_url.rstrip('/')}/api/papers/list",
        headers=_build_headers(token),
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("collections", []) if isinstance(data, dict) else []


def main() -> int:
    args = parse_args()
    pdfs = _collect_pdfs(args.paper)
    if args.paper and not pdfs:
        print(f"Target PDF not found in data/: {args.paper}", file=sys.stderr)
        return 1
    if not pdfs:
        print(f"No PDF files found in {DATA_DIR}", file=sys.stderr)
        return 1

    if not args.token:
        print(
            "Warning: no token provided. Authenticated endpoints may fail with 401.",
            file=sys.stderr,
        )

    success = 0
    failed = 0
    last_attempt_at: float | None = None
    for pdf_path in pdfs:
        print(f"Uploading {pdf_path.name} ...")
        if args.min_interval > 0 and last_attempt_at is not None:
            elapsed = time.time() - last_attempt_at
            if elapsed < args.min_interval:
                time.sleep(args.min_interval - elapsed)
        try:
            _, message = _upload_pdf(
                args.api_url,
                pdf_path,
                args.collection,
                args.doc_type,
                args.timeout,
                args.token,
                args.max_retries,
                args.retry_backoff,
            )
            last_attempt_at = time.time()
            print(f"  Success: {message}")
            success += 1
        except Exception as exc:
            last_attempt_at = time.time()
            failed += 1
            print(f"  Failed: {pdf_path.name}: {exc}", file=sys.stderr)

    try:
        indexed = _list_indexed(args.api_url, args.timeout, args.token)
        print("Indexed paper list:")
        for item in indexed:
            print(f"  - {item.get('name', '')}: {item.get('count', 0)} chunks")
    except Exception as exc:
        print(f"Failed to list indexed papers: {exc}", file=sys.stderr)
        failed += 1

    print(f"Completed. Success: {success}, Failed: {failed}")
    return 0 if success > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
