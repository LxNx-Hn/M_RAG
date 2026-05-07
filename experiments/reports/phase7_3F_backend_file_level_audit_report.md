[Summary]
- phase: Phase 7.3F - backend file-level audit and minimal cleanup
- readiness before: ready_for_phase7_3F_backend_file_level_audit
- readiness after: ready_for_phase7_3F_commit
- files moved: backend/pytest.ini -> pytest.ini; backend/tests/* -> tests/backend/*
- files deleted: none; backend/tests directory removed only after its files were moved
- files modified: backend/.env.example; backend/scripts/backup.sh; docs/USAGE/DEPLOYMENT_BOUNDARY.md; docs/USAGE/TESTING_GUIDE.md; tests/backend/test_track2_static_asset.py
- files created: pytest.ini; tests/backend/*; experiments/reports/phase7_3F_backend_file_level_audit_report.md
- commit made: no

[Backend Top-Level Classification]
- backend/.venv: local_ignored_not_deploy_source; ignored local virtualenv, not committed and not touched
- backend/alembic: backend_runtime_keep; database migration runtime source
- backend/api: backend_runtime_keep; FastAPI runtime source
- backend/modules: backend_runtime_keep; retrieval, generation, decoding, parsing, and service modules
- backend/pipelines: backend_runtime_keep; service route runtime pipelines
- backend/scripts: backend_operational_script_keep; contains only operational backend helpers after file-level audit
- backend/tests: move_tests_to_tests_backend; moved to tests/backend because tests are repo QA, not deployable backend runtime
- backend/.env: local_ignored_not_deploy_source; ignored local environment file, not committed and not touched
- backend/.env.example: backend_config_template_keep; sanitized runtime template, legacy GT-generation comments removed
- backend/alembic.ini: backend_runtime_keep; migration config
- backend/config.py: backend_runtime_keep; runtime config with MRAG_DATA_DIR and MRAG_CHROMA_DIR support
- backend/Dockerfile: backend_docker_runtime_keep; backend deploy image definition
- backend/pytest.ini: move_tests_to_tests_backend; moved to root pytest.ini with pythonpath=backend and testpaths=tests/backend
- backend/requirements.txt: backend_runtime_keep; backend dependency manifest

[Backend Scripts Classification]
- path: backend/scripts/backup.sh | classification: backend_operational_script_keep | reason: operational DB/runtime volume backup helper | action: patched to use MRAG_DATA_DIR/MRAG_CHROMA_DIR and skip absent runtime directories
- path: backend/scripts/cleanup_inactive.py | classification: backend_operational_script_keep | reason: operational inactive-user cleanup utility with dry-run/execute guard | action: kept
- path: backend/scripts/download_models.py | classification: backend_operational_script_keep | reason: operational model cache/preparation helper for BGE-M3, CrossEncoder, and configured LLM; not run in this phase | action: kept
- path: backend/scripts/entrypoint.sh | classification: backend_operational_script_keep | reason: Docker/runtime entrypoint for Alembic and uvicorn | action: kept
- path: backend/scripts/index_papers.py | classification: backend_operational_script_keep | reason: runtime API upload/indexing helper using MRAG_DATA_DIR/API token; no experiment dependency | action: kept

[Backend Tests Classification]
- path: tests/backend/conftest.py | classification: move_tests_to_tests_backend | reason: pytest collection config for backend QA tests | action: moved from backend/tests
- path: tests/backend/test_api.py | classification: move_tests_to_tests_backend | reason: manual/API integration smoke script, not deployable backend runtime | action: moved from backend/tests and remains ignored by conftest during pytest collection
- path: tests/backend/test_modules.py | classification: move_tests_to_tests_backend | reason: static module tests for QueryRouter and SCDDecoder | action: moved from backend/tests
- path: tests/backend/test_static_smoke.py | classification: move_tests_to_tests_backend | reason: static backend module smoke tests | action: moved from backend/tests
- path: tests/backend/test_track2_static_asset.py | classification: move_tests_to_tests_backend | reason: static Track 2 template asset test | action: moved from backend/tests and updated to read experiments/data/query_splits/query_templates.json

[Boundary Result]
- backend contains runtime source only: yes for tracked deployable source; backend tests moved to tests/backend
- backend/tests remaining: no
- backend/scripts non-runtime files remaining: none found
- backend/data tracked files: none
- backend/evaluation: absent
- backend/logs: absent
- backend imports experiments: no active references found
- frontend references experiments: no active references found
- unknown files: none

[Validation]
- compileall: passed with python -m compileall backend experiments
- JSON validation: passed for tuning_queries, decoder_main_queries, and candidate_final_eval_queries
- dry-run tuning: passed with python experiments/runners/run_tuning_plan.py --dry-run --plan-only --limit 5
- dry-run matrix: passed with python experiments/runners/dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
- dry-run generation: passed with python experiments/runners/run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3
- run_local_smoke help: passed with python experiments/runners/run_local_smoke.py --help
- pytest: passed with python -m pytest tests/backend -q; 11 passed
- issues: compileall traversed ignored local backend/.venv because the local directory exists, but no validation failure occurred

[HF / Model Note]
- HF_TOKEN required for this phase: no
- model download attempted: no
- model load attempted: no
- Phase 7.5 note: Alice MIDM BASE smoke has not run and remains a later explicitly approved phase

[Safety]
- generation run: no
- tuning run: no
- main experiment run: no
- --execute used: no
- --execute-smoke used: no
- model download attempted: no
- model load attempted: no
- OpenAI calls made: no
- RAGAS calls made: no
- GT regenerated: no
- query splits modified: no
- source PDFs deleted: no
- metadata deleted: no
- commit made: no

[Decision]
- ready_for_phase7_3F_commit
- explanation: backend file-level audit found no remaining active experiment/evaluation/log/RunPod/Alice execution artifacts in deployable backend source. The only cleanup needed was moving backend QA tests out of backend, sanitizing the backend env template, and making the backend backup helper respect external runtime data/vector-store paths.

[Next Step]
- whether to commit this cleanup: yes, after user approval
- exact files recommended for commit: backend/.env.example; backend/scripts/backup.sh; docs/USAGE/DEPLOYMENT_BOUNDARY.md; docs/USAGE/TESTING_GUIDE.md; pytest.ini; tests/backend/*; deletion of backend/pytest.ini and backend/tests/*; experiments/reports/phase7_3F_backend_file_level_audit_report.md
- whether Alice/Linux validation can start after this: yes, after committing Phase 7.3F and before any Phase 7.5 smoke
- any manual review needed: optional review of local ignored backend/.venv and backend/.env only; they are not deploy source and were not touched
