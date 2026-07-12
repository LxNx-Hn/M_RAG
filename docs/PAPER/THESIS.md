# M-RAG: HyDE × CAD × SCD Factor Analysis for Korean-Query English-Paper RAG

## 1. Abstract

Retrieval-Augmented Generation (RAG) is widely used to answer questions over external documents, but academic-paper question answering has two additional difficulties when Korean users ask questions about English papers. First, retrieval must bridge the linguistic and stylistic gap between Korean questions and English academic prose. Second, generation must remain faithful to retrieved evidence while producing a stable Korean answer. Even when relevant passages are retrieved, a language model may introduce parametric-memory hallucinations, copy English expressions into a Korean answer, or fail to preserve numeric and technical evidence.

This thesis studies these problems through a controlled factor analysis of HyDE, Context-Aware Decoding (CAD), and Korean-target Soft Constrained Decoding (SCD). The main experiment uses a fixed Paper-RAG retrieval backbone and varies only three factors: HyDE on/off, CAD on/off, and SCD on/off. HyDE is treated as a retrieval-side evidence-construction factor, CAD as a decoding-time context-faithfulness factor, and SCD as a Korean-target language-drift-control factor. The current scored run measures faithfulness, answer relevancy, context precision, context recall, and direct Korean-language adherence; numeric hallucination and query-type-specific routing remain planned analyses rather than measured result claims.

The project also includes an M-RAG paper-review chatbot with A-F service routes for simple question answering, section-focused question answering, document comparison, citation-oriented lookup, structured summarization, and quiz or flashcard generation. This routed application is framed as graduation-project system integration, not as the core thesis algorithm. The thesis contribution is the HyDE × CAD × SCD factor analysis and a global factor-effect-based provisional service policy from that analysis; query-type-aware refinement remains future work. The main experiment (19 queries × 8 configs = 152 generations, Mi:dm 2.0 Base on A100 80GB) has been executed and scored with RAGAS under a fixed NVIDIA NIM judge; result tables in Section 12 report the measured values. The headline findings are that CAD improves faithfulness (paired +0.044), HyDE improves answer relevancy and recall while lowering context precision, and the original Korean-target SCD v1 (`penalty_additive`) is a null factor in Section 12. A separately reported corrected `reference_scd` implementation strongly improves direct Korean-language adherence. Its first complete `gpt-4o` score panel is an asymmetric protocol-specific sensitivity analysis. A stricter bilingual follow-up applies the same normalization policy to all HyDE-off conditions and compares 38 identical-context SCD pairs per language. Faithfulness remains directionally unresolved under both `gpt-4o` and fixed `gpt-4.1-2025-04-14`. The `gpt-4o` answer-relevancy intervals are negative, but the cross-judge intervals overlap zero in both languages, so no judge-robust nonzero RAG-quality effect is established; see Section 13.3 and `experiments/reports/reference_scd_symmetric_cross_judge_report.md`.

## 2. Introduction

Academic documents differ from ordinary web text in density, structure, and verification requirements. A paper contains abstract, introduction, method, experiment, result, limitation, and reference sections, and each section contributes a different kind of evidence. A question such as "이 논문의 F1 점수가 얼마야?" requires exact numeric evidence. A question such as "방법론을 설명해줘" requires method-section evidence. A comparison question requires balanced evidence from two documents. A citation question may require bibliographic parsing, while a study-support question may require structured output such as quiz items.

RAG addresses part of this problem by searching external documents and conditioning generation on retrieved context. However, a fixed RAG pipeline is not sufficient for Korean-query English-paper use. Korean questions and English evidence differ in language, morphology, and discourse style. Dense retrieval may capture semantic similarity but miss exact numbers or acronyms. Sparse retrieval may capture exact terms but miss paraphrased academic statements. Long contexts can dilute evidence, and the generator can still rely on prior parametric knowledge instead of the provided paper.

Generation introduces another layer of risk. When the context is in English and the user asks in Korean, the model may drift into English phrases or produce mixed-language answers. In a paper-review setting, this is not only a usability issue. Language drift can obscure whether an answer is faithful to the English evidence, and it can make Korean explanations less coherent for the target user. Numeric hallucination is similarly serious: if the paper reports a score, dataset size, or ablation value, the answer must not replace it with a plausible but unsupported number.

This thesis therefore narrows the research contribution to three controllable factors:

- HyDE: a retrieval-side method that reformulates the query into a hypothetical answer-like document before retrieval.
- CAD: a decoding method that contrasts context-conditioned scores with no-context scores using the exact formula required by the method contract.
- SCD: Korean-target Soft Constrained Decoding that discourages non-target-language tokens while preserving neutral tokens and technical terms.

The graduation-project system layer remains important, but it serves a different purpose. The M-RAG chatbot demonstrates how the research can be integrated into a usable service. Its A-F routes are paper-review features, not the thesis novelty. The current analysis supports only a global provisional service policy; query-type-specific routing requires a separate query-type analysis before it can be claimed as validated.

The final intended contribution is the single core claim of this thesis. Every other statement in this document is one of: prior work supported by a citation, an implementation fact verifiable in the repository, a pre-experiment hypothesis, an experiment/analysis plan, or a verified result. No other sentence should be read as an independent novel claim.

> **Core claim (본 논문의 유일한 독자 주장):** 고정된 Paper-RAG 검색 backbone 위에서 HyDE × CAD × SCD 완전요인실험을 수행하고, 각 요소의 효과와 상호작용을 분석하여 한국어 질의-영어 논문 RAG의 전역 구성 정책을 임시적으로 도출한다. Query-type-specific policy is reserved for future analysis.

본 연구는 고정된 Paper-RAG 검색 backbone 위에서 HyDE, CAD, SCD의 3개 factor를 조합하여 한국어 질의-영어 논문 RAG 환경의 근거 충실성, 언어 이탈, 한국어 응답 안정성, 응답 관련성, 검색 품질에 미치는 영향을 분석한다. 수치 환각과 query type별 routed policy는 현재 실행에서 측정된 결과가 아니라 후속 분석 대상으로 둔다. 따라서 본 연구의 핵심 기여는 Modular/Routed RAG 자체를 새로운 알고리즘으로 제안하는 것이 아니라, HyDE/CAD/SCD 조합의 효과를 검증 가능한 실험 설계로 분해하고 이를 전역 서비스 정책으로 제한적으로 환원하는 데 있다.

## 3. Background

### 3.1 Retrieval-Augmented Generation

Retrieval-Augmented Generation combines an information retrieval component with a generative language model [1]. Given a user query \(q\), the retriever searches a corpus \(D = \{d_1, d_2, ..., d_n\}\) and returns a ranked set of passages \(C_q\). The generator then produces an answer \(y\) conditioned on both the query and the retrieved context:

```text
y = LM(q, C_q)
```

