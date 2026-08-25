"""Failure-burden analysis on the matched Open-SWE boundary sample.

Question: at fixed task and model, do failed agent trajectories carry more
observable burden than resolved ones? Three complementary views:

1. Per-scaffold failed/resolved median ratios with bootstrap intervals
   (cross-task comparison; task difficulty is a confound).
2. Discordant-outcome pairs: tasks where exactly one scaffold resolved.
   Within such a pair the two trajectories faced the identical task, so we
   ask how often the failed side is the heavier one (sign test).
3. Burden asymmetry in concordant outcomes as a reference point.

Observational only. Burden proxies are not tokens or dollars, and no causal
claim is made: failing agents may burn more because they are stuck, and hard
tasks may both fail agents and inflate burden.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PAIRS = ROOT / "outputs" / "external_trace_study" / "exact_matched_scaffold_pairs.csv"
OUT = ROOT / "outputs" / "failure_burden"

METRICS = [
    "trajectory_turns",
    "assistant_turns",
    "tool_calls",
    "tool_result_turns",
    "trajectory_characters",
    "reasoning_characters",
]


def ratio_interval(success: np.ndarray, failed: np.ndarray, n_boot: int = 10_000,
                   seed: int = 20260826) -> tuple[float, float, float]:
    """Median failed/success burden ratio with percentile bootstrap interval."""
    generator = np.random.default_rng(seed)
    stats = []
    for _ in range(n_boot):
        s = success[generator.integers(0, len(success), len(success))]
        f = failed[generator.integers(0, len(failed), len(failed))]
        if np.median(s) > 0:
            stats.append(np.median(f) / np.median(s))
    stats = np.sort(np.asarray(stats))
    return float(stats[0]), float(np.median(stats)), float(stats[-1])


def per_scaffold_ratios(rows: pd.DataFrame) -> pd.DataFrame:
    out = []
    for scaffold, group in rows.groupby("scaffold"):
        for metric in METRICS:
            ok = group.loc[group.resolved == 1, metric].to_numpy(float)
            bad = group.loc[group.resolved == 0, metric].to_numpy(float)
            lo, med, hi = ratio_interval(ok, bad)
            out.append({
                "scaffold": scaffold,
                "metric": metric,
                "n_resolved": len(ok),
                "n_failed": len(bad),
                "median_resolved": float(np.median(ok)),
                "median_failed": float(np.median(bad)),
                "failed_over_resolved_ratio": med,
                "ci_low": lo,
                "ci_high": hi,
            })
    return pd.DataFrame(out)


def discordant_sign_tests(pairs: pd.DataFrame) -> pd.DataFrame:
    """On discordant pairs, is the FAILED scaffold's trajectory heavier?"""
    disc = pairs[
        (pairs.resolved_openhands.isin([0, 1]))
        & (pairs.resolved_sweagent.isin([0, 1]))
        & (pairs.resolved_openhands != pairs.resolved_sweagent)
    ].copy()
    out = []
    for metric in METRICS:
        swe_failed = disc.resolved_sweagent == 0          # OpenHands resolved
        oh_failed = disc.resolved_openhands == 0          # SWE-agent resolved
        heavier_is_failed = (
            (disc.loc[swe_failed, f"{metric}_sweagent"].to_numpy(float)
             > disc.loc[swe_failed, f"{metric}_openhands"].to_numpy(float)).sum()
            + (disc.loc[oh_failed, f"{metric}_openhands"].to_numpy(float)
               > disc.loc[oh_failed, f"{metric}_sweagent"].to_numpy(float)).sum()
        )
        total = int(swe_failed.sum() + oh_failed.sum())
        test = binomtest(int(heavier_is_failed), total, p=0.5)
        out.append({
            "metric": metric,
            "discordant_pairs": total,
            "failed_heavier": int(heavier_is_failed),
            "fraction_failed_heavier": heavier_is_failed / total if total else float("nan"),
            "binom_p_two_sided": test.pvalue,
        })
    out = pd.DataFrame(out)

    # Failure-burden ratio inside discordant pairs: pooled failed vs pooled
    # resolved trajectory values from the SAME task set.
    rows = []
    for metric in METRICS:
        failed_vals = np.concatenate([
            disc.loc[disc.resolved_sweagent == 0, f"{metric}_sweagent"].to_numpy(float),
            disc.loc[disc.resolved_openhands == 0, f"{metric}_openhands"].to_numpy(float),
        ])
        ok_vals = np.concatenate([
            disc.loc[disc.resolved_sweagent == 1, f"{metric}_sweagent"].to_numpy(float),
            disc.loc[disc.resolved_openhands == 1, f"{metric}_openhands"].to_numpy(float),
        ])
        lo, med, hi = ratio_interval(ok_vals, failed_vals)
        rows.append({
            "metric": metric,
            "n_failed_traj": len(failed_vals),
            "n_resolved_traj": len(ok_vals),
            "median_resolved": float(np.median(ok_vals)),
            "median_failed": float(np.median(failed_vals)),
            "failed_over_resolved_ratio": med,
            "ci_low": lo,
            "ci_high": hi,
        })
    ratios = pd.DataFrame(rows)
    return out, ratios


