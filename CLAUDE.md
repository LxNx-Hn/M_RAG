# CLAUDE.md

This file is the working guide for future Claude Code or Codex sessions in this repository

## Commands

```bash
# Backend dependencies
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend && npm ci

# Development servers
cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
cd frontend && npm run dev

# Model cache
cd backend && python scripts/download_models.py
cd backend && python scripts/download_models.py --llm-model K-intelligence/Midm-2.0-Base-Instruct

# Local verification
cd backend && python scripts/master_run.py --skip-download

# Backend checks
cd backend && python -m ruff check .
cd backend && python -m black --check .
cd backend && python -m pytest -q
cd backend && python -X utf8 tests/test_api.py

# Frontend checks
cd frontend && npm run lint
cd frontend && npm run build
```

## Current Operating Rules

- Default local generation model is `K-intelligence/Midm-2.0-Mini-Instruct`
- `K-intelligence/Midm-2.0-Base-Instruct` stays available through `GENERATION_MODEL`
- Do not reintroduce quantization or `bitsandbytes`
- Use `backend/scripts/master_run.py` as the standard local experiment path
- Do not delete code, documents, or generated artifacts without explicit user confirmation
- Treat diagrams, tables, flowcharts, and checklists in docs as active documentation assets
- Update those assets to match the current system instead of removing them during cleanup

## Architecture Snapshot

- Frontend `frontend/src/` contains the React app, state stores, API clients, viewer, and chat UI
- FastAPI entrypoint lives in `backend/api/main.py`
- Request routers live under `backend/api/routers/`
- Retrieval and generation modules live under `backend/modules/`
- Query pipelines A through F live under `backend/pipelines/`
- Experiment runners and dataset prep live under `backend/evaluation/` and `backend/scripts/`

## Important Paths

- Main doc `README.md`
- Working plan `WORK_PLAN.md`
- Handoff `HANDOFF.md`
- Architecture doc `docs/ARCHITECTURE.md`
- Deployment doc `docs/DEPLOY.md`
- Results `backend/evaluation/results/`
- Master log `backend/scripts/master_run.log`

## Notes For Future Sessions

- `master_run.py` now kills only stale `uvicorn api.main:app` listeners on the target port
- `download_models.py` follows the configured generation model by default
- Mini is the default local path because it fits 12GB-class GPUs
- Base is still supported for larger GPU environments
