# M-RAG: HyDE, CAD, SCD Factor Analysis for Korean-Query English-Paper RAG

## Abstract

This thesis studies Korean-query question answering over English academic papers. The main research contribution is a controlled HyDE × CAD × SCD factor analysis on top of a fixed Paper-RAG backbone. The experiment asks how retrieval-side hypothetical-document expansion, context-aware decoding, and Korean-target language control affect evidence support, numeric hallucination, and language drift when the user asks in Korean but the evidence is primarily written in English.

M-RAG also includes a Modular/Routed RAG service with A-F routes for paper review tasks such as simple QA, section-focused QA, comparison, citation lookup, summary, and quiz generation. In this thesis direction, that routed layer is treated as graduation-project system integration and service architecture. It is not claimed as a new core RAG algorithm. The route policy is derived after interpreting the HyDE/CAD/SCD analysis by query type.

No experiment results are claimed in this draft. Tables below define the required result structure and must be filled only after the approved experiment run produces verified artifacts.

## 1. Introduction

Korean users often ask questions about English academic papers. This setting creates two coupled problems. First, retrieval must bridge the form gap between a Korean question and English paper passages. Second, generation must answer in Korean while staying faithful to English evidence. A model may copy English fragments into the answer, or it may rely on parametric memory instead of the retrieved paper.

This work isolates three controllable factors:

- HyDE: retrieval-side hypothetical document expansion.
- CAD: Context-Aware Decoding using the exact contrast between context and no-context distributions.
- SCD: Korean-target Soft Constrained Decoding for reducing language drift while preserving technical terms.

The fixed backbone holds dense retrieval, sparse retrieval, rank fusion, reranking, and generation settings constant after tuning. The main matrix varies only HyDE on/off, CAD on/off, and SCD on/off.

## 2. Thesis Claim Boundary

The thesis contribution is not a novel Modular/Routed RAG algorithm. Modular/Routed RAG is the graduation-project service layer that packages the research into an interactive paper-review application. A-F routes are service features that make the system useful to users, not separate thesis methods.

The research claim is:

본 연구는 두 단계로 구성된다. 첫째, 고정된 논문 RAG 검색 backbone 위에서 HyDE, CAD, SCD의 3개 factor를 조합하여 답변의 근거 충실성, 수치 환각, 언어 이탈에 미치는 영향을 실험적으로 분석한다. 둘째, 이 결과를 query type별로 해석하여 졸업작품 시스템인 Modular/Routed RAG 논문 리뷰 챗봇에 적용 가능한 query-type-aware policy를 설계한다. 따라서 본 연구의 핵심 기여는 새로운 Modular RAG 구조 자체가 아니라, HyDE/CAD/SCD 조합의 효과 분석과 그 결과를 시스템 policy로 연결하는 데 있다.

## 3. Method

### 3.1 Fixed Paper-RAG Backbone

The backbone includes multilingual dense retrieval, BM25 sparse retrieval, reciprocal rank fusion, reranking, and a fixed generation configuration. The freeze rule is applied after tuning on `tuning_queries`.

Frozen parameters:

- `top_k`
- `rerank_top_n`
- `cad_alpha`
- `scd_beta`
- HyDE prompt/template
- generation settings

The main experiment does not tune on `decoder_main_queries`, `query_type_analysis_queries`, or `candidate_final_eval_queries`.

### 3.2 HyDE Axis

HyDE is retained as the retrieval-side axis. It should not be reframed as multi-query fusion. HyDE on/off changes only whether the query is expanded through a hypothetical answer representation before retrieval.

### 3.3 CAD Axis

CAD is defined by the exact Context-Aware Decoding contract:

```text
cad_scores = (1 + alpha) * context_scores - alpha * no_context_scores
```

The no-context reference must use the same generated prefix `y_<t>` as the context branch. Unsupported batch or beam modes must be blocked unless prefix and cache parity are proven.

### 3.4 SCD Axis

SCD is Korean-target Soft Constrained Decoding. It penalizes non-target-language tokens to reduce language drift, while allowing a neutral token policy and a mandatory whitelist for technical terms such as model names, datasets, equations, acronyms, and cited method names.

The thesis must not expand SCD as an unsupported selective decoding claim in core method text.

## 4. Experiment Design

The main matrix is exactly:

```text
HyDE × CAD × SCD = 8 configs
```

Required config names:

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

The experiment framework lives under `experiments/` and is intentionally separated from the FastAPI runtime and frontend UI. Dry-run validation may inspect configs, schemas, query splits, and cost estimates, but it must not call models, OpenAI, RAGAS execution, or GT generation.

## 5. Query Split Policy

Existing query assets are audited before use. Queries must not be fabricated or duplicated to satisfy counts. Service-route examples are not promoted into the main experiment unless they are answerability-validated and assigned through the approved split process.

Split roles:

- `tuning_queries`: parameter selection only.
- `decoder_main_queries`: main HyDE/CAD/SCD matrix.
- `query_type_analysis_queries`: query-type breakdown after main analysis.
- `candidate_final_eval_queries`: reserved candidates for later final evaluation.
- `service_route_queries`: qualitative service-route examples only.
- `query_templates`: templates requiring validation before quantitative use.

## 6. Evaluation Design

Evaluation design separates a future RAGAS-compatible skeleton from lightweight local judging. The current Phase 5 document does not claim RAGAS execution or OpenAI-based results. Lightweight/local metrics may be described as RAGAS-inspired only.

