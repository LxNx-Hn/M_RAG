# 모듈러 RAG 기반 논문 리뷰 챗봇 에이전트
## 종합 설계 가이드라인 및 관련 연구 보고서

> 졸업작품 / 취업 포트폴리오 프로젝트
> 작성일: 2026년 4월

---

## 0. 프로젝트 개요

### 한 줄 요약

> **"범용 다국어 RAG에서 모듈별 한/영 질의 성능 갭을 정량 분해하고(Track 1), 논문 도메인에서 섹션 특화 모듈의 추가 효과를 실증한다(Track 2). CAD+SCD 조합으로 Language Drift와 파라메트릭 지식 개입을 동시 억제한다."**

---

### 세 가지 기여 (Contribution)

| # | 유형 | 내용 | 근거 |
|---|---|---|---|
| C1 | 분석 | 범용 + 논문 도메인에서 모듈별 갭 해소 기여도 정량 분해 | 선행 연구는 파이프라인 전체 or 2단계만 분리 |
| C2 | 알고리즘 | CAD+SCD 조합으로 두 문제 동시 억제 + alpha/beta ablation | CAD는 지식 억제, SCD는 언어 이탈 억제로 목적이 다름 |
| C3 | 시스템 | 오픈소스 모듈러 RAG 구현 및 공개 | 논문 도메인 특화 + 범용 동작 |

---

### 두 가지 생성 단계 문제와 해결책

```
문제 1 — 파라메트릭 지식 개입
  문서가 있어도 모델의 사전학습 기억이 개입
  → 수치 오류, 사실 왜곡 발생
  → CAD로 해결 (Shi et al., 2023) [3]

문제 2 — Language Drift
  영문 청크가 컨텍스트로 들어오면
  한국어 질의에도 영어로 답변하거나
  영어 구간을 우선 참조
  → SCD로 해결 (Li et al., 2025) [34]

두 모듈을 LogitsProcessor로 병렬 적용
→ 두 문제 동시 억제
```

---

### 직접 실험 vs 인용 대체

```
인용으로 대체:
  ✅ "언어 불일치 시 RAG 성능 저하"
     → Chirkova et al.(2024) [31], Park & Lee(2025) [32]
  ✅ "LLM은 언어별 환각률이 다르다"
     → mFAVA, Ul Islam et al.(2025) [30]
  ✅ "Language Drift 발생"
     → Li et al.(2025) [34]

직접 실험 (새로운 것):
  🔬 Table 1: 모듈별 갭 해소 기여도 Ablation (Track 1)
  🔬 Table 2: CAD/SCD 조합 Ablation
  🔬 Table 3: 논문 도메인 특화 모듈 추가 효과 (Track 2)
```

---

### 기술 스택

| 구분 | 기술 | 비고 |
|---|---|---|
| PDF 파싱 | pymupdf | 속도, 레이아웃 보존 |
| 임베딩 | BGE-M3 | 한영 크로스링구얼 |
| 벡터DB | ChromaDB | 로컬, 메타데이터 필터 |
| 생성 모델 | MIDM-2.0 Base (11.5B) | KT 한국 중심 AI |
| 환각 억제 | CAD + SCD | 학습 불필요 |
| 평가 | RAGAS | RAG 특화 자동 평가 |
| API | FastAPI | 인증, 업로드, 질의응답, SSE, Judge, PPT Export |
| UI | React + Vite | 논문 업로드, 채팅, PDF 뷰어, 결과 확인 |
| 실험 자동화 | master_run.py | SQLite + SQLAlchemy 기반 전체 실험 실행 |
| GPU | RunPod/Alice A100 | MIDM Base 기반 실험 추론 |

### 현재 코드 반영 요약

이 문서는 사용자 제공 35편 기준 설계안을 원형으로 유지하되, 현재 저장소 코드 기준으로 다음 사항을 보정한다.

| 항목 | 현재 코드 기준 |
|---|---|
| 연구 핵심 모듈 | 13개 |
| 확장/운영 모듈 | 5개 |
| 전체 모듈 파일 | 18개 |
| 파이프라인 | A~F 6개 |
| 운영 대화 기능 | follow-up 질문, F 퀴즈/플래시카드 생성 |
| 제품/운영 기능 | PPT Export, Search API, Judge API, SSE 스트리밍 |
| 논문 기본 모델 | MIDM Base |
| 로컬 스모크 모델 | MIDM Mini |
| 논문 실험 DB | SQLite + SQLAlchemy |
| 운영/서비스 DB | PostgreSQL + SQLAlchemy |

13개 연구 핵심 모듈은 논문 클레임과 ablation의 중심이 되는 모듈이다. 18개 전체 모듈 파일은 연구 핵심 모듈과 입력 처리, 저장소, 특허 추적, PPT 내보내기 모듈을 합친 현재 구현 단위다.

