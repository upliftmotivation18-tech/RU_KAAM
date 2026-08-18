"""Run aggregate-only next-stage analyses feasible from the public HAL CSV."""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_analysis import GENERALIST, PRIMARY_BENCHMARKS, add_frontiers, load_data, verify_frozen_input
from src.portability import cost_per_success, leave_one_benchmark_out_cost_prediction, lobo_rank_summary

INPUT = ROOT / "data" / "all_leaderboards_costs_HAL.csv"
OUT = ROOT / "outputs" / "aggregate_efficiency"


def pair_metric_correlations(data: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows = []
    for index, first_benchmark in enumerate(PRIMARY_BENCHMARKS):
        for second_benchmark in PRIMARY_BENCHMARKS[index + 1 :]:
            first = data[data["benchmark"].eq(first_benchmark)].set_index("model_configuration")
            second = data[data["benchmark"].eq(second_benchmark)].set_index("model_configuration")
            shared = sorted(set(first.index) & set(second.index))
            if len(shared) < 5:
                continue
            result = spearmanr(first.loc[shared, metric], second.loc[shared, metric])
            rows.append(
                {
                    "benchmark_a": first_benchmark,
                    "benchmark_b": second_benchmark,
                    "n_shared": len(shared),
                    "spearman_rho": float(result.statistic),
                    "spearman_p": float(result.pvalue),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    verify_frozen_input(INPUT)
    data = add_frontiers(load_data(INPUT))
    cohort = data[
        data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)
    ].copy()
    # HAL reports accuracy in percent, while cost-per-success requires a fraction.
    cohort["accuracy_fraction"] = cohort["accuracy"] / 100.0
    cohort["cost_per_success_nonzero"] = cost_per_success(
        cohort["total_cost"], cohort["accuracy_fraction"], minimum_accuracy=None
    )
    cohort["cost_per_success_floor_1pct"] = cost_per_success(
        cohort["total_cost"], cohort["accuracy_fraction"], minimum_accuracy=0.01
    )
    cohort["cost_per_success_floor_5pct"] = cost_per_success(
        cohort["total_cost"], cohort["accuracy_fraction"], minimum_accuracy=0.05
    )
    cohort.to_csv(OUT / "generalist_cost_per_success_rows.csv", index=False)

    nonzero = cohort.dropna(subset=["cost_per_success_nonzero"])
    pair_metric_correlations(nonzero, "cost_per_success_nonzero").to_csv(
        OUT / "cost_per_success_nonzero_pairs.csv", index=False
    )
    pair_metric_correlations(cohort, "cost_per_success_floor_1pct").to_csv(
        OUT / "cost_per_success_floor_1pct_pairs.csv", index=False
    )
    pair_metric_correlations(cohort, "cost_per_success_floor_5pct").to_csv(
        OUT / "cost_per_success_floor_5pct_pairs.csv", index=False
    )

    predictions = leave_one_benchmark_out_cost_prediction(
        cohort,
        benchmark_column="benchmark",
        label_column="model_configuration",
        cost_column="total_cost",
        min_training_benchmarks=2,
    )
    predictions.to_csv(OUT / "lobo_cost_predictions.csv", index=False)
    lobo_rank_summary(predictions, n_permutations=20_000, seed=20260818).to_csv(OUT / "lobo_cost_rank_summary.csv", index=False)

    metadata = {
        "metric_definition": "CostPerSuccess = total_cost / max(accuracy_fraction, epsilon). Primary smoothing floor is epsilon=0.01; epsilon=0.05 and zero-accuracy exclusion are sensitivity analyses. This is aggregate dollars per expected success, not observed successful-run cost.",
        "lobo_definition": "For each held-out benchmark, estimate label centered log-cost propensity from other benchmarks only; predict held-out within-benchmark cost ranking from this propensity.",
        "interpretation": "Neither analysis identifies per-task successful-run cost, failure cost, retries, tool calls, tokens, or provider list-price effects.",
    }
    (OUT / "README.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
