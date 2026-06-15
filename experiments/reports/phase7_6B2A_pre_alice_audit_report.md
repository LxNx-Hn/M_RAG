# Phase 7.6B-2A Pre-Alice Static Audit Report

- Scope: code / thesis / reference corrections and static verification only.
- No model execution, no GPU, no embedding, no CrossEncoder, no generation, no
  retrieval smoke, no Alice access was performed in this phase.
- Date basis: 2026-06.

## 1. Single Core Claim of the Thesis

The thesis is restricted to exactly one independent claim, now labelled
explicitly in `docs/PAPER/THESIS.md` §2:

> 고정된 Paper-RAG 검색 backbone 위에서 HyDE × CAD × SCD 완전요인실험을 수행하고,
> 각 요소의 효과와 상호작용을 query type별로 분석하여 한국어 질의-영어 논문 RAG의
> 구성 정책을 도출한다.

A new sentence was added immediately before it stating that every other sentence
in the document must be one of: cited prior work, a repository-verifiable
implementation fact, a pre-experiment hypothesis, an experiment/analysis plan, or
a verified result — and that no other sentence is an independent novel claim.

## 2. Unsupported / Result-Like Statements Removed or Scoped

No fabricated independent claims were found remaining (the prior commit `8505abe`
had already removed fabricated references). The following result-like phrasings
were converted to explicit hypotheses, not deleted:

- §4.6: "CAD is a decoding-time context-faithfulness factor for reducing ... and
  improving evidence support" → reframed as a hypothesized purpose tied to H2.
- §8.2: "CAD should reduce unsupported claims and numeric hallucination" →
  "CAD is hypothesized to reduce ... (hypotheses for H2, not results)".
- §8.3: "SCD should reduce language drift ... and increase Korean answer ratio" →
  "SCD is hypothesized to reduce ... (hypotheses for H3, not results)".
- §8.1: HyDE "Expected analysis" re-labelled as "hypotheses for H1, not results".
- §4.7: removed the word "Oral" from the body description of the SCD paper (see §4).

Explicit hypotheses **H1–H4** were added in a new §5.1, each grounded in a prior
work citation (H1→[8],[3],[17]; H2→[9],[10]; H3→[11]; H4→[9],[11]). They state
that no result is asserted before a verified run.

## 3. New References Added

None. The existing 18-entry reference list already covers every external fact in
the body (RAG, dense retrieval, BM25, RRF, cross-encoder reranking, MS MARCO,
HyDE, CAD, contrastive decoding, SCD/language-drift, RAGAS, Lost-in-the-Middle,
BERGEN, Mi:dm, and three Korean papers). The audit therefore **connected existing
references to body sentences** via inline `[n]` markers rather than inventing new
sources. Inline citations were added throughout §3 (Background), §4 (Related
Work), §6, and §8 so that every external fact now carries a citation. All 18
references are now cited at least once, and every inline citation maps to an
existing reference (verified by an automated consistency test, see §9).

## 4. Corrected References (thesis)

- **[11] SCD paper — verified against primary sources and corrected.**
  - Verified via arXiv (`arxiv.org/abs/2511.09984`) and the official AAAI
    proceedings page (`ojs.aaai.org/index.php/AAAI/article/view/40417`).
  - Authors confirmed: Bo Li, Zhenghua Xu, Rui Xie (matches the thesis `B. Li,
    Z. Xu, and R. Xie`).
  - Citation updated to: *Proceedings of the AAAI Conference on Artificial
    Intelligence*, vol. 40, no. 37, pp. 31519–31526, 2026,
    doi:10.1609/aaai.v40i37.40417 (arXiv:2511.09984).
  - **"Oral" was removed.** AAAI publication (volume/issue/pages/DOI) is
    officially confirmed, but the official OJS AAAI article page does not itself
    label the paper "Oral". Per the audit rule (drop Oral if not officially
    confirmable), the Oral designation — which appeared only in the authors'
    arXiv comment and a search-engine summary — was removed from both the
    reference and the §4.7 body text.
