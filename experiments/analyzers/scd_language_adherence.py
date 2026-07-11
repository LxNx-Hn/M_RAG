"""Direct Korean-language-adherence analysis for the SCD axis.

RAGAS's four metrics do not measure language adherence, which is SCD's actual
target. This computes the Korean-character ratio of every main-generation
answer and the paired SCD-on vs SCD-off effect, including the fair conditional
tests (does SCD rescue drifting answers? does it harm already-Korean answers?).

Descriptive only — no API, no model, no judge.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results" / "analysis" / "scd_language_adherence.json"

# SCD-off -> SCD-on pairs, matched on HyDE and CAD.
SCD_PAIRS = [
    ("hyde_off__no_decoder_control", "hyde_off__scd_only"),
    ("hyde_off__cad_only", "hyde_off__cad_scd"),
    ("hyde_on__no_decoder_control", "hyde_on__scd_only"),
    ("hyde_on__cad_only", "hyde_on__cad_scd"),
]


def korean_ratio(text: str) -> float:
    hangul = sum(
        1
        for c in text
        if 0xAC00 <= ord(c) <= 0xD7A3
        or 0x1100 <= ord(c) <= 0x11FF
        or 0x3130 <= ord(c) <= 0x318F
    )
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    denom = hangul + latin
    return round(hangul / denom, 4) if denom else 0.0


def _conclusion(
    mean_delta: float,
    n_pairs: int,
    scd_on_more_korean: int,
    scd_on_less_korean: int,
    tie: int,
    rescue_at_0_5: dict[str, Any],
    rescue_at_0_3: dict[str, Any],
    harm_on_already_korean: dict[str, int],
) -> str:
    harm_count = harm_on_already_korean["dragged_below_0.65"]
    good_pairs = harm_on_already_korean["good_pairs_ge_0.7"]
    harm_text = (
        f"no already-Korean harm observed ({harm_count}/{good_pairs} dragged "
        "below 0.65)"
        if harm_count == 0
        else f"{harm_count}/{good_pairs} already-Korean pairs dragged below 0.65"
    )
    rescue_text = (
        f"at the 0.5 threshold, {rescue_at_0_5['rescued_to_threshold']}/"
        f"{rescue_at_0_5['drift_pairs']} drifting pairs were rescued; "
        f"at 0.3, {rescue_at_0_3['rescued_to_threshold']}/"
        f"{rescue_at_0_3['drift_pairs']} were rescued"
    )
    metric_scope = (
        "This is a language-adherence-only measurement based on generated-text "
        "Korean character ratio, independent of any RAGAS judge; it does not by "
        "itself measure faithfulness, answer_relevancy, context_precision, or "
        "context_recall, which require separate judge-scored metrics to "
        "interpret trade-offs."
    )

    clear_positive = (
        mean_delta >= 0.05
        and scd_on_more_korean > 2 * scd_on_less_korean
        and scd_on_more_korean > n_pairs / 2
    )
    if clear_positive:
        effect_text = (
            "SCD shows a real positive Korean-adherence effect in this run: "
            f"mean paired delta is {mean_delta:+.4f}, SCD-on is more Korean in "
            f"{scd_on_more_korean}/{n_pairs} pairs versus less Korean in "
            f"{scd_on_less_korean}/{n_pairs} pairs ({tie} ties), {rescue_text}, "
            f"and {harm_text}."
        )
    elif mean_delta <= -0.05:
        effect_text = (
            "SCD shows a negative Korean-adherence effect in this run: "
            f"mean paired delta is {mean_delta:+.4f}, SCD-on is less Korean in "
            f"{scd_on_less_korean}/{n_pairs} pairs versus more Korean in "
            f"{scd_on_more_korean}/{n_pairs} pairs ({tie} ties), {rescue_text}, "
            f"and {harm_text}."
        )
    elif -0.05 < mean_delta < 0.05:
        effect_text = (
            "SCD shows no reliable Korean-adherence effect in this run: "
            f"mean paired delta is {mean_delta:+.4f}, SCD-on is more Korean in "
            f"{scd_on_more_korean}/{n_pairs} pairs and less Korean in "
            f"{scd_on_less_korean}/{n_pairs} pairs ({tie} ties), {rescue_text}, "
            f"and {harm_text}."
        )
    else:
        effect_text = (
            "SCD has a non-null mean Korean-adherence shift, but the pair-level "
            "win/loss split is not strong enough to call it a clear positive "
            "effect under the conservative threshold used here: mean paired "
            f"delta is {mean_delta:+.4f}, SCD-on is more Korean in "
            f"{scd_on_more_korean}/{n_pairs} pairs and less Korean in "
            f"{scd_on_less_korean}/{n_pairs} pairs ({tie} ties), {rescue_text}, "
            f"and {harm_text}."
        )

    return f"{effect_text} {metric_scope}"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--generation", required=True)
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()

    recs = [
        json.loads(line)
        for line in Path(args.generation).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    kr = {
        (r["config_name"], r["query_id"]): korean_ratio(r["generated_answer"])
        for r in recs
    }
    qids = sorted({r["query_id"] for r in recs})
    all_vals = sorted(kr.values())

    deltas: list[float] = []
    off_all: list[float] = []
    on_all: list[float] = []
    for off, on in SCD_PAIRS:
        for q in qids:
            b, a = kr.get((off, q)), kr.get((on, q))
            if b is None or a is None:
                continue
            deltas.append(a - b)
            off_all.append(b)
            on_all.append(a)

    def conditional(threshold: float) -> dict[str, Any]:
        offs, ons, rescued = [], [], 0
        for off, on in SCD_PAIRS:
            for q in qids:
                b, a = kr.get((off, q)), kr.get((on, q))
                if b is None or a is None or b >= threshold:
                    continue
                offs.append(b)
                ons.append(a)
                if a >= threshold:
                    rescued += 1
        return {
            "threshold": threshold,
            "drift_pairs": len(offs),
            "scd_off_mean": round(statistics.mean(offs), 4) if offs else None,
            "scd_on_mean": round(statistics.mean(ons), 4) if ons else None,
            "rescued_to_threshold": rescued,
        }

    hurt = sum(
        1
        for off, on in SCD_PAIRS
        for q in qids
        if kr.get((off, q), 0) >= 0.7 and kr.get((on, q), 1) < 0.65
    )
    good_n = sum(1 for off, _ in SCD_PAIRS for q in qids if kr.get((off, q), 0) >= 0.7)

    report = {
        "source_generation": args.generation,
        "answers": len(recs),
        "korean_ratio_distribution": {
            "min": all_vals[0],
            "p10": all_vals[len(all_vals) // 10],
            "median": all_vals[len(all_vals) // 2],
            "max": all_vals[-1],
            "below_0.5": sum(1 for v in all_vals if v < 0.5),
        },
        "scd_paired_effect": {
            "n_pairs": len(deltas),
            "mean_delta_on_minus_off": round(statistics.mean(deltas), 4),
            "scd_on_more_korean": sum(1 for d in deltas if d > 0.02),
            "scd_on_less_korean": sum(1 for d in deltas if d < -0.02),
            "tie": sum(1 for d in deltas if abs(d) <= 0.02),
        },
        "conditional_rescue": [conditional(0.5), conditional(0.3)],
        "harm_on_already_korean": {
            "good_pairs_ge_0.7": good_n,
            "dragged_below_0.65": hurt,
        },
    }
    report["conclusion"] = _conclusion(
        mean_delta=report["scd_paired_effect"]["mean_delta_on_minus_off"],
        n_pairs=report["scd_paired_effect"]["n_pairs"],
        scd_on_more_korean=report["scd_paired_effect"]["scd_on_more_korean"],
        scd_on_less_korean=report["scd_paired_effect"]["scd_on_less_korean"],
        tie=report["scd_paired_effect"]["tie"],
        rescue_at_0_5=report["conditional_rescue"][0],
        rescue_at_0_3=report["conditional_rescue"][1],
        harm_on_already_korean=report["harm_on_already_korean"],
    )
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
