"""End-to-end reproducible analysis and figure generation for the HAL study."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.analysis import (
    bootstrap_rank_correlation,
    convex_hull_frontier,
    pairwise_rank_statistics,
    weak_pareto_frontier,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "all_leaderboards_costs_HAL.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs"
GENERALIST = "HAL Generalist Agent"
PRIMARY_BENCHMARKS = [
    "corebench_hard",
    "gaia",
    "scicode",
    "scienceagentbench",
    "swebench_verified_mini",
    "taubench_airline",
]
BENCHMARK_LABELS = {
    "corebench_hard": "CORE-Bench Hard",
    "gaia": "GAIA",
    "scicode": "SciCode",
    "scienceagentbench": "ScienceAgentBench",
    "swebench_verified_mini": "SWE-bench Mini",
    "taubench_airline": "TAU Airline",
    "assistantbench": "AssistantBench",
    "online_mind2web": "Online Mind2Web",
    "usaco": "USACO",
}


def load_data(input_path: Path) -> pd.DataFrame:
    """Load the frozen source CSV and add unambiguous analysis identifiers."""
    data = pd.read_csv(input_path)
    required = {"Benchmark", "Agent Name", "Models", "Accuracy", "Total Cost", "Is Pareto", "Runs"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {sorted(missing)}")
    if data.duplicated(["Benchmark", "Agent Name", "Models"]).any():
        raise ValueError("Expected one displayed row per benchmark/scaffold/model configuration")
    data = data.rename(
        columns={
            "Benchmark": "benchmark",
            "Agent Name": "scaffold",
            "Models": "model_configuration",
            "Accuracy": "accuracy",
            "Total Cost": "total_cost",
            "Is Pareto": "hal_is_pareto",
            "Runs": "runs",
        }
    )
    data["configuration"] = data["scaffold"] + " || " + data["model_configuration"]
    return data


def add_frontiers(data: pd.DataFrame) -> pd.DataFrame:
    """Add weak and HAL-style convex-hull membership per full benchmark cohort."""
    output = data.copy()
    output["weak_pareto"] = (
        output.groupby("benchmark", group_keys=False)
        .apply(
            lambda frame: weak_pareto_frontier(
                frame, cost_column="total_cost", accuracy_column="accuracy"
            ),
            include_groups=False,
        )
        .astype(bool)
    )
    output["convex_hull"] = (
        output.groupby("benchmark", group_keys=False)
        .apply(
            lambda frame: convex_hull_frontier(
                frame, cost_column="total_cost", accuracy_column="accuracy"
            ),
            include_groups=False,
        )
        .astype(bool)
    )
    return output


def coverage_tables(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return scaffold, configuration, and model coverage tables."""
    scaffold_by_benchmark = pd.crosstab(data["scaffold"], data["benchmark"])
    configuration_by_benchmark = pd.crosstab(data["configuration"], data["benchmark"])
    model_by_benchmark = pd.crosstab(data["model_configuration"], data["benchmark"])
    return scaffold_by_benchmark, configuration_by_benchmark, model_by_benchmark


