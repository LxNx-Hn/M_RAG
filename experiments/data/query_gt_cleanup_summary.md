# Phase 6.7 Query/GT Cleanup Summary

This cleanup rebuilds experiment query splits from existing query audit and split records only. It does not fabricate queries, duplicate queries to satisfy counts, regenerate GT, or modify source query and pseudo-GT files.

## Split Counts Before/After

| Split | Before | After |
| --- | ---: | ---: |
| tuning_queries | 8 | 5 |
| decoder_main_queries | 31 | 19 |
| query_type_analysis_queries | 14 | 24 |
| candidate_final_eval_queries | 8 | 5 |
| service_route_queries | 0 | 8 |
| query_templates | 56 | 56 |

## Clean Core Splits

- tuning_queries: track1_0001, track1_0004, track1_0005, track1_0007, track1_0008
- decoder_main_queries: track1_0009, track1_0010, track1_0012, track1_0015, track1_0016, track1_0019, track1_0021, track1_0023, track1_0024, track1_0025, track1_0026, track1_0027, track1_0032, track1_0033, track1_0034, track1_0035, track1_0036, track1_0037, track1_0040
- candidate_final_eval_queries: track1_0055, track1_0056, track1_0058, track1_0059, track1_0061
- track1_0058 is preserved because it appears in the safe final-eval candidate list, but it remains flagged for human rewrite risk before final claims.

## Moved / Reclassified

- service_route_queries now contains citation/service-route candidates: track1_0006, track1_0014, track1_0022, track1_0030, track1_0038, track1_0046, track1_0053, track1_0060
- query_type_analysis_queries now contains diagnostic, broad, needs-human-rewrite, and GT-validation-risk records that should not be used for tuning or final claims until validated.
- GT metadata inconsistency records moved out of tuning/main/final: track1_0002, track1_0003, track1_0011, track1_0013, track1_0014, track1_0017, track1_0018, track1_0022, track1_0029, track1_0030, track1_0031, track1_0038, track1_0039, track1_0057, track1_0060
- Needs human rewrite: track1_0020, track1_0028, track1_0051, track1_0057, track1_0058

## Track 2 Policy

All track2_0001 through track2_0056 records remain in query_templates.json only. They require future paper binding and answer-span validation before any promotion into tuning, decoder_main, query_type_analysis, candidate_final_eval, or service_route splits.

## Validation Snapshot

- JSON validation passed for all six split files using `python -m json.tool`.
- Leakage checks found no tuning/final, tuning/decoder_main, or decoder_main/final overlap by query_id or exact query text.
- `gt_status: not_found` counts in tuning, decoder_main, and candidate_final_eval are now 0, 0, and 0.
- `python experiments/runners/dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run` passed with 8 matrix configs and 19 decoder-main queries.
- `python experiments/runners/run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3` passed without model calls.
- `python experiments/runners/run_tuning_plan.py --dry-run --plan-only --limit 3` passed without model calls.