연구 핵심 13개 모듈

- `embedder.py`
- `chunker.py`
- `reranker.py`
- `hybrid_retriever.py`
- `query_router.py`
- `section_detector.py`
- `generator.py`
- `cad_decoder.py`
- `scd_decoder.py`
- `context_compressor.py`
- `query_expander.py`
- `citation_tracker.py`
- `followup_generator.py`

확장/운영 5개 모듈

- `pdf_parser.py`
- `docx_parser.py`
- `patent_tracker.py`
- `pptx_exporter.py`
- `vector_store.py`

```python
# MIDM-2.0 로드 (transformers >= 4.45.0)
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch

model = AutoModelForCausalLM.from_pretrained(
    "K-intelligence/Midm-2.0-Base-Instruct",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(
    "K-intelligence/Midm-2.0-Base-Instruct"
)
```

---

## 1. 배경 및 연구 동기

### 1.1 RAG 패러다임의 진화

| 패러다임 | 구조 | 한계 |
|---|---|---|
| Naive RAG | 고정 파이프라인: 청킹→검색→생성 | 모든 질의가 같은 경로 |
| Advanced RAG | 사전/사후 검색 최적화 추가 | 순차적 고정 구조 |
| **Modular RAG** | 쿼리 유형에 따라 파이프라인 동적 변경 | 본 프로젝트 |

### 1.2 선행 연구가 확립한 사실 (인용으로 대체)

**사실 1: LLM은 언어별 환각률이 다르다**
→ mFAVA [30]: 30개 언어 × 11개 LLM에서 실증

**사실 2: 다국어 RAG에서 언어 불일치 시 성능 저하**
→ Chirkova et al.(2024) [31]: 13개 언어 mRAG 실험
→ Park & Lee(2025) [32]: 한국어 포함 언어 선호도 측정, 표 직접 인용 가능

**사실 3: Language Drift 발생**
→ Li et al.(2025) [34]: 영어가 의미적 끌개로 작용함을 실증

### 1.3 선행 연구의 한계 (본 연구가 채울 것)

```
공통 한계:
  - 파이프라인 전체 or 검색/생성 2단계만 분리
  - 모듈 단위 기여도 분해 없음
  - 범용 다국어 LLM 사용 (한국어 특화 LLM 없음)

추가 한계:
  - SCD [34]: Language Drift만 억제, 지식 개입 미해결
  - CAD [3]: 지식 개입만 억제, Language Drift 미해결
```

### 1.4 Modular RAG 정의

> 쿼리 유형에 따라 **어떤 모듈을 어떤 순서로 실행할지가 동적으로 결정**되는 시스템.
> 핵심은 쿼리 라우터(MODULE 6). 없으면 그냥 파이프라인.

```
❌ 파이프라인: 모든 질의 → 고정 순서 실행
✅ Modular RAG: 질의 유형 → 경로 선택 → 해당 모듈 조합 활성화
```

---

## 2. 관련 연구 (35편)

