# M-RAG: System Implementation and HyDE × CAD × SCD Evaluation for Question Answering over English Academic Papers with Korean Queries

## 1. Abstract

Retrieval-Augmented Generation (RAG) retrieves external documents and conditions answer generation on the retrieved evidence. Korean question answering over English academic papers adds two challenges: retrieval must bridge the linguistic and stylistic gap between Korean queries and English scholarly prose, and generation must remain faithful to English evidence while producing a stable Korean answer. This thesis decomposes the problem into retrieval expansion, evidence-faithfulness control, and output-language control, and integrates the three functions into an implemented paper-question-answering system named M-RAG.

The investigated methods are Hypothetical Document Embeddings (HyDE), Context-Aware Decoding (CAD), and Korean-target Soft Constrained Decoding (SCD). HyDE expands the retrieval representation with a hypothetical answer-like document, CAD contrasts context-conditioned and no-context token distributions, and SCD applies language-specific coefficients to raw logits partitioned into target, distractor, and neutral tokens. The Paper-RAG backbone—BGE-M3, BM25, weighted Reciprocal Rank Fusion, and CrossEncoder reranking—and the Mi:dm 2.0 Base generator are held fixed. The eight on/off combinations are applied to 19 queries, producing 152 answers.

In a 19-query SCD-off baseline comparison, HyDE changes answer relevancy by `+0.0303` (95% CI `[+0.0016, +0.0615]`), while the faithfulness, context-precision, and context-recall intervals include or touch zero. In a HyDE-off and SCD-off comparison with byte-identical contexts for all 19 queries, CAD changes faithfulness by `+0.0023` (95% CI `[−0.0903, +0.0952]`), providing no clear quality improvement. SCD raises the Korean-character ratio by `+0.2203` over 76 matched pairs, with 68 improvements. Outputs below the 0.5 threshold decrease from 26 to 12, and the mean difference is positive in all four HyDE × CAD strata. It remains `+0.2198` over 38 HyDE-off pairs with byte-identical contexts.

M-RAG implements paper upload, hybrid retrieval, reranking, answer generation, source display, streaming, comparison, summarization, citation support, and quiz generation through a FastAPI backend, a React frontend, and six A–F query routes. Research runners explicitly compose HyDE, CAD, and SCD, while the service routes expose module-selection points required by their functions. The study implements one 2×2×2 generation matrix and evaluates each method through controlled contrasts and target-specific measurements within the same codebase.

**Keywords:** Retrieval-Augmented Generation, academic question answering, HyDE, Context-Aware Decoding, Soft Constrained Decoding, Korean, language drift, RAGAS

## 2. Introduction

Academic papers contain functionally different sections such as abstract, introduction, method, experiment, result, limitation, and references. A numeric question needs evidence from a result section, a method question needs methodological context, a comparison question requires balanced evidence from multiple papers, and a citation-oriented question must preserve bibliographic links.

RAG supplies external documents to a generator, but successful retrieval alone does not guarantee answer quality. Multilingual dense retrieval can connect a Korean query to an English passage while missing exact numbers, acronyms, or model names. Sparse retrieval preserves surface matches but is weaker for cross-lingual semantic paraphrases. Even with relevant evidence, a generator may prefer parametric memory, add unsupported claims, or continue in English because the retrieved context is English.

This study separates retrieval and generation control into three factors:

- **HyDE:** expands the query into a hypothetical answer-like document to control English-paper retrieval.
- **CAD:** contrasts the same model under context and no-context conditions to suppress generation that is weakly supported by the paper.
- **SCD:** partitions the vocabulary into Korean target tokens, non-target distractor tokens, and symbol-oriented neutral tokens, then applies fixed coefficients to their raw logits.

The research layer executes the 2×2×2 combinations and analyzes controlled contrasts with method-specific target measurements. The system layer provides paper-QA functions and module-selection points in the same codebase. The thesis therefore treats combination evaluation, result interpretation, and system implementation as one coherent workflow.

## 3. Background

### 3.1 Retrieval-Augmented Generation

For a query `q`, RAG retrieves a context `Cq` from a document collection `D` and generates an answer `y` conditioned on the query and context [1].

```text
y = LM(q, Cq)
```

Missing evidence cannot be used by the generator, while retrieved evidence can still be ignored. Retrieval-side and decoding-side controls therefore require separate measurements.

### 3.2 Dense, Sparse, and Hybrid Retrieval

