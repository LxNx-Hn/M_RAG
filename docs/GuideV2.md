# 모듈러 RAG 기반 논문 리뷰 챗봇 에이전트
## 종합 설계 가이드라인 및 관련 연구 보고서

> 졸업작품 / 취업 포트폴리오 프로젝트  
> 작성일: 2026년 4월

---

## 0. 프로젝트 개요

### 한 줄 요약

> **"영문 논문 도메인 RAG에서 한/영 질의 성능 갭을 모듈별로 정량 분해하고, Language Drift(SCD)와 파라메트릭 지식 개입(CAD)을 동시에 억제하여 한국어 질의 성능을 개선한다."**

### 세 가지 기여 (Contribution)

| # | 유형 | 내용 | 선행 연구와의 차이 |
|---|---|---|---|
| C1 | 분석 | 영문 논문 도메인 + MIDM-2.0에서 모듈별 갭 해소 기여도 정량 분해 | 기존은 전체 파이프라인 or 검색/생성 2단계만 분리 |
| C2 | 알고리즘 | CAD + SCD 조합으로 Language Drift와 파라메트릭 지식 개입을 동시 억제 | 기존 SCD [34]는 언어 이탈만, CAD [3]는 지식 억제만 |
| C3 | 시스템 | C1+C2를 통합한 오픈소스 모듈러 RAG 구현 | 논문 도메인 특화, MIDM-2.0 기반 |

### 두 가지 생성 단계 문제와 해결책

```
문제 1: Language Drift
  영문 청크가 컨텍스트로 들어오면
  MIDM-2.0이 영어로 답변하거나
  한국어 답변 중 영어 구간을 무시함
  → SCD로 해결: 비목표 언어 토큰 패널티

문제 2: 파라메트릭 지식 개입
  문서 내용이 있어도 모델의 사전학습
  기억이 개입하여 수치/사실 오류 발생
  → CAD로 해결: 문서 없는 logit과의 차이 억제

두 모듈을 LogitsProcessor로 병렬 적용
```

### 직접 실험 vs 인용 대체

```
인용으로 대체 (직접 실험 불필요):
  ✅ "언어 불일치 시 RAG 성능 저하"
     → Chirkova et al.(2024) [31], Park & Lee(2025) [32]

  ✅ "LLM은 언어별 환각률 다르다"
     → mFAVA, Ul Islam et al.(2025) [30]

  ✅ "영문 컨텍스트가 들어오면 Language Drift 발생"
     → Li et al.(2025) [34]

직접 실험 필요:
  🔬 Table 1: 모듈별 갭 해소 기여도 Ablation
  🔬 Table 2: CAD / SCD / CAD+SCD 조합 ablation
```

### 기술 스택

| 구분 | 기술 | 비고 |
|---|---|---|
| PDF 파싱 | pymupdf | 속도, 레이아웃 보존 |
| 임베딩 | BGE-M3 | 한영 크로스링구얼 핵심 |
| 벡터DB | ChromaDB | 로컬, 메타데이터 필터 |
| 생성 모델 | MIDM-2.0 Base (11.5B) | KT 한국 중심 AI, 오픈소스 |
| 환각 억제 | **CAD + SCD** | **두 문제 동시 해결** |
| 평가 | RAGAS | RAG 특화 자동 평가 |
| UI | Streamlit | 데모용 |
| GPU | RunPod A100 | 로컬 LLM 추론 |

```python
# MIDM-2.0 로드
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch

model = AutoModelForCausalLM.from_pretrained(
    "K-intelligence/Midm-2.0-Base-Instruct",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("K-intelligence/Midm-2.0-Base-Instruct")
# transformers >= 4.45.0 필요
```

---

## 1. 배경 및 연구 동기

### 1.1 RAG 패러다임의 진화

RAG는 외부 데이터베이스 검색 결과를 생성 과정에 결합하여 LLM의 환각과 지식 단절을 보완하는 패러다임이다 [1].

| 패러다임 | 구조 | 한계 |
|---|---|---|
| Naive RAG | 고정 파이프라인: 청킹→검색→생성 | 모든 질의가 같은 경로 |
| Advanced RAG | 사전/사후 검색 최적화 추가 | 순차적 고정 구조 |
| **Modular RAG** | 쿼리 유형에 따라 파이프라인 자체가 동적 변경 | 본 프로젝트 |

