# SCD symmetric evaluation

All deltas are paired `SCD-on - SCD-off` scores. Each panel contains 38 pairs: 19 CAD-off and 19 CAD-on.

| Stratum | Metric | EN mean delta [95% CI] | KO mean delta [95% CI] | Direction match | CI classes |
|---|---|---:|---:|:---:|---|
| overall | faithfulness | +0.0071 [-0.0596, +0.0714] | -0.0283 [-0.1044, +0.0510] | no | overlaps_zero / overlaps_zero |
| overall | answer_relevancy | -0.0910 [-0.1725, -0.0240] | -0.0752 [-0.1501, -0.0138] | yes | negative / negative |
| cad_off | faithfulness | -0.0290 [-0.0963, +0.0316] | -0.0288 [-0.1154, +0.0550] | yes | overlaps_zero / overlaps_zero |
| cad_off | answer_relevancy | -0.0454 [-0.1338, +0.0244] | -0.0425 [-0.1219, +0.0182] | yes | overlaps_zero / overlaps_zero |
| cad_on | faithfulness | +0.0432 [-0.0349, +0.1227] | -0.0278 [-0.1325, +0.0795] | no | overlaps_zero / overlaps_zero |
| cad_on | answer_relevancy | -0.1365 [-0.2434, -0.0417] | -0.1078 [-0.2013, -0.0276] | yes | negative / negative |

Counts for exact wins/losses/ties and the `±0.01` practical bands are preserved in the JSON artifact.

Bootstrap: 10000 deterministic paired resamples, seed 20260712, percentile 95% CI.

## Interpretation boundary

This is a post-generation language-normalization sensitivity analysis, not an unbiased causal estimate of SCD. It improves on the earlier asymmetric panel by applying the same normalization policy to all four HyDE-off conditions and by comparing only matched identical-context SCD pairs.

Overall faithfulness is +0.0071 (overlaps_zero) in English and -0.0283 (overlaps_zero) in Korean. Overall answer relevancy is -0.0910 (negative) in English and -0.0752 (negative) in Korean. The CAD-on answer-relevancy CI classes are negative / negative.

The same `gpt-4o` model performed non-identity normalization and RAGAS judging. In the Korean panel, validated identity was realized for 15/38 SCD-off answers and 27/38 SCD-on answers, so equal rules did not create equal transformation exposure. The panel contains 19 query clusters, and no human evaluation was run. Interpret this panel together with cross-judge robustness evidence; it is not a deployment or causal verdict.
