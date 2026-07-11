# reference_scd Completion Runbook

This is the authoritative cold-start handoff for finishing the remaining `reference_scd` thesis-experiment pipeline end to end. A fresh AI session or agent with no chat history should be able to read this file, resume or diagnose the Alice scoring job, pull the official artifacts, run the final analyses, and write the final report without asking the project owner to re-explain prior decisions.

This file is specific to the corrected `reference_scd` experiment track:

- Canonical corrected experiment id: `main-hyde-cad-scd-reference-scd`
- Query split: `decoder_main_queries`
- Generation file: `experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl`
- Official scoring judge: NVIDIA NIM
- Official metrics: `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`
- SCD implementation under test: `reference_scd` in `backend/modules/scd_decoder.py`

Security rule for this handoff: never print, copy, summarize, partially reveal, truncate, or commit actual secret values into logs, reports, prompts, commits, or shell output. Refer only to environment variable names such as `NVIDIA_API_KEY` / `OPENAI_API_KEY` and secret file paths such as repo-root `.env` or remote `~/M_RAG/.env`. Do not run `cat .env` or any command that prints key contents. To verify presence, use count-only checks such as `grep -c "^NVIDIA_API_KEY=" ~/M_RAG/.env`.

## Current State Summary

The corrected `reference_scd` generation is complete and committed. The official NVIDIA-NIM RAGAS scoring loop is running on Alice and should be monitored until it converges or exhausts retries. Once official scoring completes, the remaining work is to pull the official scoring artifacts locally, run the established analyzers, write `experiments/reports/reference_scd_rerun_report.md`, verify the touched files, and commit only the intended outputs.

Do not treat the old `main-hyde-cad-scd` / `penalty_additive` v1 result as corrected in place. It is preserved for audit and comparison only. The corrected path is the separate `main-hyde-cad-scd-reference-scd` experiment.

## Connection

- Provider: Alice Cloud (Elice Cloud), CPU-only instance.
- GPU is not needed for this scoring phase. Embeddings run locally on CPU via `BAAI/bge-m3`; only the judge LLM call goes over the network.
- SSH connection, already provisioned from this machine:

```bash
ssh -i ~/.alice/alice.pem -p ALICE_PORT_REDACTED -o StrictHostKeyChecking=no ALICE_USER_AT_HOST_REDACTED
```

- Remote repo: `~/M_RAG`.
- Remote repo state at the narrow handoff snapshot: `main`, HEAD `17201ca`.
- Confirm before relying on that state because the branch may have advanced:

```bash
cd ~/M_RAG && git rev-parse --short HEAD
```

- Remote Python environment for scoring: `~/eval_venv`.
- Activate it with:

```bash
source ~/eval_venv/bin/activate
```

- The scoring environment already has `ragas`, `langchain-openai`, `datasets`, and `langchain-huggingface` installed.
- Remote secrets file: `~/M_RAG/.env`.
- That file contains `NVIDIA_API_KEY` and has already been transferred once with `chmod 600`.
- Do not re-transfer secrets unless `~/M_RAG/.env` is missing or the key has rotated.
- Safe presence-only verification:

```bash
grep -c "^NVIDIA_API_KEY=" ~/M_RAG/.env
```

Expected count is `1` when the variable line is present. Do not print the value.

## Currently Running

Verify the process is still alive before assuming this state is current. The scoring loop was launched via `nohup ... & disown`, so it survives SSH disconnects.

Command that was launched:

```bash
cd ~/M_RAG && source ~/eval_venv/bin/activate
export CONFIRM_OFFICIAL_RAGAS_EXECUTION=1
python experiments/evaluators/run_scoring_until_converged.py \
  --generation-results experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl \
  --query-split decoder_main_queries \
  --judge nvidia_nim \
  --metrics faithfulness,answer_relevancy,context_precision,context_recall \
  --out-dir experiments/results/evaluation/main-hyde-cad-scd-reference-scd \
  --max-workers 2 --judge-timeout 600 --task-timeout 1500 \
  --null-threshold 10 --max-passes 10 --pass-cooldown-seconds 90
```

- Log file: `~/scoring_loop.log`.
- Follow it with:

