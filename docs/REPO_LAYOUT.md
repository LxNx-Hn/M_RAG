# Repository Layout

Cube-RAG is organized into four responsibility boundaries. The **ops** runtime does not
import any code from the **experiment** layer, so the service runs even if
`experiments/` is deleted. The evidence CLI reads only stored experiment artifacts;
it does not import either runtime layer.

## Layers

| Layer | Location | Role |
|---|---|---|
| **Ops** (service runtime) | `backend/`, `frontend/` | FastAPI API + React app for the A–F paper-review chatbot |
| **Experiment** (thesis) | `experiments/` | fixed Paper-RAG backbone, HyDE×CAD×SCD 8-config matrix, runners, official RAGAS evaluator, analyzers, results, reports |
| **Docs** | `docs/` | runtime architecture, feature, repository-layout, and service-usage documentation |
| **Final thesis** | `FINALDOCS/` | self-contained 60-query Korean manuscript, HWP materials, evidence, and validation |
| **Evidence CLI** | `cli/` | offline, read-only presentation/replay of final thesis artifacts |

## Decoupling guarantee

- `backend/` imports nothing from `experiments/`. Verify:
  `grep -rn "experiments" backend --include=*.py` returns no import.
- The experiment layer depends on the ops modules one-way (runners add `backend/` to
  `sys.path` to reuse `modules/`), never the reverse.
- Removing `experiments/` leaves the ops service fully functional (API, pipelines,
  frontend build are unaffected).
- `cli/evidence_replay.py` uses the Python standard library plus its local
  registry only. It never starts a server, loads Mi:dm/BGE/CrossEncoder, parses a
  source PDF, connects to PostgreSQL, calls a judge, or writes result files.

## Tests

| Suite | Location | Run |
|---|---|---|
| Ops tests | `tests/backend/` | `python -m pytest` (default `testpaths`) |
| Experiment tests | `experiments/tests/` | `python -m pytest experiments/tests` |

Both use `pythonpath = backend` from `pytest.ini`. Ops tests never import experiment
code; experiment tests may import ops modules (one-way dependency).

## Secrets and runtime artifacts

Never committed (see `.gitignore`): `.env`, model caches, Chroma DB, BM25 pickles,
runtime DBs, `NVIDIA_API_KEY`, `OPENAI_API_KEY`. Judge keys are read from the
gitignored repo-root `.env` by `experiments/evaluators/official_ragas_runner.py`.
