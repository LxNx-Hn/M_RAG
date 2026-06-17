# Phase 8 — Repo Boundary Cleanup + Main-Generation Path Readiness

Scope: repository-boundary cleanup and main generation/evaluation path
preparation. **No Alice GPU job, no OpenAI, no RAGAS, no parameter freeze, no
main generation was run.** Only local dry/static checks were executed.

## 1. Repository boundary cleanup (legacy removed)

Removed 43 legacy/provenance-only files (recoverable via git history). None were
imported by any active runner, evaluator, config, query split, or Alice script
(verified by reference scan before removal).

| Removed | What it was |
|---|---|
| `experiments/archive/legacy_backend_evaluation/` (entire tree) | legacy eval code (`ragas_eval.py`, `openai_judge.py`, `run_track1/2.py`, `ablation_study.py`, `decoder_ablation.py`), legacy data (`pseudo_gt_track1/2.json`, `track1/2_queries.json`, `local_outputs/`), legacy results (`table1_track1.json`, `table2_decoder.json`), legacy scripts (`master_run.py`, `generate_pseudo_gt.py`, `generate_queries*.py`, …), `__pycache__` |
| `log-20260502/` (entire tree, repo root) | untracked-style legacy dump: `pseudo_gt_track1/2`, `table1/2/3*`, `track1/2_queries`, an 892 KB run log |
| `experiments/legacy_invalid/` | empty quarantine bucket (`.gitkeep` + "No files were moved" manifest) |
| `experiments/data/legacy_queries/` | pointer-only stub (README pointing at the now-removed archive) |
| `experiments/runners/build_query_audit.py` | derivation tool whose ONLY data source was the archive pseudo-GT/track queries (GT derivation is out of the active runtime path; splits are already checked in) |

`CLAUDE.md` was updated to drop dangling archive/pseudo-GT pointers (Evaluation
Dataset, Important Paths, Notes) so the canonical guide matches the cleaned tree.

Retained on purpose (active, or doc-referenced snapshot): all
`experiments/data/query_splits/`, `experiments/configs/`, active runners
(`run_generation.py`, `run_alice_tuning.py`, `run_alice_followup.py`,
`prepare_parameter_freeze.py`, `common.py`, `run_tuning_plan.py`,
`run_local_smoke.py`, `dry_run_matrix.py`, `estimate_cost.py`,
`generate_main_hyde_cad_scd_matrix.py`), `experiments/evaluators/` (official
runner + skeleton), all `experiments/results/*` JSONLs, all
`experiments/reports/`, and `experiments/data/query_audit.json` (a static
snapshot still referenced by `dry_run_matrix.py` and design docs).

## 2. Main-generation path audit (before Alice 80GB)

`run_generation.py` was hard-disabled (Phase 6.5 `raise SystemExit`). The broad
guard was **not** simply removed; it was replaced with a hard-guarded execution
mode plus a separate execution body `main_generation_executor.py`.

| Check | Result |
|---|---|
| `run_generation.py` still globally disabled? | No — replaced by a fail-closed `--execute` mode |
| Reuses fixed-backbone retrieval | Yes — `main_generation_executor.py` reuses the `run_alice_followup.py` path (`HybridRetriever.search_with_trace` BGE-M3+BM25+RRF → CrossEncoder rerank → `ContextCompressor`) |
| MIDM Base loaded once and reused | Yes — `Generator` built once in `build_components()` and reused across all (config, query) samples; `generator.py` lazy-loads model/tokenizer via cached properties (no per-sample reload) |
| HyDE/CAD/SCD map to the 2×2×2 matrix | Yes — `validate_main_matrix()` enforces exactly the 8 configs; HyDE via `QueryExpander`, CAD+SCD via `create_combined_processor(use_cad, cad_alpha, use_scd, scd_beta)` |
| OpenAI/RAGAS/GT disabled during generation | Yes — env guards (`OPENAI_ENABLED`/`RAGAS_ENABLED`/`GT_REGENERATION_ENABLED` must be 0) + every record flag false |
| Output satisfies `official_ragas_runner.py` | Yes — verified: synthetic record → `reference_coverage 1/1`, `records_missing_contexts 0`, `validation_passed true` |

