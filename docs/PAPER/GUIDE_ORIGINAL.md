# Phase 5 Guide: HyDE/CAD/SCD Thesis Direction

> **Historical Phase 5 guide.** Retained for design provenance. Current methods,
> completed results, limitations, and references live in `THESIS.md` and the latest
> `experiments/reports/` artifacts.

This guide supersedes the older broad modular-method guide. It keeps the project useful as a graduation-project paper-review service, while narrowing the thesis claim to the approved research contribution.

## Core Direction

The thesis studies:

```text
HyDE × CAD × SCD factor analysis in Korean-query / English-paper RAG
```

The routed M-RAG application is a service architecture. A-F routes are product features for paper review, not new thesis algorithms.

## What Must Stay Fixed

After tuning on `tuning_queries`, freeze:

- `top_k`
- `rerank_top_n`
- `cad_alpha`
- `scd_beta`
- HyDE prompt/template
- generation settings

Do not tune these on `decoder_main_queries`, `query_type_analysis_queries`, or `candidate_final_eval_queries`.

## Main Matrix

The main experiment must contain exactly these eight configs:

| Config | HyDE | CAD | SCD |
|---|---:|---:|---:|
| `hyde_off__no_decoder_control` | off | off | off |
| `hyde_off__cad_only` | off | on | off |
| `hyde_off__scd_only` | off | off | on |
| `hyde_off__cad_scd` | off | on | on |
| `hyde_on__no_decoder_control` | on | off | off |
| `hyde_on__cad_only` | on | on | off |
| `hyde_on__scd_only` | on | off | on |
| `hyde_on__cad_scd` | on | on | on |

Only HyDE, CAD, and SCD may vary in the main matrix.

## Method Contracts

CAD must use the exact formula:

```text
cad_scores = (1 + alpha) * context_scores - alpha * no_context_scores
```

The no-context branch must use the same generated prefix as the context branch. The current correctness-first design uses an uncached reference path.

SCD means Korean-target Soft Constrained Decoding. It must include a neutral token policy and a technical term whitelist. Do not use the old selective expansion in core code or docs.

HyDE remains HyDE. Do not turn it into multi-query fusion and do not demote it to appendix-only.

Evaluation must separate:

- A future RAGAS-compatible skeleton for schema/import readiness.
- A lightweight local judge named `RAGASInspiredEvaluator` or `LightweightJudgeEvaluator`.

Do not claim RAGAS execution unless it is actually run in an approved later phase.

## Service Layer

The graduation-project system keeps these A-F routes:

| Route | Service feature |
|---|---|
| A | simple paper QA |
| B | section-focused QA |
| C | document comparison |
| D | citation / patent-oriented lookup |
| E | structured summary |
| F | quiz / flashcard generation |

The route policy should be derived from the HyDE/CAD/SCD experiment by query type. It should not be presented as the core thesis method.

## Query Policy

Use existing query assets only after audit. Do not fabricate queries and do not duplicate queries to satisfy counts.

Split intent:

- `tuning_queries`: choose frozen parameters.
- `decoder_main_queries`: run the 8-config main matrix.
- `query_type_analysis_queries`: analyze query-type effects.
- `candidate_final_eval_queries`: reserve for final evaluation after validation.
- `service_route_queries`: qualitative service examples only.
- `query_templates`: templates that still require answerability validation.

## Required Table Order

Main tables:

1. Table 1. Experimental Setup
2. Table 2. Main HyDE × CAD × SCD Factorial Ablation
3. Table 3. Effect Delta Summary
4. Table 4. Query-Type Breakdown
5. Table 5. Numeric Hallucination and Evidence Support
6. Table 6. Language Drift and Korean Answer Ratio
7. Table 7. Routed Policy for Graduation-Project System

Appendix:

1. Appendix A1. CAD alpha / SCD beta sensitivity
2. Appendix A2. Reference implementation audit
3. Appendix A3. Query audit and split statistics
4. Appendix A4. Cost / run-size estimation
5. Appendix A5. Service route qualitative examples
6. Appendix A6. Frontend-backend runtime compatibility audit

## Safety Rules

- Do not run real experiments from this guide.
- Do not call models, OpenAI, RAGAS execution, or GT generation.
- Do not invent result values.
- Do not expose experiment matrix controls in the frontend.
- Do not modify CAD/SCD logic while doing documentation sync.

## Current Validation Commands

Safe Phase 5 validation:

```powershell
python -m compileall backend experiments
python experiments/runners/dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
python experiments/runners/dry_run_matrix.py --experiment all --estimate-cost --dry-run
```

Frontend validation may use `npm run typecheck` or `npm run build` only if scripts and installed dependencies already exist.
