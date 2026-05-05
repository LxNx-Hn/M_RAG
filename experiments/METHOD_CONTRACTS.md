# Method Contracts

This file is the Phase 2 contract gate for CAD, SCD, RAGAS/evaluation, and runtime compatibility. It records the implementation rules before changing core method code.

## CAD Method Contract

- CAD means Context-Aware Decoding.
- The required scoring rule is:

```text
cad_scores(token) = (1 + alpha) * context_scores(token) - alpha * no_context_scores(token)
```

- `context_scores` are the scores produced by the normal generation branch conditioned on instruction/query, retrieved context, and generated prefix `y_<t`.
- `no_context_scores` are computed from the same instruction/query without retrieved context and with the exact same generated prefix `y_<t`.
- CAD is not prompt-only and must be wired into the generation `logits_processor` path.
- The default thesis path uses fixed `alpha`; adaptive alpha may exist as a non-thesis runtime option only when explicitly enabled.

## CAD KV Cache Correctness Rule

- Correctness comes from computing `p(y_t | x, y_<t)`, not from using KV cache.
- Phase 2 uses an uncached reference no-context path for correctness:
  - record the context prompt length on the first processor call;
  - slice the generated prefix from the context-branch `input_ids`;
  - concatenate the no-context prompt and that generated prefix;
  - compute no-context logits in one forward pass.
- This reference path guarantees the no-context branch consumes the same generated prefix `y_<t`.
- Unsupported batch or beam modes must be blocked until a parity-tested cache path exists.
- Future cache parity test design:
  - choose one no-context prompt and a fixed generated-prefix token sequence;
  - compute no-context logits with the uncached reference path;
  - compute no-context logits with a cached path that initializes on the prompt and consumes prefix tokens one by one;
  - assert matching logits within dtype-appropriate tolerance at each prefix length;
  - reset cache between independent generation calls.

## SCD Method Contract

- SCD means Soft Constrained Decoding.
- This thesis uses Korean-target Soft Constrained Decoding.
- Full multilingual SCD is future work only.
- At each decoding step:
  - Korean target-language tokens are not penalized;
  - neutral tokens are not penalized;
  - mandatory technical whitelist tokens are not penalized;
  - non-target tokens may receive a `beta` penalty.
- Neutral tokens include whitespace, punctuation, numbers, math symbols, citation markers, brackets, and common academic symbols.
- Mandatory technical whitelist:

```text
RAG, CAD, SCD, BM25, RRF, BGE-M3, HyDE, RAGAS, Transformer, CrossEncoder,
Mi:dm, arXiv, DOI, BERT, RoBERTa, LLaMA, GPT, FLAN, XSUM, CNN-DM
```

## RAGAS Evaluation Contract

- Official RAGAS must be a separate path from the lightweight/local judge.
- Official RAGAS input schema uses:
  - `question` / `user_input`
  - `answer` / `response`
  - `contexts` / `retrieved_contexts`
  - `ground_truth` / `reference` when a metric requires it.
- Supported official metric plan:
  - `faithfulness`
  - `response_relevancy` or `answer_relevancy`
  - `context_precision`
  - `context_recall`
- Phase 2 may create an official RAGAS skeleton with import guards and dry validation only.
- Phase 2 must not execute RAGAS, OpenAI, model calls, or network dependency installation.
- Lightweight/local judge code must be named `RAGASInspiredEvaluator` or `LightweightJudgeEvaluator`, not official RAGAS.

## Unsupported Method Removal Contract

- RAG-Fusion, RAPTOR, RECOMP, Self-RAG, FLARE, CRAG, GraphRAG, HippoRAG, ColPali, PaperQA, and SQuAI must not be claimed as core implemented methods in the new thesis path.
- Phase 2 only removes or reframes such wording where it is directly attached to core method code touched in this phase.
- Wider document synchronization belongs to Phase 5.

## Frontend-Derived Runtime Contract

- Preserve QueryRequest compatibility:
  - `query`
  - `collection_name`
  - `use_cad`
  - `cad_alpha`
  - `use_scd`
  - `scd_beta`
  - `use_hyde`
  - `top_k`
  - `doc_id_filter`
  - `section_filter`
  - `conversation_id` if migrated later.
- Preserve QueryResponse, RouteInfo, SourceDocument, SSE `metadata`/`token`/`done`/`error`, paper APIs, citation APIs, and active-paper targeting behavior.
- Do not expose the HyDE x CAD x SCD experiment matrix in the frontend.

## Service Runtime Route Preservation Contract

- A-F routes remain service features for the graduation-project paper-review chatbot.
- Method rewrites must not remove chat query, stream, search, paper, or citation endpoints.

## Compare Route Runtime Contract

- Compare route behavior is not rewritten in Phase 2 except import fixes.
- Phase 3 must implement the full target selection policy:

```text
explicit targets
-> activePaperId/doc_id_filter + title/doc_id match
-> activePaperId/doc_id_filter + embedding/retrieval fallback
-> query-aware top-2 selection
-> deterministic fallback
```

## Forbidden Claims Gate

- The following strings are forbidden as core implementation claims unless explicitly framed as related work, future work, audit notes, or contract warnings:

```text
Selective Context-aware Decoding
Selective Context Decoding
Selective CAD
RAG-Fusion
RAPTOR
RECOMP
Self-RAG
FLARE
CRAG
GraphRAG
HippoRAG
ColPali
PaperQA
SQuAI
Full System
official RAGAS
RAGAS로 평가
Modular RAG 방법론
new Modular RAG
새로운 Modular RAG
```

## Completion Criteria

- CAD exact formula is implemented or an explicit blocker is reported.
- CAD no-context branch is defined and consumes the same generated prefix as the context branch.
- CAD KV-cache correctness is handled by reference path or parity-test design.
- SCD is Korean-target Soft Constrained Decoding and has a mandatory whitelist.
- Official RAGAS skeleton exists and is separated from lightweight judge code.
- No model, OpenAI, RAGAS, GT regeneration, dependency installation, large experiment, or commit is performed in Phase 2.
