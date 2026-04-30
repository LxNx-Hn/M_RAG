#!/usr/bin/env python3
"""Generate evaluation queries from indexed paper chunks with an OpenAI model."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
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
    ("abstract", "초록 abstract 핵심 기여 contribution problem setting"),
    ("method", "방법 method architecture algorithm training objective 구현"),
    ("result", "결과 result metric 성능 수치 비교 ablation"),
    ("related_work", "관련 연구 related work baseline comparison prior work"),
]
CITATION_SECTION_QUERIES = [
    ("related_work", "인용 cited work baseline author comparison related work"),
    ("references", "참고문헌 cited work author title baseline reference"),
]

BAD_QUERY_PATTERNS = [
    "\uc5b4\ub5a4\\s+\uc139\uc158",
    "\uc5b4\ub290\\s+\uc139\uc158",
    "\uc5b4\ub514\uc5d0\\s+\uc788",
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
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc5b8\uae09\ub41c\\s+\ud2b9\uc815",
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc0ac\uc6a9\ub41c\\s+\uc8fc\uc694",
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc81c\uc548\ub41c\\s+\ubc29\ubc95\\s+\uc911\\s+\ud558\ub098",
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc81c\uc2dc\ub41c\\s+\ud2b9\uc815\\s+\uacb0\uacfc\\s+\uac12",
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc8fc\uc7a5\ud558\ub294\\s+\ud2b9\uc815\\s+\uc0ac\uc2e4",
    "^\uc774\\s+\ub17c\ubb38\uc5d0\uc11c\\s+\uc778\uc6a9\ub41c\\s+\ud2b9\uc815\\s+\uc5f0\uad6c",
    "^what\\s+are\\s+the\\s+key\\s+contributions\\s+of\\s+the\\s+model",
    "^what\\s+is\\s+one\\s+specific\\s+method\\s+mentioned\\s+in\\s+the\\s+paper",
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
        help="Number of queries to generate per paper (Track 1 expects 8).",
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
        "--append",
        action="store_true",
        help="Append generated queries to an existing output file.",
    )
    parser.add_argument(
        "--max-generation-attempts",
        type=int,
        default=6,
        help="Retry query generation when validation rejects the output.",
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
    doc_id_filter: str | None,
    section_filter: str | None,
    query: str,
    top_k: int,
    timeout: int,
) -> list[str]:
    payload: dict[str, Any] = {
        "query": query,
        "collection_name": collection,
        "top_k": min(top_k, 50),
    }
    if doc_id_filter:
        payload["doc_id_filter"] = doc_id_filter
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
    doc_id_filter: str | None,
    section_queries: list[tuple[str, str]],
    label: str,
    paper_label: str,
) -> list[str]:
    excerpts: list[str] = []
    seen: set[str] = set()
    for section, query in section_queries:
        try:
            chunks = _search_chunks(
                args.api_url,
                args.token,
                args.collection,
                doc_id_filter,
                section,
                query,
                args.top_k,
                args.timeout,
            )
        except Exception as exc:
            print(
                f"[warn] {paper_label}/{section} sampling failed: {exc}",
                file=sys.stderr,
            )
            chunks = []

        for index, chunk in enumerate(chunks[: args.top_k], start=1):
            preview = chunk[:900]
            if preview in seen:
                continue
            seen.add(preview)
            excerpts.append(
                f"[{label} | {paper_label} | {section} | {index}]\n{preview}"
            )
    return excerpts


def collect_paper_context(args: argparse.Namespace, paper: str) -> str:
    main_excerpts = _sample_excerpts(
        args,
        paper,
        MAIN_SECTION_QUERIES,
        "main",
        paper,
    )
    citation_excerpts = _sample_excerpts(
        args,
        paper,
        CITATION_SECTION_QUERIES,
        "citation-only",
        paper,
    )

    if not main_excerpts:
        chunks = _search_chunks(
            args.api_url,
            args.token,
            args.collection,
            paper,
            None,
            f"{paper} 핵심 기여 main contribution method result 결과",
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
                f"{paper} 인용 cited work author baseline reference 참고문헌",
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


def _track1_schema_json(paper: str) -> str:
    return json.dumps(
        {
            "queries": [
                {
                    "query": "...",
                    "type": "simple_qa",
                    "applicable_papers": [paper],
                    "answer_span": "...",
                }
            ]
        },
        ensure_ascii=False,
    )


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00ad", "")
    text = re.sub(r"-\s*\n\s*", "", text)
    return " ".join(text.lower().split())


def _context_contains_answer_span(context: str, answer_span: str) -> bool:
    return _normalize_text(answer_span) in _normalize_text(context)


def _track1_prompt(
    paper: str,
    context: str,
    feedback: str | None = None,
) -> str:
    feedback_block = ""
    if feedback:
        feedback_block = (
            "\n이전 시도가 다음 이유로 거절되었습니다.\n"
            f"{feedback}\n"
            "거절된 규칙을 반영해서 8개 전체를 다시 생성하세요.\n"
        )

    types = ", ".join(TRACK1_TYPES)
    return (
        "당신은 학술 RAG 평가 데이터셋을 만드는 전문가입니다.\n"
        f"아래 발췌문은 doc_id '{paper}'의 내용만 포함합니다.\n"
        "아래 순서대로 정확히 8개의 쿼리를 생성하세요.\n"
        f"{types}\n\n"
        "규칙:\n"
        "- 모든 쿼리는 자연스러운 한국어로 작성하세요. 단 crosslingual_en만 자연스러운 영어입니다.\n"
        "- 각 쿼리는 발췌문에 명시된 구체적 사실, 수치, 지표, 데이터셋, 모델명, 방법명, 인용문헌 중 하나 이상에 직접 근거해야 합니다.\n"
        "- '이 논문에서 언급된 특정 ...' 같은 generic 표현은 금지합니다.\n"
        "- 어떤 섹션에 있는지, 초록이 일반적으로 무엇을 말하는지, 참고문헌이 어디 있는지 묻는 메타 질문은 금지합니다.\n"
        "- Main excerpts에 없는 용어를 이 논문의 고유 사실처럼 만들어서 쓰지 마세요.\n"
        "- citation 타입만 Citation-only excerpts를 사용하고, 나머지 타입은 모두 Main excerpts만 근거로 삼으세요.\n"
        "- section_method는 방법 섹션의 구현/알고리즘/설계 선택을 묻고, section_result는 결과 섹션의 수치/비교 결과를, section_abstract는 초록에 명시된 핵심 주장 하나를 묻습니다.\n"
        "- citation은 실제로 인용된 선행 연구, 데이터셋 출처, baseline 중 하나를 구체적으로 물어야 합니다.\n"
        "- 각 항목은 answer_span 필드를 반드시 포함하세요. answer_span은 발췌문에 그대로 존재하는 5~200자 길이의 문구여야 합니다.\n"
        "- answer_span이 발췌문에 없는 표현이면 안 됩니다.\n"
        f"- applicable_papers는 정확히 ['{paper}'] 이어야 합니다.\n"
        f"{feedback_block}\n"
        "[발췌문]\n"
        f"{context[:14000]}\n\n"
        "[출력 형식 - JSON only]\n"
        f"{_track1_schema_json(paper)}"
    )


def _extract_json(text: str) -> dict[str, Any] | list[dict[str, Any]]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", cleaned, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _call_openai(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
) -> list[dict[str, Any]]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai package is required for generate_queries.py"
        ) from exc
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY or --openai-api-key is required.")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=max_tokens,
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


def _assert_query_quality(
    label: str,
    query_type: str,
    query: str,
    *,
    require_korean: bool = True,
    reject_generic: bool = True,
    bad_patterns: list[str] | None = None,
) -> None:
    query_lower = query.lower()
    patterns = bad_patterns or BAD_QUERY_PATTERNS
    for pattern in patterns:
        if re.search(pattern, query_lower, flags=re.IGNORECASE):
            raise ValueError(f"{label}/{query_type}: rejected meta query: {query!r}")
    if reject_generic:
        for pattern in GENERIC_QUERY_PATTERNS:
            if re.search(pattern, query_lower, flags=re.IGNORECASE):
                raise ValueError(
                    f"{label}/{query_type}: rejected generic query: {query!r}"
                )

    has_korean = bool(KOREAN_RE.search(query))
    if query_type == "crosslingual_en":
        if has_korean:
            raise ValueError(f"{label}/{query_type}: expected English query.")
        return
    if require_korean and not has_korean:
        raise ValueError(f"{label}/{query_type}: expected Korean query.")


def _validate_track1_queries(
    paper: str,
    queries: list[dict[str, Any]],
    context: str,
) -> list[dict[str, Any]]:
    if len(queries) != len(TRACK1_TYPES):
        raise ValueError(f"{paper}: expected {len(TRACK1_TYPES)} queries.")

    normalised: list[dict[str, Any]] = []
    for item, expected_type in zip(queries, TRACK1_TYPES):
        query = str(item.get("query", "")).strip()
        if not query:
            raise ValueError(f"{paper}: empty query for type {expected_type}.")
        query_type = str(item.get("type", "")).strip()
        if query_type != expected_type:
            raise ValueError(
                f"{paper}: expected type {expected_type}, got {query_type}."
            )
        answer_span = str(item.get("answer_span", "")).strip()
        if not answer_span:
            raise ValueError(f"{paper}/{query_type}: missing answer_span.")
        if len(answer_span) < 5 or len(answer_span) > 200:
            raise ValueError(f"{paper}/{query_type}: invalid answer_span length.")
        if not _context_contains_answer_span(context, answer_span):
            raise ValueError(
                f"{paper}/{query_type}: answer_span not grounded in excerpts."
            )
        _assert_query_quality(paper, query_type, query)
        normalised.append(
            {
                "query": query,
                "ground_truth": "",
                "type": query_type,
                "expected_route": EXPECTED_ROUTE.get(query_type, "A"),
                "applicable_papers": [paper],
                "track": "track1",
            }
        )

    counts = Counter(item["type"] for item in normalised)
    if counts != Counter(TRACK1_TYPES):
        raise ValueError(f"{paper}: type counts mismatch {counts}.")
    return normalised


def _generate_track1_queries(
    args: argparse.Namespace,
    paper: str,
    context: str,
) -> list[dict[str, Any]]:
    feedback: str | None = None
    attempts = max(args.max_generation_attempts, 1)
    for attempt in range(1, attempts + 1):
        generated = _call_openai(
            api_key=args.openai_api_key,
            model=args.openai_model,
            prompt=_track1_prompt(paper, context, feedback=feedback),
            max_tokens=1800,
        )
        try:
            return _validate_track1_queries(paper, generated, context)
        except ValueError as exc:
            feedback = str(exc)
            if attempt >= attempts:
                raise
            print(f"  retry={attempt} reason={feedback}", file=sys.stderr)
    raise RuntimeError(f"{paper}: query generation retry loop exhausted.")


def _load_existing_queries(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    raise ValueError(f"Expected a top-level JSON list in {path}.")


def main() -> int:
    args = parse_args()
    expected_count = len(TRACK1_TYPES)
    if args.queries_per_paper != expected_count:
        raise SystemExit(f"track1 requires --queries-per-paper {expected_count}.")

    output = (
        args.output
        if args.output.is_absolute()
        else (Path.cwd() / args.output).resolve()
    )
    if output.exists() and not args.overwrite and not args.append and not args.dry_run:
        raise SystemExit(
            f"Output already exists. Use --overwrite or --append: {output}"
        )

    if len(args.papers) == 0:
        raise SystemExit("Requires at least one paper.")

    all_queries: list[dict[str, Any]] = []
    for paper in args.papers:
        print(f"[sample] {paper}")
        context = collect_paper_context(args, paper)
        if args.dry_run:
            print(f"  sampled_chars={len(context)}")
            continue
        generated = _generate_track1_queries(args, paper, context)
        all_queries.extend(generated)
        print(f"  generated={len(generated)}")

    if args.dry_run:
        print("[dry-run] no query file was written.")
        return 0

    if not args.openai_api_key:
        raise SystemExit("OPENAI_API_KEY or --openai-api-key is required.")

    output.parent.mkdir(parents=True, exist_ok=True)
    final_queries = all_queries
    if args.append and output.exists():
        existing = _load_existing_queries(output)
        final_queries = existing + all_queries

    output.write_text(
        json.dumps(final_queries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(final_queries)} queries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