```bash
tail -f ~/scoring_loop.log
```

- Fresher progress snapshot supplied by the calling session: `591/608` cells, `97%`, about `59h14m` elapsed.
- This progress snapshot still must be verified before trusting it in a later session.
- A prior snapshot observed PID `228`, but PIDs are not stable across reboots or restarts. Re-find the live process with:

```bash
ps aux | grep run_scoring_until_converged | grep -v grep
```

- Expected pass 1 completion: within a few more hours from the progress snapshot above.
- After pass 1, `run_scoring_until_converged.py` automatically retries only the still-null cells in smaller/faster passes until either the merged null count is `<= 10` or `10` passes are exhausted.
- No manual intervention is needed unless the process dies.

Output/state directory on Alice:

```text
~/M_RAG/experiments/results/evaluation/main-hyde-cad-scd-reference-scd/
```

Expected contents:

- `pass1/`, `pass2/`, ...: each pass's raw scorer output. These are evidence directories and should not be overwritten.
- `merged.ragas_scores.json`: cumulative merged result. This appears once pass 1 finishes and is updated atomically after every merge step. This is the file the next phase reads.

## Status Check Command

This is read-only and safe to re-run anytime. It does not print secret values.

```bash
ssh -i ~/.alice/alice.pem -p ALICE_PORT_REDACTED -o ConnectTimeout=15 -o StrictHostKeyChecking=no ALICE_USER_AT_HOST_REDACTED '
ps aux | grep run_scoring_until_converged | grep -v grep
grep -oE "Evaluating:[^]]*\][^E]*" ~/scoring_loop.log | tail -1
grep -E "^pass [0-9]+:|converged:|did not converge:" ~/scoring_loop.log | tail -5
ls -la ~/M_RAG/experiments/results/evaluation/main-hyde-cad-scd-reference-scd/
'
```

Interpretation:

- A matching `run_scoring_until_converged.py` process means the scoring loop is still alive.
- The `Evaluating:` line shows current pass progress.
- `converged: merged null count <= --null-threshold` means the official scoring loop has reached the intended stop condition.
- `did not converge:` means all configured passes were exhausted and the remaining null count is still above threshold. Preserve the artifacts and report the result honestly.
- `merged.ragas_scores.json` is expected only after pass 1 finishes.

## If The Process Died

If the status check shows no `run_scoring_until_converged.py` process, treat it as `PROC_DEAD` and diagnose before relaunching.

1. Check the tail of `~/scoring_loop.log` for a Python traceback or explicit termination signal:

```bash
tail -200 ~/scoring_loop.log
```

2. Check whether the instance was resized, restarted, or OOM-killed:

```bash
dmesg | tail
```

3. Resume with the same scoring command from the "Currently Running" section.

The script is resumable. If `merged.ragas_scores.json` already exists, re-running the same command skips straight to building a retry-subset pass for whatever is still null. It does not restart pass 1 from scratch.

Do not pass `--fresh` on resume. The `--fresh` flag intentionally discards existing progress and starts over, which should not be needed here.

Relaunch pattern:

```bash
cd ~/M_RAG
nohup bash -lc '
source ~/eval_venv/bin/activate
export CONFIRM_OFFICIAL_RAGAS_EXECUTION=1
python experiments/evaluators/run_scoring_until_converged.py \
  --generation-results experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl \
  --query-split decoder_main_queries \
  --judge nvidia_nim \
  --metrics faithfulness,answer_relevancy,context_precision,context_recall \
  --out-dir experiments/results/evaluation/main-hyde-cad-scd-reference-scd \
  --max-workers 2 --judge-timeout 600 --task-timeout 1500 \
  --null-threshold 10 --max-passes 10 --pass-cooldown-seconds 90
' > ~/scoring_loop.log 2>&1 & disown
```

## Reference Paper

Citation: "Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation." Bo Li, Zhenghua Xu, Rui Xie. Hebei University of Technology / Peking University. arXiv:2511.09984. Code: https://github.com/pkuserc/SCD