- **[17] HyDE multi-hop (Korean) — verified via KCI and TODO removed.**
  - KCI artiId ART003208016. Authors confirmed: 김예은, 이재홍, 원상혁, 정우혁,
    우지환 (exact match). 경영정보학연구 27(2), 2025, pp. 127–148,
    doi:10.14329/isr.2025.27.2.127. Pages and DOI added; "TODO: verify" removed.

## 5. Bibliographic Details — now fully verified (follow-up)

All reference TODOs are resolved. `remaining_unverified_references: 0`.

- **[16] (김범석, 양진홍) — verified via KCI primary source and TODO removed.**
  - KCI artiId ART003200663 (confirmed against the KCI article page).
  - 김범석, 양진홍, "RAG 시스템 성능 평가를 위한 자동 데이터 셋 생성 프레임워크 비교
    분석 연구," 한국정보전자통신기술학회 논문지, vol. 18, no. 2, pp. 143–154, 2025
    (ISSN 2005-081X). Page range added; "TODO: verify" removed.
- **[18] (Contrastive CAD, HCLT 2024) — author list corrected from a primary
  source.** Using the 국립국어원 official HCLT 2024 schedule (corroborated by an
  independent search), the confirmed authors are 장규식, 나승훈, 김태형, 류휘정,
  장두성. The incorrect `이현민` was removed and `장두성` added. Only the
  conference-proceedings information is asserted; no page numbers or DOI were
  fabricated. "TODO" removed.

A static test (`test_thesis_has_no_unresolved_reference_todo`) now asserts the
reference list contains no remaining TODO marker.

## 6. Code Citation Fixes

Code comments were converted from stale bracket-number citations to author-year /
title form so that future reference renumbering cannot break them again:

- `backend/modules/embedder.py`: `기반 논문: BGE M3-Embedding [2]` →
  `BGE-M3 (Chen et al., 2024, arXiv:2402.03216)` (was pointing at the wrong
  number; BGE-M3 is `[3]` in the thesis).
- `backend/modules/reranker.py`:
  - Removed the `ColBERTv2 [14]` and `Jina-ColBERT-v2 [15]` citations (neither is
    in the thesis bibliography, and the module is a cross-encoder, not ColBERT).
  - Base citation is now Nogueira & Cho, "Passage Re-ranking with BERT", 2019
    (the actual basis; thesis `[6]`), with the configured model noted
    (`cross-encoder/ms-marco-MiniLM`).
  - The `[29]` citation (which does not exist; the list ends at 18) was removed.
  - The zig-zag context reordering is now explicitly described as **the
    repository's own heuristic, motivated by the Lost-in-the-Middle observation
    (Liu et al., TACL 2024), not a method proposed by that paper.**
- Repository-wide grep confirms no remaining `ColBERTv2`, `Jina-ColBERT`,
  `mFAVA`, `[29]`, `Oral Paper`, or the previously removed fabricated arXiv IDs
  (2501.09828 / 2408.12834 / 2501.00571 / 2501.15829) outside `.venv`.

## 7. Existing 5-Sample Evidence Re-Grade (metadata only)

The Phase 7.6B-1 result file
`experiments/results/tuning/phase7_6B_limited_tuning_current_defaults_5samples.jsonl`
was a `doc_id`-filtered vector-store sample, NOT query-aware retrieval. The same
three chunks (title / intro / contributions) were returned for all five queries
regardless of query text, which is why most answers were "정보를 찾을 수 없습니다".

**The five generated answers were NOT regenerated. Only the meaning/metadata was
corrected** in each record:

- `parameter_freeze_evidence`: `true` → `false`
- `evidence_class`: added `execution_smoke_only`
- `fixed_backbone_validation`: added `false`
- `thesis_grade_result`: `false` (unchanged)
- `retrieval_mode`: added `doc_filter_sample`; `context.source` kept as
  `vector_store_doc_filter_sample`
- `evidence_correction_note`: added, stating this is a metadata-only correction.

