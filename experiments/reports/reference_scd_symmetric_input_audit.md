# Reference-SCD symmetric input audit

Audit date: 2026-07-12 (Asia/Seoul)

## Verdict

The two HyDE-off symmetric-normalization panels are valid for the restricted
`faithfulness` + `answer_relevancy` sensitivity analysis. No input validation
error remained after the final full sweep.

This is a post-generation normalization sensitivity design, not an unbiased
causal estimate of the original decoder intervention. Context metrics remain
out of scope because they do not consume the generated answer.

## Provenance

- Source: `experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl`
- Source contract: canonical `main-hyde-cad-scd-reference-scd`, Midm 2.0 Base,
  deterministic decoding, succeeded/no-error/no-fallback records only
- Protocol: `reference_scd.symmetric_normalization.gpt4o.v9`
- Policy: validated identity when a source already satisfies the target-language
  and integrity contract; otherwise lossless `gpt-4o` translation
- Unique normalization tasks: 312
  - validated identity: 125
  - `gpt-4o` translation: 187
- Integrity checks: exact number, citation, circled-number, and locked date-literal
  multisets; exact output markers; no unapproved fallback

## Panel checks

| Check | English panel | Korean panel |
|---|---:|---:|
| Records | 76 | 76 |
| Unique contexts | 61 | 61 |
| Matched SCD context pairs | 38/38 | 38/38 |
| Nested chunks checked | 380/380 | 380/380 |
| Hangul characters | 0 | 317,629 |
| Question target-script ratio, min / median | 0 / 0 | 0.461538 / 0.757576 |
| Answer target-script ratio, min / median | 0 / 0 | 0.545220 / 0.826132 |
| Context target-script ratio, min / median | 0 / 0 | 0.377278 / 0.843411 |
| Residual English answer-prose spans | n/a | 0 |

The lowest-ratio Korean question was a natural Korean question containing the
model name `Mi:dm K 2.5 Pro` and the parenthetical term `context window`. The
lowest-ratio answer and context were also manually read; their remaining Latin
text consisted of model, benchmark, and metric identifiers rather than an
untranslated prose passage.

## Output artifacts

- English input SHA-256:
  `8fba280fc240b83f88fe5a125d1a48942216b493b3256695b2454459cb09f45c`
- Korean input SHA-256:
  `d1c37e243f48b5f42f1e9ecb59d7e8a71299f0ca8f714ee3984e0067767b0ee9`
- Execution summary:
  `experiments/results/evaluation_inputs/reference_scd_symmetric/reference_scd_symmetric_normalization_summary.json`

Every output record carries the protocol id, target language, field-level
normalization methods, and the nested-context projection policy. The official
RAGAS runner records the input path and SHA-256 in each score artifact, and the
symmetric analyzer rejects a wrong target, protocol, hash shape, metric set,
judge, RAGAS version, embedding configuration, missing row, duplicate row, or
null score.

## Remaining interpretation limits

- The normalization model and first judge are both `gpt-4o`. A later fixed
  `gpt-4.1-2025-04-14` cross-judge removes exact same-model judging, but both remain
  from the same provider.
- Identity versus translation frequency differs by source language. The same
  rule is applied to every condition and both target-language panels are run,
  but normalization remains a post-hoc outcome transformation.
- The realized Korean answer treatment also differs by SCD condition because SCD
  already changes the source answer language: validated identity is used for 15/38
  SCD-off answers and 27/38 SCD-on answers (translation 23/38 versus 11/38).
  The selection rule was fixed before scoring, but equal rules do not imply equal
  transformation exposure.
- Only the 19-query HyDE-off subset supports identical retrieved contexts.
  Results must not be generalized to HyDE interactions or the full corpus.
- This panel does not replace human evaluation.
