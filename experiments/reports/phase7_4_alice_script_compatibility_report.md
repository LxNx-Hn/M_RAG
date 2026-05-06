[Summary]
- phase: Phase 7.4 Alice script compatibility validation
- readiness before: ready_for_phase7_4_alice_script_validation
- readiness after: ready_for_phase7_3_4_boundary_commit
- files inspected: experiments/scripts/alice/alice_setup.sh; experiments/scripts/alice/alice_base_smoke.sh; experiments/scripts/alice/alice_thesis_run_plan.sh; experiments/scripts/alice/alice_runtime_env.example.sh; experiments/runners/run_local_smoke.py; experiments/runners/run_tuning_plan.py; experiments/runners/run_generation.py; experiments/runners/dry_run_matrix.py; experiments/runners/generate_main_hyde_cad_scd_matrix.py; experiments/runners/estimate_cost.py
- files modified: experiments/scripts/alice/alice_base_smoke.sh; experiments/scripts/alice/alice_thesis_run_plan.sh
- files created: experiments/reports/phase7_4_alice_script_compatibility_report.md
- commit made: no

[Alice Script Compatibility]
- alice_setup.sh: compatible. It performs environment/setup checks, uses repository-local dependency files, checks CUDA/PyTorch/nvidia-smi safely, does not run models, does not call OpenAI/RAGAS, does not write to backend/logs, and does not reference backend/evaluation or root scripts/.
- alice_base_smoke.sh: compatible after patch. It calls experiments/runners/run_local_smoke.py with supported flags, requires CONFIRM_ALICE_BASE_SMOKE=1, enforces one-sample scope, uses tuning_queries only, uses K-intelligence/Midm-2.0-Base-Instruct, writes under experiments/results/smoke and experiments/reports, and keeps OpenAI/RAGAS/GT regeneration disabled.
- alice_thesis_run_plan.sh: compatible after patch. It defaults to plan-only/dry-run behavior, makes tuning use tuning_queries explicitly, keeps main generation behind a frozen-params checkpoint, keeps optional final generation behind explicit approval, and does not enable real tuning/main execution.
- alice_runtime_env.example.sh: compatible. It contains placeholders only, documents secrets as environment/local-only values, and keeps OpenAI/RAGAS disabled by default.
- compatible with current CLI: yes
- patches applied: alice_base_smoke.sh now fails closed on unexpected BASE model names and preserves/report-parses the smoke JSONL even if the smoke runner exits nonzero; alice_thesis_run_plan.sh now passes explicit --query-split tuning_queries and --no-openai in planning commands and prints a stronger Phase 8 freeze warning when CONFIRM_FROZEN_PARAMS is used without a frozen params file.

[Runner CLI Match]
- run_local_smoke.py flags: supports --execute-smoke, --query-split, --query-limit, --profile, --axis-config, --max-samples, --max-new-tokens, --temperature, --output-file, --report-file, --generation-model, --model-variant, --model-role, --phase-label, --require-mini, --alice-mode, --confirm-alice-base, and --allow-download.
- run_tuning_plan.py flags: supports --query-split, --dry-run, --plan-only, --execute, --limit, --config-limit, --output-dir, --model-tier, --generation-model, --max-new-tokens, --resume, --skip-existing, --no-openai, and --allow-empty.
- run_generation.py flags: supports --query-split, --dry-run, --plan-only, --execute, --limit, --config-limit, --output-dir, --model-tier, --generation-model, --max-new-tokens, --resume, --skip-existing, --no-openai, and --allow-empty.
- dry_run_matrix.py flags: supports --experiment, --estimate-cost, and --dry-run; help runs without side effects.
- unsupported flags found: none in the current Alice scripts after patch.
- removed or fixed flags: no unsupported flags required removal; explicit --no-openai and --query-split tuning_queries were added where they make the script intent safer.

[Execution Guards]
- Alice BASE smoke confirmation: required through CONFIRM_ALICE_BASE_SMOKE=1 in alice_base_smoke.sh plus --alice-mode and --confirm-alice-base in run_local_smoke.py.
- smoke sample cap: enforced in alice_base_smoke.sh by QUERY_LIMIT=1 and MAX_SAMPLES=1 checks, and in run_local_smoke.py by its single-record smoke path.
- tuning execution guard: alice_thesis_run_plan.sh remains plan-only by default; EXECUTE=1 requires CONFIRM_ALICE_TUNING=1 and still exits without real tuning in the current phase.
- main generation freeze guard: main-generation requires experiments/configs/frozen_params.yaml or CONFIRM_FROZEN_PARAMS=1, and real execution remains disabled.
- optional final eval guard: optional-final requires CONFIRM_OPTIONAL_FINAL=1 and real execution remains disabled.
- OpenAI default: disabled by script defaults and --no-openai planning flags.
- RAGAS default: disabled by script defaults; no Alice script invokes RAGAS.
- GT regeneration: disabled; no Alice script invokes GT generation.