def fixed_scaffold_pairwise_analysis(
    data: pd.DataFrame,
    *,
    scaffold: str = GENERALIST,
    benchmarks: list[str] = PRIMARY_BENCHMARKS,
    minimum_overlap: int = 5,
    n_bootstrap: int = 5_000,
    seed: int = 20260816,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute pairwise rank transfer and two frontier similarity variants.

    ``global`` frontier metrics use each benchmark's full fixed-scaffold cohort.
    ``common_cohort`` metrics recompute the frontier after limiting both sides to
    the pair's shared configurations. Both are reported because competitor-set
    composition itself changes a frontier.
    """
    subset = data[
        data["scaffold"].eq(scaffold) & data["benchmark"].isin(benchmarks)
    ].copy()
    subset["fixed_weak_pareto"] = (
        subset.groupby("benchmark", group_keys=False)
        .apply(
            lambda frame: weak_pareto_frontier(
                frame, cost_column="total_cost", accuracy_column="accuracy"
            ),
            include_groups=False,
        )
        .astype(bool)
    )
    subset["fixed_convex_hull"] = (
        subset.groupby("benchmark", group_keys=False)
        .apply(
            lambda frame: convex_hull_frontier(
                frame, cost_column="total_cost", accuracy_column="accuracy"
            ),
            include_groups=False,
        )
        .astype(bool)
    )

    results: list[dict[str, object]] = []
    for benchmark_a, benchmark_b in combinations(benchmarks, 2):
        first = subset[subset["benchmark"].eq(benchmark_a)].copy()
        second = subset[subset["benchmark"].eq(benchmark_b)].copy()
        shared = sorted(set(first["model_configuration"]) & set(second["model_configuration"]))
        if len(shared) < minimum_overlap:
            continue

        first_common = first.set_index("model_configuration").loc[shared].reset_index()
        second_common = second.set_index("model_configuration").loc[shared].reset_index()
        first_common["weak_common"] = weak_pareto_frontier(
            first_common, cost_column="total_cost", accuracy_column="accuracy"
        )
        second_common["weak_common"] = weak_pareto_frontier(
            second_common, cost_column="total_cost", accuracy_column="accuracy"
        )
        first_common["hull_common"] = convex_hull_frontier(
            first_common, cost_column="total_cost", accuracy_column="accuracy"
        )
        second_common["hull_common"] = convex_hull_frontier(
            second_common, cost_column="total_cost", accuracy_column="accuracy"
        )

        weak_statistics = pairwise_rank_statistics(
            first_common,
            second_common,
            configuration_column="model_configuration",
            accuracy_column="accuracy",
            cost_column="total_cost",
            frontier_column="weak_common",
        )
        hull_statistics = pairwise_rank_statistics(
            first_common,
            second_common,
            configuration_column="model_configuration",
            accuracy_column="accuracy",
            cost_column="total_cost",
            frontier_column="hull_common",
        )
        accuracy_bootstrap = bootstrap_rank_correlation(
            first_common["accuracy"],
            second_common["accuracy"],
            method="spearman",
            n_bootstrap=n_bootstrap,
            seed=seed,
        )
        cost_bootstrap = bootstrap_rank_correlation(
            first_common["total_cost"],
            second_common["total_cost"],
            method="spearman",
            n_bootstrap=n_bootstrap,
            seed=seed + 1,
        )

        global_weak_a = set(
            first.loc[first["fixed_weak_pareto"], "model_configuration"]
        ) & set(shared)
        global_weak_b = set(
            second.loc[second["fixed_weak_pareto"], "model_configuration"]
        ) & set(shared)
        global_hull_a = set(
            first.loc[first["fixed_convex_hull"], "model_configuration"]
        ) & set(shared)
        global_hull_b = set(
            second.loc[second["fixed_convex_hull"], "model_configuration"]
        ) & set(shared)

        def jaccard(first_set: set[str], second_set: set[str]) -> float:
            union = first_set | second_set
            return len(first_set & second_set) / len(union) if union else float("nan")

        results.append(
            {
                "benchmark_a": benchmark_a,
                "benchmark_b": benchmark_b,
                "benchmark_a_label": BENCHMARK_LABELS[benchmark_a],
                "benchmark_b_label": BENCHMARK_LABELS[benchmark_b],
                "n_shared": len(shared),
                "accuracy_spearman": weak_statistics["accuracy_spearman"],
                "accuracy_kendall": weak_statistics["accuracy_kendall"],
                "cost_spearman": weak_statistics["cost_spearman"],
                "cost_kendall": weak_statistics["cost_kendall"],
                "accuracy_spearman_ci_low": accuracy_bootstrap["ci_low"],
                "accuracy_spearman_ci_high": accuracy_bootstrap["ci_high"],
                "cost_spearman_ci_low": cost_bootstrap["ci_low"],
                "cost_spearman_ci_high": cost_bootstrap["ci_high"],
                "weak_jaccard_common_cohort": weak_statistics["frontier_jaccard"],
                "convex_hull_jaccard_common_cohort": hull_statistics["frontier_jaccard"],
                "weak_jaccard_global": jaccard(global_weak_a, global_weak_b),
                "convex_hull_jaccard_global": jaccard(global_hull_a, global_hull_b),
                "weak_global_frontier_a": len(global_weak_a),
                "weak_global_frontier_b": len(global_weak_b),
                "hull_global_frontier_a": len(global_hull_a),
                "hull_global_frontier_b": len(global_hull_b),
            }
        )

    configuration_rates = (
        subset.groupby("model_configuration")
        .agg(
            benchmarks_tested=("benchmark", "size"),
            weak_frontier_appearances=("fixed_weak_pareto", "sum"),
            hull_frontier_appearances=("fixed_convex_hull", "sum"),
        )
        .assign(
            weak_frontier_rate=lambda frame: frame["weak_frontier_appearances"]
            / frame["benchmarks_tested"],
            hull_frontier_rate=lambda frame: frame["hull_frontier_appearances"]
            / frame["benchmarks_tested"],
        )
        .reset_index()
        .sort_values(["benchmarks_tested", "weak_frontier_rate"], ascending=[False, False])
    )
    return pd.DataFrame(results), configuration_rates


def scaffold_sensitivity(data: pd.DataFrame, minimum_overlap: int = 5) -> pd.DataFrame:
    """Summarize paired model changes between scaffolds within each benchmark."""
    results: list[dict[str, object]] = []
    for benchmark, benchmark_data in data.groupby("benchmark"):
        scaffolds = sorted(benchmark_data["scaffold"].unique())
        for scaffold_a, scaffold_b in combinations(scaffolds, 2):
            first = benchmark_data[benchmark_data["scaffold"].eq(scaffold_a)].set_index(
                "model_configuration"
            )
            second = benchmark_data[benchmark_data["scaffold"].eq(scaffold_b)].set_index(
                "model_configuration"
            )
            shared = sorted(set(first.index) & set(second.index))
            if len(shared) < minimum_overlap:
                continue
            accuracy_difference = second.loc[shared, "accuracy"] - first.loc[shared, "accuracy"]
            log_cost_ratio = np.log(
                second.loc[shared, "total_cost"] / first.loc[shared, "total_cost"]
            )
            results.append(
                {
                    "benchmark": benchmark,
                    "benchmark_label": BENCHMARK_LABELS.get(benchmark, benchmark),
                    "scaffold_a": scaffold_a,
                    "scaffold_b": scaffold_b,
                    "n_shared": len(shared),
                    "mean_accuracy_difference_b_minus_a": accuracy_difference.mean(),
                    "median_accuracy_difference_b_minus_a": accuracy_difference.median(),
                    "b_accuracy_wins": int((accuracy_difference > 0).sum()),
                    "accuracy_ties": int((accuracy_difference == 0).sum()),
                    "mean_log_cost_ratio_b_over_a": log_cost_ratio.mean(),
                    "median_log_cost_ratio_b_over_a": log_cost_ratio.median(),
                }
            )
    return pd.DataFrame(results)


def plot_coverage(data: pd.DataFrame, output_path: Path) -> None:
    """Plot primary-cohort model availability before making any transfer claim."""
    subset = data[
        data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)
    ]
    matrix = pd.crosstab(subset["model_configuration"], subset["benchmark"])
    matrix = matrix.reindex(columns=PRIMARY_BENCHMARKS, fill_value=0)
    matrix = matrix.loc[matrix.sum(axis=1).sort_values(ascending=False).index]
    displayed = (matrix > 0).astype(int)
    displayed.columns = [BENCHMARK_LABELS[column] for column in displayed.columns]

    figure, axis = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        displayed,
        cmap=sns.color_palette(["#f3f4f6", "#1d4ed8"]),
        cbar=False,
        linewidths=0.4,
        linecolor="white",
        ax=axis,
    )
    axis.set_title("Primary-cohort coverage: HAL Generalist Agent")
    axis.set_xlabel("Benchmark")
    axis.set_ylabel("Model configuration")
    axis.tick_params(axis="x", rotation=35)
    figure.tight_layout()
    figure.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(figure)


def plot_similarity_matrix(pairwise: pd.DataFrame, output_path: Path) -> None:
    """Create paired accuracy and cost rank-transfer matrices annotated with N."""
    labels = [BENCHMARK_LABELS[benchmark] for benchmark in PRIMARY_BENCHMARKS]
    matrices = []
    annotations = []
    for value_column in ["accuracy_spearman", "cost_spearman"]:
        matrix = pd.DataFrame(np.nan, index=PRIMARY_BENCHMARKS, columns=PRIMARY_BENCHMARKS)
        annotation = pd.DataFrame("", index=PRIMARY_BENCHMARKS, columns=PRIMARY_BENCHMARKS)
        for benchmark in PRIMARY_BENCHMARKS:
            matrix.loc[benchmark, benchmark] = 1.0
            annotation.loc[benchmark, benchmark] = "—"
        for _, row in pairwise.iterrows():
            first, second = row["benchmark_a"], row["benchmark_b"]
            matrix.loc[first, second] = row[value_column]
            matrix.loc[second, first] = row[value_column]
            text = f"{row[value_column]:.2f}\nN={int(row['n_shared'])}"
            annotation.loc[first, second] = text
            annotation.loc[second, first] = text
        matrix.index = labels
        matrix.columns = labels
        annotation.index = labels
        annotation.columns = labels
        matrices.append(matrix)
        annotations.append(annotation)

    figure, axes = plt.subplots(1, 2, figsize=(15, 6.5), constrained_layout=True)
    for axis, matrix, annotation, title in zip(
        axes,
        matrices,
        annotations,
        ["Accuracy-rank transfer (Spearman ρ)", "Dollar-cost-rank transfer (Spearman ρ)"],
        strict=True,
    ):
        sns.heatmap(
            matrix,
            annot=annotation,
            fmt="",
            vmin=-1,
            vmax=1,
            center=0,
            cmap="vlag",
            linewidths=0.5,
            linecolor="white",
            cbar_kws={"label": "Spearman ρ"},
            square=True,
            ax=axis,
        )
        axis.set_title(title)
        axis.set_xlabel("")
        axis.set_ylabel("")
        axis.tick_params(axis="x", rotation=45)
        axis.tick_params(axis="y", rotation=0)
    figure.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(figure)


def plot_pareto_membership(data: pd.DataFrame, output_path: Path) -> None:
    """Plot weak-Pareto membership for the fixed-scaffold primary cohort."""
    subset = data[
        data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)
    ].copy()
    subset["fixed_weak_pareto"] = (
        subset.groupby("benchmark", group_keys=False)
        .apply(
            lambda frame: weak_pareto_frontier(
                frame, cost_column="total_cost", accuracy_column="accuracy"
            ),
            include_groups=False,
        )
        .astype(int)
    )
    matrix = subset.pivot(
        index="model_configuration", columns="benchmark", values="fixed_weak_pareto"
    ).reindex(columns=PRIMARY_BENCHMARKS)
    matrix["Frontier rate"] = matrix.mean(axis=1, skipna=True)
    matrix = matrix.loc[matrix["Frontier rate"].sort_values(ascending=False).index]
    displayed = matrix.copy()
    displayed.columns = [BENCHMARK_LABELS.get(column, column) for column in displayed.columns]

    figure, axis = plt.subplots(figsize=(11, 8))
    sns.heatmap(
        displayed,
        cmap=sns.color_palette(["#f3f4f6", "#f59e0b", "#7c2d12"], as_cmap=True),
        vmin=0,
        vmax=1,
        annot=True,
        fmt=".2g",
        linewidths=0.4,
        linecolor="white",
        cbar_kws={"label": "Weak Pareto membership / rate"},
        ax=axis,
    )
    axis.set_title("Weak-Pareto membership across fixed-scaffold workloads")
    axis.set_xlabel("Benchmark; final column = available-benchmark membership rate")
    axis.set_ylabel("Model configuration")
    axis.tick_params(axis="x", rotation=35)
    figure.tight_layout()
    figure.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(figure)


def write_outputs(
    data: pd.DataFrame,
    pairwise: pd.DataFrame,
    configuration_rates: pd.DataFrame,
    sensitivity: pd.DataFrame,
    output_directory: Path,
) -> None:
    """Persist every table needed to reproduce reported results."""
    output_directory.mkdir(parents=True, exist_ok=True)
    tables = output_directory / "tables"
    figures = output_directory / "figures"
    tables.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)

    data.to_csv(tables / "hal_with_reconstructed_frontiers.csv", index=False)
    pairwise.to_csv(tables / "generalist_pairwise_transfer.csv", index=False)
    configuration_rates.to_csv(tables / "generalist_frontier_rates.csv", index=False)
    sensitivity.to_csv(tables / "within_benchmark_scaffold_sensitivity.csv", index=False)

    label_audit = (
        data.assign(
            supplied_equals_weak=lambda frame: frame["hal_is_pareto"].eq(frame["weak_pareto"]),
            supplied_equals_hull=lambda frame: frame["hal_is_pareto"].eq(frame["convex_hull"]),
        )
        .groupby("benchmark")
        .agg(
            rows=("benchmark", "size"),
            supplied_frontier=("hal_is_pareto", "sum"),
            weak_frontier=("weak_pareto", "sum"),
            convex_hull_frontier=("convex_hull", "sum"),
            supplied_weak_agreement=("supplied_equals_weak", "mean"),
            supplied_hull_agreement=("supplied_equals_hull", "mean"),
        )
        .reset_index()
    )
    label_audit.to_csv(tables / "pareto_label_reproducibility.csv", index=False)

    scaffold_coverage, configuration_coverage, model_coverage = coverage_tables(data)
    scaffold_coverage.to_csv(tables / "scaffold_by_benchmark_coverage.csv")
    configuration_coverage.to_csv(tables / "configuration_by_benchmark_coverage.csv")
    model_coverage.to_csv(tables / "model_by_benchmark_coverage.csv")

    plot_coverage(data, figures / "coverage_heatmap.png")
    plot_similarity_matrix(pairwise, figures / "rank_transfer_similarity.png")
    plot_pareto_membership(data, figures / "weak_pareto_membership.png")

    metadata = {
        "source_csv": str(DEFAULT_INPUT),
        "primary_scaffold": GENERALIST,
        "primary_benchmarks": PRIMARY_BENCHMARKS,
        "minimum_pairwise_overlap": 5,
        "bootstrap_resamples": 5000,
        "bootstrap_seed": 20260816,
        "frontier_definitions": {
            "weak": "Standard weak non-dominance for discrete configuration selection.",
            "convex_hull": "HAL-style origin-anchored convex-hull frontier with randomized-policy interpretation.",
        },
    }
    (output_directory / "analysis_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap", type=int, default=5_000)
    arguments = parser.parse_args()

    data = add_frontiers(load_data(arguments.input))
    pairwise, configuration_rates = fixed_scaffold_pairwise_analysis(
        data, n_bootstrap=arguments.bootstrap
    )
    sensitivity = scaffold_sensitivity(data)
    write_outputs(data, pairwise, configuration_rates, sensitivity, arguments.output)


if __name__ == "__main__":
    main()
