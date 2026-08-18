"""Observed model-label cost-propensity adjustment for the frozen HAL snapshot.

This module does not infer provider list prices. It estimates a descriptive
additive decomposition of observed log dollar cost into benchmark and displayed
model-label components, then examines whether residual cost ranks transfer.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


@dataclass(frozen=True)
class CostPropensityFit:
    residuals: np.ndarray
    fitted: np.ndarray
    summary: dict[str, float | int]


def fit_cost_propensity_model(
    data: pd.DataFrame,
    *,
    label_column: str,
    benchmark_column: str,
    cost_column: str,
) -> CostPropensityFit:
    """Fit log-cost ~ displayed-label FE + benchmark FE using least squares.

    One category per fixed-effect family is omitted as a reference. Residuals
    describe cost deviations after removing the observed cross-workload cost
    propensity of each displayed label and each benchmark's average cost level.
    They must not be interpreted as price-adjusted or causal execution costs.
    """
    frame = data[[label_column, benchmark_column, cost_column]].dropna().copy()
    if (frame[cost_column] <= 0).any():
        raise ValueError("Cost values must be strictly positive for log-cost modeling")
    labels = sorted(frame[label_column].unique())
    benchmarks = sorted(frame[benchmark_column].unique())
    if len(labels) < 2 or len(benchmarks) < 2:
        raise ValueError("At least two labels and two benchmarks are required")

    intercept = np.ones((len(frame), 1))
    label_design = np.column_stack(
        [(frame[label_column].to_numpy() == label).astype(float) for label in labels[1:]]
    )
    benchmark_design = np.column_stack(
        [(frame[benchmark_column].to_numpy() == benchmark).astype(float) for benchmark in benchmarks[1:]]
    )
    design = np.column_stack([intercept, label_design, benchmark_design])
    response = np.log(frame[cost_column].to_numpy(float))
    coefficients, _, _, _ = np.linalg.lstsq(design, response, rcond=None)
    fitted = design @ coefficients
    residuals = response - fitted
    residual_df = len(frame) - design.shape[1]
    residual_ss = float(np.sum(residuals**2))
    total_ss = float(np.sum((response - response.mean()) ** 2))
    r_squared = 1 - residual_ss / total_ss if total_ss else float("nan")
    adjusted_r_squared = 1 - (1 - r_squared) * (len(frame) - 1) / residual_df
    summary = {
        "n_observations": int(len(frame)),
        "n_labels": int(len(labels)),
        "n_benchmarks": int(len(benchmarks)),
        "n_parameters": int(design.shape[1]),
        "residual_df": int(residual_df),
        "r_squared": float(r_squared),
        "adjusted_r_squared": float(adjusted_r_squared),
        "residual_sd": float(np.sqrt(residual_ss / residual_df)),
    }
    return CostPropensityFit(residuals=residuals, fitted=fitted, summary=summary)


def residual_pair_statistics(
    data: pd.DataFrame,
    *,
    benchmark_a: str,
    benchmark_b: str,
    label_column: str,
    benchmark_column: str,
    residual_column: str,
    n_permutations: int = 20_000,
    seed: int = 20260818,
) -> dict[str, float | int]:
    """Compute shared-label residual-cost rank association and permutation p-value."""
    first = data[data[benchmark_column].eq(benchmark_a)].set_index(label_column)
    second = data[data[benchmark_column].eq(benchmark_b)].set_index(label_column)
    shared = sorted(set(first.index) & set(second.index))
    if len(shared) < 2:
        raise ValueError("At least two shared labels are required")
    first_values = first.loc[shared, residual_column].to_numpy(float)
    second_values = second.loc[shared, residual_column].to_numpy(float)
    observed = float(spearmanr(first_values, second_values).statistic)
    generator = np.random.default_rng(seed)
    null = np.asarray(
        [float(spearmanr(first_values, generator.permutation(second_values)).statistic) for _ in range(n_permutations)]
    )
    p_value = (1 + int(np.sum(np.abs(null) >= abs(observed)))) / (n_permutations + 1)
    return {
        "n_shared": int(len(shared)),
        "residual_spearman": observed,
        "permutation_p_two_sided": float(p_value),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "n_permutations": int(n_permutations),
    }
