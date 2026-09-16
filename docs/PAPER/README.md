# Paper Documents

## Graduation submission package

The current Korean application-experiment submission is
[output/application_study/README.md](output/application_study/README.md).
It follows the supplied graduation-report chapter structure and separates the
application feature document from the experiment manuscript. It includes the
Korean manuscript/TXT, six figures, a 14-slide presentation and speaker notes.
See [APPLICATION_STUDY_REVIEW.md](APPLICATION_STUDY_REVIEW.md) for the request audit
and run `python -X utf8 docs/PAPER/scripts/verify_application_study.py` for its
retained-data verification.

The technical manuscripts and older presentation outlines listed below remain
available as supporting documents. Use the submission package above for HWP transfer.

## Role

This folder contains the current thesis-facing documents for the focused direction:

```text
HyDE × CAD × SCD combination evaluation in Korean-query / English-paper RAG
```

The thesis-facing documents cover the 2×2×2 research matrix. Product features and A–F routes are retained in the separate application document, not presented as thesis contributions.

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
| `EVIDENCE_SCREENSHOT_PLAN.md` | claim inventory, retained artifact mapping, and deterministic terminal capture plan |

## Current Research Scope

- Research method: RAG-Cube, a 2×2×2 HyDE × CAD × SCD configuration matrix on a fixed Paper-RAG backbone.
- Out of thesis scope: the A-F routed M-RAG paper-review application; see the separate application document when its implementation record is needed.
- HyDE quality contrast: answer relevancy `+0.0303 [+0.0016, +0.0615]` with CAD and SCD disabled; the other quality intervals include or touch zero.
- CAD quality contrast: faithfulness `+0.0023 [−0.0903, +0.0952]` over 19 byte-identical-context pairs; no quality improvement is established.
- Language-control result: SCD improves the direct Korean-character ratio by `+0.2203` over 76 matched pairs and reduces drift from 26/76 to 12/76.
- Symmetric quality check: completed on 38 HyDE-off identical-context pairs in English and Korean with `gpt-4o` and fixed `gpt-4.1-2025-04-14`; no nonzero RAG-quality effect replicates across both judges.
- Reproducibility evidence: the retained 152-answer generation artifact, the complete 152-row `gpt-4o` score artifact, the final language-adherence analysis, and `scripts/verify_current_thesis_results.py`.
- Terminal evidence replay: `../../cli/evidence_replay.py` displays stored cases without loading a model, parsing PDFs, or calling a judge.

## Manuscript Result Order

1. Experimental design and eight HyDE × CAD × SCD configurations
2. Controlled HyDE and CAD quality contrasts
3. SCD language-adherence results
4. Symmetric two-judge SCD quality check

## Evidence Handling

The manuscripts use only the current 152-answer generation matrix and contrasts whose inputs were audited. Experiment reports retain raw provenance and judge-specific scores remain in their stated protocols. Service implementation evidence is maintained separately and is not a route-level experimental result.