A correction banner was added to
`experiments/reports/phase7_6B_limited_tuning_current_defaults_report.md`, and its
"ready for 7.6C profile expansion" / "is parameter-freeze evidence" conclusions
were marked SUPERSEDED. The root-cause overclaim was also fixed in the runner:
`build_record` now sets `parameter_freeze_evidence: False` unconditionally, so a
re-run cannot re-introduce the wrong flag.

## 8. Retrieval Adapter Implementation Path

`experiments/runners/run_alice_tuning.py` now supports two retrieval modes via
`--retrieval-mode`:

- `doc_filter_sample` (default, backward compatible): metadata-only
  `collection.get(where={doc_id})` sample. `evidence_class = execution_smoke_only`.
- `fixed_backbone`: the real query-aware Paper-RAG backbone. The orchestration
  function `run_fixed_backbone_retrieval(...)` performs, using the **query text**
  and the applicable-paper `doc_id` filter, via the SINGLE public retrieval API
  `HybridRetriever.search_with_trace(...)` (the adapter no longer assembles
  retrieval from `bm25_map` / `_rrf_fusion` directly):
  1. BGE-M3 query embedding + Chroma dense retrieval + BM25 sparse retrieval +
     RRF fusion, all inside `search_with_trace` (same implementation as the
     production `search()`, which now returns `search_with_trace(...)["fused"]`),
  2. CrossEncoder reranking (`Reranker.rerank`),
  3. final `context_chunk_count` chunk selection.
  `evidence_class = retrieval_backbone_smoke`.

Heavy backend modules are imported lazily inside `build_fixed_backbone_components`,
so importing the runner (and running the unit tests) never loads torch / a model.
The orchestration takes injected components, which makes it unit-testable without
GPU.

Output metadata fields now emitted (per record): `retrieval_mode`,
`retrieval_backend`, `retrieval_pool_top_k`, `rerank_top_n`, `context_chunk_count`,
`dense_result_count`, `sparse_result_count`, `fused_result_count`,
`retrieved_chunk_ids`, `reranked_chunk_ids`, `retrieved_doc_ids`,
`bm25_index_available`, `context_available`, `fallback_used`,
`parameter_freeze_evidence`, `evidence_class`. For a Phase 7.6B-2A run these will
be `parameter_freeze_evidence: false`, `evidence_class: retrieval_backbone_smoke`,
`fallback_used: false`.

### Parameter semantics unified

Three distinct stages are now named consistently across the runner args,
`experiments/configs/fixed_backbone.yaml`, and
`experiments/configs/tuning_plan.yaml`:

- `retrieval_pool_top_k` = 20 — initial dense + BM25 candidate pool
  (backend `config.TOP_K_RETRIEVAL`).
- `rerank_top_n` = 5 — documents kept after CrossEncoder
  (backend `config.TOP_K_RERANK`; the API `QueryRequest.top_k=5` maps here).
- `context_chunk_count` = 5 — final chunks handed to the generator.

### BM25 doc_id pre-ranking filter fix (follow-up)

A correctness bug was fixed: previously BM25 selected a global top-k and then
applied `doc_id_filter` afterward, so a target document's chunks were silently
lost whenever higher-scoring chunks of other documents filled the global top-k.

- `BM25.search()` now accepts optional `doc_id_filter` / `section_filter` and
  restricts the candidate set BEFORE top-k selection (corpus-level IDF / avgdl
  are retained as scoring statistics).
- `HybridRetriever.search_with_trace()` is a new public method that runs the
  whole dense + sparse + RRF path once and returns `dense`/`sparse`/`fused`
  lists plus their counts and `bm25_available`. `HybridRetriever.search()` is now
  a thin wrapper returning `["fused"]`, so production and the experiment adapter
  share ONE retrieval implementation.
- The Alice adapter consumes `search_with_trace` only (no `bm25_map` /
  `_rrf_fusion` access); counts in the evidence metadata come from the trace.

## 9. BM25 Fail-Closed Behaviour

`fixed_backbone` does NOT silently fall back to dense-only. It raises before
generation:

- `fixed_backbone_bm25_index_missing` when no BM25 index exists for the collection.
- `retrieval_context_required_but_empty` when retrieval yields no usable context.
- `fixed_backbone_requires_query_text` when the query text is empty.

