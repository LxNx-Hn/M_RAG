# Legacy Artifact Audit

## Method and decision boundary

Audit date: 2026-09-15. Classification used references from `THESIS.md`, root
`README.md`, documentation, Python/shell/config paths, result provenance, tests,
and CI. A path is not deleted merely because its name is old. `KEEP_FINAL` is
required for current thesis tables/claims; `KEEP_SUPPORTING` preserves a final
provenance or correction trail; `LEGACY_CANDIDATE` is superseded and not referred
to by current thesis/final documentation. `UNRESOLVED` items remain in place.

The canonical final experiment is `main-hyde-cad-scd-reference-scd`, not the
older `main-hyde-cad-scd` / `penalty_additive` generation. The final result set
is defined by the files named below, rather than a directory-name heuristic.

## KEEP_FINAL

| Path | Type | Why it remains |
|---|---|---|
| `configs/fixed_backbone.yaml`, `configs/frozen_params.yaml`, `configs/main_hyde_cad_scd_matrix.yaml` | protocol/config | Fixed backbone, frozen settings, and eight-cell matrix. |
| `data/query_splits/decoder_main_queries.json` | input | The retained final 19-query split. |
| `data/source_papers/` | source paper | Input corpus, distinct from generated results. |
| `results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl` | generation | Canonical 152-answer source artifact. |
| `results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/` | evaluation | Complete 152-row score source for final HyDE/CAD contrasts. |
| `results/analysis/reference_scd_language_adherence.json` | analysis | Direct 76-pair language-adherence source. |
| `results/evaluation_inputs/reference_scd_symmetric/` | evaluation input | Frozen EN/KO normalized inputs and summary. |
| `results/evaluation/reference-scd-symmetric-hyde-off-*/merged.ragas_scores.json` | evaluation | Final EN/KO, gpt-4o/gpt-4.1 score panels. |
| `results/analysis/reference_scd_symmetric_gpt4o.json`, `results/analysis/reference_scd_symmetric_gpt41_2025_04_14.json` | analysis | Final paired two-judge analyses. |
| `reports/reference_scd_rerun_report*.md`, `reports/reference_scd_symmetric_*.md` | report | Final method, input audit, score, and cross-judge evidence. |
| `runners/`, `evaluators/`, `analyzers/` core paths and `scripts/download_test_papers.py` | official experiment | Official execution/evaluation and deterministic analysis interfaces. |

## KEEP_SUPPORTING

| Path | Type | Purpose / replacement relationship |
|---|---|---|
| `results/main_generation/main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl` | prior generation | Old `penalty_additive` v1 result; preserved to audit the corrected `reference_scd` interpretation, never merged with final scores. |
| `results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/pass*/` | score pass provenance | Retry/merge provenance for the final merged artifact, including the 41 filled transient null cells. |
| `results/evaluation/reference-scd-symmetric-hyde-off-*/pass*/` | score pass provenance | Input and retry evidence behind the four final merged panels. |
| `results/tuning/phase8_tuning_comparison_15records_v2.jsonl` and matching evaluation score | freeze provenance | Referenced by `frozen_params.yaml`; required to explain the frozen non-axis settings. |
| `reports/phase8_freeze_and_provenance_summary.md`, `phase8_parameter_freeze_readiness.md`, `phase8_scd_failure_analysis.md` | correction/freeze history | The final report distinguishes the old implementation rather than rewriting it. |
| `configs/tuning_plan.yaml`, `cad_scd_sensitivity.yaml`, `cost_estimator_defaults.yaml` | supporting protocol | Needed to audit pre-freeze candidate boundaries and dry planning. |
| `evaluators/translated_bleu_rouge_runner.py` | unexecuted evaluator | No final result exists; retained because deletion would need an explicit protocol decision. It is not cited as a final metric. |

## LEGACY_CANDIDATE removed in this cleanup

The following Phase 7 planning/status reports had no inbound reference from the
current thesis, README, final reports, code, tests, CI, or configuration. Their
facts are superseded by the retained final protocol/reports and Git history.

```text
reports/phase7_3D_deployment_boundary_cleanup_report.md
reports/phase7_3E_backend_data_boundary_cleanup_report.md
reports/phase7_3F_backend_file_level_audit_report.md
reports/phase7_4_alice_script_compatibility_report.md
reports/phase7_4_hardware_budget_report.md
reports/phase7_4L_alice_linux_validation_report.md
reports/phase7_4M_alice_model_cache_warmup_report.md
reports/phase7_5_alice_base_smoke_retry_report.md
reports/phase7_5_alice_base_smoke_retry_summary_report.md
reports/phase7_5A_mini_smoke_report.md
reports/phase7_5A_smoke_report.md
reports/phase7_5C_smoke_cleanup_patch_report.md
reports/phase7_5R_alice_retrieval_index_prep_report.md
reports/phase7_6_7_runpod_cleanup_alice_code_report.md
reports/phase7_6A_alice_tuning_adapter_report.md
reports/phase7_6B_40gb_fixed_backbone_runs_report.md
reports/phase7_6B_limited_tuning_current_defaults_report.md
reports/phase7_6B2A_pre_alice_audit_report.md
reports/phase7_8B_backend_boundary_audit_report.md
reports/phase7_8C_strict_repo_boundary_cleanup_report.md
reports/phase7_official_eval_pipeline_and_method_audit.md
reports/phase7_tuning_preparation_report.md
```

`experiments/tests/test_run_alice_tuning_retrieval.py` also contained two stale
thesis-static expectations (`## 17. References` and a superseded Korean author
spelling). They were updated to validate the current `THESIS.md` reference
heading and its normalized `[18] G. Jang et al.` entry; no manuscript text was
changed.

## UNRESOLVED: retained, not deleted

| Path group | Why no deletion occurred |
|---|---|
| `results/smoke/` and Phase 7 tuning JSONL files | Historical runner and Alice shell-script output paths still name these artifacts. Removing raw outputs without a separate decision about those runnable historical commands would leave a misleading or broken provenance path. |
| `configs/frozen_params.draft.yaml`, `tuning_execution_budget.local.yaml` | Clearly pre-final, but referenced by planning scripts and contain environment-specific history. A separate policy decision is required before removing or rewriting planning support. |
| `reports/reference_scd_session_handoff.md` | Superseded as a status handoff but contains explicit old-v1 preservation and evaluator provenance. It is not a final report; retain until its needed facts have a reviewed replacement. |
| `results/analysis/reference_scd_openai_side/` and corresponding evaluation directory | Explicitly non-canonical cross-check. It is retained as labelled audit evidence; it must not enter thesis tables. |
| `results/logs/` | No final claim cites these logs, but deletion was not necessary to establish the six role boundaries and the log provenance has not been independently reviewed line-by-line. |

## Role map after cleanup

| Role | Paths |
|---|---|
| THESIS | `FINALDOCS/`, including the Korean manuscript, HWP materials, evidence, and validation. |
| OFFICIAL_EXPERIMENT | `experiments/runners/`, `evaluators/`, `analyzers/`, `configs/`, `scripts/`. |
| EXPERIMENT_RESULT | `experiments/results/`, `experiments/reports/`. |
| SOURCE_PAPER | `experiments/data/source_papers/`. |
| OPERATION | `backend/`, `frontend/`, Docker/Compose, CI, deployment configuration. |
| CLI | `cli/`; it reads final artifacts only and does not import the operation layer. |
