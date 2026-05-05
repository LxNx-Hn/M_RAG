# Paper Documents

## Role

This folder contains thesis-facing documents for the Phase 5 direction:

```text
HyDE × CAD × SCD factor analysis in Korean-query / English-paper RAG
```

The routed M-RAG application is documented as a graduation-project service layer, not as the core thesis algorithm.

## Reading Order

| Document | Role |
|---|---|
| `THESIS.md` | thesis draft and required table structure |
| `GUIDE_ORIGINAL.md` | Phase 5 guide for method boundaries, matrix, and safety rules |
| `PPT_SUMMARY.md` | presentation outline aligned to Phase 5 claims |
| `PPT_KEYWORDS.md` | presentation keywords |
| `LIMITATIONS_AND_FUTURE_WORK.md` | limitations and future-work notes |
| `NEXT_STAGE_VLLM_CLAIM.md` | later serving/optimization candidate notes |

## Current Claim Boundary

- Core thesis method: HyDE/CAD/SCD factor analysis.
- Service architecture: A-F routed paper-review application.
- Query-type policy: derived from the main analysis after results exist.
- Result values: pending verified experiment run.

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

Do not copy legacy result numbers into the thesis unless the corresponding approved experiment run has been executed and verified. Do not describe the service router as the core thesis algorithm.