BGE-M3 represents Korean queries and English passages in a shared multilingual vector space [3]. BM25 complements semantic retrieval with exact lexical matching for terminology, numbers, and acronyms [4]. M-RAG combines the two rankings with dense 0.6 and BM25 0.4 weighted Reciprocal Rank Fusion [5].

```text
weighted_RRF(d) = 0.6 / (k + rank_dense(d))
                + 0.4 / (k + rank_BM25(d))
```

Candidate passages are reranked with the `ms-marco-MiniLM-L-6-v2` CrossEncoder [6,7].

### 3.3 HyDE

HyDE embeds a hypothetical answer-like document rather than the original query alone [8]. It can narrow the representational gap between a Korean question and English academic prose, but an over-expanded hypothetical document can also introduce off-target evidence.

### 3.4 CAD

CAD contrasts token scores under context and no-context conditions [9].

```text
score_CAD = (1 + alpha) * logits_context - alpha * logits_no_context
```

Tokens that become more likely in the presence of the retrieved evidence are prioritized over tokens that the model would generate without the evidence. The implementation recomputes the no-context branch with the same generated prefix at every step.

### 3.5 SCD and Language Drift

SCD is a training-free decoding method for mitigating language drift in multilingual RAG [11]. The implementation multiplies Korean-target raw logits by `alpha=1.1` and non-target distractor raw logits by `beta=0.9` after a generated-token warm-up of `Tstart=5`. Its purpose is to prevent the main Korean narrative from unnecessarily switching to sentences in another language.

## 4. Related Work

Lewis et al. [1] establish the basic structure of retrieval-conditioned generation, and a RAG survey [2] summarizes design choices across retrieval, augmentation, and generation. BGE-M3 [3], BM25 [4], RRF [5], and BERT reranking [6] form the evidence base of the fixed retrieval backbone. MS MARCO [7] is a representative passage-ranking resource. Lost-in-the-Middle [13] motivates careful context construction, and BERGEN [14] demonstrates reproducible benchmarking infrastructure for RAG.

HyDE [8] uses hypothetical documents for zero-shot dense retrieval; Korean work also studies HyDE-based multi-hop retrieval [17]. CAD [9] and contrastive decoding [10] control generation by contrasting distributions, and Korean Contrastive CAD research [18] explores the same general direction. Li et al. [11] characterize multilingual RAG language drift and propose SCD. The current work applies these methods as factors in Korean-query English-paper RAG. Mi:dm 2.0 provides the Korean-centric bilingual generation backbone [15]. RAGAS [12] evaluates faithfulness, answer relevancy, context precision, and context recall; Korean evaluation research also studies automatic dataset generation for RAG [16]. Because multilingual LLM judges can vary by language [20], this thesis prioritizes paired effects under fixed conditions and direct language measurements.

## 5. Problem Definition and Research Questions

Let `q_ko` be a Korean query, `D_en` a collection of English-paper chunks, `C` the retrieved context, and `y_ko` the target Korean answer. A successful system should retrieve relevant evidence, generate faithful and relevant answers, and maintain Korean output stability.

- **RQ1:** With CAD and SCD disabled, how does HyDE change end-to-end RAG quality?
- **RQ2:** With HyDE and SCD disabled and retrieved contexts held identical, how does CAD change answer quality?
- **RQ3:** Does Korean-target SCD reduce language drift across the HyDE × CAD combinations?
- **RQ4:** What quality and language trade-offs appear when the three factors are combined?
- **RQ5:** How are the three methods and A–F query functions implemented in the M-RAG codebase?

HyDE and CAD report faithfulness, answer relevancy, context precision, and context recall through controlled 19-query contrasts. SCD uses the direct Korean-character ratio and language-drift rate as primary measurements, with faithfulness and answer relevancy checked separately in matched-context symmetric panels.

## 6. System Overview

![M-RAG system overview](figures/system_overview.svg)

**Figure 1.** Research and service layers of M-RAG. The research layer evaluates HyDE × CAD × SCD combinations, and the service layer implements six paper-QA routes.

The research layer consists of the fixed Paper-RAG backbone, generation runners, RAGAS evaluators, and language-adherence analyzers under `experiments/`. The service layer uses FastAPI and React to provide paper upload, text extraction, chunking, indexing, hybrid retrieval, reranking, answer generation, SSE streaming, source display, follow-up questions, citation support, comparison, summarization, and quiz generation.

