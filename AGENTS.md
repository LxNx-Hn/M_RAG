# AGENTS.md

## Working Principles

- 모든 작업은 사용자의 최종 목적을 정확히 달성하는 방향으로 수행한다. 빠른 임시방편보다 근거가 있는 정확한 해결책을 우선한다.
- 모르는 내용은 가정하지 않는다. 구현, 테스트, 로그, 문서, 설정 파일 등 근거가 되는 파일을 찾아 확인하고 필요하면 보고에 인용한다.
- 요구사항이 모호하거나 정확한 구현이 어려우면 작업 전에 질문해서 계획을 구체화한다.
- 사용자가 요청하지 않은 예외 처리, 기본값, 실패 시 `0` 처리 같은 로직을 임의로 추가하지 않는다. 필요하다고 판단되면 먼저 사용자에게 확인한다.
- 작업 후에는 변경 내용을 재검토하고, 컴파일, 테스트, 실행, CI 관점에서 가능한 검증을 수행한다.
- 완료 보고에는 수행한 검토 내용, 실행한 검증 명령, 남아 있을 수 있는 문제점을 포함한다.
- 사용자 또는 다른 도구가 만든 기존 변경을 임의로 되돌리지 않는다.

## Project Overview

- M-RAG는 한국어 중심 학술 문서 질의응답을 위한 모듈러 RAG 시스템이다.
- Backend는 FastAPI 기반이며 `backend/api/main.py`가 진입점이다.
- Frontend는 Vite + React + TypeScript 기반이며 `frontend/src/`에 앱 코드가 있다.
- 주요 RAG 모듈은 `backend/modules/`, A-F 질의 파이프라인은 `backend/pipelines/`에 있다.
- 실험 오케스트레이션은 `backend/scripts/master_run.py`를 기준으로 한다.

## Important Runtime Rules

- 기본 논문/실험 생성 모델은 `K-intelligence/Midm-2.0-Base-Instruct`이다.
- `K-intelligence/Midm-2.0-Mini-Instruct`는 로컬 스모크 검증용 fallback으로만 사용한다.
- GPU 클라우드 및 논문 실험 기본 DB는 SQLite이고, 운영 서비스 경로는 PostgreSQL을 사용한다.
- CAD adaptive alpha code path는 유지하지만 논문 실험은 fixed alpha (`cad_adaptive=False`) 기준이다.
- 문서의 다이어그램, 표, 플로우차트, 체크리스트는 활성 문서 자산으로 보고, 정리 중 삭제하지 말고 현재 시스템에 맞춰 갱신한다.
- 코드, 문서, 생성 산출물을 삭제해야 하는 경우에는 명시적인 사용자 확인을 받는다.

## Setup

Backend dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend\requirements.txt
```

Frontend dependencies:

```powershell
cd frontend
npm ci
```

## Development Servers

Backend:

```powershell
cd backend
$env:JWT_SECRET_KEY = "change-this-secret"
$env:LOAD_GPU_MODELS = "true"
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend:

```powershell
cd frontend
npm run dev
```

## Verification Commands

Run the most relevant checks for the files changed. For broad backend changes, prefer:

```powershell
cd backend
python -m ruff check .
python -m black --check .
python -m pytest -q
python -X utf8 tests/test_api.py
```

For frontend changes, prefer:

```powershell
cd frontend
npm run lint
npm run build
```

For full local experiment verification:

```powershell
cd backend
$env:JWT_SECRET_KEY = "mrag-experiment-local-secret-2026"
$env:LOAD_GPU_MODELS = "true"
python scripts\master_run.py --skip-download
```

## Key Paths

- `README.md`: project summary and quick start.
- `CLAUDE.md`: existing detailed working guide and command reference.
- `docs/ARCHITECTURE.md`: code-level system architecture.
- `docs/FEATURES.md`: feature list with code evidence.
- `docs/PAPER/GUIDE_ORIGINAL.md`: thesis/system design reference.
- `docs/USAGE/DEPLOY.md`: local and deployment usage.
- `backend/api/`: FastAPI app, routers, auth, database, models.
- `backend/modules/`: retrieval, reranking, generation, CAD/SCD, follow-up generation, PPT export.
- `backend/pipelines/`: A-F query pipelines.
- `backend/evaluation/`: evaluation runners and datasets.
- `backend/evaluation/results/`: tracked result artifacts.
- `frontend/src/`: React app, stores, API clients, viewer, chat UI.

