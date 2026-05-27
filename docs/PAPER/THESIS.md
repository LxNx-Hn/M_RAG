# M-RAG: HyDE × CAD × SCD Factor Analysis for Korean-Query English-Paper RAG

## 1. Abstract

Retrieval-Augmented Generation (RAG) is widely used to answer questions over external documents, but academic-paper question answering has two additional difficulties when Korean users ask questions about English papers. First, retrieval must bridge the linguistic and stylistic gap between Korean questions and English academic prose. Second, generation must remain faithful to retrieved evidence while producing a stable Korean answer. Even when relevant passages are retrieved, a language model may introduce parametric-memory hallucinations, copy English expressions into a Korean answer, or fail to preserve numeric and technical evidence.

This thesis studies these problems through a controlled factor analysis of HyDE, Context-Aware Decoding (CAD), and Korean-target Soft Constrained Decoding (SCD). The main experiment uses a fixed Paper-RAG retrieval backbone and varies only three factors: HyDE on/off, CAD on/off, and SCD on/off. HyDE is treated as a retrieval-side evidence-construction factor, CAD as a decoding-time context-faithfulness factor, and SCD as a Korean-target language-drift-control factor. The central research question is how these factors and their interactions affect evidence support, numeric hallucination, language drift, Korean answer ratio, answer relevancy, and retrieval quality in Korean-query / English-paper RAG.

The project also includes an M-RAG paper-review chatbot with A-F service routes for simple question answering, section-focused question answering, document comparison, citation-oriented lookup, structured summarization, and quiz or flashcard generation. This routed application is framed as graduation-project system integration, not as the core thesis algorithm. The thesis contribution is the HyDE × CAD × SCD factor analysis and the derivation of a query-type-aware service policy from that analysis. No experimental result values are claimed in this draft; all result tables remain TODO placeholders until an approved and verified experiment run is completed.

## 2. Introduction

Academic documents differ from ordinary web text in density, structure, and verification requirements. A paper contains abstract, introduction, method, experiment, result, limitation, and reference sections, and each section contributes a different kind of evidence. A question such as "이 논문의 F1 점수가 얼마야?" requires exact numeric evidence. A question such as "방법론을 설명해줘" requires method-section evidence. A comparison question requires balanced evidence from two documents. A citation question may require bibliographic parsing, while a study-support question may require structured output such as quiz items.

RAG addresses part of this problem by searching external documents and conditioning generation on retrieved context. However, a fixed RAG pipeline is not sufficient for Korean-query English-paper use. Korean questions and English evidence differ in language, morphology, and discourse style. Dense retrieval may capture semantic similarity but miss exact numbers or acronyms. Sparse retrieval may capture exact terms but miss paraphrased academic statements. Long contexts can dilute evidence, and the generator can still rely on prior parametric knowledge instead of the provided paper.

Generation introduces another layer of risk. When the context is in English and the user asks in Korean, the model may drift into English phrases or produce mixed-language answers. In a paper-review setting, this is not only a usability issue. Language drift can obscure whether an answer is faithful to the English evidence, and it can make Korean explanations less coherent for the target user. Numeric hallucination is similarly serious: if the paper reports a score, dataset size, or ablation value, the answer must not replace it with a plausible but unsupported number.

This thesis therefore narrows the research contribution to three controllable factors:

- HyDE: a retrieval-side method that reformulates the query into a hypothetical answer-like document before retrieval.
- CAD: a decoding method that contrasts context-conditioned scores with no-context scores using the exact formula required by the method contract.
- SCD: Korean-target Soft Constrained Decoding that discourages non-target-language tokens while preserving neutral tokens and technical terms.

The graduation-project system layer remains important, but it serves a different purpose. The M-RAG chatbot demonstrates how the research can be integrated into a usable service. Its A-F routes are paper-review features, not the thesis novelty. The thesis asks what the HyDE/CAD/SCD analysis implies for those routes after query types are examined.

