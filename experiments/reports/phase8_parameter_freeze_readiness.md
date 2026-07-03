# Phase 8 — Parameter-Freeze Readiness (planning only; NOT frozen)

Scope of this change: **freeze-planning + dry-safe readiness tooling only.**
No parameter freeze, no `frozen_params.yaml`, no OpenAI/RAGAS execution, no main
8-config generation, no `decoder_main`, no GT/query generation, no network or
dependency install. Tuning/smoke outputs are treated as **descriptive inputs
only**, never as final quality evidence.

This report satisfies the required outcome: **Phase 8 is structurally ready for
scored evaluation, but parameters are not frozen and cannot be frozen yet.**

> CLAIM_POLICY note: "official RAGAS" below is the *measurement tool* for the
> HyDE × CAD × SCD factor analysis, not a thesis core claim.

## 0. Current state (verified)

- HEAD `df68306` or newer (verified `df68306`, `git pull` up to date).
- Final `experiments/configs/frozen_params.yaml`: **does not exist** (only
  `experiments/configs/frozen_params.draft.yaml`, `status: draft_not_frozen`).
- Official RAGAS execution: **never run** (only dry-validation artifacts exist).
- Parameter freeze: **never performed**.
- New tooling: [prepare_parameter_freeze.py](../runners/prepare_parameter_freeze.py)
  (dry-safe readiness helper) + machine-readable
  [phase8_freeze_readiness.json](../results/tuning/phase8_freeze_readiness.json).

The helper's verdict on current artifacts:
`decision = READY_FOR_SCORED_EVAL`, `blockers = []`,
`scored_results_present = false`, `freeze_performed = false`.

## 1. What CAN be frozen (and is already fixed by design)

These are fixed-backbone components. They are **not** tuning knobs and are **not**
part of the scored freeze decision; they are confirmed fixed by experiment
design and recorded for completeness:

| Component | Value | Source |
|---|---|---|
| Dense retriever | BGE-M3 | `experiments/configs/fixed_backbone.yaml` |
| Sparse retriever | BM25 | `experiments/configs/fixed_backbone.yaml` |
| Fusion | RRF | `experiments/configs/fixed_backbone.yaml` |
| Reranker | CrossEncoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) | `backend/config.py RERANKER_MODEL` |
| Generation model | `K-intelligence/Midm-2.0-Base-Instruct` | `backend/config.py GENERATION_MODEL` (policy default) |
| Factorial axes | HyDE × CAD × SCD, 8 configs | `experiments/configs/main_hyde_cad_scd_matrix.yaml` |

The HyDE/CAD/SCD on/off states are **experiment axes**, not tunable knobs — they
must never be "selected away" during freeze.

## 2. What CANNOT be frozen yet (and why)

The non-axis parameters that a freeze must bind:

`top_k`, `rerank_top_n`, `cad_alpha`, `scd_beta`, `hyde_template_variant`,
`max_new_tokens`, `temperature`, `decoding_mode`
(candidate ranges: `experiments/configs/tuning_plan.yaml#candidate_space`).

They cannot be frozen now because **no scored quality signal exists**:

1. **No official scored evaluation has been run.** The only evaluation artifact
   is a *dry-validation* summary (`ragas_used=false`, `openai_used=false`); the
   readiness helper correctly **rejects** it as non-scored.
2. **The available tuning evidence is structurally too thin to select on**: it
   is retrieval-only (baseline axis `use_hyde/use_cad/use_scd = false`),
   single-paper (`paper_nlp_bge`), 5 queries × 3 retrieval-breadth profiles
   (15 records), and covers only `top_k`/`rerank_top_n`. It says nothing scored
   about `cad_alpha`, `scd_beta`, HyDE template, decoding policy, or length.
