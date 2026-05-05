# GT Validation Design

## Scope

This is a design placeholder only. It does not execute GT generation or judge
calls.

## Checks Before Final Evaluation

- Confirm every final candidate query has an answer key or a documented
  not-found label.
- Keep tuning queries disjoint from final-eval candidates.
- Preserve raw GT and normalized GT separately.
- Document any normalization as meaning-preserving and symmetric.
- Treat translation or language normalization as a protocol decision, not a
  harmless cleanup step.