The general service path (`HybridRetriever.search`) **intentionally keeps**
dense-only fallback when BM25 is absent; this distinction is asserted by a
dedicated test (`test_service_search_keeps_dense_only_fallback_without_bm25`).

These are covered by unit tests, including a test proving that generation is NOT
invoked when retrieval fails (`generate_answer` call count is asserted to be 0)
and a test proving a target chunk outside the global BM25 top-k is recovered by
the pre-ranking `doc_id` filter.

## 10. Static Verification Results

All performed locally, no model/GPU:

- `compileall` (backend/modules, experiments/runners, tests/backend): PASS.
- `pytest tests/backend -q`: 28 passed (17 new adapter/retrieval/reference tests
  + existing).
- New tests: fixed-backbone happy-path metadata; adapter-uses-public-API-only;
  BM25-missing fail-closed; no dense-only fallback (experiment); trace-reports-no-
  bm25 fail-closed; empty-retrieval fail-closed; empty-query guard; BM25 doc_id
  pre-filter recovers target outside global top-k; BM25 filter does not mix other
  docs; `search` delegates to `search_with_trace` with accurate counts; service
  dense-only fallback retained; build_record does-not-generate-on-empty-retrieval;
  doc_filter_sample evidence grade; bad param-ordering rejection; [16]/[18]
  finalized; no unresolved reference TODO; THESIS citation/number consistency.
- `run_alice_tuning.py --help`: PASS (shows new retrieval-mode and param args).
- Dry-runs: `run_tuning_plan --dry-run --plan-only`, `dry_run_matrix --dry-run`,
  `run_generation --dry-run --plan-only`: PASS.
- YAML syntax (all 9 `experiments/configs/*.yaml`): PASS.
- JSON(L) syntax (patched 5-sample file + all query splits): PASS.
- Wrapper shell syntax (`bash -n`) for the new and existing Alice wrappers: PASS.
- Runner refusal guards (no exec mode / missing `--confirm-alice-base`) refuse
  cleanly with `REFUSED:` and exit 2 BEFORE any model load.
- Wrapper guards (missing CONFIRM env / `QUERY_LIMIT=2` / forbidden split) refuse
  with exit 2 before invoking Python.
- Backend `ruff check .` (repo-gated, run from `backend/`): All checks passed.
- Backend `black --check` on edited modules: clean. Runner formatted with black.

## 11. Confirmation: No Real Alice Execution

No Alice connection, GPU run, model load, real embedding, real CrossEncoder, real
generation, real retrieval smoke, 5-sample run, profile expansion, or main
experiment was performed in this phase. All retrieval-adapter behaviour was
exercised only through injected fakes in unit tests.

## 12. Remaining Conditions Before Alice Execution

Before the Phase 7.6B-2A 1-sample fixed-backbone smoke can run on Alice:

1. Alice runtime restored: venv + `backend/requirements.txt`, MIDM BASE +
   BGE-M3 + CrossEncoder caches, `chroma_db` with `local_gt__papers` populated.
2. `paper_nlp_bge` (and the tuning-query papers) indexed into `local_gt__papers`,
   **including a built BM25 index** — otherwise the run will (correctly) fail
   closed with `fixed_backbone_bm25_index_missing`.
3. Run via `experiments/scripts/alice/alice_fixed_backbone_smoke.sh` with
   `CONFIRM_ALICE_FIXED_BACKBONE_SMOKE=1` (exactly one sample, `track1_0001`).
4. Success criteria: `retrieval_mode=fixed_backbone`, `fallback_used=false`,
   `bm25_index_available=true`, `context_available=true`, `fused_result_count>0`,
   OpenAI/RAGAS/GT all false, `parameter_freeze_evidence=false`,
   `evidence_class=retrieval_backbone_smoke`.

Profile expansion, parameter freeze, and the main experiment remain blocked and
require separate explicit approval.

## 13. Final State

```text
ready_for_phase7_6B2A_alice_1sample_smoke
alice_execution_count: 0
remaining_unverified_references: 0
```
