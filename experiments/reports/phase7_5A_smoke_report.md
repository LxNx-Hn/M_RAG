[Summary]
- phase: Phase 7.5A - 1-sample local smoke execution
- readiness before: ready_for_phase7_5A_smoke_with_explicit_user_approval
- readiness after: blocked_by_local_vram
- files created:
  - experiments/runners/run_local_smoke.py
  - experiments/results/smoke/phase7_5A_smoke_local_1sample.jsonl
  - experiments/reports/phase7_5A_smoke_report.md
- files modified: none
- actual smoke generation run: attempted, failed safely before answer generation
- sample count: 1

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
- runner or script used: experiments/runners/run_local_smoke.py --execute-smoke
- code changes made:
  - added experiments/runners/run_local_smoke.py
  - the runner refuses broader tuning, uses exactly the first tuning query, fixes the axis config to hyde_off__no_decoder_control, and writes one JSONL record
  - the runner refuses implicit model downloads and blocks local execution when cached model size exceeds free VRAM
- output file: experiments/results/smoke/phase7_5A_smoke_local_1sample.jsonl
- generation succeeded: no
- error if any:
  - initial smoke attempt timed out during local Base model loading and the Python process was stopped to release VRAM
  - final one-record smoke output reports: cached generation model files total 21.51 GB, exceeding currently free VRAM 10.38 GB

[Hardware]
- GPU: NVIDIA GeForce RTX 3080 Ti
- VRAM: 12.0 GB / 12288 MiB
- pre-run VRAM usage: 1520 MiB used / 10567 MiB free
- observed during timed-out attempt: 10966 MiB used / 1121 MiB free
- post-run VRAM usage: 1427 MiB used / 10660 MiB free after stopping the smoke Python process
- CUDA/OOM issues:
  - no explicit CUDA OOM traceback was produced
  - practical local VRAM blocker observed because the Base model cache is larger than available VRAM and model loading did not complete within the smoke timeout

[Output Sanity]
- answer generated: no
- context retrieved: context was loaded from local vector store for paper_nlp_bge; generation did not complete
- output record count: 1
- required metadata present:
  - query_id, query, profile, axis config, use_hyde/use_cad/use_scd, context, backend metadata, timing, error, local_only, OpenAI/RAGAS/GT flags
- decoder_main used: no
- final_eval used: no

[Validation]
- json validation:
  - python -m json.tool experiments/data/query_splits/tuning_queries.json: pass
- compileall:
  - python -m compileall backend experiments: pass
- output JSONL validation:
  - exactly 1 record
  - status: failed
  - sample_count: 1
  - query_id: track1_0001
- sample cap validation: pass; no more than one sample record exists
- OpenAI usage check: pass; openai_used=false
- RAGAS usage check: pass; ragas_used=false
- GT regeneration check: pass; gt_regenerated=false

[Safety]
- smoke generation run: failed safely
- sample count: 1
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
- blocked_by_local_vram
- Explanation: The approved Base generation model is cached locally, but its safetensors total about 21.51 GB while the RTX 3080 Ti had only about 10.38 GB free at the guarded smoke check. The first local loading attempt drove VRAM usage to about 10.7 GB and timed out before producing an answer. Continuing locally without a smaller-model/offload plan would violate the weak-GPU budget.

[Next Step]
- whether Phase 7.5B mini can start: no, not on this local Base-model path
- whether Alice Cloud is needed now: yes, if the smoke must use the thesis Base generation model
- whether smoke artifacts should be committed: yes, after review, because they document the local blocker and add a safer smoke-only runner
- recommended next sample budget:
  - option A: rerun Phase 7.5A smoke on Alice Cloud with the same 1-sample scope and Base model
  - option B: request explicit approval for a local Mini fallback smoke, marked as smoke-only and not thesis evidence
  - option C: request explicit approval for an offload/quantization plan before another local Base attempt
- remaining risks:
  - small tuning split
  - local 12GB VRAM
  - track1_0058 final-claim risk
  - Track 2 template-only status
