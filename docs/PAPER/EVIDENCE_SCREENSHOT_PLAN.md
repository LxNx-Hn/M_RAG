# Thesis Evidence and Screenshot Plan

## Scope and source-of-truth decision

This inventory was made from `THESIS.md` and the checked-in artifacts, not from
older README prose. The final experiment is
`main-hyde-cad-scd-reference-scd`: 152 succeeded records in
`experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl`
(19 query IDs × 8 configurations), generated with
`K-intelligence/Midm-2.0-Base-Instruct`. The final quality score source is
`experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json`.
The direct language analysis and symmetric two-judge analyses are separate,
retained result sources; they must not be averaged together.

The screenshot interface is `cli/evidence_replay.py`. It is a read-only viewer:
it replays stored text and artifacts and never re-runs retrieval, generation, or
judging. `E06` is a candidate for human review, not a pre-labelled
hallucination example.

## Claim inventory

### C01 Fixed experimental unit

- **Section:** Abstract; §§7, 9.
- **Claim:** Fixed Paper-RAG with HyDE/CAD/SCD on/off produces 19 × 8 = 152 answers.
- **Evidence:** final generation JSONL; `fixed_backbone.yaml`; matrix config.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** record, unique query, and config counts are stored in the final JSONL.

### C02 Fixed backbone and generator

- **Section:** §§3, 7, 9.
- **Claim:** BGE-M3 + BM25 + weighted RRF + CrossEncoder and Mi:dm 2.0 Base are fixed outside the three axes.
- **Evidence:** final JSONL metadata; `fixed_backbone.yaml`; `frozen_params.yaml`.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** this is protocol provenance, not a new performance claim.

### C03 HyDE controlled result

- **Section:** Abstract; §11.1; §§13, 15.
- **Claim:** With CAD/SCD off, HyDE answer relevancy changes by +0.0303 [+0.0016, +0.0615]; other reported quality intervals include or touch zero.
- **Evidence:** final 152-row score artifact; `reference_scd_gpt4o_official` analysis; thesis verification script.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** the contrast is calculated from stored scores; it is not a universal retrieval-improvement claim.

### C04 HyDE changes retrieval inputs

- **Section:** §§8.1, 13.
- **Claim:** HyDE is an end-to-end retrieval-side intervention, so its quality contrast includes retrieval changes.
- **Evidence:** final JSONL fields `hyde_document`, `retrieved_chunk_ids`, and `reranked_chunk_ids`.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** `E04` displays the stored paired IDs and original hypothetical document.

### C05 CAD restricted result

- **Section:** Abstract; §11.1; §§13, 15.
- **Claim:** In the HyDE-off/SCD-off byte-identical-context comparison, CAD faithfulness is +0.0023 [−0.0903, +0.0952]; no quality improvement is established.
- **Evidence:** final generation JSONL; final score artifact; thesis verification script.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** all 19 paired contexts, retrieved IDs, and reranked IDs can be compared without a model; `E05` shows one pair.

### C06 CAD scope limit

- **Section:** §14.
- **Claim:** HyDE-on CAD comparisons are not used for the CAD quality conclusion because independently regenerated HyDE documents did not guarantee identical contexts.
- **Evidence:** final generation JSONL; §14 text.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** the stored contexts are sufficient to check the restriction.

### C07 Reference-SCD protocol

- **Section:** §§3.5, 8.3, 9.
- **Claim:** The final SCD setting is `reference_scd`, alpha 1.1, beta 0.9, Tstart 5, with raw-logit target/distractor scaling and no general-English whitelist.
- **Evidence:** SCD-on final JSONL metadata; `backend/modules/scd_decoder.py`; final protocol reports.
- **Reproducible from retained data:** YES for provenance; PARTIAL for runtime behaviour. **Model execution required:** NO/YES respectively.
- **Reason:** stored metadata proves the executed protocol; a new decoder execution would be needed to re-observe token behaviour.

### C08 Direct SCD language effect

- **Section:** Abstract; §11.2; §§13, 15.
- **Claim:** Across 76 matched pairs, Korean-character ratio changes by +0.2203; 68 improve, 3 decline, and 5 tie.
- **Evidence:** final generation JSONL; `reference_scd_language_adherence.json`.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** the ratio is a deterministic text measurement; `E03` shows a selected threshold-rescue pair.

### C09 Drift-threshold result