### 1.2 선행 연구가 확립한 사실 (인용으로 대체)

**사실 1: LLM은 언어별 환각률이 다르다**
Ul Islam et al.(2025) [30] — 직접 실험 불필요.

**사실 2: 다국어 RAG에서 언어 불일치 시 성능 저하**
Chirkova et al.(2024) [31], Park & Lee(2025) [32] — 직접 실험 불필요.

**사실 3: 영문 컨텍스트가 들어오면 Language Drift 발생**
Li et al.(2025) [34]은 영어가 의미적 끌개(semantic attractor)로 작용하여 한국어 질의에도 영어로 답변하거나 영어 구간을 우선 참조하는 현상을 실증했다 — 직접 실험 불필요.

### 1.3 선행 연구의 한계 (본 연구가 채울 것)

```
Chirkova et al.(2024) [31], Park & Lee(2025) [32]:
  → Wikipedia 기반 오픈도메인
  → 범용 다국어 LLM (Llama, Command-R)
  → 파이프라인 전체 평가, 모듈 분해 없음

Li et al.(2025) [34] SCD:
  → Language Drift 억제 (언어 이탈)
  → 파라메트릭 지식 개입은 다루지 않음

본 연구가 추가하는 것:
  1. 한국어 특화 LLM (MIDM-2.0) + 논문 도메인
  2. 모듈 단위 갭 해소 기여도 분해 (Table 1)
  3. CAD + SCD 조합으로 두 문제 동시 억제 (Table 2)
```

### 1.4 Modular RAG란 정확히 무엇인가

**핵심: 쿼리 유형에 따라 어떤 모듈을 어떤 순서로 실행할지가 동적으로 결정되는 시스템**

```
❌ 그냥 파이프라인 (Modular RAG 아님):
모든 질의 → 청킹 → 검색 → 재랭킹 → 생성 (고정)

✅ 진짜 Modular RAG (본 시스템):
"결과가 뭐야?"     → Result 섹션 필터 검색 → 생성
"A랑 B 비교해줘"  → 병렬 검색 → 합성 → 생성
"인용 논문 찾아줘" → arXiv 수집 → 확장 검색 → 생성
```

쿼리 라우터(MODULE 6)가 없으면 그냥 파이프라인이다.

---

## 2. 관련 연구

### 2.1 핵심 논문 목록 (35편)

| # | 논문 | Venue | arXiv | 역할 |
|---|---|---|---|---|
| 1 | Gao et al. — RAG Survey | ICLR 2024 | 2312.10997 | 전체 설계 근거 |
| 2 | Chen et al. — BGE M3-Embedding | ACL 2024 | 2402.03216 | MODULE 4 |
| 3 | Shi et al. — CAD | NAACL 2024 | 2305.14739 | **MODULE 13A** |
| 4 | Li et al. — Contrastive Decoding | ACL 2023 | 2210.15097 | MODULE 13A 기반 |
| 5 | Sarthi et al. — RAPTOR | ICLR 2024 | 2401.18059 | MODULE 3 |
| 6 | Gao et al. — HyDE | ACL 2023 | 2212.10496 | MODULE 7 |
| 7 | Asai et al. — Self-RAG | ICLR 2024 | 2310.11511 | MODULE 6 |
| 8 | Yan et al. — CRAG | ICLR 2024 | 2401.15884 | MODULE 8 |
| 9 | Edge et al. — GraphRAG | EMNLP 2024 | 2404.16130 | MODULE 11 |
| 10 | Es et al. — RAGAS | EACL 2024 | 2309.15217 | 평가 |
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
| 32 | Park & Lee — Language Preference mRAG | ACL 2025 Findings | 2502.11175 | 배경: 한국어 포함 언어 선호도 |
| 33 | Ranaldi et al. — Multilingual RAG | arXiv 2025 | 2504.03616 | 다국어 RAG 전략 비교 |
| 34 | Li et al. — Language Drift & SCD | arXiv 2025 | 2511.09984 | **MODULE 13B** |
| 35 | Rau et al. — BERGEN | arXiv 2024 | 2407.01102 | mRAG 벤치마킹 기반 |

