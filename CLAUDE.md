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
cd backend && python scripts/download_test_papers.py --dry-run
cd backend && python scripts/download_test_papers.py

# Alice Cloud experiment planning
bash experiments/scripts/alice/alice_setup.sh
CONFIRM_ALICE_BASE_SMOKE=1 bash experiments/scripts/alice/alice_base_smoke.sh
bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage tuning
bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage freeze-check
bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage main-generation

# Local planning verification, no model execution
python experiments/runners/run_tuning_plan.py --dry-run --plan-only --limit 5
python experiments/runners/dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
python experiments/runners/run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3

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

- Default thesis/runtime generation model is `K-intelligence/Midm-2.0-Base-Instruct`
- `K-intelligence/Midm-2.0-Mini-Instruct` is the local smoke-test fallback via `GENERATION_MODEL`
- Default DB runtime is SQLite (`sqlite+aiosqlite:///./mrag.db`) for GPU cloud runs; PostgreSQL for production
- Use `experiments/runners/` and `experiments/scripts/alice/` as the standard experiment paths
- Do not delete code, documents, or generated artifacts without explicit user confirmation
- Treat diagrams, tables, flowcharts, and checklists in docs as active documentation assets
- Update those assets to match the current system instead of removing them during cleanup
- CAD adaptive alpha codepath is retained but thesis experiments run with fixed alpha (`cad_adaptive=False`)
- Ground truth generation is out of the active runtime path. Current clean query
  splits are checked in under `experiments/data/query_splits/`; do not
  regenerate GT without an explicit later phase.

## Evaluation Dataset

- Track 1 legacy source: `experiments/archive/legacy_backend_evaluation/data/track1_queries.json` -- archived paper-specific query source, 8 documents, 61 queries
  - Documents: paper_nlp_bge, paper_nlp_rag, paper_nlp_cad, paper_nlp_raptor,
               paper_midm, paper_ko_rag_eval_framework, paper_ko_hyde_multihop,
               paper_ko_cad_contrastive
  - Query types: simple_qa, section_method, section_result, section_abstract,
                 cad_hallucination, citation, crosslingual_ko, cad_ablation
  - crosslingual_ko: Korean-language queries targeting English-body papers only (5 papers; Korean-body papers excluded as redundant)
  - Current clean splits live under `experiments/data/query_splits/`.
- Track 2 legacy source: `experiments/archive/legacy_backend_evaluation/data/track2_queries.json` -- 56 archived common-query templates
  - English-body group papers: paper_nlp_bge, paper_nlp_rag, paper_nlp_cad, paper_nlp_raptor, paper_midm
  - Korean-body group papers: paper_ko_rag_eval_framework, paper_ko_hyde_multihop, paper_ko_cad_contrastive
  - Query types: cad_ablation (14), section_method (14), section_abstract (14), citation (14)
  - This file is a checked-in evaluation asset; must be populated in the repo
  - This is a structural reproducibility asset, not proof of measured quality by itself
- Pseudo-GT snapshots from the old backend layout are archived under `experiments/archive/legacy_backend_evaluation/data/`.
- Track 2 uses common query sets because it compares config deltas under matched query difficulty
- For factual claims about Track 2 answerability or CAD gaps, inspect generated
  archived pseudo-GT and result files. Do not turn archived values into thesis
  claims without an explicit evaluation phase.

## Paper Assets (8 papers)

All 8 papers are included in the repository under `backend/data/`. The arXiv
download script is still useful for refreshing the English PDFs, but a fresh
`git pull` on Alice is enough to populate the default corpus.

| doc_id | Language | Source |
|--------|----------|--------|
| paper_nlp_bge | English | arXiv 2402.03216 |
| paper_nlp_rag | English | arXiv 2312.10997 |
| paper_nlp_cad | English | arXiv 2305.14739 |
| paper_nlp_raptor | English | arXiv 2401.18059 |
| paper_midm | English body / Korean domain | Mi:dm K 2.5 Pro Technical Report |
| paper_ko_rag_eval_framework | Korean | Korean RAG Evaluation Framework |
| paper_ko_hyde_multihop | Korean | HyDE-Based Multi-Hop Retrieval Approach |
| paper_ko_cad_contrastive | Korean | Korean CAD Contrastive Decoding |

Alice setup: `git pull` -> all 8 papers immediately available in `backend/data/`.

## Experiment Configuration

| STEP | Output file | Papers | Configs |
|------|-------------|--------|---------|
| Tuning prep | experiments/configs/tuning_plan.yaml | tuning_queries | staged limited candidates |
| Freeze draft | experiments/configs/frozen_params.draft.yaml | n/a | draft_not_frozen |
| Main matrix | experiments/configs/main_hyde_cad_scd_matrix.yaml | decoder_main_queries | 8 HyDE/CAD/SCD configs |
| Alice plan | experiments/configs/alice_execution_plan.yaml | tuning/main/final splits | smoke, tuning, freeze, main-generation gates |

## Architecture Snapshot

- Frontend `frontend/src/` contains the React app, state stores, API clients, viewer, and chat UI
- FastAPI entrypoint lives in `backend/api/main.py`
- Request routers live under `backend/api/routers/`
- Retrieval and generation modules live under `backend/modules/`
- Query pipelines A through F live under `backend/pipelines/`
- Experiment runners live under `experiments/runners/`; Alice scripts live under `experiments/scripts/alice/`

## Important Paths

- Main doc `README.md`
- Alice Cloud guide `docs/USAGE/ALICE_CLOUD_GUIDE.md`
- Architecture doc `docs/ARCHITECTURE.md`
- Current experiment results `experiments/results/`
- Current experiment reports `experiments/reports/`
- Archived legacy backend evaluation assets `experiments/archive/legacy_backend_evaluation/`

## Notes For Future Sessions

- `download_models.py` follows the configured generation model by default.
- Base model is the default thesis path; Mini is only for local smoke checks.
- OpenAI/RAGAS/GT regeneration are disabled unless a later explicit phase approves them.
- Legacy `master_run.py`, Track 1/2 runners, pseudo-GT generators, and old result scripts are archived under `experiments/archive/legacy_backend_evaluation/`.
- Local Mini output is validation-only; Alice MIDM BASE is the thesis-grade model path.
- Experiment tokens are acquired via register-or-login (`/api/auth/register` then 409 fallback `/api/auth/login`), not bypass JWT.
- Legacy evaluation and deployment-check scripts are archived, not active backend runtime.
- `hybrid_retriever.py` uses a restricted unpickler for BM25 index loading (hardening).
- `limiter.py` only trusts proxy headers when `TRUST_PROXY_HEADERS=true` is set.
- Alice BASE smoke starts from `experiments/scripts/alice/alice_base_smoke.sh`.
- Do not clear current query splits, smoke evidence, or archived provenance files without explicit approval.
