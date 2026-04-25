"""
API 엔드포인트 통합 테스트
GPU 없이 실행 가능한 테스트
Usage: python tests/test_api.py
"""

import json
import os
import sys
from uuid import uuid4

# Windows 콘솔 인코딩 문제 해결
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0
AUTH_HEADERS = {}


def _prepare_request_kwargs(kwargs):
    prepared = dict(kwargs)
    use_auth = prepared.pop("use_auth", True)
    headers = dict(prepared.pop("headers", {}) or {})
    if use_auth and AUTH_HEADERS:
        headers = {**AUTH_HEADERS, **headers}
    if headers:
        prepared["headers"] = headers
    return prepared


def test(name, method, path, expected_status=200, **kwargs):
    global PASS, FAIL
    url = f"{BASE}{path}"
    try:
        request_kwargs = _prepare_request_kwargs(kwargs)
        if method == "GET":
            resp = requests.get(url, timeout=60, **request_kwargs)
        elif method == "POST":
            resp = requests.post(url, timeout=120, **request_kwargs)
        elif method == "DELETE":
            resp = requests.delete(url, timeout=30, **request_kwargs)
        else:
            raise ValueError(f"Unknown method: {method}")

        status = "PASS" if resp.status_code == expected_status else "FAIL"
        if status == "PASS":
            PASS += 1
        else:
            FAIL += 1

        data = None
        try:
            data = resp.json()
        except Exception:
            data = resp.text[:200]

        print(f"  [{status}] {name}")
        print(f"         {method} {path} → {resp.status_code}")
        if status == "FAIL" or "--verbose" in sys.argv:
            print(f"         Response: {json.dumps(data, ensure_ascii=False)[:300]}")
        return data

    except Exception as e:
        FAIL += 1
        print(f"  [FAIL] {name}")
        print(f"         ERROR: {e}")
        return None


def bootstrap_auth():
    global AUTH_HEADERS
    unique = uuid4().hex[:8]
    email = f"mrag-smoke-{unique}@example.com"
    username = f"mrag_smoke_{unique}"
    password = "MragSmoke!2026"

    data = test(
        "Register test user",
        "POST",
        "/api/auth/register",
        json={"email": email, "username": username, "password": password},
        use_auth=False,
    )
    token = data.get("access_token") if isinstance(data, dict) else None
    if not token:
        return False

    AUTH_HEADERS = {"Authorization": f"Bearer {token}"}
    me = test("Get current user", "GET", "/api/auth/me")
    return isinstance(me, dict) and me.get("email") == email


