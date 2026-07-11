# Reference SCD Rerun Report

This report records the corrected `reference_scd` rerun: the paper-faithful
Soft Constrained Decoding implementation evaluated after the earlier
`penalty_additive` v1 SCD mode was shown to be a null result in
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md).

The result is a real trade-off. `reference_scd` decisively fixes the target
problem it was built for, Korean-language adherence. Under a language-matched
RAG-quality evaluation, it also carries a measurable cost on three of four RAGAS
metrics. Both findings are reported here as final.

## 1. Executive summary

`reference_scd` is a literal reference-paper implementation of Soft Constrained
Decoding: multiplicative target-language boost `alpha`, multiplicative
distractor-language penalty `beta`, and cold-start warm-up until `T_start`.
This differs from the earlier `penalty_additive` v1 mode, which was
additive-only, had no target-language boost, and had no warm-up. That v1 mode is
already reported as a null result in
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md).

On its actual target metric, Korean-language adherence, `reference_scd` is a
clear, strong, confirmed success. This result is judge-independent because it was
computed directly from the generated text's Korean-character ratio, not by an
LLM judge.

On RAG-quality metrics, `reference_scd` shows a real, rigorously verified cost on
three of four metrics: faithfulness, answer_relevancy, and context_recall.
Context_precision is the sole exception and moves slightly positive.

This trade-off was verified under a language-matched, cross-lingual-confound-
controlled evaluation design. The control was specifically built to rule out
judge cross-linguality noise as an alternative explanation. The RAG-quality cost
survived that control, so it is reported as a genuine finding, not a measurement
artifact.

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
| Harm on already-good answers | 9/28 harmed | **0/20 harmed** |

On SCD's actual target metric, `reference_scd` is a confirmed, strong,
mechanism-validated success, directly consistent with the paper's central claim
and exact hyperparameters. v1's null result is explained by its missing
boost/multiplicative-penalty/warm-up, already documented in
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md). Fixing those
three gaps produced the corrected result. This conclusion does not depend on
anything else in this report.

## 4. Methodology note: why RAG-quality needed a special design

When SCD succeeds, the generated answer is Korean while the retrieved context,
drawn from English source papers, remains English. RAGAS `faithfulness` and
`answer_relevancy` then require the judge LLM to do cross-lingual reasoning for
SCD-on records but same-language reasoning for SCD-off records. That asymmetry
could confound the metric independent of any real quality difference.

The approved fix was the rigorous option: translate the retrieved context to
Korean for SCD-on records only, using
[`experiments/evaluators/translate_context_for_scd.py`](../evaluators/translate_context_for_scd.py).
SCD-on is therefore judged as Korean-answer-vs-Korean-context, while SCD-off
remains English-answer-vs-English-context. The generated answer itself is never
modified for either condition. Only the comparison-side context is
language-matched.

This was chosen over translating the answer because the answer is the actual
artifact under evaluation. Translating it would risk introducing translation
artifacts into the output being judged. Translating only the reference/context
side avoids that.

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

## 5. Official RAG-quality result

The official judge for this `reference_scd` RAG-quality evaluation is OpenAI
`gpt-4o`, not NVIDIA NIM.

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

### Per-axis characterization

HyDE raises faithfulness clearly: +0.073, the largest positive effect of any
axis on any metric. It also costs some context_precision (-0.035), which is a
classic recall/precision trade-off pattern. Broader retrieval pulls in more
relevant support, but also some noise.

CAD causes the single largest negative effect of any axis/metric pair:
answer_relevancy -0.076, with 34 losses. It only marginally helps faithfulness
(+0.019). This is consistent with contrastive decoding over-anchoring generation
to retrieved context at some cost to direct question-relevance.

SCD costs three of four RAG-quality metrics: faithfulness -0.048,
answer_relevancy -0.057, and context_recall -0.066. It is the only axis with a
positive context_precision effect (+0.030). Notably, SCD's answer_relevancy cost
(-0.057) is close in direction and magnitude to CAD's (-0.076). Both
decoding-time constraint mechanisms, one for factual grounding and one for
language control, show a similar-shaped quality cost pattern. HyDE, a
retrieval-side intervention, shows a comparatively milder and more mixed
profile. This is an observed pattern in the data, not a causal mechanism claim
beyond what the data supports.

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

`hyde_off__scd_only` shows the isolated SCD cost without HyDE: faithfulness
falls from 0.8159 to 0.7906 (-0.0253), answer_relevancy falls from 0.8201 to
0.7758 (-0.0443), and context_recall falls from 1.0000 to 0.9474 (-0.0526).
The offsetting benefit is context_precision, 0.8512 versus 0.8343 (+0.0169),
which is consistent with the axis-level result that SCD is precision-positive
but quality-costly on the other RAGAS metrics.

`hyde_off__cad_scd` is the single riskiest combination in the matrix. It is the
worst config for answer_relevancy, 0.6556, and the worst hyde-off config for
context_recall, 0.7895, a full -0.2105 below the hyde-off baseline. This is the
only config where CAD's answer_relevancy cost and SCD's answer_relevancy cost
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
Under HyDE, adding CAD+SCD together costs less on faithfulness than it does
without HyDE, but the answer_relevancy cost persists.

