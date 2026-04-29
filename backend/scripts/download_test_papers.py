#!/usr/bin/env python3
"""Download the paper PDFs used by the M-RAG Alice experiment."""

from __future__ import annotations

import argparse
import time
import urllib.request
from pathlib import Path

PAPERS = [
    {
        "id": "paper_nlp_bge",
        "arxiv_id": "2402.03216",
        "title": "BGE M3-Embedding (Chen et al., ACL 2024)",
        "desc": "Embedding model reference for the retrieval stack.",
    },
    {
        "id": "paper_nlp_rag",
        "arxiv_id": "2312.10997",
        "title": "Retrieval-Augmented Generation for Large Language Models",
        "desc": "RAG survey reference for the system baseline.",
    },
    {
        "id": "paper_nlp_cad",
        "arxiv_id": "2305.14739",
        "title": "Trusting Your Evidence: Hallucinate Less with CAD",
        "desc": "Context-aware decoding reference.",
    },
    {
        "id": "paper_nlp_raptor",
        "arxiv_id": "2401.18059",
        "title": "RAPTOR (Sarthi et al., ICLR 2024)",
        "desc": "Hierarchical retrieval and chunking reference.",
    },
]

REPO_INCLUDED_PAPERS = [
    {
        "id": "paper_midm",
        "arxiv_id": None,
        "title": "MIDM-2.0 Technical Report",
        "desc": "Korean LLM model reference (tracked in repo).",
    },
    {
        "id": "paper_ko_rag_eval_framework",
        "arxiv_id": None,
        "title": "Korean RAG Evaluation Framework",
        "desc": "Korean RAG evaluation paper (tracked in repo).",
    },
    {
        "id": "paper_ko_rag_rrf_chunking",
        "arxiv_id": None,
        "title": "Korean RAG with RRF and Chunking",
        "desc": "Korean RAG chunking/fusion paper (tracked in repo).",
    },
    {
        "id": "paper_ko_cad_contrastive",
        "arxiv_id": None,
        "title": "Korean CAD Contrastive Decoding",
        "desc": "Korean CAD contrastive decoding paper (tracked in repo).",
    },
]


def arxiv_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"


def download_paper(arxiv_id: str, dest_path: Path, retries: int = 3) -> bool:
    url = arxiv_pdf_url(arxiv_id)
    for attempt in range(1, retries + 1):
        try:
            print(
                f"  Downloading {url} (attempt {attempt}/{retries}) ...",
                end="",
                flush=True,
            )
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "M-RAG/1.0 (research)"},
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            dest_path.write_bytes(data)
            size_kb = len(data) // 1024
            print(f" done ({size_kb} KB)")
            return True
        except Exception as exc:
            print(f" FAIL ({exc})")
            if attempt < retries:
                time.sleep(5)
    return False


def _manual_message(dest_path: Path) -> str:
    return f"Repo-included asset expected at {dest_path}; restore from git if missing"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download M-RAG experiment PDFs.")
    parser.add_argument(
        "--skip-korean",
        action="store_true",
        help="Skip Korean/MIDM repo-included papers.",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Target directory. Default: backend/data",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print target files without downloading or writing anything.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    backend_dir = Path(__file__).resolve().parents[1]
    data_dir = Path(args.data_dir) if args.data_dir else backend_dir / "data"
    targets = PAPERS if args.skip_korean else PAPERS + REPO_INCLUDED_PAPERS

    print(f"[download_test_papers] target directory: {data_dir}")
    if args.dry_run:
        print("[dry-run] planned targets:")
        for paper in targets:
            dest = data_dir / f"{paper['id']}.pdf"
            arxiv_id = paper.get("arxiv_id")
            source = arxiv_pdf_url(arxiv_id) if arxiv_id else "repo-included"
            print(f"  - {paper['id']}: {source} -> {dest}")
        return 0

    data_dir.mkdir(parents=True, exist_ok=True)
    success: list[str] = []
    failed: list[str] = []
    manual: list[str] = []

    for paper in targets:
        doc_id = paper["id"]
        dest = data_dir / f"{doc_id}.pdf"
        print(f"[{doc_id}] {paper['title']}")
        print(f"  purpose: {paper['desc']}")

        if dest.exists():
            size_kb = dest.stat().st_size // 1024
            print(f"  already exists ({size_kb} KB); skipping")
            success.append(doc_id)
            continue

        arxiv_id = paper.get("arxiv_id")
        if not arxiv_id:
            message = _manual_message(dest)
            print(f"  manual: {message}")
            manual.append(message)
            print()
            continue

        if download_paper(arxiv_id, dest):
            success.append(doc_id)
        else:
            failed.append(doc_id)
            print(f"  manual download needed: {arxiv_pdf_url(arxiv_id)}")
            print(f"  save as: {dest}")

        time.sleep(2)
        print()

    print("=" * 50)
    print(f"success: {len(success)} / {len(targets)}")
    if manual:
        print("manual items:")
        for message in manual:
            print(f"  - {message}")
    if failed:
        print(f"failed: {failed}")

    if failed and len(failed) == len(targets):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