The final intended contribution is:

본 연구는 고정된 Paper-RAG 검색 backbone 위에서 HyDE, CAD, SCD의 3개 factor를 조합하여 한국어 질의-영어 논문 RAG 환경의 근거 충실성, 수치 환각, 언어 이탈, 한국어 응답 안정성에 미치는 영향을 분석한다. 또한 이 분석 결과를 query type별로 해석하여 졸업작품 시스템인 M-RAG 논문 리뷰 챗봇의 Routed policy로 연결한다. 따라서 본 연구의 핵심 기여는 Modular/Routed RAG 자체를 새로운 알고리즘으로 제안하는 것이 아니라, HyDE/CAD/SCD 조합의 효과를 검증 가능한 실험 설계로 분해하고 이를 서비스 정책으로 환원하는 데 있다.

## 3. Background

### 3.1 Retrieval-Augmented Generation

Retrieval-Augmented Generation combines an information retrieval component with a generative language model. Given a user query \(q\), the retriever searches a corpus \(D = \{d_1, d_2, ..., d_n\}\) and returns a ranked set of passages \(C_q\). The generator then produces an answer \(y\) conditioned on both the query and the retrieved context:

```text
y = LM(q, C_q)
```

The key advantage is that the model can answer using documents that were not part of pretraining. In academic QA, this means a user can upload a paper and ask about the paper's method, results, or limitations without fine-tuning the language model. The answer can be grounded in retrieved passages and accompanied by source chunks.

The key limitation is that RAG quality depends on both retrieval and generation. If retrieval misses the correct passage, the generator cannot cite it. If retrieval succeeds but generation ignores the evidence, the answer may still hallucinate. Therefore, this thesis treats retrieval-side controls and decoding-side controls as separate experimental axes.

### 3.2 Dense Retrieval

Dense retrieval maps a query and documents into a shared vector space. A multilingual embedding model transforms Korean questions and English passages into vectors, and retrieval is performed by similarity search, commonly cosine similarity or inner product:

```text
score_dense(q, d) = sim(emb(q), emb(d))
```

Dense retrieval is useful for cross-lingual semantic matching because a Korean question and an English passage can be close in vector space even when they share no surface tokens. This is essential for Korean-query English-paper RAG. For example, a Korean query asking about "문맥 기반 디코딩" may retrieve an English passage about context-aware decoding if the embedding model captures multilingual semantic alignment.

However, dense retrieval compresses entire passages into vectors. Exact strings such as dataset names, acronyms, equations, score values, and hyperparameters may be weakened by this compression. In academic QA, such details are often the answer. Dense retrieval therefore benefits from sparse retrieval and reranking.

### 3.3 Sparse Retrieval and BM25

Sparse retrieval ranks documents using lexical overlap. BM25 is a classic sparse retrieval function based on term frequency, inverse document frequency, and document length normalization:

```text
score_BM25(q, d) = sum IDF(t) * ((tf(t,d) * (k1 + 1)) / (tf(t,d) + k1 * (1 - b + b * |d| / avgdl)))
```

BM25 is strong when the query contains exact terms. In paper QA, terms such as `BGE-M3`, `BM25`, `RRF`, `alpha`, `beta`, `F1`, dataset names, and method names should not be replaced by approximate semantic matches. A sparse signal helps ensure that passages containing the exact evidence are included in the candidate set.

Sparse retrieval alone is not enough for Korean-query English-paper RAG because Korean questions may not share tokens with English passages. It is therefore used as a complementary signal rather than a replacement for dense retrieval.

### 3.4 Hybrid Retrieval and RRF

Hybrid retrieval combines dense and sparse retrieval to benefit from both semantic matching and exact token matching. One practical challenge is that dense and sparse scores are not directly comparable. Dense similarity may be bounded while BM25 scores vary by corpus and query. Reciprocal Rank Fusion (RRF) avoids score-scale mismatch by combining ranks instead of raw scores:

