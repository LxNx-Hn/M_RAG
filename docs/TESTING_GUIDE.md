# M-RAG 테스팅 & 실험 가이드

> GuideV2 기준 — 졸업작품 제출용 Table 1 · Table 2 재현 절차

---

## 0. 전제 조건

```bash
# 백엔드 의존성 설치
pip install -r backend/requirements.txt

# 모델 다운로드 (GPU 없으면 --skip-llm)
python backend/scripts/download_models.py --skip-llm   # 임베딩 + 재랭커만
python backend/scripts/download_models.py              # MIDM-2.0 포함 전체
```

> **GPU 없이도 할 수 있는 것**: 파싱, 청킹, 임베딩, 검색, 재랭킹, 테스트 쿼리 구성  
> **GPU 필요한 것**: MIDM-2.0 생성, CAD/SCD 디코더, RAGAS 평가 (LLM 호출)

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

### 1-2. 모듈 개별 확인

```bash
cd backend
python -c "
from modules.pdf_parser import PDFParser
from modules.section_detector import SectionDetector
from modules.chunker import Chunker

parser = PDFParser()
detector = SectionDetector()
chunker = Chunker()

doc = parser.parse('data/sample.pdf')
doc = detector.detect(doc)
chunks = chunker.chunk_document(doc, strategy='section')
print(f'섹션 감지: {detector.get_section_summary(doc)}')
print(f'청크 수: {len(chunks)}')
for c in chunks[:3]:
    print(f'  [{c.section_type}] {c.content[:60]}...')
"
```

### 1-3. MODULE 13A CAD 단독 확인

```bash
python -c "
from modules.cad_decoder import CADDecoder, create_cad_processor
from modules.generator import Generator

gen = Generator()
processor = create_cad_processor(gen, query='이 논문의 방법론은?', alpha=0.5)
print('CAD processor 생성 성공:', type(processor))
"
```

### 1-4. MODULE 13B SCD 단독 확인

```bash
python -c "
from modules.scd_decoder import SCDDecoder, create_scd_processor

# Generator 없이 토크나이저만으로 테스트
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('BAAI/bge-m3')  # 이미 다운됐으면 빠름
scd = SCDDecoder(tokenizer=tok, beta=0.3)

# 비한국어 토큰 수 확인 (vocab의 일부가 패널티 대상)
scd._build_non_target_ids('cpu')
print(f'패널티 대상 토큰 수: {len(scd._non_target_ids)}')
print('SCD 초기화 성공')
"
```

---

## 2. 검색 품질 확인 (GPU 불필요)

논문 PDF 1편으로 검색 파이프라인 전체를 빠르게 확인합니다.

```bash
cd backend
python -c "
import sys
sys.path.insert(0, '.')
from modules.pdf_parser import PDFParser
from modules.section_detector import SectionDetector
from modules.chunker import Chunker
from modules.embedder import Embedder
from modules.vector_store import VectorStore
from modules.hybrid_retriever import HybridRetriever
from modules.reranker import Reranker

# 인덱싱
parser, detector, chunker = PDFParser(), SectionDetector(), Chunker()
embedder, vs = Embedder(), VectorStore()

doc = parser.parse('data/your_paper.pdf')   # PDF 경로 수정
doc = detector.detect(doc)
chunks = chunker.chunk_document(doc, strategy='section')
embeddings = embedder.embed_texts([c.content for c in chunks])
vs.add_chunks('test_col', chunks, embeddings)

# 검색
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

## 3. 3주차 체크포인트 — Language Drift 초기 실측

> GuideV2 §4.2: "한/영 쌍 10개로 초기 갭 + Language Drift 실측"  
> Drift 없으면 → 연구 설계 재조정 필요

```bash
cd backend
python -c "
from modules.generator import Generator
from evaluation.decoder_ablation import compute_language_drift_rate

gen = Generator()  # GPU 필요

# 영문 컨텍스트 + 한국어 질의 (Drift 재현 조건)
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

