[Summary]
- phase: Phase 7.8B-1 Backend boundary audit before cleanup
- readiness before: ready_for_alice_base_smoke_after_commit, with Phase 7.6/7.7 changes still uncommitted
- readiness after: ready_for_backend_cleanup_patch_with_secret_template_fix
- files changed: experiments/reports/phase7_8B_backend_boundary_audit_report.md only
- files deleted: none
- files moved: none
- commit made: no

[Repository Boundary]
- desired boundary: backend/ contains operational backend/runtime code only; experiments/ contains thesis experiment/evaluation code, reports, results, and archives; scripts/alice/ contains Alice execution scripts; docs/USAGE/ contains user-facing execution docs
- backend imports experiments: no active import found in backend/api, backend/modules, backend/pipelines, backend/config.py, or backend/scripts
- experiments import backend: yes, experiments/runners/run_local_smoke.py adds backend to sys.path to use runtime modules; dry_run_matrix and configs also reference backend paths for static planning/audit
- backend runtime imports backend/evaluation: no active import found in backend/api, backend/modules, backend/pipelines, or backend/config.py
- experiments import backend/evaluation: no active module import found; experiments assets and dry_run_matrix reference backend/evaluation paths as legacy/source provenance
- Alice scripts depend on backend/evaluation: new scripts/alice scripts do not; old backend-root Alice scripts and backend/scripts/pull_alice_results.sh still target backend/evaluation paths

[Backend Logs]
- files found: 11 ignored generated files under backend/logs
- tracked: none found by git ls-files
- untracked: backend/logs/manual_uvicorn.err; backend/logs/manual_uvicorn.out; backend/logs/mrag.log; backend/logs/run_all_experiments_20260425_211234.err; backend/logs/run_all_experiments_20260425_211234.out; backend/logs/run_all_experiments_20260425_211719.err; backend/logs/run_all_experiments_20260425_211719.out; backend/logs/run_all_experiments_20260425_212242.err; backend/logs/run_all_experiments_20260425_212242.out; backend/logs/server_local.log; backend/logs/server_local_err.log
- classification: safe_delete_generated_log
- recommended action: delete ignored local generated backend/logs contents in the cleanup patch; keep backend/api/main.py logging behavior but ensure backend/logs remains ignored

[Backend Evaluation]
- files found: tracked backend/evaluation Python entrypoints, tracked query/GT data, tracked legacy result tables, ignored __pycache__, and empty ignored archive directory
- tracked: backend/evaluation/__init__.py; ablation_study.py; decoder_ablation.py; openai_judge.py; ragas_eval.py; run_track1.py; run_track2.py; data/local_outputs/pseudo_gt_sample_20.json; data/pseudo_gt_track1.json; data/pseudo_gt_track2.json; data/track1_queries.json; data/track2_queries.json; results/table1_track1.json; results/table2_decoder.json
- import references: backend/scripts/verify_deployment.py imports evaluation.ragas_eval, evaluation.decoder_ablation, and evaluation.ablation_study; run_track1.py imports local evaluation modules through import_module; run_track2.py imports ragas_eval and openai_judge
- runtime dependencies: no direct backend runtime dependency found; backend/api, modules, pipelines, and config do not import backend/evaluation
- experiment dependencies: backend/scripts/master_run.py, backend/scripts/experiments/rerun_cad_affected.sh, backend/scripts/pull_alice_results.sh, backend/scripts/experiments/backup_alice_run.sh, docs, and experiments metadata reference legacy backend/evaluation paths
- classification by file:
  - openai_judge.py: safe_archive_legacy_eval_code, preserve for future explicit OpenAI evaluator work; OpenAI must remain disabled by default
  - ragas_eval.py: safe_archive_legacy_eval_code, preserve as legacy lightweight/local evaluator provenance; do not call official RAGAS
  - run_track1.py: safe_archive_legacy_eval_code after refactoring backend/scripts/master_run.py and rerun_cad_affected.sh references
  - run_track2.py: safe_archive_legacy_eval_code after refactoring backend/scripts/master_run.py and rerun_cad_affected.sh references
  - ablation_study.py: safe_archive_legacy_eval_code after refactoring verify_deployment.py and run_track1.py references
  - decoder_ablation.py: safe_archive_legacy_eval_code after refactoring verify_deployment.py and run_track1.py references
  - results/: safe_archive_legacy_result; move to experiments/archive/legacy_backend_evaluation/results with manifest, do not delete
  - archive/: safe_archive_legacy_result; currently ignored and empty in this checkout, but future non-empty archive content should move to experiments/archive/legacy_backend_evaluation/archive
  - data/: source_or_gt_data_do_not_touch for track1_queries.json, track2_queries.json, pseudo_gt_track1.json, and pseudo_gt_track2.json; data/local_outputs/pseudo_gt_sample_20.json is safe_archive_legacy_result, not source GT