Documents are parsed, section-detected, chunked, and stored in dense and sparse indexes. Each user request follows its service route through retrieval, reranking, context construction, and generation. Research runners use the same module implementations while explicitly fixing the HyDE, CAD, and SCD settings required by the experiment.

## 7. Fixed Paper-RAG Backbone

The following components remain fixed throughout the experiment:

- Dense retrieval: BGE-M3
- Sparse retrieval: BM25
- Fusion: dense 0.6 / BM25 0.4 weighted RRF
- Reranking: `ms-marco-MiniLM-L-6-v2`
- Retrieval pool: 8
- Rerank top-n: 8
- Generation context: 5 passages
- Generation model: `K-intelligence/Midm-2.0-Base-Instruct`
- Decoding: greedy, maximum 512 tokens

Retrieval methods and the generation model are held constant outside the HyDE, CAD, and SCD settings. Quality interpretation is restricted to contrasts whose context and scoring-input conditions have been audited.

## 8. Combination Evaluation Method

![HyDE CAD SCD combination design](figures/factorial_design.svg)

**Figure 2.** Eight combinations of the three binary methods. Fixed inputs and backbone settings produce 152 answers for 19 queries; the symmetric quality analysis uses the 38 HyDE-off matched pairs from this matrix.

### 8.1 HyDE

In the HyDE-on condition, the Korean query is expanded into an English academic answer-like document and embedded with BGE-M3. Dense and BM25 candidates, weighted RRF, and CrossEncoder reranking are otherwise identical to the HyDE-off condition.

### 8.2 CAD

CAD computes context-conditioned and no-context logits for the same generation prefix and contrasts them with `alpha=0.5`. CAD modifies generation scores without modifying retrieval results.

### 8.3 SCD

After generated step `Tstart=5`, SCD applies the following rule to raw logits:

```text
z'_i = z_i,          if generated step t < Tstart
z'_i = alpha * z_i,  if t >= Tstart and i is a Korean target token
z'_i = z_i,          if t >= Tstart and i is neutral
z'_i = beta * z_i,   if t >= Tstart and i is a non-target distractor token
```

The parameters are `alpha=1.1` and `beta=0.9`. Whitespace, punctuation, digits, mathematical symbols, brackets, and citation markers are neutral. General English technical terms are not protected by a separate neutral whitelist. When CAD and SCD are combined, the processor order is fixed.

## 9. Experimental Design

**Table 1. The 2×2×2 HyDE × CAD × SCD generation settings**

| Configuration | HyDE | CAD | SCD |
|---|---:|---:|---:|
| `hyde_off__no_decoder_control` | off | off | off |
| `hyde_off__cad_only` | off | on | off |
| `hyde_off__scd_only` | off | off | on |
| `hyde_off__cad_scd` | off | on | on |
| `hyde_on__no_decoder_control` | on | off | off |
| `hyde_on__cad_only` | on | on | off |
| `hyde_on__scd_only` | on | off | on |
| `hyde_on__cad_scd` | on | on | on |

The `decoder_main_queries` split contains 19 Korean questions over four English papers. Executing all eight configurations produces 152 answers and 76 matched SCD-on/off pairs. Tuning queries are not reused in this evaluation, and queries are not duplicated to inflate the sample size.

The methods are analyzed through complementary contrasts within one generation matrix:

1. **HyDE quality contrast:** the 19 HyDE on/off pairs with CAD and SCD disabled estimate the end-to-end HyDE effect, including retrieval changes.
2. **CAD quality contrast:** the 19 CAD on/off pairs with HyDE and SCD disabled use identical contexts, retrieval IDs, and reranking IDs.
3. **SCD language contrast:** 76 SCD on/off pairs are matched by query, HyDE, and CAD across the eight settings.
4. **Symmetric SCD quality contrast:** 38 HyDE-off SCD pairs with byte-identical contexts are normalized into English and Korean panels and evaluated by two judges with paired bootstrap intervals.

## 10. Evaluation Method

RAGAS 0.2.15 measures faithfulness, answer relevancy, context precision, and context recall [12]. From the artifact containing `gpt-4o` scores [19] for all 152 answers, the quality contrasts use only SCD-off records and local BGE-M3 embeddings; all 608 metric cells in the full artifact are valid. For each contrast, the same 19 query IDs are resampled 200,000 times in a paired percentile bootstrap to calculate 95% intervals. NumPy 1.26.4 `default_rng(20260713)` generates one 200,000×19 resampling-index matrix that is reused for every metric and contrast; linear quantiles are used. Wins and losses require deltas above `+0.01` and below `−0.01`, respectively; all other pairs are ties.

