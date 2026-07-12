# Reference SCD Rerun Report

This report records the corrected `reference_scd` rerun: the paper-faithful
Soft Constrained Decoding implementation evaluated after the earlier
`penalty_additive` v1 SCD mode was shown to be a null result in
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md).

The final supported result is narrower than the initial interpretation of this
artifact. `reference_scd` strongly improves direct Korean-language adherence.
The complete `gpt-4o` score panel is retained as a protocol-specific sensitivity
analysis, not as an isolated causal estimate of SCD's RAG-quality effect. A later
symmetric bilingual follow-up removes the earlier SCD-on-only preprocessing
correlation on 38 identical-context HyDE-off pairs. It leaves faithfulness
directionally unresolved. Its `gpt-4o` answer-relevancy intervals are negative, but
fixed `gpt-4.1-2025-04-14` does not reproduce nonzero intervals. No judge-robust
nonzero RAG-quality effect is established.

## 1. Executive summary

`reference_scd` is a literal reference-paper implementation of Soft Constrained
Decoding: multiplicative target-language boost `alpha`, multiplicative
distractor-language penalty `beta`, and cold-start warm-up until `T_start`.
This differs from the earlier `penalty_additive` v1 mode, which was
additive-only, had no target-language boost, and had no warm-up. That v1 mode is
already reported as a null result in
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md).

On its target metric, Korean-language adherence, `reference_scd` shows a strong,
judge-independent improvement because the ratio is computed directly from the
generated text. It does not eliminate drift in every answer: 15/26 threshold
drifts are rescued, 12/76 SCD-on answers remain below 0.5, and 3/76 pairs decline.

The `gpt-4o` panel contains 152 scored samples and 0/608 null metric cells. Under
that exact preprocessing protocol, SCD-on cells have lower faithfulness,
answer_relevancy, and context_recall and higher context_precision. Those deltas
are descriptive protocol associations. Only SCD-on contexts were translated,
all answer-key references remained English, and some paired HyDE-on records had
different retrieval contexts, so the panel does not identify SCD's causal
RAG-quality effect.

The stricter bilingual follow-up applies one score-independent normalization policy
to all four HyDE-off conditions and retains 0/304 null metric cells across the English
and Korean panels. Query-clustered 95% intervals overlap zero for faithfulness in both
languages. Answer relevancy is lower in both: English -0.0910
[-0.1725, -0.0240] and Korean -0.0752 [-0.1501, -0.0138]. This is a possible
trade-off signal under the protocol, not an unbiased causal estimate, because
normalization is post-generation and the same `gpt-4o` model normalizes and judges.
A fixed `gpt-4.1-2025-04-14` cross-judge then scores the same 304 cells without
nulls. Its English -0.0327 [-0.0851, +0.0129] and Korean -0.0356
[-0.1149, +0.0315] answer-relevancy intervals overlap zero. The nonzero cost is
therefore not judge-robust.

## 2. Reference paper: citation and verified fidelity

Reference: **Language Drift in Multilingual Retrieval-Augmented Generation:
Characterization and Decoding-Time Mitigation**. Bo Li, Zhenghua Xu, Rui Xie.
Hebei University of Technology / Peking University. arXiv:2511.09984. Code:
https://github.com/pkuserc/SCD

Direct inspection of the paper's full PDF text verified the formula. Given raw
logits `z(t)` at decoding step `t`, and a vocabulary partition into `Vtarget`,
`Vneutral`, and `Vdistractor`:

| Vocabulary class | Adjusted logit |
|---|---|
| `i in Vtarget` | `alpha * z(t)_i`, with `alpha > 1.0` |
| `i in Vneutral` | unchanged |
| `i in Vdistractor` | `beta * z(t)_i`, with `beta < 1.0` |

The paper also applies cold-start smoothing: constraints are inactive until
decoding step `Tstart`.

This exactly matches this repository's `reference_scd` implementation in
[`backend/modules/scd_decoder.py`](../../backend/modules/scd_decoder.py).

The hyperparameters also match. The paper states: "We empirically find moderate
settings (alpha = 1.1, beta = 0.9, Tstart = 5) to balance language fidelity and
semantic fluency in SCD." This repository's `reference_scd` generation run used
the identical values:

```text
--scd-alpha 1.1 --scd-beta 0.9 --scd-t-start 5
```

This is full hyperparameter fidelity, not only formula fidelity.