The key advantage is that the model can answer using documents that were not part of pretraining. In academic QA, this means a user can upload a paper and ask about the paper's method, results, or limitations without fine-tuning the language model. The answer can be grounded in retrieved passages and accompanied by source chunks.

The key limitation is that RAG quality depends on both retrieval and generation, as organized by RAG surveys and best-practice studies [2]. If retrieval misses the correct passage, the generator cannot cite it. If retrieval succeeds but generation ignores the evidence, the answer may still hallucinate. Therefore, this thesis treats retrieval-side controls and decoding-side controls as separate experimental axes.

### 3.2 Dense Retrieval

Dense retrieval maps a query and documents into a shared vector space. A multilingual embedding model such as BGE-M3 transforms Korean questions and English passages into vectors [3], and retrieval is performed by similarity search, commonly cosine similarity or inner product:

```text
score_dense(q, d) = sim(emb(q), emb(d))
```

Dense retrieval is useful for cross-lingual semantic matching because a Korean question and an English passage can be close in vector space even when they share no surface tokens. This is essential for Korean-query English-paper RAG. For example, a Korean query asking about "문맥 기반 디코딩" may retrieve an English passage about context-aware decoding if the embedding model captures multilingual semantic alignment.

However, dense retrieval compresses entire passages into vectors. Exact strings such as dataset names, acronyms, equations, score values, and hyperparameters may be weakened by this compression. In academic QA, such details are often the answer. Dense retrieval therefore benefits from sparse retrieval and reranking.

### 3.3 Sparse Retrieval and BM25

Sparse retrieval ranks documents using lexical overlap. BM25 is a classic sparse retrieval function based on term frequency, inverse document frequency, and document length normalization [4]:

```text
score_BM25(q, d) = sum IDF(t) * ((tf(t,d) * (k1 + 1)) / (tf(t,d) + k1 * (1 - b + b * |d| / avgdl)))
```

BM25 is strong when the query contains exact terms. In paper QA, terms such as `BGE-M3`, `BM25`, `RRF`, `alpha`, `beta`, `F1`, dataset names, and method names should not be replaced by approximate semantic matches. A sparse signal helps ensure that passages containing the exact evidence are included in the candidate set.

Sparse retrieval alone is not enough for Korean-query English-paper RAG because Korean questions may not share tokens with English passages. It is therefore used as a complementary signal rather than a replacement for dense retrieval.

### 3.4 Hybrid Retrieval and Weighted RRF

Hybrid retrieval combines dense and sparse retrieval to benefit from both semantic matching and exact token matching. One practical challenge is that dense and sparse scores are not directly comparable. Dense similarity may be bounded while BM25 scores vary by corpus and query. The implementation applies project-specific dense 0.6 / BM25 0.4 weights to Reciprocal Rank Fusion (RRF) [5], combining ranks instead of raw scores:

```text
weighted_RRF(d) = 0.6 / (k + rank_dense(d)) + 0.4 / (k + rank_BM25(d))
```

Here, \(rank_i(d)\) is the rank assigned by retrieval system \(i\), and \(k\) is a smoothing constant. A passage ranked highly by both dense retrieval and BM25 receives a strong fused rank. A passage found by only one retriever can still survive if it is highly ranked.

In the fixed Paper-RAG backbone, hybrid retrieval is part of the frozen retrieval pipeline. HyDE is not part of the fixed backbone because it is one of the experimental axes. This separation lets the experiment ask whether HyDE improves evidence construction beyond the same dense/sparse/weighted-RRF backbone.

### 3.5 Reranking

The retriever produces candidate passages, but top-k retrieval scores may not align perfectly with answer usefulness. A reranker evaluates query-passage pairs more directly. Cross-encoder reranking encodes the query and passage together, allowing token-level interactions that a single vector comparison cannot capture [6]:

```text
score_rerank(q, d) = CrossEncoder([q; d])
```

Reranking is especially useful for academic QA because a passage can contain the right terms but still not answer the question. For example, a method section may mention a dataset but not the result asked by the query. Reranking is therefore included in the fixed backbone and held constant across the HyDE/CAD/SCD matrix.

### 3.6 Context Construction

Context construction selects and formats retrieved evidence for the generator. It includes top-k selection, optional section filters, ordering, compression, and source metadata. A context that is too short may omit required evidence; a context that is too long may bury the answer or introduce irrelevant passages. The "Lost in the Middle" effect motivates careful context ordering because models can underuse evidence placed in the middle of long prompts [13].

For this thesis, context construction belongs to the fixed Paper-RAG backbone. The main experiment should not change context construction while measuring HyDE, CAD, and SCD. This prevents the analysis from confusing retrieval/generation-control effects with unrelated prompt construction changes.

### 3.7 RAG Hallucination

RAG hallucination occurs when a generated answer is unsupported by retrieved evidence. It can arise from retrieval failure, context noise, prompt ambiguity, or the model's parametric memory. This thesis focuses particularly on generation-side hallucination after evidence is retrieved. CAD addresses this by comparing the model's context-conditioned distribution with a no-context distribution [9]. If a token is likely without the document but not especially supported by the document, CAD can reduce its relative probability.

Numeric hallucination is a stricter subtype. A generated number can look plausible but be unsupported. In academic papers, this may affect scores, sample counts, dataset sizes, hyperparameters, confidence intervals, or ablation values. The experiment therefore separates numeric hallucination from general faithfulness.

### 3.8 Multilingual and Korean-Query English-Paper RAG

Korean-query English-paper RAG has a distinctive prompt/context/output interface:

```text
query language: Korean
evidence language: mostly English
target answer language: Korean
```

The problem is not simply whether the query is Korean or English. The central issue is that English evidence can influence the output language. The model may answer in Korean but insert English clauses, or it may over-copy English technical phrasing. SCD is introduced as a Korean-target decoding control for this output-language problem.

At the same time, English technical terms should not be blindly penalized. Academic Korean naturally preserves names such as `BERT`, `RAG`, `BM25`, `BGE-M3`, `HyDE`, `CAD`, dataset names, equations, and citations. Therefore, SCD requires a neutral-token policy and a technical-term whitelist. The goal is Korean answer stability, not forced translation of all technical vocabulary.

## 4. Related Work

### 4.1 RAG Systems and Design Practice

Early RAG work established the principle of conditioning generation on retrieved documents [1]. Later surveys and best-practice studies organized RAG pipelines into retrieval, augmentation, and generation stages, and studied practical choices such as chunk size, reranking, query expansion, and context length [2]. This thesis uses that literature to justify a fixed Paper-RAG backbone rather than treating every pipeline choice as a main contribution.

### 4.2 Multilingual Dense Retrieval

Multilingual dense retrieval research shows that embedding models can map semantically related texts across languages into a shared vector space. BGE-M3 is the implemented multilingual embedding model used in the fixed Paper-RAG backbone [3]. It is retained as an implementation reference because the system actually uses it for multilingual dense retrieval, not because this thesis treats BGE-M3 itself as a new contribution.

