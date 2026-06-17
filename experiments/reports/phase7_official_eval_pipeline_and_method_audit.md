# Official Run-Pipeline Alignment + Method-Contract Audit

Scope of this change: **code alignment + dry-validation only** (no execution).
No generation run, no RAGAS execution, no OpenAI call, no network/dependency
install. This satisfies the `experiments/METHOD_CONTRACTS.md` RAGAS contract
("official RAGAS skeleton with import guards and dry validation only") and the
`experiments/CLAIM_POLICY.md` framing rules.

## 1. Method-contract audit (CAD / SCD)

Audited `backend/modules/cad_decoder.py` and `backend/modules/scd_decoder.py`
against `experiments/METHOD_CONTRACTS.md`.

### CAD (Context-Aware Decoding) — COMPLIANT
- Exact scoring rule implemented: `(1 + alpha) * context_scores - alpha * no_context_scores`
  ([cad_decoder.py:94](../../backend/modules/cad_decoder.py)).
- Wired as a `LogitsProcessor` (not prompt-only).
- No-context branch is the uncached reference path: records context prompt
  length on first call, slices the generated prefix `y_<t` from `input_ids`,
  concatenates no-context prompt + prefix, single forward pass with
  `use_cache=False`. Matches the "CAD KV Cache Correctness Rule" exactly.
- Batch/beam blocked (`batch_size=1`, `num_beams=1` only) until a parity-tested
  cache path exists.
- Default thesis path uses fixed `alpha`; adaptive alpha exists only as an
  optional non-thesis runtime flag (`adaptive=False` by default).

### SCD (Soft Constrained Decoding, Korean-target) — COMPLIANT
- Named "Soft Constrained Decoding" (NOT the CLAIM_POLICY-forbidden
  "Selective ..." terms).
- Korean-target only; raises if `target_lang != "ko"` (full multilingual SCD is
  future work).
- Korean tokens, neutral tokens (whitespace/punctuation/numbers/math/citation/
  brackets/academic symbols), and the mandatory technical whitelist are not
  penalized; non-target tokens receive a soft `beta` penalty.
- Whitelist matches the contract list exactly (RAG, CAD, SCD, BM25, RRF, BGE-M3,
  HyDE, RAGAS, Transformer, CrossEncoder, Mi:dm, arXiv, DOI, BERT, RoBERTa,
  LLaMA, GPT, FLAN, XSUM, CNN-DM).

Conclusion: both decoders satisfy their method contracts; no code change needed.

## 2. Evaluation-query grounding (data validity)

Verified each eval query's `answer_span` is actually present in its target
paper (real PDF text, not field trust):
- `decoder_main_queries` (19): token-recall = 1.0 for all (every span token
  occurs in the cited paper).
- `candidate_final_eval_queries` (5, Korean `paper_ko_cad_contrastive`):
  whitespace-insensitive full-substring match 5/5 (the earlier low token score
  was a Korean-PDF no-word-space extraction artifact, not a content mismatch).

Conclusion: 24/24 eval queries are grounded in their papers; `answer_span` is a
valid extractive reference for RAGAS `ground_truth`/`reference`.

## 3. Official RAGAS runner (new, dry-validation default)

`experiments/evaluators/official_ragas_runner.py` wraps the validated dry-safe
primitives in `official_ragas_runner_skeleton.py` into an end-to-end pipeline:

```
generation results JSONL + query-split answer_span (reference)
  -> OfficialRAGASSample[]  (question / answer / contexts / ground_truth)
  -> check_ragas_dependency()        (find_spec only; no import)
  -> validate_official_ragas_samples (schema + reference checks)
  -> build_official_ragas_records    (official RAGAS schema, dual field names)
  -> writes <stem>.ragas_input.jsonl + <stem>.ragas_dry_validation.json
```

- Metrics (official plan): faithfulness, answer_relevancy, context_precision,
  context_recall.
- Judge: OpenAI (RAGAS standard) — configuration is plumbed and reported, but
  **not invoked** in dry mode.
- Separate from any lightweight/local judge (per contract).
- `--execute` is intentionally refused: it delegates to the skeleton's disabled
  placeholder, so official execution stays OFF until an explicitly approved
  phase (install ragas+datasets, set `OPENAI_API_KEY`, open the execution gate).

### Dry-validation result (local, cost 0)
Input: `phase7_6B2B_fixed_backbone_baseline_5samples.jsonl` + `tuning_queries`
reference. Output:
- records_read = 5, reference_coverage = 5/5, records_missing_contexts = 0
- validation_passed = true, dataset_record_count = 5
- openai_used = false, ragas_used = false, network_used = false
Artifacts under `experiments/results/evaluation/`.

## 4. Official end-to-end pipeline — status and gates

| Stage | Official requirement | Status |
|---|---|---|
| Fixed retrieval backbone | dense+BM25+RRF+CrossEncoder | DONE / validated |
| CAD / SCD method correctness | METHOD_CONTRACTS rules | COMPLIANT (audited) |
| Tuning sweep + parameter freeze | scored sweep -> `frozen_params.yaml` | TODO (draft only) |
| Main 8-config generation | decoder_main_queries, MIDM Base, 80GB GPU | GATED (run_generation Phase-6.5 guard) |
| Official RAGAS evaluation | OpenAI judge, this runner | SCAFFOLDED + dry-validated; execution gated |
| Claim writing | CLAIM_POLICY framing | pending results |

## 5. What is intentionally NOT done here
- No tuning-sweep execution, no parameter freeze.
- No main 8-config generation (run_generation Phase-6.5 guard left closed).
- No RAGAS/OpenAI execution, no dependency install, no network calls.
- "official RAGAS" / "RAGAS로 평가" are not asserted as core thesis claims; RAGAS
  is the measurement tool for the HyDE x CAD x SCD factor analysis only.

## 6. To enable official RAGAS execution later (explicit phase)
1. Approve the execution phase.
2. Install `ragas` + `datasets` in an approved setup step.
3. Set `OPENAI_API_KEY`.
4. Replace the skeleton's disabled `run_official_ragas_evaluation` placeholder
   with the real OpenAI-judge RAGAS call (metrics above) — evaluation runs on
   CPU/laptop (no GPU); only main generation needs the GPU.