The paper evaluates three datasets, HotpotQA, MuSiQue, and DuReader; two
backbones, LLaMA3-8B-Instruct and Qwen2.5-7B-Instruct; and three metrics: BLEU
(mean of BLEU-1/2/3), ROUGE (mean of ROUGE-1/2/L), and Language Consistency
(LC). Its baselines are Prompted Language Instruction (PLI) and
Vocabulary-Restricted Decoding (VRD).

The paper's headline result says SCD "consistently improves" language
consistency and content quality, and it presents target-language alignment as a
support for coherent and accurate reasoning rather than a hindrance. One
verified example is ZH-EN HotpotQA, where SCD improves LC from 68.4% to 90.6%,
BLEU from 0.086 to 0.155, and ROUGE from 0.182 to 0.306 relative to PLI.

The same paper also shows that VRD, a hard vocabulary constraint, incurs a real
quality cost in its own data: shorter, degraded outputs, sometimes
underperforming even PLI on ROUGE. The paper's point is that SCD's soft design
specifically avoids the cost that hard constraints incur. No RAG-groundedness or
faithfulness-style metric appears anywhere in the paper.

## 3. Confirmed result: language adherence

Source:
[`experiments/results/analysis/reference_scd_language_adherence.json`](../results/analysis/reference_scd_language_adherence.json).
This was computed directly from generated-answer Korean-character ratio. No LLM
judge is involved, so this result is final regardless of which judge scores the
RAGAS metrics.

`reference_scd` produced a mean paired delta of **+0.2203** across 76 matched
pairs, measured as SCD-on minus SCD-off. SCD-on was more Korean in 68 of 76
pairs, less Korean in only 3 of 76 pairs, with 5 ties.

At the 0.5 Korean-ratio threshold, 26 pairs were drifting with SCD off.
`reference_scd` raised their mean from 0.2515 to 0.5639 and fully rescued 15 of
26 past the threshold.

At the 0.3 threshold, 12 pairs were drifting. `reference_scd` raised their mean
from 0.0667 to 0.3843 and rescued 6 of 12.

The harm check is also clean. Of 20 pairs already at least 0.7 Korean with SCD
off, zero were dragged below 0.65 by SCD-on.

The direct result is robust to retrieval identity. All 38 HyDE-off SCD pairs have
byte-identical retrieved contexts, and their mean Korean-ratio delta is +0.2198.
This supports the language-control conclusion without the HyDE-on retrieval
variance discussed in Section 4.

The old `penalty_additive` v1 result is different and should not be carried
forward as a final reference-SCD claim. Its source is
[`experiments/results/analysis/scd_language_adherence.json`](../results/analysis/scd_language_adherence.json),
and it is already reported in
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md). v1 had a mean
paired delta of **-0.0137**, approximately null; win/loss of 22/24, near
coin-flip; only 2 of 19 drifting pairs rescued; and real harm, with 9 of 28
already-good answers dragged below 0.65.

| Metric | v1 (`penalty_additive`) | `reference_scd` |
|---|---:|---:|
| Mean paired delta | -0.0137 | **+0.2203** |
| Win / loss (of 76) | 22 / 24 | **68 / 3** |
| Drift rescue @0.5 | 2/19 | **15/26** |
| Predefined harm (baseline >=0.7 to SCD-on <0.65) | 9/28 | **0/20** |

On SCD's target metric, `reference_scd` is a confirmed strong improvement,
consistent with the paper's formula and hyperparameters. The 0/20 value is only
the predefined threshold-crossing check; it does not mean that no pair declined.
The direct language conclusion does not depend on the RAGAS panel below.

## 4. Methodology note: why RAG-quality needed a special design

The evaluation attempted to reduce cross-lingual judging difficulty by translating
retrieved contexts to Korean for SCD-on records only, using
[`experiments/evaluators/translate_context_for_scd.py`](../evaluators/translate_context_for_scd.py).
Generated answers were not modified. This produced a useful sensitivity panel,
but not a fully language-matched controlled comparison.

The reason is observable in the retained artifacts. SCD-off answers were not
uniformly English: 50/76 had Korean ratio >=0.5. Ground-truth references remained
English. Translation preprocessing was perfectly correlated with SCD, 20/380
translated SCD-on chunk occurrences contained no Hangul, and one five-chunk record
remained byte-for-byte English despite success metadata. Also, only 51/76 original
SCD pairs shared identical retrieval contexts; HyDE-on retrieval differed in 25/38
pairs. Structural translation success therefore does not establish semantic
language matching or isolate decoder behavior.

