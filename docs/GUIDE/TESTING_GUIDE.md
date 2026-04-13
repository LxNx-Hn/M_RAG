<!-- markdownlint-disable MD060 -->
# M-RAG 테스팅 & 실험 가이드

> 졸업작품 제출용 Table 1~4 재현 절차  
> 최종 업데이트: 2026-04-14

---

## 0. 전제 조건

```bash
# 백엔드 의존성 설치
pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install -r backend/requirements.txt
pip install accelerate

# 모델 다운로드
python backend/scripts/download_models.py              # 전체 (GPU 필요)
python backend/scripts/download_models.py --skip-llm   # 임베딩 + 재랭커만
```

### 모델별 GPU 요구사항

| 모델 | 파라미터 | VRAM | 권장 GPU |
|------|---------|------|---------|
| MIDM Mini | 2.3B | ~5GB (bfloat16) | RTX 3080 Ti, RTX 4070+ |
| MIDM Base | 11.5B | ~23GB (bfloat16) | A100 40GB, H100 |
| MIDM Base (4-bit) | 11.5B | ~7GB (NF4) | RTX 3090, RTX 4090 |

> **GPU 없이도 할 수 있는 것**: 파싱, 청킹, 임베딩, 검색, 재랭킹, 테스트 쿼리 구성  
> **GPU 필요한 것**: MIDM 생성, CAD/SCD 디코더, RAGAS 평가 (LLM 호출)

---

## 1. 단위 테스트 — 모듈별 동작 확인

### 1-1. API 통합 테스트 (23개)

```bash
# FastAPI 서버 먼저 실행
cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000

# 별도 터미널에서
cd backend && python -X utf8 tests/test_api.py
# 목표: 23/23 PASS
```

### 1-2. 모듈 임포트 전체 확인

```bash
cd backend && python -c "
import modules.pdf_parser
import modules.section_detector
import modules.chunker
import modules.embedder
import modules.vector_store
import modules.query_router
import modules.query_expander
import modules.hybrid_retriever
import modules.reranker
import modules.context_compressor
import modules.citation_tracker
import modules.cad_decoder
import modules.scd_decoder
import modules.generator
print('모든 모듈 임포트 성공')
"
```

### 1-3. CAD/SCD 단독 확인

```bash
# CAD (MODULE 13A)
python -c "
from modules.cad_decoder import CADDecoder, create_cad_processor
from modules.generator import Generator
gen = Generator()
processor = create_cad_processor(gen, query='이 논문의 방법론은?', alpha=0.5)
print('CAD processor 생성 성공:', type(processor))
"

# SCD (MODULE 13B)
python -c "
from modules.scd_decoder import SCDDecoder
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('K-intelligence/Midm-2.0-Mini-Instruct')
scd = SCDDecoder(tokenizer=tok, beta=0.3)
scd._build_non_target_ids('cpu')
print(f'패널티 대상 토큰 수: {len(scd._non_target_ids)}')
print('SCD 초기화 성공')
"
```

---

## 2. 검색 품질 확인 (GPU 불필요)

```bash
cd backend
python -c "
from modules.pdf_parser import PDFParser
from modules.section_detector import SectionDetector
from modules.chunker import Chunker
from modules.embedder import Embedder
from modules.vector_store import VectorStore
from modules.hybrid_retriever import HybridRetriever
from modules.reranker import Reranker

doc = PDFParser().parse('data/1810.04805_bert.pdf')
doc = SectionDetector().detect(doc)
chunks = Chunker().chunk_document(doc, strategy='section')
embedder = Embedder()
vs = VectorStore()
embeddings = embedder.embed_texts([c.content for c in chunks])
vs.add_chunks('test_col', chunks, embeddings)

hr = HybridRetriever(vs, embedder)
hr.fit_bm25('test_col')
rr = Reranker()

query = '이 논문의 핵심 방법론은 무엇인가?'
results = hr.search('test_col', query)
reranked = rr.rerank(query, results)

print(f'검색 결과 {len(reranked)}개:')
for r in reranked[:3]:
    print(f'  [{r[\"metadata\"][\"section_type\"]}] score={r.get(\"rerank_score\",0):.3f}')
    print(f'  {r[\"content\"][:100]}...')
"
```

