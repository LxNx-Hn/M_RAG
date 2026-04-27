# 국문 논문 원본 초안 복구본

- 복구일 2026-04-26
- 원본 경로 `Guide.md` → `docs/Guide.md`
- 원본 생성 커밋 `578c2c0`
- 삭제 확인 커밋 `8ff8917`
- 상태 과거 초안 보존용
- 주의 현재 코드 기준 문서가 아니며 EXAONE, Streamlit, RunPod 등 과거 설계를 포함

---

# 모듈러 RAG 기반 논문 리뷰 챗봇 에이전트
## 종합 설계 가이드라인 및 관련 연구 보고서

> 졸업작품 / 취업 포트폴리오 프로젝트  
> 작성일: 2026년 4월

---

## 0. 프로젝트 개요

본 프로젝트는 학술 논문 PDF를 입력으로 받아 **한국어 질의응답, 다중 논문 비교, 인용 논문 추적**을 제공하는 모듈러 RAG 기반 챗봇 에이전트를 구현한다. 쿼리 유형에 따라 파이프라인이 동적으로 변경되는 진정한 의미의 Modular RAG이며, 대조 해독(Contrastive Decoding) 기반 환각 억제 모듈을 포함한다.

### 핵심 차별점

- 논문 섹션 구조(Abstract/Method/Result/Conclusion) 인식 청킹
- **쿼리 라우터**: 질의 유형에 따라 파이프라인 자체가 동적으로 변경
- BGE-M3 기반 한국어↔영어 크로스링구얼 검색
- arXiv API 기반 인용 논문 자동 수집
- **Context-Aware Contrastive Decoding** 적용 환각 억제 (학습 불필요)
- RAGAS 기반 정량 평가로 일반 RAG 대비 성능 실증

### 기술 스택

| 구분 | 기술 | 선택 근거 |
|---|---|---|
| PDF 파싱 | pymupdf | 속도 빠르고 레이아웃 정보 보존 |
| 임베딩 | BGE-M3 | 한영 동시 처리, 크로스링구얼 매칭 |
| 벡터DB | ChromaDB | 로컬 실행, 메타데이터 필터링 지원 |
| 생성 모델 | EXAONE-7.8B | 한국어 성능 우수, 오픈소스 |
| 보조 생성 | Llama-3.1-8B | 비교 실험 baseline |
| 환각 억제 | Contrastive Decoding | 학습 없이 LogitsProcessor로 구현 |
| 평가 | RAGAS | RAG 특화 자동 평가 프레임워크 |
| UI | Streamlit | 빠른 데모 구현, 파일 업로드 지원 |
| 인용 수집 | arXiv API | 무료, 공개 학술 논문 대량 수집 |
| GPU | RunPod A100 | 로컬 LLM 추론 환경 |

---

## 1. 배경 및 연구 동기

### 1.1 RAG 패러다임의 진화

대규모 언어 모델(LLM)은 환각, 지식 단절, 불투명한 추론이라는 구조적 한계를 가진다. RAG는 외부 데이터베이스 검색 결과를 생성 과정에 결합하여 이를 보완하는 패러다임이다 [1].

| 패러다임 | 구조 | 한계 |
|---|---|---|
| Naive RAG | 고정 파이프라인: 청킹→검색→생성 | 복잡한 질의 처리 불가 |
| Advanced RAG | 사전/사후 검색 최적화 추가 | 여전히 순차적 고정 구조 |
| **Modular RAG** | 쿼리 유형에 따라 동적 파이프라인 구성 | 구현 복잡도 높음 (본 프로젝트) |

### 1.2 논문 도메인의 특수성

기존 범용 RAG는 논문의 구조적 특성을 무시한다. 논문은 명확한 섹션 구조를 가지며 각 섹션은 서로 다른 유형의 정보를 담는다.

- `"결과가 어떻게 나왔어?"` → Result 섹션 우선 검색 필요
- `"방법론 설명해줘"` → Method 섹션 우선 검색 필요
- `"A 논문이랑 B 논문 비교해줘"` → 병렬 멀티 문서 검색 필요
- `"인용 논문도 같이 분석해줘"` → arXiv 외부 수집 + 확장 검색 필요

### 1.3 한국어 특화 필요성

영어 논문에 한국어로 질의할 때 발생하는 크로스링구얼 갭이 검색 및 생성 품질에 영향을 미친다. BGE-M3는 동일 임베딩 공간에서 다국어를 처리하여 이 문제를 해결한다 [2]. 생성 단계의 환각은 Context-Aware Contrastive Decoding으로 추가 억제한다 [3, 4].

