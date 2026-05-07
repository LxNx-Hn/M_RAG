[Summary]
- phase: Phase 7.5 Retry - Alice MIDM BASE 1-sample smoke retry after retrieval indexing
- readiness before: ready_for_phase7_5_retry_with_explicit_user_approval
- readiness after: ready_for_phase7_6_alice_tuning_with_explicit_user_approval
- files created: experiments/results/smoke/phase7_5_alice_base_smoke_retry_1sample.jsonl; experiments/reports/phase7_5_alice_base_smoke_retry_report.md; experiments/reports/phase7_5_alice_base_smoke_retry_summary_report.md
- files modified: experiments/reports/phase7_5_alice_base_smoke_retry_summary_report.md
- commit made: no

[Retry Scope]
- query_id: track1_0001
- profile: current_defaults
- axis config: hyde_off__no_decoder_control
- model: K-intelligence/Midm-2.0-Base-Instruct
- sample count: 1
- output file: experiments/results/smoke/phase7_5_alice_base_smoke_retry_1sample.jsonl

[Retrieval Precheck]
- collection: local_gt__papers
- doc_id: paper_nlp_bge
- chunk count before smoke: 5 sample chunks returned; indexed collection total was previously verified as 82
- context available before smoke: yes

[Execution]
- script used: OUTPUT_FILE=experiments/results/smoke/phase7_5_alice_base_smoke_retry_1sample.jsonl REPORT_FILE=experiments/reports/phase7_5_alice_base_smoke_retry_report.md CONFIRM_ALICE_BASE_SMOKE=1 bash experiments/scripts/alice/alice_base_smoke.sh
- generation succeeded: yes
- output record count: 1
- error if any: None

[Output Sanity]
- answer generated: yes
- context_available: True
- chunk count: 3
- required metadata present: yes
- thesis_grade_result: False
- decoder_main used: False
- final_eval used: False

[Validation]
- JSONL validation: passed
- sample cap validation: passed, exactly 1 record
- model variant check: passed, model_variant=base
- retrieval context check: passed, context_available=true and chunk count=3
- OpenAI usage check: passed, openai_used=False
- RAGAS usage check: passed, ragas_used=False
- GT regeneration check: passed, gt_regenerated=False
- issues: none blocking; ONNX Runtime CPU affinity warnings and Transformers deterministic-generation temperature/top_k warnings appeared but did not fail execution

[Hardware]
- GPU: NVIDIA A100 80GB PCIe MIG 3g.40gb
- VRAM: 40448 MiB MIG slice by nvidia-smi; post-run usage returned to 16 MiB / 40448 MiB
- OOM or CUDA errors: none observed

[Safety]
- smoke generation run: yes
- sample count: 1
- full tuning run: no
- mini tuning run: no
- small tuning run: no
- main experiment run: no
- OpenAI calls made: no
- RAGAS calls made: no
- GT regenerated: no
- query fabricated: no
- result values invented: no
- commit made: no

[Decision]
- ready_for_phase7_6_alice_tuning_with_explicit_user_approval

[Next Step]
- whether Alice thesis tuning can start: yes, after explicit user approval
- whether a small script patch is needed before Phase 7.6: no hard blocker from this retry; optional cleanup could rename default Alice smoke output/report labels from phase7_7 to phase7_5 for clarity, but the env override worked correctly
- reminder that this smoke is validation-only, not thesis evidence: yes
