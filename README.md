# M-RAG

**Graduation submission:** [FINALDOCS](FINALDOCS/README.md) is the self-contained
Korean manuscript, HWP-transfer, table, figure, UI replay, and validation package.

M-RAG is a Korean-query academic paper QA project. The thesis contribution is a
HyDE × CAD × SCD factor analysis for Korean questions over English papers, evaluated
on a fixed Paper-RAG backbone. The FastAPI + React application is a graduation-project
service integration layer; its A-F routed paper-review features are preserved but are
not the core thesis algorithm.

**Final thesis evidence** uses 60 Korean query-document pairs over four English
papers and eight HyDE/CAD/SCD configurations, yielding 480 stored generation
records. In the fixed comparisons, HyDE changes answer relevancy by `+0.0805`,
CAD changes matched-context faithfulness by `+0.0288` across 58 valid pairs,
and SCD increases the Korean-character ratio by `+0.2289`. These are
application-study results: HyDE concerns query-side retrieval representation,
CAD concerns decoding under identical context, and SCD concerns output-language
adherence. The manuscript and claim map state the metric-specific limits.

## Repository Layout

Four responsibility boundaries are intentionally kept separate — the ops runtime
does **not** import experiment code, and the evidence CLI reads stored artifacts
without importing either runtime (see `docs/REPO_LAYOUT.md`):

| Layer | Location | Role |
|---|---|---|
| Ops | `backend/`, `frontend/` | FastAPI + React paper-review service |
| Experiment | `experiments/` | fixed backbone, 8-config matrix, runners, RAGAS evaluator, analyzers, reports |
| Docs | `docs/` | architecture, paper, usage, explainers |
| Evidence CLI | `cli/` | offline, read-only replay of final thesis evidence |

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

These are service features. The current experiment supports only global
HyDE/CAD/SCD factor-effect defaults; query-type-specific route policy requires
a separate query-type analysis before it is claimed as validated.

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
| `FINALDOCS/` | self-contained 60-query Korean thesis and HWP submission package |
| `FINALDOCS/MANUSCRIPT/GRADUATION_REPORT_TRANSFER_KO_60Q.md` | final Korean manuscript for HWP transfer |
| `FINALDOCS/VALIDATION/verify_finaldocs_60q.py` | read-only package completeness and claim-boundary verifier |
| `FINALDOCS/VALIDATION/FINAL_CLAIM_MAP_60Q.md` | final claim-to-artifact map used by UI replay |
| `docs/ARCHITECTURE.md` | runtime and experiment-layer architecture |
| `experiments/configs/fixed_backbone.yaml` | fixed Paper-RAG backbone config |
| `experiments/configs/main_hyde_cad_scd_matrix.yaml` | 8-config main matrix |
| `experiments/configs/frozen_params.yaml` | frozen parameters (from scored tuning) |
| `experiments/results/` | scored generation + evaluation artifacts |
| `experiments/LEGACY_AUDIT.md` | final/supporting/legacy-candidate role and dependency audit |
| `experiments/reports/reference_scd_rerun_report.md` | `reference_scd` corrected-implementation results (English) |
| `experiments/reports/reference_scd_rerun_report_KO.md` | `reference_scd` corrected-implementation results (Korean) |
| `experiments/reports/reference_scd_rerun_explainer_KO.md` | plain-language Korean walkthrough of the `reference_scd` rerun |
| `experiments/reports/reference_scd_symmetric_input_audit.md` | pre-score audit of the fixed bilingual symmetric inputs |
| `experiments/reports/reference_scd_symmetric_eval_report.md` | matched-context bilingual sensitivity results and clustered confidence intervals |
| `experiments/reports/reference_scd_symmetric_cross_judge_report.md` | `gpt-4o` versus fixed `gpt-4.1` robustness verdict |
| `experiments/data/query_audit.json` | audited existing query assets |
| `experiments/data/query_splits/` | tuning/main/query-type/final/service splits |
| `backend/api/` | FastAPI service |
| `backend/modules/` | service modules and generation controls |
| `backend/pipelines/` | A-F service route pipelines |
| `frontend/src/` | React application |
| `cli/evidence_replay.py` | offline viewer for stored evidence cases and claim inventory |

## Notes

- Thesis claims and their 60-query source boundaries are fixed in `FINALDOCS/`.
  Historical experiment reports remain in `experiments/` for provenance, but are
  not an alternative thesis package.
- Ground truth is the verified extractive `answer_span` in each query split; it is not
  regenerated.
- Result claims come only from the scored artifacts under `experiments/results/`.
- For terminal evidence capture, run `python -X utf8 cli/evidence_replay.py list`;
  it is not an experiment runner and performs no model/API/database work.
