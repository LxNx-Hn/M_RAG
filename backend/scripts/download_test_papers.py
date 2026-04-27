"""
테스트 논문 PDF 자동 다운로드 스크립트
arXiv API를 사용하여 실험에 필요한 논문을 backend/data/에 다운로드

사용법:
    cd backend
    python scripts/download_test_papers.py
    python scripts/download_test_papers.py --skip-korean   # 한국어 논문 건너뜀
"""

import argparse
import sys
import time
import urllib.request
from pathlib import Path

# ─────────────────────────────────────────────────────────
# 다운로드 대상 논문
# ─────────────────────────────────────────────────────────

PAPERS = [
    {
        "id": "paper_nlp_bge",
        "arxiv_id": "2402.03216",
        "title": "BGE M3-Embedding (Chen et al., ACL 2024)",
        "desc": "MODULE 4 기반 논문. Table 1~3 기본 실험 대상.",
    },
    {
        "id": "paper_nlp_rag",
        "arxiv_id": "2312.10997",
        "title": "RAG Survey (Gao et al., ICLR 2024)",
        "desc": "Track 1 범용 QA 실험 대상. LLM 사전학습 지식 ↑ → CAD 효과 측정에 적합.",
    },
    {
        "id": "paper_nlp_cad",
        "arxiv_id": "2305.14739",
        "title": "CAD: Context-Aware Decoding (Shi et al., NAACL 2024)",
        "desc": "MODULE 13A 기반 논문. CAD on/off 비교 시 수치환각률 측정에 최적.",
    },
    {
        "id": "paper_nlp_raptor",
        "arxiv_id": "2401.18059",
        "title": "RAPTOR (Sarthi et al., ICLR 2024)",
        "desc": "MODULE 3 RAPTOR 청킹 기반. Track 2 요약 경로(E) 실험 대상.",
    },
    {
        "id": "1810.04805_bert",
        "arxiv_id": "1810.04805",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers (Devlin et al., NAACL 2019)",
        "desc": "Track 1 Table 1~3 ablation 대상 (7번째 논문). 사전학습 지식 풍부 → CAD 효과 측정.",
    },
    {
        "id": "2101.08577",
        "arxiv_id": "2101.08577",
        "title": "Unsupervised Cross-lingual Representation Learning (arXiv 2021)",
        "desc": "Track 1 ablation 대상 (7번째 논문 보완). 다국어 도메인 쿼리 평가.",
    },
]

# 한국어 논문: arXiv cs.CL 에서 한국어 포함 논문
KOREAN_PAPERS = [
    {
        "id": "paper_korean",
        "arxiv_id": "2502.11175",
        "title": "Language Preference of Multilingual RAG (Park & Lee, ACL 2025 Findings)",
        "desc": "SCD 언어이탈률 측정 대상. 한/영 혼합 도메인.",
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
            req = urllib.request.Request(
                url, headers={"User-Agent": "M-RAG/1.0 (research)"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            dest_path.write_bytes(data)
            size_kb = len(data) // 1024
            print(f" done ({size_kb} KB)")
            return True
        except Exception as e:
            print(f" FAIL ({e})")
            if attempt < retries:
                time.sleep(5)
    return False


def main():
    parser = argparse.ArgumentParser(description="테스트 논문 PDF 다운로드")
    parser.add_argument("--skip-korean", action="store_true", help="한국어 논문 건너뜀")
    parser.add_argument(
        "--data-dir", default=None, help="저장 디렉토리 (기본: backend/data)"
    )
    args = parser.parse_args()

    # 경로 설정
    here = Path(__file__).parent.parent  # backend/
    data_dir = Path(args.data_dir) if args.data_dir else here / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"[download_test_papers] 저장 경로: {data_dir}")
    print()

    targets = PAPERS if args.skip_korean else PAPERS + KOREAN_PAPERS
    success, failed = [], []

    for paper in targets:
        dest = data_dir / f"{paper['id']}.pdf"
        print(f"[{paper['id']}] {paper['title']}")
        print(f"  용도: {paper['desc']}")

        if dest.exists():
            size_kb = dest.stat().st_size // 1024
            print(f"  이미 존재함 ({size_kb} KB) → 건너뜀")
            success.append(paper["id"])
            continue

        ok = download_paper(paper["arxiv_id"], dest)
        if ok:
            success.append(paper["id"])
        else:
            failed.append(paper["id"])
            print(
                f"  ⚠️  수동 다운로드 필요: https://arxiv.org/pdf/{paper['arxiv_id']}.pdf"
            )
            print(f"     → {dest}에 저장하세요.")

        time.sleep(2)  # arXiv rate limit 준수
        print()

    print("=" * 50)
    print(f"성공: {len(success)} / {len(targets)}")
    if failed:
        print(f"실패 (수동 필요): {failed}")

    # 한국어 논문 없을 때 안내
    korean_dest = data_dir / "paper_korean.pdf"
    if not korean_dest.exists() and not args.skip_korean:
        print()
        print("⚠️  한국어 논문(paper_korean.pdf)이 없습니다.")
        print("   SCD 언어이탈률 측정을 위해 한국어 논문이 필요합니다.")
        print("   아래 중 하나를 선택하세요:")
        print(
            "   1) arXiv 2502.11175 PDF를 수동 다운로드 후 backend/data/paper_korean.pdf 로 저장"
        )
        print("   2) RISS/KISS에서 한국어 NLP 논문 다운로드 후 저장")
        print("   3) --skip-korean 플래그로 SCD 측정 제외하고 실행")

    if failed and len(failed) == len(targets):
        sys.exit(1)


if __name__ == "__main__":
    main()
