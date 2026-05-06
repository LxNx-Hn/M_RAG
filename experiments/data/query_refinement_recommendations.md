# Phase 6 Query Refinement Recommendations

This review uses only existing query assets. It does not fabricate, duplicate, or edit source queries.

## Snapshot

- `query_audit.json`: 117 total queries.
- `tuning_queries.json`: 8 queries.
- `decoder_main_queries.json`: 31 queries.
- `query_type_analysis_queries.json`: 14 queries.
- `candidate_final_eval_queries.json`: 8 queries.
- `service_route_queries.json`: 0 queries.
- `query_templates.json`: 56 template records.
- Duplicate `query_id`: none found.
- Overlap by `query_id` or exact query text between tuning, decoder main, and final candidate: none found.
- Duplicate query text: 28 duplicate template pairs in `query_templates.json`.

## Queries Safe To Keep

Safe means the current record is answerable, has an `answer_span`, has no split overlap, and does not obviously evaluate service-route behavior.

| Split | Query IDs |
|---|---|
| tuning | `track1_0001`, `track1_0004`, `track1_0005`, `track1_0007`, `track1_0008` |
| decoder_main | `track1_0009`, `track1_0010`, `track1_0012`, `track1_0015`, `track1_0016`, `track1_0019`, `track1_0021`, `track1_0023`, `track1_0024`, `track1_0025`, `track1_0026`, `track1_0027`, `track1_0032`, `track1_0033`, `track1_0034`, `track1_0035`, `track1_0036`, `track1_0037`, `track1_0040` |
| query_type_analysis | `track1_0041`, `track1_0044`, `track1_0045`, `track1_0048`, `track1_0049`, `track1_0050`, `track1_0054` |
| final_eval_candidate | `track1_0055`, `track1_0056`, `track1_0058`, `track1_0059`, `track1_0061` |

Notes:

- `track1_0020`, `track1_0028`, and `track1_0051` are answerable with spans, but their wording is broad enough to benefit from human rewrite before use in a main metric table.
- Citation queries are answerable in several cases, but they primarily exercise Route D behavior and should be separated from the main HyDE/CAD/SCD decoder matrix unless the experiment explicitly includes citation-style evidence QA.

## Queries To Move To Tuning

Do not move anything automatically in Phase 6. If the tuning split must avoid citation-route behavior and `gt_status: not_found`, use the following as replacement candidates after human review:

| Candidate | Current split | Reason |
|---|---|---|
| `track1_0041` | query_type_analysis | answerable simple QA, valid GT, useful Korean RAG-evaluation domain coverage |
| `track1_0045` | query_type_analysis | answerable numeric/factual hallucination query, valid GT |
| `track1_0048` | query_type_analysis | answerable HyDE-domain simple QA, valid GT |
| `track1_0049` | query_type_analysis | answerable HyDE-domain method query, valid GT |
| `track1_0050` | query_type_analysis | answerable HyDE-domain result query, valid GT |
| `track1_0054` | query_type_analysis | answerable decoder-ablation style query, valid GT |

Current tuning records needing review before tuning:

| Query ID | Risk | Recommendation |
|---|---|---|
| `track1_0002` | `gt_status: not_found` despite answer span | validate GT status or replace |
| `track1_0003` | `gt_status: not_found` despite answer span | validate GT status or replace |
| `track1_0006` | citation-route behavior | move to service_route or query_type_analysis if route-specific examples are needed |

## Queries To Move To Decoder Main

Do not move final-eval candidates into decoder main unless final holdout is rebuilt. Decoder main should use answerable, span-backed, non-template queries that directly test retrieval evidence and decoding controls.

Recommended decoder-main policy:

- Keep non-citation records with valid GT and answer spans.
- Remove or replace records with `gt_status: not_found` before real main execution.
- Keep crosslingual examples, but acknowledge the source pool has only five `crosslingual_ko` queries.
- Do not promote `query_templates` into decoder main until each template is bound to a specific paper and answer span.

Decoder-main records needing review:

| Query IDs | Reason |
|---|---|
| `track1_0011`, `track1_0013`, `track1_0017`, `track1_0018`, `track1_0029`, `track1_0031` | `gt_status: not_found` despite answer span; validate GT before use |
| `track1_0014`, `track1_0022`, `track1_0030`, `track1_0038` | citation-route behavior and `gt_status: not_found`; move out of main decoder matrix unless citation QA is explicitly included |

## Queries To Move To Query Type Analysis

Use query_type_analysis for route-sensitive or broad query-type exploration, not for parameter tuning or final claims.

| Query IDs | Reason |
|---|---|
| `track1_0006`, `track1_0014`, `track1_0022`, `track1_0030`, `track1_0038`, `track1_0046`, `track1_0053`, `track1_0060` | citation-style records are better for route D analysis than the core decoder matrix |
| `track1_0020`, `track1_0028`, `track1_0051`, `track1_0058` | broad "core claim/problem/contribution" wording can help qualitative query-type analysis after rewrite |

## Queries To Move To Final Eval Candidate

Final eval should be the cleanest held-out split. Keep only records with validated GT, answer spans, no service-route behavior, and no ambiguous paper target.

Current final candidates to keep after review:

- `track1_0055`
- `track1_0056`
- `track1_0058`
- `track1_0059`
- `track1_0061`

