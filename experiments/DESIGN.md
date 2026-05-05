# Phase 4 Experiment Design

## Core Direction

The main research contribution is the HyDE/CAD/SCD factor analysis under a
fixed Paper-RAG backbone for Korean questions over English/mixed academic
papers. The routed service system remains a graduation-project integration
layer, not the research novelty.

## Fixed Backbone

The fixed backbone uses dense retrieval, sparse retrieval, rank fusion, and
reranking. HyDE is deliberately excluded from the fixed backbone because it is a
main experimental axis.

Frozen after tuning:

- `top_k`
- `rerank_top_n`
- `cad_alpha`
- `scd_beta`
- HyDE prompt/template
- generation settings

The main matrix varies only HyDE, CAD, and SCD.

## Query Assets

Existing Track 1 and Track 2 query assets are audited into
`experiments/data/query_audit.json`. Track 1 concrete queries are split into
tuning, main, query-type analysis, and candidate final-eval groups. Track 2
records are treated as templates requiring answerability validation before final
evaluation.

## Safety

Dry-run scripts perform static checks, matrix validation, split leakage checks,
and cost estimation only.