[Path Boundary]
- references to backend/evaluation: no active backend/frontend/Alice-script references. Remaining mentions are documentation/provenance boundary text only.
- references to backend/logs: no active backend/frontend/Alice-script references. Remaining mentions are documentation/provenance boundary text only.
- references to root scripts: none as an active path. Alice scripts live under experiments/scripts/alice.
- references to experiments/scripts/alice: present only as the intended canonical Alice script path in scripts/docs.
- output paths: Alice smoke writes to experiments/results/smoke and experiments/reports; no script writes to backend/evaluation or backend/logs.

[Validation]
- compileall: passed with python -m compileall backend experiments.
- JSON validation: passed for tuning_queries.json, decoder_main_queries.json, and candidate_final_eval_queries.json.
- runner dry-runs: passed for run_tuning_plan.py --dry-run --plan-only --limit 5; dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run; run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3; additional exact Alice-plan-compatible dry runs with --query-split tuning_queries and --no-openai also passed.
- runner help checks: passed for run_local_smoke.py, run_tuning_plan.py, run_generation.py, dry_run_matrix.py, generate_main_hyde_cad_scd_matrix.py, and estimate_cost.py.
- bash syntax: not validated on this Windows host because bash/WSL reported /bin/bash unavailable. Per phase instructions this is not treated as a script failure; rerun bash -n on Alice/Linux before Phase 7.5 smoke.
- secret grep: no real secrets found. Matches were placeholder/example strings or unrelated false positives.
- issues: bash syntax must be rerun on Alice/Linux; compileall still traverses ignored local virtualenv/cache directories if present, but active backend/experiments code compiled successfully.

[Safety]
- generation run: no
- tuning run: no
- main experiment run: no
- --execute used: no
- --execute-smoke used: no
- model calls made: no
- OpenAI calls made: no
- RAGAS calls made: no
- GT regenerated: no
- query fabricated: no
- result values invented: no
- clean query splits modified: no
- source PDFs deleted: no
- metadata deleted: no
- current smoke evidence deleted: no
- .claude/worktrees touched: no
- secrets written: no
- commit made: no

[Decision]
- ready_for_phase7_3_4_boundary_commit
- Explanation: Alice scripts now match the current runner CLI, the repository boundary checks still show no backend/evaluation, backend/logs, or root scripts directory, dry-run/static validation passed, and no execution/model/API path was invoked. The only remaining pre-smoke environment check is to rerun bash -n on Alice/Linux because local bash is unavailable.

[Next Step]
- whether Phase 7.3D and Phase 7.4 should be committed together: yes, after reviewing the combined boundary cleanup and Alice compatibility diff.
- exact files recommended for commit: .gitignore; AGENTS.md; CLAUDE.md; backend/config.py; docker-compose.yml; docs/ARCHITECTURE.md; docs/FEATURES.md; docs/USAGE/ALICE_CLOUD.md; docs/USAGE/DEPLOYMENT_BOUNDARY.md; docs/USAGE/DEPLOY.md; docs/USAGE/README.md; docs/USAGE/DOCKER_RUNBOOK.md; docs/PAPER/GUIDE_ORIGINAL.md; experiments/archive/legacy_backend_evaluation/**; experiments/configs/alice_execution_plan.yaml; experiments/reports/phase7_3D_deployment_boundary_cleanup_report.md; experiments/reports/phase7_4_alice_script_compatibility_report.md; experiments/reports/phase7_6_7_runpod_cleanup_alice_code_report.md; experiments/reports/phase7_8B_backend_boundary_audit_report.md; experiments/reports/phase7_8C_strict_repo_boundary_cleanup_report.md; experiments/runners/build_query_audit.py; experiments/runners/dry_run_matrix.py; experiments/runners/run_local_smoke.py; experiments/scripts/alice/**; frontend/src/i18n/index.ts; deletions of legacy backend/evaluation, backend logs/scripts, RunPod docs/scripts, backend-root Alice helpers, and tracked .claude local settings.
- exact files intentionally not committed: ignored/local-only .claude/worktrees and any ignored virtualenv/cache artifacts.
- whether Alice BASE smoke can start after commit: yes, only as Phase 7.5 with explicit user approval and only on Alice/Linux.
- exact first Alice/Linux validation commands: bash -n experiments/scripts/alice/alice_setup.sh; bash -n experiments/scripts/alice/alice_base_smoke.sh; bash -n experiments/scripts/alice/alice_thesis_run_plan.sh; python -m compileall backend experiments; python experiments/runners/run_local_smoke.py --help.
- reminder that Phase 7.5 Alice MIDM BASE smoke has not run yet.
