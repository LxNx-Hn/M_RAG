# Lightweight Judge Design

The lightweight/local judge path is RAGAS-inspired but is not official RAGAS.

## Naming

- Backend lightweight evaluator class: `RAGASInspiredEvaluator`
- Backward compatibility aliases may exist temporarily, but new code should use the explicit name.

## Boundary

- Uses a local generator or caller-provided `judge_fn`.
- Produces RAGAS-like metric names for continuity.
- Must not claim to be official RAGAS.
- Must not call OpenAI unless an evaluation script explicitly supplies a configured judge function in a permitted run.

## Phase 2 Safety

No lightweight judge execution is performed in this phase.