# Baseline (디코더 없음)
answers_baseline = []
for q in ko_queries:
    ans = gen.generate(query=q, context=en_context)
    answers_baseline.append(ans)
    print(f'Q: {q}')
    print(f'A (baseline): {ans[:100]}')
    print()

drift_rate = compute_language_drift_rate(answers_baseline)
print(f'Language Drift 이탈률 (baseline): {drift_rate:.1%}')
print('→ 이탈 있으면 SCD 효과 측정 가능 / 없으면 연구 설계 재검토')
"
```

---

## 4. Table 1 — 모듈별 갭 해소 기여도 (Ablation Study)

GuideV2 §5.1.2 기준. **가장 중요한 실험** — 시간이 가장 많이 걸립니다.

### 4-1. 테스트 쿼리 준비

`backend/evaluation/test_queries.json` 형식:

```json
[
  {
    "query": "이 논문의 핵심 기여는 무엇인가?",
    "ground_truth": "...",
    "lang": "ko",
    "paper_id": "attention_is_all_you_need"
  },
  {
    "query": "What is the main contribution of this paper?",
    "ground_truth": "...",
    "lang": "en",
    "paper_id": "attention_is_all_you_need"
  }
]
```

> **규모**: 논문 20편 × (한국어 5 + 영어 5) = 200쌍  
> **정답 생성**: GPT-4 API로 자동 생성 후 인간 검토  
> **수치 포함 질의**: 40% 이상 (CAD 효과 측정용)

### 4-2. Ablation Study 실행

```bash
cd backend
python -m evaluation.ablation_study
# → results/table1_ablation_*.json 생성
```

실행 시간 예상 (A100 기준):
- 논문 20편 인덱싱: ~30분
- Baseline 6개 × 200쌍: ~4~6시간

### 4-3. 결과 확인

```bash
python -c "
import json
with open('backend/results/table1_ablation_latest.json') as f:
    results = json.load(f)

print('='*60)
print('Table 1: 모듈별 갭 해소 기여도')
print('='*60)
print(f'{\"시스템\":<30} {\"EN\":>8} {\"KO\":>8} {\"갭(↓)\":>8}')
print('-'*60)
for name, r in results.items():
    en_score = r.get('en_answer_relevancy', 0)
    ko_score = r.get('ko_answer_relevancy', 0)
    gap = en_score - ko_score
    print(f'{name:<30} {en_score:>7.3f} {ko_score:>7.3f} {gap:>7.3f}')
