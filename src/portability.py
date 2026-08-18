"""Aggregate-only portability and cost-per-success analyses.

The functions in this module require only per-benchmark aggregate accuracy and
cost. They deliberately do not infer per-task success cost, retry behavior, or
trace-level reliability from aggregate rows.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def cost_per_success(
    costs: pd.Series,
    accuracies: pd.Series,
    *,
    minimum_accuracy: float | None,
) -> pd.Series:
    """Compute aggregate dollars per expected success.

    Accuracy must be expressed as a fraction in [0, 1]. With ``None``, rows at
    zero accuracy are returned as missing because the ratio is undefined. With a
    predeclared positive floor, the denominator is max(accuracy, floor); this is
    a sensitivity metric, not observed per-success spending.
    """
    cost_values = pd.Series(costs, dtype=float)
    accuracy_values = pd.Series(accuracies, dtype=float)
    if (accuracy_values < 0).any() or (accuracy_values > 1).any():
        raise ValueError("accuracies must be fractions in [0, 1]")
    if minimum_accuracy is not None and not 0 < minimum_accuracy <= 1:
        raise ValueError("minimum_accuracy must be in (0, 1]")
    if minimum_accuracy is None:
        denominator = accuracy_values.where(accuracy_values > 0)
    else:
        denominator = accuracy_values.clip(lower=minimum_accuracy)
    return cost_values / denominator


def leave_one_benchmark_out_cost_prediction(
    data: pd.DataFrame,
    *,
    benchmark_column: str,
    label_column: str,
    cost_column: str,
    min_training_benchmarks: int = 2,
) -> pd.DataFrame:
    """Predict held-out benchmark cost from label propensity on other benchmarks.

    For each held-out benchmark, costs are first centered in log space within
    each training benchmark. Each label's predicted held-out centered cost is
    its average centered log cost over the remaining benchmarks. The held-out
    benchmark mean log cost is then added only for scale; within-benchmark rank
    is determined by the label propensity. A label must occur in at least
    ``min_training_benchmarks`` other benchmarks to be predicted.
    """
    frame = data[[benchmark_column, label_column, cost_column]].dropna().copy()
    if (frame[cost_column] <= 0).any():
        raise ValueError("cost values must be strictly positive")
    frame["log_cost"] = np.log(frame[cost_column].astype(float))
    outputs: list[pd.DataFrame] = []
    for held_out in sorted(frame[benchmark_column].unique()):
        train = frame[~frame[benchmark_column].eq(held_out)].copy()
        test = frame[frame[benchmark_column].eq(held_out)].copy()
        train["centered_log_cost"] = train["log_cost"] - train.groupby(benchmark_column)["log_cost"].transform("mean")
        propensity = train.groupby(label_column).agg(
            training_benchmarks=(benchmark_column, "nunique"),
            mean_centered_log_cost=("centered_log_cost", "mean"),
        )
        propensity = propensity[propensity["training_benchmarks"] >= min_training_benchmarks]
        predicted = test.join(propensity, on=label_column, how="inner")
        if predicted.empty:
            continue
        held_out_mean = test["log_cost"].mean()
        predicted["held_out_benchmark"] = held_out
        predicted["observed_log_cost"] = predicted["log_cost"]
        predicted["predicted_log_cost"] = held_out_mean + predicted["mean_centered_log_cost"]
        outputs.append(predicted)
    return pd.concat(outputs, ignore_index=True) if outputs else pd.DataFrame()


def lobo_rank_summary(
    predictions: pd.DataFrame,
    *,
    n_permutations: int = 20_000,
    seed: int = 20260818,
) -> pd.DataFrame:
    """Summarize held-out rank fidelity with within-benchmark permutation tests."""
    rows: list[dict[str, float | int | str]] = []
    generator = np.random.default_rng(seed)
    for benchmark, group in predictions.groupby("held_out_benchmark"):
        observed_result = spearmanr(group["observed_log_cost"], group["predicted_log_cost"])
        observed = float(observed_result.statistic)
        p_value = float(observed_result.pvalue)
        null = np.asarray(
            [
                float(spearmanr(group["observed_log_cost"], generator.permutation(group["predicted_log_cost"])).statistic)
                for _ in range(n_permutations)
            ]
        )
        empirical_p = (1 + int(np.sum(np.abs(null) >= abs(observed)))) / (n_permutations + 1)
        rows.append(
            {
                "held_out_benchmark": benchmark,
                "n_predicted_labels": int(len(group)),
                "spearman_rho": float(observed),
                "spearman_p": float(p_value),
                "permutation_p_two_sided": float(empirical_p),
                "null_q025": float(np.quantile(null, 0.025)),
                "null_q975": float(np.quantile(null, 0.975)),
                "n_permutations": int(n_permutations),
                "mean_absolute_log_error": float(
                    np.mean(np.abs(group["observed_log_cost"] - group["predicted_log_cost"]))
                ),
            }
        )
    return pd.DataFrame(rows)
