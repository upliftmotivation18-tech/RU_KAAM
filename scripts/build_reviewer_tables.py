"""Create supplemental tables for reviewer-oriented robustness checks."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "reviewer_checks"
DESTINATION = ROOT / "paper" / "appendix"
DESTINATION.mkdir(parents=True, exist_ok=True)

pairs = pd.read_csv(SOURCE / "pairwise_bootstrap_10000.csv")
pairs["Pair"] = (
    pairs["benchmark_a_label"].str.replace("_", r"\_", regex=False)
    + "--"
    + pairs["benchmark_b_label"].str.replace("_", r"\_", regex=False)
)
pairs["Acc. $\\rho$ [interval]"] = pairs.apply(
    lambda row: f"{row['accuracy_spearman']:.2f} [{row['accuracy_spearman_ci_low']:.2f}, {row['accuracy_spearman_ci_high']:.2f}]",
    axis=1,
)
pairs["Cost $\\rho$ [interval]"] = pairs.apply(
    lambda row: f"{row['cost_spearman']:.2f} [{row['cost_spearman_ci_low']:.2f}, {row['cost_spearman_ci_high']:.2f}]",
    axis=1,
)
pairs["N"] = pairs["n_shared"].astype(int)
(DESTINATION / "all_pairwise_intervals.tex").write_text(
    pairs[["Pair", "N", "Acc. $\\rho$ [interval]", "Cost $\\rho$ [interval]"]].to_latex(
        index=False, escape=False, column_format="lrrr"
    )
)

holm = pd.read_csv(SOURCE / "holm_bonferroni.csv")
holm["Pair"] = (
    holm["benchmark_a"].str.replace("_", r"\_", regex=False)
    + "--"
    + holm["benchmark_b"].str.replace("_", r"\_", regex=False)
)
holm["Metric"] = holm["metric"].map({"accuracy_rank": "Accuracy", "cost_rank": "Cost"})
holm["Uncorrected p"] = holm["uncorrected_p"].map(lambda value: f"{value:.4f}")
holm["Holm p"] = holm["holm_adjusted_p"].map(lambda value: f"{value:.4f}")
holm["Reject"] = holm["holm_reject_alpha_0_05"].map({True: "Yes", False: "No"})
(DESTINATION / "holm_results.tex").write_text(
    holm[["Pair", "Metric", "Uncorrected p", "Holm p", "Reject"]].to_latex(
        index=False, escape=False, column_format="llrrc"
    )
)

frontier = pd.read_csv(SOURCE / "frontier_definition_sensitivity.csv")
frontier = frontier.rename(
    columns={
        "frontier_definition": "Definition",
        "max_appearances_broad_labels": "Max appearances (broad labels)",
        "universal_winner_broad_labels": "Universal broad winner",
    }
)
frontier["Definition"] = frontier["Definition"].map(
    {
        "nondominated": "Nondominated",
        "convex_hull": "HAL-inspired hull",
        "nondominated_5pct_tolerance": r"Nondominated, 5\% tolerance",
    }
)
frontier["Universal broad winner"] = frontier["Universal broad winner"].map({True: "Yes", False: "No"})
(DESTINATION / "frontier_sensitivity.tex").write_text(
    frontier[["Definition", "Max appearances (broad labels)", "Universal broad winner"]].to_latex(
        index=False, escape=False, column_format="lrc"
    )
)

quartiles = pd.read_csv(SOURCE / "quartile_rank_changes.csv")
quartiles = quartiles[quartiles["metric"].eq("cost_rank")].copy()
quartiles["Pair"] = (
    quartiles["benchmark_a"].str.replace("_", r"\_", regex=False)
    + "--"
    + quartiles["benchmark_b"].str.replace("_", r"\_", regex=False)
)
quartiles["N"] = quartiles["n_shared"].astype(int)
quartiles["Cheap-to-expensive"] = quartiles.apply(
    lambda row: f"{int(row['top_a_to_bottom_b_count'])}/{int(row['n_shared'])} ({row['top_a_to_bottom_b_fraction']:.0%})".replace("%", r"\%"),
    axis=1,
)
quartiles["Any extreme flip"] = quartiles.apply(
    lambda row: f"{int(row['any_extreme_quartile_flip_count'])}/{int(row['n_shared'])} ({row['any_extreme_quartile_flip_fraction']:.0%})".replace("%", r"\%"),
    axis=1,
)
(DESTINATION / "cost_quartile_flips.tex").write_text(
    quartiles[["Pair", "N", "Cheap-to-expensive", "Any extreme flip"]].to_latex(
        index=False, escape=False, column_format="lrrr"
    )
)