### 4.3 Sparse Retrieval and Rank Fusion

BM25 [4] and RRF [5] provide the sparse and rank-fusion foundations of the fixed backbone. BM25 contributes exact-term sensitivity, while RRF combines retrieval systems without requiring score calibration. These methods are not claimed as new contributions; they provide a stable retrieval baseline for the factor analysis.

### 4.4 Reranking and Passage Relevance

Cross-encoder reranking [6] and passage-ranking benchmarks [7] motivate a second-stage relevance model after initial retrieval. This is particularly important in academic documents because a passage may contain query terms but fail to answer the question. Reranking is therefore fixed in the backbone.

### 4.5 Query Reformulation and HyDE

HyDE generates a hypothetical answer-like document from a query and retrieves using that representation [8]. The key intuition is that answer-like text can be closer to relevant documents than the original question form. A Korean-language study also applies HyDE-based multi-hop retrieval to improve retrieval performance, which is directly relevant to the Korean-query setting of this thesis [17]. This thesis does not propose HyDE itself. It evaluates HyDE as an on/off retrieval-side experimental factor in the Korean-query English-paper setting.

### 4.6 Context-Aware Decoding

CAD is related to contrastive decoding [10] because it compares two distributions during generation. Instead of contrasting a strong model with a weak model, CAD contrasts the same model under context and no-context conditions [9]. A Korean-language study also explores contrastive context-aware decoding for hallucination mitigation [18]. In this thesis, CAD is treated as a decoding-time context-faithfulness factor whose hypothesized purpose is to reduce parametric-memory intervention and improve evidence support; whether it does so is an empirical question (see H2).

### 4.7 Language Drift and Korean-Target Decoding

Recent work on multilingual RAG language drift characterizes unintended output-language shifts under cross-lingual evidence and proposes Soft Constrained Decoding (SCD), a training-free decoding strategy that penalizes non-target-language tokens [11]. This thesis evaluates Korean-target SCD as a controlled decoding factor for Korean-query English-paper RAG, not as a general multilingual solution or as a new method introduced by this thesis.

### 4.8 Evaluation of RAG Answers

RAG evaluation commonly measures faithfulness, answer relevance, context precision, and context recall. The original Phase 8 main matrix evaluates those four metrics with RAGAS [12] under a fixed judge. Because Mi:dm 2.0 is not served through the judge provider used here, that judge is an OpenAI-compatible NVIDIA NIM endpoint (`meta/llama-3.3-70b-instruct`, temperature 0) held constant across the original scored comparison; answer-relevancy embeddings use local BGE-M3. Absolute scores are therefore judge-specific and are not compared across judges — the claims rest on within-experiment factor deltas measured under the relevant fixed judge. The corrected `reference_scd` score track is a documented exception: it uses OpenAI `gpt-4o` [19] after NVIDIA NIM failed to converge reliably and adds fixed `gpt-4.1-2025-04-14` as a cross-judge sensitivity check, while preserving the judge-independent language-adherence comparison separately. Because multilingual LLM judges can exhibit language-dependent reliability [20], Section 15.2 limits the interpretation of those panels. Korean-language work also studies automatic dataset-generation frameworks for RAG evaluation [16].

### 4.9 Methods Outside the Core Scope

Some related RAG research studies multi-query retrieval, hierarchical summarization, compression-specific retrieval, self-evaluation, graph-based retrieval, multimodal paper understanding, or agentic paper QA. Benchmarking libraries for RAG provide standardized comparison across such directions [14]. These directions are relevant as background or future work, but they are not core implemented methods in this thesis. They must not be presented as part of the HyDE × CAD × SCD main experiment unless a later implementation audit explicitly changes the scope.

## 5. Problem Definition

Let \(q_{ko}\) be a Korean query and \(D_{en}\) be a collection of English academic paper chunks. The system retrieves a context \(C\) from \(D_{en}\) and generates a Korean answer \(y_{ko}\). The desired answer should satisfy four constraints:

```text
evidence support: answer claims are supported by retrieved context
numeric exactness: numeric claims match paper evidence
language stability: the answer remains Korean except accepted technical terms
answer relevance: the answer addresses the user's question
```

The main research problem is to estimate how HyDE, CAD, and SCD affect these constraints under a fixed retrieval backbone:

```text
factors = {HyDE on/off, CAD on/off, SCD on/off}
backbone = fixed Paper-RAG retrieval and reranking pipeline
task = Korean-query / English-paper RAG
```

The thesis asks:

- RQ1: Does HyDE improve evidence construction for Korean questions over English paper passages?
- RQ2: Does exact CAD reduce unsupported and numeric hallucinations when evidence is available?
- RQ3: Does Korean-target SCD reduce language drift without suppressing necessary technical terms?
- RQ4: How do CAD and SCD interact when both decoding controls are active?
- RQ5: Which query types should enable each factor in the graduation-project routed service?

### 5.1 Research Hypotheses

These are pre-experiment hypotheses. No result is asserted here; each will be accepted, rejected, or left undetermined only after a verified experiment run. The theoretical grounding for each hypothesis is a prior-work citation, not evidence produced by this thesis.

- **H1 (HyDE):** Enabling HyDE will change retrieval quality and evidence support relative to query-only retrieval under the same fixed backbone. Direction is not assumed. Grounding: HyDE as hypothetical-document retrieval [8], multilingual dense retrieval [3], and Korean HyDE-based multi-hop retrieval [17].
- **H2 (CAD):** Enabling CAD will change the rate of unsupported claims and numeric hallucination when relevant evidence is present. Grounding: Context-Aware Decoding [9] and contrastive decoding [10].
- **H3 (SCD):** Enabling Korean-target SCD will change language-drift rate and Korean answer ratio without removing whitelisted technical terms. Grounding: language drift and Soft Constrained Decoding [11].
- **H4 (CAD × SCD interaction):** When CAD and SCD are both enabled, their combined effect may be non-additive because both modify decoding-time token scores. Grounding: CAD [9] and SCD [11].

The thesis explicitly does not claim that the routed service architecture itself is a new RAG algorithm. The route layer is evaluated qualitatively as system integration and policy application.

## 6. System Overview

M-RAG has two layers.

The research layer is the fixed Paper-RAG backbone plus the HyDE × CAD × SCD matrix. It is implemented under the separated `experiments/` framework and should be executed only after parameter tuning, query split validation, and evaluation readiness checks.

The service layer is a FastAPI and React paper-review chatbot. It supports document upload, text extraction, chunking, vector indexing, retrieval, answer generation, source display, streaming, follow-up questions, citations, comparison, summaries, and quizzes. The configured generation model is the Mi:dm 2.0 instruct model [15]. The service layer helps demonstrate the graduation-project application, but it is not the thesis novelty.

The high-level runtime flow is:

