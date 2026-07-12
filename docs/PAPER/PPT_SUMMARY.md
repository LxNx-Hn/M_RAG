# M-RAG Presentation Summary

> PPT outline aligned to the verified original Phase 8 and corrected `reference_scd` artifacts.

## 1. Title

- M-RAG
- HyDE × CAD × SCD factor analysis for Korean-query English-paper RAG

## 2. Problem

- Korean users ask about papers whose evidence is often in English
- Retrieval must bridge Korean questions and English passages
- Generation must answer in Korean without drifting into English
- The model may rely on parametric memory instead of retrieved evidence

## 3. Research Question

- How do HyDE, CAD, and SCD affect the measured RAGAS metrics and Korean-language adherence?
- What follow-up metrics are still needed for numeric hallucination and query-type-specific routing?
- How should the graduation-project service use the current global factor-effect findings without overstating route-level validation?

## 4. Core Method

- Fixed Paper-RAG backbone
- HyDE on/off as retrieval-side expansion axis
- CAD on/off as context-faithfulness decoding axis
- SCD on/off as Korean-target language-control axis
- 8-config factorial matrix

## 5. Service System

- FastAPI backend and React frontend
- Paper upload, indexing, chat, sources, SSE streaming
- A-F service routes for QA, section QA, comparison, citation lookup, summary, quiz/flashcards
- Routes are service features, not the thesis algorithmic novelty

## 6. Experiment Matrix

- `hyde_off__no_decoder_control`
- `hyde_off__cad_only`
- `hyde_off__scd_only`
- `hyde_off__cad_scd`
- `hyde_on__no_decoder_control`
- `hyde_on__cad_only`
- `hyde_on__scd_only`
- `hyde_on__cad_scd`

## 7. Metrics

- RAGAS: faithfulness, answer relevancy, context precision, context recall
- Direct language metric: Korean answer ratio and drift rescue
- Numeric hallucination and query-type breakdown remain future analyses
- Never mix original NIM scores with corrected-run `gpt-4o` / fixed `gpt-4.1` scores

## 8. Verified Results

- Original `penalty_additive` SCD v1: null on its Korean-adherence target (−0.0137 paired)
- Corrected `reference_scd`: +0.2203 Korean ratio, 68/76 increases, 15/26 drift rescues
- Harm threshold: 0/20 baseline ≥0.7 cases fell below 0.65; 3/76 pairs still decreased
- `gpt-4o` sensitivity panel: faithfulness −0.0480, answer relevancy −0.0571, context precision +0.0300, context recall −0.0658
- Method boundary: only the language result is judge-independent; SCD-on-only context translation makes the RAG-quality deltas descriptive, not causal
- Symmetric HyDE-off follow-up (38 matched pairs per language): faithfulness unresolved in EN/KO; answer relevancy EN −0.0910 [−0.1725, −0.0240], KO −0.0752 [−0.1501, −0.0138]
- Fixed `gpt-4.1-2025-04-14` cross-judge: all EN/KO overall intervals overlap zero; the `gpt-4o` nonzero answer-relevancy cost does not replicate
- Follow-up boundary: no judge-robust nonzero RAG-quality effect; post-generation normalization still prevents a causal or deployment verdict

## 9. Service Interpretation

- Original-matrix CAD/HyDE policy remains provisional and global
- `reference_scd` is available when Korean language control is required
- Select any deployment combination only after task-specific quality validation
- No route-specific or causal RAG-quality policy follows from either sensitivity panel

## 10. Conclusion

- The thesis contribution is the HyDE/CAD/SCD analysis
- Paper-faithful SCD substantially improves language adherence; faithfulness stays unresolved and the apparent answer-relevancy cost is judge-sensitive
- The M-RAG service demonstrates how that analysis can inform a Korean paper-review assistant
