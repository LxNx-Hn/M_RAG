# M-RAG 기능 정리

## 문서 목적

이 문서는 현재 코드에 존재하는 기능을 연구 기능, 대화 기능, 운영 기능, 실험 기능으로 나누어 설명한다

---

## 연구 기능

논문 클레임과 실험 ablation에 직접 연결되는 기능이다

| 기능 | 코드 근거 | 목적 |
|---|---|---|
| A~E 연구 질의 라우팅 | `backend/modules/query_router.py` | 단순 QA, 섹션 질의, 비교, 인용, 요약 경로 선택 [7, 8, 17] |
| 하이브리드 검색 | `backend/modules/hybrid_retriever.py` | Dense(BGE-M3) + BM25 + RRF 결합 [2, 22, 23] |
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

F 경로는 운영/서비스 관점의 학습 보조 경로다. 논문 실험 표는 A~E 연구 경로와 CAD/SCD 효과를 중심으로 구성하고, F 경로는 실제 챗봇 기능 설명과 시연 문서에서 다룬다

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
| 전체 실행 | `backend/scripts/master_run.py` | end-to-end 실험 자동화 |
| Track 1 실행 | `backend/evaluation/run_track1.py` | 모듈 누적 ablation, decoder ablation |
| Track 2 실행 | `backend/evaluation/run_track2.py` | 논문 도메인 특화 비교 |
| RAGAS 스타일 평가 | `backend/evaluation/ragas_eval.py` | 자동 평가 점수 산출 |
| Markdown 표 변환 | `backend/scripts/results_to_markdown.py` | 결과 JSON을 논문 표로 변환 |
| 배포 검증 | `backend/scripts/verify_deployment.py` | 필수 import와 실행 환경 확인 |

---

## 실행 경로 선택 기준

| 목적 | 기준 경로 |
|---|---|
| 논문 실험 | MIDM Base + transformers 직접 디코딩 + SQLite + SQLAlchemy |
| 로컬 스모크 검증 | MIDM Mini + SQLite + SQLAlchemy |
| 운영/서비스 | MIDM Base + PostgreSQL + SQLAlchemy + ChromaDB |
| 다음 단계 추론 최적화 연구 | vLLM 기반 별도 연구 계획 |

참고문헌 번호(`[N]`)는 `docs/PAPER/THESIS.md`의 참고문헌 목록 기준이다 (총 39편)
