# Paper Documents

## Role

This folder contains the current thesis-facing documents for the focused direction:

```text
HyDE × CAD × SCD combination evaluation in Korean-query / English-paper RAG
```

The folder covers both the 2×2×2 research matrix and the implemented A–F M-RAG service layer.

## Reading Order

| Document | Role |
|---|---|
| `THESIS.md` | current English thesis manuscript based on the verified HyDE × CAD × SCD matrix |
| `THESIS_KO.md` | current Korean thesis manuscript aligned with the English manuscript |
| `SUBMISSION_METADATA.md` | institution-specific metadata and template fields that must not be guessed |
| `PPT_SUMMARY.md` | presentation outline updated to the verified results |
| `PPT_KEYWORDS.md` | presentation keywords |
| `LIMITATIONS_AND_FUTURE_WORK.md` | limitations and future-work notes |
| `scripts/verify_current_thesis_results.py` | read-only reproduction check for the manuscript result tables |
| `REFERENCE_AUDIT_2026-07-11.md` | all-reference verification against primary sources |
| `NEXT_STAGE_VLLM_CLAIM.md` | later serving/optimization candidate notes |

## Current Research Scope

- Research method: 2×2×2 HyDE × CAD × SCD generation matrix on a fixed Paper-RAG backbone.
- System implementation: A-F routed M-RAG paper-review application.
- HyDE quality contrast: answer relevancy `+0.0303 [+0.0016, +0.0615]` with CAD and SCD disabled; the other quality intervals include or touch zero.
- CAD quality contrast: faithfulness `+0.0023 [−0.0903, +0.0952]` over 19 byte-identical-context pairs; no quality improvement is established.
- Language-control result: SCD improves the direct Korean-character ratio by `+0.2203` over 76 matched pairs and reduces drift from 26/76 to 12/76.
- Symmetric quality check: completed on 38 HyDE-off identical-context pairs in English and Korean with `gpt-4o` and fixed `gpt-4.1-2025-04-14`; no nonzero RAG-quality effect replicates across both judges.
- Reproducibility evidence: the retained 152-answer generation artifact, the complete 152-row `gpt-4o` score artifact, the final language-adherence analysis, and `scripts/verify_current_thesis_results.py`.

## Manuscript Result Order

1. Experimental design and eight HyDE × CAD × SCD configurations
2. Controlled HyDE and CAD quality contrasts
3. SCD language-adherence results
4. Symmetric two-judge SCD quality check
5. M-RAG implementation and A-F route policy

## Evidence Handling

The manuscripts use only the current 152-answer generation matrix and contrasts whose inputs were audited. Experiment reports retain raw provenance, judge-specific scores remain in their stated protocols, and the A-F table describes implemented selection points rather than a route-level optimum.