Core claim: multilingual RAG systems exhibit "language drift" (generating in an unintended language, usually English, when retrieved context is in a different language than the target) due to decoder-level collapse (dominant high-frequency English token distributions), not comprehension failure. English is identified as the strongest interference source and most common fallback language.

SCD formula, verified to exactly match this repo's `reference_scd` implementation in `backend/modules/scd_decoder.py`: given raw logits `z(t)` at decoding step `t`, and a vocabulary partition into `Vtarget` (target-language tokens), `Vneutral` (punctuation/digits/shared symbols), `Vdistractor` (non-target-language tokens):

- if token `i` in `Vtarget`: adjusted logit = `alpha * z(t)_i`, `alpha > 1.0` (soft boost)
- if token `i` in `Vneutral`: unchanged
- if token `i` in `Vdistractor`: adjusted logit = `beta * z(t)_i`, `beta < 1.0` (soft penalty)
- Cold-start smoothing: language constraints are not activated until decoding step `Tstart`, to avoid disrupting the model's unstable early tokens (repeated prompt fragments, template artifacts).

Exact hyperparameters used in the paper's own experiments, verified quote: "We empirically find moderate settings (alpha = 1.1, beta = 0.9, Tstart = 5) to balance language fidelity and semantic fluency in SCD." These are the exact same values this repo's `reference_scd` run used (`--scd-alpha 1.1 --scd-beta 0.9 --scd-t-start 5`), so the rerun has full hyperparameter fidelity to the paper, not just formula fidelity.

Paper's evaluation setup:

- Datasets: HotpotQA, MuSiQue, DuReader
- Backbones: LLaMA3-8B-Instruct, Qwen2.5-7B-Instruct
- Metrics: BLEU (mean of BLEU-1/2/3), ROUGE (mean of ROUGE-1/2/L), and Language Consistency (LC, percentage of outputs in the correct target language)
- Baselines compared: Prompted Language Instruction (PLI, prompt-only), Vocabulary-Restricted Decoding (VRD, hard vocab constraint), and SCD

Paper's headline result: SCD beats both baselines on LC and on BLEU/ROUGE simultaneously. Verified quote: "SCD consistently improves both language consistency and content quality... maintaining alignment with the target language can reinforce, rather than hinder, the coherence and accuracy of reasoning paths." Example figure: ZH-EN HotpotQA, LC 68.4% -> 90.6%, BLEU 0.086 -> 0.155, ROUGE 0.182 -> 0.306 (SCD vs PLI baseline).

Notably, VRD (the hard-constraint baseline) does show a real quality cost in the paper's own data: shorter, degraded outputs, and VRD often underperforms even the plain PLI baseline on ROUGE despite VRD being more "language pure." The paper's point is that SCD's soft, boosted, warmed-up design specifically avoids the quality cost that a hard constraint (VRD) incurs.

No dedicated Limitations section discusses RAG-groundedness/faithfulness-style metrics; the paper's Conclusion simply restates that SCD "consistently enhances both language consistency and task performance."

### Why the paper's "no trade-off" claim and this project's own findings are not necessarily in conflict

This is the most important interpretive context for the final report.

The paper's "quality" metric is BLEU/ROUGE, meaning lexical n-gram overlap with a target-language reference answer. This project's RAG-quality metrics are RAGAS `faithfulness` and `answer_relevancy`, meaning LLM-judged semantic groundedness in the retrieved context and semantic relevance to the question. These are fundamentally different constructs. BLEU/ROUGE against a target-language reference will mechanically improve whenever an answer switches into the correct language, largely independent of whether the answer's content is actually well-grounded in the retrieved evidence. RAGAS faithfulness does not reward language-correctness by itself; it specifically judges whether the answer's claims are supported by retrieved context.

Therefore, the paper's claim that SCD raises BLEU/ROUGE alongside language consistency does not imply SCD would also raise RAGAS faithfulness/answer_relevancy. These are different measurements of different things. An informal side-check run in this project (OpenAI `gpt-4o-mini` judge, see "Side Artifact Warning") showed a real faithfulness/answer_relevancy decrease under SCD even though language adherence improved sharply. This is not a contradiction of the paper. It is very plausibly a cost that BLEU/ROUGE-based evaluation is simply blind to, and that the official NVIDIA-NIM-judged RAGAS result, still pending in the running Alice job, may or may not confirm at a similar magnitude.