3. **A descriptive (non-quality) generation-stability signal is unresolved.**
   From [phase8_freeze_readiness.json](../results/tuning/phase8_freeze_readiness.json):

   | Profile | top_k/rerank/ctx | mean answer chars | mean Korean ratio | mean dur (s) | degeneration-suspected |
   |---|---|---|---|---|---|
   | retrieval_conservative | 3/3/3 | 889 | 0.545 | 17.7 | 0/5 |
   | current_defaults | 20/5/5 | 2457 | 0.356 | 39.8 | 2/5 |
   | retrieval_recall_oriented | 8/8/5 | 3806 | 0.128 | 56.8 | 4/5 |

   The "degeneration-suspected" flag = (duration at/near the `max_new_tokens`
   ceiling) **and** (answer mostly non-Korean). This is a **descriptive
   structural observation, not a quality score**: broader retrieval coincided
   with longer, English-echoing, runaway generations on this single paper. It
   **motivates** scored evaluation; it does **not** by itself decide that
   conservative retrieval is "better." Only official scored metrics can
   adjudicate the accuracy/faithfulness trade-off.

## 3. Required scoring inputs (before any freeze)

A freeze decision requires **official scored evaluation results** with:

- Metrics: `faithfulness`, `answer_relevancy`, `context_precision`,
  `context_recall` (per `experiments/configs/evaluation_metrics.yaml`).
- Judge: OpenAI-compatible endpoint — selected provider **NVIDIA NIM**
  (`integrate.api.nvidia.com/v1`, default `meta/llama-3.3-70b-instruct`,
  key `NVIDIA_API_KEY`; OpenAI retained as alternative) per
  [official_ragas_runner.py](../evaluators/official_ragas_runner.py) `JudgeConfig`.
  The judge model must stay fixed across all scored evaluations.
  `answer_relevancy` embeddings: local BGE-M3 (no API).
- Reference: each query's `answer_span` (verified grounded 24/24; for the tuning
  split, references are present for all 5 query_ids, `gt_status=valid`).
- Coverage: every candidate profile scored over the **same** query
  intersection, so deltas reflect parameters, not query mix.
- Per-record contexts present (already satisfied: `missing_context = []`).

The readiness helper recognizes a result as a real score only when it is an
*executed* result (`ragas_used` or `openai_used` true) carrying a numeric
metric aggregate — dry-validation summaries do not qualify.

## 4. Decision criteria (defined for the later scored phase)

For each non-axis parameter, on the scored tuning set (shared query
intersection), under the baseline axis unless the parameter is decoder-specific:

1. **Primary objective** = mean **faithfulness** (hallucination control is the
   thesis priority for paper QA), subject to a **context-recall floor**: the
   chosen `top_k`/`rerank_top_n` must not drop mean `context_recall` below the
   best profile's recall minus a small tolerance (default 0.05).
2. **Secondary objective** = mean **answer_relevancy**, then **context_precision**.
3. **Decoder params** (`cad_alpha`, `scd_beta`) are tuned **only under their own
   axis-on condition** and must beat their own axis-off control on the combined
   objective; a parameter that does not beat its control stays at the repo
   default and is reported as "no tuning gain."
4. **`max_new_tokens` / `decoding_mode` / `temperature`** are frozen to the
   setting that **minimizes the descriptive degeneration flag while not
   reducing faithfulness** — i.e. stability is a guard, not the optimizer.
5. **Scope guard**: only `tuning_queries` may inform freeze. `decoder_main_queries`
   and `candidate_final_eval_queries` remain held out (no `query_id`/text leakage).

## 5. Tie-break rules

Applied in order when scored differences are within tolerance (default 0.02 on
the primary objective):

1. Prefer the **current repository default** value (reproducibility, least
   surprise).
2. Prefer the **lower-cost / more conservative** setting (smaller `top_k`,
   `rerank_top_n`, `max_new_tokens`; deterministic decoding over sampling).
3. Prefer the setting with the **lower descriptive degeneration rate**.
4. If still tied, **do not freeze that parameter to a tuned value** — record it
   at the repo default with a "tie, defaulted" note.

## 6. Minimum validation checks before writing `frozen_params.yaml`

All must pass (the helper enforces the structural ones today; the scored ones
become checkable only after the scored phase):

- [ ] `decision == READY_TO_FREEZE` (requires scored results present).
- [ ] `all_succeeded`, `all_answers_present`, `all_contexts_present`,
      `all_references_present` (✅ already true for current tuning set).
- [ ] Profile/query coverage **balanced** over the shared intersection (✅ 3×5).
- [ ] Scored results cover **every** candidate value being decided.
- [ ] `openai_used=true` / `ragas_used=true` in the scored artifact, with the
      four metrics aggregated.
