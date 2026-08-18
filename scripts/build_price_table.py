"""Create a compact LaTeX table for observed cost-propensity adjustment."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "outputs" / "price_confound" / "residual_cost_rank_pairs.csv"
destination = ROOT / "paper" / "tables" / "cost_propensity_adjustment.tex"
destination.parent.mkdir(parents=True, exist_ok=True)

table = pd.read_csv(source)
raw = pd.read_csv(ROOT / "outputs" / "reviewer_checks" / "pairwise_bootstrap_10000.csv")
merged = table.merge(
    raw[["benchmark_a", "benchmark_b", "cost_spearman"]],
    on=["benchmark_a", "benchmark_b"],
    how="left",
)
selected = merged[merged["n_shared"] >= 12].copy()
labels = {
    "corebench_hard": "CORE",
    "gaia": "GAIA",
    "scicode": "SciCode",
    "scienceagentbench": "SAB",
    "swebench_verified_mini": "SWE-mini",
    "taubench_airline": "TAU",
}
selected["Pair"] = selected["benchmark_a"].map(labels) + "--" + selected["benchmark_b"].map(labels)
selected["N"] = selected["n_shared"].astype(int)
selected["Raw $\\rho$"] = selected["cost_spearman"].map(lambda value: f"{value:.2f}")
selected["Residual $\\rho$"] = selected["residual_spearman"].map(lambda value: f"{value:.2f}")
selected["Perm. $p$"] = selected["permutation_p_two_sided"].map(lambda value: f"{value:.3f}")
destination.write_text(
    selected[["Pair", "N", "Raw $\\rho$", "Residual $\\rho$", "Perm. $p$"]].to_latex(
        index=False, escape=False, column_format="lrrrr"
    )
)
