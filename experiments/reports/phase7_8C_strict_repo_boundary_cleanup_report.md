[Summary]
- phase: Phase 7.8C - Strict repo boundary cleanup before Alice Cloud smoke
- readiness before: ready_for_alice_base_smoke_with_explicit_user_approval, with pending RunPod/Alice and backend-boundary cleanup changes
- readiness after: ready_for_alice_base_smoke_after_boundary_cleanup_commit
- files deleted: generated backend/logs contents, ignored cache/pycache artifacts, active backend/evaluation directory after archival, empty root scripts directory after Alice script move, RunPod-only files from Phase 7.6/7.7
- files moved: backend/evaluation code/data/results to experiments/archive/legacy_backend_evaluation; legacy backend experiment scripts to the same archive; root scripts/alice to experiments/scripts/alice; backend Alice env example to experiments/scripts/alice after sanitization
- files modified: .gitignore, AGENTS.md, CLAUDE.md, docker-compose.yml, docs under docs/, experiments/runners/build_query_audit.py, experiments/runners/dry_run_matrix.py, experiments/runners/run_local_smoke.py, Alice scripts
- files created: experiments/archive/legacy_backend_evaluation/MANIFEST.md, experiments/scripts/alice/alice_runtime_env.example.sh, experiments/reports/phase7_8C_strict_repo_boundary_cleanup_report.md
- commit made: no

[Final Boundary]
- backend runtime only: yes; backend/evaluation and backend/logs are absent, and backend/scripts now contains only operational backend helper scripts
- frontend untouched: yes
- experiments contains experiment scripts: yes; Alice scripts live under experiments/scripts/alice
- docs contains usage docs: yes; active Alice docs point to experiments/scripts/alice
- root scripts remaining: no
- backend/evaluation remaining: no
- backend/logs remaining: no

[Cleanup Actions]
- backend logs deleted: yes; ignored generated backend/logs files removed
- backend evaluation archived/deleted: archived tracked code/data/results under experiments/archive/legacy_backend_evaluation, then removed active backend/evaluation
- legacy backend scripts archived/deleted: archived master_run.py, verify_deployment.py, query/GT generators, result conversion, legacy Alice helpers, and rerun/backup experiment shell scripts
- Alice scripts moved to experiments/scripts/alice: alice_setup.sh, alice_base_smoke.sh, alice_thesis_run_plan.sh
- Alice env example sanitized: yes; static credential-like values replaced with CHANGE_ME or explicit non-secret placeholders
- docs updated: yes; active docs now point to experiments/runners, experiments/scripts/alice, experiments/results, or explicit archive paths
- .gitignore updated: yes; added backend/logs/, *.out, and *.err
- archive manifest: experiments/archive/legacy_backend_evaluation/MANIFEST.md

[Archive]
- archive path: experiments/archive/legacy_backend_evaluation
- code archived: legacy evaluation Python files from backend/evaluation/code
- data archived: track1/track2 query snapshots, pseudo_gt_track1/2 snapshots, local_outputs/pseudo_gt_sample_20.json
- results archived: table1_track1.json and table2_decoder.json
- source/GT-like snapshots preserved: yes, moved only; not deleted
- deletion rationale: only generated logs/cache and empty directories were deleted; tracked legacy experiment/evaluation artifacts were preserved for provenance

[Remaining References]
- backend/evaluation references: only provenance/source_file fields in experiments/data/query_audit.json and query split JSON, archive manifest/scripts, and prior cleanup reports
- backend/logs references: prior audit report references and .gitignore policy only
- root scripts/alice references: none as active path; experiments/scripts/alice references are intentional
- RunPod references: report-only references in Phase 7.6/7.7 and Phase 7.8B reports
- classification: allowed provenance, allowed archive, allowed report, or active experiments/scripts/alice path
- blockers: none

[Validation]
- git status: expected dirty working tree with cleanup changes; .claude/worktrees remains untracked and untouched
- compileall: passed for python -m compileall backend experiments
- JSON validation: passed for tuning_queries, decoder_main_queries, candidate_final_eval_queries
- run_tuning_plan dry-run: passed, 40 planned tuning samples, no execute/model/OpenAI/RAGAS/GT calls
- dry_run_matrix: passed, 8 configs, leakage check passed, runtime core forbidden hits empty
- run_generation plan: passed, 6 planned samples for decoder_main subset, no execute/model/OpenAI/RAGAS/GT calls
- bash syntax: attempted, but local Windows Bash service failed with E_ACCESSDENIED before checking scripts; rerun bash -n on Alice/Linux before smoke
- issues: query split source_file fields still preserve original backend/evaluation provenance by design and were not modified in this phase

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
- clean query splits deleted or modified: no
- current smoke evidence deleted: no
- secrets written: no
- .claude/worktrees deleted: no

[Decision]
- ready_for_alice_base_smoke_after_boundary_cleanup_commit
- explanation: Active backend/evaluation, backend/logs, backend-root Alice helpers, and root scripts/alice were removed from the active repository boundary. Legacy experiment/evaluation provenance was preserved under experiments/archive with a manifest, active docs/scripts now point to experiments paths, and safe static/dry-run validation passed. The only remaining validation item is rerunning bash syntax checks on Alice/Linux because local Bash could not start.

[Next Step]
- whether Phase 7.6/7.7/7.8C should be committed together: yes, after user review
- exact files recommended for commit: .gitignore; AGENTS.md; CLAUDE.md; docker-compose.yml; backend/config.py; deletions of backend/evaluation/**, backend-root Alice helpers, backend legacy experiment scripts, RunPod scripts/docs; docs/USAGE/ALICE_CLOUD.md; docs/USAGE/ALICE_CLOUD_GUIDE.md; docs/USAGE/ALICE_SETUP.md; docs/USAGE/README.md; docs/USAGE/DEPLOY.md; docs/USAGE/TESTING_GUIDE.md; docs/ARCHITECTURE.md; docs/FEATURES.md; docs/EXPLAIN/*.md; docs/PAPER/DOC_SYNC_PLAN_35.md; docs/PAPER/LIMITATIONS_AND_FUTURE_WORK.md; docs/PAPER/NEXT_STAGE_VLLM_CLAIM.md; experiments/configs/alice_execution_plan.yaml; experiments/runners/build_query_audit.py; experiments/runners/dry_run_matrix.py; experiments/runners/run_local_smoke.py; experiments/scripts/alice/*; experiments/archive/legacy_backend_evaluation/**; experiments/gt/README.md; experiments/data/legacy_queries/README.md; experiments/reports/phase7_6_7_runpod_cleanup_alice_code_report.md; experiments/reports/phase7_8B_backend_boundary_audit_report.md; this report
- exact files intentionally not committed: .claude/worktrees/ and ignored cache/pycache/venv artifacts
- whether Alice BASE smoke can start after commit: yes, with explicit user approval and after rerunning bash -n on Alice/Linux
- manual cleanup still needed: optional future provenance-path refresh for query_audit/source_file fields only if explicitly approved; no blocker for Alice smoke