Correct interpretive frame for the final report, established through direct discussion with the project owner this session:

- SCD's actual target metric is language adherence, Korean-character ratio in this project's case. On that metric, `reference_scd` is a clear, strong, confirmed success. This part is judge-independent because it is computed directly from generated text, not from any LLM judge, and does not change based on which judge scores the RAGAS metrics.
- The four RAGAS metrics (`faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`) were never SCD's optimization target. Reporting how they move under SCD-on vs SCD-off is characterization of an interaction/trade-off, not a re-litigation of whether SCD "worked."
- This matches how `experiments/analyzers/aggregate_main_scores.py` already treats every axis (HyDE, CAD, SCD): it reports the full 4-metric panel for every axis regardless of what that axis specifically targets.
- Continue that convention for the final report: report SCD's effect on all 4 RAGAS metrics honestly, framed as "interaction/cost characterization," not as "did SCD pass or fail."

## Confirmed Results

The following language-adherence results are final and judge-independent. They will not change no matter what the official NIM RAGAS scoring reports because they come from `experiments/analyzers/scd_language_adherence.py`, which computes Korean-character ratio directly from generated answer text with no judge/API involved.

Source:

```text
experiments/results/analysis/reference_scd_language_adherence.json
```

Confirmed `reference_scd` language-adherence result:

- `mean_delta_on_minus_off = +0.2203`
- Interpretation: SCD-on is 22 percentage points more Korean than SCD-off, on average, across 76 matched HyDE/CAD-controlled pairs.
- Win/loss: SCD-on more Korean in 68/76 pairs, less Korean in only 3/76, 5 ties.
- Drift rescue at the 0.5 Korean-ratio threshold: 26 pairs were drifting (below 0.5) when SCD was off; SCD raised their mean from 0.2515 to 0.5639, fully rescuing 15/26 past the threshold.
- Drift rescue at the stricter 0.3 threshold: 12 drifting pairs, mean 0.0667 -> 0.3843, 6/12 rescued.
- Harm check on already-good answers: of 20 pairs that were already >= 0.7 Korean with SCD off, zero were dragged below 0.65 by turning SCD on.

Contrast with the old `penalty_additive` v1 result, which was the pre-existing unrelated implementation used in the original Phase 8 run and is preserved at:

```text
experiments/results/analysis/scd_language_adherence.json
```

Old `penalty_additive` v1 language-adherence result:

- Mean delta: `-0.0137`, approximately null.
- Win/loss: 22/24, near coin-flip.
- Drift rescue: only 2/19 drifting pairs rescued.
- Harm check: 9/28 already-good answers were harmed, meaning dragged below 0.65.

Conclusion for the report: on SCD's actual target metric, `reference_scd` is a confirmed, strong, mechanism-validated success, directly consistent with the paper's central claim and exact hyperparameters. This does not need the official NIM RAGAS scoring to be considered final. It is already final.

## Known Issue Fixed This Session

`experiments/analyzers/scd_language_adherence.py`'s `conclusion` field used to be a hardcoded static string that always said "Null result..." regardless of the actual computed statistics. It happened to be accidentally correct for the old `penalty_additive` v1 data, which genuinely was null, but it was silently wrong/misleading in general and would have mis-described `reference_scd`'s clearly positive result as "null" had it not been fixed.

This was fixed this session: `report["conclusion"]` is now computed dynamically from the real statistics via a new `_conclusion(...)` function, using explicit thresholds (`>=0.05` delta + strong win ratio -> positive; `<=-0.05` -> negative; between `-0.05` and `0.05` -> null). The JSON schema/keys are otherwise unchanged. Verified: re-running the fixed script against both the old v1 file and the new `reference_scd` file produces the correct, data-consistent conclusion text in both cases. `ruff check` and `black --check` both pass on the fixed file.

This fix has not yet been committed. Folding it into the same commit as the rest of Task 18's analysis outputs is acceptable, or it can be committed as its own small fix. The project owner has not specified which; use judgment. Do not leave it uncommitted indefinitely.

