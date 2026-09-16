# Final thesis document cleanup manifest

Date: 2026-09-17

`FINALDOCS/` is the sole thesis-writing and HWP-transfer package. This manifest
records the document-tree cleanup that established that boundary.

## Migrated into this package

- `FINAL_CLAIM_MAP_60Q.md` is the claim-to-artifact map consumed by the offline
  UI evidence replay.
- `verify_finaldocs_60q.py` verifies the manuscript, HWP-transfer materials,
  workbook, evidence files, and current 60-query claim boundaries without a
  network call, model load, retrieval, generation, judge call, or write.

## Removed legacy documentation

- `docs/PAPER/`: superseded 19-query manuscripts, duplicate output packages,
  historical prompts, planning notes, and thesis figures.
- `docs/EXPLAIN/`: superseded explanatory copies tied to the prior thesis
  packages and score tracks.
- `docs/USAGE/ALICE_CLOUD.md`, `ALICE_CLOUD_GUIDE.md`, and `ALICE_SETUP.md`:
  no-longer-needed cloud execution runbooks and pointers.

## Preserved outside FINALDOCS

- `docs/ARCHITECTURE.md`, `docs/FEATURES.md`, `docs/REPO_LAYOUT.md`, and the
  non-thesis files under `docs/USAGE/` remain service and repository guides.
- `experiments/scripts/alice/` remains experiment-runner source code. It is not
  a thesis document or a current cloud-execution guide.
- `experiments/results/` and other stored experiment artifacts remain unchanged.