---

## 2. 관련 연구

### 2.1 핵심 논문 목록 (30편)

| # | 논문 | Venue | arXiv | 적용 모듈 |
|---|---|---|---|---|
| 1 | Gao et al. — RAG Survey | ICLR 2024 | 2312.10997 | 전체 설계 근거 |
| 2 | Chen et al. — BGE M3-Embedding | ACL 2024 | 2402.03216 | MODULE 4 임베딩 |
| 3 | Shi et al. — Context-Aware Decoding (CAD) | NAACL 2024 | 2305.14739 | MODULE 13 환각 억제 |
| 4 | Li et al. — Contrastive Decoding | ACL 2023 | 2210.15097 | MODULE 13 기반 이론 |
| 5 | Sarthi et al. — RAPTOR | ICLR 2024 | 2401.18059 | MODULE 3 계층 청킹 |
| 6 | Gao et al. — HyDE | ACL 2023 | 2212.10496 | MODULE 7 쿼리 확장 |
| 7 | Asai et al. — Self-RAG | ICLR 2024 | 2310.11511 | MODULE 6 라우터 설계 |
| 8 | Yan et al. — CRAG | ICLR 2024 | 2401.15884 | MODULE 8 검색 교정 |
| 9 | Edge et al. — GraphRAG | EMNLP 2024 | 2404.16130 | MODULE 11 인용 그래프 |
| 10 | Es et al. — RAGAS | EACL 2024 | 2309.15217 | 평가 프레임워크 |
| 11 | Jiang et al. — LLMLingua | EMNLP 2023 | 2310.05736 | MODULE 10 컨텍스트 압축 |
| 12 | Jiang et al. — LongLLMLingua | ACL 2024 | 2310.05736 | MODULE 10 쿼리 의존 압축 |
| 13 | Wang et al. — Best Practices in RAG | arXiv 2024 | 2407.01219 | MODULE 8 하이브리드 검색 |
| 14 | Santhanam et al. — ColBERTv2 | NAACL 2022 | 2112.01488 | MODULE 9 재랭킹 |
| 15 | Jha et al. — Jina-ColBERT-v2 | MRL 2024 | 2408.16672 | MODULE 9 다국어 재랭킹 |
| 16 | Wang et al. — Speculative RAG | arXiv 2024 | 2407.08223 | MODULE 12 초안-검증 생성 |
| 17 | Jiang et al. — FLARE | EMNLP 2023 | 2305.06983 | MODULE 6 적응적 검색 |
| 18 | Shao et al. — ITER-RETGEN | arXiv 2023 | 2305.15294 | MODULE 6 반복 검색 |
| 19 | Xu et al. — RECOMP | ICLR 2024 | 2310.04408 | MODULE 10 추출/요약 압축 |
| 20 | Lewis et al. — RAG (Original) | NeurIPS 2020 | 2005.11401 | 전체 기반 이론 |
| 21 | Khattab & Zaharia — ColBERT | SIGIR 2020 | 2004.12832 | MODULE 9 레이트 인터랙션 |
| 22 | Robertson et al. — BM25 | TREC 1994 | - | MODULE 8 희소 검색 |
| 23 | Cormack et al. — RRF | SIGIR 2009 | - | MODULE 8 결과 융합 |
| 24 | Chen et al. — Dense-X Retrieval | arXiv 2023 | 2312.06648 | MODULE 3 명제 단위 청킹 |
| 25 | Trivedi et al. — IRCoT | ACL 2023 | 2212.10509 | MODULE 6 멀티홉 추론 |
| 26 | Rackauckas — RAG-Fusion | arXiv 2024 | 2402.03367 | MODULE 7 다중 쿼리 |
| 27 | Gutiérrez et al. — HippoRAG2 | arXiv 2025 | 2502.14802 | MODULE 11 장기 기억 검색 |
| 28 | Zhong et al. — Meta-Chunking | arXiv 2024 | 2410.12788 | MODULE 3 논리 인식 청킹 |
| 29 | Liu et al. — Lost in the Middle | TACL 2024 | 2307.03172 | MODULE 9 위치 편향 보정 |
| 30 | Ge et al. — ICAE (컨텍스트 압축) | NeurIPS 2024 | 2307.06945 | MODULE 10 임베딩 압축 |

---

