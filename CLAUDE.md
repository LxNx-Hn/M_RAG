# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (from repo root)
pip install -r backend/requirements.txt

# Pre-download all models (GPU required for LLM)
python backend/scripts/download_models.py
python backend/scripts/download_models.py --skip-llm  # CPU 환경

# Run the Streamlit app
streamlit run backend/app.py

# Run RAGAS evaluation
python -m backend.evaluation.ragas_eval

# Run ablation study
python -m backend.evaluation.ablation_study
```

## Architecture

M-RAG는 **쿼리 유형에 따라 파이프라인이 동적으로 분기**되는 Modular RAG 시스템입니다. 학술 논문 PDF를 업로드하면 한국어로 질의응답합니다.

### 핵심 흐름

1. **인덱싱**: PDF → `PDFParser(M1)` → `SectionDetector(M2)` → `Chunker(M3)` → `Embedder(M4)` → `VectorStore(M5)` + BM25
2. **질의응답**: 쿼리 → `QueryRouter(M6)` → 5개 파이프라인 중 1개 → 답변

### 파이프라인 라우팅 (`backend/modules/query_router.py`)

`QueryRouter`가 키워드 매칭(`config.ROUTE_MAP`)으로 경로를 결정:

| 경로 | 파일 | 특징 |
|------|------|------|
| A (단순QA) | `pipeline_a_simple_qa.py` | HyDE 확장 → 하이브리드 검색 → CAD 생성 |
| B (섹션특화) | `pipeline_b_section.py` | 섹션 필터 검색 → 섹션 boost 재랭킹 |
| C (비교) | `pipeline_c_compare.py` | 논문별 병렬 검색(ThreadPoolExecutor) → 비교 템플릿 |
| D (인용추적) | `pipeline_d_citation.py` | arXiv API → PDF 자동 다운로드 → 재인덱싱 |
| E (요약) | `pipeline_e_summary.py` | 섹션별 5회 검색 → 구조화 요약 |

### 13개 모듈 (`backend/modules/`)

```
M1  pdf_parser.py          pymupdf 기반 블록 추출
M2  section_detector.py    정규식 + 폰트크기 헤더 판별
M3  chunker.py             section/fixed/sentence 3가지 전략 + RAPTORChunker
M4  embedder.py            BAAI/bge-m3 (1024차원, 한영 동일 공간)
M5  vector_store.py        ChromaDB PersistentClient
M6  query_router.py        키워드 스코어 → RouteDecision
M7  query_expander.py      HyDE / RAG-Fusion / 한→영 번역
M8  hybrid_retriever.py    Dense(BGE-M3) + BM25 → RRF 융합
M9  reranker.py            cross-encoder + 섹션가중치 + Lost-in-the-Middle 보정
M10 context_compressor.py  추출/요약 압축, 3072 토큰 한계
M11 citation_tracker.py    Reference 섹션 파싱 → arXiv API
M12 generator.py           EXAONE-3.5-7.8B-Instruct (FP16, device_map=auto)
M13 contrastive_decoder.py CAD LogitsProcessor (파라메트릭 지식 억제)
```

### 설정 (`backend/config.py`)

모든 하이퍼파라미터의 단일 진실 원천. 자주 바뀌는 값들:
- `GENERATION_MODEL` — LLM 교체 시 여기만 변경 (HuggingFace CausalLM 호환)
- `EMBEDDING_MODEL` + `EMBEDDING_DIMENSION` — 임베딩 교체 시 **ChromaDB 삭제 후 재인덱싱 필요**
- `CAD_ALPHA` — 환각 억제 강도 (0.0~1.0)
- `DENSE_WEIGHT` / `BM25_WEIGHT` — 하이브리드 검색 가중치 (합계 1.0)
- `ROUTE_MAP` — 라우터 키워드 추가/수정

### 데이터 스키마

- `ParsedDocument`: PDF 파싱 결과 (`doc_id`, `title`, `blocks: list[TextBlock]`)
- `Chunk`: 검색 단위 (`chunk_id`, `doc_id`, `content`, `section_type`, `page`, `chunk_level`)
- `RouteDecision`: 라우터 출력 (`route`, `section_filter`, `target_doc_ids`, `confidence`)
- 파이프라인 반환: `{ answer, sources, source_documents, pipeline, steps }`

### 저장소 경로

- `backend/chroma_db/` — ChromaDB 영속 저장소
- `backend/data/` — 업로드된 PDF 파일

### 새 파이프라인 경로 추가 방법

1. `config.ROUTE_MAP`에 키워드 추가
2. `query_router.py`의 `RouteType` enum에 경로 추가
3. `pipelines/pipeline_x_name.py` 생성 (`run()` 함수)
4. `app.py`의 `process_query()`에 분기 추가

### 모델 요구사항

- **LLM (EXAONE-3.5-7.8B)**: GPU 24GB+ VRAM 필요. 없으면 Generator 로드 실패 시 검색 결과만 반환
- **Embedding (BGE-M3)**: CPU 가능하나 느림
- **Reranker**: CPU 가능

### 배포 계획 (memo.md 기준)

- 실제 배포 시 EXAONE → **MIDM** 교체 예정 (vLLM 서빙)
- 아키텍처: Kubernetes + Docker Compose (BE / FE / LM / DB 레이어 분리)