## Pending New Work: Translated BLEU/ROUGE (requested, build interrupted by local reboot)

The project owner asked to also evaluate `reference_scd` the same way the reference paper does: BLEU/ROUGE against a reference answer. This is NOT a drop-in reuse of the existing `answer_span` reference, because of a real methodological mismatch discovered this session:

- `experiments/data/query_splits/*.json`'s `answer_span` field is always **English** (extracted verbatim from the English source papers), regardless of query language.
- SCD's whole point is to push generation toward **Korean**.
- Raw BLEU/ROUGE of a correctly-Korean SCD-on answer against an English reference would mechanically score low for reasons unrelated to answer quality — the same unfairness problem the paper itself designed around with its own "Translation-Based Evaluation" baseline (translate drifted outputs back into the target language before scoring BLEU/ROUGE).

**Decision (approved by the project owner): mirror the paper's own fix.** Translate each `reference_scd` generated answer into English (via the same official NVIDIA NIM judge already used for RAGAS scoring), THEN compute BLEU/ROUGE against the existing English `answer_span`. This was approved as "option 3" of three choices presented (skip it / run it raw with heavy caveats / translate-then-score) and should run **appended after the official NIM RAGAS scoring loop finishes** on Alice — not concurrently with it, not replacing it.

### Status at this handoff: build in progress, NOT finished, NOT committed

A Codex CLI background task was writing a new file,
`experiments/evaluators/translated_bleu_rouge_runner.py`, when the project
owner's local PC reboot interrupted the calling session. That background
process runs locally (not on Alice) and does NOT survive a local reboot, so
treat this as **not done** regardless of what partial file content may or
may not exist on disk — verify from scratch:

```bash
ls -la experiments/evaluators/translated_bleu_rouge_runner.py
git status --short experiments/evaluators/translated_bleu_rouge_runner.py experiments/requirements-eval.txt
```

If the file does not exist, or exists but is incomplete/uncompiled, it must
be (re)built. Full design spec, so this can be redone from scratch without
any other context:

**New file**: `experiments/evaluators/translated_bleu_rouge_runner.py`, in
the same guarded-execution style as `experiments/evaluators/official_ragas_runner.py`
(dry-validation-only by default; real API calls only behind `--execute` +
an explicit confirm env var + API key present + deps importable).

**Reuse by import from `official_ragas_runner.py`** (same package, do not
duplicate): `JUDGE_PROVIDERS`, `JudgeConfig`, `ENV_FILE`,
`_load_key_from_env_file`, `_load_reference_map`, `load_samples` (this
already joins generation records against the query-split reference and
assigns `group` = `config_name`), `_redact_api_keys`/`NVAPI_KEY_RE`, and
the atomic JSON-write helper (check its exact name in the file — it writes
to a `.tmp` path then `os.replace()`).

**New confirm gate**: its own env var, `CONFIRM_TRANSLATED_BLEU_ROUGE_EXECUTION`
(deliberately separate from `CONFIRM_OFFICIAL_RAGAS_EXECUTION` so the two
guarded actions can never be triggered by the same flag).

**Per record**: skip records with empty `generated_answer` or missing
reference (record `error` instead of wasting a call). Otherwise call the
judge (`ChatOpenAI(base_url=judge.base_url, api_key=api_key,
model=judge.resolved_model, temperature=0.0, timeout=judge_timeout,
max_retries=...)`, same construction pattern as
`official_ragas_runner.py`) with a translation prompt: "Translate the
following text into English. Preserve technical terms, numbers, and
citations exactly. Output ONLY the translated text..." Retry on transient
failure up to `--max-retries` (default 5) with simple backoff; on final
failure, record nulls + an error string and move on — never crash the
whole run over one record.

**Scoring**: `sacrebleu.sentence_bleu(translated_answer, [reference]).score`
for BLEU (0-100 scale); `rouge_score.rouge_scorer.RougeScorer(["rouge1",
"rouge2", "rougeL"], use_stemmer=True).score(reference,
translated_answer)`, taking `.fmeasure` of each (0-1 scale), for ROUGE.
Round to 4 decimals.

