#!/usr/bin/env python3
"""Generate paper-specific evaluation queries with an OpenAI model.

The source is intentionally ASCII-only. Korean output is requested through
English prompts and validated with Unicode escape based patterns so the script
does not depend on terminal code pages or editor encoding heuristics.
"""

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

MAIN_SECTION_QUERIES = [
    ("abstract", "specific contribution claim problem setting abstract"),
    ("method", "specific method architecture algorithm training objective"),
    ("result", "specific results metrics ablation performance numbers"),
    ("related_work", "specific prior work baseline comparison"),
]
CITATION_SECTION_QUERIES = [
    ("related_work", "specific cited work baseline author comparison"),
    ("references", "specific cited work author title baseline reference"),
]

# Korean phrases are written with Unicode escapes to keep this file ASCII-only.
BAD_QUERY_PATTERNS = [
    "\uc5b4\ub5a4\\s+\uc139\uc158",  # what section
    "\uc5b4\ub290\\s+\uc139\uc158",  # which section
    "\uc5b4\ub514\uc5d0\\s+\uc788",  # where is
    "\ucd08\ub85d(?:\uc5d0\ub294|\uc740)?\\s+\uc5b4\ub5a4\\s+\ub0b4\uc6a9",
    "\ucd08\ub85d(?:\uc5d0\uc11c\ub294|\uc5d0\uc11c)?\\s+\ub2e4\ub8e8",
    "\ubc29\ubc95\ub860\\s+\uc139\uc158",
    "\uacb0\uacfc\\s+\uc139\uc158",
    "\uc774\\s+\ub17c\ubb38\uc758\\s+\ucd08\ub85d",
    "\uc774\\s+\ub17c\ubb38\uc758\\s+\ubc29\ubc95\ub860",
    "\uc774\\s+\ub17c\ubb38\uc758\\s+\uacb0\uacfc",
    "\ucc38\uace0\\s*\ubb38\ud5cc(?:\uc740|\ub294)?\\s+\uc5b4\ub514",
    "what\\s+section",
    "where\\s+(?:is|are).*(?:reference|section)",
    "what\\s+does\\s+the\\s+abstract",
    "what\\s+is\\s+in\\s+the\\s+abstract",
    "methodology\\s+section",
    "results?\\s+section",
]

GENERIC_QUERY_PATTERNS = [
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc81c\uc548\ub41c\\s+\ubaa8\ub378",
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc0ac\uc6a9\ub41c\\s+\ub370\uc774\ud130\uc14b",
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc778\uc6a9\ub41c\\s+\uc8fc\uc694",
    "^what\\s+are\\s+the\\s+key\\s+contributions\\s+of\\s+the\\s+model",
]

