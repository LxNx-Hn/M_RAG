# M-RAG 시스템 아키텍처

## 목차
1. [시스템 개요](#1-시스템-개요)
2. [모듈 의존성 그래프](#2-모듈-의존성-그래프)
3. [데이터 흐름](#3-데이터-흐름)
4. [모듈 상세 명세](#4-모듈-상세-명세)
5. [파이프라인 설계](#5-파이프라인-설계)
6. [핵심 알고리즘](#6-핵심-알고리즘)
7. [평가 프레임워크](#7-평가-프레임워크)
8. [확장 가이드](#8-확장-가이드)

---

## 1. 시스템 개요

M-RAG는 **쿼리 유형에 따라 파이프라인이 동적으로 변경되는 Modular RAG** 시스템입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                  React SPA (:5173) + FastAPI (:8000)          │
│  ┌──────────┐  ┌──────────────────────────────────────────┐ │
│  │ 소스 패널 │  │            채팅 인터페이스                │ │
│  │ PDF 업로드│  │  추천 질문 → 라우터 배지 → 출처 표시     │ │
│  │ 논문 카드 │  │         (SSE 스트리밍)                   │ │
│  │ 설정 패널 │  │                                          │ │
│  └──────────┘  └──────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Query Router (MODULE 6)                    │
│              쿼리 분석 → 5개 경로 중 택 1                     │
└──┬──────┬──────┬──────┬──────┬──────────────────────────────┘
   A      B      C      D      E
   │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│단순QA││섹션  ││비교  ││인용  ││요약  │
│      ││특화  ││      ││추적  ││      │
└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘
   │       │       │       │       │
   └───────┴───────┴───────┴───────┘
                   │
   ┌───────────────▼───────────────┐
   │  공통 모듈: 검색 → 재랭킹 →   │
   │  압축 → 생성 → CAD 억제       │
   └───────────────────────────────┘
```

### 설계 원칙

1. **모듈러 파이프라인**: 각 모듈은 독립적으로 교체 가능
2. **동적 라우팅**: 쿼리 유형에 따라 파이프라인이 자동 구성, 라우트 배지로 사용자에게 투명하게 표시
3. **점진적 로딩**: GPU 모듈은 lazy loading으로 필요할 때만 로드
4. **학습 불필요**: CAD/SCD 환각 억제·언어이탈 방지는 inference-time intervention으로 추가 학습 불필요
5. **한국어 학술 RAG 특화** (C3 기여): CAD(Shi et al., NAACL 2024)를 한국어 학술 RAG에 적용하여 환각 억제 효과를 실증한 최초 시스템. SCD(Li et al., 2025)로 영문 논문 컨텍스트에서의 언어 이탈(Language Drift)을 동시 억제

---

## 2. 모듈 의존성 그래프

```
config.py ◄─────────────────── 모든 모듈이 참조
    │
    ├── pdf_parser.py (M1)
    │       │
    │       ▼
    ├── section_detector.py (M2) ──► config.SECTION_PATTERNS
    │       │
    │       ▼
    ├── chunker.py (M3) ──────────► embedder (optional, RAPTOR용)
    │       │                       generator (optional, RAPTOR용)
    │       ▼
    ├── embedder.py (M4) ─────────► sentence-transformers
    │       │
    │       ▼
    ├── vector_store.py (M5) ─────► chromadb
    │       │
    │       ▼
    ├── query_router.py (M6) ─────► config.ROUTE_MAP
    │       │
    │       ▼
    ├── query_expander.py (M7) ───► generator (optional)
    │       │
    │       ▼
    ├── hybrid_retriever.py (M8) ─► vector_store + embedder
    │       │
    │       ▼
    ├── reranker.py (M9) ────────► sentence-transformers CrossEncoder
    │       │
    │       ▼
    ├── context_compressor.py (M10) ► generator (optional)
    │       │
    │       ▼
    ├── citation_tracker.py (M11) ► requests (arXiv API)
    │       │
    │       ▼
    ├── generator.py (M12) ──────► transformers (AutoModelForCausalLM)
    │       │
    │       ▼
    ├── cad_decoder.py (M13A) ───────► generator.model (LogitsProcessor: 환각 억제)
    └── scd_decoder.py (M13B) ───────► generator.model (LogitsProcessor: 언어이탈 방지)
    [contrastive_decoder.py: 구버전 import 호환성 shim — 직접 사용 금지]
```

---

## 3. 데이터 흐름

### 3.1 인덱싱 (PDF → 벡터DB)

```
PDF 파일
  │
  ▼ PDFParser.parse()
ParsedDocument { doc_id, title, blocks: [TextBlock] }
  │
  ▼ SectionDetector.detect()
ParsedDocument (각 block에 section_type 부착)
  │
  ▼ Chunker.chunk_document()
list[Chunk] { chunk_id, doc_id, content, section_type, page, ... }
  │
  ▼ Embedder.embed_texts()
np.ndarray (N × 1024)
  │
  ▼ VectorStore.add_chunks()
ChromaDB 컬렉션에 저장 (벡터 + 메타데이터)
  │
  ▼ HybridRetriever.fit_bm25()
BM25 인덱스 구축
```

### 3.2 질의응답 (쿼리 → 답변)

```
사용자 쿼리 (한국어/영어)
  │
  ▼ QueryRouter.route()
RouteDecision { route: A|B|C|D|E, section_filter, target_doc_ids }
  │
  ▼ Pipeline 선택 (pipeline_X.run())
  │
  ├──► QueryExpander.expand()        [HyDE 가상 문서 / 다중 쿼리 / 한→영 번역]
  │
  ├──► HybridRetriever.search()      [Dense(BGE-M3) + Sparse(BM25) → RRF 결합]
  │
  ├──► Reranker.rerank()             [Cross-Encoder + 섹션 가중치 + 위치 편향 보정]
  │
  ├──► ContextCompressor.compress()  [추출 압축 / 요약 압축]
  │
  ├──► Generator.generate()          [MIDM-2.0 11.5B 생성]
  │       │
  │       ▼ (LogitsProcessor)
  │    ContrastiveDecoder.__call__()  [CAD: 파라메트릭 지식 억제]
  │
  ▼
{ answer, sources, source_documents, pipeline, steps }
```

### 3.3 데이터 스키마

#### TextBlock (PDF 파싱 결과)
```python
{
    "content": str,        # 텍스트 내용
    "page": int,           # 페이지 번호 (0-indexed)
    "font_size": float,    # 폰트 크기
    "is_bold": bool,       # 볼드 여부
    "bbox": (x0, y0, x1, y1),  # 위치 좌표
    "block_type": str,     # "text" | "table" | "image"
    "section_type": str,   # "abstract" | "method" | "result" | ...
}
```

#### Chunk (검색 단위)
```python
{
    "chunk_id": str,       # MD5 해시 기반 고유 ID
    "doc_id": str,         # 문서 ID (파일명)
    "content": str,        # 청크 텍스트
    "section_type": str,   # 섹션 타입
    "page": int,           # 페이지 번호
    "char_start": int,     # 시작 위치
    "char_end": int,       # 끝 위치
    "chunk_level": int,    # RAPTOR: 0=leaf, 1=mid, 2=root
}
```

#### ChromaDB 메타데이터
```python
{
    "doc_id": str,
    "section_type": str,
    "page": int,
    "chunk_level": int,
    "char_start": int,
    "char_end": int,
}
```

---

## 4. 모듈 상세 명세

### MODULE 1: PDFParser (`modules/pdf_parser.py`)
- **입력**: PDF 파일 경로
- **출력**: `ParsedDocument`
- **핵심**: pymupdf 블록 단위 추출, 폰트 크기 기반 제목 감지
- **제한**: 스캔 PDF(이미지 PDF)는 OCR 미지원

### MODULE 2: SectionDetector (`modules/section_detector.py`)
- **입력**: `ParsedDocument`
- **출력**: 섹션 타입이 부착된 `ParsedDocument`
- **방법**: 규칙 기반 정규식 + 폰트 크기 비율로 헤더 판별
- **감지 대상**: abstract, introduction, related_work, method, experiment, result, discussion, conclusion, references

### MODULE 3: Chunker (`modules/chunker.py`)
- **전략 3가지**:
  - `section`: 섹션 경계를 절대 넘지 않는 윈도우 청킹 (기본)
  - `fixed`: 고정 크기 청킹 (Baseline용)
  - `sentence`: 문장 단위 그룹화
- **RAPTORChunker**: leaf → 클러스터 요약(mid) → 전체 요약(root) 트리 구성

### MODULE 4: Embedder (`modules/embedder.py`)
- **모델**: `BAAI/bge-m3` (1024차원)
- **핵심**: 한영 동일 임베딩 공간 → 크로스링구얼 매칭
- **정규화**: L2 정규화 후 코사인 유사도 = 내적

### MODULE 5: VectorStore (`modules/vector_store.py`)
- **DB**: ChromaDB (PersistentClient)
- **메타데이터 필터**: `section_type`, `doc_id` 기반 필터 검색
- **배치 처리**: 500개 단위 (ChromaDB 제한 대응)

### MODULE 6: QueryRouter (`modules/query_router.py`)
- **5개 경로**: A(단순QA), B(섹션특화), C(비교), D(인용), E(요약)
- **방법**: 키워드 매칭 스코어 기반 (config.ROUTE_MAP)
- **출력**: `RouteDecision { route, section_filter, target_doc_ids, confidence }`

### MODULE 7: QueryExpander (`modules/query_expander.py`)
- **HyDE**: 가상 답변 문서 생성 → 해당 문서로 검색
- **RAG-Fusion**: 쿼리를 3가지 표현으로 확장
- **한→영 번역**: 한국어 쿼리를 영어로도 변환하여 병렬 검색

### MODULE 8: HybridRetriever (`modules/hybrid_retriever.py`)
- **Dense**: BGE-M3 벡터 유사도 (의미적 매칭)
- **Sparse**: BM25 키워드 (정확한 용어, 저자명)
- **융합**: Reciprocal Rank Fusion (k=60)
- **가중치**: Dense 0.6 + Sparse 0.4 (config에서 조절)

### MODULE 9: Reranker (`modules/reranker.py`)
- **모델**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **섹션 가중치**: 쿼리 라우터의 섹션 정보에 따라 boost
- **위치 편향 보정**: Lost in the Middle — 중요 청크를 앞/뒤에 배치

### MODULE 10: ContextCompressor (`modules/context_compressor.py`)
- **추출 압축**: 쿼리 용어 겹침 기반 문장 선택 (LLMLingua 근사)
- **요약 압축**: LLM으로 쿼리 관련 요약 생성 (RECOMP)
- **절단**: 토큰 한계(3072) 초과 시 문서 리스트 절단

### MODULE 11: CitationTracker (`modules/citation_tracker.py`)
- **파싱**: 정규식으로 Reference 섹션에서 제목/저자/연도/arXiv ID 추출
- **수집**: arXiv API로 메타데이터 + PDF URL 가져오기
- **인덱싱**: 수집된 논문을 자동으로 벡터DB에 추가

### MODULE 12: Generator (`modules/generator.py`)
- **모델**: `K-intelligence/Midm-2.0-Base-Instruct` (bfloat16, device_map="auto")
- **템플릿**: QA / Compare / Summary 3종
- **시스템 프롬프트**: 컨텍스트 기반 답변 강제 + 한국어 생성 + 전문용어 영어 병기

### MODULE 13A: CADDecoder (`modules/cad_decoder.py`) — 핵심 기여 C3

- **수식**: `Logit_final = Logit(context) - α × Logit(empty_context)`
- **구현**: HuggingFace `LogitsProcessor` 인터페이스
- **α**: 0.5 기본값, JSD(Jensen-Shannon Divergence) 기반 적응적 동적 조절 가능
- **KV Cache**: 첫 스텝 이후 KV cache 재사용으로 추론 오버헤드 최소화
- **학술 기여**: 한국어 학술 RAG에서 CAD 효과를 평가한 최초 구현 — Shi et al. (NAACL 2024) 대비 한국어/학술 도메인 확장

### MODULE 13B: SCDDecoder (`modules/scd_decoder.py`)

- **기반**: Li et al. (arXiv 2511.09984, 2025) Selective Context-aware Decoding
- **수식**: 비목표 언어 토큰의 logit에서 β를 차감
- **허용 토큰**: 한글(AC00-D7A3), 숫자, 공백, 구두점
- **목적**: 영문 논문 컨텍스트에서 생성 언어가 영어로 이탈하는 것을 방지
- **CAD와 결합**: `LogitsProcessorList([cad, scd])`로 동시 적용

> `contrastive_decoder.py`는 구버전 import 호환성을 위한 shim입니다. 직접 사용하지 마세요.

---

## 5. 파이프라인 설계

### 경로 A: 단순 QA (`pipeline_a_simple_qa.py`)
```
쿼리 → HyDE 확장 → 하이브리드 검색 → 재랭킹 → 압축 → 생성+CAD → 답변
```

### 경로 B: 섹션 특화 (`pipeline_b_section.py`)
```
쿼리 → 섹션 필터 검색 → (부족 시 전체 검색 보완) → 섹션 boost 재랭킹 → 생성+CAD → 답변
```

### 경로 C: 멀티 논문 비교 (`pipeline_c_compare.py`)
```
쿼리 → 논문별 병렬 검색 (ThreadPoolExecutor) → 재랭킹 → 합성 → 비교 템플릿 생성 → 표 형식 답변
```

### 경로 D: 인용 추적 (`pipeline_d_citation.py`)
```
쿼리 → Reference 파싱 → arXiv API 수집 → PDF 다운로드 → 자동 인덱싱 → BM25 재구축 → 확장 검색 → 생성 → 답변
```

### 경로 E: 전체 요약 (`pipeline_e_summary.py`)
```
쿼리 → 섹션별(5개) 검색 → 전체 검색 보완 → 재랭킹 → 섹션 순서 정렬 → 요약 템플릿 생성 → 구조화 답변
```

---

## 6. 핵심 알고리즘

### 6.1 Reciprocal Rank Fusion (RRF)

```
RRF_score(d) = Σ weight_i / (k + rank_i(d))
```

- Dense 가중치: 0.6, Sparse 가중치: 0.4
- k = 60 (smoothing constant)
- 두 검색 결과의 chunk_id 기준으로 스코어 합산

### 6.2 Context-Aware Contrastive Decoding (CAD)

```
Logit_final = Logit(context_prompt) - α × Logit(empty_prompt)
```

- `context_prompt`: "[시스템] [컨텍스트: 검색 문서] [질문] [답변]"
- `empty_prompt`: "[시스템] [컨텍스트: (없음)] [질문] [답변]"
- α: 0.5 (기본값), 0.0~1.0 범위 조절 가능
- 적응적 모드: JSD(context_probs, empty_probs)로 α 자동 조절

### 6.3 Lost in the Middle 보정

재랭킹 결과를 지그재그 배치:
```
입력: [1위, 2위, 3위, 4위, 5위]  (점수 순)
출력: [1위, 3위, 5위, 4위, 2위]  (짝수 → 앞, 홀수 → 뒤 역순)
```

LLM이 컨텍스트의 처음/끝을 더 잘 기억하는 특성 활용.

---

## 7. 평가 프레임워크

### 7.1 RAGAS 4대 지표

| 지표 | 측정 대상 | 계산 방법 |
|---|---|---|
| Faithfulness | 답변이 컨텍스트에 근거하는지 | LLM 판정 (0~1) |
| Answer Relevancy | 답변이 질의와 관련있는지 | LLM 판정 (0~1) |
| Context Precision | 검색 청크 중 관련 비율 | LLM 판정 (0~1) |
| Context Recall | 정답에 필요한 정보가 검색됐는지 | LLM 판정 (0~1) |

LLM 미사용 시 토큰 오버랩 기반 휴리스틱으로 대체.

### 7.2 Ablation Study 구성 (6단계)

| # | 시스템 | 추가 모듈 |
|---|---|---|
| 1 | Naive RAG | 고정 500토큰 청킹 + 벡터 검색 + 생성 |
| 2 | + Section Chunking | 섹션 인식 청킹 |
| 3 | + Hybrid Search | BM25 + Dense + RRF |
| 4 | + Reranker | Cross-Encoder 재랭킹 |
| 5 | + Query Router + HyDE | 동적 라우팅 + 가상 문서 검색 |
| 6 | **Full System** | + CAD 환각 억제 + 컨텍스트 압축 |

### 7.3 CAD Alpha Ablation

α ∈ {0.1, 0.3, 0.5, 0.7, 1.0} 5단계 실험.

---

## 8. 확장 가이드

### 8.1 새 파이프라인 경로 추가

1. `config.py`의 `ROUTE_MAP`에 새 키워드 추가
2. `modules/query_router.py`의 `RouteType` enum에 경로 추가
3. `pipelines/pipeline_x_name.py` 생성 (`run()` 함수 구현)
4. `api/routers/chat.py`의 `_run_pipeline()`에 분기 추가

### 8.2 생성 모델 교체

`config.py`의 `GENERATION_MODEL` 변경:
```python
GENERATION_MODEL = "your-model/name"
```

HuggingFace AutoModelForCausalLM 호환 모델이면 교체 가능.

### 8.3 임베딩 모델 교체

`config.py`의 `EMBEDDING_MODEL`과 `EMBEDDING_DIMENSION` 변경.

> 모델 교체 시 기존 ChromaDB를 삭제하고 재인덱싱 필요.

### 8.4 검색 방식 변경

`hybrid_retriever.py`의 `DENSE_WEIGHT` / `BM25_WEIGHT` 비율 조정,
또는 `_rrf_fusion()` 메서드에 새 검색 소스 추가.