```text
RRF(d) = sum_i 1 / (k + rank_i(d))
```

Here, \(rank_i(d)\) is the rank assigned by retrieval system \(i\), and \(k\) is a smoothing constant. A passage ranked highly by both dense retrieval and BM25 receives a strong fused rank. A passage found by only one retriever can still survive if it is highly ranked.

In the fixed Paper-RAG backbone, hybrid retrieval is part of the frozen retrieval pipeline. HyDE is not part of the fixed backbone because it is one of the experimental axes. This separation lets the experiment ask whether HyDE improves evidence construction beyond the same dense/sparse/RRF backbone.

### 3.5 Reranking

The retriever produces candidate passages, but top-k retrieval scores may not align perfectly with answer usefulness. A reranker evaluates query-passage pairs more directly. Cross-encoder reranking encodes the query and passage together, allowing token-level interactions that a single vector comparison cannot capture:

```text
score_rerank(q, d) = CrossEncoder([q; d])
```

Reranking is especially useful for academic QA because a passage can contain the right terms but still not answer the question. For example, a method section may mention a dataset but not the result asked by the query. Reranking is therefore included in the fixed backbone and held constant across the HyDE/CAD/SCD matrix.

### 3.6 Context Construction

Context construction selects and formats retrieved evidence for the generator. It includes top-k selection, optional section filters, ordering, compression, and source metadata. A context that is too short may omit required evidence; a context that is too long may bury the answer or introduce irrelevant passages. The "Lost in the Middle" effect motivates careful context ordering because models can underuse evidence placed in the middle of long prompts.

For this thesis, context construction belongs to the fixed Paper-RAG backbone. The main experiment should not change context construction while measuring HyDE, CAD, and SCD. This prevents the analysis from confusing retrieval/generation-control effects with unrelated prompt construction changes.

### 3.7 RAG Hallucination

RAG hallucination occurs when a generated answer is unsupported by retrieved evidence. It can arise from retrieval failure, context noise, prompt ambiguity, or the model's parametric memory. This thesis focuses particularly on generation-side hallucination after evidence is retrieved. CAD addresses this by comparing the model's context-conditioned distribution with a no-context distribution. If a token is likely without the document but not especially supported by the document, CAD can reduce its relative probability.

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

Early RAG work established the principle of conditioning generation on retrieved documents. Later surveys and best-practice studies organized RAG pipelines into retrieval, augmentation, and generation stages, and studied practical choices such as chunk size, reranking, query expansion, and context length. This thesis uses that literature to justify a fixed Paper-RAG backbone rather than treating every pipeline choice as a main contribution.

### 4.2 Multilingual Dense Retrieval

Multilingual dense retrieval research shows that embedding models can map semantically related texts across languages into a shared vector space. BGE-M3 is the implemented multilingual embedding model used in the fixed Paper-RAG backbone. It is retained as an implementation reference because the system actually uses it for multilingual dense retrieval, not because this thesis treats BGE-M3 itself as a new contribution.

### 4.3 Sparse Retrieval and Rank Fusion

BM25 and RRF provide the sparse and rank-fusion foundations of the fixed backbone. BM25 contributes exact-term sensitivity, while RRF combines retrieval systems without requiring score calibration. These methods are not claimed as new contributions; they provide a stable retrieval baseline for the factor analysis.

### 4.4 Reranking and Passage Relevance

Cross-encoder reranking and passage-ranking benchmarks motivate a second-stage relevance model after initial retrieval. This is particularly important in academic documents because a passage may contain query terms but fail to answer the question. Reranking is therefore fixed in the backbone.

### 4.5 Query Reformulation and HyDE

HyDE generates a hypothetical answer-like document from a query and retrieves using that representation. The key intuition is that answer-like text can be closer to relevant documents than the original question form. This thesis does not propose HyDE itself. It evaluates HyDE as an on/off retrieval-side experimental factor in the Korean-query English-paper setting.

