[Summary]
- phase: Phase 7.3E Backend data boundary cleanup
- readiness before: ready_for_phase7_3_4_boundary_commit
- readiness after: ready_for_phase7_3_4_boundary_commit
- files moved: 8 tracked source PDFs moved from backend/data to experiments/data/source_papers; backend/scripts/download_test_papers.py moved to experiments/scripts/download_test_papers.py; 65 ignored local runtime/upload PDFs moved out of backend/data into an ignored local preservation snapshot at experiments/archive/runtime_data_snapshot/backend_data
- files deleted: generated non-venv __pycache__ directories created by validation only
- files modified: .gitignore; backend/config.py; backend/scripts/index_papers.py; docs/USAGE/DEPLOY.md; docs/USAGE/DEPLOYMENT_BOUNDARY.md; docs/USAGE/POSTGRES_GUIDE.md; experiments/scripts/download_test_papers.py
- files created: experiments/data/source_papers/README.md; experiments/reports/phase7_3E_backend_data_boundary_cleanup_report.md
- commit made: no

[Backend Data Inventory]
- backend/data exists: no, after cleanup
- tracked files: 0 after cleanup; before cleanup there were 8 tracked paper PDFs under backend/data
- untracked files: 0 remaining under backend/data; 65 ignored local runtime/upload PDFs were preserved outside backend/data
- PDFs: 8 tracked thesis/source PDFs moved to experiments/data/source_papers; 65 ignored local runtime/upload PDF copies moved to ignored runtime_data_snapshot
- metadata: none found under backend/data
- generated caches: backend/chroma_db remains ignored runtime vector-store data; no tracked backend/data cache files found
- vector stores: no vector-store files under backend/data; backend/chroma_db is ignored runtime vector-store storage
- unknown files: none remaining under backend/data

[Cleanup Actions]
- source papers moved: yes, 8 tracked PDFs moved to experiments/data/source_papers with filenames preserved
- metadata moved: none, because no backend/data metadata files were found
- demo seed moved: none found under backend/data
- generated data deleted: only generated __pycache__ directories outside backend/.venv after validation
- runtime data ignored: backend/data/* remains ignored; backend/chroma_db/ was explicitly ignored; experiments/archive/runtime_data_snapshot/ was added as an ignored local preservation area for moved runtime/upload copies
- config updates: backend/config.py now reads MRAG_DATA_DIR and MRAG_CHROMA_DIR before falling back to ignored local runtime directories
- docs updates: deployment docs now identify experiments/data/source_papers as the checked-in thesis paper location and MRAG_DATA_DIR/MRAG_CHROMA_DIR as runtime volume paths

[Final Data Boundary]
- backend/data tracked files: none
- backend runtime data policy: runtime uploads belong in MRAG_DATA_DIR or a mounted/ignored runtime data volume; runtime vector stores belong in MRAG_CHROMA_DIR or a mounted/ignored vector-store volume
- experiments source paper path: experiments/data/source_papers
- experiments metadata path: reserved under experiments/data if future paper metadata is added; no metadata was found or moved in this phase
- deploy package includes source PDFs: no under backend; source PDFs are under experiments/data/source_papers
- deploy package includes generated cache: no tracked backend generated cache; backend/chroma_db and runtime_data_snapshot are ignored

[Validation]
- compileall: passed with python -m compileall backend experiments
- JSON validation: passed for tuning_queries.json, decoder_main_queries.json, and candidate_final_eval_queries.json
- run_tuning_plan dry-run: passed with --dry-run --plan-only --limit 5
- dry_run_matrix: passed with --experiment main-hyde-cad-scd --estimate-cost --dry-run
- run_generation plan: passed with --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3
- run_local_smoke help: passed with --help only
- issues: compileall traversed ignored local backend/.venv, backend/chroma_db, and ignored runtime_data_snapshot directories while compiling active Python files; no execution path was invoked. The ignored runtime_data_snapshot is local preservation only and should not be force-added.

[Safety]
- generation run: no
- tuning run: no
- main experiment run: no
- --execute used: no
- --execute-smoke used: no
- model calls made: no
- OpenAI calls made: no
- RAGAS calls made: no
- source PDFs deleted: no
- metadata deleted: no
- query splits modified: no
- smoke evidence deleted: no
- .claude/worktrees touched: no
- commit made: no

[Decision]
- ready_for_phase7_3_4_boundary_commit
- Explanation: backend/data no longer exists as a tracked or active local data directory, git ls-files backend/data is empty, tracked thesis paper PDFs now live under experiments/data/source_papers, backend runtime data paths are environment-configurable, and static/dry-run validation passed without model/API execution. The only non-commit artifact is the ignored runtime_data_snapshot preservation directory for local upload/runtime copies.

[Next Step]
- whether this should be committed with Phase 7.3D/7.4: yes, commit together after reviewing the combined boundary/data/Alice compatibility diff
- whether backend deploy package is now data-clean: yes, for tracked deploy-source contents
- whether Alice BASE smoke can start after commit: yes, only after explicit Phase 7.5 approval and Alice/Linux bash syntax validation
- any manual review needed: do not force-add experiments/archive/runtime_data_snapshot; optionally delete that ignored local preservation snapshot later only if the user confirms those local runtime/upload PDF copies are no longer needed