The primary SCD measurement is the direct Korean-character ratio, which does not use an LLM judge. It divides the number of Hangul characters by the combined number of Hangul and ASCII alphabetic characters. An answer below 0.5 is classified as language drift. SCD-on and SCD-off outputs are paired by query, HyDE condition, and CAD condition.

For the symmetric quality contrast, the 38 HyDE-off pairs are verified to have byte-identical retrieved contexts. The same score-independent normalization rules are applied to question, answer, reference, and context for English and Korean panels. `gpt-4o` and fixed `gpt-4.1-2025-04-14` serve as judges, and 95% intervals are calculated with 10,000 query-clustered paired bootstrap resamples. SCD-on scores are not mixed into the HyDE and CAD quality contrasts; SCD quality is assessed separately in these symmetric panels.

Numeric hallucination rate and query-type-specific effects are not included because the run does not contain dedicated numeric annotations or sufficiently large per-type samples.

## 11. Experimental Results

### 11.1 Controlled HyDE and CAD Quality Contrasts

**Table 2. Controlled HyDE and CAD contrasts from the 2×2×2 generation matrix (n=19 each)**

| Contrast | Metric | Paired delta [95% CI] | Win/loss/tie |
|---|---|---:|---:|
| HyDE on−off<br>(CAD off, SCD off) | faithfulness | `+0.0734 [−0.0248, +0.1777]` | 9/6/4 |
|  | answer relevancy | `+0.0303 [+0.0016, +0.0615]` | 9/3/7 |
|  | context precision | `−0.0679 [−0.1702, +0.0194]` | 7/6/6 |
|  | context recall | `−0.0526 [−0.1579, 0.0000]` | 0/1/18 |
| CAD on−off<br>(HyDE off, SCD off) | faithfulness | `+0.0023 [−0.0903, +0.0952]` | 7/9/3 |
|  | answer relevancy | `−0.0715 [−0.1792, +0.0004]` | 5/12/2 |
|  | context precision | `−0.0022 [−0.0447, +0.0322]` | 2/1/16 |
|  | context recall | `−0.0526 [−0.1579, 0.0000]` | 0/1/18 |

With CAD and SCD disabled, HyDE produces a small answer-relevancy increase whose interval excludes zero. The faithfulness mean is positive and the context-precision and context-recall means are negative, but these three intervals include or touch zero. In the byte-identical-context CAD contrast, the faithfulness difference is only `+0.0023`, and all four intervals include zero. Because CAD does not change retrieval inputs, nonzero context-metric differences in this identical-context contrast are treated as judge variation rather than decoder effects. This sample therefore does not establish a CAD quality improvement.

### 11.2 SCD Language Adherence by Configuration

**Table 3. Mean Korean-character ratio and language-drift count by setting**

| Configuration | Mean Korean ratio | Drift count (<0.5) |
|---|---:|---:|
| `hyde_off__no_decoder_control` | 0.5088 | 8/19 |
| `hyde_off__cad_only` | 0.5175 | 8/19 |
| `hyde_off__scd_only` | 0.7069 | 4/19 |
| `hyde_off__cad_scd` | 0.7590 | 3/19 |
| `hyde_on__no_decoder_control` | 0.6023 | 3/19 |
| `hyde_on__cad_only` | 0.5099 | 7/19 |
| `hyde_on__scd_only` | 0.8035 | 2/19 |
| `hyde_on__cad_scd` | 0.7501 | 3/19 |

Across all 76 matched pairs, the mean SCD-on minus SCD-off Korean-ratio difference is `+0.2203`. Sixty-eight pairs improve by more than `+0.02`, three decline by more than `−0.02`, and five remain within that band. Drift decreases from 26/76 SCD-off outputs to 12/76 SCD-on outputs. Fifteen of the 26 drifting baselines cross the 0.5 threshold, while one pair crosses in the opposite direction.

The mean deltas in the four HyDE × CAD strata are `+0.1981`, `+0.2415`, `+0.2012`, and `+0.2402`; all are positive. The mean difference is `+0.2198` over the 38 HyDE-off pairs with byte-identical retrieved contexts.

### 11.3 Symmetric SCD Quality Check

**Table 4. Judge- and language-specific quality differences for matched-context SCD pairs**

