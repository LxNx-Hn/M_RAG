"""Thesis statistics restricted to paired t-tests and repeated-measures ANOVA.

Input is the frozen query-level observation table (60 queries x 8 conditions).
No inference/API calls and no multiplicity adjustment; every p value is the
original two-sided value of its own test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import statsmodels
from scipy import stats
from statsmodels.stats.anova import AnovaRM

ROOT = Path(__file__).resolve().parents[2]
OBS = ROOT / "FINALDOCS/DATA/FACTORIAL_OBSERVATIONS_60Q.csv"
OUT = ROOT / "FINALDOCS/DATA/TTEST_ANOVA_60Q.json"
QUALITY = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
COLD_START = ["track1_0009", "ext_rag_001"]


def load(path: Path) -> pd.DataFrame:
    # statsmodels reserves the factor name "C", so CAD stays "D" internally.
    df = pd.read_csv(path)
    if len(df) != 480 or df.query_id.nunique() != 60:
        raise ValueError("Expected 60 queries x 8 conditions")
    return df


def paired(df, metric, on, off):
    """Paired t-test; list arguments are averaged within each query first."""
    w = df.pivot(index="query_id", columns="condition", values=metric)
    on, off = ([on] if isinstance(on, str) else on), (
        [off] if isinstance(off, str) else off
    )
    a = w[on].mean(axis=1, skipna=False)
    b = w[off].mean(axis=1, skipna=False)
    ok = a.notna() & b.notna()
    a, b = a[ok], b[ok]
    d = a - b
    n = len(d)
    sd = float(d.std(ddof=1))
    t, p = stats.ttest_rel(a, b)
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    return {
        "metric": metric,
        "on": on,
        "off": off,
        "n": n,
        "raw_pairs": n * len(on),
        "on_mean": float(a.mean()),
        "on_sd": float(a.std(ddof=1)),
        "off_mean": float(b.mean()),
        "off_sd": float(b.std(ddof=1)),
        "mean_diff": float(d.mean()),
        "sd_diff": sd,
        "df": n - 1,
        "t": float(t),
        "p": float(p),
        "dz": float(d.mean() / sd),
        "ci95": [float(d.mean() - half), float(d.mean() + half)],
        "increased": int((d > 0).sum()),
        "decreased": int((d < 0).sum()),
        "ties": int((d == 0).sum()),
    }


def rm_anova(df, metric, factors):
    d = df.dropna(subset=[metric])
    cells = d.groupby("query_id").condition.nunique()
    keep = cells[cells == d.condition.nunique()].index
    d = d[d.query_id.isin(keep)]
    table = AnovaRM(d, metric, "query_id", within=factors).fit().anova_table
    rows = []
    for effect, r in table.iterrows():
        f, df1, df2 = float(r["F Value"]), int(r["Num DF"]), int(r["Den DF"])
        rows.append(
            {
                "metric": metric,
                "effect": effect.replace("D", "C").replace(":", "×"),
                "n": len(keep),
                "df1": df1,
                "df2": df2,
                "F": f,
                "p": float(r["Pr > F"]),
                "partial_eta_squared": f * df1 / (f * df1 + df2),
            }
        )
    return rows


def cond(h, c, s):
    return f"H{h}C{c}S{s}"


def analyze(df: pd.DataFrame) -> dict:
    descriptives = {
        c: {
            m: {
                "n": int(g[m].notna().sum()),
                "mean": float(g[m].mean()),
                "sd": float(g[m].std(ddof=1)),
                "median": float(g[m].median()),
            }
            for m in QUALITY + ["korean_ratio", "duration_seconds"]
        }
        for c, g in df.groupby("condition")
    }
    primary = {
        "RQ1_HyDE_answer_relevancy": paired(
            df, "answer_relevancy", "H1C0S0", "H0C0S0"
        ),
        "RQ2_CAD_faithfulness": paired(df, "faithfulness", "H0C1S0", "H0C0S0"),
        "RQ3_SCD_korean_ratio_H0": paired(
            df, "korean_ratio", ["H0C0S1", "H0C1S1"], ["H0C0S0", "H0C1S0"]
        ),
    }
    secondary = {
        "RQ3_SCD_korean_ratio_all_states": paired(
            df,
            "korean_ratio",
            [cond(h, c, 1) for h in (0, 1) for c in (0, 1)],
            [cond(h, c, 0) for h in (0, 1) for c in (0, 1)],
        )
    }
    for m in QUALITY:
        if m != "answer_relevancy":
            secondary[f"HyDE_{m}"] = paired(df, m, "H1C0S0", "H0C0S0")
        if m != "faithfulness":
            secondary[f"CAD_{m}"] = paired(df, m, "H0C1S0", "H0C0S0")
    anova = {
        "korean_ratio": rm_anova(df, "korean_ratio", ["H", "D", "S"]),
        "duration_seconds": rm_anova(df, "duration_seconds", ["H", "D", "S"]),
    }
    for s in (0, 1):
        anova[f"quality_S{s}"] = [
            row for m in QUALITY for row in rm_anova(df[df.S == s], m, ["H", "D"])
        ]
    # Simple effects that unpack interactions with original p < 0.05.
    followups = {
        "korean_ratio_HyDE_at_C0": paired(
            df,
            "korean_ratio",
            [cond(1, 0, s) for s in (0, 1)],
            [cond(0, 0, s) for s in (0, 1)],
        ),
        "korean_ratio_HyDE_at_C1": paired(
            df,
            "korean_ratio",
            [cond(1, 1, s) for s in (0, 1)],
            [cond(0, 1, s) for s in (0, 1)],
        ),
        "duration_CAD_at_S0": paired(
            df,
            "duration_seconds",
            [cond(h, 1, 0) for h in (0, 1)],
            [cond(h, 0, 0) for h in (0, 1)],
        ),
        "duration_CAD_at_S1": paired(
            df,
            "duration_seconds",
            [cond(h, 1, 1) for h in (0, 1)],
            [cond(h, 0, 1) for h in (0, 1)],
        ),
    }
    warm = df[~df.query_id.isin(COLD_START)]
    cold_start = {
        "excluded_queries": COLD_START,
        "H0C0S0_durations": df[
            (df.condition == "H0C0S0") & df.query_id.isin(COLD_START)
        ]
        .set_index("query_id")
        .duration_seconds.to_dict(),
        "anova_without": rm_anova(warm, "duration_seconds", ["H", "D", "S"]),
        "condition_means_without": warm.groupby("condition")
        .duration_seconds.mean()
        .to_dict(),
    }
    return {
        "descriptives": descriptives,
        "primary_paired_t": primary,
        "secondary_paired_t": secondary,
        "rm_anova": anova,
        "interaction_followups": followups,
        "runtime_cold_start_check": cold_start,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", type=Path, default=OBS)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    df = load(args.observations)
    result = {
        "observations": str(args.observations.relative_to(ROOT)).replace("\\", "/"),
        "observations_sha256": hashlib.sha256(
            args.observations.read_bytes()
        ).hexdigest(),
        "software": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "statsmodels": statsmodels.__version__,
        },
        "contract": {
            "methods": "paired t-test (scipy.stats.ttest_rel) and repeated-measures "
            "ANOVA (statsmodels AnovaRM) only",
            "alpha": "two-sided 0.05",
            "multiplicity": "no adjustment; original p of each test is reported",
            "status": "exploratory analysis organized after the results were "
            "collected; primary metrics were not preregistered",
            "unit": "query (n=60); multiple pairs within a query are averaged first",
            "missing": "queries with all conditions of the test present, no imputation",
            "quality_blocks": "H x C within S0 (English context) and S1 (Korean-"
            "translated context) separately",
        },
        **analyze(df),
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for k, v in result["primary_paired_t"].items():
        print(f"{k}: n={v['n']} diff={v['mean_diff']:+.4f} t={v['t']:.3f} p={v['p']:.4g}")


if __name__ == "__main__":
    main()
