[Summary]
- phase: Phase 7.4 - Hardware-aware tuning budget check
- readiness before: ready_for_phase7_5_with_explicit_user_approval
- readiness after: ready_for_phase7_5A_smoke_with_explicit_user_approval
- files created:
  - experiments/configs/tuning_execution_budget.local.yaml
  - experiments/reports/phase7_4_hardware_budget_report.md
- files modified: none
- actual tuning run: no

[Hardware]
- cuda available: yes
- gpu name: NVIDIA GeForce RTX 3080 Ti
- vram: 12.0 GB
- torch/cuda inspection:
  - torch_available: true
  - cuda_available: true
  - device_count: 1
  - device 0: NVIDIA GeForce RTX 3080 Ti, total_memory_gb 12.0
- nvidia-smi inspection:
  - nvidia-smi: available
  - driver version: 591.86
  - driver-reported CUDA version: 13.1
  - observed memory usage: 1469 MiB / 12288 MiB
- limitations:
  - Desktop WDDM GPU with background graphics processes already using VRAM.
  - Treat local execution as weak/limited for thesis tuning.
  - Start with serial single-sample smoke only; do not run full staged or axis-replicated tuning first.

[Tuning Budget]
- tuning query count: 5
- staged profile count: 12
- smoke samples: 1
- mini samples: 12
- small samples: 60
- full staged samples: 60 before axis replication
- axis-replicated upper bound: 480
- recommended first execution: Phase 7.5A smoke_1 only, with 1 query, 1 profile, 1 axis config, serial execution

[Execution Ladder]
- smoke:
  - queries: 1
  - profiles: 1
  - axis_configs: 1
  - max_samples: 1
  - purpose: verify execution path only
- mini:
  - queries: 3
  - profiles: 2
  - axis_configs: 2
  - max_samples: 12
  - purpose: check stability and rough signal
  - require_user_approval: true
- small:
  - queries: 5
  - profiles: 3
  - axis_configs: 4
  - max_samples: 60
  - purpose: limited tuning evidence
  - require_user_approval: true
- full staged:
  - queries: 5
  - profiles: 12
  - axis_configs: 1
  - max_samples: 60
  - require_user_approval: true
  - recommended_for_weak_gpu: only after smoke and mini pass
- full axis-replicated:
  - queries: 5
  - profiles: 12
  - axis_configs: 8
  - max_samples: 480
  - require_user_approval: true
  - not_recommended_for_weak_gpu: true

[Config]
- budget file: experiments/configs/tuning_execution_budget.local.yaml
- conservative settings:
  - batch_size: 1
  - max_parallel_requests: 1
  - max_new_tokens: 512
  - smoke temperature: 0.0
  - current repo temperature default: 0.1
  - smoke decoding mode: deterministic_greedy
  - use_cache: true_if_supported
  - retry_failed_samples for smoke: false
- unsupported or symbolic settings:
  - batch_size and max_parallel_requests are execution-policy constraints, not proven current runner CLI flags.
  - use_cache remains symbolic until a future execution adapter confirms runtime support.
  - run_tuning_plan.py does not yet accept a --budget-profile argument; Phase 7.4 did not change runner code.

[Validation]
- json validation:
  - python -m json.tool experiments/data/query_splits/tuning_queries.json: pass
- compileall:
  - python -m compileall backend experiments: pass
- run_tuning_plan dry-run:
  - python experiments/runners/run_tuning_plan.py --dry-run --plan-only --limit 5: pass
  - planned samples: 40
  - execute: false
  - model/OpenAI/RAGAS/GT regeneration flags: false
- dry_run_matrix:
  - python experiments/runners/dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run: pass
  - selected configs: 8
  - decoder_main queries: 19
  - leakage check: passed
- issues:
  - No runner change was made, so budget profiles are documented but not yet CLI-selectable.
  - Local hardware is available but constrained; larger runs should be explicitly staged and monitored.

[Safety]
- actual tuning run: no
- generation run: no
- main experiment run: no
- --execute enabled: no
- model calls made: no
- OpenAI calls made: no
- RAGAS calls made: no
- GT regenerated: no
- query fabricated: no
- result values invented: no
- commit made: no

[Next Step]
- whether Phase 7.5A smoke execution can start: yes, only with explicit user approval
- exact recommended smoke scope:
  - 1 tuning query
  - current_defaults profile
  - hyde_off__no_decoder_control config only
  - batch_size 1 / max_parallel_requests 1 / max_new_tokens 512 / deterministic_greedy if supported
  - no OpenAI / no RAGAS / no GT regeneration
- whether commit is recommended: yes, after review, commit the Phase 7.4 budget config and report
- what user approval is needed before real execution:
  - explicit approval to enter Phase 7.5A smoke execution
  - approval for the exact smoke scope above
  - approval that the local model/backend generation path may be invoked
  - confirmation that OpenAI and RAGAS remain disabled