RAGAS 0.2.15 further constrains interpretation: answer_relevancy uses the question
and generated answer but not context; context_precision and context_recall use
question/context/reference but not the generated answer. Only faithfulness uses
the generated answer together with context. Context-metric deltas cannot therefore
be described as decoder-caused SCD quality effects.

The retrieval and decoding backbone remained the project setup under test:
HyDE is dense branch within fixed hybrid backbone, using weighted RRF, dense 0.6
/ BM25 0.4. CAD uses exact single-sequence CAD for greedy decoding. SCD is the
paper-faithful `reference_scd` mode described above.

Implementation details:

| Detail | Verified result |
|---|---|
| Context deduplication key | Exact context content |
| Reason for content deduplication | HyDE-on retrieval was not perfectly deterministic across nominally identical query and HyDE settings |
| HyDE-off retrieval | Fully deterministic/shared |
| Unique context groups | 48 |
| Total chunks translated | 240 |
| Translation model | `gpt-4o` |
| Translation failures | 0 |
| SCD-on records excluded | 0 |
| SCD-on records with translated context | 76/76 |

The original assumption that contexts could be deduplicated by `(query_id,
use_hyde)` was rejected because retrieval for HyDE-on records was found not to
be perfectly deterministic across the original generation run. HyDE's
hypothetical-document generation step introduces retrieval variance even for
nominally identical query+HyDE-setting pairs. Content-based deduplication
therefore produced the correct comparison groups.

Any record whose context translation failed was designed to be excluded from the
pipeline entirely. The pipeline never silently falls back to untranslated
context. In this run, no record was excluded.

## 5. Complete `gpt-4o` sensitivity panel

The judge for this retained sensitivity panel is OpenAI `gpt-4o`, not NVIDIA NIM.

The judge switch is specific to this experiment track and was made for
empirically demonstrated reliability reasons. An earlier NVIDIA NIM attempt,
using the project's originally selected judge from the 2026-07-03 decision, ran
for over 60 hours, completed pass 1 with a 38.6% null rate (235/608 cells), and
was abandoned after the underlying Alice Cloud instance was deleted mid-run.

`gpt-4o` then converged fully: null 0/608 in approximately 2 hours. Pass 1 took
about 98 minutes. Pass 2 retried 38 still-null pairs and took about 27 minutes.

This means `reference_scd`'s RAG-quality metrics are not directly numerically
comparable to any other experiment in this project scored under NVIDIA NIM.
There are no converged NVIDIA NIM RAG-quality scores for `reference_scd`
specifically, because NIM never converged for it. This judge switch does not
affect the language-adherence comparison against v1 in Section 3, which is
judge-independent.

### Full 8-config table

152 samples total, 19 per config. All metrics converged, with 0 nulls.

| Config | HyDE | CAD | SCD | faithfulness | answer_relevancy | context_precision | context_recall |
|---|:-:|:-:|:-:|---:|---:|---:|---:|
| no_decoder_control | off | off | off | 0.8159 | 0.8201 | 0.8343 | 1.0000 |
| cad_only | off | on | off | 0.8181 | 0.7485 | 0.8321 | 0.9474 |
| scd_only | off | off | on | 0.7906 | 0.7758 | 0.8512 | 0.9474 |
| cad_scd | off | on | on | 0.7792 | 0.6556 | 0.8446 | 0.7895 |
| no_decoder_control | on | off | off | 0.8892 | 0.8504 | 0.7664 | 0.9474 |
| cad_only | on | on | off | 0.9230 | 0.7507 | 0.7988 | 0.8947 |
| scd_only | on | off | on | 0.8171 | 0.7614 | 0.8135 | 0.8947 |
| cad_scd | on | on | on | 0.8674 | 0.7483 | 0.8422 | 0.8947 |

Aggregate over all 152 samples:

| Metric | Aggregate |
|---|---:|
| faithfulness | 0.8376 |
| answer_relevancy | 0.7639 |
| context_precision | 0.8229 |
| context_recall | 0.9145 |

### Axis effects

Paired deltas are computed over 76 matched pairs each. Wins/losses count pairs
where `|delta| > 0.01`.