### 2.2 핵심 기술 상세 설명

#### 2.2.1 RAPTOR — 계층적 요약 트리 [5]

문서를 청킹한 뒤 유사 청크를 클러스터링하고 LLM으로 요약하여 계층 트리를 구성한다. 검색 시 트리의 다양한 레벨에서 검색하여 세부 사실과 전체 맥락을 동시에 포착한다.

```
원본 청크 (leaf) → 클러스터 요약 (mid) → 전체 요약 (root)
                 ↕ 검색 시 모든 레벨 활용
```

#### 2.2.2 HyDE — 가상 문서 임베딩 [6]

쿼리를 직접 검색하는 대신, LLM이 가상의 답변 문서를 먼저 생성하고 그 문서로 검색한다.

```
한국어 쿼리 → LLM → 가상 영문 답변 → 영문 논문 검색
             (크로스링구얼 갭 해소)
```

#### 2.2.3 Self-RAG — 적응적 검색 [7]

LLM이 reflection token(`[Retrieve]`, `[Relevant]`, `[Supported]`)을 사용해 검색 필요 여부를 스스로 판단한다. 쿼리 라우터 설계의 이론적 기반이 된다.

#### 2.2.4 CRAG — 교정적 RAG [8]

검색 결과의 관련성을 평가기로 판정하여 낮으면 웹 검색(본 시스템에서는 arXiv 검색)으로 보완한다.

#### 2.2.5 Hybrid Search + RRF [13, 23]

BM25(키워드)와 벡터 검색(의미)을 결합한다. Reciprocal Rank Fusion으로 두 결과를 통합한다.

```
RRF score(d) = Σ 1 / (k + rank_i(d))   (k=60)
```

#### 2.2.6 ColBERTv2 — 레이트 인터랙션 재랭킹 [14]

토큰 레벨 다중 벡터로 쿼리-문서 관련성을 세밀하게 평가한다. MaxSim 연산으로 각 쿼리 토큰과 가장 유사한 문서 토큰을 매칭한다.

```
score(q, d) = Σ_i max_j (E_q[i] · E_d[j])
```

#### 2.2.7 LLMLingua / LongLLMLingua — 컨텍스트 압축 [11, 12]

쿼리 조건부 퍼플렉시티로 각 토큰의 중요도를 계산하여 불필요한 토큰을 제거한다.

#### 2.2.8 Context-Aware Contrastive Decoding (CAD) [3, 4]

본 프로젝트의 핵심 추가 모듈. 파인튜닝 없이 LogitsProcessor 하나로 구현.

$$\text{Logit}_{\text{final}} = \text{Logit}(\text{문서 포함 프롬프트}) - \alpha \cdot \text{Logit}(\text{문서 없는 프롬프트})$$

모델이 다음 토큰을 예측할 때 파라메트릭 지식(사전 학습 기억)의 개입을 실시간으로 억제한다. Shi et al.(2023)의 CAD를 한국어 RAG 수치 환각 억제에 적용한다.

#### 2.2.9 Speculative RAG [16]

소형 specialist LM이 병렬로 여러 draft를 생성하고, 대형 generalist LM이 검증한다. 지연 시간을 줄이면서 품질을 유지하는 효율적 생성 전략이다.

#### 2.2.10 RECOMP — 추출/요약 압축 [19]

검색된 문서를 쿼리 관련 부분만 추출(extractive) 또는 요약(abstractive)하여 압축한다. LLMLingua와 상호보완적으로 사용 가능하다.

#### 2.2.11 Dense-X Retrieval — 명제 단위 청킹 [24]

문장 대신 `"명제(proposition)"` 단위로 청킹한다. 각 청크가 하나의 원자적 사실을 담도록 하여 검색 정밀도를 높인다.

#### 2.2.12 IRCoT — 추론 연계 반복 검색 [25]

Chain-of-Thought 추론과 검색을 교차하며 반복한다. 멀티홉 질문(여러 논문에 걸친 정보)에 효과적이다.

#### 2.2.13 Lost in the Middle [29]

긴 컨텍스트에서 LLM은 처음과 끝 정보를 잘 기억하고 중간 정보를 잘 잊는다. 재랭킹 시 중요 청크를 컨텍스트 앞/뒤에 배치하는 전략의 근거가 된다.

---

## 3. 시스템 아키텍처

### 3.1 전체 구조