| # | 논문 | Venue | arXiv | 역할 |
|---|---|---|---|---|
| 1 | Gao et al. — RAG Survey | ICLR 2024 | 2312.10997 | 전체 설계 |
| 2 | Chen et al. — BGE M3 | ACL 2024 | 2402.03216 | MODULE 4 |
| 3 | Shi et al. — CAD | NAACL 2024 | 2305.14739 | MODULE 13A |
| 4 | Li et al. — Contrastive Decoding | ACL 2023 | 2210.15097 | MODULE 13A 기반 |
| 5 | Sarthi et al. — RAPTOR | ICLR 2024 | 2401.18059 | MODULE 3 |
| 6 | Gao et al. — HyDE | ACL 2023 | 2212.10496 | MODULE 7 |
| 7 | Asai et al. — Self-RAG | ICLR 2024 | 2310.11511 | MODULE 6 |
| 8 | Yan et al. — CRAG | ICLR 2024 | 2401.15884 | MODULE 8 |
| 9 | Edge et al. — GraphRAG | EMNLP 2024 | 2404.16130 | MODULE 11 |
| 10 | Es et al. — RAGAS | EACL 2024 | 2309.15217 | 평가 프레임워크 |
| 11 | Jiang et al. — LLMLingua | EMNLP 2023 | 2310.05736 | MODULE 10 |
| 12 | Jiang et al. — LongLLMLingua | ACL 2024 | 2310.06839 | MODULE 10 |
| 13 | Wang et al. — Best Practices RAG | arXiv 2024 | 2407.01219 | MODULE 8 |
| 14 | Santhanam et al. — ColBERTv2 | NAACL 2022 | 2112.01488 | MODULE 9 |
| 15 | Jha et al. — Jina-ColBERT-v2 | MRL 2024 | 2408.16672 | MODULE 9 |
| 16 | Wang et al. — Speculative RAG | arXiv 2024 | 2407.08223 | MODULE 12 |
| 17 | Jiang et al. — FLARE | EMNLP 2023 | 2305.06983 | MODULE 6 |
| 18 | Shao et al. — ITER-RETGEN | EMNLP 2023 | 2305.15294 | MODULE 6 |
| 19 | Xu et al. — RECOMP | ICLR 2024 | 2310.04408 | MODULE 10 |
| 20 | Lewis et al. — RAG Original | NeurIPS 2020 | 2005.11401 | 전체 기반 |
| 21 | Khattab & Zaharia — ColBERT | SIGIR 2020 | 2004.12832 | MODULE 9 |
| 22 | Robertson et al. — BM25 | TREC 1994 | — | MODULE 8 |
| 23 | Cormack et al. — RRF | SIGIR 2009 | — | MODULE 8 |
| 24 | Chen et al. — Dense-X Retrieval | arXiv 2023 | 2312.06648 | MODULE 3 |
| 25 | Trivedi et al. — IRCoT | ACL 2023 | 2212.10509 | MODULE 6 |
| 26 | Rackauckas — RAG-Fusion | arXiv 2024 | 2402.03367 | MODULE 7 |
| 27 | Gutiérrez et al. — HippoRAG2 | arXiv 2025 | 2502.14802 | MODULE 11 |
| 28 | Zhong et al. — Meta-Chunking | arXiv 2024 | 2410.12788 | MODULE 3 |
| 29 | Liu et al. — Lost in the Middle | TACL 2024 | 2307.03172 | MODULE 9 |
| 30 | Ul Islam et al. — mFAVA | EMNLP 2025 | 2502.12769 | 배경: 언어별 환각률 |
| 31 | Chirkova et al. — mRAG | KnowLLM@ACL 2024 | 2407.01463 | 배경: 언어 불일치 성능 저하 |
| 32 | Park & Lee — Language Preference | ACL 2025 Findings | 2502.11175 | 배경: 표 직접 인용 |
| 33 | Ranaldi et al. — Multilingual RAG | arXiv 2025 | 2504.03616 | 다국어 RAG 전략 비교 |
| 34 | Li et al. — Language Drift & SCD | arXiv 2025 | 2511.09984 | MODULE 13B |
| 35 | Rau et al. — BERGEN | arXiv 2024 | 2407.01102 | mRAG 벤치마킹 기반 |

---

## 3. 시스템 아키텍처 (13개 연구 핵심 모듈 + 5개 확장 모듈)

### 3.1 전체 구조

```
                    ┌─────────────────────────┐
PDF 업로드 ────────▶│     공통 인덱싱 레이어   │
                    │  MODULE 1: PDF 파서      │
                    │  MODULE 2: 섹션 인식기   │
                    │  MODULE 3: 청킹          │
                    │  MODULE 4: BGE-M3        │ ← Table 1 측정점
                    │  MODULE 5: ChromaDB      │
                    └──────────┬──────────────┘
                               │
한/영 질의 ────────────────────▼
                    ┌─────────────────────────┐
                    │  MODULE 6: 쿼리 라우터  │ ★ Modular RAG 핵심
                    └──┬──┬──┬──┬──┬─────────┘
              A경로  B  C  D  E  F
                    ┌──▼──────────────────────┐
                    │  경로별 파이프라인       │
                    │  A 단순 QA               │
                    │  B 섹션 특화             │
                    │  C 문서 비교             │
                    │  D 인용/특허 추적         │ ← MODULE 11
                    │  E 전체 요약             │
                    │  F 퀴즈/플래시카드        │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  MODULE 7: 쿼리 확장     │
                    │  MODULE 8: 하이브리드    │ ← Table 1 측정점
                    │  MODULE 9: 재랭커        │ ← Table 1 측정점
                    │  MODULE 10: 컨텍스트 압축 │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  MODULE 12: MIDM-2.0    │
                    │  MODULE 13A: CAD        │ ← Table 2 측정점
                    │  MODULE 13B: SCD        │ ← Table 2 측정점
                    └─────────────────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  답변/출처/후속질문       │
                    └─────────────────────────┘

운영 API
  Search API: 검색 결과 점검
  Judge API: 실험 평가 라벨 생성
  PPT Export: 답변과 출처를 발표 자료로 변환
```

### 3.2 경로별 활성화 모듈

| 경로 | 트리거 | 활성화 모듈 | 비활성화 |
|---|---|---|---|
| A. 단순 QA | 일반 질문 | 4,5,7,8,9,12,13A,13B | 11 |
| B. 섹션 특화 | "결과", "방법론" | 4,5,8(섹션필터),9,12,13A,13B | 7,11 |
| C. 멀티 논문 비교 | "비교", "vs" | 4,5,8(병렬),합성,12,13A,13B | 7,9,11 |
| D. 인용 트래커 | "인용", "reference" | 4,5,11,8(확장),12,13A,13B | 7,9 |
| E. 전체 요약 | "요약" | 3(RAPTOR),4,5,10,12,13A,13B | 7,9,11 |
| F. 퀴즈/플래시카드 | "퀴즈", "문제", "flashcard" | 4,5,8,9,12,13A,13B | 7,11 |

