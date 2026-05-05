# Numeric Hallucination Evaluation Design

`numeric_hallucination_rate` is an evaluator metric, not a CAD decoder responsibility.

Planned evaluator inputs:

- question
- generated answer
- ground truth or reference answer
- retrieved contexts

Planned outputs:

- extracted answer numbers
- extracted reference/context numbers
- unsupported numeric claim flags
- aggregate `numeric_hallucination_rate`

Phase 2 does not execute the metric.
