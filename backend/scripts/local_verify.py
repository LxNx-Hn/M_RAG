"""
로컬 검증 스크립트 — Alice 런 전 파이프라인 end-to-end 확인용.

논문별 대표 쿼리 1개씩 실행해서:
  1. 서버 health
  2. 각 논문 인덱싱 여부
  3. 검색(search) 정상 동작
  4. 생성(query) 정상 동작
  5. skip-query-generation 동작 확인 (track1_queries.json 비어있지 않은지)

Usage:
    python scripts/local_verify.py --token <JWT>
    python scripts/local_verify.py  (MRAG_API_TOKEN 환경변수 사용)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_BASE = os.environ.get("MRAG_API_BASE", "http://127.0.0.1:8000")
COLLECTION = "papers"

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

# 논문별 대표 쿼리 (track1_queries.json에서 simple_qa 타입 발췌)
REPRESENTATIVE_QUERIES: dict[str, str] = {
    "paper_nlp_bge":             "M3-Embedding 모델은 몇 개의 언어를 지원하나요?",
    "paper_nlp_rag":             "RAG가 LLM에서 사실적으로 부정확한 콘텐츠 생성을 줄이는 데 어떻게 기여합니까?",
    "paper_nlp_cad":             "LLaMA 모델이 FIFA 월드컵 우승 횟수에 대해 잘못된 예측을 하는 이유는 무엇인가요?",
    "paper_nlp_raptor":          "RAPTOR 모델이 QuALITY 벤치마크에서 기존 성능을 얼마나 개선했나요?",
    "paper_midm":                "Mi:dm K 2.5 Pro 모델의 파라미터 수는 몇 개입니까?",
    "paper_ko_rag_eval_framework": "AutoRAG는 한국어 문장 표현의 자연성과 컨텍스트 기반의 정확성 측면에서 어떤 성능을 보였나요?",
    "paper_ko_hyde_multihop":    "HyDE 기반 멀티 홉 검색 기법의 실험 결과에서 recall과 hit rate는 각각 얼마나 증가했나요?",
    "paper_ko_cad_contrastive":  "대규모 언어 모델의 디코딩 과정에서 발생하는 문제는 무엇인가요?",
}

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"


def get_token() -> str:
    if len(sys.argv) > 2 and sys.argv[1] == "--token":
        return sys.argv[2]
    t = os.environ.get("MRAG_API_TOKEN", "")
    if not t:
        print(f"[{WARN}] MRAG_API_TOKEN not set — requests may fail with 401")
    return t


def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def check(label: str, ok: bool, detail: str = "") -> bool:
    status = PASS if ok else FAIL
    msg = f"  [{status}] {label}"
    if detail:
        msg += f"  — {detail}"
    print(msg)
    return ok


# ── STEP 1: Health ──────────────────────────────────────────────────────────

def step_health(token: str) -> bool:
    print("\n[STEP 1] Server health check")
    try:
        r = requests.get(f"{API_BASE}/health", timeout=10)
        d = r.json()
        ok_db = d.get("database_connected", False)
        ok_chroma = d.get("chroma_connected", False)
        ok_modules = d.get("modules_loaded", False)
        ok_gpu = d.get("gpu_available", False)
        ok_gen = d.get("generator_loaded", False)
        check("database_connected", ok_db)
        check("chroma_connected", ok_chroma)
        check("modules_loaded", ok_modules)
        check("gpu_available", ok_gpu)
        check("generator_loaded", ok_gen)
        collections = d.get("collections", [])
        print(f"  indexed collections: {collections}")
        all_ok = all([ok_db, ok_chroma, ok_modules, ok_gen])
        return all_ok
    except Exception as e:
        check("health endpoint", False, str(e))
        return False


# ── STEP 2: Paper index check ───────────────────────────────────────────────

def step_index_check(token: str) -> dict[str, bool]:
    print("\n[STEP 2] Paper index check")
    try:
        r = requests.get(
            f"{API_BASE}/api/papers/list",
            headers=headers(token),
            timeout=10,
        )
        r.raise_for_status()
        available = {item["name"] for item in r.json().get("collections", [])}
    except Exception as e:
        print(f"  [{FAIL}] /api/papers/list error: {e}")
        return {p: False for p in PAPERS}

    status = {}
    for paper in PAPERS:
        ok = paper in available
        check(paper, ok, "" if ok else "NOT INDEXED — upload needed")
        status[paper] = ok
    return status


def upload_paper(token: str, paper_id: str) -> bool:
    pdf = PROJECT_ROOT / "data" / f"{paper_id}.pdf"
    if not pdf.exists():
        print(f"  [{FAIL}] PDF not found: {pdf}")
        return False
    try:
        with pdf.open("rb") as f:
            r = requests.post(
                f"{API_BASE}/api/papers/upload",
                headers=headers(token),
                files={"file": (pdf.name, f, "application/pdf")},
                data={"collection_name": COLLECTION, "doc_id": paper_id},
                timeout=120,
            )
        if r.status_code == 200:
            print(f"  [{PASS}] uploaded {paper_id}")
            return True
        else:
            print(f"  [{FAIL}] upload {paper_id}: {r.status_code} {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  [{FAIL}] upload {paper_id}: {e}")
        return False


# ── STEP 3: Search test ─────────────────────────────────────────────────────

def step_search(token: str, indexed: dict[str, bool]) -> dict[str, bool]:
    print("\n[STEP 3] Search test (top-3 per paper)")
    status = {}
    for paper, query in REPRESENTATIVE_QUERIES.items():
        if not indexed.get(paper):
            print(f"  [{WARN}] {paper}: skipped (not indexed)")
            status[paper] = False
            continue
        try:
            r = requests.post(
                f"{API_BASE}/api/chat/search",
                headers=headers(token),
                json={
                    "query": query,
                    "collection_name": COLLECTION,
                    "top_k": 3,
                    "doc_id_filter": paper,
                },
                timeout=30,
            )
            r.raise_for_status()
            results = r.json().get("results", [])
            ok = len(results) > 0
            detail = f"{len(results)} chunks" if ok else "0 chunks returned"
            check(paper, ok, detail)
            status[paper] = ok
        except Exception as e:
            check(paper, False, str(e))
            status[paper] = False
    return status


# ── STEP 4: Generation test ─────────────────────────────────────────────────

def step_generate(token: str, indexed: dict[str, bool]) -> dict[str, bool]:
    print("\n[STEP 4] Generation test (naive RAG, no CAD)")
    status = {}
    for paper, query in REPRESENTATIVE_QUERIES.items():
        if not indexed.get(paper):
            print(f"  [{WARN}] {paper}: skipped (not indexed)")
            status[paper] = False
            continue
        try:
            t0 = time.perf_counter()
            r = requests.post(
                f"{API_BASE}/api/chat/query",
                headers=headers(token),
                json={
                    "query": query,
                    "collection_name": COLLECTION,
                    "use_hyde": False,
                    "use_cad": False,
                    "top_k": 3,
                    "doc_id_filter": paper,
                },
                timeout=120,
            )
            elapsed = round(time.perf_counter() - t0, 1)
            r.raise_for_status()
            answer = r.json().get("answer", "").strip()
            ok = bool(answer) and answer.lower() != "error"
            snippet = answer[:80].replace("\n", " ") if answer else "(empty)"
            check(paper, ok, f"{elapsed}s | {snippet}...")
            status[paper] = ok
        except Exception as e:
            check(paper, False, str(e))
            status[paper] = False
    return status


# ── STEP 5: Static asset check ──────────────────────────────────────────────

def step_static_assets() -> bool:
    print("\n[STEP 5] Static asset check")
    t1 = PROJECT_ROOT / "evaluation" / "data" / "track1_queries.json"
    t2 = PROJECT_ROOT / "evaluation" / "data" / "track2_queries.json"

    ok1 = False
    try:
        queries = json.loads(t1.read_text(encoding="utf-8"))
        count = len(queries) if isinstance(queries, list) else 0
        papers_in_file = {q.get("applicable_papers", [None])[0] for q in queries if isinstance(q, dict)}
        ok1 = count == 64 and len(papers_in_file - {None}) == 8
        check(
            "track1_queries.json",
            ok1,
            f"{count} queries, {len(papers_in_file - {None})} papers",
        )
    except Exception as e:
        check("track1_queries.json", False, str(e))

    ok2 = False
    try:
        queries2 = json.loads(t2.read_text(encoding="utf-8"))
        count2 = len(queries2) if isinstance(queries2, list) else 0
        ok2 = count2 >= 28
        check("track2_queries.json", ok2, f"{count2} queries")
    except Exception as e:
        check("track2_queries.json", False, str(e))

    # run_alice_full.sh has --skip-query-generation?
    alice_sh = PROJECT_ROOT / "run_alice_full.sh"
    skip_ok = "--skip-query-generation" in alice_sh.read_text(encoding="utf-8")
    check("run_alice_full.sh has --skip-query-generation", skip_ok)

    return ok1 and ok2 and skip_ok


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    token = get_token()

    print("=" * 60)
    print("M-RAG Local Verification")
    print(f"API: {API_BASE}")
    print("=" * 60)

    # STEP 1: health
    health_ok = step_health(token)
    if not health_ok:
        print(f"\n[{FAIL}] Server not healthy. Start with:")
        print("  cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000")
        return 1

    # STEP 2: index
    indexed = step_index_check(token)
    missing = [p for p, ok in indexed.items() if not ok]
    if missing:
        print(f"\n  Uploading {len(missing)} missing papers...")
        for paper in missing:
            ok = upload_paper(token, paper)
            indexed[paper] = ok
        print("  Waiting 5s for indexing to settle...")
        time.sleep(5)

    # STEP 3: search
    search_ok = step_search(token, indexed)

    # STEP 4: generation
    gen_ok = step_generate(token, indexed)

    # STEP 5: static assets
    assets_ok = step_static_assets()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_search = all(search_ok.values())
    all_gen = all(gen_ok.values())
    check("All 8 papers searchable", all_search)
    check("All 8 papers generate answers", all_gen)
    check("Static assets ready", assets_ok)

    if all_search and all_gen and assets_ok:
        print(f"\n[{PASS}] 로컬 검증 완료 — Alice 런 준비됨")
        print("\nAlice에서:")
        print("  git pull --ff-only origin main")
        print("  bash run_alice_full.sh")
        return 0
    else:
        failed_papers = [p for p, ok in {**search_ok, **gen_ok}.items() if not ok]
        print(f"\n[{FAIL}] 검증 실패 — 위 FAIL 항목 확인 필요")
        if failed_papers:
            print("  실패 논문:", ", ".join(set(failed_papers)))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
