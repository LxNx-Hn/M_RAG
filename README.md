# M-RAG

M-RAG is a Korean-query academic paper QA project. The current thesis direction is a HyDE × CAD × SCD factor analysis for Korean questions over English papers, evaluated on a fixed Paper-RAG backbone.

The FastAPI + React application remains a graduation-project service integration layer. Its A-F routed paper-review features are preserved, but they are not the core thesis algorithm.

## Thesis Direction

Main research contribution:

```text
HyDE × CAD × SCD factor analysis in Korean-query / English-paper RAG
```

Core rules:

- HyDE is the retrieval-side expansion axis.
- CAD is the context-faithfulness decoding axis.
- SCD is Korean-target Soft Constrained Decoding for language-drift control.
- The main matrix varies only HyDE on/off, CAD on/off, and SCD on/off.
- No result values should be claimed until verified experiment artifacts exist.

## Main Experiment

The separated experiment framework lives in `experiments/`.

Required 8-config matrix:

| Config |
|---|
| `hyde_off__no_decoder_control` |
| `hyde_off__cad_only` |
| `hyde_off__scd_only` |
| `hyde_off__cad_scd` |
| `hyde_on__no_decoder_control` |
| `hyde_on__cad_only` |
| `hyde_on__scd_only` |
| `hyde_on__cad_scd` |

Parameter freeze rule:

- Tune only on `tuning_queries`.
- Freeze `top_k`, `rerank_top_n`, `cad_alpha`, `scd_beta`, HyDE prompt/template, and generation settings before the main matrix.
- Do not tune on main, query-type analysis, or final-eval candidate queries.

## Service Features

The product runtime keeps the A-F paper-review routes:

- A: simple QA.
- B: section-focused QA.
- C: document comparison.
- D: citation / patent-oriented lookup.
- E: structured summary.
- F: quiz / flashcard generation.

These are service features. The route policy should be derived from the HyDE/CAD/SCD analysis by query type.

## Quick Setup

Backend:

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend\requirements.txt
```

Frontend:

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

## Safe Validation

Compile and dry-run checks:

```powershell
python -m compileall backend experiments
python experiments/runners/dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
python experiments/runners/dry_run_matrix.py --experiment all --estimate-cost --dry-run
```

Frontend validation, if dependencies are already installed:

```powershell
cd frontend
npm run typecheck
# or
npm run build
```

## Important Paths

| Path | Role |
|---|---|
| `docs/PAPER/THESIS.md` | thesis draft aligned to the HyDE/CAD/SCD direction |
| `docs/PAPER/GUIDE_ORIGINAL.md` | Phase 5 thesis and experiment guide |
| `docs/ARCHITECTURE.md` | runtime and experiment-layer architecture |
| `experiments/configs/fixed_backbone.yaml` | fixed Paper-RAG backbone config |
| `experiments/configs/main_hyde_cad_scd_matrix.yaml` | 8-config main matrix |
| `experiments/data/query_audit.json` | audited existing query assets |
| `experiments/data/query_splits/` | tuning/main/query-type/final/service splits |
| `backend/api/` | FastAPI service |
| `backend/modules/` | service modules and generation controls |
| `backend/pipelines/` | A-F service route pipelines |
| `frontend/src/` | React application |

## Safety

Do not run real experiments, model calls, OpenAI calls, RAGAS execution, or GT regeneration unless explicitly approved. Do not fabricate queries or result values.