```text
document upload
-> parsing and section detection
-> chunking
-> embedding and vector storage
-> user query
-> service route selection
-> retrieval and reranking
-> context construction
-> generation with optional HyDE/CAD/SCD controls
-> answer, sources, metadata
```

The experiment flow is more constrained:

```text
fixed query split
-> fixed backbone config
-> select one of 8 HyDE/CAD/SCD configs
-> retrieve evidence
-> generate answer
-> evaluate with predefined metrics
-> aggregate by factor and query type
```

The distinction matters. Runtime may contain service conveniences, but the main experiment must vary only the three declared factors.

## 7. Fixed Paper-RAG Backbone

### 7.1 Document Parsing and Chunking

Academic papers are parsed into text and metadata. Section detection assigns labels such as abstract, introduction, method, result, discussion, or conclusion where possible. Chunking divides the document into retrievable units while preserving section metadata. The goal is to create passages small enough for retrieval but large enough to retain evidence.

### 7.2 Dense Retrieval Component

The dense retriever embeds queries and chunks into a multilingual vector space. This supports Korean-to-English semantic matching. In the fixed backbone, the dense retriever is always enabled, and its configuration is not varied during the main matrix.

### 7.3 Sparse Retrieval Component

BM25 is used to capture exact lexical evidence. It is particularly important for acronyms, model names, numerical values, equation references, and dataset names. In the fixed backbone, sparse retrieval is always enabled.

### 7.4 Rank Fusion

Dense and sparse candidates are fused with weighted RRF, using dense weight 0.6 and BM25 weight 0.4. This avoids raw score calibration and allows both semantic and lexical candidates to contribute. The weighted-RRF configuration is part of the fixed backbone.

### 7.5 Reranking

The reranker scores query-passage pairs and selects the most relevant passages for context construction. Reranking is fixed across all eight main configs.

### 7.6 Frozen Parameters

After tuning on `tuning_queries`, the following parameters must be frozen before the main matrix:

- `top_k`
- `rerank_top_n`
- `cad_alpha`
- `scd_beta`
- HyDE prompt/template
- generation settings

The main matrix must not tune these values on `decoder_main_queries`, `query_type_analysis_queries`, or `candidate_final_eval_queries`.

## 8. Proposed Factor Analysis Method

### 8.1 HyDE

HyDE addresses the mismatch between question form and document form. A Korean question is usually short, interrogative, and user-oriented. A relevant paper passage is usually declarative, technical, and English. HyDE generates a hypothetical answer-like text and uses it as the retrieval representation.

The retrieval process can be described as:

```text
h = HyDE(q)
search_text = h if HyDE is enabled else q
C = retrieve(search_text, D)
```

In this thesis, HyDE [8] is not treated as a new method. It is the retrieval-side experimental axis. The question is whether enabling it changes evidence support and answer relevancy under the same fixed backbone (H1).

Expected analysis (hypotheses for H1, not results):

- HyDE may improve semantic recall for method and conceptual questions.
- HyDE may be less useful for exact numeric questions if the hypothetical text omits the exact number.
- HyDE may interact with CAD because better evidence construction gives CAD more useful context-conditioned signals.

### 8.2 CAD

CAD is designed to reduce parametric-memory intervention by contrasting context-conditioned and no-context model scores [9]; whether it does so on this corpus is the empirical question of H2. Let \(s_c(y_t)\) be the score for token \(y_t\) conditioned on query, retrieved context, and generated prefix. Let \(s_0(y_t)\) be the score for the same token conditioned on the same query and generated prefix but without retrieved context. The exact contract used in this thesis is:

```text
cad_scores = (1 + alpha) * context_scores - alpha * no_context_scores
```

Equivalently:

```text
s_CAD(y_t) = (1 + alpha) * s_c(y_t) - alpha * s_0(y_t)
```

This formula increases the relative importance of tokens that are more supported under the context condition and decreases tokens likely under the no-context condition. The no-context branch must use the same generated prefix \(y_{<t}\), otherwise the contrast is not valid.

Implementation contract:

- Use the same generated prefix in context and no-context branches.
- Use fixed alpha for the main thesis experiment.
- Use the uncached no-context reference path unless cached parity is proven.
- Block unsupported batch or beam modes if prefix parity is not guaranteed.

Expected analysis (hypotheses for H2, not results):

- CAD is hypothesized to reduce unsupported claims and numeric hallucination when relevant evidence exists.
- CAD may make generation more conservative.
- CAD should not change retrieval metrics directly; if context precision changes under CAD-only comparisons, the evaluation pipeline should be inspected.

### 8.3 SCD

SCD is Korean-target Soft Constrained Decoding, a training-free decoding strategy for mitigating language drift in multilingual RAG [11]. This repository now distinguishes two experimentally different implementations instead of calling both simply "SCD."

The original Phase 8 matrix used the project-specific `penalty_additive` v1 mode. Let \(V_{ko}\) be Korean target tokens, \(V_n\) neutral tokens, and \(V_w\) project-whitelisted technical tokens. Its rule was:

```text
z'_i = z_i - beta,  if i is outside V_ko ∪ V_n ∪ V_w
z'_i = z_i,         otherwise
```

The corrected `reference_scd` rerun instead reproduces the reference paper's three-way raw-logit scaling after a generated-token warm-up:

```text
z'_i = z_i,          if generated step t < Tstart
z'_i = alpha * z_i,  if t >= Tstart and i is a target-language token
z'_i = z_i,          if t >= Tstart and i is neutral
z'_i = beta * z_i,   if t >= Tstart and i is a distractor-language token
```

The reproduced settings are `alpha=1.1`, `beta=0.9`, and `Tstart=5`. The implementation deliberately applies the paper's formula to raw logits, including negative logits. Neutral tokens include whitespace, punctuation, digits, brackets, math symbols, citation markers, and common academic symbols. The project whitelist belongs to the v1 application mode; the literal `reference_scd` mode uses the reference vocabulary partition without that whitelist.

SCD is not intended to translate every English term into Korean. Academic Korean naturally includes English method names and acronyms. The corrected experiment therefore measures whether unnecessary sentence-level drift decreases, and reports language adherence separately from RAG-quality effects. Section 12 preserves the v1 result; Section 13.3 reports the completed `reference_scd` result and its measured trade-off. CAD and SCD may interact because both operate at decoding time, so a combined benefit must be measured rather than assumed.

### 8.4 Combined Decoding

When CAD and SCD are both enabled, CAD first adjusts the evidence contrast and SCD then applies Korean-target constraints, or the implementation applies both processors in a deterministic order. The main analysis should compare:

```text
no decoder control
CAD only
SCD only
CAD + SCD
```

The combined condition should be interpreted carefully. If CAD improves evidence support but SCD changes lexical choices, evaluator behavior must be checked so that language control is not mistaken for evidence loss.

## 9. Experimental Design

The main experiment is a full factorial matrix:

```text
HyDE × CAD × SCD = 8 configs
```

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

