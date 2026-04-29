#!/usr/bin/env python3
"""Generate paper-specific evaluation queries with an OpenAI model."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "evaluation" / "data" / "track1_queries.json"

TRACK1_TYPES = [
    "simple_qa",
    "simple_qa",
    "section_method",
    "section_result",
    "section_abstract",
    "cad_hallucination",
    "citation",
    "crosslingual_en",
]
TRACK2_TYPES = [
    "cad_ablation",
    "cad_ablation",
    "section_method",
    "section_method",
    "section_abstract",
    "section_abstract",
    "citation",
]

EXPECTED_ROUTE = {
    "simple_qa": "A",
    "section_method": "B",
    "section_result": "B",
    "section_abstract": "B",
    "cad_hallucination": "B",
    "cad_ablation": "B",
    "citation": "D",
    "crosslingual_en": "A",
}

SECTION_QUERIES = [
    ("abstract", "main contribution abstract overview"),
    ("method", "method architecture algorithm training objective"),
    ("result", "results metrics ablation performance numbers"),
    ("references", "related work cited papers baseline references"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate M-RAG evaluation queries from indexed paper chunks."
    )
    parser.add_argument("--papers", nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--collection", default="papers")
    parser.add_argument(
        "--token",
        default=os.environ.get("MRAG_API_TOKEN", ""),
        help="Bearer token for the local M-RAG API.",
    )
    parser.add_argument(
        "--openai-model",
        default="gpt-4o",
        help="OpenAI model used for query generation.",
    )
    parser.add_argument(
        "--openai-api-key",
        default=os.environ.get("OPENAI_API_KEY", ""),
        help="OpenAI API key. Prefer OPENAI_API_KEY.",
    )
    parser.add_argument(
        "--queries-per-paper",
        type=int,
        default=8,
        help="Track 1 expects 8. Track 2 expects 7.",
    )
    parser.add_argument(
        "--track",
        choices=["track1", "track2"],
        default="track1",
        help="Query schema to generate.",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output when it already exists.",
    )
    return parser.parse_args()


def _build_headers(token: str) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _search_chunks(
    api_url: str,
    token: str,
    collection: str,
    paper: str,
    section_filter: str | None,
    query: str,
    top_k: int,
    timeout: int,
) -> list[str]:
    payload: dict[str, Any] = {
        "query": query,
        "collection_name": collection,
        "doc_id_filter": paper,
        "top_k": min(top_k, 50),
    }
    if section_filter:
        payload["section_filter"] = section_filter

    response = requests.post(
        f"{api_url.rstrip('/')}/api/chat/search",
        json=payload,
        headers=_build_headers(token),
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return [
        str(item.get("content", ""))
        for item in data.get("results", [])
        if item.get("content")
    ]


def collect_paper_context(args: argparse.Namespace, paper: str) -> str:
    excerpts: list[str] = []
    for section, query in SECTION_QUERIES:
        try:
            chunks = _search_chunks(
                args.api_url,
                args.token,
                args.collection,
                paper,
                section,
                query,
                args.top_k,
                args.timeout,
            )
        except Exception as exc:
            print(
                f"[warn] {paper}/{section} sampling failed: {exc}",
                file=sys.stderr,
            )
            chunks = []
        for index, chunk in enumerate(chunks[: args.top_k], start=1):
            excerpts.append(f"[{paper} | {section} | {index}]\n{chunk[:900]}")

    if not excerpts:
        chunks = _search_chunks(
            args.api_url,
            args.token,
            args.collection,
            paper,
            None,
            f"{paper} main contribution method result citation",
            args.top_k,
            args.timeout,
        )
        excerpts.extend(
            f"[{paper} | general | {i}]\n{chunk[:900]}"
            for i, chunk in enumerate(chunks, start=1)
        )

    return "\n\n".join(excerpts)


def _prompt_for_track(track: str, paper: str, context: str) -> str:
    if track == "track1":
        types = ", ".join(TRACK1_TYPES)
        return (
            "당신은 학술 RAG 평가 데이터셋 전문가입니다.\n"
            f"아래 논문 내용만 근거로 doc_id '{paper}'에 대한 평가 쿼리를 "
            "생성하세요.\n"
            "- 쿼리는 모두 자연스러운 한국어로 작성하세요.\n"
            "- crosslingual_en 타입만 자연스러운 영어 질문으로 작성하세요.\n"
            "- 논문명, 모델명, 데이터셋명 같은 고유명사는 영어 그대로 쓰세요.\n"
            "- 논문에서 실제로 답할 수 있는 구체적 내용만 질문하세요.\n"
            f"- 타입 순서는 반드시 다음과 같아야 합니다: {types}\n"
            f"- applicable_papers는 반드시 ['{paper}']만 사용하세요.\n\n"
            "[논문 내용]\n"
            f"{context[:12000]}\n\n"
            '[출력 형식 - JSON only]\n{"queries": ['
            '{"query": "...", "type": "simple_qa", '
            f'"applicable_papers": ["{paper}"]}}]}}'
        )

    types = ", ".join(TRACK2_TYPES)
    return (
        "당신은 논문 도메인 RAG 평가 쿼리 작성자입니다.\n"
        f"아래 논문 내용만 근거로 doc_id '{paper}'에 대한 Track 2 평가 "
        "쿼리를 생성하세요.\n"
        "- 모든 쿼리는 자연스러운 한국어로 작성하세요.\n"
        "- 논문에서 실제로 답할 수 있는 내용만 질문하세요.\n"
        "- cad_ablation은 수치, 파라미터, 실험 세부값을 묻는 질문입니다.\n"
        f"- 타입 순서는 반드시 다음과 같아야 합니다: {types}\n"
        f"- applicable_papers는 반드시 ['{paper}']만 사용하세요.\n\n"
        "[논문 내용]\n"
        f"{context[:12000]}\n\n"
        '[출력 형식 - JSON only]\n{"queries": ['
        '{"query": "...", "type": "cad_ablation", '
        f'"applicable_papers": ["{paper}"]}}]}}'
    )


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def generate_for_paper(
    args: argparse.Namespace, paper: str, context: str
) -> list[dict]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai package is required for generate_queries.py"
        ) from exc
    if not args.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY or --openai-api-key is required.")

    client = OpenAI(api_key=args.openai_api_key)
    response = client.chat.completions.create(
        model=args.openai_model,
        messages=[
            {"role": "user", "content": _prompt_for_track(args.track, paper, context)}
        ],
        temperature=0.2,
        max_tokens=1800,
    )
    content = response.choices[0].message.content or ""
    payload = _extract_json(content)
    queries = payload.get("queries")
    if not isinstance(queries, list):
        raise ValueError("OpenAI response did not contain a queries list.")
    return queries


def normalise_queries(track: str, paper: str, queries: list[dict]) -> list[dict]:
    expected = TRACK1_TYPES if track == "track1" else TRACK2_TYPES
    if len(queries) != len(expected):
        raise ValueError(
            f"{paper}: expected {len(expected)} queries, got {len(queries)}."
        )

    normalised: list[dict] = []
    for item, expected_type in zip(queries, expected):
        query = str(item.get("query", "")).strip()
        if not query:
            raise ValueError(f"{paper}: empty query for type {expected_type}.")
        query_type = str(item.get("type", "")).strip()
        if query_type != expected_type:
            raise ValueError(
                f"{paper}: expected type {expected_type}, got {query_type}."
            )
        normalised.append(
            {
                "query": query,
                "ground_truth": "",
                "type": query_type,
                "expected_route": EXPECTED_ROUTE.get(query_type, "A"),
                "applicable_papers": [paper],
                "track": track,
            }
        )

    counts = Counter(item["type"] for item in normalised)
    expected_counts = Counter(expected)
    if counts != expected_counts:
        raise ValueError(
            f"{paper}: type counts mismatch {counts} != {expected_counts}."
        )
    return normalised


def main() -> int:
    args = parse_args()
    expected_count = 8 if args.track == "track1" else 7
    if args.queries_per_paper != expected_count:
        raise SystemExit(f"{args.track} requires --queries-per-paper {expected_count}.")

    output = args.output
    if not output.is_absolute():
        output = (Path.cwd() / output).resolve()
    if output.exists() and not args.overwrite and not args.dry_run:
        raise SystemExit(f"Output already exists. Use --overwrite: {output}")

    all_queries: list[dict] = []
    for paper in args.papers:
        print(f"[sample] {paper}")
        context = collect_paper_context(args, paper)
        if args.dry_run:
            print(f"  sampled_chars={len(context)}")
            continue
        generated = generate_for_paper(args, paper, context)
        all_queries.extend(normalise_queries(args.track, paper, generated))
        print(f"  generated={len(generated)}")

    if args.dry_run:
        print("[dry-run] no query file was written.")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(all_queries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(all_queries)} queries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