현재 파이프라인 파일은 `backend/pipelines/pipeline_a_simple_qa.py`부터 `pipeline_f_quiz.py`까지 6개다. F 경로는 논문 리뷰 챗봇의 학습형 질문 생성 경로이며, 운영 대화 기능 문서와 시연 문서에서 중심적으로 다룬다.

질문 생성 계층은 두 부분으로 나뉜다.

| 기능 | 코드 위치 | 분류 |
|---|---|---|
| 후속 질문 생성 | `backend/modules/followup_generator.py` | 독립 핵심 모듈 |
| 퀴즈/플래시카드 생성 | `backend/pipelines/pipeline_f_quiz.py` | F 경로 내부 생성 로직 |

퀴즈/플래시카드 생성의 구현 단위는 `pipeline_f_quiz.py`다. 이 파일이 검색, 재랭킹, 압축, 퀴즈 프롬프트, 생성을 묶어 F 경로를 실행한다.

### 3.3 핵심 모듈 명세

---

#### MODULE 3: 청킹 `chunker.py`
기반: **RAPTOR** [5], **Dense-X** [24], **Meta-Chunking** [28]

| 전략 | 설명 | 활성 경로 | 트랙 |
|---|---|---|---|
| 섹션 단위 | 섹션 경계 유지 | A,B,C,D | Track 1+2 |
| 명제 단위 | 원자적 사실 단위 | B | Track 1+2 |
| RAPTOR 계층 | 클러스터→요약→트리 | E | **Track 2 핵심** |

---

#### MODULE 4: 임베딩 `embedder.py` ★ Table 1 핵심
기반: **BGE M3-Embedding** [2]

```python
# 한영 동일 임베딩 공간
# Baseline 2→3 구간에서 갭 변화 가장 클 것으로 예상
model = SentenceTransformer("BAAI/bge-m3")
```

---

#### MODULE 6: 쿼리 라우터 `query_router.py` ★ Modular RAG 핵심
기반: **Self-RAG** [7], **FLARE** [17], **CRAG** [8]

```python
ROUTE_MAP = {
    "section_result": ["결과", "성능", "result", "accuracy"],
    "section_method": ["방법론", "method", "approach"],
    "section_limit":  ["한계", "limitation", "future work"],
    "compare":        ["비교", "vs", "compare"],
    "citation":       ["인용", "reference", "cited"],
    "summary":        ["요약", "summarize", "overview"],
}

def route(query: str) -> str:
    for route_name, keywords in ROUTE_MAP.items():
        if any(kw in query.lower() for kw in keywords):
            return route_name
    return llm_classify(query)  # 불명확 시 LLM 분류
```

---

#### MODULE 8: 하이브리드 검색기 `hybrid_retriever.py`
기반: **Best Practices** [13], **BM25** [22], **RRF** [23]

```python
def retrieve(query, route, section_filter=None, docs=None):
    if route == "section_b":
        # 경로 B: 섹션 필터 (Track 2 핵심)
        return vector_search(query, filter={"section_type": section_filter})
    elif route == "compare":
        # 경로 C: 병렬 검색
        return [vector_search(query, filter={"doc_id": d}) for d in docs]
    else:
        # 경로 A/D/E: BM25 + 벡터 + RRF
        return rrf(vector_search(query), bm25_search(query))
```

---

#### MODULE 13A: CAD `cad_decoder.py`
기반: **CAD** [3], **Contrastive Decoding** [4]

**목적: 파라메트릭 지식 개입 억제**

$$\text{Logit}_{\text{CAD}} = \text{Logit}(\text{문서 포함}) - \alpha \cdot \text{Logit}(\text{문서 없음})$$

문서 없음 경로는 질문 단독 입력을 사용한다. CAD가 활성화된 생성은 greedy decoding으로 수행한다.

```python
from transformers import LogitsProcessor
import torch

class CADDecoder(LogitsProcessor):
    def __init__(self, model, empty_input_ids, alpha=0.5):
        self.model = model
        self.empty_input_ids = empty_input_ids
        self.alpha = alpha  # Grid Search 대상

    def __call__(self, input_ids, scores):
        with torch.no_grad():
            empty_logits = self.model(
                self.empty_input_ids
            ).logits[:, -1, :]
        return scores - self.alpha * empty_logits
```

---

#### MODULE 13B: SCD `scd_decoder.py`
기반: **Language Drift & SCD** [34]

