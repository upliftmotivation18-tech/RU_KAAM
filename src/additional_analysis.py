"""Additional reviewer-oriented statistical analyses for the HAL study."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def holm_bonferroni(p_values: Sequence[float], *, alpha: float = 0.05) -> pd.DataFrame:
    """Apply the step-down Holm--Bonferroni correction to a family of p-values."""
    values = np.asarray(p_values, dtype=float)
    if values.ndim != 1 or len(values) == 0:
        raise ValueError("p_values must be a non-empty one-dimensional sequence")
    if np.any(~np.isfinite(values)) or np.any((values < 0) | (values > 1)):
        raise ValueError("p_values must be finite values in [0, 1]")

    count = len(values)
    order = np.argsort(values)
    sorted_values = values[order]
    adjusted_sorted = np.maximum.accumulate(
        np.minimum(1.0, (count - np.arange(count)) * sorted_values)
    )
    reject_sorted = np.zeros(count, dtype=bool)
    for position, value in enumerate(sorted_values):
        if value <= alpha / (count - position):
            reject_sorted[position] = True
        else:
            break

    adjusted = np.empty(count)
    rejected = np.empty(count, dtype=bool)
    adjusted[order] = adjusted_sorted
    rejected[order] = reject_sorted
    return pd.DataFrame({"p_value": values, "adjusted_p": adjusted, "reject": rejected})


def tolerant_nondominated_frontier(
    frame: pd.DataFrame,
    *,
    cost_column: str,
    accuracy_column: str,
    relative_tolerance: float = 0.05,
) -> pd.Series:
    """Return a conservative nondominated frontier under multiplicative tolerances.

    A candidate dominates another only if it is at least ``relative_tolerance``
    cheaper and at least ``relative_tolerance`` more accurate. Near-ties remain
    non-dominated, making the result a sensitivity analysis rather than a claim
    that reported values have known 5% measurement error.
    """
    if not 0 <= relative_tolerance < 1:
        raise ValueError("relative_tolerance must be in [0, 1)")
    values = frame[[cost_column, accuracy_column]].astype(float).to_numpy()
    membership: list[bool] = []
    for cost, accuracy in values:
        materially_cheaper = values[:, 0] <= cost * (1 - relative_tolerance)
        materially_more_accurate = values[:, 1] >= accuracy * (1 + relative_tolerance)
        membership.append(not bool(np.any(materially_cheaper & materially_more_accurate)))
    return pd.Series(membership, index=frame.index, name="tolerant_nondominated")


def null_label_shuffle(
    first: Sequence[float],
    second: Sequence[float],
    *,
    n_simulations: int = 1_000,
    seed: int = 20260816,
) -> dict[str, float | int]:
    """Permutation null for a pairwise Spearman association.

    Values are kept fixed while their pairing is randomized. This assesses whether
    the observed magnitude differs from random matching at its observed overlap,
    not whether labels were selected randomly for evaluation.
    """
    first_values = np.asarray(first, dtype=float)
    second_values = np.asarray(second, dtype=float)
    if first_values.shape != second_values.shape:
        raise ValueError("Input vectors must have the same length")
    if len(first_values) < 2:
        raise ValueError("At least two values are required")
    observed = float(spearmanr(first_values, second_values).statistic)
    generator = np.random.default_rng(seed)
    simulated = np.asarray(
        [
            float(spearmanr(first_values, generator.permutation(second_values)).statistic)
            for _ in range(n_simulations)
        ]
    )
    empirical_p = (1 + int(np.sum(np.abs(simulated) >= abs(observed)))) / (n_simulations + 1)
    lower, upper = np.quantile(simulated, [0.025, 0.975])
    return {
        "n": int(len(first_values)),
        "observed_rho": observed,
        "null_mean": float(np.mean(simulated)),
        "null_sd": float(np.std(simulated, ddof=1)),
        "null_q025": float(lower),
        "null_q975": float(upper),
        "two_sided_empirical_p": float(empirical_p),
        "n_simulations": int(n_simulations),
    }