- **Section:** §11.2.
- **Claim:** 26 SCD-off pairs are below 0.5; 15 cross the threshold with SCD on, and one crosses in the opposite direction.
- **Evidence:** `reference_scd_language_adherence.json` and final generation JSONL.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** threshold membership is calculated from unchanged generated strings.

### C10 SCD matched-context check

- **Section:** Abstract; §11.2.
- **Claim:** The HyDE-off identical-context subset retains a +0.2198 mean Korean-ratio delta over 38 pairs.
- **Evidence:** final JSONL; language-adherence analysis.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** paired context equality and ratios are stored.

### C11 Quality versus language separation

- **Section:** §§10, 11.4, 13.
- **Claim:** Korean-character ratio measures language adherence only; it does not establish faithfulness or answer quality.
- **Evidence:** analyzer implementation; language analysis conclusion; symmetric reports.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** this is a measurement-boundary claim.

### C12 Symmetric evaluation design

- **Section:** §§9, 10, 11.3.
- **Claim:** The quality sensitivity analysis uses 38 HyDE-off SCD pairs with byte-identical contexts, English/Korean normalized panels, two metrics, and query-clustered bootstrap intervals.
- **Evidence:** input audit; EN/KO score artifacts; symmetric analysis JSONs.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** inputs, hashes, score records, and analysis outputs are retained.

### C13 Cross-judge conclusion

- **Section:** §§11.3, 14, 15.
- **Claim:** `gpt-4o`'s nonzero answer-relevancy intervals do not replicate with fixed `gpt-4.1-2025-04-14`; no judge-robust nonzero RAG-quality effect is established.
- **Evidence:** two symmetric analysis JSONs; `reference_scd_symmetric_cross_judge_report.md`.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** the conclusion compares already stored score analyses; `E08` replays the report.

### C14 Translation-confound limit

- **Section:** §14.
- **Claim:** Symmetric normalization is post-generation; source-language translation exposure differs by SCD condition and both judges share a provider.
- **Evidence:** `reference_scd_symmetric_input_audit.md`; cross-judge report.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** the audit stores counts, protocol, and limitations; `E07` replays it without translating text again.

### C15 Unsupported-generation review boundary

- **Section:** §§10, 14.
- **Claim:** A low automated faithfulness score alone is not a qualitative hallucination finding.
- **Evidence:** final score artifact and original question/context/answer strings.
- **Reproducible from retained data:** PARTIAL. **Model execution required:** NO.
- **Reason:** locating the low-score row is deterministic; deciding whether it asserts an unsupported fact requires human reading. `E06` supplies the unmodified evidence.

### C16 Research/service separation

- **Section:** §§6, 12, 15.
- **Claim:** The thesis experiment layer and A–F service integration share modules one-way but are distinct responsibilities.
- **Evidence:** `docs/REPO_LAYOUT.md`; import graph; backend/frontend source.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** source inspection establishes the boundary; it does not validate live service performance.

### C17 A–F implementation claim

- **Section:** §12.
- **Claim:** A–F routes expose implemented paper-review functions and method-selection points, not validated per-route optima.
- **Evidence:** `backend/api/`, `backend/pipelines/`, `frontend/src/`; §12 table.
- **Reproducible from retained data:** PARTIAL. **Model execution required:** NO for source evidence; YES for a live end-to-end run.
- **Reason:** code proves implementation structure, not production usability or user outcomes.

### C18 External-validity and evaluation limits

- **Section:** §14.
- **Claim:** Four papers, 19 query clusters, judge dependence, no blinded human review, decoder cost, and tokenizer-specific SCD behaviour limit generalization.
- **Evidence:** final artifact counts; symmetric reports; implementation source.
- **Reproducible from retained data:** YES. **Model execution required:** NO.
- **Reason:** these are scope limits supported by the retained protocol and records.

## Suggested capture order

1. `list`, then `show E01` for an ordinary stored QA row.
2. `show E02` and `show E03` to show an actual drift/rescue contrast.
3. `show E04` and `show E05` for retrieval change versus identical-context CAD control.
4. `show E06` only with a human annotation that it is a review candidate.
5. `show E07` and `show E08` for the translation and cross-judge limitations.

No listed claim requires a new model run for evidence already present in the
repository. A live execution would be a separate future task only for claims
about fresh data, production behaviour, or new qualitative evaluation.
