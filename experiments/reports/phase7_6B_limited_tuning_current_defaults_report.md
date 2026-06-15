> **[CORRECTION — Phase 7.6B-2A static audit]**
> This run used a `doc_id`-filtered vector-store sample (`collection.get(where={doc_id})`),
> NOT query-aware fixed-backbone retrieval (BGE-M3 + BM25 + RRF + CrossEncoder).
> The same three chunks (title/intro/contributions) were returned for all five
> queries regardless of query text, so the run validates execution stability only.
> Corrected evidence grade (also written into the JSONL metadata): `evidence_class:
> execution_smoke_only`, `parameter_freeze_evidence: false`, `fixed_backbone_validation:
> false`, `thesis_grade_result: false`. Generated answers were NOT regenerated; only
> the meaning/metadata was corrected. The `[Decision]` and `[Next Step]` sections below
> are superseded: the correct next step is **Phase 7.6B-2A** (1-sample query-aware
> fixed-backbone retrieval smoke), NOT Phase 7.6C profile expansion.

[Summary]
- phase: Phase 7.6B-1 - Alice limited tuning, current_defaults only
- readiness before: ready_for_phase7_6B_limited_tuning_with_explicit_user_approval
- readiness after: ready_for_phase7_6C_profile_expansion_with_explicit_user_approval
- files created: experiments/scripts/alice/alice_limited_tuning.sh; experiments/results/tuning/phase7_6B_limited_tuning_current_defaults_5samples.jsonl; experiments/reports/phase7_6B_limited_tuning_current_defaults_report.md
- files modified: experiments/runners/run_alice_tuning.py; experiments/reports/phase7_6B_limited_tuning_current_defaults_report.md
- commit made: no

[Limited Tuning Scope]
- query split: tuning_queries
- query count: 5
- query ids: track1_0001, track1_0004, track1_0005, track1_0007, track1_0008
- profile: current_defaults
- axis config: hyde_off__no_decoder_control
- model: K-intelligence/Midm-2.0-Base-Instruct
- collection: local_gt__papers
- max samples: 5
- output file: experiments/results/tuning/phase7_6B_limited_tuning_current_defaults_5samples.jsonl

[Execution]
- generation succeeded: yes
- output record count: 5
- succeeded records: 5
- failed records: 0
- errors if any: none

[Per-Sample Summary]
For sample 1:
- query_id: track1_0001
- status: succeeded
- context_available: True
- chunk count: 3
- answer generated: yes
- duration_seconds: 20.379
For sample 2:
- query_id: track1_0004
- status: succeeded
- context_available: True
- chunk count: 3
- answer generated: yes
- duration_seconds: 340.322
For sample 3:
- query_id: track1_0005
- status: succeeded
- context_available: True
- chunk count: 3
- answer generated: yes
- duration_seconds: 85.283
For sample 4:
- query_id: track1_0007
- status: succeeded
- context_available: True
- chunk count: 3
- answer generated: yes
- duration_seconds: 231.919
For sample 5:
- query_id: track1_0008
- status: succeeded
- context_available: True
- chunk count: 3
- answer generated: yes
- duration_seconds: 86.289

[Validation]
- compileall: passed
- pytest: passed, python -m pytest tests/backend -q
- runner help: passed, python experiments/runners/run_alice_tuning.py --help
- dry-runs: passed for run_tuning_plan, dry_run_matrix, and run_generation plan
- output JSONL validation: passed, exactly five expected records with context_available=true and safety markers false
- issues: non-blocking ONNX Runtime CPU affinity warnings, Transformers deterministic-generation temperature/top_k warnings, and CPU/meta offload notices appeared; no validation blocker or CUDA/OOM failure occurred

[Hardware]
- GPU: NVIDIA A100 80GB PCIe MIG 3g.40gb
- VRAM: 40448 MiB MIG slice; post-run usage returned to 16 MiB / 40448 MiB
- OOM/CUDA errors: none observed

[Safety]
- real limited tuning samples: 5
- full tuning run: no
- multi-profile tuning run: no
- multi-axis tuning run: no
- main experiment run: no
- decoder_main used: no
- final_eval used: no
- OpenAI calls made: no
- RAGAS calls made: no
- GT regenerated: no
- query fabricated: no
- result values invented: no
- runtime vector DB committed: no
- model cache committed: no
- secrets committed: no

[Decision]
- SUPERSEDED by Phase 7.6B-2A audit: ready_for_phase7_6B_2A_fixed_backbone_retrieval_smoke_with_explicit_user_approval (NOT 7.6C profile expansion)

[Next Step]
- whether profile expansion can start: NO. Profile expansion is blocked until a query-aware fixed-backbone retrieval smoke (Phase 7.6B-2A) succeeds.
- recommended next scope:
  - 5 tuning queries
  - 3 profiles max
  - one axis config only
- whether 80GB upgrade is needed: not needed for this 5-sample current_defaults run; consider more headroom only if later profile/axis expansion becomes too slow or hits memory/offload limits
- reminder that limited tuning is parameter-freeze evidence, not final evaluation evidence: SUPERSEDED — see correction banner. This run is execution_smoke_only and is NOT parameter-freeze evidence, because it bypassed query-aware fixed-backbone retrieval.