---

## 3. 시스템 아키텍처 (13개 모듈)

### 3.1 Modular RAG 전체 구조

```
                    ┌─────────────────────────┐
PDF 업로드 ────────▶│     공통 인덱싱 레이어   │
                    │  MODULE 1: PDF 파서      │
                    │  MODULE 2: 섹션 인식기   │
                    │  MODULE 3: 청킹          │
                    │  MODULE 4: BGE-M3        │ ← Ablation 측정점
                    │  MODULE 5: ChromaDB      │
                    └──────────┬──────────────┘
                               │
한/영 질의 ────────────────────▼
                    ┌─────────────────────────┐
                    │  MODULE 6: 쿼리 라우터  │ ★ Modular RAG 핵심
                    └──┬──┬──┬──┬────────────┘
              A경로  B  C  D  E
                    ┌──▼──────────────────────┐
                    │  MODULE 7: 쿼리 확장    │
                    │  MODULE 8: 하이브리드   │ ← Ablation 측정점
                    │  MODULE 9: 재랭커       │ ← Ablation 측정점
                    │  MODULE 10: 컨텍스트 압축│
                    │  MODULE 11: 인용 트래커 │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  MODULE 12: MIDM-2.0    │
                    │  MODULE 13A: CAD        │ ← Table 2 ablation
                    │  MODULE 13B: SCD        │ ← Table 2 ablation
                    └─────────────────────────┘
                               │
                    한국어 답변 (출처 포함)
```

### 3.2 경로별 활성화 모듈

| 경로 | 트리거 | 활성화 모듈 | 비활성화 |
|---|---|---|---|
| A. 단순 QA | 일반 질문 | 4,5,7,8,9,12,13A,13B | 11 |
| B. 섹션 특화 | "결과", "방법론" | 4,5,8(섹션필터),9,12,13A,13B | 7,11 |
| C. 멀티 논문 비교 | "비교", "vs" | 4,5,8(병렬),합성,12,13A,13B | 7,9,11 |
| D. 인용 트래커 | "인용", "reference" | 4,5,11,8(확장),12,13A,13B | 7,9 |
| E. 전체 요약 | "요약" | 3(RAPTOR),4,5,10,12,13A,13B | 7,9,11 |

### 3.3 모듈 명세

---

#### MODULE 1: PDF 파서 `pdf_parser.py`
- 도구: `pymupdf`
- 출력: `{section, content, page, has_table, font_size}`

---

#### MODULE 2: 섹션 인식기 `section_detector.py`
- 감지: Abstract / Introduction / Related Work / Method / Experiment / Result / Discussion / Conclusion / References
- 방법: 키워드 매칭 + 폰트 크기 헤더 감지

---

#### MODULE 3: 청킹 모듈 `chunker.py`
기반: **RAPTOR** [5], **Dense-X** [24], **Meta-Chunking** [28]

| 전략 | 설명 | 활성 경로 |
|---|---|---|
| 섹션 단위 | 섹션 경계 절대 유지 | A, B, C, D |
| 명제 단위 | 원자적 사실 단위 | B (정밀 검색) |
| RAPTOR 계층 | 클러스터→요약→트리 | **E만** |

---

#### MODULE 4: 임베딩 `embedder.py` ★ Ablation 핵심
기반: **BGE M3-Embedding** [2]

```python
model = SentenceTransformer("BAAI/bge-m3")
# 한영 동일 임베딩 공간
# Baseline 2→3 교체 시 갭 변화가 가장 클 것으로 예상
```

---

#### MODULE 5: 벡터DB `vector_store.py`
- ChromaDB persistent 모드
- 메타데이터 필터: `section_type`으로 섹션별 검색

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
    return llm_classify(query)
