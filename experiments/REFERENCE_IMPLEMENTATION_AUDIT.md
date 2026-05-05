# Reference Implementation Audit

This file summarizes repository-specific implementation status from Phase 1,
Phase 2, and Phase 3 reports. It is not a result file.

## CAD

- Status: exact single-sequence Context-Aware Decoding was reported implemented
  in Phase 2.
- Formula: `(1 + alpha) * context_scores - alpha * no_context_scores`.
- No-context branch: template-matched no-context prompt with same generated
  prefix through an uncached reference path.
- Phase 4 action: no CAD logic changes.

## SCD

- Status: Korean-target Soft Constrained Decoding was reported implemented in
  Phase 2.
- Policy: Korean tokens, neutral tokens, and technical whitelist terms are not
  penalized; other non-target tokens may receive beta penalty.
- Phase 4 action: no SCD logic changes.

## RAGAS

- Status: official RAGAS runner skeleton is separated from the lightweight
  `RAGASInspiredEvaluator`.
- Phase 4 action: keep dry-run/schema readiness only. Do not execute RAGAS.

## HyDE

- Status: shared runtime implementation exists in query expansion/retrieval
  paths and is preserved as a main experiment axis.
- Phase 4 action: do not convert HyDE into multi-query fusion and do not expose
  matrix controls in frontend.

## Demoted / Excluded From Core Main Path

The main Phase 4 framework excludes unsupported methods from the core thesis
experiment. Mentions of deprecated legacy labels in old evaluation/data/docs are
not treated as current results and require Phase 5 documentation cleanup or
legacy demotion decisions.

