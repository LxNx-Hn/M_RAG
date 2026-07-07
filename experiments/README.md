# Experiments

This directory contains the separated research experiment framework for the
fixed Paper-RAG backbone plus HyDE x CAD x SCD factor analysis. The fixed
retrieval backbone uses BGE-M3 dense retrieval, BM25 sparse retrieval, weighted
RRF (dense 0.6 / BM25 0.4), CrossEncoder reranking, and context compression.

It is intentionally separate from the FastAPI service runtime and frontend UI.
Experiment runners here must support dry-run/static validation without calling
models, OpenAI, RAGAS, or GT generation.

Main experiment:

```text
HyDE off/on x CAD off/on x SCD off/on = 8 configs
```

HyDE is the retrieval-side evidence construction axis. CAD is the
context-faithfulness decoding-time control axis. SCD is the Korean-target
language-drift decoding-time control axis.

SCD mode provenance matters:

- `penalty_additive` is the default Phase 8 v1 application mode and preserves
  the already-scored main results.
- `reference_scd` is the literal arXiv:2511.09984 SCD formula
  (`target *= alpha`, `distractor *= beta`) with generated-token warm-up and no
  project technical whitelist. It is implemented only for separate guarded
  reruns.
- `prob_scale_logit_offset` is an engineering alternative
  (`target += log(alpha)`, `distractor += log(beta)`) and must not be described
  as the original reference SCD.

## Phase 6.5 Runner Readiness

Phase 6.5 originally added planning runners for future tuning and generation.
Current `run_generation.py` supports hard-gated `--execute` for approved
generation paths while retaining dry-run/static validation as the safe default.

Safe runner checks:

```powershell
python experiments/runners/generate_main_hyde_cad_scd_matrix.py --help
python experiments/runners/dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
python experiments/runners/run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3
python experiments/runners/run_tuning_plan.py --dry-run --plan-only --limit 3
```

Local post-score sensitivity checks:

```powershell
python experiments/analyzers/null_cell_sensitivity.py --scores experiments/results/evaluation/main-hyde-cad-scd__decoder_main_queries__main_generation.ragas_scores.json --generation experiments/results/main_generation/main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl
```

Future tuning should use only `tuning_queries`, then freeze `top_k`,
`rerank_top_n`, `cad_alpha`, `scd_beta`, the HyDE prompt/template, and
generation settings. The main matrix must vary only HyDE, CAD, and SCD.

Future main generation should use `decoder_main_queries` only after query/GT
cleanup confirms answerability and split integrity. Plan JSONL records map each
matrix config into runtime request fields: `use_hyde`, `use_cad`, `use_scd`,
`cad_alpha`, and `scd_beta`.

Do not run tuning, main generation, OpenAI, official RAGAS, or GT regeneration
without the relevant hard guard, approved split/config, and explicit phase
authorization.
