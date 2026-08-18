"""Build Phase-A aggregate efficiency figures and concise manuscript tables."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "aggregate_efficiency"
FIGURES = ROOT / "paper" / "figures"
TABLES = ROOT / "paper" / "tables"
FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

labels = {
    "corebench_hard": "CORE",
    "gaia": "GAIA",
    "scicode": "SciCode",
    "scienceagentbench": "SAB",
    "swebench_verified_mini": "SWE-mini",
    "taubench_airline": "TAU",
}

raw = pd.read_csv(ROOT / "outputs" / "reviewer_checks" / "pairwise_bootstrap_10000.csv")
cps = pd.read_csv(OUT / "cost_per_success_floor_1pct_pairs.csv")
merged = raw[["benchmark_a", "benchmark_b", "n_shared", "cost_spearman"]].merge(
    cps[["benchmark_a", "benchmark_b", "spearman_rho"]],
    on=["benchmark_a", "benchmark_b"],
    how="inner",
    suffixes=("_raw_cost", "_cps"),
)
merged = merged[merged["n_shared"] >= 12].copy()
merged["pair"] = merged["benchmark_a"].map(labels) + "--" + merged["benchmark_b"].map(labels)
merged = merged.sort_values("cost_spearman")

fig, ax = plt.subplots(figsize=(6.7, 3.2), constrained_layout=True)
y = np.arange(len(merged))
ax.scatter(merged["cost_spearman"], y, s=55, color="#0072B2", marker="o", label="Raw dollar cost")
ax.scatter(merged["spearman_rho"], y, s=55, color="#D55E00", marker="s", label="Cost per expected success (1% floor)")
for _, row in merged.iterrows():
    yy = merged.index.get_loc(row.name)
    ax.plot([row["cost_spearman"], row["spearman_rho"]], [yy, yy], color="#9ca3af", lw=1.1, zorder=0)
    ax.text(row["cost_spearman"] + 0.015, yy + 0.12, f"{row['cost_spearman']:.2f}", color="#0072B2", fontsize=6.5)
    ax.text(row["spearman_rho"] + 0.015, yy - 0.22, f"{row['spearman_rho']:.2f}", color="#D55E00", fontsize=6.5)
ax.axvline(0, color="black", lw=0.8)
ax.set_yticks(y, merged["pair"])
ax.set_xlabel("Cross-benchmark Spearman correlation")
ax.set_title("Raw cost ranks are more portable across most pairs")
ax.set_xlim(-0.05, 1.0)
ax.legend(frameon=False, loc="upper left", fontsize=8)
fig.savefig(FIGURES / "raw_cost_vs_cost_per_success.pdf", bbox_inches="tight")
fig.savefig(FIGURES / "raw_cost_vs_cost_per_success.png", dpi=300, bbox_inches="tight")
plt.close(fig)

lobo = pd.read_csv(OUT / "lobo_cost_rank_summary.csv")
lobo["label"] = lobo["held_out_benchmark"].map(labels)
lobo = lobo.sort_values("spearman_rho")
fig, ax = plt.subplots(figsize=(6.7, 3.1), constrained_layout=True)
colors = ["#D55E00" if p >= 0.05 else "#0072B2" for p in lobo["permutation_p_two_sided"]]
ax.bar(lobo["label"], lobo["spearman_rho"], color=colors)
ax.axhline(0, color="black", lw=0.8)
for i, row in enumerate(lobo.itertuples()):
    ax.text(i, row.spearman_rho + (0.04 if row.spearman_rho >= 0 else -0.07), f"{row.spearman_rho:.2f}\nN={row.n_predicted_labels}", ha="center", va="bottom" if row.spearman_rho >= 0 else "top", fontsize=7)
ax.set_ylim(-0.85, 1.0)
ax.set_ylabel("LOBO predicted vs observed cost-rank $\\rho$")
ax.set_title("Stable cost propensity predicts some held-out workloads, not all")
fig.savefig(FIGURES / "lobo_cost_portability.pdf", bbox_inches="tight")
fig.savefig(FIGURES / "lobo_cost_portability.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# Compact main-paper table: raw cost vs aggregate success-adjusted cost at primary 1% floor.
main = merged.copy()
main["Pair"] = main["pair"]
main["N"] = main["n_shared"].astype(int)
main["Raw cost $\\rho$"] = main["cost_spearman"].map(lambda v: f"{v:.2f}")
main["CPS $\\rho$"] = main["spearman_rho"].map(lambda v: f"{v:.2f}")
TABLES.joinpath("cost_vs_cps_transfer.tex").write_text(
    main[["Pair", "N", "Raw cost $\\rho$", "CPS $\\rho$"]].to_latex(index=False, escape=False, column_format="lrrr")
)

lobo_table = lobo.copy()
lobo_table["Held-out"] = lobo_table["label"]
lobo_table["N"] = lobo_table["n_predicted_labels"].astype(int)
lobo_table["$\\rho$"] = lobo_table["spearman_rho"].map(lambda v: f"{v:.2f}")
lobo_table["Perm. $p$"] = lobo_table["permutation_p_two_sided"].map(lambda v: f"{v:.4f}")
TABLES.joinpath("lobo_cost_portability.tex").write_text(
    lobo_table[["Held-out", "N", "$\\rho$", "Perm. $p$"]].to_latex(index=False, escape=False, column_format="lrrr")
)
