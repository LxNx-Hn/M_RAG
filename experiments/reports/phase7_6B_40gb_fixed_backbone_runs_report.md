# Phase 7.6B/7.6C — Alice 40GB Fixed-Backbone Runs Report

Status: tuning/probe evidence only. **Not** a parameter freeze, **not** a final
evaluation, **not** the main 8-config experiment. OpenAI, RAGAS, and GT
regeneration were disabled throughout. No queries were generated or duplicated.

## Environment

- Repo HEAD: `035c1a9` (latest `origin/main`; contains `d0ea76a`)
- GPU: NVIDIA A100 80GB PCIe **MIG 3g.40gb** (42.41 GB visible to the process)
- Python 3.10.15, torch 2.5.1+cu121 (CUDA available), transformers 4.45.2,
  sentence-transformers 2.7.0, chromadb 1.5.9
- Model: `K-intelligence/Midm-2.0-Base-Instruct` (bf16; clean single load = 23.1 GB
  allocated, fully on `cuda:0`, no CPU/disk offload)
- Embedder: BGE-M3; Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2
- Collection: `local_gt__papers`, doc_id `paper_nlp_bge`, 82 chunks; BM25 index present
- Runtime/caches kept OUTSIDE the repo (`~/mrag_runtime`, `~/.cache/huggingface`);
  Chroma DB, BM25 pickle, venv, model caches, runtime DB are untracked.

## 1. Phase 7.6B-2A — one-sample fixed-backbone smoke

- Command: `CONFIRM_ALICE_FIXED_BACKBONE_SMOKE=1 bash experiments/scripts/alice/alice_fixed_backbone_smoke.sh`
- Output: `experiments/results/tuning/phase7_6B2A_fixed_backbone_retrieval_smoke_1sample.jsonl`
- record_count = 1. **Validation: PASS (16/16).**
- query_id=track1_0001, retrieval_mode=fixed_backbone, bm25_index_available=true,
  fallback_used=false, context_available=true, dense/sparse/fused = 20/20/20,
  context_chunk_count=5, generated_answer non-empty (734 chars),
  openai/ragas/gt=false, parameter_freeze_evidence=false,
  evidence_class=retrieval_backbone_smoke.
- Reranked chunk IDs: paper_nlp_bge_8d13f430675e, _623ac2210d33, _af2c8112fcd5,
  _209a4ebb079e, _d62aa02112b0.

## 2. Phase 7.6B-2B — five-sample fixed-backbone baseline

- Command: `python experiments/runners/run_alice_tuning.py --execute-limited-tuning
  --confirm-alice-limited-tuning --retrieval-mode fixed_backbone --query-split
  tuning_queries --query-limit 5 --max-samples 5 --profile current_defaults
  --axis-config hyde_off__no_decoder_control --generation-model
  K-intelligence/Midm-2.0-Base-Instruct --model-variant base --collection-name
  local_gt__papers --max-new-tokens 512 --temperature 0.0 --output-file ...`
- Output: `experiments/results/tuning/phase7_6B2B_fixed_backbone_baseline_5samples.jsonl`
- record_count = 5. **Validation: PASS (all 5).**
- All records: status=succeeded, retrieval_mode=fixed_backbone,
  bm25_index_available=true, fallback_used=false, context_available=true,
  dense/sparse/fused = 20/20/20 each, context_chunk_count=5, non-empty answers,
  openai/ragas/gt=false, parameter_freeze_evidence=false,
  evidence_class=retrieval_backbone_smoke.
- Query IDs: track1_0001, track1_0004, track1_0005, track1_0007, track1_0008.
- Note: the legacy `generate_answer` path reloads the model per sample without
  freeing the prior copy, so samples 2-5 emitted "offloaded to cpu" warnings
  (accumulated weights exceeded the 40GB partition). Outputs are correct; the
  run is simply slow (~190s/sample). The new follow-up runner avoids this by
  loading the model once.

## 3. New limited follow-up runner

`experiments/runners/run_alice_followup.py` — a narrowly scoped, hard-guarded
adapter that REUSES existing components only:

- fixed-backbone retrieval (`HybridRetriever.search_with_trace`: BGE-M3 dense +
  BM25 sparse + RRF) + CrossEncoder reranker + `ContextCompressor`
