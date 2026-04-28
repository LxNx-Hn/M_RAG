# 35편 기준 문서 동기화 기록

## 기준

- 기준 원문 `C:/Users/KiKi/Downloads/modular_rag_guideline.md`
- 기준 성격 35편 참고문헌 기반 전체 설계 가이드
- 코드 기준 `backend/modules`, `backend/pipelines`, `backend/api/routers`, `backend/evaluation`, `backend/scripts`

## 현재 문서 체계

| 영역 | 위치 | 역할 |
|---|---|---|
| 루트 소개 | `README.md` | 프로젝트 개요와 핵심 실행 경로 |
| 아키텍처 | `docs/ARCHITECTURE.md` | 현재 코드 구조와 A~F 경로별 모듈 동작 |
| 기능 | `docs/FEATURES.md` | 연구 기능, 대화 기능, 운영 기능, 실험 기능 분리 |
| 논문 | `docs/PAPER/THESIS.md` | 제출용 논문 본문 초안 |
| 설계 기준 | `docs/PAPER/GUIDE_ORIGINAL.md` | 35편 기준 전체 설계 문서 |
| 발표 요약 | `docs/PAPER/PPT_SUMMARY.md` | PPT 제작용 개조식 요약 |
| 발표 키워드 | `docs/PAPER/PPT_KEYWORDS.md` | PPT 제작용 키워드 요약 |
| 설명 문서 | `docs/EXPLAIN` | 비전공자용 구조, 용어, 흐름, 표 해석 설명 |
| 사용법 | `docs/USAGE` | 로컬, RunPod, Alice, DB, 테스트 실행법 |

## 연구 문서와 운영 문서의 분리 기준

| 분류 | 문서 중심 | 코드 중심 |
|---|---|---|
| 연구 | Track 1, Track 2, CAD, SCD, A~E 경로 | `run_track1.py`, `run_track2.py`, `ragas_eval.py`, 검색/생성 모듈 |
| 운영/서비스 | F 퀴즈, 후속 질문, PPT Export, Search/Judge API, SSE | `pipeline_f_quiz.py`, `followup_generator.py`, `pptx_exporter.py`, `chat.py` |
| 실행 | SQLite 실험, PostgreSQL 운영, RunPod/Alice 실행 | `master_run.py`, `database.py`, `docker-compose.yml` |

## 현재 모듈 기준

현재 `backend/modules` 기준 전체 모듈 파일은 18개다

연구 핵심 모듈 13개

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

운영/입출력 모듈 5개

- `pdf_parser.py`
- `docx_parser.py`
- `patent_tracker.py`
- `pptx_exporter.py`
- `vector_store.py`

## A~F 경로 기준

| 경로 | 분류 | 설명 |
|---|---|---|
| A | 연구 | 단순 질의응답 |
| B | 연구 | 섹션 특화 질의응답 |
| C | 연구 | 여러 문서 비교 |
| D | 연구 + 운영 | 인용/특허 추적 |
| E | 연구 | 전체 요약 |
| F | 운영/학습 보조 | 퀴즈/플래시카드 생성 |

경로별 모듈 동작 상세 설명은 `docs/EXPLAIN/ROUTE_MODULE_MATRIX_KO.md`와 `docs/ARCHITECTURE.md`를 기준으로 한다

## 모델과 DB 기준

| 목적 | 기준 |
|---|---|
| 논문 실험 | MIDM Base + transformers 직접 디코딩 |
| 로컬 스모크 검증 | MIDM Mini |
| 논문 실험 DB | SQLite + SQLAlchemy |
| 운영/서비스 DB | PostgreSQL + SQLAlchemy |
| 벡터 저장소 | ChromaDB |

## 검증 항목

- `GUIDE_ORIGINAL.md`에 35편 참고문헌 반영
- `THESIS.md`에 연구 범위와 운영 기능 분리
- `ARCHITECTURE.md`에 A~F 경로별 활성 모듈 표 반영
- `FEATURES.md`에 연구 기능, 대화 기능, 운영 기능, 실험 기능 분리
- `EXPLAIN`에 용어, 구조, 흐름, 경로별 모듈, 참고문헌, 표 해석 문서 반영
- `USAGE`에 로컬, RunPod, Alice, PostgreSQL, 테스트 문서 반영
- 삭제된 문서명과 과거 구조 참조 제거
- Markdown 로컬 링크 검증
- `git diff --check` 검증

## 완료 상태

- 상태 완료
- 기준 현재 코드와 35편 설계 문서
- 후속 문서 수정 조건 코드 구조, 실험 경로, 모델 정책, DB 정책 변경