**Output schema must exactly match what `experiments/analyzers/aggregate_main_scores.py`
already expects** (`judge`, `metrics: ["bleu","rouge1","rouge2","rougeL"]`,
`per_sample: [{query_id, group, bleu, rouge1, rouge2, rougeL, ...}]`) so that
existing analyzer can be reused unmodified against this new score file — no
new analyzer script should be needed. Write to
`<out_dir>/<stem>.translated_bleu_rouge.json`, with incremental atomic
writes every ~10 records (not just once at the end — this project already
lost hours of progress once this session from a script that only wrote at
the end; do not repeat that).

**New dependencies**: add to `experiments/requirements-eval.txt`:
```
sacrebleu>=2.4,<3
rouge-score>=0.1.2,<0.2
```

**Verification before commit**: `python -m py_compile
experiments/evaluators/translated_bleu_rouge_runner.py`, `--help`, and
optionally a `--execute`-free dry-validation run (zero network calls, safe)
against the reference_scd generation file. Then `ruff check` and
`black --check`. Then commit + push so Alice can `git pull` it.

### After the script exists: chaining it onto the end of the Alice run

This was requested to run automatically right after the official NIM RAGAS
scoring loop finishes, without a human needing to come back and trigger it
manually. Recommended mechanism (same nohup/disown pattern already proven
in this project): SSH to Alice and launch a small waiter wrapper that polls
for the `run_scoring_until_converged.py` process (PID 228 at last check,
re-find via `ps aux | grep run_scoring_until_converged | grep -v grep`) to
exit, THEN launches the new evaluator with `--execute`:

```bash
ssh -i ~/.alice/alice.pem -p ALICE_PORT_REDACTED -o StrictHostKeyChecking=no ALICE_USER_AT_HOST_REDACTED '
cd ~/M_RAG
git pull --ff-only origin main
nohup bash -lc "
while ps aux | grep -q \"[r]un_scoring_until_converged\"; do sleep 60; done
source ~/eval_venv/bin/activate
python -m pip install -r experiments/requirements-eval.txt --quiet
export CONFIRM_TRANSLATED_BLEU_ROUGE_EXECUTION=1
python experiments/evaluators/translated_bleu_rouge_runner.py \
  --generation-results experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl \
  --query-split decoder_main_queries \
  --judge nvidia_nim \
  --out-dir experiments/results/evaluation/main-hyde-cad-scd-reference-scd-bleu-rouge \
  --execute
" > ~/bleu_rouge_translation.log 2>&1 & disown
echo launched
'
```

Adjust the `--out-dir` if the project owner prefers a different location,
but keep it a SEPARATE directory from the RAGAS scores (this is a different
metric family, not one of the four RAGAS metrics — do not mix the two
result sets in one directory).

### How to interpret/report this metric once it lands

