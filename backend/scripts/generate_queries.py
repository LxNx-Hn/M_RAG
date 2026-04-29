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

MAIN_SECTION_QUERIES = [
    ("abstract", "초록 abstract 핵심 기여 contribution problem setting"),
    ("method", "방법 method architecture 알고리즘 training objective 구현"),
    ("result", "결과 result metric 실험 성능 수치 비교 ablation"),
    ("related_work", "관련 연구 related work baseline comparison prior work"),
]
CITATION_SECTION_QUERIES = [
    ("related_work", "인용 cited work baseline author comparison related work"),
    ("references", "참고문헌 cited work author title baseline reference"),
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


def _schema_json(first_type: str, paper: str) -> str:
    return json.dumps(
        {
            "queries": [
                {
                    "query": "...",
                    "type": first_type,
                    "applicable_papers": [paper],
                    "answer_span": "...",
                }
            ]
        },
        ensure_ascii=False,
    )


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _context_contains_answer_span(context: str, answer_span: str) -> bool:
    return _normalize_text(answer_span) in _normalize_text(context)


def _prompt_for_track(
    track: str,
    paper: str,
    context: str,
    feedback: str | None = None,
) -> str:
    feedback_block = ""
    if feedback:
        feedback_block = (
            "\n이전 시도가 다음 이유로 거부되었습니다:\n"
            f"{feedback}\n"
            "거부된 패턴을 피해서 8개/7개 전체를 다시 생성하세요.\n"
        )

    if track == "track1":
        types = ", ".join(TRACK1_TYPES)
        return (
            "당신은 학술 RAG 평가 데이터셋을 만드는 전문가입니다.\n"
            f"아래 발췌문은 doc_id '{paper}'의 내용만 포함합니다.\n"
            "아래 순서대로 정확히 8개의 쿼리를 생성하세요:\n"
            f"{types}\n\n"
            "규칙:\n"
            "- 모든 쿼리는 자연스러운 한국어로 작성하세요. 단, crosslingual_en만 자연스러운 영어로 작성하세요.\n"
            "- 각 쿼리는 발췌문에 명시된 구체적 사실, 수치, 메트릭, 데이터셋, 모델명, 방법명, 저자명 중 하나 이상에 근거해야 합니다.\n"
            "- '이 논문에서 언급된 특정 ...' 같은 포괄적 문장을 쓰지 마세요.\n"
            "- 어느 섹션에 있는지, 초록이 일반적으로 무엇을 말하는지, 참고문헌이 어디 있는지 묻는 메타 질문을 만들지 마세요.\n"
            f"- Main excerpts에 명시되지 않은 용어를 '{paper}'의 핵심 사실처럼 만들지 마세요.\n"
            "- citation 타입만 Citation-only excerpts를 사용할 수 있습니다. 나머지 타입은 모두 Main excerpts만 근거로 삼으세요.\n"
            "- section_method는 방법 섹션에 실제로 등장하는 구현 세부사항, 알고리즘, 설계 선택 중 하나를 물어야 합니다.\n"
            "- section_result는 실제 결과값, 비교 결과, 메트릭, 수치 중 하나를 물어야 합니다.\n"
            "- section_abstract는 초록 전체 요약이 아니라 초록에 명시된 구체적 주장 하나를 물어야 합니다.\n"
            "- citation은 실제로 인용된 선행연구, 저자, baseline 하나를 구체적으로 물어야 합니다.\n"
            "- 각 항목에는 answer_span 필드를 반드시 포함하세요. answer_span은 발췌문에 그대로 등장하는 5~80자 길이의 짧은 답 단서여야 합니다.\n"
            "- answer_span은 질문에 대한 답을 직접 뒷받침해야 하며, 발췌문에 없는 표현을 쓰면 안 됩니다.\n"
            f"- applicable_papers는 정확히 ['{paper}'] 이어야 합니다.\n"
            f"{feedback_block}\n"
            "[발췌문]\n"
            f"{context[:14000]}\n\n"
            "[출력 형식 - JSON only]\n"
            f"{_schema_json('simple_qa', paper)}"
        )

    types = ", ".join(TRACK2_TYPES)
    return (
        "당신은 Track 2 학술 RAG 평가 쿼리를 만드는 전문가입니다.\n"
        f"아래 발췌문은 doc_id '{paper}'의 내용만 포함합니다.\n"
        "아래 순서대로 정확히 7개의 한국어 쿼리를 생성하세요:\n"
        f"{types}\n\n"
        "규칙:\n"
        "- 모든 쿼리는 발췌문만으로 답할 수 있어야 합니다.\n"
        "- cad_ablation은 실제 수치, 파라미터, 실험 설정, 결과값을 물어야 합니다.\n"
        "- section_method와 section_abstract는 섹션 구조가 아니라 실제 고유명사, 설계 선택, 핵심 주장 하나를 물어야 합니다.\n"
        "- citation 타입만 Citation-only excerpts를 사용할 수 있습니다. 나머지 타입은 모두 Main excerpts만 근거로 삼으세요.\n"
        "- citation은 실제로 등장하는 선행연구, baseline, 저자명 중 하나를 구체적으로 물어야 합니다.\n"
        "- '이 논문에서...'처럼 일반적인 질문이나, 섹션/참고문헌 위치를 묻는 질문은 금지합니다.\n"
        "- 각 항목에는 answer_span 필드를 반드시 포함하세요. answer_span은 발췌문에 그대로 등장하는 5~80자 길이의 짧은 답 단서여야 합니다.\n"
        f"- applicable_papers는 정확히 ['{paper}'] 이어야 합니다.\n"
        f"{feedback_block}\n"
        "[발췌문]\n"
        f"{context[:14000]}\n\n"
        "[출력 형식 - JSON only]\n"
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


def normalise_queries(
    track: str,
    paper: str,
    queries: list[dict],
    context: str,
) -> list[dict]:
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
        answer_span = str(item.get("answer_span", "")).strip()
        if not answer_span:
            raise ValueError(f"{paper}/{query_type}: missing answer_span.")
        if len(answer_span) < 5 or len(answer_span) > 80:
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
            return normalise_queries(args.track, paper, generated, context)
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
