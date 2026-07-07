# M-RAG 기능 정리

## 문서 목적

이 문서는 현재 코드에 존재하는 기능을 연구 기능, 대화 기능, 운영 기능, 실험 기능으로 나누어 설명한다

---

## 연구 기능

논문 클레임과 실험 ablation에 직접 연결되는 기능이다

| 기능 | 코드 근거 | 목적 |
|---|---|---|
| A~E 연구 질의 라우팅 | `backend/modules/query_router.py` | 단순 QA, 섹션 질의, 비교, 인용, 요약 경로 선택 [7, 8, 17] |
| 하이브리드 검색 | `backend/modules/hybrid_retriever.py` | Dense(BGE-M3, weight 0.6) + BM25(weight 0.4) + weighted RRF 결합 [2, 22, 23] |
| 재랭킹 | `backend/modules/reranker.py` | Cross-encoder로 검색 결과 순서 개선 [14] |
| 컨텍스트 압축 | `backend/modules/context_compressor.py` | 추출/생성 압축으로 근거 압축 [11, 12, 19] |
| CAD | `backend/modules/cad_decoder.py` | 파라메트릭 지식 개입 억제 (α=0.5) [3, 4] |
| SCD | `backend/modules/scd_decoder.py` | Language Drift 억제 (β=0.3) [34] |
| 인용 추적 | `backend/modules/citation_tracker.py` | arXiv/Semantic Scholar 기반 인용/참고문헌 질문 지원 |

---

## 대화 기능

서비스에서 사용자의 논문 탐색 흐름을 이어 주는 기능이다

| 기능 | 코드 근거 | 실행 위치 |
|---|---|---|
| 후속 질문 제안 | `backend/modules/followup_generator.py` | A~F 답변 이후 |
| 퀴즈 생성 | `backend/pipelines/pipeline_f_quiz.py` | F 경로 |
| 플래시카드 생성 | `backend/pipelines/pipeline_f_quiz.py` | F 경로 |

F 경로는 운영/서비스 관점의 학습 보조 경로다. 논문 실험 표는 A–E 연구 경로와 CAD/SCD 효과를 중심으로 구성하고, F 경로는 실제 챗봇 기능 설명과 시연 문서에서 다룬다

---

## 운영 기능

서비스 사용성과 운영에 필요한 기능이다

| 기능 | 코드 근거 | 목적 |
|---|---|---|
| PDF/DOCX/TXT 업로드 | `backend/api/routers/papers.py` | 문서 수집과 인덱싱 |
| 사용자별 collection 격리 | `namespace_collection_name` in `papers.py` | 사용자 데이터 분리 |
| SSE 스트리밍 | `/api/chat/query/stream` | 답변을 점진적으로 전달 |
| 검색 전용 API | `/api/chat/search` | 검색 결과 점검 |
| Judge API | `/api/chat/judge` | 실험 평가와 라벨 판정 |
| PPT Export | `/api/chat/export/ppt` | 답변과 출처를 발표 자료로 변환 |
| 특허 추적 | `backend/modules/patent_tracker.py` | 특허 문서와 prior art 질의 지원 |
| 대화 이력 | `backend/api/routers/history.py` | 채팅 세션 저장 |

---

## 실험 기능

논문 결과 재현을 위한 기능이다

| 기능 | 코드 근거 | 목적 |
|---|---|---|
| 본 생성 실행 | `experiments/runners/run_generation.py` (+ `main_generation_executor.py`) | 8-config HyDE×CAD×SCD 본 생성 (하드 가드) |
| 튜닝/메모리 프로브 | `experiments/runners/run_alice_followup.py` | 고정 backbone 튜닝 비교, worst-case VRAM 프로브 |
| 파라미터 freeze | `experiments/runners/prepare_parameter_freeze.py` | scored 결과 기반 `frozen_params.yaml` 작성 |
| 공식 RAGAS 평가 | `experiments/evaluators/official_ragas_runner.py` | NVIDIA NIM judge로 4-메트릭 채점 |
| 점수 집계/표 변환 | `experiments/analyzers/aggregate_main_scores.py` | config별 CSV + 축별 요인효과 JSON |
| 언어 준수 분석 | `experiments/analyzers/scd_language_adherence.py` | SCD 한국어 비율 직접 측정 |
| dry-run 검증 | `experiments/runners/dry_run_matrix.py` | 계획/설정 정적 검증 |

---

## 실행 경로 선택 기준

| 목적 | 기준 경로 |
|---|---|
| 논문 실험 | MIDM Base + transformers 직접 디코딩 + SQLite + SQLAlchemy |
| 로컬 스모크 검증 | MIDM Mini + SQLite + SQLAlchemy |
| 운영/서비스 | MIDM Base + PostgreSQL + SQLAlchemy + ChromaDB |
| 다음 단계 추론 최적화 연구 | vLLM 기반 별도 연구 계획 |

참고문헌 번호(`[N]`)는 `docs/PAPER/THESIS.md`의 참고문헌 목록 기준이다 (총 39편)