| Judge | Target | Faithfulness delta [95% CI] | Answer relevancy delta [95% CI] |
|---|---|---:|---:|
| `gpt-4o` | English | `+0.0071 [−0.0596, +0.0714]` | `−0.0910 [−0.1725, −0.0240]` |
| `gpt-4o` | Korean | `−0.0283 [−0.1044, +0.0510]` | `−0.0752 [−0.1501, −0.0138]` |
| `gpt-4.1-2025-04-14` | English | `−0.0579 [−0.1322, +0.0060]` | `−0.0327 [−0.0851, +0.0129]` |
| `gpt-4.1-2025-04-14` | Korean | `−0.0326 [−0.0997, +0.0226]` | `−0.0356 [−0.1149, +0.0315]` |

All four faithfulness intervals include zero. Mean answer-relevancy differences are negative in all four panels, but nonzero intervals appear only under `gpt-4o`. The direct language-control effect is established, whereas a nonzero quality difference does not replicate across the two judges.

### 11.4 Joint Interpretation

HyDE yields a small answer-relevancy improvement in the baseline contrast, while the directions of the other quality metrics remain unresolved. The identical-context CAD contrast does not establish a quality improvement. In contrast, the Korean-ratio difference from SCD is positive in all four HyDE × CAD strata. The results do not support a single always-on configuration: SCD is appropriate when Korean output control is required, while HyDE and CAD require task-specific validation.

## 12. M-RAG System Implementation

The backend entry point is `backend/api/main.py`. FastAPI endpoints expose paper, query, user, citation, and export functions. Modules under `backend/modules/` implement parsing, section detection, embedding, hybrid retrieval, reranking, HyDE, CAD, SCD, and follow-up generation. Pipelines under `backend/pipelines/` compose the A–F query flows. The Vite, React, and TypeScript frontend provides paper viewing, chat, source navigation, and streaming responses. Research runners explicitly pass the evaluated SCD formula and parameters, while service pipelines expose route-specific HyDE, CAD, and SCD enable/disable points.

**Table 5. Current A–F service routes and module-selection points**

| Route | Service purpose | Selection points implemented in code |
|---|---|---|
| A | Simple QA | Optional HyDE, CAD, and SCD |
| B | Section-focused QA | Optional HyDE, CAD, and SCD |
| C | Paper comparison | Optional CAD and SCD |
| D | Citation and bibliography | Optional CAD and SCD |
| E | Structured summarization | Optional CAD and SCD |
| F | Quiz and flashcards | Optional HyDE, CAD, and SCD |

Table 5 summarizes current function arguments and processor connections; it is not a route-specific optimum. Module selection for each A–F query type requires a sufficiently large type-specific evaluation set.

## 13. Discussion

The baseline HyDE contrast shows a small positive answer-relevancy difference. The faithfulness and context-precision intervals include zero, and the context-recall interval reaches zero, so the sample does not support a broad retrieval-quality improvement. The context changes between HyDE on and off represent the intended end-to-end retrieval effect of query expansion.

The CAD contrast holds retrieved context identical for all 19 queries and therefore focuses on decoding changes. Nevertheless, all four intervals, including faithfulness, contain zero. CAD also evaluates a no-context branch at each generated token, so its added inference cost must be considered without a demonstrated quality gain in this sample.

SCD produces the largest direct difference in Korean adherence and preserves a positive direction across all HyDE × CAD combinations. A similar magnitude remains in the 38 HyDE-off pairs with identical contexts, showing that output language can be adjusted at decoding time when the evidence is English. Digits, formulas, punctuation, and citation markers are neutral, but general English technical terms are not protected by a separate whitelist.

Together, the results show the need to validate each module rather than assume a universally optimal configuration. SCD has an established language-control effect, while HyDE and CAD quality effects remain bounded by the controlled comparisons in this sample. M-RAG provides a structure in which these functions can be selected independently.

## 14. Limitations and Future Work

The experiment is limited to four English papers and 19 Korean queries, and each HyDE or CAD quality contrast contains 19 pairs. Additional academic domains and independently authored queries are required to test external validity. RAGAS quality scores depend on the LLM judge, and the answer-relevancy intervals in the symmetric SCD panels differ by judge. Independent-provider evaluation and blinded human review would strengthen quality interpretation.

In HyDE-on cells, hypothetical documents were regenerated independently across settings, so CAD on/off contexts were not sufficiently identical. The CAD quality conclusion is therefore restricted to the fully matched HyDE-off contrast. Numeric hallucination and query-type-specific effects are not measured because dedicated annotations and sufficiently large per-type samples are unavailable. CAD adds inference cost through its no-context branch, and SCD depends on tokenizer-specific subword composition. The service layer also requires route-specific optimization, load testing, observability, and deployment validation.

