# Paper Documents

## Role

This folder contains the current thesis-facing documents for the focused direction:

```text
HyDE × CAD × SCD factor analysis in Korean-query / English-paper RAG
```

The routed M-RAG application is documented as a graduation-project service layer, not as the core thesis algorithm.

## Reading Order

| Document | Role |
|---|---|
| `THESIS.md` | current thesis draft with verified original-matrix and `reference_scd` results |
| `GUIDE_ORIGINAL.md` | historical Phase 5 guide for method boundaries, matrix, and safety rules |
| `PPT_SUMMARY.md` | presentation outline updated to the verified results |
| `PPT_KEYWORDS.md` | presentation keywords |
| `LIMITATIONS_AND_FUTURE_WORK.md` | limitations and future-work notes |
| `REFERENCE_AUDIT_2026-07-11.md` | all-reference verification against primary sources |
| `NEXT_STAGE_VLLM_CLAIM.md` | later serving/optimization candidate notes |

## Current Claim Boundary

- Core thesis method: HyDE/CAD/SCD factor analysis.
- Service architecture: A-F routed paper-review application.
- Query-type policy: global provisional defaults only; route-specific validation remains future work.
- Original Phase 8 result: completed under the fixed NVIDIA NIM judge (583/608 scored cells).
- Corrected `reference_scd`: completed, with strong judge-independent language-adherence improvement. Its first `gpt-4o` panel has 0/608 null cells but is a protocol-specific sensitivity analysis because only SCD-on contexts were translated.
- Symmetric follow-up: completed on the 38 HyDE-off identical-context SCD pairs in both English and Korean. Faithfulness is directionally unresolved. `gpt-4o` gives negative answer-relevancy intervals, but fixed `gpt-4.1-2025-04-14` intervals overlap zero in both languages; the nonzero cost is not cross-judge robust.
- Canonical result reports: `../../experiments/reports/reference_scd_rerun_report.md`, `reference_scd_rerun_report_KO.md`, and `../../experiments/reports/reference_scd_symmetric_cross_judge_report.md`.

## Required Table Order

1. Table 1. Experimental Setup
2. Table 2. Main HyDE × CAD × SCD Factorial Ablation
3. Table 3. Effect Delta Summary
4. Table 4. Query-Type Breakdown
5. Table 5. Numeric Hallucination and Evidence Support
6. Table 6. Language Drift and Korean Answer Ratio
7. Table 7. Routed Policy for Graduation-Project System

Appendices A1-A6 are defined in `THESIS.md`.

## Safety

Keep the original `penalty_additive` v1 and corrected `reference_scd` result tracks explicitly labeled; never blend scores across their different implementations or judges. Do not describe the service router as the core thesis algorithm.