### 4.6 Context-Aware Decoding

CAD is related to contrastive decoding because it compares two distributions during generation. Instead of contrasting a strong model with a weak model, CAD contrasts the same model under context and no-context conditions. In this thesis, CAD is a decoding-time context-faithfulness factor for reducing parametric-memory intervention and improving evidence support.

### 4.7 Language Drift and Korean-Target Decoding

Recent AAAI 2026 Oral Paper work on multilingual RAG language drift characterizes unintended output-language shifts under cross-lingual evidence and proposes Soft Constrained Decoding (SCD), a training-free decoding strategy that penalizes non-target-language tokens. This thesis evaluates Korean-target SCD as a controlled decoding factor for Korean-query English-paper RAG, not as a general multilingual solution or as a new method introduced by this thesis.

### 4.8 Evaluation of RAG Answers

RAG evaluation commonly measures faithfulness, answer relevance, context precision, and context recall. RAGAS is used as an evaluation-design reference, but this draft does not claim that RAGAS execution has been performed. The repository separates a RAGAS-compatible future path from a lightweight local judge. This thesis uses the metric concepts while keeping result claims pending until verified experiment artifacts exist.

### 4.9 Methods Outside the Core Scope

Some related RAG research studies multi-query retrieval, hierarchical summarization, compression-specific retrieval, self-evaluation, graph-based retrieval, multimodal paper understanding, or agentic paper QA. These directions are relevant as background or future work, but they are not core implemented methods in this thesis. They must not be presented as part of the HyDE × CAD × SCD main experiment unless a later implementation audit explicitly changes the scope.

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

The thesis explicitly does not claim that the routed service architecture itself is a new RAG algorithm. The route layer is evaluated qualitatively as system integration and policy application.

## 6. System Overview

M-RAG has two layers.

The research layer is the fixed Paper-RAG backbone plus the HyDE × CAD × SCD matrix. It is implemented under the separated `experiments/` framework and should be executed only after parameter tuning, query split validation, and evaluation readiness checks.

The service layer is a FastAPI and React paper-review chatbot. It supports document upload, text extraction, chunking, vector indexing, retrieval, answer generation, source display, streaming, follow-up questions, citations, comparison, summaries, and quizzes. The service layer helps demonstrate the graduation-project application, but it is not the thesis novelty.

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

Dense and sparse candidates are fused with RRF. This avoids raw score calibration and allows both semantic and lexical candidates to contribute. RRF configuration is part of the fixed backbone.

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

In this thesis, HyDE is not treated as a new method. It is the retrieval-side experimental axis. The question is whether enabling it improves evidence support and answer relevancy under the same fixed backbone.

Expected analysis:

- HyDE may improve semantic recall for method and conceptual questions.
- HyDE may be less useful for exact numeric questions if the hypothetical text omits the exact number.
- HyDE may interact with CAD because better evidence construction gives CAD more useful context-conditioned signals.

### 8.2 CAD

CAD reduces parametric-memory intervention by contrasting context-conditioned and no-context model scores. Let \(s_c(y_t)\) be the score for token \(y_t\) conditioned on query, retrieved context, and generated prefix. Let \(s_0(y_t)\) be the score for the same token conditioned on the same query and generated prefix but without retrieved context. The exact contract used in this thesis is:

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

Expected analysis:

- CAD should reduce unsupported claims and numeric hallucination when relevant evidence exists.
- CAD may make generation more conservative.
- CAD should not change retrieval metrics directly; if context precision changes under CAD-only comparisons, the evaluation pipeline should be inspected.

### 8.3 SCD

SCD is Korean-target Soft Constrained Decoding, a training-free decoding strategy for mitigating language drift in multilingual RAG. It penalizes non-target-language tokens during generation while preserving neutral tokens and mandatory technical terms. Let \(V_{ko}\) be Korean target tokens, \(V_n\) neutral tokens, and \(V_w\) whitelisted technical tokens. Tokens outside these sets may receive a beta penalty:

