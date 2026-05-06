[Summary]
- phase: Phase 7.6 RunPod cleanup + Phase 7.7 Alice execution code
- readiness before: ready_for_alice_base_smoke_with_explicit_user_approval
- readiness after: ready_for_alice_base_smoke_after_commit
- files deleted: backend/scripts/runpod_one_shot.sh; backend/scripts/runpod_start.sh; docs/USAGE/RUNPOD_A100_NO_SSH.md
- files created: docs/USAGE/ALICE_CLOUD.md; experiments/configs/alice_execution_plan.yaml; experiments/scripts/alice/alice_setup.sh; experiments/scripts/alice/alice_base_smoke.sh; experiments/scripts/alice/alice_thesis_run_plan.sh; experiments/reports/phase7_6_7_runpod_cleanup_alice_code_report.md
- files modified: backend/config.py; backend/scripts/master_run.py; docs/PAPER/DOC_SYNC_PLAN_35.md; docs/USAGE/ALICE_CLOUD_GUIDE.md; docs/USAGE/ALICE_SETUP.md; docs/USAGE/README.md; experiments/runners/run_local_smoke.py
- actual generation run: no
- actual tuning run: no
- commit made: no

[RunPod Cleanup]
- initial RunPod match count: 13 lines across 7 files
- files deleted: backend/scripts/runpod_one_shot.sh; backend/scripts/runpod_start.sh; docs/USAGE/RUNPOD_A100_NO_SSH.md
- references removed: backend/config.py cache comment; backend/scripts/master_run.py external GPU comment; docs/USAGE/README.md usage map; docs/PAPER/DOC_SYNC_PLAN_35.md historical usage sync plan
- remaining RunPod match count: 0 active matches before this report was written; 12 report-only matches after report creation
- remaining references classification: phase-report-only cleanup wording; no active code/doc execution path remains
- active RunPod blocker: no

[Alice Code]
- docs created: docs/USAGE/ALICE_CLOUD.md
- configs created: experiments/configs/alice_execution_plan.yaml
- scripts created: experiments/scripts/alice/alice_setup.sh; experiments/scripts/alice/alice_base_smoke.sh; experiments/scripts/alice/alice_thesis_run_plan.sh
- runners created or modified: modified experiments/runners/run_local_smoke.py; no duplicate Alice Python runner was created
- Alice smoke command: CONFIRM_ALICE_BASE_SMOKE=1 bash experiments/scripts/alice/alice_base_smoke.sh
- Alice tuning command: bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage tuning
- Alice main-generation command: bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage main-generation after experiments/configs/frozen_params.yaml exists
- freeze checkpoint guard: main-generation fails closed unless experiments/configs/frozen_params.yaml exists or a later explicit CONFIRM_FROZEN_PARAMS=1 approval is provided

[Secret Safety]
- SSH private key stored in repo: no
- API token stored in repo: no
- HF token stored in repo: no
- OpenAI key stored in repo: no
- instructions for user-provided secrets: use environment variables, huggingface-cli login, ssh-agent, chmod 600 local key files, or Alice secret mechanisms; never commit secrets

[Execution Safety]
- Alice BASE smoke requires explicit confirmation: yes, CONFIRM_ALICE_BASE_SMOKE=1 plus runner --alice-mode and --confirm-alice-base
- smoke sample cap: yes, query_limit=1 and max_samples=1 are enforced in the Alice shell wrapper; run_local_smoke.py remains one-sample only
- OpenAI default: disabled
- RAGAS default: disabled
- GT regeneration: disabled
- main generation requires frozen params: yes
- optional final eval requires explicit approval: yes, CONFIRM_OPTIONAL_FINAL=1

[Validation]
- bash syntax: attempted; local Windows bash is WSL-backed and unavailable. Initial sandbox run returned Bash/Service/CreateInstance/E_ACCESSDENIED; escalated run returned /bin/bash no such file or directory. Rerun bash -n on Alice/Linux before execution.
- compileall: passed with python -m compileall backend experiments
- JSON validation: passed for tuning_queries, decoder_main_queries, candidate_final_eval_queries
- YAML validation: passed for alice_execution_plan.yaml, tuning_plan.yaml, frozen_params.draft.yaml
- dry-run tuning plan: passed; 8 configs x 5 tuning queries = 40 planned samples, no model/OpenAI/RAGAS/GT calls
- dry-run matrix: passed; 8 configs x 19 decoder_main queries = 152 planned main samples, leakage check passed, runtime core forbidden hits empty
- dry-run generation plan: passed; config-limit 2 x limit 3 = 6 planned samples, no model/OpenAI/RAGAS/GT calls
- RunPod grep: passed before report creation with zero active matches; final grep after report creation shows only this phase report
- issues: bash -n could not be run on this Windows host because no usable Bash runtime is available

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
- experiment result files deleted: no
- secrets committed or written: no

[Decision]
- decision: ready_for_alice_base_smoke_after_commit
- explanation: Active RunPod execution references were removed, Alice setup/smoke/planning scripts and runbook were added, BASE smoke is explicit-confirmation-only, and Python/YAML/JSON/dry-run validation passed. The only incomplete local check is bash -n because this Windows host has no usable Bash runtime; rerun bash syntax checks on Alice before executing the smoke script.

[Next Step]
- whether changes should be committed: yes, after reviewing the Phase 7.6/7.7 diff
- exact files recommended for commit: backend/config.py; backend/scripts/runpod_one_shot.sh; backend/scripts/runpod_start.sh; docs/PAPER/DOC_SYNC_PLAN_35.md; docs/USAGE/ALICE_CLOUD.md; docs/USAGE/ALICE_CLOUD_GUIDE.md; docs/USAGE/ALICE_SETUP.md; docs/USAGE/README.md; docs/USAGE/RUNPOD_A100_NO_SSH.md; experiments/configs/alice_execution_plan.yaml; experiments/runners/run_local_smoke.py; experiments/reports/phase7_6_7_runpod_cleanup_alice_code_report.md; experiments/scripts/alice/alice_setup.sh; experiments/scripts/alice/alice_base_smoke.sh; experiments/scripts/alice/alice_thesis_run_plan.sh
- whether Alice MIDM BASE 1-sample smoke can start after commit: yes, with explicit user approval and after bash syntax checks pass on Alice
- recommended Alice instance: G-NAHPM-40 for smoke; G-NAHP-80 if smoke OOMs or main run needs more headroom
- reminder that local Mini outputs are validation-only: yes
- reminder that Alice Base outputs are thesis-grade only after actual thesis run phase: yes
