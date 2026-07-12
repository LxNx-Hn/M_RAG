# M-RAG 전체 리포지토리 쉬운 안내서

이 문서는 처음 보는 사람이 코드, 서비스, 실험, 논문을 하나의 흐름으로 이해하기 위한 출발점이다. 세부 구현을 모두 복제하지 않고, 어떤 질문에 어느 파일을 읽어야 하는지와 서로 다른 산출물을 섞으면 안 되는 이유를 설명한다.

## 1. M-RAG는 무엇인가

M-RAG에는 두 계층이 있다.

1. **연구 계층:** 한국어 질문으로 영어 논문을 검색하고 답할 때 HyDE, CAD, SCD가 어떤 영향을 주는지 통제 실험한다.
2. **서비스 계층:** 사용자가 논문을 올리고, 질문하고, 출처를 확인하고, 비교·요약·퀴즈를 만들 수 있는 FastAPI + React 애플리케이션이다.

서비스 A-F route는 사용 편의를 위한 기능 구조다. 논문의 새 알고리즘은 아니다. 논문의 연구 기여는 고정된 Paper-RAG backbone 위에서 세 요소를 8개 조합으로 비교한 것이다.

## 2. 가장 먼저 읽을 파일

| 알고 싶은 내용 | 읽을 파일 |
|---|---|
| 프로젝트 한눈에 보기 | `README.md` |
| 국문 전체 논문 | `docs/PAPER/THESIS_KO.md` |
| 영문 전체 논문 | `docs/PAPER/THESIS.md` |
| 최신 SCD 결과를 아주 쉽게 이해하기 | `experiments/reports/reference_scd_rerun_explainer_KO.md` |
| 핵심 용어 | `docs/EXPLAIN/TERMS_GLOSSARY_KO.md` |
| 코드 구조 | `docs/ARCHITECTURE.md`와 `docs/EXPLAIN/ARCHITECTURE_EXPLAINED_KO.md` |
| 업로드부터 답변까지 | `docs/EXPLAIN/FLOW_EXPLAINED_KO.md` |
| 기능별 코드 위치 | `docs/FEATURES.md`와 `docs/EXPLAIN/FEATURES_EXPLAINED_KO.md` |
| 실험표 읽는 법 | `docs/EXPLAIN/TABLE_INTERPRETATION_GUIDE.md` |
| 참고문헌 검증 | `docs/PAPER/REFERENCE_AUDIT_2026-07-11.md` |

## 3. 서비스 코드 지도

### Backend

`backend/api/main.py`가 FastAPI 진입점이다. router, 인증, 데이터베이스, 요청·응답 model은 `backend/api/`에 있다. 사용자가 요청을 보내면 API 계층이 필요한 paper collection과 pipeline을 선택하고, streaming 응답이면 SSE 형식으로 결과를 전달한다.

RAG 구성요소는 `backend/modules/`에 있다.

- 문서 parsing과 chunking
- dense embedding 및 vector retrieval
- BM25 sparse retrieval
- weighted RRF fusion
- CrossEncoder reranking
- context construction과 compression
- Mi:dm generation
- CAD/SCD decoding control
- citation, follow-up, PPT export

질의 목적별 A-F pipeline은 `backend/pipelines/`에 있다. route A는 단순 QA, B는 절 중심 QA, C는 비교, D는 인용·서지 탐색, E는 구조화 요약, F는 퀴즈·플래시카드다. route가 달라도 논문 주실험에서는 route별 로직을 섞지 않고 고정 experiment runner를 사용한다.

### Frontend

`frontend/src/`는 Vite + React + TypeScript 애플리케이션이다. 주요 역할은 다음과 같다.

- 논문 업로드와 목록 관리
- 활성 문서 선택
- 채팅 질의와 SSE streaming 표시
- 근거 source panel
- PDF viewer
- 사용자·논문·채팅 상태 store
- backend API client

frontend가 점수를 계산하거나 논문 실험을 실행하지 않는다. 연구 점수는 `experiments/`의 평가기에서 생성된다.

## 4. 한 질문이 답변이 되기까지

