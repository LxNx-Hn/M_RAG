# Phase 8 — Limitations

> **Historical Phase 8/v1 snapshot.** The SCD null result and deferred-rerun wording
> below apply to `penalty_additive` v1 at that time. The corrected `reference_scd`
> rerun and symmetric follow-up are complete; use the current thesis,
> `reference_scd_rerun_report.md`, and `reference_scd_symmetric_cross_judge_report.md` for
> present conclusions.

Honest constraints on the HyDE × CAD × SCD factor analysis. These bound how the
results should be read; they do not invalidate the within-experiment factor
comparison, which is the thesis claim.

## Judge

- The evaluation judge is **NVIDIA NIM `meta/llama-3.3-70b-instruct`** (an
  OpenAI-compatible endpoint), not OpenAI. Reported metrics are **NVIDIA-judge
  scores**.
- Absolute metric values are therefore **not directly comparable** to
  RAGAS numbers produced with a different judge in other work. The claim basis is
  the **within-experiment factor deltas** (CAD/HyDE/SCD on vs off), all measured
  under the same judge, same prompts, same references — where a fixed judge is a
  controlled constant.
- The judge was held fixed across every scored decision (tuning freeze and main
  evaluation); no judge or judge-model mixing.
- answer_relevancy embeddings ran locally with BGE-M3 (no external embedding API).

## Generation

- The generation model is **K-intelligence/Midm-2.0-Base-Instruct run locally on
  GPU**. NIM was used **only as the evaluation judge**, never for generation
  (Mi:dm is not in the NIM catalog, and CAD/SCD are logits-processor methods that
  cannot be expressed over a chat-completions API).
- Answer decoding was deterministic greedy. However, **HyDE hypothetical-document
  generation samples at temperature 0.1** (`do_sample=True`), so the four
  `hyde_on` configs carry a stochastic retrieval-reformulation component; a re-run
  could retrieve slightly different context for those cells even with greedy answer
  decoding.

## SCD target and null result

- The four RAGAS metrics do not measure SCD's actual target (Korean-language
  adherence). A **direct Korean-character-ratio measurement** of the 152 answers
  (`experiments/results/analysis/scd_language_adherence.json`) shows SCD is a
  **null result on its own target**: paired mean Δ = −0.014, and on the subset
  where the baseline actually drifted (< 0.5 Korean, 19 pairs) SCD rescued only
  2/19 to ≥ 0.5 while dragging 9/28 already-Korean answers below 0.65. The
  uniform soft-penalty SCD therefore does **not** provide a demonstrated
  language-adherence benefit here; it is reported as a null factor, not a
  positive one. Drift-conditional application is the indicated future work.
- Language drift itself is real and non-trivial on this corpus (43/152 answers
  below 0.5 Korean; some fully English), so the problem SCD targets exists — the
  limitation is the uniform-penalty mechanism, not the motivation.

## Compute

- Worst-case tuning/probe fit within a 40GB MIG slice (near-saturation on the
  heaviest HyDE+CAD+SCD path). Main generation used a full **A100 80GB**; observed
  peak was **34.8 GiB / 96% utilization**, no OOM. The 80GB recommendation gave
  ample headroom.

## Sample size and design

- **n = 19 queries per config** (152 records over 8 configs). Small per-cell n, but
  a **paired design**: all 8 configs answer the **same 19 queries**, so factor
  deltas are computed per query and are more stable than unpaired cell means. Axis
  effects report paired win/loss counts alongside mean deltas.

## Retrieval index difference (tuning vs main)

- The tuning comparison ran against an index of a single paper (99 chunks); the
  main experiment ran against the full checked-in corpus (8 papers, 698 chunks).
  Retrieval was **`doc_id`-filtered to the target paper in both**, so a query only
  ever retrieves from its own paper. The residual difference is limited to
  **BM25 corpus statistics** (IDF is computed over the whole collection), which can
  shift sparse-retrieval ranking slightly between the two indexes. The frozen
  retrieval-breadth choice is unaffected in kind.

## Scored coverage

- **583 / 608 metric cells scored (95.9%)**. 25 cells remain null (faithfulness 14,
  context_precision 11) after four retry passes with the same judge; these are the
  largest multi-context judging payloads, which repeatedly hit endpoint timeouts.
  answer_relevancy and context_recall are complete (152/152). Nulls are excluded
  from means, not zero-filled, and each reported mean carries its scored-n.
