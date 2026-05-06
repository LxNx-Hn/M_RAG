# Legacy Backend Evaluation Archive

This archive was created during Phase 7.8C strict repository boundary cleanup.
The original `backend/evaluation/` package and legacy backend experiment scripts
were removed from the active backend boundary because the current backend runtime
does not import them.

## Boundary Status

- Original location: `backend/evaluation/`, selected `backend/scripts/`, and backend-root Alice helper scripts.
- New location: `experiments/archive/legacy_backend_evaluation/`.
- Current experiment runners: `experiments/runners/`.
- Current clean query splits: `experiments/data/query_splits/`.
- Current Alice scripts: `experiments/scripts/alice/`.
- OpenAI/RAGAS legacy evaluator code is archived and disabled by default.

## Archived Code

| original_path | new_path | reason | moved_in_phase |
|---|---|---|---|
| `backend/evaluation/__init__.py` | `experiments/archive/legacy_backend_evaluation/code/__init__.py` | legacy evaluation package marker | 7.8C |
| `backend/evaluation/ablation_study.py` | `experiments/archive/legacy_backend_evaluation/code/ablation_study.py` | legacy ablation evaluator | 7.8C |
| `backend/evaluation/decoder_ablation.py` | `experiments/archive/legacy_backend_evaluation/code/decoder_ablation.py` | legacy decoder evaluator | 7.8C |
| `backend/evaluation/openai_judge.py` | `experiments/archive/legacy_backend_evaluation/code/openai_judge.py` | legacy OpenAI judge code, not active by default | 7.8C |
| `backend/evaluation/ragas_eval.py` | `experiments/archive/legacy_backend_evaluation/code/ragas_eval.py` | legacy lightweight evaluator lineage, not official RAGAS execution | 7.8C |
| `backend/evaluation/run_track1.py` | `experiments/archive/legacy_backend_evaluation/code/run_track1.py` | legacy Track 1 runner | 7.8C |
| `backend/evaluation/run_track2.py` | `experiments/archive/legacy_backend_evaluation/code/run_track2.py` | legacy Track 2 runner | 7.8C |

## Archived Data And Results

| original_path | new_path | reason | moved_in_phase |
|---|---|---|---|
| `backend/evaluation/data/track1_queries.json` | `experiments/archive/legacy_backend_evaluation/data/track1_queries.json` | legacy source query snapshot preserved | 7.8C |
| `backend/evaluation/data/track2_queries.json` | `experiments/archive/legacy_backend_evaluation/data/track2_queries.json` | legacy Track 2 template source preserved | 7.8C |
| `backend/evaluation/data/pseudo_gt_track1.json` | `experiments/archive/legacy_backend_evaluation/data/pseudo_gt_track1.json` | legacy pseudo-GT snapshot preserved | 7.8C |
| `backend/evaluation/data/pseudo_gt_track2.json` | `experiments/archive/legacy_backend_evaluation/data/pseudo_gt_track2.json` | legacy pseudo-GT snapshot preserved | 7.8C |
| `backend/evaluation/data/local_outputs/pseudo_gt_sample_20.json` | `experiments/archive/legacy_backend_evaluation/data/local_outputs/pseudo_gt_sample_20.json` | legacy local output sample preserved | 7.8C |
| `backend/evaluation/results/table1_track1.json` | `experiments/archive/legacy_backend_evaluation/results/table1_track1.json` | legacy result table preserved as provenance only | 7.8C |
| `backend/evaluation/results/table2_decoder.json` | `experiments/archive/legacy_backend_evaluation/results/table2_decoder.json` | legacy result table preserved as provenance only | 7.8C |

## Archived Scripts

| original_path | new_path | reason | moved_in_phase |
|---|---|---|---|
| `backend/scripts/master_run.py` | `experiments/archive/legacy_backend_evaluation/scripts/master_run.py` | legacy experiment orchestration | 7.8C |
| `backend/scripts/verify_deployment.py` | `experiments/archive/legacy_backend_evaluation/scripts/verify_deployment.py` | legacy deployment/evaluation check imported legacy evaluation modules | 7.8C |
| `backend/scripts/pull_alice_results.sh` | `experiments/archive/legacy_backend_evaluation/scripts/pull_alice_results.sh` | legacy backend/evaluation result pull helper | 7.8C |
| `backend/scripts/results_to_markdown.py` | `experiments/archive/legacy_backend_evaluation/scripts/results_to_markdown.py` | legacy result table conversion | 7.8C |
| `backend/scripts/generate_pseudo_gt.py` | `experiments/archive/legacy_backend_evaluation/scripts/generate_pseudo_gt.py` | legacy GT generation helper, not active | 7.8C |
| `backend/scripts/generate_queries.py` | `experiments/archive/legacy_backend_evaluation/scripts/generate_queries.py` | legacy query generation helper, not active | 7.8C |
| `backend/scripts/generate_queries_local.py` | `experiments/archive/legacy_backend_evaluation/scripts/generate_queries_local.py` | legacy local query generation helper, not active | 7.8C |
| `backend/scripts/local_verify.py` | `experiments/archive/legacy_backend_evaluation/scripts/local_verify.py` | legacy local verification helper | 7.8C |
| `backend/scripts/experiments/rerun_cad_affected.sh` | `experiments/archive/legacy_backend_evaluation/scripts/experiments/rerun_cad_affected.sh` | legacy rerun helper | 7.8C |
| `backend/scripts/experiments/backup_alice_run.sh` | `experiments/archive/legacy_backend_evaluation/scripts/experiments/backup_alice_run.sh` | legacy Alice backup helper | 7.8C |
| `backend/run_alice_full.sh` | `experiments/archive/legacy_backend_evaluation/scripts/run_alice_full.sh` | obsolete backend-root Alice entrypoint | 7.8C |
| `backend/check_alice_status.sh` | `experiments/archive/legacy_backend_evaluation/scripts/check_alice_status.sh` | obsolete backend-root Alice status helper | 7.8C |
| `backend/watch_alice_log.sh` | `experiments/archive/legacy_backend_evaluation/scripts/watch_alice_log.sh` | obsolete backend-root Alice log helper | 7.8C |

## Usage Policy

These archived files are not the current experiment execution path and must not
be used to produce thesis result claims without a later explicit review phase.
They are kept for provenance, auditability, and possible future evaluator
reference only.