The experiment uses the fixed Paper-RAG backbone. The main matrix varies only HyDE, CAD, and SCD. It must not introduce additional retrieval modes, route-dependent logic changes, or service-only controls.

The planned analysis includes:

- main effects of HyDE, CAD, and SCD
- CAD × SCD interaction
- HyDE × CAD interaction
- HyDE × SCD interaction
- query-type breakdown
- numeric-question subset analysis
- language-drift subset analysis
- cost and latency discussion

The main experiment has been executed and scored; Section 12 reports the measured
faithfulness, answer-relevancy, context-precision, and context-recall values plus a
direct Korean-answer-ratio measurement. A numeric-hallucination subset metric and a
per-query-type breakdown were not computed in this run and are marked as such.

## 10. Query Set and Split Policy

The query policy prevents leakage and avoids fabricated evaluation data. Existing query assets are audited into query types, then assigned to split roles.

Split roles:

- `tuning_queries`: used only to choose frozen parameters.
- `decoder_main_queries`: used for the main HyDE × CAD × SCD matrix.
- `query_type_analysis_queries`: used to analyze query-type effects.
- `candidate_final_eval_queries`: reserved for a later final evaluation after validation.
- `service_route_queries`: qualitative examples for A-F service routes only.
- `query_templates`: templates that require answerability validation before quantitative use.

Rules:

- Do not duplicate queries to satisfy target counts.
- Do not fabricate service-route queries.
- Do not tune on main or final-eval candidate queries.
- Do not promote templates into quantitative evaluation without answerability validation.
- Keep GT generation separate from evaluated system output.

This policy is important because weak or contaminated query splits can make method effects look stronger or weaker than they are.

## 11. Evaluation Metrics

### 11.1 Faithfulness

Faithfulness measures whether answer claims are supported by retrieved context. A faithful answer should not add unsupported facts even if those facts are plausible from pretraining. CAD is expected to affect this metric most directly.

### 11.2 Evidence Support

Evidence support is a claim-level or answer-level assessment of whether the cited passages contain sufficient support. It differs from raw retrieval relevance because a passage can be topically related but not sufficient to justify the answer.

### 11.3 Answer Relevancy

Answer relevancy measures whether the response addresses the user's question. A highly faithful answer can still be incomplete or off-target. HyDE may affect answer relevancy indirectly through better evidence retrieval.

### 11.4 Context Precision

Context precision measures the proportion of retrieved context that is useful for answering the question. Dense retrieval, sparse retrieval, RRF, and reranking all contribute to this, but they are fixed in the main experiment. HyDE may change context precision because it changes the retrieval query representation.

### 11.5 Context Recall

Context recall measures whether necessary evidence is included in the retrieved context. In academic QA, context recall matters for method descriptions, multi-part results, and comparison questions.

### 11.6 Numeric Hallucination Rate

Numeric hallucination rate measures unsupported or incorrect numeric claims. It should check values, units, comparisons, and associated entities. For example, reporting the right number for the wrong dataset is still an error.

### 11.7 Language Drift Rate

Language drift rate measures unnecessary non-Korean output in answers expected to be Korean. It should distinguish technical terms from English clauses or sentences. This metric is central for evaluating SCD.

### 11.8 Korean Answer Ratio

Korean answer ratio measures how much of the answer is Korean-compatible after neutral symbols and whitelisted terms are accounted for. It complements language drift rate by measuring positive target-language stability.

### 11.9 Answer Span Hit at K

Answer span hit at K measures whether retrieved top-k passages contain expected evidence spans. It is useful for separating retrieval failure from generation failure. If the answer span is absent from retrieved context, CAD cannot recover evidence that was never retrieved.

### 11.10 RAGAS-Compatible and Lightweight Evaluation Boundary

RAGAS is executed as the evaluation tool for the four metrics, kept separate from any lightweight local evaluator. The original Phase 8 main matrix used the RAGAS package with a fixed NVIDIA NIM judge (`meta/llama-3.3-70b-instruct`) and local BGE-M3 embeddings. Scored coverage was 583/608 metric cells (95.9%); the remaining cells were judge-endpoint timeouts on the largest multi-context payloads and are excluded from means. The corrected `reference_scd` RAG-quality re-evaluation used `gpt-4o` as a deliberate experiment-specific judge exception and converged to 0/608 null cells after the NIM attempt failed to converge at scale. Its later symmetric track adds 304/304 `gpt-4o` cells and 304/304 fixed `gpt-4.1-2025-04-14` cells for cross-judge robustness. RAGAS is the measurement instrument, not a proposed method of this thesis.

## 12. Result Tables

Values are from the executed and scored main run (152 generations; RAGAS with a
fixed NVIDIA NIM judge `meta/llama-3.3-70b-instruct`, local BGE-M3 embeddings).
Means exclude null cells (583/608 scored). Source artifacts:
`experiments/results/analysis/main_config_scores.csv` and `main_axis_effects.json`.

### Table 1. Experimental Setup

| Item | Value |
|---|---|
| Task | Korean-query / English-paper RAG |
| Backbone | Fixed Paper-RAG retrieval backbone |
| Dense retrieval | BGE-M3 |
| Sparse retrieval | BM25 |
| Fusion | Weighted RRF (dense 0.6 / BM25 0.4) |
| Reranking | CrossEncoder `ms-marco-MiniLM-L-6-v2` |
| Generation model | Mi:dm 2.0 Base (`K-intelligence/Midm-2.0-Base-Instruct`), A100 80GB |
| Frozen params | pool 8 / rerank 8 / context 5, cad_alpha 0.5, scd_beta 0.3, 512 tokens, greedy |
| Main factors | HyDE, CAD, SCD |
| Tuned only on | `tuning_queries` |
| Main query split | `decoder_main_queries` (19 queries) |
| Judge | NVIDIA NIM `meta/llama-3.3-70b-instruct` (fixed) |
| Result status | completed and scored (583/608 cells) |

### Table 2. Main HyDE × CAD × SCD Factorial Ablation

Columns are the four executed RAGAS metrics plus a directly measured Korean answer
ratio. A separate numeric-hallucination metric and an "evidence support" metric were
not computed in this run.

| Config | Faithfulness | Answer relevancy | Context precision | Context recall | Korean answer ratio |
|---|---:|---:|---:|---:|---:|
| `hyde_off__no_decoder_control` | 0.871 | 0.825 | 0.891 | 0.947 | 0.594 |
| `hyde_off__cad_only` | 0.926 | 0.805 | 0.914 | 0.947 | 0.524 |
| `hyde_off__scd_only` | 0.848 | 0.829 | 0.853 | 0.947 | 0.602 |
| `hyde_off__cad_scd` | 0.919 | 0.784 | 0.877 | 0.947 | 0.525 |
| `hyde_on__no_decoder_control` | 0.867 | 0.866 | 0.844 | 0.947 | 0.607 |
| `hyde_on__cad_only` | 0.917 | 0.906 | 0.845 | 0.974 | 0.588 |
| `hyde_on__scd_only` | 0.916 | 0.892 | 0.810 | 1.000 | 0.582 |
| `hyde_on__cad_scd` | 0.925 | 0.858 | 0.867 | 0.974 | 0.549 |