**목적: Language Drift 억제 (영문 컨텍스트 입력 시 한국어 답변 강제)**

```python
class SCDDecoder(LogitsProcessor):
    def __init__(self, tokenizer, target_lang="ko", beta=0.3):
        self.tokenizer = tokenizer
        self.beta = beta  # Grid Search 대상
        self.non_target_ids = self._get_non_korean_ids()

    def _get_non_korean_ids(self):
        non_target = []
        for token_id in range(self.tokenizer.vocab_size):
            token = self.tokenizer.decode([token_id])
            if token and not self._is_korean_or_common(token):
                non_target.append(token_id)
        return torch.tensor(non_target)

    def _is_korean_or_common(self, token):
        for ch in token:
            code = ord(ch)
            if not (0xAC00 <= code <= 0xD7A3 or
                    0x1100 <= code <= 0x11FF or
                    ch in ' \n\t.,!?()[]{}:;"\'-0123456789'):
                return False
        return True

    def __call__(self, input_ids, scores):
        if len(self.non_target_ids) > 0:
            scores[:, self.non_target_ids] -= self.beta
        return scores
```

---

#### MODULE 13 병렬 적용

```python
cad = CADDecoder(model, empty_input_ids, alpha=0.5)
scd = SCDDecoder(tokenizer, target_lang="ko", beta=0.3)

output = model.generate(
    input_ids.to("cuda"),
    generation_config=generation_config,
    logits_processor=[cad, scd],  # 병렬 적용
    max_new_tokens=512,
)
```

| | CAD [3] | SCD [34] |
|---|---|---|
| 억제 대상 | 파라메트릭 지식 개입 | 비목표 언어 토큰 |
| 해결 문제 | 수치 오류, 사실 왜곡 | Language Drift |
| 파라미터 | alpha | beta |

---

## 4. 개발 섹션

### 4.1 개발 / 실험 / 논문 완전 분리 원칙

```
개발 (1~8주차): 시스템 구현에만 집중
               데이터셋은 다운로드만, 건드리지 않음

실험 (9~10주차): 구현 완료 후 데이터셋 투입
                RAGAS 자동 평가로 Table 생성

논문 (11~12주차): 결과 해석 + 보고서 작성
```

### 4.2 개발 원칙

```
원칙 1 — 모듈 독립성: 각 모듈 on/off 가능 → Ablation 필수 조건
원칙 2 — 경로 분리: pipelines/ 폴더에 경로별 파일 분리
원칙 3 — 실험 재현성: 모든 결과 JSON 자동 저장
원칙 4 — 한/영 쌍 강제: 동일 질의를 항상 한/영 쌍으로 실행
```

### 4.3 개발 로드맵 (1~8주차)

#### Phase 1 — Core 파이프라인 (1~3주차)

**1주차:**
```bash
pip install pymupdf chromadb sentence-transformers
pip install transformers>=4.45.0 ragas datasets
```
- MODULE 1, 2 구현 (PDF 파서, 섹션 인식기)
- 검증: 논문 5편 섹션 감지 수동 확인

**2주차:**
- MODULE 3 (섹션 단위 청킹)
- MODULE 4 (BGE-M3 임베딩)
- MODULE 5 (ChromaDB)
- 검증: 한국어 쿼리 → 영문 청크 검색 확인

**3주차:**
- MODULE 12 (MIDM-2.0 생성)
- Baseline 1 완성

> **⚠️ 3주차 체크포인트**: 8개 문서 샘플 쿼리로 초기 갭 + Language Drift 실측
> 갭 + Drift 확인 → Phase 2 진행 / 없으면 → 설계 재조정

---

#### Phase 2 — Modular RAG 핵심 (4~5주차)

**4주차:**
- MODULE 8 (하이브리드 검색 + RRF)
- MODULE 9 (ColBERT 재랭커)
- Baseline 2, 3, 4 순차 완성

**5주차:**
- MODULE 6 (쿼리 라우터) ★
- MODULE 7 (HyDE + 다중 쿼리)
- Baseline 5 완성
- pipelines/ 경로별 파일 분리

---

#### Phase 3 — 킬러 기능 (6~8주차)

**6주차:**
- MODULE 3 확장: RAPTOR 계층 요약 트리
- Dense-X 명제 단위 청킹

**7주차:**
- MODULE 11 (인용 트래커 + arXiv API)
- 경로 D 파이프라인 완성

**8주차:**
- MODULE 13A (CAD 구현)
- MODULE 13B (SCD 구현)
- MODULE 10 (LLMLingua + RECOMP)
- Full System 완성

---

### 4.4 프로젝트 구조

