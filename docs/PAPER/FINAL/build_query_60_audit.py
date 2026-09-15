"""Build the final 60-query audit from the two frozen query splits."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SPLITS = (
    ROOT / "experiments/data/query_splits/decoder_main_queries.json",
    ROOT / "experiments/data/query_splits/extended_validation_questions.json",
)
OUT = ROOT / "docs/PAPER/FINAL/generated/QUERY_60_AUDIT.md"

PAPER_LABELS = {
    "paper_nlp_rag": "RAG Survey",
    "paper_nlp_cad": "CAD",
    "paper_nlp_raptor": "RAPTOR",
    "paper_midm": "Mi:dm K 2.5 Pro Technical Report",
}


def load_queries() -> list[dict]:
    queries: list[dict] = []
    for path in SPLITS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        queries.extend(payload["queries"])
    return queries


def verify(queries: list[dict]) -> None:
    if len(queries) != 60:
        raise ValueError(f"expected 60 queries, found {len(queries)}")
    ids = [str(query["query_id"]) for query in queries]
    if len(set(ids)) != 60:
        raise ValueError("query_id values are not unique")
    texts = [str(query["query"]).strip() for query in queries]
    if not all(texts):
        raise ValueError("blank query text found")
    if len(set(texts)) != 60:
        raise ValueError("exact duplicate query text found")
    for query in queries:
        papers = query.get("applicable_papers", [])
        if len(papers) != 1:
            raise ValueError(f"{query['query_id']}: expected one target paper")
        if query.get("paper_language") not in {"en", "ko"}:
            raise ValueError(f"{query['query_id']}: paper_language metadata is invalid")
        if query.get("gt_status") != "valid":
            raise ValueError(f"{query['query_id']}: GT is not valid")
        if query.get("answerability_status") != "answerable":
            raise ValueError(f"{query['query_id']}: query is not answerable")
        if not query.get("has_answer_span") or not str(query.get("answer_span", "")).strip():
            raise ValueError(f"{query['query_id']}: answer span is missing")


def main() -> None:
    queries = load_queries()
    verify(queries)
    paper_counts = Counter(query["applicable_papers"][0] for query in queries)
    type_counts = Counter(query.get("normalized_query_type", "unspecified") for query in queries)
    language_metadata_counts = Counter(query.get("paper_language") for query in queries)
    lines = [
        "# 60개 질의-대상문서 쌍 감사",
        "",
        "이 보고서는 최종 RAG-Cube 실험에 사용한 두 개의 동결 query split을 읽어 자동 생성한다.",
        "각 질의는 하나의 고정 대상 문서, 한국어 질문, valid answer span, answerable 상태를 함께 가진다.",
        "",
        "## 검증 결과",
        "",
        "| 항목 | 값 |",
        "|---|---:|",
        "| 질의-대상문서 쌍 | 60 |",
        "| 고유 query ID | 60 |",
        "| 고유 한국어 질문 | 60 |",
        "| 고정 대상 문서 | 4 |",
        "| valid GT 및 answerable 질의 | 60 |",
        "| answer span 보유 질의 | 60 |",
        "",
        "## 대상 문서 분포",
        "",
        "| 대상 문서 | 질의 수 |",
        "|---|---:|",
    ]
    for paper, count in sorted(paper_counts.items()):
        lines.append(f"| {PAPER_LABELS[paper]} | {count} |")
    lines += ["", "## 질문 유형 분포", "", "| 유형 | 질의 수 |", "|---|---:|"]
    for kind, count in sorted(type_counts.items()):
        lines.append(f"| {kind} | {count} |")
    lines += [
        "",
        "## Split 언어 메타데이터",
        "",
        "| 메타데이터 값 | 질의 수 |",
        "|---|---:|",
    ]
    for language, count in sorted(language_metadata_counts.items()):
        lines.append(f"| {language} | {count} |")
    lines += ["", "## 전체 질의 목록", "", "| query ID | 대상 문서 | 유형 | 한국어 질문 |", "|---|---|---|---|"]
    for query in sorted(queries, key=lambda item: str(item["query_id"])):
        paper = PAPER_LABELS[query["applicable_papers"][0]]
        text = str(query["query"]).replace("|", "\\|")
        lines.append(f"| {query['query_id']} | {paper} | {query.get('normalized_query_type')} | {text} |")
    lines += [
        "",
        "## 입력 근거",
        "",
        "- `experiments/data/query_splits/decoder_main_queries.json`",
        "- `experiments/data/query_splits/extended_validation_questions.json`",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
