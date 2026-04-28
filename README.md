# M-RAG

M-RAG는 한국어 중심 학술 문서 질의응답을 위한 모듈러 RAG 시스템이다. 질문 유형을 A~F 경로로 라우팅하고, BGE-M3 기반 검색, BM25, RRF, reranker, context compression, MIDM Base 생성, CAD/SCD 생성 제어를 결합한다.

## 핵심

- 논문 기본 모델은 `K-intelligence/Midm-2.0-Base-Instruct`
- Mini 모델은 로컬 스모크 검증용
- 논문 실험 빠른 실행은 SQLite + SQLAlchemy
- 운영/서비스 경로는 PostgreSQL + SQLAlchemy
- 논문 실험 경로는 MIDM Base 직접 디코딩을 기준으로 함

## 주요 기능

- PDF/DOCX/TXT 업로드
- 사용자별 문서 collection 격리
- A~F 질의 라우팅
- Hybrid retrieval + reranker
- CAD 기반 환각 억제
- SCD 기반 언어 이탈 억제
- 인용/특허 추적
- 퀴즈/플래시카드 생성
- SSE 스트리밍
- Judge/Search/PPT Export API

## 빠른 실행

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend\requirements.txt
```

```powershell
cd backend
$env:JWT_SECRET_KEY = "mrag-experiment-local-secret-2026"
$env:LOAD_GPU_MODELS = "true"
python scripts\master_run.py --skip-download
```

## 개발 서버

```powershell
cd backend
$env:JWT_SECRET_KEY = "change-this-secret"
$env:LOAD_GPU_MODELS = "true"
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

```powershell
cd frontend
npm run dev
```

## 문서 구조

| 경로 | 역할 |
|---|---|
| `docs/PAPER` | 논문 본문, 전체 설계 기준, PPT 요약 |
| `docs/EXPLAIN` | 비전공자용 상세 설명 |
| `docs/USAGE` | 실행, 배포, 테스트, DB 사용법 |
| `docs/ARCHITECTURE.md` | 코드 기준 시스템 구조 |
| `docs/FEATURES.md` | 기능 목록과 코드 근거 |

## 주요 문서

- `docs/PAPER/GUIDE_ORIGINAL.md` 전체 설계 기준 문서
- `docs/PAPER/THESIS.md` 논문 본문 초안
- `docs/EXPLAIN/README.md` 설명 문서 읽는 순서
- `docs/EXPLAIN/TERMS_GLOSSARY_KO.md` 용어사전
- `docs/EXPLAIN/ROUTE_MODULE_MATRIX_KO.md` A~F 경로별 모듈 동작
- `docs/EXPLAIN/TABLE_INTERPRETATION_GUIDE.md` 실험표 해석
- `docs/USAGE/DEPLOY.md` 로컬/배포 실행
- `docs/USAGE/RUNPOD_A100_NO_SSH.md` RunPod 실행
- `docs/USAGE/ALICE_CLOUD_GUIDE.md` Alice Cloud 실행

## 결과 위치

- `backend/evaluation/results/*.json`
- `backend/evaluation/results/TABLES.md`
- `backend/scripts/master_run.log`

## 코드 맵

### Backend API

- `backend/api/main.py` FastAPI entrypoint
- `backend/api/auth.py` JWT auth and token revoke
- `backend/api/database.py` SQLAlchemy engine/session
- `backend/api/models.py` User, Conversation, Message, Paper, RevokedToken
- `backend/api/routers/papers.py` upload/list/delete papers
- `backend/api/routers/chat.py` query, stream, search, judge, PPT export
- `backend/api/routers/citations.py` citation APIs
- `backend/api/routers/history.py` conversation history

### Backend Modules

- `backend/modules/query_router.py` A~F route decision
- `backend/modules/hybrid_retriever.py` dense + BM25 + RRF
- `backend/modules/reranker.py` cross-encoder reranking
- `backend/modules/generator.py` MIDM generation
- `backend/modules/cad_decoder.py` CAD
- `backend/modules/scd_decoder.py` SCD
- `backend/modules/followup_generator.py` 후속 질문 생성
- `backend/modules/pptx_exporter.py` PPT export

### Pipelines

- `backend/pipelines/pipeline_a_simple_qa.py`
- `backend/pipelines/pipeline_b_section.py`
- `backend/pipelines/pipeline_c_compare.py`
- `backend/pipelines/pipeline_d_citation.py`
- `backend/pipelines/pipeline_e_summary.py`
- `backend/pipelines/pipeline_f_quiz.py` 퀴즈/플래시카드 생성 경로

### Experiment

- `backend/scripts/master_run.py`
- `backend/evaluation/run_track1.py`
- `backend/evaluation/run_track2.py`
- `backend/evaluation/ragas_eval.py`
- `backend/scripts/results_to_markdown.py`