def scaffold_normalized_discordant(pairs: pd.DataFrame, long_df: pd.DataFrame) -> pd.DataFrame:
    """Scaffold-offset-adjusted discordant test.

    Each trajectory burden is divided by its own scaffold's median over all
    known-outcome matched tasks before comparing sides. This removes the
    baseline OpenHands/SWE-agent offset so the sign test measures failure
    association rather than scaffold identity.
    """
    medians = long_df.groupby("scaffold")[METRICS].median().to_dict("index")
    norm = {}
    for metric in METRICS:
        for scaffold in ["sweagent", "openhands"]:
            norm[(metric, scaffold)] = medians[scaffold][metric]

    disc = pairs[
        (pairs.resolved_openhands.isin([0, 1]))
        & (pairs.resolved_sweagent.isin([0, 1]))
        & (pairs.resolved_openhands != pairs.resolved_sweagent)
    ].copy()

    rows = []
    from scipy.stats import wilcoxon
    for metric in METRICS:
        swe_v = disc[f"{metric}_sweagent"].to_numpy(float) / norm[(metric, "sweagent")]
        oh_v = disc[f"{metric}_openhands"].to_numpy(float) / norm[(metric, "openhands")]
        swe_failed = disc.resolved_sweagent.to_numpy(int) == 0
        # +>0 means the failed side carries more normalized burden.
        diff = np.where(swe_failed, swe_v - oh_v, oh_v - swe_v)
        heavier = int((diff > 0).sum())
        total = int(len(diff))
        test = binomtest(heavier, total, p=0.5)
        nonzero = diff[diff != 0]
        w_p = float(wilcoxon(nonzero, alternative="two-sided").pvalue) if len(nonzero) >= 10 else float("nan")
        failed_norm = np.where(swe_failed, swe_v, oh_v)
        ok_norm = np.where(swe_failed, oh_v, swe_v)
        lo, med_r, hi = ratio_interval(ok_norm, failed_norm)
        rows.append({
            "metric": metric,
            "discordant_pairs": total,
            "failed_side_norm_burden_greater": heavier,
            "fraction": heavier / total,
            "binom_p_two_sided": test.pvalue,
            "wilcoxon_p_nonzero_diffs": w_p,
            "median_failed_over_ok_norm_ratio": med_r,
            "ci_low": lo,
            "ci_high": hi,
        })
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = pd.read_csv(PAIRS)

    known = pairs[
        pairs.resolved_sweagent.isin([0, 1]) & pairs.resolved_openhands.isin([0, 1])
    ]
    long_rows = []
    for _, row in known.iterrows():
        for scaffold in ["sweagent", "openhands"]:
            long_rows.append({
                "instance_id": row["instance_id"],
                "scaffold": scaffold,
                "resolved": int(row[f"resolved_{scaffold}"]),
                **{m: row[f"{m}_{scaffold}"] for m in METRICS},
            })
    long_df = pd.DataFrame(long_rows)

    per_scaffold = per_scaffold_ratios(long_df)
    sign_tests, discordant_ratios = discordant_sign_tests(known)
    normalized = scaffold_normalized_discordant(known, long_df)

    per_scaffold.to_csv(OUT / "per_scaffold_failure_burden.csv", index=False)
    sign_tests.to_csv(OUT / "discordant_sign_tests.csv", index=False)
    discordant_ratios.to_csv(OUT / "discordant_failure_burden.csv", index=False)
    normalized.to_csv(OUT / "discordant_normalized_sign_tests.csv", index=False)

    meta = {
        "source": "nvidia/Open-SWE-Traces four-shard MiniMax-M2.5 boundary sample",
        "n_matched_pairs": int(len(pairs)),
        "n_pairs_with_known_outcomes": int(len(known)),
        "design": [
            "per-scaffold failed/resolved ratios are cross-task (task difficulty confounds)",
            "discordant-pair sign tests compare scaffolds on the IDENTICAL task",
            "burden proxies are character/turn counts, not tokens or dollars",
        ],
        "prohibited_interpretation": "dollar failure-cost ratio; causal effect of failure on spend",
    }
    (OUT / "README.json").write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()