KOREAN_RE = re.compile("[\uac00-\ud7a3]")


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
    parser.add_argument(
        "--max-generation-attempts",
        type=int,
        default=3,
        help="Retry query generation when validation rejects generic queries.",
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


def _sample_excerpts(
    args: argparse.Namespace,
    paper: str,
    section_queries: list[tuple[str, str]],
    label: str,
) -> list[str]:
    excerpts: list[str] = []
    seen: set[str] = set()
    for section, query in section_queries:
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
            preview = chunk[:900]
            if preview in seen:
                continue
            seen.add(preview)
            excerpts.append(f"[{label} | {paper} | {section} | {index}]\n{preview}")
    return excerpts


def collect_paper_context(args: argparse.Namespace, paper: str) -> str:
    main_excerpts = _sample_excerpts(
        args,
        paper,
        MAIN_SECTION_QUERIES,
        "main",
    )
    citation_excerpts = _sample_excerpts(
        args,
        paper,
        CITATION_SECTION_QUERIES,
        "citation-only",
    )

    if not main_excerpts:
        chunks = _search_chunks(
            args.api_url,
            args.token,
            args.collection,
            paper,
            None,
            f"{paper} main contribution method result",
            args.top_k,
            args.timeout,
        )
        main_excerpts.extend(
            f"[main | {paper} | general | {i}]\n{chunk[:900]}"
            for i, chunk in enumerate(chunks, start=1)
        )

    if not citation_excerpts:
        try:
            chunks = _search_chunks(
                args.api_url,
                args.token,
                args.collection,
                paper,
                None,
                f"{paper} cited work author baseline reference",
                args.top_k,
                args.timeout,
            )
        except Exception:
            chunks = []
        citation_excerpts.extend(
            f"[citation-only | {paper} | general | {i}]\n{chunk[:900]}"
            for i, chunk in enumerate(chunks, start=1)
        )

    parts = [
        "[Main excerpts: use for all non-citation query types]",
        "\n\n".join(main_excerpts),
    ]
    if citation_excerpts:
        parts.extend(
            [
                "[Citation-only excerpts: use only for citation query types]",
                "\n\n".join(citation_excerpts),
            ]
        )
    return "\n\n".join(part for part in parts if part)


def _schema_json(first_type: str, paper: str) -> str:
    return json.dumps(
        {
            "queries": [
                {
                    "query": "...",
                    "type": first_type,
                    "applicable_papers": [paper],
                }
            ]
        },
        ensure_ascii=False,
    )


def _prompt_for_track(
    track: str,
    paper: str,
    context: str,
    feedback: str | None = None,
) -> str:
    feedback_block = ""
    if feedback:
        feedback_block = (
            "\nPrevious attempt was rejected for this reason:\n"
            f"{feedback}\n"
            "Regenerate all queries and avoid the rejected pattern.\n"
        )

    if track == "track1":
        types = ", ".join(TRACK1_TYPES)
        return (
            "You are building a high-precision academic RAG evaluation set.\n"
            f"Use only the excerpts below for doc_id '{paper}'.\n"
            "Generate exactly eight queries in this order:\n"
            f"{types}\n\n"
            "Rules:\n"
            "- All queries must be natural Korean, except crosslingual_en, "
            "which must be natural English.\n"
            "- Each query must ask about a concrete fact, method, dataset, "
            "metric, number, or cited work explicitly present in the excerpts.\n"
            "- Do not ask meta questions such as which section contains "
            "something, what the abstract says in general, or where a "
            "reference is located.\n"
            "- Do not invent terms from nearby references unless the main "
            f"excerpts clearly state that they are central to '{paper}'.\n"
            "- Only the citation query may use Citation-only excerpts. All "
            "other query types must be grounded in Main excerpts.\n"
            "- For section_method, ask about one named method or implementation "
            "detail from the method/main excerpts.\n"
            "- For section_result, ask about one specific result, metric, "
            "comparison, or numeric value from the result/main excerpts.\n"
            "- For section_abstract, ask about one specific claim from the "
            "abstract/main excerpts, not a summary of the abstract itself.\n"
            "- For citation, ask about a specific cited prior work, author, or "
            "baseline that appears in Citation-only or Main excerpts.\n"
            f"- applicable_papers must be exactly ['{paper}'].\n"
            f"{feedback_block}\n"
            "[Paper excerpts]\n"
            f"{context[:14000]}\n\n"
            "[Output format - JSON only]\n"
            f"{_schema_json('simple_qa', paper)}"
        )

    types = ", ".join(TRACK2_TYPES)
    return (
        "You are building high-precision Track 2 RAG evaluation queries.\n"
        f"Use only the excerpts below for doc_id '{paper}'.\n"
        "Generate exactly seven Korean queries in this order:\n"
        f"{types}\n\n"
        "Rules:\n"
        "- Every query must be answerable from the excerpts.\n"
        "- cad_ablation queries must ask about a concrete number, parameter, "
        "experimental setting, or result stated in the main excerpts.\n"
        "- section_method and section_abstract queries must ask about a "
        "specific named detail, not the section as a document structure.\n"
        "- Only the citation query may use Citation-only excerpts. All other "
        "query types must be grounded in Main excerpts.\n"
        "- citation queries must mention a concrete cited work, baseline, or "
        "author name found in the excerpts.\n"
        "- Do not ask generic questions beginning with 'this paper'.\n"
        "- Do not ask where a section or reference is located.\n"
        f"- applicable_papers must be exactly ['{paper}'].\n"
        f"{feedback_block}\n"
        "[Paper excerpts]\n"
        f"{context[:14000]}\n\n"
        "[Output format - JSON only]\n"
        f"{_schema_json('cad_ablation', paper)}"
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
    args: argparse.Namespace,
    paper: str,
    context: str,
    feedback: str | None = None,
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
            {
                "role": "user",
                "content": _prompt_for_track(
                    args.track,
                    paper,
                    context,
                    feedback=feedback,
                ),
            }
        ],
        temperature=0.1,
        max_tokens=1800,
    )
    content = response.choices[0].message.content or ""
    payload = _extract_json(content)
    if isinstance(payload, list):
        queries = payload
    elif isinstance(payload, dict):
        queries = payload.get("queries")
    else:
        raise ValueError(
            "OpenAI response must be a JSON object with 'queries' or a list."
        )
    if not isinstance(queries, list):
        raise ValueError("OpenAI response did not contain a queries list.")
    return queries


def _assert_query_quality(paper: str, query_type: str, query: str) -> None:
    query_lower = query.lower()
    for pattern in BAD_QUERY_PATTERNS:
        if re.search(pattern, query_lower, flags=re.IGNORECASE):
            raise ValueError(f"{paper}/{query_type}: rejected meta query: {query!r}")
    for pattern in GENERIC_QUERY_PATTERNS:
        if re.search(pattern, query_lower, flags=re.IGNORECASE):
            raise ValueError(f"{paper}/{query_type}: rejected generic query: {query!r}")
    has_korean = bool(KOREAN_RE.search(query))
    if query_type == "crosslingual_en":
        if has_korean:
            raise ValueError(f"{paper}/{query_type}: expected English query.")
    elif not has_korean:
        raise ValueError(f"{paper}/{query_type}: expected Korean query.")


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
        _assert_query_quality(paper, query_type, query)
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


def generate_validated_queries(
    args: argparse.Namespace,
    paper: str,
    context: str,
) -> list[dict]:
    feedback: str | None = None
    attempts = max(args.max_generation_attempts, 1)
    for attempt in range(1, attempts + 1):
        generated = generate_for_paper(args, paper, context, feedback=feedback)
        try:
            return normalise_queries(args.track, paper, generated)
        except ValueError as exc:
            feedback = str(exc)
            if attempt >= attempts:
                raise
            print(f"  retry={attempt} reason={feedback}", file=sys.stderr)
    raise RuntimeError(f"{paper}: query generation retry loop exhausted.")


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
        normalised = generate_validated_queries(args, paper, context)
        all_queries.extend(normalised)
        print(f"  generated={len(normalised)}")

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
