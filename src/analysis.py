"""Core reproducible analysis routines for cross-workload cost-efficiency study."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal
import warnings

import numpy as np
import pandas as pd
from scipy.stats import ConstantInputWarning, kendalltau, spearmanr

RankMethod = Literal["spearman", "kendall"]


def weak_pareto_frontier(
    frame: pd.DataFrame,
    *,
    cost_column: str,
    accuracy_column: str,
) -> pd.Series:
    """Return standard weak-Pareto membership for lower cost and higher accuracy.

    A point is retained when no other observed point has at least its accuracy and
    at most its cost, with one comparison strict. This represents discrete agent
    selection: an evaluator chooses one observed configuration, not a randomized
    mixture of configurations.
    """
    values = frame[[cost_column, accuracy_column]].astype(float).to_numpy()
    membership: list[bool] = []

    for cost, accuracy in values:
        dominates = (
            (values[:, 1] >= accuracy)
            & (values[:, 0] <= cost)
            & ((values[:, 1] > accuracy) | (values[:, 0] < cost))
        )
        membership.append(not bool(np.any(dominates)))

    return pd.Series(membership, index=frame.index, name="weak_pareto")


def convex_hull_frontier(
    frame: pd.DataFrame,
    *,
    cost_column: str,
    accuracy_column: str,
) -> pd.Series:
    """Reproduce HAL's origin-anchored cost--accuracy convex-hull frontier.

    HAL's public analysis adds the origin and keeps points on the upper concave
    envelope. It has a randomized-policy interpretation: an interior point can be
    excluded when a probabilistic mixture of two other configurations yields at
    least as much expected accuracy at no greater expected cost.
    """
    observed = frame[[cost_column, accuracy_column]].astype(float).to_numpy()
    points = np.vstack((np.array([[0.0, 0.0]]), observed))
    points = points[np.lexsort((points[:, 1], points[:, 0]))]

    def cross(origin: np.ndarray, first: np.ndarray, second: np.ndarray) -> float:
        return float(
            (first[0] - origin[0]) * (second[1] - origin[1])
            - (first[1] - origin[1]) * (second[0] - origin[0])
        )

    hull: list[tuple[float, float]] = []
    for point in points:
        while len(hull) >= 2 and cross(
            np.asarray(hull[-2]), np.asarray(hull[-1]), point
        ) >= 0:
            hull.pop()
        hull.append((float(point[0]), float(point[1])))

    monotonic_hull = [
        point
        for index, point in enumerate(hull)
        if index == 0 or point[1] >= hull[index - 1][1]
    ]
    frontier_points = monotonic_hull[1:]

    membership = [
        any(
            np.isclose(cost, frontier_cost, rtol=0.0, atol=1e-10)
            and np.isclose(accuracy, frontier_accuracy, rtol=0.0, atol=1e-10)
            for frontier_cost, frontier_accuracy in frontier_points
        )
        for cost, accuracy in observed
    ]
    return pd.Series(membership, index=frame.index, name="convex_hull")


def _rank_correlation(
    first: Sequence[float],
    second: Sequence[float],
    method: RankMethod,
) -> float:
    if method == "spearman":
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConstantInputWarning)
            return float(spearmanr(first, second).statistic)
    if method == "kendall":
        return float(kendalltau(first, second, variant="b").statistic)
    raise ValueError(f"Unsupported rank method: {method}")


def bootstrap_rank_correlation(
    first: Sequence[float],
    second: Sequence[float],
    *,
    method: RankMethod,
    n_bootstrap: int = 5_000,
    seed: int = 20260816,
) -> dict[str, float | int]:
    """Estimate a percentile bootstrap interval over shared configurations.

    The interval captures sensitivity to the finite set of shared configurations;
    it is not a rollout-level uncertainty interval because most HAL rows are
    single-run evaluations.
    """
    first_values = np.asarray(first, dtype=float)
    second_values = np.asarray(second, dtype=float)
    if first_values.shape != second_values.shape:
        raise ValueError("Input vectors must have the same length")
    if first_values.ndim != 1:
        raise ValueError("Input vectors must be one-dimensional")
    if len(first_values) < 2:
        raise ValueError("At least two shared configurations are required")
    if n_bootstrap < 1:
        raise ValueError("n_bootstrap must be positive")

    estimate = _rank_correlation(first_values, second_values, method)
    generator = np.random.default_rng(seed)
    bootstrap_values: list[float] = []
    for _ in range(n_bootstrap):
        indices = generator.integers(0, len(first_values), len(first_values))
        value = _rank_correlation(first_values[indices], second_values[indices], method)
        if np.isfinite(value):
            bootstrap_values.append(value)

    if not bootstrap_values:
        ci_low = float("nan")
        ci_high = float("nan")
    else:
        ci_low, ci_high = np.quantile(bootstrap_values, [0.025, 0.975]).tolist()

    return {
        "estimate": estimate,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n": int(len(first_values)),
        "n_valid_bootstrap": int(len(bootstrap_values)),
    }


def pairwise_rank_statistics(
    first: pd.DataFrame,
    second: pd.DataFrame,
    *,
    configuration_column: str,
    accuracy_column: str,
    cost_column: str,
    frontier_column: str,
) -> dict[str, float | int]:
    """Compute rank and frontier similarity statistics on shared configurations."""
    first_indexed = first.set_index(configuration_column)
    second_indexed = second.set_index(configuration_column)
    shared = sorted(set(first_indexed.index) & set(second_indexed.index))
    if len(shared) < 2:
        raise ValueError("At least two shared configurations are required")

    first_shared = first_indexed.loc[shared]
    second_shared = second_indexed.loc[shared]
    first_frontier = set(first_shared.index[first_shared[frontier_column].astype(bool)])
    second_frontier = set(second_shared.index[second_shared[frontier_column].astype(bool)])
    union = first_frontier | second_frontier

    return {
        "n_shared": int(len(shared)),
        "accuracy_spearman": _rank_correlation(
            first_shared[accuracy_column], second_shared[accuracy_column], "spearman"
        ),
        "accuracy_kendall": _rank_correlation(
            first_shared[accuracy_column], second_shared[accuracy_column], "kendall"
        ),
        "cost_spearman": _rank_correlation(
            first_shared[cost_column], second_shared[cost_column], "spearman"
        ),
        "cost_kendall": _rank_correlation(
            first_shared[cost_column], second_shared[cost_column], "kendall"
        ),
        "frontier_jaccard": float(len(first_frontier & second_frontier) / len(union))
        if union
        else float("nan"),
    }