```
M_RAG/
├── backend/
│   ├── api/                      # FastAPI, auth, SQLAlchemy models, routers
│   ├── modules/                  # 연구 핵심 13 + 확장 5 모듈
│   ├── pipelines/                # A~F 질의 경로
│   ├── evaluation/               # Track 1/2, RAGAS, decoder ablation
│   ├── scripts/                  # master_run, 모델/PDF 준비, 표 변환
│   └── data/                     # 실험 PDF 입력
├── frontend/                     # React + Vite UI
├── docs/
│   ├── PAPER/                    # 논문, 기준 설계, PPT 요약
│   ├── EXPLAIN/                  # 비전공자용 상세 설명
│   └── USAGE/                    # 실행, 배포, 테스트, DB 문서
└── README.md
```

현재 구현의 전체 API와 코드 지도는 저장소 루트 `README.md`, 세부 구조는 `docs/ARCHITECTURE.md`를 기준으로 한다.

---

## 5. 실험 섹션 (9~10주차)

### 5.1 데이터셋 구성

#### Track 1 — 8개 문서 기반 모듈 검증

현재 Alice 실행 기준 코퍼스는 다음 8개 문서다.

| doc_id | 역할 |
|---|---|
| `paper_nlp_bge` | BGE M3-Embedding |
| `paper_nlp_rag` | RAG Survey |
| `paper_nlp_cad` | CAD |
| `paper_nlp_raptor` | RAPTOR |
| `paper_midm` | MIDM-2.0 Technical Report |
| `paper_ko_rag_eval_framework` | 한국어 RAG 평가 프레임워크 |
| `paper_ko_rag_rrf_chunking` | 한국어 RAG RRF/청킹 |
| `paper_ko_cad_contrastive` | 한국어 CAD 대조적 디코딩 |

Track 1은 8개 문서에 대해 논문별 특화 쿼리로 구성한다. 기본 쿼리는 한국어로 생성하고, `crosslingual_en` 타입만 영어 대조군으로 둔다.

---

#### Track 2 — 논문 도메인 특화

Track 2는 `paper_nlp_bge`, `paper_nlp_rag`, `paper_nlp_cad`, `paper_nlp_raptor` 네 편을 대상으로 한다. 쿼리는 28개이며, cad_ablation, section_method, section_abstract, citation 유형을 유지한다.

---

### 5.2 실험 Table 구조

#### Table 1: 모듈별 갭 해소 기여도 (Track 1, 직접 실험)

| 시스템 | EN 질의 | KO 질의 | 갭(↓) | Faithfulness | 언어이탈률 |
|---|---|---|---|---|---|
| Baseline 1 (naive RAG) | — | — | — | — | — |
| Baseline 2 (+섹션 청킹) | — | — | — | — | — |
| Baseline 3 (+BGE-M3) | — | — | **↓ 최대 예상** | — | — |
| Baseline 4 (+하이브리드) | — | — | — | — | — |
| Baseline 5 (+재랭커+라우터) | — | — | — | — | — |
| Full System (+CAD+SCD) | — | — | **↓ 최소** | — | **↓ 최소** |

> Baseline 2→3 구간(BGE-M3 교체)에서 갭 최대 감소 예상.
> 실제 숫자는 실험 후 채워짐.

---

#### Table 2: CAD/SCD 조합 Ablation (Track 1, 직접 실험)

**조합 비교:**

| 시스템 | 수치환각률 | 언어이탈률 | Faithfulness | Answer Relevancy |
|---|---|---|---|---|
| 디코더 없음 | — | — | — | — |
| CAD만 (α=0.5) | **↓** | — | ↑ | — |
| SCD만 (β=0.3) | — | **↓** | — | — |
| CAD+SCD | **↓↓** | **↓↓** | ↑↑ | — |

**Alpha Grid Search (CAD):**

```python
alphas = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
betas  = [0.1, 0.3, 0.5]

# 18개 조합 × 200쌍 = 3,600회 추론
# RunPod A100 기준 약 2~3일
for alpha, beta in itertools.product(alphas, betas):
    result = evaluate(cad_alpha=alpha, scd_beta=beta)
    save_to_json(result)
```

| alpha | 수치환각률 | Faithfulness | Answer Relevancy |
|---|---|---|---|
| 0.0 | — | — | — |
| 0.1 | — | — | — |
| 0.3 | — | — | — |
| 0.5 | — | — | — |
| 0.7 | — | — | — |
| 1.0 | — | — | — |

**Beta Grid Search (SCD):**

| beta | 언어이탈률 | Answer Relevancy |
|---|---|---|
| 0.1 | — | — |
| 0.3 | — | — |
| 0.5 | — | — |

---

#### Table 3: 논문 도메인 특화 모듈 추가 효과 (Track 2, 직접 실험)