```

---

#### MODULE 7: 쿼리 확장기 `query_expander.py`
기반: **HyDE** [6], **RAG-Fusion** [26]

- HyDE: 가상 답변 문서 생성 → 검색
- 다중 쿼리: 3가지 표현 확장 → RRF 합산
- 한→영 번역: 병렬 검색

---

#### MODULE 8: 하이브리드 검색기 `hybrid_retriever.py`
기반: **Best Practices** [13], **BM25** [22], **RRF** [23]

```python
def retrieve(query, route, section_filter=None, docs=None):
    if route == "section_b":
        return vector_search(query, filter={"section_type": section_filter})
    elif route == "compare":
        return [vector_search(query, filter={"doc_id": d}) for d in docs]
    else:
        return rrf(vector_search(query), bm25_search(query))
```

---

#### MODULE 9: 재랭커 `reranker.py`
기반: **ColBERTv2** [14], **Jina-ColBERT-v2** [15], **Lost in the Middle** [29]

- cross-encoder 관련성 재정렬
- 위치 편향 보정: 중요 청크를 컨텍스트 앞/뒤 배치

---

#### MODULE 10: 컨텍스트 압축기 `context_compressor.py`
기반: **LLMLingua** [11], **LongLLMLingua** [12], **RECOMP** [19]

---

#### MODULE 11: 인용 트래커 `citation_tracker.py`
기반: **GraphRAG** [9], **HippoRAG2** [27]

- 경로 D 전용
- Reference 파싱 → arXiv API → 자동 인덱싱

---

#### MODULE 12: 생성 모듈 `generator.py`
기반: **Speculative RAG** [16], **RAG Original** [20]

```python
messages = [
    {
        "role": "system",
        "content": "반드시 제공된 문서 내용에만 근거하여 한국어로 답변하세요. "
                   "문서에 없는 내용은 '문서에 해당 정보가 없습니다'라고 답하세요."
    },
    {"role": "user", "content": f"문서:\n{context}\n\n질문: {query}"}
]
```

---

#### MODULE 13A: CAD 환각 억제기 `cad_decoder.py`
기반: **CAD (Shi et al., 2023)** [3], **Contrastive Decoding** [4]

**목적: 파라메트릭 지식 개입 억제**

$$\text{Logit}_{\text{CAD}} = \text{Logit}(\text{문서 포함}) - \alpha \cdot \text{Logit}(\text{문서 없음})$$

```python
from transformers import LogitsProcessor
import torch

class CADDecoder(LogitsProcessor):
    """
    문서가 있어도 모델이 사전학습 기억에서 끌어오는 것을 억제.
    수치 오류, 사실 왜곡 타입 환각에 효과적.
    """
    def __init__(self, model, empty_input_ids, alpha=0.5):
        self.model = model
        self.empty_input_ids = empty_input_ids
        self.alpha = alpha  # Table 2 ablation 대상

    def __call__(self, input_ids, scores):
        with torch.no_grad():
            empty_logits = self.model(
                self.empty_input_ids
            ).logits[:, -1, :]
        return scores - self.alpha * empty_logits
```

---

#### MODULE 13B: SCD 언어 이탈 억제기 `scd_decoder.py`
기반: **Language Drift & SCD (Li et al., 2025)** [34]

**목적: Language Drift 억제 — 영문 컨텍스트 입력 시 한국어 답변 강제**

```python
from transformers import LogitsProcessor
import torch

class SCDDecoder(LogitsProcessor):
    """
    영문 논문 청크가 컨텍스트로 들어와도
    한국어 답변을 생성하도록 비목표 언어 토큰에 패널티.
    Li et al.(2025) SCD 기반 구현.
    """
    def __init__(self, tokenizer, target_lang="ko", beta=0.3):
        self.tokenizer = tokenizer
        self.target_lang = target_lang
        self.beta = beta  # Table 2 ablation 대상
        self.non_target_ids = self._get_non_target_token_ids()

    def _get_non_target_token_ids(self):
        # 한국어 범위 외 토큰 ID 수집
        non_target = []
        for token_id in range(self.tokenizer.vocab_size):
            token = self.tokenizer.decode([token_id])
            if token and not self._is_korean_or_common(token):
                non_target.append(token_id)
        return torch.tensor(non_target)

    def _is_korean_or_common(self, token):
        # 한국어 + 숫자/공백/구두점은 허용
        for ch in token:
            code = ord(ch)
            if not (0xAC00 <= code <= 0xD7A3 or  # 한글 음절
                    0x1100 <= code <= 0x11FF or   # 한글 자모
                    ch in ' \n\t.,!?()[]{}:;"\'-0123456789'):
                return False
        return True

    def __call__(self, input_ids, scores):
        if len(self.non_target_ids) > 0:
            scores[:, self.non_target_ids] -= self.beta
        return scores