- HyDE via `modules.query_expander.QueryExpander`
- CAD + SCD via `modules.scd_decoder.create_combined_processor`
- generation via `modules.generator.Generator` (instantiated **once** and reused)

Guards (fail closed): requires `CONFIRM_ALICE_FOLLOWUP=1`; collection must be
`local_gt__papers`; model must be MIDM BASE; OpenAI/RAGAS must be disabled; only
`tuning_queries`; memory-probe hard-limited to 1 record; tuning-7c limited to
<=3 allow-listed profiles x 5 queries (<=15 records). It never touches
`run_generation.py`/decoder_main, the 8-config matrix, final eval, freeze,
OpenAI, RAGAS, or GT.

## 4. Phase 7.6B-3 — 40GB worst-case memory probe

- Mode: memory-probe (HyDE on + CAD on + SCD on), 1 sample (track1_0001),
  current_defaults, fixed_backbone, local_gt__papers.
- Output: `experiments/results/tuning/phase7_6B3_worstcase_memory_probe_1sample.jsonl`
- **Validation: PASS.** status=succeeded, generated_answer non-empty (938 chars),
  cuda_oom=false, retrieval d/s/f=20/20/20, context=5, hyde_used=true,
  cad_alpha=0.5, scd_beta=0.3, openai/ragas/gt=false.
- **Memory evidence (the key result):**
  - GPU: MIG 3g.40gb, 42.41 GB total
  - peak_allocated = **27.07 GB**
  - peak_reserved = **41.99 GB (~99% of the 40GB partition)**
  - free after = 12.85 GB; duration 110.9s
- Interpretation: the heaviest local path SURVIVES one short-context sample on
  the 40GB MIG with no OOM, but peak reserved memory reaches ~99%. CAD's parallel
  no-context forward pass plus HyDE drive memory to the partition ceiling. Headroom
  is minimal (~0.4 GB at peak reserved).

## 5. Phase 7.6C — small tuning comparison

- Mode: tuning-7c, fixed_backbone baseline axis (no HyDE/CAD/SCD).
- Profiles (from tuning_plan.yaml staged_candidate_profiles): current_defaults,
  retrieval_conservative, retrieval_recall_oriented.
- 3 profiles x 5 tuning queries = **15 records**.
- Output: `experiments/results/tuning/phase7_6C_small_tuning_comparison_15records.jsonl`
- **Validation: PASS (15/15).** all succeeded, all fixed_backbone,
  fallback_used=false, context_available=true, non-empty answers,
  openai/ragas/gt=false, parameter_freeze_evidence=false.

| profile | pool / rerank / context | avg answer chars |
|---|---|---|
| retrieval_conservative | 3 / 3 / 3 | 889 |
| current_defaults | 20 / 5 / 5 | 2457 |
| retrieval_recall_oriented | 8 / 8 / 5 | 3806 |

Observation (tuning evidence only): broader retrieval/rerank breadth yields longer
answers with more context; conservative breadth is markedly terser. This is a
retrieval-breadth sensitivity signal, **not** a parameter-freeze decision and
**not** a quality/accuracy claim (no GT/RAGAS scoring was run).

## 6. GPU / OOM status

- No CUDA OOM in any step. MIG 3g.40gb confirmed in use (clean load: 23.1 GB on
  cuda:0, no offload). The Alice dashboard's 0% GPU utilization is a MIG-guest
  reporting limitation (`nvidia-smi` from the guest returns "Insufficient
  Permissions"); actual usage was confirmed from inside the process via
  torch.cuda memory stats.

## 7. Next-step recommendation

- Parameter freeze (Phase 8): can be CONSIDERED later, but NOT on this evidence.
  7.6C is a 5-query x 3-profile retrieval-breadth probe with no GT/RAGAS scoring;
  a freeze needs the approved tuning sweep with a scoring criterion.
- Main experiment GPU: **80GB recommended.** The worst-case HyDE+CAD+SCD probe
  reserved ~99% of the 40GB partition for a single short-context sample. Longer
  contexts, the full 8-config matrix, or any batching would risk OOM on 40GB.
- Must NOT be run yet: parameter freeze, decoder_main, the 8-config main
  experiment, final evaluation, OpenAI, RAGAS, GT regeneration, query
  generation/duplication.