| 시스템 | Faithfulness | Context Precision | Answer Relevancy |
|---|---|---|---|
| 범용 RAG (Track 1 Full System) | — | — | — |
| +섹션 인식 청킹 (논문 특화) | ↑ | ↑ | — |
| +쿼리 라우터 섹션 필터 | ↑↑ | ↑↑ | — |
| +RAPTOR 계층 검색 | — | — | ↑ |
| +인용 트래커 | — | ↑ | ↑ |
| Full Track 2 System | ↑↑↑ | ↑↑↑ | ↑↑ |

> "논문 도메인에서 섹션 인식 청킹이 범용 청킹 대비 X% 향상"
> → 논문 도메인 특화의 정당성 확보

---

### 5.3 평가 지표

| 지표 | 측정 대상 | 사용 Table |
|---|---|---|
| Answer Relevancy | 답변-질의 관련도 | Table 1, 2, 3 |
| Faithfulness | 답변-컨텍스트 근거 비율 | Table 1, 2, 3 |
| Context Precision | 검색 청크 중 관련 비율 | Table 1, 3 |
| Context Recall | 필요 컨텍스트 검색 비율 | Table 1, 3 |
| 수치 환각률 | 수치 오류 포함 답변 비율 | Table 2 |
| 언어 이탈률 | 한국어 질의에 비한국어 답변 비율 | Table 2 |

---

## 6. 논문 작성 섹션 (11~12주차)

### 6.1 논문 구조

```
1. Introduction         (1.5p)
   - 배경: mFAVA [30], Chirkova [31], Park&Lee [32] 인용
   - 두 문제: Language Drift + 파라메트릭 지식 개입
   - "모듈별 분해 없었다" 갭 지적
   - C1, C2, C3 bullet

2. Related Work         (1p)
   - mRAG 선행 연구 [31, 32, 33, 35]
   - 언어별 환각률 [30]
   - 디코딩 개입 기법 [3, 4, 34]

3. System Design        (2p)
   - Modular RAG 구조 (쿼리 라우터 중심)
   - CAD + SCD 병렬 적용
   - 경로별 활성화 모듈 표

4. Experiments          (2.5p)
   - Table 0: 선행 연구 갭 인용 [31, 32]
   - Table 1: 모듈별 Ablation (Track 1)
   - Table 2: CAD/SCD Ablation
   - Table 3: 논문 도메인 특화 효과 (Track 2)

5. Conclusion           (0.5p)
   - Track 1: 범용 일반화 주장
   - Track 2: 논문 도메인 특화 효과
   - 한계 및 향후 연구
```

### 6.2 핵심 포지셔닝 문장

**Track 1 → Track 2 전환:**
```
"Track 1에서 범용 다국어 RAG 설정으로
 모듈별 갭 해소 기여도를 검증한 뒤,
 Track 2에서 논문 도메인 특화 모듈
 (섹션 인식 청킹, RAPTOR, 인용 트래커)의
 추가 효과를 실증한다."
```

**CAD + SCD 조합 포지셔닝:**
```
"SCD [34]는 Language Drift를 억제하나
 파라메트릭 지식 개입은 다루지 않는다.
 CAD [3]는 반대다. 본 연구는 두 기법을
 조합하여 Table 2에서 상호보완 효과를 실증한다."
```

**최적값 한계 명시:**
```
"실험 범위 내 최적 alpha, beta 값은
 이 데이터셋과 도메인에 특화된
 경험적 값이며, 타 도메인 적용 시
 재조정이 필요할 수 있다."
```

### 6.3 주의할 표현

| 쓰면 안 되는 표현 | 대신 쓸 표현 |
|---|---|
| "Language Drift를 최초 발견" | Li et al.(2025) 인용 |
| "언어 갭이 존재한다" | 선행 연구 [31, 32] 인용 |
| "최적값이다" | "실험 범위 내 경험적 최적값" |
| "모든 환각 해결" | "X%p 감소" |

### 6.4 한계 솔직하게 쓰기

```
Limitations:
- alpha, beta 최적값은 이 설정에 특화된 경험적 값
- CAD+SCD 병렬 적용으로 추론 속도 약 2배 감소
- SCD의 한국어 판별이 음절 기반
  (영어 전문용어 억제 가능성)
- Track 1은 자동 생성 쿼리 품질이 실험에 영향을 줄 수 있음
- Track 2는 4편의 NLP 논문 샘플
- 한국어 원문 논문 확장은 후속 재실험에서 보강
```

---

### 6.5 면접 Q&A