```
PDF 업로드
    │
    ▼
┌─────────────────────────────────────┐
│          입력 처리 레이어            │
│  MODULE 1: PDF 파서                 │
│  MODULE 2: 섹션 인식기              │
│  MODULE 3: 청킹 모듈                │
└───────────────┬─────────────────────┘
                │
    ▼
┌─────────────────────────────────────┐
│          인덱싱 레이어              │
│  MODULE 4: 임베딩 (BGE-M3)         │
│  MODULE 5: 벡터DB (ChromaDB)       │
└───────────────┬─────────────────────┘
                │
사용자 질의 ──▶ │
    ▼
┌─────────────────────────────────────┐
│         쿼리 처리 레이어            │
│  MODULE 6: 쿼리 라우터 ★핵심       │
│  MODULE 7: 쿼리 확장기 (HyDE)      │
└───────┬──────┬──────┬──────┬───────┘
        │A     │B     │C     │D/E
    ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼
┌─────────────────────────────────────┐
│          검색 레이어                │
│  MODULE 8: 하이브리드 검색기        │
│  MODULE 9: 재랭커 (ColBERT)        │
│  MODULE 10: 컨텍스트 압축기        │
│  MODULE 11: 인용 트래커             │
└───────────────┬─────────────────────┘
                │
    ▼
┌─────────────────────────────────────┐
│          생성 레이어                │
│  MODULE 12: 생성 모듈 (EXAONE)     │
│  MODULE 13: 대조 해독 환각 억제    │
└─────────────────────────────────────┘
                │
    ▼
         최종 답변 (출처 포함)
```

### 3.2 모듈 상세 명세

---

#### MODULE 1: PDF 파서 `pdf_parser.py`

**역할**: PDF → 텍스트/표/수식 구조화 추출

- 입력: PDF 파일 경로
- 출력: `{section, content, page, has_table, font_size}` 리스트
- 도구: `pymupdf (fitz)`
- 핵심: 블록 단위 추출 → 폰트 크기로 헤더 감지 → 2단 레이아웃 처리

```bash
pip install pymupdf
```

---

#### MODULE 2: 섹션 인식기 `section_detector.py`

**역할**: 논문 섹션 경계 감지 및 레이블 부착

- 감지 대상: Abstract, Introduction, Related Work, Method, Experiment, Result, Discussion, Conclusion, References
- 방법: 규칙 기반(섹션명 키워드) + 폰트 크기 기반 헤더 감지
- 출력: 각 텍스트 블록에 `section_type` 메타데이터 부착

---

#### MODULE 3: 청킹 모듈 `chunker.py`

**역할**: 섹션 구조를 존중하는 검색 단위 분할

기반 논문: **RAPTOR** [5], **Dense-X Retrieval** [24], **Meta-Chunking** [28]

전략 선택:
- `섹션 단위`: 섹션 경계를 절대 넘지 않음 (기본값)
- `명제 단위`: Dense-X 방식, 원자적 사실 단위로 분리
- `RAPTOR 계층`: 청크 클러스터링 → LLM 요약 → 트리 구성

```python
# 메타데이터 스키마
{
    "doc_id": str,
    "section_type": str,   # "abstract" | "method" | "result" | ...
    "chunk_id": str,
    "page": int,
    "char_start": int,
    "char_end": int,
    "chunk_level": int     # RAPTOR: 0=leaf, 1=mid, 2=root
}
```

---

#### MODULE 4: 임베딩 모듈 `embedder.py`

**역할**: 텍스트 → 벡터 변환

기반 논문: **BGE M3-Embedding** [2]

- 모델: `BAAI/bge-m3`
- 특징: 한영 동일 임베딩 공간 → 크로스링구얼 매칭 가능
- 배치 처리: GPU 메모리 고려한 자동 배치 크기 조절

```bash
pip install sentence-transformers
```

---

#### MODULE 5: 벡터DB 관리자 `vector_store.py`

**역할**: 임베딩 저장 및 메타데이터 필터 검색

- DB: `ChromaDB` (로컬 persistent 모드)
- 메타데이터 필터: `section_type`으로 특정 섹션만 검색 가능
- 컬렉션 구조: 문서별 컬렉션 분리

```bash
pip install chromadb
```

---

#### MODULE 6: 쿼리 라우터 `query_router.py` ★ Modular RAG 핵심

**역할**: 질의 분석 → 최적 파이프라인 경로 동적 결정

기반 논문: **Self-RAG** [7], **FLARE** [17], **CRAG** [8]

