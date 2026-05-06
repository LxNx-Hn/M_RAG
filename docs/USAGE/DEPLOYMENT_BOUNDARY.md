# Deployment Boundary

This repository keeps deployable runtime code separate from thesis experiment
infrastructure. The boundary is intentionally strict so backend and frontend
packages can be deployed without legacy experiment files, generated logs, local
tooling, or cloud-run orchestration artifacts.

## Top-Level Packages

- `backend/`: FastAPI backend runtime, runtime modules, runtime pipelines,
  database migrations, backend tests, backend dependency files, and operational
  backend helper scripts only.
- `frontend/`: Vite React frontend runtime, frontend build configuration,
  static assets, API client code, and frontend dependency manifests only.
- `experiments/`: thesis experiment configs, runners, evaluators, reports,
  results, archives, query split assets, and Alice Cloud experiment scripts.
- `docs/`: standalone documentation. Runtime services must not depend on docs
  at import time or execution time.

## Dependency Direction

- `backend/` must not import or call `experiments/`.
- `frontend/` must not import, call, or reference `experiments/`.
- `experiments/` may import backend runtime modules when running controlled
  experiment or smoke-validation scripts.
- `docs/` may describe all packages, but docs are not runtime dependencies.

## Backend Deploy Package

The backend deploy package may include:

- `backend/api/`
- `backend/modules/`
- `backend/pipelines/`
- `backend/alembic/`
- `backend/scripts/` only for operational backend helpers such as entrypoint,
  model download, indexing, cleanup, or backup utilities.
- `backend/config.py`, `backend/requirements.txt`, `backend/Dockerfile`,
  `backend/pytest.ini`, and migration/config files required by the backend.

The backend deploy package must not include:

- `backend/evaluation/`
- `backend/logs/`
- legacy cloud-provider scripts
- Alice experiment scripts
- thesis experiment orchestration scripts
- OpenAI/RAGAS judge scripts
- generated experiment result tables
- local smoke outputs
- local database files, vector-store directories, generated caches, or `.env`
  files as committed runtime source
- local Claude settings or local IDE/worktree files

Runtime uploads should be stored in `MRAG_DATA_DIR` or a mounted runtime volume.
Runtime vector stores should be stored in `MRAG_CHROMA_DIR` or a mounted runtime
volume. Checked-in thesis source PDFs belong in
`experiments/data/source_papers/`, not in `backend/data/`.

## Frontend Deploy Package

The frontend deploy package may include:

- `frontend/src/`
- `frontend/public/`
- frontend dependency manifests
- Vite, TypeScript, ESLint, Docker, and nginx configuration needed to build and
  serve the frontend

The frontend deploy package must not include:

- experiment runners, experiment outputs, or experiment configs
- backend source internals such as `backend/evaluation` or `backend/logs`
- cloud experiment orchestration paths
- generated build outputs unless produced by the deployment build process
- local secrets, tokens, or local-only settings

## Experiments Package

The experiments package owns:

- `experiments/configs/`
- `experiments/data/`
- `experiments/evaluators/`
- `experiments/runners/`
- `experiments/scripts/alice/`
- `experiments/results/`
- `experiments/reports/`
- `experiments/archive/`

Alice Cloud execution scripts belong under `experiments/scripts/alice/`.
Legacy backend evaluation artifacts, if preserved for provenance, belong under
`experiments/archive/`.

## Verification

Run these checks before committing boundary cleanup:

```powershell
Test-Path backend/evaluation
Test-Path backend/logs
Test-Path scripts
Test-Path experiments/scripts/alice
Test-Path .claude/settings.local.json

rg -n "from experiments|import experiments|experiments/" backend
rg -n "backend/evaluation|backend/logs|backend/scripts/experiments|scripts/alice" backend
rg -n "experiments|backend/evaluation|backend/logs|scripts/alice" frontend
rg -n "from backend|import backend|backend/" experiments

python -m compileall backend experiments
python experiments/runners/run_tuning_plan.py --dry-run --plan-only --limit 5
python experiments/runners/dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
python experiments/runners/run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3
```

Expected results:

- `backend/evaluation`, `backend/logs`, and root `scripts/` are absent.
- `experiments/scripts/alice/` is present.
- `.claude/settings.local.json` is absent from the repository.
- Backend and frontend have no active dependency on `experiments/`.
- Remaining `backend/evaluation` references, if any, are provenance-only fields
  in experiment data, archives, or reports.
