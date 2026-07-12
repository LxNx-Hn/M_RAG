# Official RAGAS Evaluation Design

The official RAGAS path is separate from the lightweight judge path.

## Required Inputs

- `question` or `user_input`
- `answer` or `response`
- `contexts` or `retrieved_contexts`
- `ground_truth` or `reference` when a selected metric requires it

## Implemented Metrics

- `faithfulness`
- `response_relevancy` or `answer_relevancy`
- `context_precision`
- `context_recall`

## Current Boundary

- Dry validation remains the default and performs no network calls.
- Real execution exists in `official_ragas_runner.py` behind `--execute`, the
  explicit confirmation environment variable, provider key, installed dependencies,
  and input validation.
- The original Phase 8 matrix used NVIDIA NIM. The completed `reference_scd`
  sensitivity track has documented `gpt-4o` and fixed `gpt-4.1` exceptions; scores from different
  judges must not be compared as absolute values.
- Official score artifacts record the generation-input path, SHA-256, byte and record
  counts, query split, and any symmetric-normalization protocol metadata.
- The completed English/Korean symmetric follow-up uses only the 38 identical-context
  HyDE-off SCD pairs and only `faithfulness` plus `answer_relevancy`. Context metrics
  are excluded because they do not consume the generated answer. Both `gpt-4o` and
  fixed `gpt-4.1-2025-04-14` judge panels are retained; the former's nonzero
  answer-relevancy intervals do not replicate under the latter. The result remains a
  post-generation sensitivity analysis, not an unbiased causal estimate.
- `official_ragas_runner_skeleton.py` is now a legacy-named, side-effect-free
  validation helper, not the whole evaluation implementation.