| 경로 | 쿼리 패턴 | 파이프라인 |
|---|---|---|
| A. 단순 QA | 일반 사실 질문 | 벡터검색 → 생성 |
| B. 섹션 특화 | "결과가", "방법론", "한계점" | 섹션 필터 검색 → 생성 |
| C. 멀티 논문 비교 | "A랑 B 비교", "vs" | 병렬 검색 → 합성 → 생성 |
| D. 인용 트래커 | "인용 논문", "reference" | arXiv 수집 → 확장 검색 → 생성 |
| E. 전체 요약 | "요약해줘", "summarize" | RAPTOR 계층 검색 → 생성 |

```python
# 쿼리 라우터 키워드 맵
ROUTE_MAP = {
    "section_result":  ["결과", "성능", "result", "performance", "accuracy"],
    "section_method":  ["방법론", "어떻게", "method", "approach", "architecture"],
    "section_limit":   ["한계", "limitation", "future work", "단점"],
    "compare":         ["비교", "차이", "vs", "compare", "versus"],
    "citation":        ["인용", "참고문헌", "reference", "cited by"],
    "summary":         ["요약", "summarize", "전체", "overview"],
}
```

---

#### MODULE 7: 쿼리 확장기 `query_expander.py`

**역할**: 검색 성능 향상을 위한 쿼리 변환

기반 논문: **HyDE** [6], **RAG-Fusion** [26], **IRCoT** [25]

- `HyDE`: LLM으로 가상 답변 문서 생성 → 그 문서로 검색
- `다중 쿼리 (RAG-Fusion)`: 쿼리를 3가지 표현으로 확장 → RRF로 결과 합산
- `한→영 번역`: 한국어 쿼리를 영어로도 번역하여 병렬 검색

---

#### MODULE 8: 하이브리드 검색기 `hybrid_retriever.py`

**역할**: Dense + Sparse 검색 결합

기반 논문: **Best Practices in RAG** [13], **BM25** [22], **RRF** [23], **CRAG** [8]

```python
# Reciprocal Rank Fusion
def rrf(dense_ranks, sparse_ranks, k=60):
    scores = {}
    for rank, doc_id in enumerate(dense_ranks):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    for rank, doc_id in enumerate(sparse_ranks):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
```

- Dense: BGE-M3 벡터 유사도 (의미적 매칭)
- Sparse: BM25 키워드 (정확한 용어, 저자명, 모델명)
- 섹션 필터: 쿼리 라우터의 섹션 정보를 ChromaDB 메타데이터 필터로 전달

---

#### MODULE 9: 재랭커 `reranker.py`

**역할**: 검색 결과 관련성 재정렬

기반 논문: **ColBERTv2** [14], **Jina-ColBERT-v2** [15], **Lost in the Middle** [29]

- 모델: `cross-encoder/ms-marco-MiniLM-L-6-v2` (경량 cross-encoder)
- ColBERT 레이트 인터랙션: 토큰 레벨 MaxSim으로 정밀 관련성 계산
- 위치 편향 보정: 중요 청크를 컨텍스트 앞/뒤에 배치 (Lost in the Middle [29])
- 섹션 가중치: 쿼리 유형에 따라 특정 섹션 청크에 가중치 부여

---

#### MODULE 10: 컨텍스트 압축기 `context_compressor.py`

**역할**: LLM 컨텍스트 윈도우 한계 내 정보 밀도 최대화

기반 논문: **LLMLingua** [11], **LongLLMLingua** [12], **RECOMP** [19], **ICAE** [30]

```python
# 압축 전략 선택
if len(context_tokens) > THRESHOLD:
    if query_dependent:
        compress_with_longllmlingua(context, query)  # 쿼리 의존적
    else:
        compress_with_recomp(context)               # 추출 요약
```

- LLMLingua: 토큰 레벨 퍼플렉시티 기반 압축
- LongLLMLingua: 쿼리 조건부 대조 퍼플렉시티 압축
- RECOMP: 쿼리 관련 문장만 추출 또는 요약 생성

---

#### MODULE 11: 인용 트래커 `citation_tracker.py`

**역할**: Reference 파싱 → 인용 논문 자동 수집

기반 논문: **GraphRAG** [9], **HippoRAG2** [27]

```python
# 처리 흐름
Reference 섹션 파싱 (정규식 + LLM)
    → 저자/제목/연도 추출
    → arXiv API 검색
    → 실패 시 Semantic Scholar API 보조
    → 수집 논문 자동 인덱싱
```

