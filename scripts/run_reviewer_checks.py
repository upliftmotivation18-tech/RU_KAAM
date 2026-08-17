"""Run reviewer-oriented robustness analyses for the fixed-scaffold HAL study."""

from __future__ import annotations

import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from scripts.run_analysis import (
    BENCHMARK_LABELS,
    GENERALIST,
    PRIMARY_BENCHMARKS,
    add_frontiers,
    fixed_scaffold_pairwise_analysis,
    load_data,
    scaffold_sensitivity,
    verify_frozen_input,
)
from src.additional_analysis import (
    holm_bonferroni,
    null_label_shuffle,
    tolerant_nondominated_frontier,
)
from src.analysis import convex_hull_frontier, weak_pareto_frontier

INPUT = ROOT / "data" / "all_leaderboards_costs_HAL.csv"
OUT = ROOT / "outputs" / "reviewer_checks"
SEED = 20260816


def pair_frames(data: pd.DataFrame, benchmark_a: str, benchmark_b: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    subset = data[data["scaffold"].eq(GENERALIST)]
    first = subset[subset["benchmark"].eq(benchmark_a)].set_index("model_configuration")
    second = subset[subset["benchmark"].eq(benchmark_b)].set_index("model_configuration")
    shared = sorted(set(first.index) & set(second.index))
    return first.loc[shared].copy(), second.loc[shared].copy()


def quartile_rank_changes(data: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, pair in pairs.iterrows():
        first, second = pair_frames(data, pair["benchmark_a"], pair["benchmark_b"])
        n = len(first)
        for metric, ascending in [("accuracy", False), ("total_cost", True)]:
            rank_a = first[metric].rank(method="average", ascending=ascending)
            rank_b = second[metric].rank(method="average", ascending=ascending)
            top_cut = np.ceil(n * 0.25)
            bottom_cut = np.floor(n * 0.75) + 1
            top_a = rank_a <= top_cut
            bottom_a = rank_a >= bottom_cut
            top_b = rank_b <= top_cut
            bottom_b = rank_b >= bottom_cut
            top_to_bottom = top_a & bottom_b
            bottom_to_top = bottom_a & top_b
            changed_quartile = np.ceil(rank_a / (n / 4.0)) != np.ceil(rank_b / (n / 4.0))
            rows.append(
                {
                    "benchmark_a": pair["benchmark_a"],
                    "benchmark_b": pair["benchmark_b"],
                    "metric": "accuracy_rank" if metric == "accuracy" else "cost_rank",
                    "n_shared": n,
                    "top_a_to_bottom_b_count": int(top_to_bottom.sum()),
                    "top_a_to_bottom_b_fraction": float(top_to_bottom.mean()),
                    "bottom_a_to_top_b_count": int(bottom_to_top.sum()),
                    "bottom_a_to_top_b_fraction": float(bottom_to_top.mean()),
                    "any_extreme_quartile_flip_count": int((top_to_bottom | bottom_to_top).sum()),
                    "any_extreme_quartile_flip_fraction": float((top_to_bottom | bottom_to_top).mean()),
                    "different_quartile_count": int(changed_quartile.sum()),
                    "different_quartile_fraction": float(changed_quartile.mean()),
                }
            )
    return pd.DataFrame(rows)


def tolerant_frontier_rates(data: pd.DataFrame, tolerance: float = 0.05) -> pd.DataFrame:
    subset = data[
        data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)
    ].copy()
    subset["tolerant"] = (
        subset.groupby("benchmark", group_keys=False)
        .apply(
            lambda frame: tolerant_nondominated_frontier(
                frame,
                cost_column="total_cost",
                accuracy_column="accuracy",
                relative_tolerance=tolerance,
            ),
            include_groups=False,
        )
        .astype(bool)
    )
    return (
        subset.groupby("model_configuration")
        .agg(tested=("benchmark", "size"), appearances=("tolerant", "sum"))
        .assign(rate=lambda frame: frame["appearances"] / frame["tested"])
        .reset_index()
        .sort_values(["tested", "appearances"], ascending=[False, False])
    )


def full_frontier_sensitivity(data: pd.DataFrame) -> pd.DataFrame:
    subset = data[
        data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)
    ].copy()
    methods = {
        "nondominated": weak_pareto_frontier,
        "convex_hull": convex_hull_frontier,
    }
    rows: list[dict[str, object]] = []
    for name, function in methods.items():
        membership = (
            subset.groupby("benchmark", group_keys=False)
            .apply(
                lambda frame: function(frame, cost_column="total_cost", accuracy_column="accuracy"),
                include_groups=False,
            )
            .astype(bool)
        )
        working = subset.assign(member=membership)
        rates = working.groupby("model_configuration").agg(
            tested=("benchmark", "size"), appearances=("member", "sum")
        )
        rows.append(
            {
                "frontier_definition": name,
                "max_appearances_all_labels": int(rates["appearances"].max()),
                "max_appearances_broad_labels": int(rates.loc[rates["tested"] >= 5, "appearances"].max()),
                "universal_winner_all_labels": bool((rates["appearances"] == rates["tested"]).any()),
                "universal_winner_broad_labels": bool(
                    ((rates["tested"] >= 5) & (rates["appearances"] == rates["tested"])).any()
                ),
            }
        )
    tolerant = tolerant_frontier_rates(data)
    rows.append(
        {
            "frontier_definition": "nondominated_5pct_tolerance",
 "max_appearances_all_labels": int(tolerant["appearances"].max()),
            "max_appearances_broad_labels": int(tolerant.loc[tolerant["tested"] >= 5, "appearances"].max()),
            "universal_winner_all_labels": bool((tolerant["appearances"] == tolerant["tested"]).any()),
            "universal_winner_broad_labels": bool(
                ((tolerant["tested"] >= 5) & (tolerant["appearances"] == tolerant["tested"])).any()
            ),
        }
    )
    return pd.DataFrame(rows), tolerant