def main():
    print("=" * 60)
    print("M-RAG API Integration Tests")
    print("=" * 60)

    # ─── 1. System ───
    print("\n--- System ---")
    test("Root endpoint", "GET", "/")
    test("Health check", "GET", "/health")
    test("Swagger docs accessible", "GET", "/docs")

    print("\n--- Auth bootstrap ---")
    if not bootstrap_auth():
        print("  [FAIL] Authentication bootstrap")
        print("         Could not create a test user or acquire a bearer token")
        return False

    # ─── 2. Papers (empty) ───
    print("\n--- Papers (before upload) ---")
    test("List collections (empty)", "GET", "/api/papers/list")
    test("Get nonexistent paper", "GET", "/api/papers/nonexistent", expected_status=404)

    # ─── 3. PDF Upload ───
    print("\n--- PDF Upload ---")
    os.makedirs("data", exist_ok=True)

    # 테스트용 미니 PDF 생성
    import fitz

    doc = fitz.open()
    # 페이지 1: Title + Abstract
    page = doc.new_page()
    page.insert_text((72, 80), "Test Paper: A Novel Approach", fontsize=18)
    page.insert_text((72, 120), "Abstract", fontsize=14)
    page.insert_text(
        (72, 145),
        "This paper proposes a novel method for improving text classification "
        "accuracy using transformer-based models. We achieve 95.3% accuracy "
        "on the GLUE benchmark dataset, surpassing previous state-of-the-art.",
        fontsize=10,
    )
    # 페이지 2: Method
    page2 = doc.new_page()
    page2.insert_text((72, 80), "1. Introduction", fontsize=14)
    page2.insert_text(
        (72, 110),
        "Natural language understanding is a fundamental challenge in NLP. "
        "Recent advances in transformer models have shown remarkable progress.",
        fontsize=10,
    )
    page2.insert_text((72, 160), "2. Method", fontsize=14)
    page2.insert_text(
        (72, 190),
        "We propose a multi-head cross-attention mechanism that enables "
        "the model to capture both local and global dependencies. The architecture "
        "consists of 12 transformer layers with 768 hidden dimensions.",
        fontsize=10,
    )
    # 페이지 3: Results + References
    page3 = doc.new_page()
    page3.insert_text((72, 80), "3. Results", fontsize=14)
    page3.insert_text(
        (72, 110),
        "Our model achieves 95.3% accuracy on GLUE, 92.1% on SuperGLUE, "
        "and 88.7% F1-score on SQuAD 2.0. The training time is 48 hours "
        "on 8 NVIDIA A100 GPUs with a batch size of 256.",
        fontsize=10,
    )
    page3.insert_text((72, 180), "4. Conclusion", fontsize=14)
    page3.insert_text(
        (72, 210),
        "We presented a novel attention mechanism that outperforms existing methods. "
        "The main limitation is the computational cost during inference.",
        fontsize=10,
    )
    page3.insert_text((72, 260), "References", fontsize=14)
    page3.insert_text(
        (72, 290),
        '[1] Vaswani, A. et al. (2017). "Attention Is All You Need." NeurIPS 2017. arXiv:1706.03762\n'
        '[2] Devlin, J. et al. (2019). "BERT: Pre-training of Deep Bidirectional Transformers." NAACL.',
        fontsize=9,
    )

    pdf_path = "data/test_paper.pdf"
    doc.save(pdf_path)
    doc.close()
    print(f"  (Created test PDF: {pdf_path})")

    with open(pdf_path, "rb") as f:
        data = test(
            "Upload PDF",
            "POST",
            "/api/papers/upload",
            files={"file": ("test_paper.pdf", f, "application/pdf")},
        )
    if data:
        print(f"         Paper: {data.get('paper', {}).get('title', 'N/A')[:60]}")
        print(f"         Chunks: {data.get('paper', {}).get('num_chunks', 0)}")

    # 두 번째 논문 업로드 (비교 테스트용)
    doc2 = fitz.open()
    page = doc2.new_page()
    page.insert_text((72, 80), "Second Paper: Efficient Training", fontsize=18)
    page.insert_text((72, 120), "Abstract", fontsize=14)
    page.insert_text(
        (72, 145),
        "We present an efficient training method that reduces GPU memory usage "
        "by 40% while maintaining model accuracy. Our approach uses gradient "
        "checkpointing and mixed precision training.",
        fontsize=10,
    )
    page2 = doc2.new_page()
    page2.insert_text((72, 80), "2. Method", fontsize=14)
    page2.insert_text(
        (72, 110),
        "The proposed method combines gradient accumulation with dynamic "
        "batch sizing to optimize memory efficiency during training.",
        fontsize=10,
    )
    page2.insert_text((72, 170), "3. Results", fontsize=14)
    page2.insert_text(
        (72, 200),
        "Our method achieves 94.8% accuracy with only 60% of the original "
        "memory footprint, enabling training on consumer GPUs.",
        fontsize=10,
    )
    pdf_path2 = "data/second_paper.pdf"
    doc2.save(pdf_path2)
    doc2.close()

    with open(pdf_path2, "rb") as f:
        test(
            "Upload second PDF",
            "POST",
            "/api/papers/upload",
            files={"file": ("second_paper.pdf", f, "application/pdf")},
        )

    # ─── 4. List after upload ───
    print("\n--- Papers (after upload) ---")
    data = test("List collections", "GET", "/api/papers/list")
    if data:
        for col in data.get("collections", []):
            print(f"         Collection: {col['name']} ({col['count']} chunks)")

    test("Get paper info", "GET", "/api/papers/test_paper")

    # ─── 5. Search ───
    print("\n--- Search ---")
    data = test(
        "Search: accuracy",
        "POST",
        "/api/chat/search",
        json={"query": "What accuracy did the model achieve?", "top_k": 3},
    )
    if data:
        for r in data.get("results", []):
            print(
                f"         [{r['section_type']}] score={r['score']:.4f}: {r['content'][:60]}..."
            )

    data = test(
        "Search: Korean query",
        "POST",
        "/api/chat/search",
        json={"query": "이 모델의 정확도가 얼마야?", "top_k": 3},
    )
    if data:
        for r in data.get("results", []):
            print(
                f"         [{r['section_type']}] score={r['score']:.4f}: {r['content'][:60]}..."
            )

    data = test(
        "Search: section filter (method)",
        "POST",
        "/api/chat/search",
        json={"query": "model architecture", "section_filter": "method", "top_k": 3},
    )

    data = test(
        "Search: doc_id filter",
        "POST",
        "/api/chat/search",
        json={"query": "accuracy", "doc_id_filter": "test_paper", "top_k": 3},
    )

    # ─── 6. Chat (Query Router) ───
    print("\n--- Chat (Query Router) ---")

    # Route A: 단순 QA
    data = test(
        "Route A: 단순 QA",
        "POST",
        "/api/chat/query",
        json={"query": "이 논문에서 사용한 데이터셋이 뭐야?"},
    )
    if data:
        print(
            f"         Route: {data.get('route', {}).get('route')} - {data.get('route', {}).get('route_name', '')}"
        )
        print(f"         Answer: {data.get('answer', '')[:100]}...")

    # Route B: 섹션 특화
    data = test(
        "Route B: 결과 섹션",
        "POST",
        "/api/chat/query",
        json={"query": "실험 결과가 어떻게 나왔어?"},
    )
    if data:
        print(
            f"         Route: {data.get('route', {}).get('route')} - {data.get('route', {}).get('route_name', '')}"
        )

    # Route B: 방법론
    data = test(
        "Route B: 방법론 섹션",
        "POST",
        "/api/chat/query",
        json={"query": "방법론 설명해줘"},
    )
    if data:
        print(
            f"         Route: {data.get('route', {}).get('route')} - {data.get('route', {}).get('route_name', '')}"
        )

    # Route C: 비교
    data = test(
        "Route C: 논문 비교",
        "POST",
        "/api/chat/query",
        json={"query": "두 논문의 정확도 차이를 비교해줘"},
    )
    if data:
        print(
            f"         Route: {data.get('route', {}).get('route')} - {data.get('route', {}).get('route_name', '')}"
        )

    # Route E: 요약
    data = test(
        "Route E: 전체 요약",
        "POST",
        "/api/chat/query",
        json={"query": "이 논문 전체 요약해줘"},
    )
    if data:
        print(
            f"         Route: {data.get('route', {}).get('route')} - {data.get('route', {}).get('route_name', '')}"
        )

    # Route D: 인용
    data = test(
        "Route D: 인용 논문",
        "POST",
        "/api/chat/query",
        json={"query": "인용 논문들 분석해줘"},
    )
    if data:
        print(
            f"         Route: {data.get('route', {}).get('route')} - {data.get('route', {}).get('route_name', '')}"
        )

    # ─── 7. Error Cases ───
    print("\n--- Error Handling ---")
    test(
        "Empty query",
        "POST",
        "/api/chat/query",
        json={"query": ""},
        expected_status=422,
    )
    test(
        "Invalid file type",
        "POST",
        "/api/papers/upload",
        files={"file": ("bad.xyz", b"not a valid file", "application/octet-stream")},
        expected_status=400,
    )

    # ─── 8. Citations ───
    print("\n--- Citations ---")
    data = test(
        "Track citations",
        "POST",
        "/api/citations/track",
        json={"doc_id": "test_paper", "max_citations": 2},
    )
    if data:
        print(f"         Citations found: {len(data.get('citations', []))}")
        for c in data.get("citations", []):
            print(f"         - {c.get('title', 'N/A')[:50]}")

    # ─── 9. Cleanup ───
    print("\n--- Cleanup ---")
    test("Delete collection", "DELETE", "/api/papers/papers")
    test("Logout", "POST", "/api/auth/logout")

    # ─── Summary ───
    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"Results: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("ALL TESTS PASSED!")
    else:
        print(f"WARNING: {FAIL} test(s) failed")
    print("=" * 60)

    return FAIL == 0


if __name__ == "__main__":
    if not main():
        sys.exit(1)