```text
s_SCD(y_t) = s(y_t) - beta, if y_t not in V_ko ∪ V_n ∪ V_w
s_SCD(y_t) = s(y_t), otherwise
```

Neutral tokens include whitespace, punctuation, digits, brackets, math symbols, citation markers, and common academic symbols. The whitelist preserves terms such as `RAG`, `CAD`, `SCD`, `BM25`, `RRF`, `BGE-M3`, `HyDE`, `RAGAS`, `Transformer`, `CrossEncoder`, `Mi:dm`, `arXiv`, `DOI`, `BERT`, and other technical expressions.

SCD is not intended to translate every English term into Korean. Academic Korean naturally includes English method names and acronyms. This thesis evaluates Korean-target SCD as a controlled decoding factor for Korean-query English-paper RAG. The goal is to reduce unnecessary English sentence drift while preserving technical precision.

Expected analysis:

- SCD should reduce language drift rate and increase Korean answer ratio.
- SCD may harm answer naturalness if beta is too high or whitelist coverage is insufficient.
- SCD may interact with CAD because both operate at decoding time.

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

No main experiment has been executed in this draft. All tables are placeholders.

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

RAGAS is used as an evaluation-design reference. The repository separates a RAGAS-compatible future path from a lightweight local evaluator. This draft does not claim RAGAS package execution, OpenAI judging, or completed official results. Metrics remain planned until verified artifacts exist.

## 12. Result Tables

All tables in this section are TODO placeholders. No values should be filled until the approved experiment run is completed and checked.

### Table 1. Experimental Setup

| Item | Value |
|---|---|
| Task | Korean-query / English-paper RAG |
| Backbone | Fixed Paper-RAG retrieval backbone |
| Dense retrieval | TODO: fill configured model |
| Sparse retrieval | BM25 |
| Fusion | RRF |
| Reranking | TODO: fill configured reranker |
| Main factors | HyDE, CAD, SCD |
| Tuned only on | `tuning_queries` |
| Main query split | `decoder_main_queries` |
| Result status | TODO: pending verified run |

### Table 2. Main HyDE × CAD × SCD Factorial Ablation

| Config | Faithfulness | Evidence support | Numeric hallucination rate | Language drift rate | Korean answer ratio | Answer relevancy |
|---|---:|---:|---:|---:|---:|---:|
| `hyde_off__no_decoder_control` | TODO | TODO | TODO | TODO | TODO | TODO |
| `hyde_off__cad_only` | TODO | TODO | TODO | TODO | TODO | TODO |
| `hyde_off__scd_only` | TODO | TODO | TODO | TODO | TODO | TODO |
| `hyde_off__cad_scd` | TODO | TODO | TODO | TODO | TODO | TODO |
| `hyde_on__no_decoder_control` | TODO | TODO | TODO | TODO | TODO | TODO |
| `hyde_on__cad_only` | TODO | TODO | TODO | TODO | TODO | TODO |
| `hyde_on__scd_only` | TODO | TODO | TODO | TODO | TODO | TODO |
| `hyde_on__cad_scd` | TODO | TODO | TODO | TODO | TODO | TODO |

### Table 3. Effect Delta Summary

| Effect | Delta definition | Result |
|---|---|---|
| HyDE main effect | mean(HyDE on) - mean(HyDE off) | TODO |
| CAD main effect | mean(CAD on) - mean(CAD off) | TODO |
| SCD main effect | mean(SCD on) - mean(SCD off) | TODO |
| CAD × SCD interaction | combined decoder effect beyond additive expectation | TODO |
| HyDE × CAD interaction | retrieval expansion under context-aware decoding | TODO |
| HyDE × SCD interaction | retrieval expansion under Korean-target decoding | TODO |

### Table 4. Query-Type Breakdown