def pairwise_nulls(data: pd.DataFrame, pairs: pd.DataFrame, simulations: int = 10_000) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for index, pair in pairs.reset_index(drop=True).iterrows():
        first, second = pair_frames(data, pair["benchmark_a"], pair["benchmark_b"])
        for metric, label in [("accuracy", "accuracy_rank"), ("total_cost", "cost_rank")]:
            result = null_label_shuffle(
                first[metric],
                second[metric],
                n_simulations=simulations,
                seed=SEED + index * 13 + (0 if metric == "accuracy" else 1),
            )
            rows.append(
                {
                    "benchmark_a": pair["benchmark_a"],
                    "benchmark_b": pair["benchmark_b"],
                    "metric": label,
                    **result,
                }
            )
    return pd.DataFrame(rows)


def multiple_comparisons(data: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for metric, column in [("accuracy_rank", "accuracy"), ("cost_rank", "total_cost")]:
        p_values: list[float] = []
        for _, pair in pairs.iterrows():
            first, second = pair_frames(data, pair["benchmark_a"], pair["benchmark_b"])
            p_values.append(float(spearmanr(first[column], second[column]).pvalue))
        correction = holm_bonferroni(p_values)
        output = pairs[["benchmark_a", "benchmark_b", "n_shared"]].copy()
        output["uncorrected_p"] = p_values
        output["metric"] = metric
        output["holm_adjusted_p"] = correction["adjusted_p"]
        output["holm_reject_alpha_0_05"] = correction["reject"]
        rows.append(output)
    return pd.concat(rows, ignore_index=True)


def missingness_summary(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    subset = data[data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)]
    coverage = pd.crosstab(subset["model_configuration"], subset["benchmark"]).reindex(columns=PRIMARY_BENCHMARKS, fill_value=0)
    coverage["benchmarks_tested"] = (coverage > 0).sum(axis=1)
    broad = coverage[coverage["benchmarks_tested"] >= 5].copy()
    model_summary = (
        subset.groupby("model_configuration")
        .agg(
            benchmarks_tested=("benchmark", "nunique"),
            mean_accuracy=("accuracy", "mean"),
            mean_cost=("total_cost", "mean"),
            min_accuracy=("accuracy", "min"),
            max_cost=("total_cost", "max"),
        )
        .join(broad[[column for column in PRIMARY_BENCHMARKS if column in broad.columns]], how="left")
        .reset_index()
    )
    benchmark_summary = (
        subset.groupby("benchmark")
        .agg(
            labels_observed=("model_configuration", "nunique"),
            mean_accuracy=("accuracy", "mean"),
            median_accuracy=("accuracy", "median"),
            mean_cost=("total_cost", "mean"),
            median_cost=("total_cost", "median"),
        )
        .reset_index()
    )
    return model_summary, benchmark_summary


def plot_slopegraphs(data: pd.DataFrame, path: Path) -> None:
    """Create a supplementary rank-line plot for three all-six-workload labels.

    Ranks are computed among all displayed Generalist labels available on each
    benchmark. Ties receive average ranks; marker positions are slightly offset
    horizontally only to keep tied series visible.
    """
    subset = data[data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)].copy()
    counts = subset.groupby("model_configuration")["benchmark"].nunique().sort_values(ascending=False)
    selected = [
        "Claude-3.7 Sonnet (February 2025)",
        "DeepSeek V3 (March 2025)",
        "o4-mini High (April 2025)",
    ]
    selected = [model for model in selected if model in counts.index]
    colors = ["#0072B2", "#D55E00", "#009E73"]
    markers = ["o", "s", "^"]
    positions = np.arange(len(PRIMARY_BENCHMARKS))
    labels = ["CORE", "GAIA", "SciCode", "SAB", "SWE-mini", "TAU"]

    figure, axes = plt.subplots(1, 2, figsize=(7.1, 3.25), sharey=True, constrained_layout=True)
    for axis, metric, title, ascending in [
        (axes[0], "accuracy", "Accuracy rank", False),
        (axes[1], "total_cost", "Dollar-cost rank", True),
    ]:
        ranks = subset.pivot(index="model_configuration", columns="benchmark", values=metric).reindex(columns=PRIMARY_BENCHMARKS)
        ranks = ranks.rank(axis=0, method="average", ascending=ascending)
        maximum_rank = int(np.nanmax(ranks.to_numpy()))
        for model_index, (color, marker, model) in enumerate(zip(colors, markers, selected, strict=True)):
            values = ranks.loc[model].to_numpy()
            shifted_positions = positions + (model_index - 1) * 0.055
            axis.plot(
                shifted_positions,
                values,
                marker=marker,
                linewidth=1.8,
                markersize=4.5,
                color=color,
                label=model.replace(" (April 2025)", "").replace(" (February 2025)", ""),
            )
        axis.set_title(title, fontsize=10)
        axis.set_xticks(positions, labels, rotation=35, ha="right", fontsize=7)
        axis.set_ylim(maximum_rank + 0.5, 0.5)
        axis.set_ylabel("Rank (1 = best)", fontsize=8)
        axis.grid(axis="y", alpha=0.25)
    axes[1].legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=6.7, frameon=False)
    figure.savefig(path, bbox_inches="tight")
    figure.savefig(path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    verify_frozen_input(INPUT)
    data = add_frontiers(load_data(INPUT))
    pairs, _ = fixed_scaffold_pairwise_analysis(data, n_bootstrap=10_000, seed=SEED)
    pairs.to_csv(OUT / "pairwise_bootstrap_10000.csv", index=False)

    corrections = multiple_comparisons(data, pairs)
    corrections.to_csv(OUT / "holm_bonferroni.csv", index=False)

    quartiles = quartile_rank_changes(data, pairs)
    quartiles.to_csv(OUT / "quartile_rank_changes.csv", index=False)

    frontier_summary, tolerant_rates = full_frontier_sensitivity(data)
    frontier_summary.to_csv(OUT / "frontier_definition_sensitivity.csv", index=False)
    tolerant_rates.to_csv(OUT / "tolerant_frontier_rates.csv", index=False)

    nulls = pairwise_nulls(data, pairs, simulations=10_000)
    nulls.to_csv(OUT / "permutation_nulls_10000.csv", index=False)

    model_missingness, benchmark_missingness = missingness_summary(data)
    model_missingness.to_csv(OUT / "missingness_by_model_label.csv", index=False)
    benchmark_missingness.to_csv(OUT / "missingness_by_benchmark.csv", index=False)

    figure_path = OUT / "rank_change_slopegraph.pdf"
    plot_slopegraphs(data, figure_path)

    summary = {
        "bootstrap_resamples": 10_000,
        "null_permutations": 10_000,
        "seed": SEED,
        "source_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "primary_scaffold": GENERALIST,
        "primary_benchmarks": PRIMARY_BENCHMARKS,
    }
    (OUT / "reviewer_checks_metadata.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
