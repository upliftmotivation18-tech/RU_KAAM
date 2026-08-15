"""Create compact LaTeX tables for the anonymous manuscript."""

from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parents[1]
tables = root / "paper" / "tables"
appendix = root / "paper" / "appendix"
tables.mkdir(parents=True, exist_ok=True)
appendix.mkdir(parents=True, exist_ok=True)

pairs = pd.read_csv(root / "outputs" / "tables" / "generalist_pairwise_transfer.csv")
high_overlap = pairs[pairs["n_shared"] >= 12].copy()
high_overlap["Pair"] = high_overlap["benchmark_a_label"] + "--" + high_overlap["benchmark_b_label"]
high_overlap["Accuracy $\\rho$"] = high_overlap.apply(
    lambda row: (
        f"{row['accuracy_spearman']:.2f} "
        f"[{row['accuracy_spearman_ci_low']:.2f}, {row['accuracy_spearman_ci_high']:.2f}]"
    ),
    axis=1,
)
high_overlap["Cost $\\rho$"] = high_overlap.apply(
    lambda row: (
        f"{row['cost_spearman']:.2f} "
        f"[{row['cost_spearman_ci_low']:.2f}, {row['cost_spearman_ci_high']:.2f}]"
    ),
    axis=1,
)
high_overlap["N"] = high_overlap["n_shared"].astype(int)
high_overlap["ND Jaccard"] = high_overlap["weak_jaccard_common_cohort"].map(lambda value: f"{value:.2f}")
(tables / "high_overlap_pairs.tex").write_text(
    high_overlap[["Pair", "N", "Accuracy $\\rho$", "Cost $\\rho$", "ND Jaccard"]].to_latex(
        index=False, escape=False, column_format="lrrrr"
    )
)

rates = pd.read_csv(root / "outputs" / "tables" / "generalist_frontier_rates.csv")
rates = rates[rates["benchmarks_tested"] >= 5].copy()
rates["Model label"] = rates["model_configuration"].str.replace(
    r" \([A-Za-z]+ \d{4}\)", "", regex=True
)
rates["Tested"] = rates["benchmarks_tested"].astype(int)
rates["ND appearances"] = rates["weak_frontier_appearances"].astype(int)
rates["ND rate"] = rates["weak_frontier_rate"].map(lambda value: f"{value:.2f}")
(tables / "frontier_rates.tex").write_text(
    rates[["Model label", "Tested", "ND appearances", "ND rate"]].to_latex(
        index=False, escape=False, column_format="lrrr"
    )
)

audit = pd.read_csv(root / "outputs" / "tables" / "pareto_label_reproducibility.csv")
audit = audit.rename(
    columns={
        "benchmark": "Benchmark",
        "rows": "Rows",
        "supplied_frontier": "Supplied",
        "weak_frontier": "Nondominated",
        "convex_hull_frontier": "Hull",
        "supplied_weak_agreement": "Supplied--ND agreement",
        "supplied_hull_agreement": "Supplied--hull agreement",
    }
)
audit["Benchmark"] = audit["Benchmark"].str.replace("_", r"\_", regex=False)
(appendix / "pareto_label_audit.tex").write_text(
    audit.to_latex(index=False, float_format="%.3f", column_format="lrrrrrr")
)
