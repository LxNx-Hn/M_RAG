# SCD symmetric evaluation

All deltas are paired `SCD-on - SCD-off` scores. Each panel contains 38 pairs: 19 CAD-off and 19 CAD-on.

| Stratum | Metric | EN mean delta [95% CI] | KO mean delta [95% CI] | Direction match | CI classes |
|---|---|---:|---:|:---:|---|
| overall | faithfulness | -0.0579 [-0.1322, +0.0060] | -0.0326 [-0.0997, +0.0226] | yes | overlaps_zero / overlaps_zero |
| overall | answer_relevancy | -0.0327 [-0.0851, +0.0129] | -0.0356 [-0.1149, +0.0315] | yes | overlaps_zero / overlaps_zero |
| cad_off | faithfulness | -0.0759 [-0.1995, +0.0042] | -0.0165 [-0.0841, +0.0408] | yes | overlaps_zero / overlaps_zero |
| cad_off | answer_relevancy | +0.0015 [-0.0976, +0.0927] | -0.0190 [-0.1035, +0.0465] | no | overlaps_zero / overlaps_zero |
| cad_on | faithfulness | -0.0399 [-0.1526, +0.0571] | -0.0486 [-0.1447, +0.0384] | yes | overlaps_zero / overlaps_zero |
| cad_on | answer_relevancy | -0.0668 [-0.1688, +0.0271] | -0.0521 [-0.1574, +0.0389] | yes | overlaps_zero / overlaps_zero |

Counts for exact wins/losses/ties and the `±0.01` practical bands are preserved in the JSON artifact.

Bootstrap: 10000 deterministic paired resamples, seed 20260712, percentile 95% CI.

## Interpretation boundary

This is a post-generation language-normalization sensitivity analysis, not an unbiased causal estimate of SCD. It improves on the earlier asymmetric panel by applying the same normalization policy to all four HyDE-off conditions and by comparing only matched identical-context SCD pairs.

Overall faithfulness is -0.0579 (overlaps_zero) in English and -0.0326 (overlaps_zero) in Korean. Overall answer relevancy is -0.0327 (overlaps_zero) in English and -0.0356 (overlaps_zero) in Korean. The CAD-on answer-relevancy CI classes are overlaps_zero / overlaps_zero.

Non-identity normalization used `gpt-4o`, while RAGAS judging used `gpt-4.1-2025-04-14`. This removes exact same-model judging but not same-provider or post-generation-normalization effects. In the Korean panel, validated identity was realized for 15/38 SCD-off answers and 27/38 SCD-on answers, so equal rules did not create equal transformation exposure. The panel contains 19 query clusters, and no human evaluation was run. Interpret this panel together with cross-judge robustness evidence; it is not a deployment or causal verdict.
