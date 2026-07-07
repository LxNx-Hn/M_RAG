# Ground Truth Policy

Ground truth is the verified extractive `answer_span` recorded in each query split
under `experiments/data/query_splits/`. It is used directly as the RAGAS reference /
`ground_truth` and is **not** regenerated.

Each split entry's `answer_span` was checked to be present in its target paper (a
grounding check), so the reference is an extractive gold span rather than a
model-generated answer key.

GT normalization or translation decisions are fairness-sensitive and must be
documented symmetrically before any final evaluation.