- 실패 처리: arXiv에 없는 경우 스킵 후 메타데이터만 저장
- 수집된 논문을 벡터DB에 추가하여 멀티 논문 검색 확장

---

#### MODULE 12: 생성 모듈 `generator.py`

**역할**: 컨텍스트 + 질의 → 최종 답변 생성

기반 논문: **Speculative RAG** [16], **RAG (Original)** [20]

- 모델: `EXAONE-7.8B` (한국어 우선) / `Llama-3.1-8B` (비교 baseline)
- Speculative RAG 적용: 소형 모델이 draft 생성 → 대형 모델 검증 (선택적)
- 출처 추적: 각 주장이 어느 논문/섹션에서 왔는지 인라인 표시
- 언어 제어: 질의 언어(한/영)로 답변 생성 강제

---

#### MODULE 13: 대조 해독 환각 억제기 `contrastive_decoder.py` ★ 차별화 포인트

**역할**: 생성 단계에서 파라메트릭 지식 개입 실시간 억제

기반 논문: **CAD (Shi et al., 2023)** [3], **Contrastive Decoding (Li et al., 2023)** [4]

$$\text{Logit}_{\text{final}} = \text{Logit}(\text{문서 포함 프롬프트}) - \alpha \cdot \text{Logit}(\text{문서 없는 프롬프트})$$

```python
from transformers import LogitsProcessor
import torch

class ContrastiveDecoder(LogitsProcessor):
    """
    Context-Aware Contrastive Decoding
    Shi et al. (2023) 기반, 학습 불필요
    HuggingFace LogitsProcessor 인터페이스 활용
    """
    def __init__(self, model, tokenizer, empty_input_ids, alpha=0.5):
        self.model = model
        self.empty_input_ids = empty_input_ids  # 문서 없는 프롬프트
        self.alpha = alpha                       # 억제 강도 (0~1)

    def __call__(self, input_ids, scores):
        with torch.no_grad():
            # 문서 없는 프롬프트로 logit 계산
            empty_logits = self.model(
                self.empty_input_ids
            ).logits[:, -1, :]

        # 수식 적용: 파라메트릭 지식 억제
        scores = scores - self.alpha * empty_logits
        return scores

# 사용법
decoder = ContrastiveDecoder(model, tokenizer, empty_ids, alpha=0.5)
output = model.generate(
    input_ids,
    logits_processor=[decoder],
    max_new_tokens=512
)
```

**왜 논문에 넣을 수 있나:**
- 기존 CAD를 **한국어 RAG 수치 환각 억제** 용도로 특화 적용
- 학습 없이 inference-time intervention
- `alpha` 파라미터 조절 실험으로 ablation study 가능

---

## 4. 쿼리 경로별 파이프라인

### 경로 A: 단순 QA
```
"이 논문에서 사용한 데이터셋이 뭐야?"

쿼리 → [라우터: A] → [HyDE 쿼리 확장] → [하이브리드 검색]
     → [재랭커] → [컨텍스트 압축] → [생성] → [CAD 억제] → 답변
```

### 경로 B: 섹션 특화
```
"결과가 어떻게 나왔어?" / "방법론 설명해줘"

쿼리 → [라우터: B, section=result] → [ChromaDB 섹션 필터 검색]
     → [ColBERT 재랭킹] → [생성] → [CAD 억제] → 답변
```

### 경로 C: 멀티 논문 비교
```
"논문 A랑 B의 방법론 차이가 뭐야?"

쿼리 → [라우터: C] → [논문A 병렬 검색 + 논문B 병렬 검색]
     → [결과 합성기] → [구조화 비교 생성] → 표 형식 답변
```

### 경로 D: 인용 트래커
```
"이 논문이 인용한 핵심 논문들도 분석해줘"

쿼리 → [라우터: D] → [Reference 파싱] → [arXiv API 수집]
     → [자동 인덱싱] → [확장 검색] → [생성] → 인용 관계 포함 답변
```

### 경로 E: 전체 요약
```
"이 논문 전체 요약해줘"

쿼리 → [라우터: E] → [RAPTOR 계층 트리 검색]
     → [섹션별 핵심 추출] → [LLMLingua 압축] → [생성] → 구조화 요약
```

---

## 5. 평가 설계

### 5.1 Ablation Study