```

---

#### MODULE 13 통합 사용법

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

**CAD vs SCD 역할 분리:**

| | CAD [3] | SCD [34] |
|---|---|---|
| 억제 대상 | 파라메트릭 지식 개입 | 비목표 언어 토큰 |
| 해결 문제 | 수치 오류, 사실 왜곡 | Language Drift (영어 답변) |
| 핵심 파라미터 | alpha | beta |
| 선행 연구와의 차이 | 한국어 RAG 특화 적용 | 동일 기법, 본 시스템에 통합 |

---

## 4. 개발 섹션

### 4.1 개발 원칙

```
원칙 1 — 모듈 독립성: 각 모듈 on/off 가능 → Ablation 필수 조건
원칙 2 — 경로 분리: 각 경로를 별도 파일로 관리
원칙 3 — 실험 재현성: 모든 결과 JSON 자동 저장
원칙 4 — 한/영 쌍 강제: 항상 쌍으로 실행 → Table 1 측정 조건
```

### 4.2 개발 순서 (12주)

#### Phase 1 — Core 파이프라인 (1~3주차)

**1주차:** MODULE 1, 2 구현 + 논문 5편 섹션 감지 검증

**2주차:** MODULE 3, 4, 5 (청킹, BGE-M3, ChromaDB)

**3주차:** MODULE 12 (MIDM-2.0 생성) + Baseline 1 완성

> **⚠️ 3주차 체크포인트**: 한/영 쌍 10개로 초기 갭 + Language Drift 실측
> - 갭 + Drift 확인 → Phase 2 진행
> - 없으면 → 연구 설계 재조정

#### Phase 2 — Modular RAG 핵심 (4~5주차)

**4주차:** MODULE 8, 9 + Baseline 2, 3, 4 완성

**5주차:** MODULE 6 (쿼리 라우터) + MODULE 7 + Baseline 5 완성

#### Phase 3 — 킬러 기능 (6~8주차)

**6주차:** MODULE 3 확장 (RAPTOR), Dense-X 청킹

**7주차:** MODULE 11 (인용 트래커 + arXiv API)

**8주차:** MODULE 13A (CAD) + MODULE 13B (SCD) + MODULE 10

```
alpha ∈ {0.1, 0.3, 0.5, 0.7, 1.0}
beta  ∈ {0.1, 0.3, 0.5}
조합 실험 → Table 2 완성
```

#### Phase 4 — 마무리 (9~12주차)

**9주차:** Streamlit UI + 데모 영상

**10주차:** RAGAS 전체 평가 → Table 1 완성

**11~12주차:** 졸업작품 보고서 + GitHub 공개

### 4.3 프로젝트 구조

```
modular-rag-paper-agent/
├── app.py
├── config.py
├── modules/
│   ├── pdf_parser.py
│   ├── section_detector.py
│   ├── chunker.py
│   ├── embedder.py               ← Ablation 핵심
│   ├── vector_store.py
│   ├── query_router.py           ★ Modular RAG 심장
│   ├── query_expander.py
│   ├── hybrid_retriever.py       ← 경로별 다른 동작
│   ├── reranker.py
│   ├── context_compressor.py
│   ├── citation_tracker.py       (경로 D 전용)
│   ├── generator.py              (MIDM-2.0 Base)
│   ├── cad_decoder.py            ★ C2-A: 파라메트릭 지식 억제
│   └── scd_decoder.py            ★ C2-B: Language Drift 억제
├── pipelines/
│   ├── pipeline_a_simple_qa.py
│   ├── pipeline_b_section.py
│   ├── pipeline_c_compare.py
│   ├── pipeline_d_citation.py
│   └── pipeline_e_summary.py
├── evaluation/
│   ├── ragas_eval.py
│   ├── ablation_study.py         → Table 1 생성
│   ├── decoder_ablation.py       → Table 2 생성
│   └── test_queries.json         한/영 질의 쌍 100개
├── results/
└── README.md
```

---

## 5. 평가 및 논문 작성 섹션

### 5.1 실험 설계

#### 5.1.1 데이터셋

```
논문: arXiv NLP 분야 20편 (영문)
질의: 논문당 한국어 5개 + 영어 5개 = 총 200쌍
정답: GPT-4 자동 생성 후 인간 검토
수치 포함 질의 비율: 40% 이상 (CAD 효과 측정용)
```

#### 5.1.2 Table 1: 모듈별 갭 해소 기여도 (직접 실험)

| 시스템 | EN 질의 | KO 질의 | 갭(↓) | Faithfulness | 언어이탈률 |
|---|---|---|---|---|---|
| Baseline 1 (naive RAG) | — | — | — | — | — |
| Baseline 2 (+섹션 청킹) | — | — | — | — | — |
| Baseline 3 (+BGE-M3) | — | — | **↓ 최대 예상** | — | — |
| Baseline 4 (+하이브리드 검색) | — | — | — | — | — |
| Baseline 5 (+재랭커+라우터) | — | — | — | — | — |
| Full System (+CAD+SCD) | — | — | **↓ 최소** | — | **↓ 최소** |

> 숫자는 실험 후 채워짐.

#### 5.1.3 Table 2: CAD / SCD / 조합 ablation (직접 실험, 본 논문의 핵심 표)

| 시스템 | 수치환각률 | 언어이탈률 | Faithfulness | Answer Relevancy |
|---|---|---|---|---|
| Baseline (디코더 없음) | — | — | — | — |
| + CAD만 (α=0.5) | **↓** | — | ↑ | — |
| + SCD만 (β=0.3) | — | **↓** | — | — |
| + CAD+SCD | **↓↓** | **↓↓** | ↑↑ | — |

**Alpha ablation (CAD):**

| alpha | 수치환각률 | Faithfulness | Answer Relevancy |
|---|---|---|---|
| 0.0 | — | — | — |
| 0.3 | — | — | — |
| 0.5 | — | — | — |
| 0.7 | — | — | — |
| 1.0 | — | — | — |

**Beta ablation (SCD):**

| beta | 언어이탈률 | Answer Relevancy |
|---|---|---|
| 0.1 | — | — |
| 0.3 | — | — |
| 0.5 | — | — |

#### 5.1.4 평가 지표

| 지표 | 측정 대상 | 연결 위치 |
|---|---|---|
| Answer Relevancy | 답변이 질의와 관련된 정도 | Table 1, 2 |
| Faithfulness | 답변이 컨텍스트에 근거한 정도 | Table 1, 2 |
| Context Precision | 검색 청크 중 관련 청크 비율 | Table 1 |
| Context Recall | 필요 컨텍스트 검색 비율 | Table 1 |
| 수치 환각률 | 수치 오류 포함 답변 비율 | Table 2 |
| 언어 이탈률 | 한국어 질의에 비한국어 답변 비율 | Table 2 |

---

### 5.2 논문 작성 가이드

#### 5.2.1 논문 구조

```
1. Introduction         (1.5p)
   - 배경: mFAVA [30], Chirkova [31], Park&Lee [32] 인용
   - 두 문제 제기: Language Drift + 파라메트릭 지식 개입
   - "모듈별 분해는 없었다" 갭 지적
   - C1, C2, C3