### Table 3. Effect Delta Summary

Main effects are paired ON−OFF deltas over configs identical except for the named
factor (win/loss counts use a ±0.01 band).

| Effect | Metric | Paired delta (win/loss) |
|---|---|---:|
| HyDE main effect | answer_relevancy | +0.070 (28/18) |
| HyDE main effect | context_recall | +0.026 (4/3) |
| HyDE main effect | context_precision | −0.056 (19/18) |
| CAD main effect | faithfulness | +0.044 (25/17) |
| CAD main effect | context_recall | 0.000 (1/2) |
| SCD v1 main effect | faithfulness | +0.009 (16/17) |
| SCD v1 main effect | Korean answer ratio (direct) | −0.014 (22/24) |

Interpretation: CAD raises faithfulness; HyDE trades context precision for higher
answer relevancy and recall; SCD is a null factor in the v1 `penalty_additive`
implementation on both the RAGAS metrics and its own Korean-adherence target.
Section 13.3 reports the corrected `reference_scd` rerun, where SCD strongly
improves Korean-language adherence; its RAGAS panel is a separate sensitivity analysis.
Internal-validity note: the decoder-side factors (CAD,
SCD) leave context_recall essentially unchanged (retrieval is not altered), while the
retrieval-side factor (HyDE) moves it — factors affect the metrics they structurally
should. The combined `hyde_on__cad_scd` cell reaches the joint-highest faithfulness
(0.925), consistent with an additive CAD contribution rather than a strong
CAD×SCD interaction.

### Table 4. Query-Type Breakdown

Not computed in this run. With n = 19 queries the per-query-type cells are too small
to split reliably; a per-type breakdown is left as future work on a larger query set.

### Table 5. Numeric Hallucination and Evidence Support

Not computed in this run. The evaluation measured the four RAGAS metrics and Korean
answer ratio; a numeric-exactness metric and a separate evidence-support metric are
future work.

### Table 6. Language Drift and Korean Answer Ratio

Language drift rate = fraction of the 19 answers below 0.5 Korean-character ratio;
Korean answer ratio = mean per config. Whitelist errors were not separately counted.

| Config | Language drift rate (<0.5) | Korean answer ratio |
|---|---:|---:|
| `hyde_off__no_decoder_control` | 0.26 | 0.594 |
| `hyde_off__cad_only` | 0.32 | 0.524 |
| `hyde_off__scd_only` | 0.26 | 0.602 |
| `hyde_off__cad_scd` | 0.37 | 0.525 |
| `hyde_on__no_decoder_control` | 0.26 | 0.607 |
| `hyde_on__cad_only` | 0.16 | 0.588 |
| `hyde_on__scd_only` | 0.26 | 0.582 |
| `hyde_on__cad_scd` | 0.37 | 0.549 |

The original `penalty_additive` v1 SCD-on configs do not reduce drift relative to their
matched SCD-off configs; drift is substantial (16–37%) across that matrix, and v1 does
not remove it (see the SCD failure analysis). The completed `reference_scd` result is
reported separately in Section 13.3 and must not be read back into this historical table.

### Table 7. Routed Policy for Graduation-Project System

Derived from the original-matrix factor effects plus the corrected direct language
result (not a measurement table). CAD is recommended on across routes for its original
faithfulness gain; HyDE is recommended where recall/relevancy matters more than context
precision. `reference_scd` is available conditionally for language control, but its
RAG-quality effect must be validated per task.

| Service route | Query type | Derived HyDE | Derived CAD | Derived SCD | Status |
|---|---|---|---|---|---|
| A simple QA | factual / conceptual | optional | on | conditional; validate quality | service feature |
| B section QA | section-specific | off (precision) | on | conditional; validate quality | service feature |
| C comparison | comparison | on (recall) | on | conditional; validate quality | service feature |
| D citation lookup | citation-oriented | off (precision) | on | conditional; validate quality | service feature |
| E structured summary | summary | on (recall) | on | conditional; validate quality | service feature |
| F quiz / flashcard | study support | optional | on | conditional; validate quality | service feature |

## 13. Discussion

The following interprets the measured factor effects (Section 12).

### 13.1 Interpreting HyDE

HyDE raised answer relevancy (+0.070 paired) and context recall (+0.026) while lowering
context precision (−0.056). This is the expected recall/precision trade-off of query
reformulation: hypothetical-document expansion pulls more relevant material into the
pool but also admits some off-target chunks. Faithfulness moved only slightly (+0.016),
so HyDE mainly reshapes retrieval rather than grounding.

### 13.2 Interpreting CAD

CAD raised faithfulness by +0.044 (paired 25 wins / 17 losses), the largest single-axis
gain, matching its design goal of contrasting context and no-context distributions to
suppress ungrounded tokens. Context recall was unchanged (CAD is decoder-side), and
answer relevancy dipped slightly (−0.015), consistent with a mild fluency cost rather
than a failure; alpha = 0.5 did not appear too strong on this corpus.

### 13.3 Interpreting SCD

The original Phase 8 SCD result should be read as the superseded v1
`penalty_additive` result, not as a claim about paper-faithful SCD. In that v1
run, SCD did not reduce language drift. It was neutral on all four RAGAS metrics
and net-null on its own Korean-adherence target (direct Korean-ratio delta
−0.0137, rounded as −0.014 in Table 3), rescuing only 2/19 drifting answers
while degrading 9/28 already-Korean ones. The dedicated SCD failure analysis
attributes this to implementing only a penalty-only, additive, always-on
fragment of the reference method — missing the target-language boost,
multiplicative scaling, and cold-start warm-up.

The corrected `reference_scd` rerun resolves that implementation gap. It is a
literal reference-paper implementation with multiplicative target boost
`alpha=1.1`, multiplicative distractor penalty `beta=0.9`, and cold-start
warm-up until `Tstart=5`. On SCD's actual target metric, Korean-language
adherence, it improves strongly: mean paired delta +0.2203 over 76 matched
pairs, SCD-on more Korean in 68/76 pairs versus 3/76 less Korean, 15/26 drift
rescues at the 0.5 threshold, and no baseline ratio ≥0.7 case crossing below the
predefined 0.65 harm threshold (0/20). Three of 76 pairs nevertheless decreased,
and 12/76 SCD-on answers remained below 0.5, so this is a substantial improvement,
not complete elimination of drift. The mean delta remains +0.2198 in the 38
HyDE-off pairs whose retrieved contexts are byte-identical, supporting the direct
language-control conclusion independently of HyDE retrieval variance.