---

## 3. 전체 실험 실행 (Table 1~4)

### 통합 실험 스크립트

`run_all_experiments.py`로 Table 1~4를 한 번에 실행합니다.

```bash
cd backend

# ─── 로컬 (MIDM Mini, RTX 3080 Ti 12GB) ───
LOAD_GPU_MODELS=true python -X utf8 scripts/run_all_experiments.py \
    --paper-pdf data/1810.04805_bert.pdf \
    --max-queries 10

# ─── 특정 테이블만 ───
LOAD_GPU_MODELS=true python -X utf8 scripts/run_all_experiments.py \
    --paper-pdf data/1810.04805_bert.pdf \
    --tables 2,3 --max-queries 8

# ─── MIDM Base (24GB+ GPU) ───
GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct \
LOAD_GPU_MODELS=true python -X utf8 scripts/run_all_experiments.py \
    --paper-pdf data/1810.04805_bert.pdf \
    --max-queries 10
```

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--paper-pdf` | (필수) | 실험용 논문 PDF 경로 |
| `--collection` | `full_eval` | ChromaDB 컬렉션 이름 |
| `--tables` | `1,2,3,4` | 실행할 테이블 번호 |
| `--max-queries` | `10` | 사용할 최대 쿼리 수 (빠른 테스트: 5) |

### 소요 시간 예상

각 쿼리당 **4회 LLM 호출** (생성 1 + RAGAS 평가 3: faithfulness, relevancy, precision)

| 구성 | LLM 호출 수 (10q) | A100 (Base) | 3080 Ti (Mini) |
|------|-------------------|-------------|----------------|
| Table 1 (6 config) | 240 | ~12분 | ~40분 |
| Table 2 (6 config) | 240 | ~12분 | ~40분 |
| Table 3 (4 config) | 160 | ~8분 | ~27분 |
| Table 4 (4 config) | 160 | ~8분 | ~27분 |
| **합계** | **800** | **~40분** | **~134분** |

### 실험 결과 파일

```text
evaluation/results/full_experiment_YYYYMMDD_HHMMSS.json
```

stdout에 마크다운 테이블이 출력됩니다 (Table 1~4).

---

## 4. RunPod 실행 가이드

로컬 GPU가 부족하거나 Base 모델 실험이 필요할 때 RunPod을 사용합니다.

### 4-1. RunPod 설정

1. [runpod.io](https://runpod.io)에서 GPU Pod 생성
   - **Mini 실험**: RTX 4090 (24GB), ~$0.44/hr
   - **Base 실험**: A100 40GB, ~$1.04/hr
   - Template: `RunPod PyTorch 2.x`
2. SSH 접속 정보 확인

### 4-2. 실행

```bash
# 1. 스크립트 업로드
scp backend/scripts/runpod_experiment.sh root@<pod-ip>:/workspace/

# 2-A. Base 모델 실행 (A100, 기본)
ssh root@<pod-ip> "bash /workspace/runpod_experiment.sh"

# 2-B. Mini 모델 실행 (RTX 4090 등)
ssh root@<pod-ip> "bash /workspace/runpod_experiment.sh mini"

# 2-C. 쿼리 수 조절 (빠른 테스트)
ssh root@<pod-ip> "bash /workspace/runpod_experiment.sh base 5"