2. Related Work         (1p)
   - mRAG 선행 연구 [31, 32, 33, 35]
   - 언어별 환각률 [30]
   - 디코딩 개입 기법 [3, 4, 34]

3. System Design        (2p)
   - 쿼리 라우터 중심 Modular RAG 아키텍처
   - CAD + SCD 병렬 적용 구조
   - 두 모듈의 역할 차이 명시

4. Experiments          (2.5p)
   - Table 0: 선행 연구 갭 인용 [31, 32]
   - Table 1: 모듈별 Ablation
   - Table 2: CAD/SCD/조합 Ablation
   - 분석 및 해석

5. Conclusion           (0.5p)
```

#### 5.2.2 핵심 포지셔닝 문장

**두 가지 문제 제기 (Introduction):**

```
"영문 논문에 한국어로 질의할 때 두 가지 문제가 발생한다.
 첫째, Language Drift: 영문 컨텍스트가 입력되면
 모델이 영어로 답변하거나 영어 구간을 우선 참조한다
 (Li et al., 2025 [34]).
 둘째, 파라메트릭 지식 개입: 문서 내용에도 불구하고
 모델의 사전학습 기억이 활성화되어 수치/사실 오류가 발생한다
 (Shi et al., 2023 [3]).
 본 연구는 SCD와 CAD를 조합하여 두 문제를 동시에 억제한다."
