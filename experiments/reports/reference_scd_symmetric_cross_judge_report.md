# Reference-SCD symmetric cross-judge report

## Verdict

The bilingual matched-context sensitivity result is judge-sensitive. Across both
judges and both target languages, the mean answer-relevancy delta is negative, but
only the `gpt-4o` intervals exclude zero. The fixed `gpt-4.1-2025-04-14` cross-judge
intervals overlap zero in English and Korean, including the CAD-on stratum. A robust
nonzero answer-relevancy cost is therefore not established. Faithfulness remains
directionally unresolved in every panel.

This is not score fitting: all four score panels use the same two input files and
their pre-score hashes. No input was changed after any judge result was observed.

## Overall paired results

All values are `SCD-on - matched SCD-off`, with 19 query-clustered bootstrap units,
38 contrasts per language, 10,000 percentile resamples, and a 95% interval.

| Judge | Target | Faithfulness mean [95% CI] | Answer relevancy mean [95% CI] |
|---|---|---:|---:|
| `gpt-4o` | English | +0.0071 [-0.0596, +0.0714] | -0.0910 [-0.1725, -0.0240] |
| `gpt-4o` | Korean | -0.0283 [-0.1044, +0.0510] | -0.0752 [-0.1501, -0.0138] |
| `gpt-4.1-2025-04-14` | English | -0.0579 [-0.1322, +0.0060] | -0.0327 [-0.0851, +0.0129] |
| `gpt-4.1-2025-04-14` | Korean | -0.0326 [-0.0997, +0.0226] | -0.0356 [-0.1149, +0.0315] |

The `gpt-4o` CAD-on answer-relevancy intervals are negative in both languages. The
corresponding `gpt-4.1-2025-04-14` values are English -0.0668
[-0.1688, +0.0271] and Korean -0.0521 [-0.1574, +0.0389], both overlapping zero.

## Completeness and provenance

- Four panels: 76 rows and 152 metric cells each; 608/608 cells scored, 0 null.
- Metrics: `faithfulness`, `answer_relevancy` only.
- RAGAS: 0.2.15; answer-relevancy embeddings: local `BAAI/bge-m3`.
- English generation input SHA-256:
  `8fba280fc240b83f88fe5a125d1a48942216b493b3256695b2454459cb09f45c`
- Korean generation input SHA-256:
  `d1c37e243f48b5f42f1e9ecb59d7e8a71299f0ca8f714ee3984e0067767b0ee9`
- Normalization protocol: `reference_scd.symmetric_normalization.gpt4o.v9`.
- `gpt-4o` English/Korean score SHA-256:
  `30c26f0c12c3c168bff9515b9aa15af88a50636090e2b7e46fa9df5ffc5df2c1` /
  `ccedb54073eacb782be9633b9ca3c6fb37f366ae88f7b045fef1d2a95b27c46c`.
- Fixed `gpt-4.1` English/Korean score SHA-256:
  `1ed4d32c34351f754b6cd401ef7be878df09eb8ed9e3789ec07a5d902e13978c` /
  `1dbd30e7dbe39a432874f4a1e2fc1cccf79a9bd57ea170283dfb67b7ac472057`.
- `gpt-4o` analysis:
  `experiments/results/analysis/reference_scd_symmetric_gpt4o.json`.
- `gpt-4.1-2025-04-14` analysis:
  `experiments/results/analysis/reference_scd_symmetric_gpt41_2025_04_14.json`.

## Interpretation boundary

The `gpt-4.1-2025-04-14` cross-judge removes exact same-model normalization/judging,
but both models are from the same provider. Normalization is still performed after
generation, and Korean answer transformation exposure differs by condition: 23/38
SCD-off versus 11/38 SCD-on answers required translation. The sample contains only
19 query clusters and has no blinded human ratings. The supported conclusion is
therefore: strong direct Korean-language control, no resolved faithfulness direction,
and no judge-robust nonzero answer-relevancy effect.
