# M-RAG Presentation Summary

> PPT outline. Keep result slides as placeholders until a verified run exists.

## 1. Title

- M-RAG
- HyDE × CAD × SCD factor analysis for Korean-query English-paper RAG

## 2. Problem

- Korean users ask about papers whose evidence is often in English
- Retrieval must bridge Korean questions and English passages
- Generation must answer in Korean without drifting into English
- The model may rely on parametric memory instead of retrieved evidence

## 3. Research Question

- How do HyDE, CAD, and SCD affect evidence support, numeric hallucination, and language drift?
- Which query types benefit from each factor?
- How should the graduation-project service route policy use those findings?

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

- Evidence support
- Numeric hallucination
- Language drift
- Korean answer ratio
- Query-type breakdown
- Cost/run-size estimate

## 8. Result Policy

- Do not claim improvements before running the approved matrix
- Use pending placeholders until verified artifacts exist
- Keep RAGAS-compatible design separate from lightweight local judging

## 9. Expected Deliverable

- Factor analysis table
- Effect delta summary
- Query-type policy for the graduation-project routed service
- Runtime compatibility audit appendix

## 10. Conclusion

- The thesis contribution is the HyDE/CAD/SCD analysis
- The M-RAG service demonstrates how that analysis can inform a Korean paper-review assistant
