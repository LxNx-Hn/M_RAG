"""Offline, query-level factorial reanalysis of immutable 60-query records.

No inference/API calls. Undefined tests remain explicitly undefined, never zero.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy import stats
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/analyzers"))
from analyze_extended_validation_60 import (
    DEFAULT_NEW_GENERATION,
    DEFAULT_OLD_GENERATION,
    DEFAULT_OLD_SCORES,
    METRICS,
    korean_ratio,
    read_jsonl,
    validate_generation,
    validate_scores,
)

SCORES = [
    DEFAULT_OLD_SCORES,
    ROOT / "experiments/results/evaluation/ext60_gpt4o/merged.ragas_scores.json",
]
GEN = [DEFAULT_OLD_GENERATION, DEFAULT_NEW_GENERATION]
OUT = ROOT / "FINALDOCS/DATA/FACTORIAL_STATISTICS_60Q.json"


def summary(x):
    a = np.asarray(x, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) < 2:
        raise ValueError("Descriptive SD requires at least two observations")
    return {"n": len(a), "mean": float(a.mean()), "sd": float(a.std(ddof=1))}


def test_difference(d):
    """Two-sided test; exact zero variance is a reported singular design."""
    d = np.asarray(d, dtype=float)
    if not np.isfinite(d).all() or len(d) < 2:
        raise ValueError("Invalid contrast data")
    result = {
        **summary(d),
        "df": len(d) - 1,
        "zero_differences": int(np.count_nonzero(d == 0)),
        "difference_quantiles": np.quantile(d, [0, 0.25, 0.5, 0.75, 1]).tolist(),
    }
    if d.std(ddof=1) == 0:
        return {
            **result,
            "status": "undefined_zero_difference_variance",
            "t": None,
            "p": None,
            "dz": None,
            "wilcoxon_p": None,
            "sign_flip_p": None,
        }
    t = stats.ttest_1samp(d, 0)
    w = stats.wilcoxon(d, zero_method="wilcox", method="approx")
    # Fixed-seed query-level sign-flip sensitivity, not independent cell flips.
    rng = np.random.default_rng(20261015)
    count = 0
    for _ in range(100):
        signs = rng.choice([-1, 1], size=(1000, len(d)))
        count += np.count_nonzero(
            np.abs((signs * d).mean(axis=1)) >= abs(d.mean()) - 1e-14
        )
    return {
        **result,
        "status": "estimated",
        "t": float(t.statistic),
        "p": float(t.pvalue),
        "dz": float(d.mean() / d.std(ddof=1)),
        "wilcoxon_p": float(w.pvalue),
        "sign_flip_p": float((count + 1) / 100001),
        "sign_flip_draws": 100000,
        "shapiro_difference_p": float(stats.shapiro(d).pvalue),
    }


def holm(rows, field="p", output="p_holm"):
    valid = [r for r in rows if r[field] is not None]
    for r in rows:
        r[output] = None
    for r, p in zip(valid, multipletests([r[field] for r in valid], method="holm")[1]):
        r[output] = float(p)


def factorial(frame, metric, factors, label):
    wide = frame.pivot(index="query_id", columns=factors, values=metric).dropna()
    if len(wide) < 2:
        raise ValueError("Insufficient complete queries")
    long = frame[frame.query_id.isin(wide.index)].copy()
    # Independent least-squares implementation versus signed orthogonal contrasts.
    fitted = AnovaRM(long, metric, "query_id", within=factors).fit().anova_table
    results = []
    for order in range(1, len(factors) + 1):
        for effect in itertools.combinations(factors, order):
            signs = np.asarray(
                [
                    np.prod([2 * col[factors.index(f)] - 1 for f in effect])
                    for col in wide.columns
                ]
            )
            delta = wide.to_numpy() @ signs / (len(wide.columns) / 2)
            test = test_difference(delta)
            key = ":".join(effect)
            f = None if test["t"] is None else test["t"] ** 2
            if f is not None:
                np.testing.assert_allclose(
                    f, fitted.loc[key, "F Value"], rtol=1e-7, atol=1e-9
                )
                np.testing.assert_allclose(
                    test["p"], fitted.loc[key, "Pr > F"], rtol=1e-7, atol=1e-10
                )
            results.append(
                {
                    "protocol": label,
                    "metric": metric,
                    "effect": key,
                    "n": len(wide),
                    "df1": 1,
                    "df2": len(wide) - 1,
                    "F": f,
                    "p": test["p"],
                    "partial_eta_squared": (
                        None if f is None else f / (f + len(wide) - 1)
                    ),
                    "contrast_mean": test["mean"],
                    "contrast_sd": test["sd"],
                    "status": test["status"],
                    "sign_flip_p": test.get("sign_flip_p"),
                    "shapiro_difference_p": test.get("shapiro_difference_p"),
                    "crosscheck": "statsmodels.AnovaRM versus orthogonal contrast t squared",
                }
            )
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    out = parser.parse_args().output
    out.parent.mkdir(parents=True, exist_ok=True)
    records, score_map, hashes = [], {}, {}
    for gp, sp, expected in zip(GEN, SCORES, [19, 41]):
        group = read_jsonl(gp)
        ids = validate_generation(group, expected)
        score_map.update(
            validate_scores(json.loads(sp.read_text(encoding="utf-8")), ids)
        )
        records.extend(group)
        for p in [gp, sp]:
            hashes[p.relative_to(ROOT).as_posix()] = hashlib.sha256(
                p.read_bytes().replace(b"\r\n", b"\n")
            ).hexdigest()
    assert len(score_map) == len(records) == 480
    rows, missing, zero_denominators = [], [], []
    for r in records:
        q, config = r["query_id"], r["config_name"]
        h, c, s = (int(r[k]) for k in ["use_hyde", "use_cad", "use_scd"])
        values = score_map[q, config]
        for m in METRICS:
            if values[m] is None:
                missing.append(
                    {"query_id": q, "condition": f"H{h}C{c}S{s}", "metric": m}
                )
        if not any(
            ch.isascii()
            and ch.isalpha()
            or "\uac00" <= ch <= "\ud7a3"
            or "\u1100" <= ch <= "\u11ff"
            or "\u3130" <= ch <= "\u318f"
            for ch in r["generated_answer"]
        ):
            zero_denominators.append(
                {
                    "query_id": q,
                    "condition": f"H{h}C{c}S{s}",
                    "existing_rule": "existing korean_ratio returns 0; not a new imputation",
                }
            )
        rows.append(
            {
                "query_id": q,
                "paper": r["paper"],
                "H": h,
                "D": c,
                "S": s,
                "condition": f"H{h}C{c}S{s}",
                **{m: values[m] for m in METRICS},
                "korean_ratio": korean_ratio(r["generated_answer"]),
                "duration_seconds": float(r["duration_seconds"]),
            }
        )
    frame = pd.DataFrame(rows)
    frame.sort_values(["query_id", "condition"]).to_csv(
        out.with_name("FACTORIAL_OBSERVATIONS_60Q.csv"),
        index=False,
        encoding="utf-8",
        lineterminator="\n",
    )
    assert len(frame.query_id.unique()) == 60 and len(missing) == 5
    assert frame.groupby("paper").query_id.nunique().tolist() == [15] * 4
    descriptives = {
        name: {m: summary(g[m]) for m in [*METRICS, "korean_ratio", "duration_seconds"]}
        for name, g in frame.groupby("condition", sort=True)
    }
    anovas = []
    for state, label in [
        (0, "S0_English_context"),
        (1, "S1_Korean_translated_context"),
    ]:
        for metric in METRICS:
            anovas += factorial(frame[frame.S == state], metric, ["H", "D"], label)
    # Conservative revision-time family: all 24 quality factor tests together.
    holm(anovas)
    for metric in ["korean_ratio", "duration_seconds"]:
        group = factorial(frame, metric, ["H", "D", "S"], "generation_records")
        holm(group)
        anovas += group
    paired = []
    for factor, on in [("HyDE", "H1C0S0"), ("CAD", "H0C1S0")]:
        for metric in METRICS:
            wide = frame.pivot(index="query_id", columns="condition", values=metric)[
                ["H0C0S0", on]
            ].dropna()
            paired.append(
                {
                    "factor": factor,
                    "metric": metric,
                    "on": on,
                    "off": "H0C0S0",
                    **test_difference(wide[on] - wide.H0C0S0),
                }
            )
        holm(paired[-4:])
        holm(paired[-4:], "wilcoxon_p", "wilcoxon_p_holm")
        holm(paired[-4:], "sign_flip_p", "sign_flip_p_holm")
    lang = frame.pivot(index="query_id", columns="condition", values="korean_ratio")
    for label, hs in [("SCD_H0_same_context", [0]), ("SCD_all_states", [0, 1])]:
        differences = [
            (lang[f"H{h}C{c}S1"] - lang[f"H{h}C{c}S0"]) for h in hs for c in [0, 1]
        ]
        d = pd.concat(differences, axis=1).mean(axis=1)
        paired.append(
            {
                "factor": label,
                "metric": "korean_ratio",
                "raw_pairs": 60 * len(differences),
                **test_difference(d),
            }
        )
    holm(paired[-2:])
    holm(paired[-2:], "wilcoxon_p", "wilcoxon_p_holm")
    holm(paired[-2:], "sign_flip_p", "sign_flip_p_holm")
    runtime_followups = []
    for state in [0, 1]:
        wide = frame[frame.S == state].pivot(
            index="query_id", columns=["H", "D"], values="duration_seconds"
        )
        difference = ((wide[(0, 1)] - wide[(0, 0)]) + (wide[(1, 1)] - wide[(1, 0)])) / 2
        runtime_followups.append(
            {
                "metric": "duration_seconds",
                "comparison": f"CAD_simple_effect_S{state}_averaged_over_H",
                **test_difference(difference),
            }
        )
    holm(runtime_followups)
    holm(runtime_followups, "wilcoxon_p", "wilcoxon_p_holm")
    holm(runtime_followups, "sign_flip_p", "sign_flip_p_holm")
    sensitivity = []
    for p in sorted(frame.paper.unique()):
        keep = set(frame[frame.paper != p].query_id)
        for contrast in paired:
            metric = contrast["metric"]
            wide = frame[frame.query_id.isin(keep)].pivot(
                index="query_id", columns="condition", values=metric
            )
            if "on" in contrast:
                d = (wide[contrast["on"]] - wide[contrast["off"]]).dropna()
            else:
                hs = [0] if contrast["factor"] == "SCD_H0_same_context" else [0, 1]
                d = pd.concat(
                    [
                        wide[f"H{h}C{c}S1"] - wide[f"H{h}C{c}S0"]
                        for h in hs
                        for c in [0, 1]
                    ],
                    axis=1,
                ).mean(axis=1)
            sensitivity.append(
                {
                    "omitted_paper": p,
                    "factor": contrast["factor"],
                    "metric": metric,
                    **summary(d),
                }
            )
    report = {
        "analysis_date": "2026-10-15",
        "baseline_commit": "d4931ec76f591016b2601561d17fbd37ac2a833a",
        "source_sha256": hashes,
        "source_hash_method": "SHA-256 of UTF-8 file bytes with CRLF normalized to LF; source files are not rewritten",
        "raw_records_mutated": False,
        "software": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "statsmodels": __import__("statsmodels").__version__,
        },
        "analysis_contract": {
            "unit": "query; 60 queries nested in 4 fixed documents; one generation per query-condition",
            "factor_D": "CAD; statsmodels formula reserves name C",
            "quality": "separate H x CAD within S0 and S1 evaluation protocols; no causal SCD quality ANOVA",
            "missing": "complete queries per endpoint and tested condition set, no imputation",
            "multiplicity": "revision-time exploratory Holm families: 24 quality factorial tests; 7 per generation endpoint; 4 simple contrasts per HyDE/CAD; 2 SCD language contrasts",
            "preregistration": "No claim that revision-time ANOVA/multiplicity choices were preregistered",
            "zero_variance": "t/F/p/dz undefined and explicitly null, never substituted with zero or p=1",
            "sensitivity": "100000 query-level sign flips, Wilcoxon for paired contrasts, leave-one-document-out means; 4 documents limit population inference",
        },
        "counts": {"queries": 60, "records": 480, "valid_quality_cells": 1915},
        "missing_cells": missing,
        "zero_denominator_answers": zero_denominators,
        "descriptives": descriptives,
        "anova": anovas,
        "paired": paired,
        "runtime_followups": runtime_followups,
        "leave_one_document_out": sensitivity,
        "boundary_counts": {
            m: {
                "zero": int((frame[m] == 0).sum()),
                "one": int((frame[m] == 1).sum()),
                "missing": int(frame[m].isna().sum()),
            }
            for m in METRICS
        },
        "documentation": [
            "https://www.statsmodels.org/stable/generated/statsmodels.stats.anova.AnovaRM.html",
            "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html",
        ],
    }
    omitted_ids = {r["query_id"] for r in zero_denominators}
    report["zero_denominator_sensitivity"] = factorial(
        frame[~frame.query_id.isin(omitted_ids)],
        "korean_ratio",
        ["H", "D", "S"],
        "exclude_zero_denominator_query",
    )
    holm(report["zero_denominator_sensitivity"])
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"PASS: {len(rows)} records; {len(anovas)} factorial tests; {len(paired)} contrasts; {len(missing)} missing cells; independent ANOVA crosscheck"
    )


if __name__ == "__main__":
    main()
