# Phase 8 — Parameter Freeze & Provenance Summary

End-to-end chain from tuning to the scored main experiment, with the artifacts
and commits that make each step reproducible. The judge
(`nvidia_nim / meta/llama-3.3-70b-instruct`) is fixed throughout; no OpenAI, no
GT regeneration, no query generation.

## Provenance chain

```
tuning generation (7.6C v2, Alice A100 80GB)
  15 records = 5 tuning queries × 3 retrieval-breadth profiles, inline contexts
  -> experiments/results/tuning/phase8_tuning_comparison_15records_v2.jsonl
        │  official NIM scoring (2 identical passes, merged; nulls 20->6)
        ▼
tuning scores
  -> experiments/results/evaluation/phase8_tuning_comparison_15records_v2.ragas_scores.json
        │  freeze decision (prepare_parameter_freeze.py, hard-gated)
        ▼
frozen_params.yaml  (status: frozen, commit f081430)
        │  run_generation.py --execute (fail-closed gates)
        ▼
main generation (Alice A100 80GB, commit e283ea1)
  152 records = 19 decoder_main queries × 8 HyDE/CAD/SCD configs
  -> experiments/results/main_generation/main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl
        │  official NIM scoring (multi-pass, per-metric targeted retries, merged)
        ▼
main scores  (583/608 cells scored)
  -> experiments/results/evaluation/main-hyde-cad-scd__decoder_main_queries__main_generation.ragas_scores.json
        │  aggregate_main_scores.py
        ▼
config table + axis effects
  -> experiments/results/analysis/{main_config_scores.csv, main_axis_effects.json}
```

## Freeze decision

Tuning scores per profile (NIM judge):

| Profile | pool/rerank/ctx | faithfulness | context_recall |
|---|---|---|---|
| current_defaults | 20/5/5 | 0.852 | 1.000 |
| retrieval_conservative | 3/3/3 | 0.810 | 1.000 |
| **retrieval_recall_oriented** | **8/8/5** | **0.917** | 1.000 |

Rule (pre-registered in the freeze-readiness report): primary objective =
mean faithfulness subject to a context-recall floor (best recall − 0.05 = 0.95);
ties within 0.02 faithfulness broken toward the repo default then the more
conservative `rerank_top_n`.

Outcome: **retrieval_recall_oriented** selected — highest faithfulness (0.917),
all profiles clear the recall floor (1.000), no tie. This is a **retrieval-breadth**
choice; it does not select away any HyDE/CAD/SCD axis.

## Frozen values (`experiments/configs/frozen_params.yaml`, commit f081430)

| Group | Parameter | Frozen value | Basis |
|---|---|---|---|
| retrieval | retrieval_pool_top_k | 8 | selected profile |
| retrieval | rerank_top_n | 8 | selected profile |
| retrieval | context_chunk_count | 5 | selected profile |
| decoder | cad_alpha | 0.5 | planned default (unswept) |
| decoder | scd_beta | 0.3 | planned default (unswept) |
| generation | max_new_tokens | 512 | planned default (unswept) |
| generation | decoding_mode | deterministic greedy | planned default (unswept) |
| generation | model | K-intelligence/Midm-2.0-Base-Instruct | thesis default |

Provenance recorded inside the file: `judge_provider: nvidia_nim`,
`judge_model: meta/llama-3.3-70b-instruct`, source score file, source
generation file, and the per-profile scores that drove the decision.

## Order guarantee

Freeze preceded main generation (frozen file committed at `f081430`, main
generation at `e283ea1`). `run_generation.py --execute` refuses to run without a
`status: frozen` file, so the main experiment could not have used post-hoc
parameters.