1. 사용자가 PDF를 업로드한다.
2. backend가 텍스트와 metadata를 추출한다.
3. section detection 후 문서를 chunk로 나눈다.
4. 각 chunk를 BGE-M3 embedding과 BM25 색인에 저장한다.
5. 사용자가 한국어로 질문한다.
6. 서비스 router가 A-F 목적을 선택한다.
7. dense retrieval과 BM25가 각각 후보를 찾는다.
8. dense 0.6 / BM25 0.4 weighted RRF로 순위를 합친다.
9. CrossEncoder가 후보를 다시 정렬한다.
10. 상위 문맥을 생성 prompt에 넣는다.
11. 설정에 따라 HyDE, CAD, SCD가 적용된다.
12. Mi:dm이 답변을 생성하고 backend가 답변·출처·metadata를 반환한다.
13. frontend가 streaming 답변과 source를 화면에 표시한다.

## 5. 세 연구 요소

### HyDE

짧은 한국어 질문을 가상의 답변형 문서로 확장해 검색 representation으로 사용한다. 더 많은 관련 근거를 찾을 수 있지만 관련 없는 chunk도 들어올 수 있다. 실제 결과도 answer relevancy와 recall은 올랐고 precision은 낮아졌다.

### CAD

문맥이 있을 때와 없을 때 같은 모델의 token score를 대조한다. 문서가 없어도 쉽게 나오는 token보다 문서 근거가 있을 때 강해지는 token을 우선한다. 원본 실험에서 faithfulness가 `+0.044` 개선됐다.

### SCD

한국어 목표 token을 강화하고 방해 언어 token을 낮춰 영어 문장 이탈을 줄인다. 원본 `penalty_additive v1`은 참조 방법의 핵심을 빠뜨려 실패했다. 수정된 `reference_scd`는 한국어 비율을 평균 `+0.2203` 개선했지만 RAG 품질의 안정적인 개선·저하는 교차 judge에서 확정되지 않았다.

## 6. 실험 코드 지도

| 역할 | 위치 |
|---|---|
| 실행 계획과 generation | `experiments/runners/` |
| 공식 RAGAS 평가 | `experiments/evaluators/official_ragas_runner.py` |
| 대칭 SCD 평가 입력 준비 | `experiments/evaluators/prepare_scd_symmetric_eval.py` |
| 점수 집계·요인효과 분석 | `experiments/analyzers/` |
| Alice GPU 설정·실행 | `experiments/scripts/alice/` |
| 질의 split과 GT | `experiments/queries/`, `experiments/gt/` |
| 실행 결과 | `experiments/results/` |
| 사람이 읽는 공식 보고서 | `experiments/reports/` |

주실험 생성 모델은 `K-intelligence/Midm-2.0-Base-Instruct`다. Mini 모델은 로컬 smoke 검사용 fallback이며 논문 주실험 결과로 대체하면 안 된다. 논문 실험은 GPU/Alice 경로를 canonical 실행 환경으로 사용한다.

## 7. 공식 산출물과 역사적 산출물

가장 중요한 원칙은 이름이 비슷한 결과를 합치지 않는 것이다.

### 원본 Phase 8

- 19질의 × 8설정 = 152생성
- `penalty_additive v1` SCD
- 고정 NVIDIA NIM judge
- 583/608 RAGAS 셀
- v1 SCD는 null 결과

이 결과는 실패 이력과 감사 근거로 보존한다.

### 수정된 reference_scd

- 별도 experiment ID와 결과 파일
- `alpha=1.1`, `beta=0.9`, `Tstart=5`
- 직접 한국어 준수율 `+0.2203`
- 76쌍 중 68개 개선, 3개 악화, 5개 동률

### 대칭 교차 judge

- HyDE-off byte-identical context 38쌍
- 영어·한국어 동일 정규화 정책
- `gpt-4o`와 고정 `gpt-4.1-2025-04-14`
- query-clustered bootstrap 10,000회
- RAG 품질의 judge-robust 비영점 효과는 확립되지 않음

## 8. RAGAS와 평가 경계

공식 평가는 RAGAS 0.2.15 패키지를 사용한다. 프로젝트가 RAGAS 점수 공식을 임의로 다시 만든 것이 아니다. `official_ragas_runner.py`는 judge 연결, 로컬 embedding, 재시도, null 기록, provenance, 최종 산출물 저장을 관리한다.

원본 NIM 평가에서 timeout인 25개 셀은 null이며 0점으로 대체하지 않는다. 서로 다른 judge의 절대점수를 직접 비교하지 않고, 같은 judge·프로토콜 안에서 matched factor delta를 본다.

