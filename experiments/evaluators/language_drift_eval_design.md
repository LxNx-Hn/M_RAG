# Language Drift Evaluation Design

`language_drift_rate` and `korean_answer_ratio` are evaluator metrics, not decoder responsibilities.

Planned evaluator inputs:

- generated answer
- expected target language
- optional token-level metadata emitted by Korean-target SCD

Planned outputs:

- `language_drift_rate`
- `korean_answer_ratio`
- per-answer language diagnostics

Phase 2 does not implement or execute the metric.