Output record fields: `query_id`, `query`, `generated_answer`, `contexts` (+
`context.chunks` with `chunk_id`/`doc_id`/`content`/`snippet`), config/axis
metadata (`config_name`, `use_hyde`/`use_cad`/`use_scd`, `cad_alpha`,
`scd_beta`, `hyde_used`), retrieval trace (`retrieval_pool_top_k`,
`rerank_top_n`, `context_chunk_count`, dense/sparse/fused counts, retrieved/
reranked chunk ids), and `openai_used`/`ragas_used`/`gt_regenerated`/
`decoder_main_used`/`final_eval_used`/`parameter_freeze_evidence` flags.

### Execution guards (all verified fail-closed, no GPU)

`--execute` refuses unless **all** hold:
`CONFIRM_MAIN_8CONFIG_GENERATION=1`; `OPENAI_ENABLED=0`, `RAGAS_ENABLED=0`,
`GT_REGENERATION_ENABLED=0`; collection `local_gt__papers`; model MIDM Base;
query split `decoder_main_queries`; no `--limit/--config-limit`; matrix exactly
8 configs; output under `experiments/results/`; and a real **frozen**
`frozen_params.yaml` (file present, `final_values_selected: true`, no `pending`
values, numeric `rerank_top_n`/`cad_alpha`/`scd_beta`/`max_new_tokens`).

Verified refusals (exit 2): missing CONFIRM, missing frozen file, wrong
collection, wrong split, `RAGAS_ENABLED=1`. The planner path
(`--dry-run --plan-only`) is unchanged and needs no backend/torch.

## 3. Model-reload fix (2B regression)

The 2B CPU-offload was caused by a legacy per-sample model-reload pattern. The
active path does not use it: `Generator` caches `model`/`tokenizer` and is
constructed once per run in `build_components()`, then reused for every sample
(same pattern as the validated `run_alice_followup.py`). No `generate_answer`
per-sample reload exists in `backend/modules/generator.py`.

## 4. Status summary (required answers)

1. **Commit pushed**: see repo log (this report's commit).
2. **Removed/quarantined as legacy**: the 43 files in §1 (archive tree,
   `log-20260502/`, `legacy_invalid/`, `legacy_queries/`, `build_query_audit.py`).
3. **Active files retained**: query_splits, configs, active runners, official
   evaluator + skeleton, results JSONLs, reports, `query_audit.json`.
4. **`run_generation.py` ready for approved Alice 80GB execution?** Code-ready
   and fail-closed, but intentionally **blocked** until the freeze exists.
5. **Model reload fixed?** Yes — load-once/reuse confirmed; legacy reload absent.
6. **Evaluator input schema satisfied?** Yes — verified via dry-validation.
7. **OpenAI/RAGAS/GT disabled for generation?** Yes — env guards + per-record
   flags.
8. **Exact blocker before Alice 80GB main generation**: **no frozen
   `frozen_params.yaml`** (parameter freeze not performed). `--execute` refuses
   at the frozen-params gate. Secondary operational prerequisites: set
   `CONFIRM_MAIN_8CONFIG_GENERATION=1` and provision the Alice 80GB instance.

## 5. Next approved step

Run the scored evaluation → freeze sequence from
`experiments/reports/phase8_parameter_freeze_readiness.md` (official scoring of
tuning outputs → aggregation → freeze decision → write `frozen_params.yaml`).
Once `frozen_params.yaml` is frozen, `run_generation.py --execute` becomes
runnable on Alice 80GB with `CONFIRM_MAIN_8CONFIG_GENERATION=1`.