Primary measurement categories:

- Evidence support and faithfulness.
- Numeric hallucination.
- Language drift and Korean answer ratio.
- Query-type breakdown.
- Cost and run-size estimation.

## 7. Required Main Tables

### Table 1. Experimental Setup

| Item | Value |
|---|---|
| Task | Korean-query / English-paper RAG |
| Backbone | Fixed Paper-RAG retrieval and reranking |
| Main factors | HyDE, CAD, SCD |
| Tuned only on | `tuning_queries` |
| Main queries | `decoder_main_queries` |
| Result status | pending verified run |

### Table 2. Main HyDE × CAD × SCD Factorial Ablation

| Config | Evidence support | Numeric hallucination | Language drift | Korean answer ratio | Notes |
|---|---|---|---|---|---|
| `hyde_off__no_decoder_control` | pending | pending | pending | pending | baseline |
| `hyde_off__cad_only` | pending | pending | pending | pending | CAD axis |
| `hyde_off__scd_only` | pending | pending | pending | pending | SCD axis |
| `hyde_off__cad_scd` | pending | pending | pending | pending | decoder interaction |
| `hyde_on__no_decoder_control` | pending | pending | pending | pending | HyDE axis |
| `hyde_on__cad_only` | pending | pending | pending | pending | HyDE + CAD |
| `hyde_on__scd_only` | pending | pending | pending | pending | HyDE + SCD |
| `hyde_on__cad_scd` | pending | pending | pending | pending | full factor combination |

### Table 3. Effect Delta Summary

| Effect | Delta definition | Result |
|---|---|---|
| HyDE main effect | HyDE on mean - HyDE off mean | pending |
| CAD main effect | CAD on mean - CAD off mean | pending |
| SCD main effect | SCD on mean - SCD off mean | pending |
| CAD x SCD interaction | combined effect beyond additive expectation | pending |
| HyDE x decoder interaction | retrieval expansion effect under decoder controls | pending |

### Table 4. Query-Type Breakdown

| Query type | HyDE effect | CAD effect | SCD effect | Policy implication |
|---|---|---|---|---|
| factual | pending | pending | pending | pending |
| numeric | pending | pending | pending | pending |
| method | pending | pending | pending | pending |
| comparison | pending | pending | pending | pending |
| summary | pending | pending | pending | pending |

### Table 5. Numeric Hallucination and Evidence Support

| Config | Numeric exactness | Unsupported numeric claims | Evidence support |
|---|---|---|---|
| 8-config matrix rows | pending | pending | pending |

### Table 6. Language Drift and Korean Answer Ratio

| Config | Language drift rate | Korean answer ratio | Whitelist errors |
|---|---|---|---|
| 8-config matrix rows | pending | pending | pending |

### Table 7. Routed Policy for Graduation-Project System

| Service route | Derived policy from HyDE/CAD/SCD analysis | Status |
|---|---|---|
| A simple QA | pending analysis | service feature |
| B section QA | pending analysis | service feature |
| C comparison | pending analysis | service feature |
| D citation/patent | pending analysis | service feature |
| E summary | pending analysis | service feature |
| F quiz/flashcard | pending analysis | service feature |

## 8. Required Appendices

### Appendix A1. CAD alpha / SCD beta sensitivity

Use only tuning-query experiments. Freeze selected values before the main matrix.

### Appendix A2. Reference implementation audit

Summarize CAD exactness, no-context parity, SCD whitelist policy, and RAGAS separation.

### Appendix A3. Query audit and split statistics

Report audited counts and leakage checks. Do not duplicate or fabricate queries.

### Appendix A4. Cost / run-size estimation

Use dry-run estimates from `experiments/runners/dry_run_matrix.py`.

### Appendix A5. Service route qualitative examples

Use only qualitative examples for A-F routes unless validated for quantitative evaluation.

### Appendix A6. Frontend-backend runtime compatibility audit

Document QueryRequest, QueryResponse, SSE, paper APIs, citation APIs, and `activePaperId -> doc_id_filter` compatibility.

## 9. Reference Classification

### Core implementation references

- Lewis et al., Retrieval-Augmented Generation.
- RAG survey / best-practice references used for backbone framing.
- BGE-M3 for multilingual dense retrieval.
- BM25 for sparse retrieval.
- Reciprocal Rank Fusion for rank fusion.
- Passage re-ranking with BERT / cross-encoder reranking.
- MS MARCO if used for reranker background.
- HyDE for hypothetical-document retrieval expansion.
- Context-Aware Decoding.
- Soft Constrained Decoding for language-drift control.

### Evaluation references

- RAGAS as evaluation-design background only.
- Lightweight judge design must be named as RAGAS-inspired when it is not the RAGAS package.
- Numeric hallucination and language-drift metrics as local evaluator designs until verified experiments exist.

### Background references

- Korean or multilingual RAG and language-drift references.
- Lost in the Middle, if used to motivate context-order sensitivity.

### Related or future-work references

Unsupported retrieval, graph, agentic, compression, or multimodal RAG variants may be discussed only as related work or future work. They are not part of the core thesis method unless a later implementation audit proves otherwise.

## 10. Conclusion

This thesis direction centers on the HyDE × CAD × SCD factor analysis for Korean-query English-paper RAG. The graduation-project service demonstrates how the resulting policy can be integrated into a useful paper-review assistant, but the service router is not the thesis algorithmic novelty. Results remain pending until the approved experiment run is executed and verified.