- [ ] No holdout-split leakage (tuning-only).
- [ ] Explicit human approval (`--confirm-freeze-approved`) — and even then the
      final file is authored in an explicitly approved freeze phase, not
      auto-generated.

## 7. Readiness statement (updated 2026-07-03)

**Phase 8 is NOT_READY → requires one small Alice re-run, then scored eval.**

The scoring-grade context check revealed that the 7.6C v1 tuning records carry
chunk **IDs** but not the context **texts**, and chunk IDs are NOT recoverable
off-instance: PDF chunk extraction is environment-sensitive (verified locally
— Windows/Linux + pymupdf-layout differences produce 47/60/82 chunks with
non-matching hashes; Alice's Chroma is gone with the instance). The readiness
helper was tightened accordingly (`_has_context` now requires inline texts) and
truthfully reports `NOT_READY`.

Fixes in place:
- `run_alice_followup.py` now inlines `contexts` + `context_chunks` into every
  record, so the 7.6C **re-run is scoreable** (15 records, minutes of GPU time
  on the next Alice session).
- `main_generation_executor.py` already inlines full contexts — main-run
  outputs are unaffected by this issue.
- Judge switched to **NVIDIA NIM** and the scored-execution path is implemented
  and double-gated (`CONFIRM_OFFICIAL_RAGAS_EXECUTION=1` + `NVIDIA_API_KEY`).

Until scored results exist, the helper refuses (`exit 3`) to write
`frozen_params.yaml`.

## 8. Exact next commands needed later (gated, require explicit approval)

Execution phase approved 2026-07-03; deps installed
(`experiments/requirements-eval.txt`). Remaining prerequisites: `NVIDIA_API_KEY`
+ one Alice session for step 0.

```bash
# 0. (Alice, next session) Re-run 7.6C with inline contexts -- 15 records.
#    The patched run_alice_followup.py now records context texts.
CONFIRM_ALICE_FOLLOWUP=1 python experiments/runners/run_alice_followup.py \
  --mode tuning-7c \
  --output-file experiments/results/tuning/phase8_tuning_comparison_15records_v2.jsonl

# 1. (Local CPU) Official scored evaluation. Judge = NVIDIA NIM
#    (OpenAI-compatible); embeddings = local BGE-M3.
export NVIDIA_API_KEY=...
CONFIRM_OFFICIAL_RAGAS_EXECUTION=1 \
python experiments/evaluators/official_ragas_runner.py \
  --generation-results experiments/results/tuning/phase8_tuning_comparison_15records_v2.jsonl \
  --query-split tuning_queries \
  --metrics faithfulness,answer_relevancy,context_precision,context_recall \
  --judge nvidia_nim \
  --execute
# -> writes <stem>.ragas_scores.json (aggregate + per-profile + per-sample)

# 2. Score aggregation is included in step 1's output
#    (<stem>.ragas_scores.json carries aggregate + per_group/per-profile).

# 3. Final freeze decision: re-run the readiness helper WITH the scored results.
#    With real scores present it can reach READY_TO_FREEZE.
python experiments/runners/prepare_parameter_freeze.py \
  --tuning-results experiments/results/tuning/phase8_tuning_comparison_15records_v2.jsonl \
  --eval-results   experiments/results/evaluation/phase8_tuning_comparison_15records_v2.ragas_scores.json \
  --query-split tuning_queries

# 4. Write frozen_params.yaml — explicit, human-approved freeze phase only.
#    The helper double-gates this; the final file records the selected values
#    from the scored aggregation per Sections 4-6 above.
```

## 9. Status summary (updated 2026-07-03)

| Item | State |
|---|---|
| Final `frozen_params.yaml` exists | **No** (only `.draft`) |
| Official RAGAS / judge API executed | **No** (path implemented; gated by `CONFIRM_OFFICIAL_RAGAS_EXECUTION` + `NVIDIA_API_KEY`) |
| Parameter freeze performed | **No** |
| Readiness decision | **NOT_READY** (7.6C v1 records lack inline context texts) |
| Exact blocker for actual freeze | 7.6C re-run with contexts (Alice, step 0) → scored eval (local, step 1) |
| Next approved step needed | Set `NVIDIA_API_KEY`; run step 0 on the next Alice session, then step 1 locally |
