[Summary]
- phase: Phase 7.5A-mini - 1-sample local MIDM Mini smoke execution
- readiness before: ready_for_phase7_5A_mini_smoke_with_explicit_user_approval
- readiness after: ready_for_alice_base_smoke_with_explicit_user_approval
- files created:
  - experiments/results/smoke/phase7_5A_mini_smoke_local_1sample.jsonl
  - experiments/reports/phase7_5A_mini_smoke_report.md
- files modified:
  - experiments/runners/run_local_smoke.py
- actual smoke generation run: yes
- sample count: 1

[Model Policy]
- local smoke model: K-intelligence/Midm-2.0-Mini-Instruct
- thesis experiment model: K-intelligence/Midm-2.0-Base-Instruct on Alice Cloud
- thesis_grade_result: false
- Alice Cloud needed for thesis-grade runs: yes

[Smoke Scope]
- query_id: track1_0001
- profile: current_defaults
- axis config: hyde_off__no_decoder_control
- use_hyde: false
- use_cad: false
- use_scd: false
- max_new_tokens: 512
- temperature: 0.0
- decoding mode: deterministic_greedy
- local_only: true

[Execution]
- execution path: dedicated Phase 7.5A smoke-only runner with one-sample hard cap
- runner or script used: experiments/runners/run_local_smoke.py --execute-smoke --generation-model K-intelligence/Midm-2.0-Mini-Instruct --model-variant mini --require-mini --output-file experiments/results/smoke/phase7_5A_mini_smoke_local_1sample.jsonl
- code changes made:
  - added smoke-only --model-variant metadata
  - added --require-mini guard to block accidental BASE use during local Mini smoke
  - added model_role, model_family, model_variant, thesis_grade_result, and selected_model_path_or_name metadata to smoke records
  - preserved one-sample cap and no-download guard
- output file: experiments/results/smoke/phase7_5A_mini_smoke_local_1sample.jsonl
- generation succeeded: yes
- error if any: none
- warnings:
  - Transformers emitted a warning that temperature/top_k generation flags may be ignored by the model configuration.

[Hardware]
- GPU: NVIDIA GeForce RTX 3080 Ti
- VRAM: 12.0 GB / 12288 MiB
- pre-run VRAM usage: 1112 MiB used / 10975 MiB free
- post-run VRAM usage: 1100 MiB used / 10987 MiB free
- CUDA/OOM issues: none observed

[Output Sanity]
- answer generated: yes
- context retrieved: context was loaded from local vector store for paper_nlp_bge
- output record count: 1
- required metadata present:
  - query_id, query, profile, axis config, model_role, model_family, model_variant, thesis_grade_result, selected_model_path_or_name, use_hyde/use_cad/use_scd, answer, context, backend metadata, timing, local_only, OpenAI/RAGAS/GT flags
- decoder_main used: no
- final_eval used: no
- thesis_grade_result: false

[Validation]
- json validation:
  - python -m json.tool experiments/data/query_splits/tuning_queries.json: pass
- compileall:
  - python -m compileall backend experiments: pass
- output JSONL validation:
  - exactly 1 record
  - status: succeeded
  - sample_count: 1
  - query_id: track1_0001
- sample cap validation: pass; no more than one sample record exists
- model variant check: pass; model_variant=mini
- OpenAI usage check: pass; openai_used=false
- RAGAS usage check: pass; ragas_used=false
- GT regeneration check: pass; gt_regenerated=false

[Safety]
- smoke generation run: yes
- sample count: 1
- MIDM BASE local run: no
- full tuning run: no
- mini tuning run: no
- small tuning run: no
- main experiment run: no
- decoder_main used for tuning: no
- final_eval used for tuning: no
- OpenAI calls made: no
- RAGAS calls made: no
- GT regenerated: no
- query fabricated: no
- result values invented: no
- commit made: no

[Decision]
- ready_for_alice_base_smoke_with_explicit_user_approval
- Explanation: The local MIDM Mini smoke validated that the one-sample smoke runner can select the first tuning query, load local context, run a local model, produce one output record, and preserve the safety markers. The output is validation-only and not thesis-grade. Because local MIDM BASE remains blocked by VRAM, thesis-grade BASE smoke should move to Alice Cloud with explicit approval.

[Next Step]
- whether Alice MIDM BASE smoke can start: yes, with explicit user approval and the same 1-sample scope
- whether local MIDM Mini mini-subset is useful: yes, only for pipeline stability validation, not thesis claims
- whether smoke artifacts should be committed: yes, after review
- recommended next sample budget:
  - Alice BASE smoke: 1 tuning query x 1 profile x 1 axis config = 1 sample
  - Optional local Mini subset: keep very small and label all outputs validation-only
- remaining risks:
  - local Mini is validation-only
  - thesis results require Alice MIDM BASE
  - small tuning split
  - track1_0058 final-claim risk
  - Track 2 template-only status