# 3. 결과 다운로드
scp root@<pod-ip>:/workspace/M_RAG/backend/evaluation/results/*.json ./results/
scp root@<pod-ip>:/workspace/experiment_log.txt ./results/
```

### 4-3. 비용 참고

| GPU | 모델 | 예상 시간 | 비용 |
|-----|------|----------|------|
| A100 40GB | Base (11.5B) | ~40분 | ~$0.70 |
| RTX 4090 | Mini (2.3B) | ~60분 | ~$0.44 |

> 실험 완료 후 반드시 Pod를 정지/삭제하세요!

---

## 5. 실험용 논문

### 기본 제공 (BERT)

`data/1810.04805_bert.pdf` — BERT: Pre-training of Deep Bidirectional Transformers (Devlin et al., 2019)

- 16페이지, NLP/AI 논문
- 구체적 수치 풍부 (GLUE 82.1%, SQuAD F1 93.2, 파라미터 110M/340M 등)
- CAD 환각 억제 실험에 적합 (모델이 파라메트릭 지식으로 답할 위험 있는 도메인)
- `test_queries.json`의 CAD ablation 쿼리에 ground_truth가 BERT 수치로 채워져 있음

### 테스트 쿼리

`evaluation/test_queries.json` — 67개 쿼리 (v2.2)

| 유형 | 개수 | 용도 |
|------|------|------|
| simple_qa | 7 | 기본 QA (A경로) |
| section_result | 6 | 실험 결과 검색 (B경로) |
| section_method | 7 | 방법론 검색 (B경로) |
| cad_ablation | 7 | CAD 환각 억제 평가 (ground_truth 포함) |
| crosslingual | 3 | SCD 언어 이탈 방지 평가 |
| compare | 3 | 비교 분석 (C경로, 2편 필요) |
| citation | 4 | 인용 추적 (D경로) |
| summary | 3 | 전체 요약 (E경로) |
| lecture | 8 | 강의 모드 |
| patent | 6 | 특허 모드 |
| general_doc | 5 | 일반 문서 |

---

## 6. Language Drift 확인

```bash
cd backend
python -c "
from modules.generator import Generator
from evaluation.decoder_ablation import compute_language_drift_rate

gen = Generator()  # GPU 필요

en_context = '''
This paper proposes a novel approach to information retrieval
using dense embeddings. Our method achieves state-of-the-art
performance on multiple benchmarks, outperforming BM25 by 15%.
'''

ko_queries = [
    '이 논문의 핵심 기여는 무엇인가?',
    '제안된 방법의 성능은 어떻게 되는가?',
    '기존 방법과 비교하여 얼마나 개선되었는가?',
]

answers = [gen.generate(query=q, context=en_context) for q in ko_queries]
for q, a in zip(ko_queries, answers):
    print(f'Q: {q}')
    print(f'A: {a[:100]}')
    print()

drift = compute_language_drift_rate(answers)
print(f'Language Drift 이탈률: {drift:.1%}')
print('→ 이탈 있으면 SCD 효과 측정 가능 / 없으면 연구 설계 재검토')
"
```

---

## 7. 남은 작업 체크리스트

### 🔴 필수 (논문 Contribution 직결)

- [x] **test_queries.json 구성** — 67개 쿼리, CAD ablation 7개에 BERT ground_truth 채움
- [ ] **Language Drift 초기 실측** — 섹션 6 참고 (GPU 필요)
- [ ] **Table 1~4 실험 실행** — `run_all_experiments.py` 코드 완성, RunPod에서 실행 필요
- [x] **`_run_single_config()` 구현** — CAD+SCD 통합 logits_processor, 쿼리별 진행 로깅 포함
- [x] **RAPTOR 청킹 (E경로)** — Pipeline E에서 RAPTOR chunk_level>0 자동 감지/활용 연동 완료

### 🟡 중요 (시스템 완성도)

- [x] **MIDM-2.0 프롬프트 템플릿 최적화** — `apply_chat_template()` 적용, Llama-3 스타일 특수 토큰 사용
- [x] **한→영 번역 쿼리 확장 (M7)** — `query_expander.py` 검증 완료, 학술 용어 정확도 개선
- [x] **수치 환각률 측정 함수 정밀화** — 단위 포괄(M/B/K/GB/%), trivial 숫자 제외, 정규화 비교

### 🟢 선택 (포트폴리오 강화)

- [x] **답변 내보내기** — Copy/MD/PPT 내보내기 구현 완료
- [x] **플래시카드 모드** — Pipeline F 확장, FlashcardViewer 컴포넌트
- [ ] **데모 영상 제작** — React UI 기반 시연
- [ ] **React UI 데모 폴리싱** — Ablation 결과 시각화 추가