| 시스템 | 구성 | 목적 |
|---|---|---|
| Baseline 1 | 고정 500토큰 청킹 + 벡터 검색 + 생성 | 최단순 RAG |
| Baseline 2 | + 섹션 인식 청킹 | 섹션 청킹 효과 |
| Baseline 3 | + 하이브리드 검색 | Hybrid Search 효과 |
| Baseline 4 | + ColBERT 재랭커 | Reranking 효과 |
| Baseline 5 | + 쿼리 라우터 + HyDE | Modular RAG 효과 |
| **Full System** | + CAD 환각 억제 + 컨텍스트 압축 | 완전 시스템 |

### 5.2 평가 지표 (RAGAS [10])

- **Faithfulness**: 답변이 검색 컨텍스트에 근거하는 정도 (환각 방지)
- **Answer Relevancy**: 답변이 질의와 관련된 정도
- **Context Precision**: 검색 청크 중 실제 관련 청크 비율
- **Context Recall**: 정답에 필요한 컨텍스트 검색 비율

### 5.3 평가 데이터셋

- 논문 20편 (NLP 분야 arXiv 논문)
- 질의 100개 (유형별: 단순 QA 40%, 섹션 특화 30%, 비교 20%, 요약 10%)
- CAD alpha 값 ablation: α ∈ {0.1, 0.3, 0.5, 0.7, 1.0}

---

## 6. 3개월 개발 로드맵

| 기간 | 목표 | 산출물 |
|---|---|---|
| 1주차 | 환경 구성, PDF 파서, 섹션 인식기 | `pdf_parser.py`, `section_detector.py` |
| 2주차 | 청킹, 임베딩, ChromaDB 연동 | `chunker.py`, `embedder.py`, `vector_store.py` |
| 3주차 | 기본 QA 파이프라인 완성 (Baseline 1) | 기본 동작 데모 |
| 4주차 | 하이브리드 검색 + ColBERT 재랭커 | `hybrid_retriever.py`, `reranker.py` |
| 5주차 | **쿼리 라우터 구현** (핵심) | `query_router.py` |
| 6주차 | HyDE + 다중 쿼리 + RAPTOR 계층 요약 | `query_expander.py`, `raptor.py` |
| 7주차 | 인용 트래커 + arXiv API 연동 | `citation_tracker.py` |
| 8주차 | **CAD 환각 억제** + 컨텍스트 압축 | `contrastive_decoder.py`, `context_compressor.py` |
| 9주차 | Streamlit UI + 데모 완성 | `app.py`, 데모 영상 |
| 10주차 | RAGAS 평가 + Ablation Study | 평가 결과 표 |
| 11주차 | 졸업작품 보고서 작성 | 보고서 초안 |
| 12주차 | GitHub 정리 + README + 최종 제출 | GitHub repo 공개 |

**우선순위**: 1~3주차(Core) → 4~5주차(차별점) → 6~8주차(킬러 기능) → 9~12주차(마무리)

---

## 7. 프로젝트 구조

```
modular-rag-paper-agent/
├── app.py                        # Streamlit UI 진입점
├── config.py                     # 전역 설정 (모델명, 파라미터 등)
├── modules/
│   ├── pdf_parser.py             # MODULE 1: PDF 파싱
│   ├── section_detector.py       # MODULE 2: 섹션 인식
│   ├── chunker.py                # MODULE 3: 섹션/RAPTOR/명제 청킹
│   ├── embedder.py               # MODULE 4: BGE-M3 임베딩
│   ├── vector_store.py           # MODULE 5: ChromaDB 관리
│   ├── query_router.py           # MODULE 6: ★ 쿼리 라우터
│   ├── query_expander.py         # MODULE 7: HyDE + 다중 쿼리
│   ├── hybrid_retriever.py       # MODULE 8: BM25 + 벡터 + RRF
│   ├── reranker.py               # MODULE 9: ColBERT 재랭킹
│   ├── context_compressor.py     # MODULE 10: LLMLingua + RECOMP
│   ├── citation_tracker.py       # MODULE 11: 인용 추적 + arXiv API
│   ├── generator.py              # MODULE 12: EXAONE 생성
│   └── contrastive_decoder.py    # MODULE 13: ★ CAD 환각 억제
├── pipelines/
│   ├── pipeline_a_simple_qa.py
│   ├── pipeline_b_section.py
│   ├── pipeline_c_compare.py
│   ├── pipeline_d_citation.py
│   └── pipeline_e_summary.py
├── evaluation/
│   ├── ragas_eval.py             # RAGAS 자동 평가
│   ├── ablation_study.py         # Ablation Study 실험
│   └── test_queries.json         # 당시 기준 평가 질의 100개
├── data/                         # 테스트 논문 PDF
├── notebooks/                    # 실험 노트북
├── requirements.txt
└── README.md
```