```

**모듈별 분해 포지셔닝:**

```
"Chirkova et al.(2024) [31], Park & Lee(2025) [32]는
 다국어 RAG에서 언어 갭을 실증하였으나,
 어떤 모듈이 갭 해소에 기여하는지 분해하지 않았다.
 본 연구는 이를 최초로 정량 분해한다."
```

**CAD vs SCD 차별화:**

```
"Li et al.(2025) [34]의 SCD는 언어 이탈을 억제하나
 파라메트릭 지식 개입은 다루지 않는다.
 Shi et al.(2023) [3]의 CAD는 파라메트릭 지식을 억제하나
 언어 이탈은 다루지 않는다.
 본 연구는 두 기법을 조합하여 상호보완적으로 적용한다."
```

#### 5.2.3 주의할 표현

| 쓰면 안 되는 표현 | 대신 쓸 표현 |
|---|---|
| "Language Drift를 최초 발견" | Li et al.(2025) 인용 + "본 시스템에 통합" |
| "언어 갭이 존재한다" | 선행 연구 [31, 32] 인용 |
| "모든 환각 해결" | "수치 환각률 X%p, 언어 이탈률 Y%p 감소" |
| "노트북LM보다 낫다" | 비교 안 함 |

#### 5.2.4 한계 솔직하게 쓰기

```
Limitations:
- 영문 논문 도메인에 한정
- 20편의 소규모 데이터셋
- CAD + SCD 병렬 적용으로 추론 속도 약 2배 감소
- SCD의 한국어 토큰 판별이 음절 기반이라
  영어 고유명사(모델명 등) 억제 가능성
- 한국어 질의는 자동 번역 사용
```

---

### 5.3 포트폴리오 구성

#### 면접 Q&A

```
Q: 선행 연구랑 뭐가 달라요?
A: 기존 연구(Chirkova 2024, Park&Lee 2025)는
   다국어 RAG에서 언어 갭을 확인했지만,
   어떤 모듈이 갭 해소에 얼마나 기여하는지는
   분해하지 않았습니다. 저는 13개 모듈 단위로
   이를 정량 분해하고, Language Drift와
   파라메트릭 지식 개입 두 문제를 SCD+CAD 조합으로
   동시 억제했습니다.

Q: CAD랑 SCD 동시에 쓰는 이유가 뭔가요?
A: 역할이 달라서요. CAD는 모델의 사전학습 기억이
   문서보다 우선시되는 것을 막고, SCD는 영문 컨텍스트가
   들어와도 한국어로 답변하게 강제합니다.
   둘을 따로 쓰면 각자 하나만 해결하고, 같이 쓰면
   두 문제를 동시에 잡을 수 있습니다.
   Table 2가 이 상호보완 효과를 보여줍니다.

Q: 왜 MIDM-2.0인가요?
A: 기존 mRAG 연구들은 Llama, Command-R 같은
   범용 다국어 모델을 썼습니다. 한국어 특화 LLM에서
   언어 갭이 어떻게 다른지, 어떤 모듈이 필요한지
   분석한 연구가 없었습니다.
```

---

## 6. 참고 문헌

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

[33] Ranaldi, L. et al. (2025). *Multilingual RAG for Knowledge-Intensive Task.* arXiv:2504.03616

[34] Li, B. et al. (2025). *Language Drift in Multilingual RAG & SCD.* arXiv:2511.09984

[35] Rau, D. et al. (2024). *BERGEN: Benchmarking Library for RAG.* arXiv:2407.01102

---

> 본 보고서는 프로젝트 진행에 따라 지속 업데이트됩니다.