| Query type | Expected risk | HyDE effect | CAD effect | SCD effect | Policy implication |
|---|---|---|---|---|---|
| factual | missing exact evidence | TODO | TODO | TODO | TODO |
| numeric | unsupported numbers | TODO | TODO | TODO | TODO |
| method | semantic mismatch | TODO | TODO | TODO | TODO |
| section-specific | wrong section evidence | TODO | TODO | TODO | TODO |
| comparison | unbalanced evidence | TODO | TODO | TODO | TODO |
| summary | broad context coverage | TODO | TODO | TODO | TODO |

### Table 5. Numeric Hallucination and Evidence Support

| Config | Numeric exactness | Unsupported numeric claims | Evidence support | Notes |
|---|---:|---:|---:|---|
| 8-config matrix rows | TODO | TODO | TODO | TODO |

### Table 6. Language Drift and Korean Answer Ratio

| Config | Language drift rate | Korean answer ratio | Whitelist errors | Notes |
|---|---:|---:|---:|---|
| 8-config matrix rows | TODO | TODO | TODO | TODO |

### Table 7. Routed Policy for Graduation-Project System

| Service route | Query type | Derived HyDE policy | Derived CAD policy | Derived SCD policy | Status |
|---|---|---|---|---|---|
| A simple QA | factual / conceptual | TODO | TODO | TODO | service feature |
| B section QA | section-specific | TODO | TODO | TODO | service feature |
| C comparison | comparison | TODO | TODO | TODO | service feature |
| D citation / patent lookup | citation-oriented | TODO | TODO | TODO | service feature |
| E structured summary | summary | TODO | TODO | TODO | service feature |
| F quiz / flashcard | study support | TODO | TODO | TODO | service feature |

## 13. Discussion

The discussion should be written after the verified result tables are filled. This draft defines the analysis plan without claiming outcomes.

### 13.1 Interpreting HyDE

If HyDE improves context recall and answer relevancy, the discussion should explain whether the improvement is concentrated in semantic or method-description questions. If HyDE does not improve numeric questions, the discussion should examine whether hypothetical answers omit exact values or retrieve broader but less precise evidence.

### 13.2 Interpreting CAD

If CAD reduces unsupported claims or numeric hallucination, the discussion should connect the result to the contrast between context and no-context distributions. If CAD reduces answer relevancy or fluency, the discussion should consider whether alpha is too strong or whether evidence is insufficient.

### 13.3 Interpreting SCD

If SCD reduces language drift, the discussion should distinguish Korean sentence stability from technical-term preservation. If whitelist errors occur, the discussion should identify which terms or tokenization patterns require adjustment.

### 13.4 Interactions

CAD and SCD may complement each other because they target different failure modes. CAD targets evidence faithfulness, while SCD targets output language. However, both modify token scores, so interaction effects must be interpreted carefully. HyDE may also affect decoder controls by changing the quality of retrieved evidence.

### 13.5 Query-Type Policy

The final service policy should not simply enable every factor for every route. It should derive route-level defaults from query-type evidence. For example, numeric factual questions may prioritize CAD, while Korean-language stability questions may prioritize SCD. These are hypotheses until results are available.

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

However, the route layer is not presented as the thesis algorithm. It is a runtime architecture that applies the research findings. After the HyDE/CAD/SCD matrix is evaluated, Table 7 should translate query-type results into route-level defaults. This makes the service integration evidence-driven rather than claim-driven.

Runtime compatibility also matters. The service must preserve QueryRequest, QueryResponse, SSE streaming, paper APIs, citation APIs, and active document filtering. The thesis should mention these as engineering constraints, not as experimental variables.

## 15. Limitations and Future Work

### 15.1 Experiment Scope

The main experiment is limited to the selected paper corpus and query splits. Results may not generalize to all academic domains, all Korean users, or all English paper styles. A larger corpus and independently authored queries would strengthen external validity.

### 15.2 Evaluation Reliability