Current final candidates needing action:

| Query ID | Risk | Recommendation |
|---|---|---|
| `track1_0039` | `gt_status: not_found` | validate GT or replace before final eval |
| `track1_0057` | `gt_status: not_found`; broad "proposed method vs CAD" wording | validate GT and rewrite to name the method, dataset, and compared baseline |
| `track1_0060` | citation-route behavior and `gt_status: not_found` | move to service_route/query_type_analysis or replace with a non-citation final query |

Candidate replacements, if held-out integrity can be preserved:

- Use valid, answerable records currently in `query_type_analysis` only if they are removed from query-type analysis and not used elsewhere.
- Do not pull from `tuning_queries` or `decoder_main_queries`.

## Queries To Move To Service Route

The current `service_route_queries.json` is empty. Existing citation-style records are the safest source-backed service-route candidates, but they should not be silently moved during Phase 6.

| Route | Candidate IDs |
|---|---|
| D citation / reference lookup | `track1_0006`, `track1_0014`, `track1_0022`, `track1_0030`, `track1_0038`, `track1_0046`, `track1_0053`, `track1_0060` |
| B section-focused QA examples | selected Track 2 templates only after binding each template to a specific paper and answer span |
| E/F summary or study support | no safe existing quantitative examples found; do not fabricate |

## Queries To Mark Template Only

All `track2_0001` through `track2_0056` should remain `template_only`.

Reasons:

- All 56 records have missing `answer_span`.
- 52 are marked `not_answerable`.
- All 56 have multi-paper applicability and therefore require active-paper binding.
- 28 exact duplicate query-text pairs exist: `track2_0001/0029`, `0002/0030`, ..., `0028/0056`.

These templates can seed later service-route qualitative examples only after human rewrite and GT/answer-span binding.

## Queries To Exclude

Exclude from tuning, decoder main, and final eval until fixed:

| Query IDs | Reason |
|---|---|
| all `track2_0001` through `track2_0056` | template-only, missing answer spans, duplicate template pairs, multi-paper target ambiguity |
| `track1_0014`, `track1_0022`, `track1_0030`, `track1_0038`, `track1_0060` | citation-route behavior plus `gt_status: not_found` |
| `track1_0039`, `track1_0057` | final-candidate GT risk; validate or replace before final eval |

## Queries Needing Human Rewrite

Proposed rewrites are suggestions only. Source query files were not modified.

| Query ID | Current issue | Proposed rewrite direction |
|---|---|---|
| `track1_0020` | broad "핵심 주장" wording | Ask for the specific CAD claim about mitigating hallucination or overriding prior knowledge using the paper's terminology. |
| `track1_0028` | broad "새로운 접근 방식" wording | Ask specifically how RAPTOR constructs a tree from chunk embeddings and summaries. |
| `track1_0051` | broad "주요 문제" wording | Name the HyDE multi-hop framework and ask which retrieval problem it targets. |
| `track1_0057` | vague "제안된 방법" and comparison target | Name Contrastive CAD, the compared baseline, and the dataset or metric expected in the answer. |
| `track1_0058` | broad "주요 기여" wording | Ask for the paper's enumerated contributions or the specific SCD/CAD-related contribution. |
| `track2_0001` to `track2_0056` | template-only and multi-paper ambiguity | Bind each template to one paper ID, one section, one answer span, and one expected GT answer before use. |

## Query Types Needing More Data

| Query type | Current source count | Risk |
|---|---:|---|
| `crosslingual_ko` | 5 | too sparse for stable query-type conclusions |
| `simple_qa` | 8 | small relative to 22-count categories |
| `section_result` | 8 | small and includes GT-status risks |
| `numeric_or_factual_hallucination` | 8 | central metric category but small |
| comparison | 0 | Route C service examples cannot be quantitatively analyzed from current splits |
| summary / quiz / study support | 0 | Route E/F service examples cannot be quantitatively analyzed from current splits |

## Answerability Risks

- Template records are not answerable until bound to paper-specific evidence.
- Citation queries may be answerable, but they evaluate citation lookup behavior more than HyDE/CAD/SCD factor effects.
- Broad "core claim", "major contribution", or "proposed method" queries can be answerable but may create evaluator ambiguity.
- Some `gt_status: not_found` records still have answer spans, which indicates metadata inconsistency rather than necessarily unanswerable content.

## GT Validation Risks

- `query_audit.json` reports 73 records with `gt_status: not_found`.
- Non-template splits include 21 `gt_status: not_found` records despite answer spans.
- `candidate_final_eval_queries.json` includes 3 `gt_status: not_found` records.
- `tuning_queries.json` includes 2 `gt_status: not_found` records.
- Do not run tuning or final evaluation until GT status is reconciled with answer spans and expected answers.

## Recommended Next Action

Before tuning, perform a query/GT cleanup pass that:

1. Reconciles `gt_status` with `answer_span` for tuning and decoder-main records.
2. Moves citation-route records out of the main decoder matrix or explicitly documents citation QA as an included query type.
3. Keeps all Track 2 templates as `template_only`.
4. Rebuilds candidate final eval from validated, held-out, non-service-route queries.
5. Adds more source-backed `crosslingual_ko`, numeric, comparison, summary, and service-route examples only if they can be sourced without fabrication.