---

## 8. 참고 문헌

[1] Gao, Y. et al. (2023). *Retrieval-Augmented Generation for Large Language Models: A Survey.* ICLR 2024. arXiv:2312.10997

[2] Chen, J. et al. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation.* ACL 2024. arXiv:2402.03216

[3] Shi, W. et al. (2023). *Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding.* NAACL 2024. arXiv:2305.14739

[4] Li, X. et al. (2022). *Contrastive Decoding: Open-ended Text Generation as Optimization.* ACL 2023. arXiv:2210.15097

[5] Sarthi, P. et al. (2024). *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval.* ICLR 2024. arXiv:2401.18059

[6] Gao, L. et al. (2022). *Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE).* ACL 2023. arXiv:2212.10496

[7] Asai, A. et al. (2023). *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.* ICLR 2024. arXiv:2310.11511

[8] Yan, S. et al. (2024). *Corrective Retrieval Augmented Generation (CRAG).* ICLR 2024. arXiv:2401.15884

[9] Edge, D. et al. (2024). *From Local to Global: A Graph RAG Approach to Query-Focused Summarization.* EMNLP 2024. arXiv:2404.16130

[10] Es, S. et al. (2023). *RAGAS: Automated Evaluation of Retrieval Augmented Generation.* EACL 2024. arXiv:2309.15217

[11] Jiang, H. et al. (2023). *LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models.* EMNLP 2023. arXiv:2310.05736

[12] Jiang, H. et al. (2023). *LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression.* ACL 2024. arXiv:2310.06839

[13] Wang, X. et al. (2024). *Searching for Best Practices in Retrieval-Augmented Generation.* arXiv:2407.01219

[14] Santhanam, K. et al. (2022). *ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction.* NAACL 2022. arXiv:2112.01488

[15] Jha, R. et al. (2024). *Jina-ColBERT-v2: A General-Purpose Multilingual Late Interaction Retriever.* MRL 2024. arXiv:2408.16672

[16] Wang, Z. et al. (2024). *Speculative RAG: Enhancing Retrieval Augmented Generation through Drafting.* arXiv:2407.08223

[17] Jiang, Z. et al. (2023). *Active Retrieval Augmented Generation (FLARE).* EMNLP 2023. arXiv:2305.06983

[18] Shao, Z. et al. (2023). *Enhancing Retrieval-Augmented Large Language Models with Iterative Retrieval-Generation Synergy (ITER-RETGEN).* EMNLP 2023 Findings. arXiv:2305.15294

[19] Xu, F. et al. (2023). *RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation.* ICLR 2024. arXiv:2310.04408

[20] Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS 2020. arXiv:2005.11401

[21] Khattab, O. & Zaharia, M. (2020). *ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT.* SIGIR 2020. arXiv:2004.12832

[22] Robertson, S. et al. (1994). *Okapi at TREC-3.* TREC 1994. (BM25 원논문)

[23] Cormack, G. et al. (2009). *Reciprocal Rank Fusion outperforms Condorcet and Individual Rank Learning Methods.* SIGIR 2009.

[24] Chen, T. et al. (2023). *Dense X Retrieval: What Retrieval Granularity Should We Use?* arXiv:2312.06648

[25] Trivedi, H. et al. (2022). *Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions (IRCoT).* ACL 2023. arXiv:2212.10509

[26] Rackauckas, A. (2024). *RAG-Fusion: a New Take on Retrieval-Augmented Generation.* arXiv:2402.03367

[27] Gutiérrez, B.J. et al. (2025). *From RAG to Memory: Non-Parametric Continual Learning for Large Language Models (HippoRAG2).* arXiv:2502.14802

[28] Zhong, Q. et al. (2024). *Meta-Chunking: Learning Efficient Text Segmentation via Logical Perception.* arXiv:2410.12788

[29] Liu, N.F. et al. (2023). *Lost in the Middle: How Language Models Use Long Contexts.* TACL 2024. arXiv:2307.03172

[30] Ge, T. et al. (2023). *In-context Autoencoder for Context Compression in a Large Language Model (ICAE).* ICLR 2024. arXiv:2307.06945

---

> 본 보고서는 프로젝트 진행에 따라 지속 업데이트됩니다.