| Axis | faithfulness | answer_relevancy | context_precision | context_recall |
|---|---:|---:|---:|---:|
| use_hyde | +0.0732 (40W/24L) | +0.0277 (27W/19L) | -0.0353 (27W/23L) | -0.0132 (5W/6L) |
| use_cad | +0.0187 (31W/27L) | -0.0762 (24W/34L) | +0.0131 (14W/9L) | -0.0658 (2W/7L) |
| **use_scd** | **-0.0480 (28W/30L)** | **-0.0571 (22W/32L)** | **+0.0300 (13W/7L)** | **-0.0658 (2W/7L)** |

Null-cell sensitivity is trivial. There are 0 null cells out of 608, so no
sensitivity analysis is meaningful: there is no missing data to be sensitive to.

### Protocol-level characterization

HyDE raises faithfulness clearly: +0.073, the largest positive effect of any
axis on any metric. It also costs some context_precision (-0.035), which is a
classic recall/precision trade-off pattern. Broader retrieval pulls in more
relevant support, but also some noise.

CAD causes the single largest negative effect of any axis/metric pair:
answer_relevancy -0.076, with 34 losses. It only marginally helps faithfulness
(+0.019). This is consistent with contrastive decoding over-anchoring generation
to retrieved context at some cost to direct question-relevance.

Under this protocol, SCD-on cells differ by faithfulness -0.048,
answer_relevancy -0.057, context_recall -0.066, and context_precision +0.030.
The answer_relevancy difference is a direct question-answer score association;
the other three metrics are exposed to the asymmetric context translation, and
the two context metrics do not use the generated answer at all. These values are
useful for sensitivity analysis, not as a four-metric SCD effect estimate.

### Per-config characterization

`hyde_off__no_decoder_control` is the clean no-intervention baseline. It has
the highest context_recall of any config, 1.0000, and strong answer_relevancy,
0.8201. Every other config should be read against this floor.

`hyde_off__cad_only` keeps faithfulness essentially flat against the hyde-off
baseline, 0.8181 versus 0.8159, a +0.0022 delta. Its main cost is
answer_relevancy, 0.7485 versus 0.8201, a -0.0716 delta, with smaller drops in
context_precision (-0.0022) and context_recall (-0.0526). CAD without HyDE is
therefore not a faithfulness win by itself; its visible trade-off is
question-relevance.

`hyde_off__scd_only` shows a lower-score association for SCD-on without HyDE: faithfulness
falls from 0.8159 to 0.7906 (-0.0253), answer_relevancy falls from 0.8201 to
0.7758 (-0.0443), and context_recall falls from 1.0000 to 0.9474 (-0.0526).
The offsetting benefit is context_precision, 0.8512 versus 0.8343 (+0.0169),
which matches the protocol-level axis table. It is not an isolated causal estimate.

`hyde_off__cad_scd` is the single riskiest combination in the matrix. It is the
worst config for answer_relevancy, 0.6556, and the worst hyde-off config for
context_recall, 0.7895, a full -0.2105 below the hyde-off baseline. This is the
only config where the CAD-on and SCD-on answer_relevancy score differences
appear to compound rather than partially cancel: CAD-only is -0.0716 from the
hyde-off baseline, SCD-only is -0.0443, and CAD+SCD is -0.1645.

`hyde_on__no_decoder_control` shows HyDE's clean lift when no decoder control is
active. Compared with the hyde-off baseline, faithfulness rises from 0.8159 to
0.8892 (+0.0733) and answer_relevancy rises from 0.8201 to 0.8504 (+0.0303),
while context_precision drops from 0.8343 to 0.7664 (-0.0679) and
context_recall drops from 1.0000 to 0.9474 (-0.0526). This config is the main
source of the axis-level HyDE faithfulness gain and precision trade-off.

`hyde_on__cad_only` reaches the highest faithfulness of any config, 0.9230.
Compared with `hyde_off__cad_only`, HyDE adds +0.1049 faithfulness, while
answer_relevancy is nearly unchanged, 0.7507 versus 0.7485 (+0.0022). HyDE's
faithfulness boost and CAD's marginal faithfulness boost appear to stack
constructively here, even though CAD alone under hyde-off only adds +0.0022
faithfulness.

