# M-RAG 실행 및 배포 가이드

## 기준

- 논문 실험 기본 모델은 `K-intelligence/Midm-2.0-Base-Instruct`
- 로컬 스모크 검증은 `K-intelligence/Midm-2.0-Mini-Instruct` 선택 가능
- 논문 실험 빠른 실행은 SQLite + SQLAlchemy 사용
- 운영/서비스 경로는 PostgreSQL + SQLAlchemy 사용
- 논문 실험 경로는 MIDM Base 직접 디코딩을 기준으로 함

## 로컬 환경 준비

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend\requirements.txt
cd frontend
npm ci
cd ..
```

## 모델 캐시

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
python scripts\download_models.py --llm-model K-intelligence/Midm-2.0-Base-Instruct
```

Mini 스모크 검증

```powershell
python scripts\download_models.py --llm-model K-intelligence/Midm-2.0-Mini-Instruct
```

## 개발 서버 실행

Backend

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
$env:JWT_SECRET_KEY = "change-this-secret"
$env:LOAD_GPU_MODELS = "true"
$env:GENERATION_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Frontend

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\frontend
npm run dev -- --host 0.0.0.0
```

## 논문 실험 실행

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
python experiments\runners\run_tuning_plan.py --dry-run --plan-only --limit 5
python experiments\runners\dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
python experiments\runners\run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3
```

Alice Cloud 실제 실행은 `docs/USAGE/ALICE_CLOUD.md`와
`experiments/scripts/alice/`를 따른다. 레거시 `master_run.py`는
`experiments/archive/legacy_backend_evaluation/scripts/master_run.py`에
보존되어 있지만 현재 활성 실행 경로가 아니다.

현재 실험 계획 기본값

- `DATABASE_URL=sqlite+aiosqlite:///./mrag.db`
- `GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct`
- `LOAD_GPU_MODELS=true`
- 토큰 획득: API health check 후 runner 계정 register-or-login

논문 자산 (8편, 전부 저장소 포함)

| 언어 | doc_id |
|------|--------|
| 영어 본문 | paper_nlp_bge, paper_nlp_rag, paper_nlp_cad, paper_nlp_raptor, paper_midm |
| 한국어 본문 | paper_ko_rag_eval_framework, paper_ko_hyde_multihop, paper_ko_cad_contrastive |

`git pull` 후 `experiments/data/source_papers/`에 8편 전부 존재한다. 별도
수동 배치 없이 실험 소스 자산을 확인할 수 있다. backend 런타임 업로드
디렉터리는 `MRAG_DATA_DIR` 또는 별도 마운트 볼륨으로 지정한다.

Track 2는 checked-in 공통 query asset을 사용한다.

- 영어 본문 그룹 28개
- 한국어 본문 그룹 28개
- 총 56개

현재 논문 실험은 `experiments/scripts/alice/`와 `experiments/runners/`를
기준으로 실행한다. 과거 `master_run.py` 성공 기준은
`experiments/archive/legacy_backend_evaluation/scripts/master_run.py`에
보존된 레거시 기준이며, 현재 활성 실행 경로가 아니다.

## Docker Compose

```powershell
docker compose up --build
```

운영 DB를 쓰려면 `.env`에 PostgreSQL 값을 설정한다.

## 결과 위치

- JSON 결과 `experiments/results/*.json`
- Markdown 표 `experiments/results/TABLES.md`
- 실행 로그 `experiments/reports/` 또는 실행별 지정 로그
- 실험 소스 PDF `experiments/data/source_papers/`
- 런타임 업로드 PDF `MRAG_DATA_DIR` 또는 마운트된 runtime data 볼륨
- ChromaDB `MRAG_CHROMA_DIR` 또는 마운트된 runtime vector-store 볼륨

## 배포 검증

```powershell
python -m compileall backend experiments
python experiments\runners\dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
```

레거시 `verify_deployment.py`는
`experiments/archive/legacy_backend_evaluation/scripts/verify_deployment.py`에
보존되어 있지만 현재 backend 런타임 경로는 아니다.