숫자 환각과 query-type 효과는 현재 미측정이다. 숫자 환각은 숫자·단위·대상 entity를 paper evidence와 대조한 별도 주석이 필요하고, query-type 효과는 유형마다 충분한 독립 질의가 필요하다.

## 9. 논문과 코드의 관계

`THESIS.md`와 `THESIS_KO.md`의 구현 주장은 저장소 코드와 연결된다. 결과 수치는 `experiments/results/analysis/` 및 공식 보고서와 연결된다. 참고문헌은 외부 방법과 평가 근거를 제공하며 [1]–[20]은 `REFERENCE_AUDIT_2026-07-11.md`에서 확인됐다.

논문이 주장하지 않는 것은 다음과 같다.

- A-F router가 새로운 알고리즘이라는 주장
- SCD가 RAG 품질을 반드시 개선한다는 주장
- v1 SCD 실패가 참조 SCD 방법의 실패라는 주장
- 질의 유형별 route 정책이 정량 검증됐다는 주장
- 숫자 환각률이 0이라는 주장
- 4개 논문·19개 질의 결과가 모든 학문 분야에 일반화된다는 주장

## 10. 로컬 실행과 검증

### Backend 검증

```powershell
python -m pytest tests -q
python -m pytest experiments/tests -q
```

실험 테스트는 저장소 루트에서 실행해야 `experiments` package import가 정상 동작한다.

### Frontend 검증

```powershell
cd frontend
npm run lint
npm run build
```

### 실험 계획만 확인

```powershell
python experiments\runners\run_tuning_plan.py --dry-run --plan-only --limit 5
python experiments\runners\dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
python experiments\runners\run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3
```

API key가 필요한 실제 평가를 dry-run과 혼동하면 안 된다. 특히 공식 NIM RAGAS는 `NVIDIA_API_KEY`가 없으면 실행할 수 없다. OpenAI 기반 후속 평가도 기존 공식 결과를 덮어쓰지 않고 별도 experiment와 provenance로 저장해야 한다.

## 11. 배포와 운영 경계

개발 backend는 FastAPI, frontend는 Vite dev server로 실행할 수 있다. GPU 모델을 직접 올릴 때는 `LOAD_GPU_MODELS`, 모델 이름, JWT secret 등 환경설정이 필요하다. 실험용 기본 DB는 SQLite이며 운영 서비스 경로는 PostgreSQL이다.

현재 저장소는 졸업프로젝트 demo와 연구 재현에는 충분하지만, 임의 사용자 대상 운영 완성으로 주장하려면 다음이 더 필요하다.

- 실제 배포 환경 end-to-end 검증
- 동시 사용자 부하 시험
- 지연시간·오류율·GPU memory 관측성
- 사용자 데이터 보존·삭제 정책
- secret rotation과 운영 보안 점검
- frontend component/E2E test
- 실제 server를 띄운 API integration test

## 12. 논문 제출 산출물

`docs/PAPER/output/`에는 국·영문 DOCX와 PDF가 있다. 이는 A4 일반 학술 원고 형식이며 내용·표·그림 렌더를 검증했다. 학교 고유 표지와 인준 페이지는 저자, 학번, 학과, 지도교수, 제출연월과 공식 템플릿이 필요하므로 `docs/PAPER/SUBMISSION_METADATA.md`를 확인한 뒤 적용한다.

## 13. 새 작업자가 지켜야 할 규칙

1. 결과가 마음에 들지 않는다고 judge를 계속 바꿔 유리한 결과만 채택하지 않는다.
2. 원본 v1과 수정 SCD 결과를 같은 평균으로 합치지 않는다.
3. null을 0으로 바꾸지 않는다.
4. 측정하지 않은 숫자 환각·query-type 효과를 결과처럼 쓰지 않는다.
5. 서비스 route와 논문 method를 구분한다.
6. 논문 결과를 바꿀 때 공식 artifact, 보고서, 국·영문 원고, 쉬운 문서를 함께 동기화한다.
7. 실험 실행 전 dry-run, split, frozen parameter, 비용, API key를 확인한다.
8. 한글 문서는 UTF-8로 저장한다.

이 규칙을 지키면 새 참여자도 코드의 기능, 실험의 근거, 논문의 주장 범위를 서로 혼동하지 않고 프로젝트를 이어갈 수 있다.