`hyde_on__scd_only` shows that HyDE cushions the absolute faithfulness level of
the SCD-only condition: 0.8171 versus 0.7906 for `hyde_off__scd_only`, a +0.0265
matched-pair lift. Answer_relevancy does not receive the same protection:
0.7614 versus 0.7758, a -0.0144 matched-pair delta. Thus HyDE's protective
effect around SCD is specific to faithfulness here, not general across metrics.

`hyde_on__cad_scd`, with all three axes active, recovers faithfulness relative
to `hyde_off__cad_scd`, 0.8674 versus 0.7792 (+0.0882). The answer_relevancy
score remains low at 0.7483, even though it is +0.0927 above
`hyde_off__cad_scd`; it is still -0.1021 below `hyde_on__no_decoder_control`.
Under HyDE, the CAD+SCD cell has a smaller faithfulness gap than without HyDE,
while the lower answer_relevancy association persists.

Across the four matched HyDE-on/off pairs with identical CAD/SCD settings, every
HyDE-on variant has higher faithfulness than its matched HyDE-off variant:
+0.0733, +0.1049, +0.0265, and +0.0882. The same uniform pattern does not hold
for answer_relevancy: the matched deltas are +0.0303, +0.0022, -0.0144, and
+0.0927. HyDE therefore consistently cushions faithfulness levels in these
matched comparisons, including under CAD and SCD constraints, but it does not
provide the same uniform answer_relevancy cushion.

### Why this is not a causal faithfulness decomposition

The project has two stated core goals: Korean-language adaptation and RAG
groundedness, approximated here by RAGAS `faithfulness`. The following values
describe this scoring protocol; they do not decompose causal contributions.

The axis-level faithfulness effects from the table above are:

| Axis | Paired faithfulness delta |
| --- | ---: |
| use_hyde | +0.0732 |
| use_cad | +0.0187 |
| use_scd | -0.0480 |

Within the panel, `hyde_on__cad_only` scores 0.9230 and
`hyde_on__cad_scd` scores 0.8674, a -0.0556 association. Because context
translation and, for many HyDE-on pairs, retrieval content also differ, this
comparison cannot show that SCD itself reduced faithfulness. Conversely, it
cannot show that SCD improved faithfulness. The later symmetric bilingual panel
adds identical retrieval contexts and uncertainty estimates; it still leaves both
faithfulness intervals overlapping zero. Independent judging and human review remain
needed for the groundedness claim.

## 6. Why this panel cannot be compared directly with the reference paper

### Different metric construct

This is the primary reason. The paper's "content quality" metric is BLEU/ROUGE:
lexical n-gram overlap with a target-language reference answer. That score
mechanically improves whenever an answer switches into the correct language,
largely independent of whether the answer's content is well grounded in
retrieved evidence.

RAGAS `faithfulness` measures something categorically different: whether the
answer's specific claims are supported by retrieved context, independent of
surface language match. The paper's claim that SCD raises BLEU/ROUGE alongside
language consistency does not imply it would also raise RAGAS-style
groundedness. These are different measurements of different things, not
competing measurements of the same thing.

### Scope gap, not a contradiction

The paper never measures RAG groundedness or faithfulness. Its metric suite is
BLEU/ROUGE/LC only. This report's finding is therefore not a refutation of the
paper's claim so much as a measurement in a space the paper's own evaluation
never covered.

### Setup differences may amplify the effect here

This project's corpus is dense academic and technical text: terminology,
citations, and exact figures matter. In that domain, forcing a language switch
plausibly risks more precision loss than in the paper's general multi-hop QA
benchmarks, HotpotQA, MuSiQue, and DuReader.

The paper's hyperparameters, `alpha=1.1`, `beta=0.9`, and `Tstart=5`, were tuned
on LLaMA3-8B-Instruct and Qwen2.5-7B-Instruct. This project uses a different
backbone, Mi:dm. There is no guarantee the same fixed hyperparameter values sit
at the identical fidelity/control balance point for a different model.

This report does not claim the paper is wrong. It records a protocol-specific
RAGAS panel in a metric space the paper did not test, under a different domain
and backbone. Its causal quality effect remains unresolved.

## 7. Overall conclusion

`reference_scd` substantially improves direct Korean-language adherence and
rescues 15/26 threshold drifts. The predefined severe-harm transition is 0/20,
although 3/76 pairs decline and 12/76 SCD-on outputs remain below 0.5. This is
the primary confirmed finding.