Unlike the OpenAI side-check, this new BLEU/ROUGE-after-translation metric
uses the SAME official NVIDIA NIM judge as the canonical RAGAS scoring, so
it is not disqualified the way the OpenAI side numbers are — but it is
still a DIFFERENT metric family (paper-methodology-matched content-overlap
metric, not a RAGAS semantic-groundedness metric) and should be presented
in the final report as an additional, clearly-labeled analysis alongside
the four RAGAS metrics, not merged into the same table. Its main value: it
lets the final report directly compare against the paper's own reported
BLEU/ROUGE-improves-alongside-language-consistency claim, using the exact
same kind of metric the paper used, on our own data. If it shows BLEU/ROUGE
improving under SCD (matching the paper's finding) while RAGAS
faithfulness/answer_relevancy show a cost (per the methodological caveat in
the Reference Paper section above), that is a coherent, reportable, and
interesting joint finding — report it exactly as observed either way, do
not force it to match the paper if the data disagrees.

## Side Artifact Warning

A separate local side run scored the same `reference_scd` generation file with OpenAI `gpt-4o-mini` instead of the official NVIDIA NIM judge. This was an informal sanity-check side reference requested directly by the project owner. It is complete, with `152` samples, `0` nulls, and a single pass after about `34` minutes.

Side outputs:

- `experiments/results/evaluation/main-hyde-cad-scd-reference-scd-openai-side/merged.ragas_scores.json`
- `experiments/results/analysis/reference_scd_openai_side/main_config_scores.csv`
- `experiments/results/analysis/reference_scd_openai_side/main_axis_effects.json`

Do not merge these OpenAI-judged side results with the official NVIDIA-NIM-judged `reference_scd` result. Do not present them as equivalent to the official result. `merge_score_passes.py` refuses to merge two score files whose judge provider/model differ, and the project's frozen methodology decision from 2026-07-03 fixes the official judge as NVIDIA NIM.

Informal OpenAI side-check `use_scd` axis numbers from `experiments/results/analysis/reference_scd_openai_side/main_axis_effects.json`:

```text
use_scd axis (informal OpenAI side-check only, NOT official):
  faithfulness       on=0.8078 off=0.8815  paired_delta=-0.0737 (n=76, +17/-30)
  answer_relevancy   on=0.7089 off=0.7788  paired_delta=-0.0699 (n=76, +22/-30)
  context_precision  on=0.9265 off=0.9187  paired_delta=+0.0079 (n=76, +7/-4)
  context_recall     on=0.9737 off=0.9605  paired_delta=+0.0132 (n=76, +1/-0)
```

This pattern, faithfulness/answer_relevancy down and context_precision/context_recall roughly flat-to-slightly-up, is the current best available signal for how SCD interacts with RAG-quality metrics. However, it is from an informal, non-canonical judge and must be re-characterized, not assumed to transfer, once the official NVIDIA-NIM result lands. Do not assume the official result will show the same pattern or magnitude. Different judge models can and do diverge on faithfulness-style semantic judgments.

This OpenAI side file exists only as an informal cross-check the project owner can eyeball. It must not appear in `experiments/reports/reference_scd_rerun_report.md` as supporting official measurement. It may at most be mentioned later as a clearly labeled, explicitly non-canonical appendix or footnote if useful for narrative context. For example, "an informal cross-check with a different judge showed a similar direction of effect, pending confirmation with the official judge" is acceptable only if the official result actually agrees in direction. If the official result disagrees, say so plainly instead.

## Canonical Files - Do Not Touch

Never overwrite or modify these files as part of the `reference_scd` scoring continuation:

- `experiments/results/main_generation/main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl`
  - Original `penalty_additive` v1 generation.
  - Different SCD implementation.
  - Already scored and already reported in `experiments/reports/phase8_scd_failure_analysis.md`.
- Any existing `*.ragas_scores.json` or analysis output belonging to that v1 run.
- `experiments/data/query_splits/*.json`
  - Frozen query splits.

Also never commit `.env`, `*.pem`, credential files, or cache files.

Do not overwrite or alter:

```text
experiments/reports/phase8_scd_failure_analysis.md
```

That is the old v1 failure/null analysis. The final `reference_scd` report is a new, separate report about a new, separate experiment.

## Done/Pending Checklist

Done:

- `reference_scd` generation completed with `152/152` records.
- That generation is committed at `17201ca`.
- `official_ragas_runner.py` diagnostics instrumentation is done: incremental writes and atomic writes.
- `run_scoring_until_converged.py` orchestrator is done.
- The diagnostics/orchestrator work was committed at `c191eba` and code-reviewed.
- Informal OpenAI `gpt-4o-mini` side reference score is complete. It is non-canonical and not blocking.
- Judge-independent `reference_scd` language-adherence analysis is complete and final: `mean_delta_on_minus_off = +0.2203`, 68/76 wins, strong drift rescue, and zero harm on already-good answers.
- `experiments/analyzers/scd_language_adherence.py` was fixed so its `conclusion` field is dynamically computed rather than hardcoded. The fix passes `ruff check` and `black --check`, but it has not yet been committed.

In progress:

- Alice NVIDIA NIM scoring loop for `main-hyde-cad-scd-reference-scd`.
- Pass 1 was at `591/608` cells, `97%`, about `59h14m` elapsed at the fresher snapshot supplied by the calling session. Verify before trusting in any later session.

Pending, in order after `~/scoring_loop.log` reports `converged: merged null count <= --null-threshold`:

1. Pull `merged.ragas_scores.json` and all `passN/` evidence directories from Alice into the local repo under:

```text
experiments/results/evaluation/main-hyde-cad-scd-reference-scd/
```

Use `scp`, `rsync`, or another non-secret file transfer method over the same SSH connection. These result files are not secrets.

2. Run analysis against the pulled official NIM `merged.ragas_scores.json`:

```bash
python experiments/analyzers/aggregate_main_scores.py
python experiments/analyzers/scd_language_adherence.py
python experiments/analyzers/null_cell_sensitivity.py
```

Write outputs to the default `experiments/results/analysis/` directory for this NIM run. Do not use a `_side` suffix for the canonical NIM analysis.

3. Write the official rerun report:

```text
experiments/reports/reference_scd_rerun_report.md
```

Detailed Task 19 report-writing instructions:

- Lead with the confirmed, final, judge-independent language-adherence result as the primary finding. This is real and does not depend on anything still pending.
- Present the four RAGAS metrics' movement under SCD as a separate characterization/interaction analysis, not as a pass/fail verdict on SCD. Use the official NVIDIA-NIM numbers once available. Pull them from the converged `merged.ragas_scores.json` on Alice, then run `experiments/analyzers/aggregate_main_scores.py` against it into the default `experiments/results/analysis/` directory.
- Cite the reference paper explicitly, including the exact hyperparameter match (`alpha=1.1`, `beta=0.9`, `Tstart=5`) as evidence of faithful reproduction.
- Explicitly include the BLEU/ROUGE-vs-RAGAS-faithfulness methodological caveat so a reader does not mistake this project's finding as contradicting the paper.
- Explicitly contrast against the old `penalty_additive` v1 result already in `experiments/reports/phase8_scd_failure_analysis.md`, using the side-by-side language-adherence numbers above to make the implementation-gap causal story concrete: weak/no-boost/no-warmup -> null-to-harmful; paper-faithful implementation -> strong, safe positive effect.
- Report the RAGAS-metric characterization honestly even if the official NIM numbers confirm a real faithfulness/relevancy cost. Per the project owner's explicit standing instruction, do not sugar-coat or spin a negative characterization result. A real trade-off, honestly reported alongside a confirmed language-adherence win, is a legitimate and publishable thesis finding; it does not need to be framed as an overall "failure."
- Must not overwrite or alter `experiments/reports/phase8_scd_failure_analysis.md` or any `penalty_additive` v1 result file.
- Use the project's exact established phrasing where relevant to backbone/retrieval description:
  - "HyDE is dense branch within fixed hybrid backbone"
  - "weighted RRF, dense 0.6 / BM25 0.4"
  - "exact single-sequence CAD for greedy decoding"
- Must not present the OpenAI side-check numbers as if they were the official result. They may appear only as a clearly labeled, explicitly non-canonical footnote/appendix if useful for narrative context and only with correct directionality relative to the official result.
- The project's established convention is to delegate code/doc-writing to Codex CLI, then have the orchestrating session review the output before accepting it. If using that convention for Task 19, pass this runbook into the delegated session and require it to preserve the boundaries above.

4. Final verification before commit/push:

```bash
python -m pytest tests/backend experiments/tests
python -m ruff check .
python -m black --check <touched-python-files>
```

Adjust command scope to the files actually touched, but include both `tests/backend` and `experiments/tests` for the final verification. Commit and push only intended files. Never stage or commit `.env`, `*.pem`, credential files, or cache files.

## Final Commit Scope Guidance

Before committing, inspect the worktree and stage only intended files. Expected intended files may include:

- Pulled official scoring artifacts under `experiments/results/evaluation/main-hyde-cad-scd-reference-scd/`
- Official analysis outputs under `experiments/results/analysis/`
- `experiments/reports/reference_scd_rerun_report.md`
- The fixed `experiments/analyzers/scd_language_adherence.py`
- This runbook, if the project owner wants it committed with the handoff/report updates

Do not stage unrelated local changes, local secrets, key files, caches, or any old v1 artifact changes. If unrelated worktree changes exist, leave them alone and report them separately.