The `gpt-4o` panel has 152 samples and 0/608 null metric cells. Under that exact
protocol, SCD-on cells differ by faithfulness −0.048, answer_relevancy −0.057,
context_precision +0.030, and context_recall −0.066. These deltas are descriptive,
not isolated causal SCD effects: only SCD-on contexts were translated, all answer-key
references remained English, and 25/38 HyDE-on SCD pairs had different retrieved
contexts. RAGAS 0.2.15 context precision and context recall do not use the generated
answer, so their differences cannot be attributed to decoder behavior. The panel
does not establish that SCD improves or harms hallucination. Full details are in
`experiments/reports/reference_scd_rerun_report.md`.

A stricter follow-up completes the previously proposed symmetric test on the
HyDE-off subset. It freezes 76 records across four configurations, verifies all
38 SCD-on/off pairs have byte-identical retrieved contexts, and applies one
score-independent normalization policy to question, answer, reference, and all
nested context text for both English and Korean target panels. The two panels have
0/304 null metric cells in total. With 10,000 deterministic query-clustered paired
bootstrap resamples, overall faithfulness is unresolved in both languages: English
+0.0071, 95% CI [−0.0596, +0.0714], and Korean −0.0283,
[−0.1044, +0.0510]. Under `gpt-4o`, overall answer relevancy is lower in both:
English −0.0910 [−0.1725, −0.0240] and Korean −0.0752
[−0.1501, −0.0138]. A fixed `gpt-4.1-2025-04-14` cross-judge does not reproduce
nonzero intervals: English −0.0327 [−0.0851, +0.0129] and Korean −0.0356
[−0.1149, +0.0315]. Its faithfulness intervals also overlap zero. Across all four
language-by-judge panels, answer-relevancy means are negative, but the nonzero
`gpt-4o` interval class is not judge-robust. Therefore the follow-up does not establish
an unbiased causal SCD effect or a stable quality cost. Normalization occurs after
generation, Korean answer transformation exposure differs by condition, only 19 query
clusters are available, and no human evaluation was run. Input audit, hashes, counts,
and full results are retained in
`experiments/reports/reference_scd_symmetric_input_audit.md` and
`experiments/reports/reference_scd_symmetric_cross_judge_report.md`.

### 13.4 Interactions

CAD and SCD may complement each other because they target different failure modes. CAD targets evidence faithfulness, while SCD targets output language. However, both modify token scores, so interaction effects must be interpreted carefully. HyDE may also affect decoder controls by changing the quality of retrieved evidence.

### 13.5 Query-Type Policy

The service policy does not simply enable every factor for every route. Table 7 derives
route-level defaults from the measured effects: CAD on across routes (faithfulness gain),
HyDE on where recall/relevancy outweighs precision (comparison, summary) and off where
precision matters (section-specific, citation lookup), and SCD as a conditional
language-adaptation control whose use requires task-specific quality validation; the
symmetric follow-up finds no judge-robust nonzero RAG-quality effect and remains
insufficient to set a causal or deployment policy.

## 14. Graduation-Project System Integration

The M-RAG service integrates the research layer into a paper-review chatbot. It supports A-F routes:

| Route | Service purpose | Thesis status |
|---|---|---|
| A | simple QA | service feature |
| B | section-focused QA | service feature |
| C | document comparison | service feature |
| D | citation / patent-oriented lookup | service feature |
| E | structured summary | service feature |
| F | quiz / flashcard generation | service feature |

These routes are useful for a graduation project because users do not interact with academic papers through one question type. They ask factual questions, request method explanations, compare papers, inspect citations, summarize documents, and generate study materials. The service router organizes these tasks.

However, the route layer is not presented as the thesis algorithm. It is a runtime architecture that applies the research findings. The current run can support only global factor-effect defaults. Route-level defaults by query type require the future query-type analysis described in Table 4, which keeps the service integration evidence-driven rather than claim-driven.

Runtime compatibility also matters. The service must preserve QueryRequest, QueryResponse, SSE streaming, paper APIs, citation APIs, and active document filtering. The thesis should mention these as engineering constraints, not as experimental variables.

## 15. Limitations and Future Work

### 15.1 Experiment Scope

The main experiment is limited to the selected paper corpus and query splits. Results may not generalize to all academic domains, all Korean users, or all English paper styles. A larger corpus and independently authored queries would strengthen external validity.

### 15.2 Evaluation Reliability

Automatic evaluation can misjudge faithfulness, relevance, or language drift. The original Phase 8 main matrix used a single fixed judge (NVIDIA NIM `meta/llama-3.3-70b-instruct`), so absolute scores are judge-specific and the claims rest on within-experiment factor deltas rather than cross-judge comparison. The corrected `reference_scd` RAG-quality panel is a deliberate exception: reported Alice-run provenance says NVIDIA NIM ran for over 60 hours and ended its first pass with a 38.6% null rate before the instance was deleted; the removed remote logs are no longer independently reproducible from the local repository. OpenAI `gpt-4o` [19] then produced 0/608 null cells in the retained asymmetric artifact. The symmetric follow-up adds zero-null `gpt-4o` and fixed `gpt-4.1-2025-04-14` panels, whose interval disagreement directly demonstrates judge sensitivity. These judge changes do not affect the direct Korean-ratio comparison.

The first `gpt-4o` panel does not fully control the cross-lingual confound. `translate_context_for_scd.py` translated contexts only for SCD-on records, making preprocessing perfectly correlated with the experimental factor; SCD-off answers were not uniformly English, and ground-truth references remained English. The parser also verified structure rather than Korean-language content. Retrieval itself differed in 25/38 HyDE-on SCD pairs. Accordingly, faithfulness and both context metrics in that panel are protocol-dependent, while answer relevancy is a descriptive question-answer score not directly affected by context translation.

The completed symmetric follow-up removes the SCD-on-only preprocessing correlation,
uses the 38 byte-identical-context HyDE-off pairs, validates target language and
literal integrity, and reports query-clustered confidence intervals. A fixed
`gpt-4.1-2025-04-14` cross-judge also removes exact same-model normalization/judging.
Its intervals overlap zero for both metrics and languages, so the `gpt-4o` nonzero
answer-relevancy finding is not cross-judge robust. Evaluation uncertainty remains:
normalization is a post-generation outcome transformation, both judges are from the
same provider, and realized Korean answer translation exposure differs by SCD
condition (23/38 SCD-off versus 11/38 SCD-on translated). The sample contains 19
query clusters, and no human evaluation is available. Multilingual judge reliability
[20], independent-provider replication, larger independently authored query sets, and
blinded human review therefore remain future work.

### 15.3 GT and Answer-Key Policy

Ground truth must be treated as an answer key, not as evaluated system output. If GT generation uses retrieval assistance or external models, that process must be separated from the system being evaluated. GT normalization, translation, and cross-lingual controls are fairness-sensitive choices.

### 15.4 CAD Cost

