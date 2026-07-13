# M-RAG Presentation Summary

PPT outline aligned to the current HyDE × CAD × SCD experiment and M-RAG implementation.

## 1. Title

- M-RAG
- HyDE × CAD × SCD combination evaluation for Korean-query English-paper RAG

## 2. Problem

- Korean users ask about papers whose evidence is often in English
- Retrieval must bridge Korean questions and English passages
- Generation must answer in Korean without drifting into English
- The model may rely on parametric memory instead of retrieved evidence

## 3. Research Question

- How do HyDE, CAD, and SCD affect the measured RAGAS metrics and Korean-language adherence?
- What follow-up metrics are still needed for numeric hallucination and query-type-specific routing?
- How should the graduation-project service use the current global factor-effect findings without overstating route-level validation?

## 4. Method

- Fixed Paper-RAG backbone
- HyDE on/off as retrieval-side expansion axis
- CAD on/off as context-faithfulness decoding axis
- SCD on/off as Korean-target language-control axis
- 8-config factorial matrix

## 5. Service System

- FastAPI backend and React frontend
- Paper upload, indexing, chat, sources, SSE streaming
- A-F service routes for QA, section QA, comparison, citation lookup, summary, quiz/flashcards
- Service and experiment layers share the M-RAG codebase

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
- Use the controlled SCD-off HyDE/CAD contrasts and the separate symmetric SCD quality panels

## 8. Verified Results

- HyDE baseline contrast: answer relevancy +0.0303 [+0.0016, +0.0615]; other quality intervals include or touch zero
- CAD byte-identical-context contrast: faithfulness +0.0023 [−0.0903, +0.0952]; no quality improvement established
- SCD result: +0.2203 mean Korean ratio over 76 matched pairs, with 68 improvements and 3 declines outside the ±0.02 tie band
- Language drift: 26/76 without SCD versus 12/76 with SCD
- HyDE × CAD strata: Korean-ratio deltas +0.1981, +0.2415, +0.2012, and +0.2402
- Symmetric HyDE-off check (38 matched pairs per language): every faithfulness interval includes zero
- `gpt-4o` answer-relevancy deltas: English −0.0910 [−0.1725, −0.0240], Korean −0.0752 [−0.1501, −0.0138]
- Fixed `gpt-4.1-2025-04-14`: English and Korean answer-relevancy intervals include zero, so a nonzero quality effect does not replicate across judges

## 9. Service Interpretation

- SCD is selected when Korean language control is required
- HyDE and CAD remain selectable modules that require task-specific validation
- Select any deployment combination only after task-specific quality validation
- No route-specific or causal RAG-quality policy follows from either sensitivity panel

## 10. Conclusion

- The thesis combines a HyDE/CAD/SCD combination evaluation with the implemented M-RAG system
- SCD substantially improves language adherence across all four HyDE × CAD strata; the symmetric quality check remains judge-sensitive
- The M-RAG service demonstrates how that analysis can inform a Korean paper-review assistant