"
```

---

## 5. Table 2 — CAD/SCD 조합 Ablation

GuideV2 §5.1.3 기준. **논문의 핵심 표** — C2 Contribution 직접 증명.

### 5-1. 기본 4개 구성 실험

```bash
cd backend
python -m evaluation.decoder_ablation
# → results/table2_decoder_ablation.json
```

출력 예시:
```
======================================================================
Table 2: CAD / SCD / 조합 Ablation
======================================================================
구성                                수치환각률  언어이탈률
----------------------------------------------------------------------
Baseline (no decoder)                   32.0%      45.0%
CAD only (α=0.5)                        18.0%      44.0%
SCD only (β=0.3)                        31.0%       8.0%
CAD+SCD (α=0.5, β=0.3)                 17.0%       7.0%
======================================================================
```

### 5-2. Alpha sweep (CAD 강도 최적화)

```bash
python -c "
import json, sys
sys.path.insert(0, 'backend')
from evaluation.decoder_ablation import DecoderAblationStudy
# ... (모듈 로드 후)
study.run_alpha_sweep(ko_samples)
# → results/table2_alpha_sweep.json
"
```

### 5-3. Beta sweep (SCD 강도 최적화)

```bash
python -m evaluation.decoder_ablation  # __main__ 블록에서 자동 실행
# → results/table2_beta_sweep.json
```

### 5-4. 실험 결과 해석 기준

| 결과 패턴 | 해석 | 논문 기술 방법 |
|---|---|---|
| CAD만 → 수치환각↓, 언어이탈 유지 | CAD 효과 확인 | "수치환각률 X%p 감소" |
| SCD만 → 수치환각 유지, 언어이탈↓ | SCD 효과 확인 | "언어이탈률 Y%p 감소" |
| CAD+SCD → 둘 다↓ | 상호보완 효과 | "두 모듈의 상호보완적 적용" |
| 효과 미미 | alpha/beta 조정 필요 | sweep 결과 참조 |

---

## 6. RAGAS 평가 (4대 지표)

```bash
cd backend
python -m backend.evaluation.ragas_eval
```

측정 지표:

| 지표 | 의미 | Table 1/2 |
|---|---|---|
| Answer Relevancy | 답변이 질의와 관련된 정도 | 둘 다 |
| Faithfulness | 답변이 컨텍스트에 근거한 정도 | 둘 다 |
| Context Precision | 검색 청크 중 관련 비율 | Table 1 |
| Context Recall | 필요 컨텍스트 검색 비율 | Table 1 |

> RAGAS는 내부적으로 LLM을 호출하므로 GPU 또는 OpenAI API 키 필요.

---

## 7. 남은 작업 체크리스트

GuideV2 기준으로 아직 미구현 또는 검증이 필요한 항목입니다.

### 🔴 필수 (논문 Contribution 직결)

- [ ] **test_queries.json 구성** — 논문 20편 × 200쌍 (한/영 각 100쌍)
  - GPT-4로 자동 생성 스크립트 작성 필요
  - 수치 포함 질의 40% 이상 포함
- [ ] **3주차 체크포인트 실행** — Language Drift 초기 실측 (섹션 3 참고)
  - Drift 확인 없으면 연구 설계 재조정
- [ ] **Table 1 실험 실행** — Baseline 1~5 + Full System 6개 구성
- [ ] **Table 2 실험 실행** — CAD/SCD/조합 + alpha/beta sweep
- [ ] **RAPTOR 청킹 (E경로)** — `chunker.py`에 `RAPTORChunker` 클래스 있으나 E경로와 연동 확인 필요
- [ ] **언어 이탈률 측정 함수 검증** — `decoder_ablation.py`의 30% 임계값이 MIDM에 적합한지 확인

### 🟡 중요 (시스템 완성도)

- [ ] **MIDM-2.0 프롬프트 템플릿 최적화** — `generator.py`의 현재 템플릿이 MIDM chat format에 맞는지 확인
  - MIDM-2.0-Base-Instruct의 공식 chat template 확인 필요
- [ ] **한→영 번역 쿼리 확장 (M7)** — `query_expander.py`에서 번역 API 또는 모델 확인
- [ ] **수치 환각률 측정 함수 정밀화** — 현재 단순 숫자 비교, 단위 포함 매칭으로 개선 가능
- [ ] **`evaluation/ablation_study.py` `_run_single_config()` 구현** — 실제 파이프라인 분기 로직 완성

### 🟢 선택 (포트폴리오 강화)

- [ ] **데모 영상 제작** — React UI 기반 시연
- [ ] **arXiv 논문 20편 자동 수집 스크립트** — `citation_tracker.py` 활용
- [ ] **React UI 데모 폴리싱** — Ablation 결과 시각화 추가

---

## 8. 빠른 확인 명령 모음

```bash
# 1. 모듈 임포트 전체 확인 (의존성 오류 사전 탐지)
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
print('모든 모듈 임포트 성공')
"

# 2. config 확인
python -c "
import sys; sys.path.insert(0,'backend')
import config
print('GENERATION_MODEL:', config.GENERATION_MODEL)
print('CAD_ALPHA:', config.CAD_ALPHA)
print('SCD_BETA:', config.SCD_BETA)
"

# 3. ChromaDB 상태 확인
python -c "
import sys; sys.path.insert(0,'backend')
from modules.vector_store import VectorStore
vs = VectorStore()
info = vs.get_collection_info('papers')
print('ChromaDB 청크 수:', info.get('count', 0))
"
```