```
Q: 선행 연구랑 뭐가 달라요?
A: Chirkova(2024), Park&Lee(2025)가 언어 갭을
   확인했지만 모듈별 분해는 없었습니다.
   저는 13개 모듈 단위로 분해했고,
   BGE-M3 교체 시 갭이 가장 크게 줄었습니다.
   또한 CAD+SCD 조합으로 두 문제를 동시에 잡았습니다.

Q: Track 1이랑 Track 2를 나눈 이유가 뭔가요?
A: 시스템이 논문 도메인이 아니어도 동작하는 걸
   먼저 보이고 (Track 1 범용 검증),
   그 위에서 논문 도메인 특화 모듈이
   추가로 얼마나 효과적인지 보였습니다 (Track 2).
   일반성과 특수성을 동시에 주장할 수 있습니다.

Q: CAD랑 SCD 같이 쓰는 이유가 뭔가요?
A: 역할이 다릅니다. CAD는 모델의 사전학습 기억
   개입을 막고, SCD는 영문 컨텍스트가 들어와도
   한국어로 답하게 강제합니다.
   Table 2에서 둘을 각각 썼을 때와 같이 썼을 때를
   비교해서 상호보완 효과를 보였습니다.
```

---

## 7. 참고 문헌

[1] Gao, Y. et al. (2023). *RAG Survey.* ICLR 2024. arXiv:2312.10997

[2] Chen, J. et al. (2024). *BGE M3-Embedding.* ACL 2024. arXiv:2402.03216

[3] Shi, W. et al. (2023). *Context-Aware Decoding (CAD).* NAACL 2024. arXiv:2305.14739

[4] Li, X. et al. (2022). *Contrastive Decoding.* ACL 2023. arXiv:2210.15097

[5] Sarthi, P. et al. (2024). *RAPTOR.* ICLR 2024. arXiv:2401.18059

[6] Gao, L. et al. (2022). *HyDE.* ACL 2023. arXiv:2212.10496

[7] Asai, A. et al. (2023). *Self-RAG.* ICLR 2024. arXiv:2310.11511

[8] Yan, S. et al. (2024). *CRAG.* ICLR 2024. arXiv:2401.15884

[9] Edge, D. et al. (2024). *GraphRAG.* EMNLP 2024. arXiv:2404.16130

[10] Es, S. et al. (2023). *RAGAS.* EACL 2024. arXiv:2309.15217

[11] Jiang, H. et al. (2023). *LLMLingua.* EMNLP 2023. arXiv:2310.05736

[12] Jiang, H. et al. (2023). *LongLLMLingua.* ACL 2024. arXiv:2310.06839

[13] Wang, X. et al. (2024). *Best Practices in RAG.* arXiv:2407.01219

[14] Santhanam, K. et al. (2022). *ColBERTv2.* NAACL 2022. arXiv:2112.01488

[15] Jha, R. et al. (2024). *Jina-ColBERT-v2.* MRL 2024. arXiv:2408.16672

[16] Wang, Z. et al. (2024). *Speculative RAG.* arXiv:2407.08223

[17] Jiang, Z. et al. (2023). *FLARE.* EMNLP 2023. arXiv:2305.06983

[18] Shao, Z. et al. (2023). *ITER-RETGEN.* EMNLP 2023. arXiv:2305.15294

[19] Xu, F. et al. (2023). *RECOMP.* ICLR 2024. arXiv:2310.04408

[20] Lewis, P. et al. (2020). *RAG Original.* NeurIPS 2020. arXiv:2005.11401

[21] Khattab, O. & Zaharia, M. (2020). *ColBERT.* SIGIR 2020. arXiv:2004.12832

[22] Robertson, S. et al. (1994). *BM25.* TREC 1994.

[23] Cormack, G. et al. (2009). *Reciprocal Rank Fusion.* SIGIR 2009.

[24] Chen, T. et al. (2023). *Dense-X Retrieval.* arXiv:2312.06648

[25] Trivedi, H. et al. (2022). *IRCoT.* ACL 2023. arXiv:2212.10509

[26] Rackauckas, A. (2024). *RAG-Fusion.* arXiv:2402.03367

[27] Gutiérrez, B.J. et al. (2025). *HippoRAG2.* arXiv:2502.14802

[28] Zhong, Q. et al. (2024). *Meta-Chunking.* arXiv:2410.12788

[29] Liu, N.F. et al. (2023). *Lost in the Middle.* TACL 2024. arXiv:2307.03172

[30] Ul Islam, S.O. et al. (2025). *mFAVA.* EMNLP 2025. arXiv:2502.12769

[31] Chirkova, N. et al. (2024). *RAG in Multilingual Settings.* KnowLLM@ACL 2024. arXiv:2407.01463

[32] Park, J. & Lee, H. (2025). *Language Preference of Multilingual RAG.* ACL 2025 Findings. arXiv:2502.11175

[33] Ranaldi, L. et al. (2025). *Multilingual RAG.* arXiv:2504.03616

[34] Li, B. et al. (2025). *Language Drift in Multilingual RAG & SCD.* arXiv:2511.09984

[35] Rau, D. et al. (2024). *BERGEN: Benchmarking Library for RAG.* arXiv:2407.01102

---

> 본 보고서는 프로젝트 진행에 따라 지속 업데이트됩니다.