Automatic evaluation can misjudge faithfulness, relevance, or language drift. Lightweight local judging is useful for reproducibility but may be weaker than human evaluation. A future approved evaluation phase may compare local metrics, human checks, and RAGAS-compatible metrics.

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

No experimental results are claimed in this draft. The next thesis step is to run the approved tuning and main matrix workflow, fill the TODO tables from verified artifacts, and then write the discussion around observed effects, query-type patterns, and service-policy implications.

## 17. References

[1] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in Neural Information Processing Systems 33, 2020.

[2] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, Q. Guo, M. Wang, and H. Wang, "Retrieval-Augmented Generation for Large Language Models: A Survey," arXiv:2312.10997, 2023.

[3] J. Chen, S. Xiao, P. Zhang, K. Luo, D. Lian, and Z. Liu, "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation," arXiv:2402.03216, 2024.

[4] S. E. Robertson, S. Walker, S. Jones, M. M. Hancock-Beaulieu, and M. Gatford, "Okapi at TREC-3," in Proceedings of the Third Text REtrieval Conference (TREC-3), 1994.

[5] G. V. Cormack, C. L. A. Clarke, and S. Buettcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," in Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval, 2009.

[6] R. Nogueira and K. Cho, "Passage Re-ranking with BERT," arXiv:1901.04085, 2019.

[7] P. Bajaj et al., "MS MARCO: A Human Generated Machine Reading Comprehension Dataset," arXiv:1611.09268, 2016.

[8] L. Gao, X. Ma, J. Lin, and J. Callan, "Precise Zero-Shot Dense Retrieval without Relevance Labels," in Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 1762-1777, 2023.

[9] W. Shi, X. Han, M. Lewis, Y. Tsvetkov, L. Zettlemoyer, and W.-t. Yih, "Trusting Your Evidence: Hallucinate Less with Context-aware Decoding," in Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 2: Short Papers), pp. 783-791, 2024.

[10] X. L. Li, A. Holtzman, D. Fried, P. Liang, J. Eisner, T. Hashimoto, L. Zettlemoyer, and M. Lewis, "Contrastive Decoding: Open-ended Text Generation as Optimization," in Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics, 2023.

[11] B. Li, Z. Xu, and R. Xie, "Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation," AAAI 2026 Oral Paper, arXiv:2511.09984, 2025.

[12] S. Es, J. James, L. E. Anke, and S. Schockaert, "RAGAs: Automated Evaluation of Retrieval Augmented Generation," in Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations, pp. 150-158, 2024.

[13] N. F. Liu, K. Lin, J. Hewitt, A. Paranjape, M. Bevilacqua, F. Petroni, and P. Liang, "Lost in the Middle: How Language Models Use Long Contexts," Transactions of the Association for Computational Linguistics, 2024.

[14] D. Rau, H. Déjean, N. Chirkova, T. Formal, S. Wang, S. Clinchant, and V. Nikoulina, "BERGEN: A Benchmarking Library for Retrieval-Augmented Generation," in Findings of the Association for Computational Linguistics: EMNLP 2024, pp. 7640-7663, 2024.

[15] K-intelligence, "Mi:dm 2.0 Technical Report," 2025.

[16] 김범석, 양진홍, "RAG 시스템 성능 평가를 위한 자동 데이터 셋 생성 프레임워크 비교 분석 연구," 한국정보전자통신기술학회논문지, vol. 18, no. 2, 2025. TODO: verify bibliographic details.

[17] 김예은, 이재홍, 원상혁, 정우혁, 우지환, "HyDE 기반 멀티 홉 검색 기법을 활용한 검색 성능 향상 방안," 경영정보학연구, vol. 27, no. 2, 2025. TODO: verify bibliographic details.

[18] 장규식, 이현민, 나승훈, 김태형, 류휘정, "Contrastive CAD: 대형 언어 모델의 환각 완화를 위한 대조적 Context-Aware Decoding," 제36회 한글 및 한국어 정보처리 학술대회 논문집, 2024. TODO: verify bibliographic details.
