"""
Standalone Track 1 query generator — no API server required.
Reads PDFs directly with PyMuPDF, calls GPT-4o, saves track1_queries.json.
Same prompt/validation logic as generate_queries.py.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import fitz  # PyMuPDF

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT = PROJECT_ROOT / "evaluation" / "data" / "track1_queries.json"

PAPERS = [
    "paper_nlp_bge",
    "paper_nlp_rag",
    "paper_nlp_cad",
    "paper_nlp_raptor",
    "paper_midm",
    "paper_ko_rag_eval_framework",
    "paper_ko_hyde_multihop",
    "paper_ko_cad_contrastive",
]

TRACK1_TYPES = [
    "simple_qa",
    "section_method",
    "section_result",
    "section_abstract",
    "cad_hallucination",
    "citation",
    "crosslingual_en",
    "cad_ablation",
]

MAX_ATTEMPTS = 6


# ── PDF text extraction ────────────────────────────────────────────────────────

def extract_pdf_text(paper_id: str) -> str:
    pdf_path = DATA_DIR / f"{paper_id}.pdf"
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


def build_context(paper_id: str) -> str:
    text = extract_pdf_text(paper_id)
    # Trim to ~12000 chars to fit in prompt
    main = text[:12000]
    # Use last portion for citations
    citation_text = text[-3000:] if len(text) > 15000 else text[8000:]
    return (
        "[Main excerpts: use for all non-citation query types]\n"
        + main
        + "\n\n[Citation-only excerpts: use only for citation query types]\n"
        + citation_text
    )


# ── Text normalisation ─────────────────────────────────────────────────────────

def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("­", "")
    text = re.sub(r"-\s*\n\s*", "", text)
    return " ".join(text.lower().split())


def _context_contains_answer_span(context: str, answer_span: str) -> bool:
    return _normalize_text(answer_span) in _normalize_text(context)


# ── Prompt & OpenAI call ───────────────────────────────────────────────────────

def _track1_schema_json(paper: str) -> str:
    return json.dumps(
        {"queries": [{"query": "...", "type": "simple_qa",
                      "applicable_papers": [paper], "answer_span": "..."}]},
        ensure_ascii=False,
    )


def _build_prompt(paper: str, context: str, feedback: str | None = None) -> str:
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
        "- section_method는 방법 섹션의 구현/알고리즘/설계 선택을 묻고, section_result는 결과 섹션의 수치/비교 결과를, "
        "section_abstract는 초록에 명시된 핵심 주장 하나를 묻습니다.\n"
        "- citation은 실제로 인용된 선행 연구, 데이터셋 출처, baseline 중 하나를 구체적으로 물어야 합니다.\n"
        "- 각 항목은 answer_span 필드를 반드시 포함하세요. answer_span은 발췌문에 그대로 존재하는 5~500자 길이의 문구여야 합니다.\n"
        "- answer_span이 발췌문에 없는 표현이면 안 됩니다.\n"
        f"- applicable_papers는 정확히 ['{paper}'] 이어야 합니다.\n"
        f"{feedback_block}\n"
        "[발췌문]\n"
        f"{context[:14000]}\n\n"
        "[출력 형식 - JSON only]\n"
        f"{_track1_schema_json(paper)}"
    )


def _call_openai(api_key: str, prompt: str) -> list[dict]:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1800,
    )
    text = resp.choices[0].message.content.strip()
    # strip markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    data = json.loads(text)
    if isinstance(data, dict):
        return data.get("queries", [])
    return data


# ── Validation ────────────────────────────────────────────────────────────────

def _validate(paper: str, queries: list[dict], context: str) -> list[dict]:
    expected_types = TRACK1_TYPES[:]
    if len(queries) != len(expected_types):
        raise ValueError(f"{paper}: expected {len(expected_types)} queries, got {len(queries)}")

    normalised = []
    for item, expected_type in zip(queries, expected_types):
        query = str(item.get("query", "")).strip()
        if not query:
            raise ValueError(f"{paper}: empty query for type {expected_type}")
        query_type = str(item.get("type", "")).strip()
        if query_type != expected_type:
            raise ValueError(f"{paper}: expected {expected_type}, got {query_type}")

        answer_span = str(item.get("answer_span", "")).strip()
        if not answer_span:
            raise ValueError(f"{paper}/{query_type}: missing answer_span")
        if len(answer_span) < 5 or len(answer_span) > 500:
            raise ValueError(f"{paper}/{query_type}: invalid answer_span length ({len(answer_span)})")
        if not _context_contains_answer_span(context, answer_span):
            print(f"  [WARN] {paper}/{query_type}: answer_span not grounded (kept)", file=sys.stderr)

        # Korean check (except crosslingual_en)
        if query_type != "crosslingual_en":
            korean_chars = sum(1 for c in query if "가" <= c <= "힣")
            if korean_chars < 2:
                raise ValueError(f"{paper}/{query_type}: expected Korean query")

        normalised.append({
            "query": query,
            "ground_truth": "",
            "type": query_type,
            "applicable_papers": [paper],
            "answer_span": answer_span,
        })
    return normalised


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        return 1

    all_queries: list[dict] = []

    for paper in PAPERS:
        print(f"\n[{paper}] extracting PDF text...", file=sys.stderr)
        try:
            context = build_context(paper)
        except Exception as e:
            print(f"  ERROR reading PDF: {e}", file=sys.stderr)
            return 1

        print(f"  context chars: {len(context)}", file=sys.stderr)
        feedback: str | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                prompt = _build_prompt(paper, context, feedback)
                raw = _call_openai(api_key, prompt)
                validated = _validate(paper, raw, context)
                all_queries.extend(validated)
                print(f"  generated={len(validated)}", file=sys.stderr)
                break
            except (ValueError, json.JSONDecodeError) as exc:
                feedback = str(exc)
                if attempt >= MAX_ATTEMPTS:
                    print(f"  FAILED after {MAX_ATTEMPTS} attempts: {feedback}", file=sys.stderr)
                    return 1
                print(f"  retry={attempt} reason={feedback}", file=sys.stderr)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(all_queries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_queries)} queries to {OUTPUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