Across the four matched HyDE-on/off pairs with identical CAD/SCD settings, every
HyDE-on variant has higher faithfulness than its matched HyDE-off variant:
+0.0733, +0.1049, +0.0265, and +0.0882. The same uniform pattern does not hold
for answer_relevancy: the matched deltas are +0.0303, +0.0022, -0.0144, and
+0.0927. HyDE therefore consistently cushions faithfulness levels in these
matched comparisons, including under CAD and SCD constraints, but it does not
provide the same uniform answer_relevancy cushion.

### Faithfulness contribution decomposition

The project has two stated core goals: Korean-language adaptation and RAG
hallucination reduction, operationalized here as RAGAS `faithfulness`. A natural
but incorrect inference would be that because the full "everything on" config,
`hyde_on__cad_scd`, beats the zero-intervention baseline on both language
adherence and faithfulness, SCD must be contributing positively to hallucination
reduction. It is not.

The axis-level faithfulness effects from the table above are:

| Axis | Paired faithfulness delta |
| --- | ---: |
| use_hyde | +0.0732 |
| use_cad | +0.0187 |
| use_scd | -0.0480 |

The direct config comparison makes the same point concrete.
`hyde_on__cad_only`, meaning HyDE+CAD with no SCD, reaches faithfulness 0.9230,
the single highest value of any of the eight configs. Adding SCD to that same
HyDE+CAD combination, `hyde_on__cad_scd`, drops faithfulness to 0.8674. That is
a -0.0556 decrease from turning SCD on while holding HyDE and CAD fixed at
"on."

Therefore, the faithfulness improvement of the "everything on" configuration
over the zero-intervention baseline, 0.8159 to 0.8674, a +0.0515 net gain, is
entirely attributable to HyDE and CAD. SCD's own isolated contribution to
faithfulness is negative across every measurement in this report: the
axis-level effect and the direct HyDE+CAD-only versus HyDE+CAD+SCD comparison.
The precise claim for this project's two stated goals is: SCD achieves the
language-adaptation goal; it does not contribute to the hallucination-reduction
goal, and in fact costs some of the faithfulness gain that HyDE and CAD produce.
The "everything on" configuration still nets out ahead of doing nothing on both
fronts only because HyDE's and CAD's combined faithfulness contribution,
+0.0732 and +0.0187, outweighs SCD's cost, -0.0480, not because SCD helps.

A secondary pattern is also worth flagging for discussion. CAD is this
project's nominal hallucination-mitigation axis: contrastive decoding, designed
to reduce hallucination by anchoring generation more strongly to retrieved
context. Yet CAD's own isolated faithfulness effect, +0.0187, is smaller than
HyDE's incidental effect, +0.0732. In this dataset, HyDE, a retrieval-side
intervention with no explicit anti-hallucination design goal, contributes more
to faithfulness than CAD does. This should be read as an observed data pattern,
not as a claim that CAD does not work; CAD's effect is positive, just smaller
than HyDE's.

## 6. Why the reference paper reports no trade-off while this report finds one

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

This report does not claim the paper is wrong. It extends measurement into a
metric space the paper never tested, RAG groundedness, under a different domain
and backbone, and finds a real cost there.

## 7. Overall conclusion

SCD, as `reference_scd`, achieves its stated goal decisively. It improves
Korean-language adherence with a strong positive effect, meaningful drift
rescue, and zero harm to already-good answers. This is fully consistent with,
and validated against, the reference paper's exact formula and hyperparameters.
It is the primary confirmed finding.

Separately, under a rigorously language-matched,
cross-lingual-confound-controlled evaluation, SCD carries a real cost on three
of four RAGAS RAG-quality metrics: faithfulness, answer_relevancy, and
context_recall. It improves context_precision.

This is not a measurement artifact. The cost survived the specific control
designed to rule out judge cross-linguality noise as an alternative explanation.
Both findings should be reported side by side. The language-control success
should not be downplayed, and the RAG-quality cost should not be softened or
buried.

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

The direction of the main finding replicates even before the
context-translation control was applied: both the informal, uncontrolled
`gpt-4o-mini` pass and the official, controlled `gpt-4o` pass show SCD costing
faithfulness and answer_relevancy, and both show context_precision as the one
metric SCD helps. This adds some incidental support that the Section 5 finding
is not solely an artifact of the specific translation methodology. However, the
official, controlled Section 5 numbers remain the ones to cite for any actual
claim, not these informal numbers. Context_recall differs in direction between
the two runs, informal +0.0132 versus official -0.0658. A plausible explanation
is that context_recall is sensitive to exactly which text, original versus
translated, the judge is asked to compare against the ground-truth reference,
but this remains an open question for future work rather than a confirmed
mechanism.

A translated-BLEU/ROUGE evaluation was also queued to run automatically on the
Alice Cloud instance after the NIM RAGAS scoring process exited. That metric
would have translated SCD-on answers to English via NVIDIA NIM, then scored
against the English `answer_span` reference, mirroring the reference paper's own
"Translation-Based Evaluation" method; the runner is
[`experiments/evaluators/translated_bleu_rouge_runner.py`](../evaluators/translated_bleu_rouge_runner.py).
It never completed because the Alice instance was deleted by the project owner
before that stage finished. This metric was deliberately not re-attempted under
the `gpt-4o` path because the context-translated RAGAS result in Section 5
already provides a rigorous, language-matched answer to the same underlying
question that BLEU/ROUGE was intended to help answer: whether SCD carries a
content-quality cost. It remains a candidate for future work if a supplementary
content-overlap metric matching the paper's own methodology is later wanted.
