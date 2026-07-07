# Sample-Level Result Schema

Allowed `experiment` values:

- `main-hyde-cad-scd`
- `final-eval`
- `appendix-sanity`

Allowed `config_name` values:

- `hyde_off__no_decoder_control`
- `hyde_off__cad_only`
- `hyde_off__scd_only`
- `hyde_off__cad_scd`
- `hyde_on__no_decoder_control`
- `hyde_on__cad_only`
- `hyde_on__scd_only`
- `hyde_on__cad_scd`

Required sample fields:

```json
{
  "query_id": "string",
  "query": "string",
  "query_type": "string",
  "paper": "string",
  "paper_language": "en|ko|mixed|unknown",
  "experiment": "main-hyde-cad-scd|final-eval|appendix-sanity",
  "config_id": "string",
  "config_name": "hyde_off__no_decoder_control",
  "model_tier": "mini|base",
  "model_name": "string",
  "judge_model": "string|null",
  "official_ragas": false,
  "lightweight_judge": false,
  "fixed_backbone": {
    "dense": "BGE-M3 or configured dense retriever",
    "bm25": true,
    "rrf": true,
    "reranker": true
  },
  "retrieval_reformulation": {
    "hyde": false,
    "hyde_mode": "off|on",
    "translated_query": null,
    "hyde_query": null,
    "hyde_document": null,
    "hyde_corpus_lang": null,
    "hyde_generation_settings": {
      "method": "generate_simple",
      "model_name": "string|null",
      "max_new_tokens": 512,
      "temperature": 0.1,
      "top_p": 0.9,
      "do_sample": true,
      "force_greedy": false
    }
  },
  "decoder": {
    "cad": false,
    "scd": false,
    "cad_alpha": 0.5,
    "scd_beta": 0.3,
    "cad_mode": "exact",
    "scd_mode": "korean-target"
  },
  "answer": "string",
  "ground_truth": "string",
  "raw_gt": "string",
  "normalized_gt": "string",
  "contexts": [
    {
      "chunk_id": "string",
      "paper": "string",
      "section": "string",
      "text": "string",
      "score": 0.0,
      "retrieval_source": "dense|bm25|rrf|hyde"
    }
  ],
  "scores": {
    "faithfulness": null,
    "answer_relevancy": null,
    "context_precision": null,
    "context_recall": null,
    "numeric_hallucination_rate": null,
    "language_drift_rate": null,
    "korean_answer_ratio": null,
    "evidence_support": null,
    "answer_span_hit_at_k": null
  },
  "not_found": false,
  "errors": []
}
```
