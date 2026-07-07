# M-RAG

M-RAG is a Korean-query academic paper QA project. The thesis contribution is a
HyDE × CAD × SCD factor analysis for Korean questions over English papers, evaluated
on a fixed Paper-RAG backbone. The FastAPI + React application is a graduation-project
service integration layer; its A-F routed paper-review features are preserved but are
not the core thesis algorithm.

**Headline results** (152 generations, Mi:dm 2.0 Base on A100 80GB, RAGAS scored under
a fixed NVIDIA NIM judge): CAD improves faithfulness (+0.044 paired); HyDE raises answer
relevancy and recall but lowers context precision; Korean-target SCD is a **null factor**
in its current form. See `docs/PAPER/THESIS.md` §12 and `experiments/reports/phase8_*`.

## Repository Layout

Three independent layers — the ops runtime does **not** import experiment code, so it
runs even if `experiments/` is removed (see `docs/REPO_LAYOUT.md`):

| Layer | Location | Role |
|---|---|---|
| Ops | `backend/`, `frontend/` | FastAPI + React paper-review service |
| Experiment | `experiments/` | fixed backbone, 8-config matrix, runners, RAGAS evaluator, analyzers, reports |
| Docs | `docs/` | architecture, paper, usage, explainers |

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
- Result values come only from the scored artifacts under `experiments/results/`.

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

## Reproducing the Experiment

The scored artifacts are checked in under `experiments/results/`. To reproduce:

1. Freeze: score tuning outputs with `experiments/evaluators/official_ragas_runner.py`
   (NVIDIA NIM judge; needs `NVIDIA_API_KEY`), then `experiments/runners/prepare_parameter_freeze.py`
   writes `experiments/configs/frozen_params.yaml`.
2. Generate (GPU): `experiments/runners/run_generation.py --execute` with
   `CONFIRM_MAIN_8CONFIG_GENERATION=1` (Mi:dm 2.0 Base, A100 80GB recommended).
3. Score + aggregate: `official_ragas_runner.py` then `experiments/analyzers/aggregate_main_scores.py`
   and `scd_language_adherence.py`.

Evaluation runs on CPU + the NIM judge API; only generation needs the GPU. NIM is used
**only as the judge** — generation is local Mi:dm Base, never a NIM API call.

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
| `experiments/configs/frozen_params.yaml` | frozen parameters (from scored tuning) |
| `experiments/results/` | scored generation + evaluation artifacts |
| `experiments/reports/phase8_official_evaluation_summary.md` | measured factor-effect results |
| `experiments/reports/phase8_scd_failure_analysis.md` | why SCD produced a null result |
| `experiments/data/query_audit.json` | audited existing query assets |
| `experiments/data/query_splits/` | tuning/main/query-type/final/service splits |
| `backend/api/` | FastAPI service |
| `backend/modules/` | service modules and generation controls |
| `backend/pipelines/` | A-F service route pipelines |
| `frontend/src/` | React application |

## Notes

- Generation model is local Mi:dm 2.0 Base on GPU; the NVIDIA NIM endpoint is used only
  as the RAGAS judge. OpenAI is not used.
- Ground truth is the verified extractive `answer_span` in each query split; it is not
  regenerated.
- Result claims come only from the scored artifacts under `experiments/results/`.