[Alice Env Example]
- current path: backend/.alice_runtime_env.example.sh exists; backend/alice_runtime_env_example.sh does not exist
- contains secrets: contains credential-like static example values for JWT_SECRET_KEY and MRAG_RUNNER_PASSWORD plus a placeholder OpenAI API key string; no private key, real-looking sk token, HF token, or PEM block pattern was detected
- classification: alice_script_should_move_to_scripts_alice plus secret_template_needs_sanitization
- recommended action: move to scripts/alice/alice_runtime_env.example.sh in the cleanup patch and replace static password/JWT values with obvious placeholders such as CHANGE_ME, not usable credentials

[RunPod Status]
- remaining references: only experiments/reports/phase7_6_7_runpod_cleanup_alice_code_report.md from the prior Phase 7.6/7.7 report
- classification: report-only historical cleanup evidence
- active blocker: no active RunPod execution path found by grep

[Recommended Cleanup Patch]
- safe deletes: ignored backend/logs generated files; ignored backend/evaluation/__pycache__; no tracked source/query/GT/result deletion
- safe moves: backend/evaluation/*.py to experiments/archive/legacy_evaluation_code or experiments/evaluators/legacy after import/path refactor; backend/evaluation/results to experiments/archive/legacy_backend_evaluation/results with manifest; backend/evaluation/data/local_outputs to experiments/archive/legacy_backend_evaluation/data/local_outputs; backend/.alice_runtime_env.example.sh and backend-root Alice shell helpers to scripts/alice after sanitization/review
- files requiring refactor: backend/scripts/verify_deployment.py; backend/scripts/master_run.py; backend/scripts/experiments/rerun_cad_affected.sh; backend/scripts/pull_alice_results.sh; backend/scripts/experiments/backup_alice_run.sh; experiments/runners/build_query_audit.py if source files move; experiments/runners/dry_run_matrix.py if archive allow-rules move; docs that point to backend/evaluation as active
- files requiring user review: backend/.alice_runtime_env.example.sh because it has credential-like static values; backend/run_alice_full.sh because it runs master_run and requires OpenAI; backend/check_alice_status.sh and backend/watch_alice_log.sh because they hardcode /home/elicer paths; .claude/worktrees because git worktree list shows it is an active linked worktree, not disposable clutter
- .gitignore recommendations: backend/logs/ is already ignored through logs/ and *.log; add explicit backend/logs/, *.out, and *.err only if the cleanup patch wants clearer generated-log policy
- docs updates needed: docs/FEATURES.md, docs/EXPLAIN/*.md, docs/USAGE/TESTING_GUIDE.md, docs/USAGE/DEPLOY.md, and legacy plan docs should stop presenting backend/evaluation as the current active experiment path after code/data is moved

[Validation]
- compileall: passed with python -m compileall backend experiments
- JSON validation: passed for tuning_queries.json, decoder_main_queries.json, and candidate_final_eval_queries.json
- run_tuning_plan dry-run: passed; 8 configs x 5 tuning queries = 40 planned samples; no model/OpenAI/RAGAS/GT calls
- dry_run_matrix: passed; 8 configs x 19 decoder_main queries = 152 planned samples; leakage check passed
- run_generation plan: passed; config-limit 2 x limit 3 = 6 planned samples
- issues: first dependency rg command included a missing top-level tests path and returned a path error; rerun over existing backend/experiments/scripts/docs completed and showed backend/scripts/verify_deployment.py as the only direct import of evaluation modules outside backend/evaluation itself

[Safety]
- generation run: no
- tuning run: no
- main experiment run: no
- model calls made: no
- OpenAI calls made: no
- RAGAS calls made: no
- GT regenerated: no
- query fabricated: no
- result values invented: no
- source PDFs deleted: no
- metadata deleted: no
- source query files deleted: no
- pseudo-GT files deleted: no
- thesis-grade experiment results deleted: no
- imports modified: no
- backend/evaluation moved: no

[Decision]
- decision: ready_for_backend_cleanup_patch
- explanation: backend runtime is not directly coupled to backend/evaluation, so a cleanup patch is feasible. The patch must not be a blind move because backend maintenance/legacy experiment scripts still reference evaluation modules and paths, and the backend Alice env example needs sanitization before relocation.

[Next Step]
- exact cleanup patch recommended: delete ignored backend/logs and backend/evaluation/__pycache__; move/sanitize backend Alice helper scripts into scripts/alice; archive backend/evaluation code/results/local_outputs under experiments/archive with a manifest; preserve query/GT files or move only after updating experiments source references and with explicit approval; refactor legacy script/doc paths in the same cleanup patch
- whether user approval is needed before moving/deleting files: yes for moving source/GT query data, deleting any tracked result/provenance, and handling the active .claude linked worktree; no for ignored generated logs/cache if cleanup is explicitly approved
- whether Alice BASE smoke remains blocked by backend hygiene: not by runtime imports, but recommended to complete the cleanup patch first to avoid committing mixed backend experiment artifacts
- whether Phase 7.6/7.7 changes should wait before commit: yes; commit Phase 7.6/7.7 together with the later approved backend cleanup patch, or commit Phase 7.6/7.7 first only if the user decides backend cleanup should be separate
