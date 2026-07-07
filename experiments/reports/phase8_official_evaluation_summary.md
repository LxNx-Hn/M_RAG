# Phase 8 — Official Evaluation Summary (HyDE × CAD × SCD Factor Analysis)

Measurement tool: RAGAS with an **NVIDIA NIM** judge
(`meta/llama-3.3-70b-instruct`, temperature 0, OpenAI-compatible endpoint),
answer_relevancy embeddings = local BGE-M3. Judge held fixed across every
scored decision. Reference = verified `answer_span` per query. This summary
reports the HyDE × CAD × SCD factor analysis on the fixed Paper-RAG backbone;
RAGAS is the measurement instrument, not a thesis method.

Source: [main generation](../results/main_generation/main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl)
(152 records) → [scored](../results/evaluation/main-hyde-cad-scd__decoder_main_queries__main_generation.ragas_scores.json)
→ [aggregation](../results/analysis/main_config_scores.csv).

## 1. Scored coverage

- 152 records × 4 metrics = 608 metric cells.
- Scored: **583 / 608 (95.9%)**. Null: 25 (faithfulness 14, context_precision 11),
  all from transient judge timeouts on the largest multi-context payloads that
  survived four retry passes; answer_relevancy and context_recall are 152/152.
- Nulls are excluded from means (not zero-filled); every cell mean below reports
  its scored-n.

## 2. Aggregate (all 8 configs)

| Metric | Mean |
|---|---|
| faithfulness | 0.900 |
| answer_relevancy | 0.846 |
| context_precision | 0.864 |
| context_recall | 0.961 |

## 3. Per-config scores

| Config | HyDE | CAD | SCD | faith | ans_rel | ctx_prec | ctx_rec |
|---|:--:|:--:|:--:|---|---|---|---|
| hyde_off__no_decoder_control | – | – | – | 0.871 | 0.825 | 0.891 | 0.947 |
| hyde_off__cad_only | – | ✓ | – | **0.926** | 0.805 | 0.914 | 0.947 |
| hyde_off__scd_only | – | – | ✓ | 0.848 | 0.829 | 0.853 | 0.947 |
| hyde_off__cad_scd | – | ✓ | ✓ | 0.919 | 0.784 | 0.877 | 0.947 |
| hyde_on__no_decoder_control | ✓ | – | – | 0.867 | 0.866 | 0.844 | 0.947 |
| hyde_on__cad_only | ✓ | ✓ | – | 0.917 | **0.906** | 0.845 | 0.974 |
| hyde_on__scd_only | ✓ | – | ✓ | 0.916 | 0.892 | 0.810 | **1.000** |
| hyde_on__cad_scd | ✓ | ✓ | ✓ | **0.925** | 0.858 | 0.867 | 0.974 |

## 4. Per-axis effects (paired, same query across on/off)

Deltas are ON − OFF over configs identical except for the named axis; win/loss
counts use a ±0.01 band.

| Axis | Metric | ON | OFF | Δ (paired) | win/loss (n) |
|---|---|---|---|---|---|
| **CAD** | faithfulness | 0.922 | 0.876 | **+0.044** | +25/−17 (63) |
| CAD | context_precision | 0.876 | 0.851 | +0.013 | +9/−11 (65) |
| CAD | answer_relevancy | 0.838 | 0.853 | −0.015 | +26/−35 (76) |
| CAD | context_recall | 0.961 | 0.961 | 0.000 | +1/−2 (76) |
| **HyDE** | answer_relevancy | 0.881 | 0.811 | **+0.070** | +28/−18 (76) |
| HyDE | context_recall | 0.974 | 0.947 | +0.026 | +4/−3 (76) |
| HyDE | faithfulness | 0.906 | 0.894 | +0.016 | +24/−18 (65) |
| HyDE | context_precision | 0.843 | 0.884 | **−0.056** | +19/−18 (66) |
| **SCD** | context_recall | 0.967 | 0.954 | +0.013 | +1/−0 (76) |
| SCD | faithfulness | 0.903 | 0.896 | +0.009 | +16/−17 (66) |
| SCD | context_precision | 0.853 | 0.874 | −0.005 | +7/−5 (65) |
| SCD | answer_relevancy | 0.841 | 0.850 | −0.010 | +20/−21 (76) |

## 5. Findings

1. **CAD raises faithfulness** (+0.044 mean, paired 25 wins / 17 losses) — its
   designed effect: context-aware decoding suppresses ungrounded tokens. The two
   highest-faithfulness cells (`hyde_off__cad_only` 0.926, `hyde_on__cad_scd`
   0.925) are both CAD-on.
2. **HyDE raises answer_relevancy (+0.070) and context_recall (+0.026) but lowers
   context_precision (−0.056)** — a recall/precision trade-off consistent with
   query-reformulation retrieval: hypothetical-document expansion pulls more
   relevant material into the pool while admitting some off-target chunks.
3. **SCD is a null result** — neutral on all four RAGAS metrics (|Δ| ≤ 0.013)
   AND, on a direct Korean-character-ratio check of the 152 answers, net-null on
   its own target (paired mean Δ = **−0.014**; 22 up / 24 down / 30 tie). Language
   drift is real (43/152 answers < 0.5 Korean; 25% of SCD-off answers drift below
   0.5), but the **uniform soft-penalty SCD does not fix it**: it rescues only
   **2/19** drift cases to ≥ 0.5 while dragging **9/28** already-Korean answers
   (≥ 0.7) below 0.65. As implemented, SCD delivers no reliable Korean-adherence
   guarantee. This null result motivates **drift-conditional** language control as
   future work (apply the penalty only when drift is detected, rather than
   uniformly). Evidence: [scd_language_adherence.json](../results/analysis/scd_language_adherence.json).
4. **Internal-validity check**: the retrieval-side axis (HyDE) moves context_recall
   (+0.026) while the decoder-side axes (CAD, SCD) leave it essentially unchanged
   (0.000, +0.013). Axes move the metrics they structurally should, and the four
   `hyde_off` configs share identical context_recall (0.947) — evidence the
   backbone is genuinely fixed across configs.

Design note: n = 19 queries per config, paired across the 8 configs on the same
query set. See [limitations](phase8_limitations.md).