The `gpt-4o` panel is complete and reproducible from the retained artifacts, but
its asymmetric translation and retrieval differences prevent a causal SCD
RAG-quality conclusion. Report the numeric panel only with that qualification.

The completed symmetric follow-up materially tightens that boundary: all 38 HyDE-off
SCD contrasts have identical retrieval contexts, both target languages use the same
field-level normalization policy, and uncertainty is reported by 19-query clustered
bootstrap. It does not identify a directional faithfulness effect. `gpt-4o` identifies
a negative answer-relevancy interval in both language panels, concentrated in the
CAD-on stratum, but fixed `gpt-4.1-2025-04-14` leaves every corresponding interval
overlapping zero. Korean answer translation was also realized for 23/38 SCD-off
versus 11/38 SCD-on answers despite the fixed rule. The supported conclusion is no
judge-robust nonzero RAG-quality effect, not a causal or deployment verdict. See
[reference_scd_symmetric_cross_judge_report.md](reference_scd_symmetric_cross_judge_report.md)
and [reference_scd_symmetric_input_audit.md](reference_scd_symmetric_input_audit.md).

## 8. Appendix: informal gpt-4o-mini cross-check (non-canonical)

This used a different, weaker judge model (`gpt-4o-mini`, not the official
`gpt-4o`).

Critically, this cross-check was run BEFORE the context-translation fix
described in Section 4. It used the ORIGINAL, untranslated generation file, so
it has the SAME cross-lingual judging confound that Section 4 was specifically
built to eliminate. It must not be read as confirming or refuting the Section 5
result with equivalent rigor; it is included only for historical completeness
and rough directional triangulation.

Source:
[`experiments/results/analysis/reference_scd_openai_side/main_config_scores.csv`](../results/analysis/reference_scd_openai_side/main_config_scores.csv)
and
[`experiments/results/evaluation/main-hyde-cad-scd-reference-scd-openai-side/`](../results/evaluation/main-hyde-cad-scd-reference-scd-openai-side/).

| Config | faithfulness | answer_relevancy | context_precision | context_recall |
|---|---:|---:|---:|---:|
| hyde_off__no_decoder_control | 0.8443 | 0.8370 | 0.9330 | 0.9474 |
| hyde_off__cad_only | 0.8653 | 0.6614 | 0.9432 | 0.9474 |
| hyde_off__scd_only | 0.8216 | 0.7177 | 0.9330 | 0.9474 |
| hyde_off__cad_scd | 0.7595 | 0.6142 | 0.9330 | 0.9474 |
| hyde_on__no_decoder_control | 0.9115 | 0.8603 | 0.8803 | 0.9474 |
| hyde_on__cad_only | 0.9047 | 0.7566 | 0.9181 | 1.0000 |
| hyde_on__scd_only | 0.8086 | 0.7609 | 0.9238 | 1.0000 |
| hyde_on__cad_scd | 0.8413 | 0.7430 | 0.9164 | 1.0000 |

Source:
[`experiments/results/analysis/reference_scd_openai_side/main_axis_effects.json`](../results/analysis/reference_scd_openai_side/main_axis_effects.json).

| Metric | `use_scd` paired_delta | n | Wins/losses |
|---|---:|---:|---:|
| faithfulness | -0.0737 | 76 | +17/-30 |
| answer_relevancy | -0.0699 | 76 | +22/-30 |
| context_precision | +0.0079 | 76 | +7/-4 |
| context_recall | +0.0132 | 76 | +1/-0 |

Both panels show lower answer_relevancy and faithfulness scores for SCD-on cells,
which is useful directional triangulation. They are not equivalent controls and
do not establish causality. Context_recall even changes direction, from +0.0132
to -0.0658, illustrating sensitivity to the text and language presented to the
judge.

A translated-BLEU/ROUGE evaluation was also queued to run automatically on the
Alice Cloud instance after the NIM RAGAS scoring process exited. That metric
would have translated SCD-on answers to English via NVIDIA NIM, then scored
against the English `answer_span` reference, mirroring the reference paper's own
"Translation-Based Evaluation" method; the runner is
[`experiments/evaluators/translated_bleu_rouge_runner.py`](../evaluators/translated_bleu_rouge_runner.py).
It never completed because the Alice instance was deleted before that stage
finished. It remains future work because the current RAGAS sensitivity panel
does not answer the causal content-quality question.