CAD requires a no-context reference branch. The correctness-first implementation recomputes no-context logits with the same generated prefix. This is safer than an unproven cache optimization but increases decoding cost. Future work can optimize cache handling only after parity tests prove correctness.

### 15.5 SCD Token Policy

SCD depends on tokenization. Technical terms may split into subword units, and some tokens may mix Korean, English, punctuation, or numbers. The whitelist and neutral-token policy must be validated with the target tokenizer.

### 15.6 Service Scaling

The graduation-project service layer still requires deployment validation, load testing, observability, and user-facing robustness work. These engineering tasks are important for the application but separate from the core factor analysis.

## 16. Conclusion

This thesis reconstructs M-RAG around a focused research contribution: HyDE × CAD × SCD factor analysis for Korean-query English-paper RAG. The fixed Paper-RAG backbone provides a stable retrieval environment. HyDE tests retrieval-side evidence construction, CAD tests context-faithfulness control, and Korean-target SCD tests output-language stability. The routed paper-review chatbot remains the graduation-project service integration layer, and its A-F routes should derive policy from the factor analysis rather than being claimed as a new algorithm.

The original main experiment was executed and scored under a fixed judge. The measured
effects are: CAD improves faithfulness (+0.044 paired), HyDE trades context precision
for higher answer relevancy and recall, and Korean-target SCD is a null factor in its
v1 `penalty_additive` form. The separate `reference_scd` rerun has now completed the
previously deferred test of the reference method: with target-language boost,
multiplicative scaling, and generated-token warm-up restored, SCD substantially
improves Korean-language adherence. The first completed `gpt-4o` panel supplies useful
protocol-specific observations but has asymmetric preprocessing and retrieval
confounds. The stricter bilingual identical-context follow-up leaves faithfulness
directionally unresolved. `gpt-4o` finds a negative answer-relevancy interval in both
target languages, but fixed `gpt-4.1-2025-04-14` does not reproduce a nonzero interval.
Thus no judge-robust nonzero RAG-quality effect is established. Because normalization
is post-generation and no human evaluation exists, this is not a causal or deployment
verdict. The global provisional policy therefore changes from
"SCD deferred" to "SCD conditionally available for language control": CAD remains
the default faithfulness control, HyDE remains route-dependent, and SCD requires
task-specific quality validation before deployment.

## 17. References

[1] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in Neural Information Processing Systems 33, 2020.

[2] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, M. Wang, and H. Wang, "Retrieval-Augmented Generation for Large Language Models: A Survey," arXiv:2312.10997, 2023.

[3] J. Chen, S. Xiao, P. Zhang, K. Luo, D. Lian, and Z. Liu, "M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation," in Findings of the Association for Computational Linguistics: ACL 2024, pp. 2318-2335, 2024, doi:10.18653/v1/2024.findings-acl.137.

[4] S. E. Robertson, S. Walker, S. Jones, M. M. Hancock-Beaulieu, and M. Gatford, "Okapi at TREC-3," in Proceedings of the Third Text REtrieval Conference (TREC-3), 1994.

[5] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," in Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval, pp. 758-759, 2009, doi:10.1145/1571941.1572114.

[6] R. Nogueira and K. Cho, "Passage Re-ranking with BERT," arXiv:1901.04085, 2019.

[7] P. Bajaj et al., "MS MARCO: A Human Generated Machine Reading Comprehension Dataset," arXiv:1611.09268, 2016.

[8] L. Gao, X. Ma, J. Lin, and J. Callan, "Precise Zero-Shot Dense Retrieval without Relevance Labels," in Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 1762-1777, 2023, doi:10.18653/v1/2023.acl-long.99.

[9] W. Shi, X. Han, M. Lewis, Y. Tsvetkov, L. Zettlemoyer, and W.-t. Yih, "Trusting Your Evidence: Hallucinate Less with Context-aware Decoding," in Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 2: Short Papers), pp. 783-791, 2024, doi:10.18653/v1/2024.naacl-short.69.

[10] X. L. Li, A. Holtzman, D. Fried, P. Liang, J. Eisner, T. Hashimoto, L. Zettlemoyer, and M. Lewis, "Contrastive Decoding: Open-ended Text Generation as Optimization," in Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 12286-12312, 2023, doi:10.18653/v1/2023.acl-long.687.

[11] B. Li, Z. Xu, and R. Xie, "Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation," in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 40, no. 37, pp. 31519-31526, 2026, doi:10.1609/aaai.v40i37.40417 (arXiv:2511.09984).

[12] S. Es, J. James, L. Espinosa Anke, and S. Schockaert, "RAGAs: Automated Evaluation of Retrieval Augmented Generation," in Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations, pp. 150-158, 2024, doi:10.18653/v1/2024.eacl-demo.16.

[13] N. F. Liu, K. Lin, J. Hewitt, A. Paranjape, M. Bevilacqua, F. Petroni, and P. Liang, "Lost in the Middle: How Language Models Use Long Contexts," Transactions of the Association for Computational Linguistics, vol. 12, pp. 157-173, 2024, doi:10.1162/tacl_a_00638.

[14] D. Rau, H. Déjean, N. Chirkova, T. Formal, S. Wang, S. Clinchant, and V. Nikoulina, "BERGEN: A Benchmarking Library for Retrieval-Augmented Generation," in Findings of the Association for Computational Linguistics: EMNLP 2024, pp. 7640-7663, 2024, doi:10.18653/v1/2024.findings-emnlp.449.

[15] D. Shin et al., "Mi:dm 2.0 Korea-centric Bilingual Language Models," arXiv:2601.09066, 2026.

[16] 김범석, 양진홍, "RAG 시스템 성능 평가를 위한 자동 데이터 셋 생성 프레임워크 비교 분석 연구," 한국정보전자통신기술학회 논문지, vol. 18, no. 2, pp. 143-154, 2025, doi:10.17661/jkiiect.2025.18.2.143.

[17] 김예은, 이재홍, 원상혁, 정우혁, 우지환, "HyDE 기반 멀티 홉 검색 기법을 활용한 검색 성능 향상 방안," 경영정보학연구(Information Systems Review), vol. 27, no. 2, pp. 127-148, 2025, doi:10.14329/isr.2025.27.2.127.

[18] 장규식, 나승훈, 김태형, 류휘정, 장두성, "Contrastive CAD: 대형 언어 모델의 환각 완화를 위한 대조적 Context-Aware Decoding," 2024년도 한글 및 한국어 정보처리·한국코퍼스언어학회 공동 학술대회(HCLT-KACL 2024) 논문집, 2024.

[19] OpenAI, "GPT-4o System Card," arXiv:2410.21276, 2024.

[20] X. Fu and W. Liu, "How Reliable is Multilingual LLM-as-a-Judge?", in Findings of the Association for Computational Linguistics: EMNLP 2025, pp. 11040-11053, 2025, doi:10.18653/v1/2025.findings-emnlp.587.
