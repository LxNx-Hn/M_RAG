# Query-Type Grouping Design

Group main-matrix samples by `normalized_query_type` from
`experiments/data/query_audit.json`.

Planned groups:

- `simple_qa`
- `section_method`
- `section_result`
- `section_abstract`
- `numeric_or_factual_hallucination`
- `citation_query`
- `crosslingual_ko`
- `decoder_ablation`

The analyzer should report per-config deltas within each group after real
results exist. Phase 4 creates no result values.

