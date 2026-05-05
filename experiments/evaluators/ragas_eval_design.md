# Official RAGAS Evaluation Design

The official RAGAS path is separate from the lightweight judge path.

## Required Inputs

- `question` or `user_input`
- `answer` or `response`
- `contexts` or `retrieved_contexts`
- `ground_truth` or `reference` when a selected metric requires it

## Planned Metrics

- `faithfulness`
- `response_relevancy` or `answer_relevancy`
- `context_precision`
- `context_recall`

## Phase 2 Boundary

- Provide import readiness checks.
- Validate sample schemas.
- Do not import and execute RAGAS evaluation.
- Do not call OpenAI or any external judge.
- Do not install dependencies.
