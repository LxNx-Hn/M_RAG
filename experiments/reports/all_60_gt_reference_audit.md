# All-60 Ground-Truth Literal Audit

## Scope

This report standardizes the final acceptance rule for the complete thesis query set:

- retained main split: 19 queries (`decoder_main_queries`)
- held-out extension: 41 queries (`extended_validation_questions` + `extended_validation_literal_gt`)
- pooled analysis target: 60 independent query units
- paper allocation after pooling: 15 queries each for RAG, CAD, RAPTOR, and Mi:dm

The two subsets have different construction histories, but the final reference criterion is now identical: **every RAGAS reference must occur as a contiguous normalized extract in its checked-in source PDF.** No model or judge is allowed to create, rewrite, or repair a reference during this audit.

## Retained 19

The original main split keeps the existing verified extractive `answer_span` values. The repository already records a Phase-8 readiness check in `experiments/reports/phase8_parameter_freeze_readiness.md` stating that the evaluation references were **verified grounded 24/24**; that set comprised the 5 tuning queries plus the 19 decoder-main queries. Phase 6.7 then removed `gt_status=not_found` candidates from tuning/main/final-facing clean splits rather than regenerating GT.

For the extension handoff, historical evidence is no longer the only guard. `experiments/scripts/audit_all_60_gt_literal.py` freshly re-scans each of the retained 19 `answer_span` values across every page of its checked-in source PDF using the same normalization function used for the extension.

## Held-out 41

The extension references live in `experiments/data/query_splits/extended_validation_literal_gt.json`. They were extracted from the checked-in source PDFs and record a zero-based `source_page`. `experiments/scripts/audit_extended_gt_literal.py` requires each span to literal-match that declared page and fails closed otherwise.

The extension GT construction does **not** call OpenAI or another LLM. This does not alter the retained 19 references; it only avoids repeating the earlier unstable pseudo-GT generation path. What is made identical across all 60 items is the source-grounding acceptance rule.

## Unified runtime audit

Run:

```bash
python experiments/scripts/audit_all_60_gt_literal.py \
  --report experiments/results/analysis/all_60_gt_literal_audit.json
```

Required result:

```text
main=19/19 extension=41/41 total=60/60 failures=0 passed=true
```

The script also enforces:

- no duplicate query IDs inside either subset
- no query-ID overlap between retained 19 and extension 41
- exactly 60 pooled query units
- exactly 15 query units per source paper after pooling
- `gt_status=valid` and `answerability_status=answerable` for all retained main references
- page-level literal matching for all 41 extension references
- whole-PDF literal matching for all 19 retained references

## Execution gate

`alice_prepare_extended_validation.sh`, `alice_extended_validation.sh`, and `score_extended_validation.sh` invoke the all-60 audit before generation/scoring. Therefore a fresh Alice run cannot proceed if even one retained or extension reference fails the common source-grounding rule.

## Interpretation

This audit deliberately distinguishes **reference construction** from **reference acceptance**:

- retained 19: existing extractive answer spans from the original Track-1 asset pipeline, subsequently grounded/cleaned and retained for the final experiment
- extension 41: manually extracted literal spans
- final acceptance for both: the same literal source-PDF verification

This preserves the original final experiment references while making the 60-query pooled analysis use a single, auditable source-grounding standard.
