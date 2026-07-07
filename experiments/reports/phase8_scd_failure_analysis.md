# Phase 8 — Why Our SCD Produced a Null Result

The main experiment found SCD (Korean-target Soft Constrained Decoding) to be a
**null factor**: no effect on the four RAGAS metrics (|Δ| ≤ 0.013) and net-null on
its own target, Korean-language adherence (paired mean Δ = **−0.014**; direct
measurement in [scd_language_adherence.json](../results/analysis/scd_language_adherence.json)).
This document explains the failure by comparing our implementation against the
reference method it is based on.

Reference: **Language Drift in Multilingual RAG: Characterization and Decoding-Time
Mitigation**, arXiv 2511.09984 (https://arxiv.org/abs/2511.09984). The reference
reports that SCD mitigates language drift; our implementation does not. The
difference is that **we implemented only a weakened fragment of the method.**

## The reference SCD has three components

1. **Distractor penalty (β)** — down-weight non-target-language tokens.
2. **Target-language boost (α > 1.0)** — *up-weight* target-language tokens.
3. **Cold-start smoothing** — delay constraint activation until step `T_start`,
   because multilingual decoders emit unstable initial output (repeated prompts,
   template/context fragments) that constraints applied from token 0 cannot fix and
   may entrench.

The reference frames drift as **decoder-level collapse** — high-frequency English
patterns dominating the target-language distribution — which is why it both boosts
the target and warms up, rather than only penalizing distractors.

## What our code actually does

`backend/modules/scd_decoder.py`, the only logit modification (line 211):

```python
scores[:, self._non_target_ids] -= self.beta   # beta = 0.3, applied every step
```

| Reference component | Our implementation | Status |
|---|---|---|
| Vocab partition (target / neutral / distractor) | present (`_build_non_target_ids`) | ✅ matches |
| β distractor penalty | **additive constant −0.3** (not the reference's multiplicative β<1.0) | ⚠️ weakened form |
| **α target-language boost** | **absent** — Korean tokens are never up-weighted | ❌ missing |
| **Cold-start smoothing (T_start)** | **absent** — penalty applied from token 0 | ❌ missing |

We implemented roughly **one third** of the method — the distractor penalty only —
and in its weakest (additive-constant) form.

## Why each gap produces the observed null

1. **No α boost → net-zero shift.** With only a small penalty on distractors and no
   promotion of Korean, the target distribution is never actively pulled up.
   Measured net Korean Δ = −0.014 (22 answers more Korean, 24 less, 30 unchanged) —
   exactly the wash expected from a one-sided, weak nudge.

2. **Additive −0.3 is too weak against confident English.** When the model commits to
   an English continuation, the logit gap to the next candidate is typically far
   larger than 0.3, so a flat subtraction does not change the greedy argmax. Evidence:
   in 6/19 matched pairs the SCD-on answer text is **byte-identical** to SCD-off (zero
   effect), and on the answers that actually drifted below 0.5 Korean, SCD rescued only
   **2/19** to ≥ 0.5 (0.237 → 0.289 mean).

3. **No warm-up → cold-start collapse is untouched.** The drift cases are exactly the
   cold-start failures the reference's warm-up targets, and they come in two forms our
   penalty cannot address:
   - *fresh-English answering* (e.g. `track1_0010`: 0.0 Korean, 1,638 chars, ~0%
     context overlap — the model simply answered in English from the start);
   - *context-copy degeneration* (e.g. `track1_0035`: 0.0 Korean, 66% of the answer is
     copied verbatim from the English context).
   Applying a constant penalty from token 0 does not pull the model out of either basin.

4. **Broad carve-outs leave English stepping-stones.** Neutral characters (digits,
   punctuation, math, brackets) and the technical whitelist (RAG, BM25, GPT, …) are
   unpenalized, and subword fragments of English words often decode to neutral-looking
   pieces — so English technical prose can proceed largely unpenalized.

5. **β never tuned for drift.** β = 0.3 was carried as a planned default; the parameter
   freeze swept only retrieval breadth, never SCD strength against a drift objective. On
   already-Korean answers the same uniform penalty even **hurt** — dragging 9/28
   answers (baseline ≥ 0.7 Korean) below 0.65 — so simply raising β is not obviously
   safe without the boost and warm-up.

## Conclusion and future work

The null result is not evidence that soft constrained decoding cannot work; it is
evidence that a **penalty-only, additive, always-on** reduction of the reference method
does not. To reproduce the reference's benefit, the implementation must add the two
missing components and fix the third:

1. add the **α > 1.0 target-language boost**;
2. use **multiplicative** logit scaling (α>1.0 on target, β<1.0 on distractor) instead
   of a flat additive penalty;
3. add **cold-start smoothing** (activate constraints at `T_start`, not token 0);
4. then tune (α, β, T_start) against the direct Korean-adherence objective.

The vocab partition already in place is reusable; the gap is entirely in the logit
adjustment and its schedule.

Sources: [arXiv 2511.09984](https://arxiv.org/abs/2511.09984).
