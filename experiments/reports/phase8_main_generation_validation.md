# Phase 8 — Main 8-Config Generation: Validation Report

Run: 2026-07-04 (KST evening), Alice Cloud, single **NVIDIA A100 80GB PCIe**.
Output: [main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl](../results/main_generation/main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl)
(commit `e283ea1`).

## 1. Execution conditions

| Item | Value |
|---|---|
| Runner | `run_generation.py --execute` (fail-closed gate chain) |
| Confirmation | `CONFIRM_MAIN_8CONFIG_GENERATION=1` |
| Frozen parameters | `experiments/configs/frozen_params.yaml` (commit `f081430`): pool 8 / rerank 8 / ctx 5, cad_alpha 0.5, scd_beta 0.3, max_new_tokens 512, deterministic greedy |
| Generation model | `K-intelligence/Midm-2.0-Base-Instruct`, loaded ONCE and reused for all samples |
| Retrieval | fixed backbone (BGE-M3 dense + BM25 + RRF + CrossEncoder), collection `local_gt__papers`, full corpus (8 papers, 698 chunks), per-query `doc_id_filter` |
| Query split | `decoder_main_queries` (19 queries; targets paper_nlp_rag 5 / paper_midm 6 / paper_nlp_cad 4 / paper_nlp_raptor 4) |
| Configs | exactly the approved 8 HyDE x CAD x SCD combinations (`validate_main_matrix`) |
| External calls | none — OpenAI / RAGAS / GT-regeneration flags false on every record |

## 2. Validation results (152 records)

| Check | Result |
|---|---|
| Record count = 19 x 8 = 152 | ✅ (19 per config, all 8 configs) |
| All `status=succeeded` | ✅ 152/152, `error` null everywhere |
| `generated_answer` non-empty | ✅ (mean 1,075 chars) |
| Inline `contexts` present & non-empty | ✅ every record |
| Retrieval trace (backend, pool/rerank/ctx, chunk ids, counts) | ✅ pool=8, rerank=8, ctx<=5 on every record |
| Config/axis metadata (`config_name`, `use_hyde/cad/scd`) | ✅; `hyde_used` true in exactly the 4 hyde_on configs (76 records) |
| `fallback_used=false` everywhere | ✅ |
| CUDA OOM | none |
| Mean duration | 45.3 s/sample (worst-case CAD+SCD+HyDE cells included) |

## 3. GPU evidence (2-minute sampler)

- GPU: NVIDIA A100 80GB PCIe (81,920 MiB)
- Peak observed: **96% utilization, 34,800 MiB** — ample headroom on 80GB;
  consistent with the earlier 40GB worst-case probe reserving ~99% (the 80GB
  recommendation was correct: the same workload leaves ~45GB free here).

## 4. Incidents during the phase (resolved before the accepted run)

1. First launch aborted at `git pull` (untracked result file collision on the
   instance); fixed by removing the instance-side duplicate (byte-identical to
   the committed copy) — watcher patterns widened to catch `Aborting`/`error:`.
2. First full run produced 152/152 *failures* ("no context chunks after
   rerank"): the index contained only `paper_nlp_bge` while the main split
   targets four other papers. Root cause fixed by indexing the full checked-in
   corpus (`build_local_gt_index.py --reset`, 8 papers / 698 chunks, commit
   `c8e0046`) and re-running. The failed file was quarantined off-repo.
3. Executor honored `rerank_top_n` as context depth; fixed to respect the
   frozen `context_chunk_count` (commit `f081430`) before any accepted run.

The accepted run is the only one whose outputs enter evaluation.
