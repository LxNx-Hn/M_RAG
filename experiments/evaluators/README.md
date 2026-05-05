# Evaluation Adapters

Phase 2 separates two evaluation paths:

- `official_ragas_runner_skeleton.py`: import-guarded official RAGAS readiness and schema validation only. It must not execute RAGAS in Phase 2.
- lightweight/local judge design: a RAGAS-inspired evaluator that uses local or provided judge functions and must not be called official RAGAS.

Metric implementation for language drift, Korean answer ratio, numeric hallucination, and evidence support belongs in evaluator modules, not CAD/SCD decoder modules.
