"""LOBO influence and descriptive benchmark-characteristic diagnostics."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_analysis import GENERALIST, PRIMARY_BENCHMARKS, add_frontiers, load_data, verify_frozen_input
from src.portability import leave_one_benchmark_out_cost_prediction

INPUT = ROOT / "data" / "all_leaderboards_costs_HAL.csv"
OUT = ROOT / "outputs" / "v2_robustness"


def leave_one_label_out(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for benchmark, frame in predictions.groupby("held_out_benchmark"):
        for label in frame["model_configuration"]:
            keep = frame[~frame["model_configuration"].eq(label)]
            if len(keep) < 3:
                continue
            rho = spearmanr(keep["observed_log_cost"], keep["predicted_log_cost"]).statistic
            rows.append(
                {
                    "held_out_benchmark": benchmark,
                    "dropped_label": label,
                    "n_remaining": len(keep),
                    "lolo_spearman": float(rho),
                }
            )
    return pd.DataFrame(rows)


def benchmark_characteristics(cohort: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for benchmark, frame in cohort.groupby("benchmark"):
        accuracy = frame["accuracy"] / 100.0
        log_cost = np.log(frame["total_cost"])
        rows.append(
            {
                "benchmark": benchmark,
                "n_labels": len(frame),
                "accuracy_mean": float(accuracy.mean()),
                "accuracy_sd": float(accuracy.std(ddof=1)),
                "zero_accuracy_fraction": float(np.mean(accuracy.eq(0))),
                "log_cost_sd": float(log_cost.std(ddof=1)),
                "cost_median": float(frame["total_cost"].median()),
                "cost_max_over_median": float(frame["total_cost"].max() / frame["total_cost"].median()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    verify_frozen_input(INPUT)
    data = add_frontiers(load_data(INPUT))
    cohort = data[data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)].copy()
    predictions = leave_one_benchmark_out_cost_prediction(
        cohort,
        benchmark_column="benchmark",
        label_column="model_configuration",
        cost_column="total_cost",
        min_training_benchmarks=2,
    )
    influence = leave_one_label_out(predictions)
    influence.to_csv(OUT / "lobo_leave_one_label_out.csv", index=False)
    summary = influence.groupby("held_out_benchmark")["lolo_spearman"].agg(["min", "median", "max", "std", "count"]).reset_index()
    summary.to_csv(OUT / "lobo_leave_one_label_out_summary.csv", index=False)
    benchmark_characteristics(cohort).to_csv(OUT / "benchmark_characteristics.csv", index=False)
    (OUT / "README.md").write_text(
        "# V2 small-cohort robustness diagnostics\n\n"
        "Leave-one-label-out (LOLO) recalculates each LOBO held-out correlation after omitting one predicted label. "
        "It tests leverage within the observed finite cohort, not population stability. Benchmark characteristics are six-unit descriptive diagnostics only and are not used for domain-level regression or causal explanation.\n"
    )


if __name__ == "__main__":
    main()