## 15. Conclusion

This thesis executes the 2×2×2 combinations of HyDE, CAD, and SCD for Korean-query question answering over English academic papers and implements them in the M-RAG research and service codebase. In a controlled 19-query contrast, HyDE changes answer relevancy by `+0.0303`, while the other quality intervals include or touch zero. In the byte-identical-context CAD contrast, faithfulness changes by `+0.0023`, and no quality improvement is established. SCD raises the Korean-character ratio by `+0.2203` over 76 matched pairs, reduces drifting outputs from 26 to 12, and produces a positive mean difference in all four HyDE × CAD strata.

The SCD language result remains in 38 matched-context pairs, while the symmetric quality check finds no nonzero quality difference that replicates across judges. The service routes provide integration and enable/disable points for the three methods, while the evaluated SCD setting is reproduced by the research runner. By using only auditable controlled contrasts from one generation matrix, the study presents the implementation and combination-specific behavior of Korean academic RAG.

## 16. References

[1] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS 33, 2020.

[2] Y. Gao et al., "Retrieval-Augmented Generation for Large Language Models: A Survey," arXiv:2312.10997, 2023.

[3] J. Chen et al., "M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation," Findings of ACL 2024, pp. 2318-2335, doi:10.18653/v1/2024.findings-acl.137.

[4] S. E. Robertson et al., "Okapi at TREC-3," TREC-3, 1994.

[5] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," SIGIR 2009, pp. 758-759, doi:10.1145/1571941.1572114.

[6] R. Nogueira and K. Cho, "Passage Re-ranking with BERT," arXiv:1901.04085, 2019.

[7] P. Bajaj et al., "MS MARCO: A Human Generated Machine Reading Comprehension Dataset," arXiv:1611.09268, 2016.

[8] L. Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Labels," ACL 2023, pp. 1762-1777, doi:10.18653/v1/2023.acl-long.99.

[9] W. Shi et al., "Trusting Your Evidence: Hallucinate Less with Context-aware Decoding," NAACL 2024, pp. 783-791, doi:10.18653/v1/2024.naacl-short.69.

[10] X. L. Li et al., "Contrastive Decoding: Open-ended Text Generation as Optimization," ACL 2023, pp. 12286-12312, doi:10.18653/v1/2023.acl-long.687.

[11] B. Li, Z. Xu, and R. Xie, "Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation," AAAI, vol. 40, no. 37, pp. 31519-31526, 2026, doi:10.1609/aaai.v40i37.40417.

[12] S. Es et al., "RAGAs: Automated Evaluation of Retrieval Augmented Generation," EACL 2024 System Demonstrations, pp. 150-158, doi:10.18653/v1/2024.eacl-demo.16.

[13] N. F. Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," TACL, vol. 12, pp. 157-173, 2024, doi:10.1162/tacl_a_00638.

[14] D. Rau et al., "BERGEN: A Benchmarking Library for Retrieval-Augmented Generation," Findings of EMNLP 2024, pp. 7640-7663, doi:10.18653/v1/2024.findings-emnlp.449.

[15] D. Shin et al., "Mi:dm 2.0 Korea-centric Bilingual Language Models," arXiv:2601.09066, 2026.

[16] B. Kim and J. Yang, "A Comparative Analysis of Automatic Dataset Generation Frameworks for RAG System Performance Evaluation," Journal of the Korea Institute of Information and Electronic Communication Technology, vol. 18, no. 2, pp. 143-154, 2025, doi:10.17661/jkiiect.2025.18.2.143.

[17] Y. Kim et al., "Improving Retrieval Performance Using HyDE-Based Multi-Hop Retrieval," Information Systems Review, vol. 27, no. 2, pp. 127-148, 2025, doi:10.14329/isr.2025.27.2.127.

[18] G. Jang et al., "Contrastive CAD: Contrastive Context-Aware Decoding for Mitigating Hallucinations in Large Language Models," HCLT-KACL 2024, 2024.

[19] OpenAI, "GPT-4o System Card," arXiv:2410.21276, 2024.

[20] X. Fu and W. Liu, "How Reliable is Multilingual LLM-as-a-Judge?", Findings of EMNLP 2025, pp. 11040-11053, doi:10.18653/v1/2025.findings-emnlp.587.
