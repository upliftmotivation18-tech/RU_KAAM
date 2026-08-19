"""Finite-label inference for aggregate CostPerSuccess rank portability."""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr


def _rho(first: np.ndarray, second: np.ndarray) -> float:
    value = spearmanr(first, second).statistic
    return float(value)


def bootstrap_rank_pair(
    first: np.ndarray,
    second: np.ndarray,
    *,
    n_resamples: int = 10_000,
    seed: int = 20260818,
) -> dict[str, float | int]:
    """Resample shared configurations jointly and compute a percentile interval."""
    first = np.asarray(first, dtype=float)
    second = np.asarray(second, dtype=float)
    if len(first) != len(second) or len(first) < 2:
        raise ValueError("paired arrays of length at least two required")
    point = _rho(first, second)
    generator = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(n_resamples):
        idx = generator.integers(0, len(first), size=len(first))
        value = _rho(first[idx], second[idx])
        if np.isfinite(value):
            values.append(value)
    array = np.asarray(values)
    return {
        "point_rho": point,
        "ci_low": float(np.quantile(array, 0.025)) if len(array) else float("nan"),
        "ci_high": float(np.quantile(array, 0.975)) if len(array) else float("nan"),
        "valid_resamples": int(len(array)),
        "degenerate_resamples": int(n_resamples - len(array)),
        "n_resamples": int(n_resamples),
    }


def permutation_rank_pair(
    first: np.ndarray,
    second: np.ndarray,
    *,
    n_permutations: int = 20_000,
    seed: int = 20260818,
) -> dict[str, float | int]:
    """Two-sided label-pairing permutation test for a rank association."""
    first = np.asarray(first, dtype=float)
    second = np.asarray(second, dtype=float)
    point = _rho(first, second)
    generator = np.random.default_rng(seed)
    null = np.asarray([_rho(first, generator.permutation(second)) for _ in range(n_permutations)])
    p_value = (1 + int(np.sum(np.abs(null) >= abs(point)))) / (n_permutations + 1)
    return {
        "permutation_p_two_sided": float(p_value),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "n_permutations": int(n_permutations),
    }


def paired_raw_cps_contrast(
    raw_first: np.ndarray,
    raw_second: np.ndarray,
    cps_first: np.ndarray,
    cps_second: np.ndarray,
    *,
    n_resamples: int = 10_000,
    seed: int = 20260818,
) -> dict[str, float | int]:
    """Bootstrap difference in raw-cost and CPS rank correlations on shared rows."""
    arrays = [np.asarray(x, dtype=float) for x in (raw_first, raw_second, cps_first, cps_second)]
    if len({len(x) for x in arrays}) != 1 or len(arrays[0]) < 2:
        raise ValueError("four paired arrays of equal length at least two required")
    raw_point = _rho(arrays[0], arrays[1])
    cps_point = _rho(arrays[2], arrays[3])
    point = raw_point - cps_point
    generator = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(n_resamples):
        idx = generator.integers(0, len(arrays[0]), size=len(arrays[0]))
        raw = _rho(arrays[0][idx], arrays[1][idx])
        cps = _rho(arrays[2][idx], arrays[3][idx])
        if np.isfinite(raw) and np.isfinite(cps):
            values.append(raw - cps)
    sampled = np.asarray(values)
    return {
        "point_difference": float(point),
        "ci_low": float(np.quantile(sampled, 0.025)) if len(sampled) else float("nan"),
        "ci_high": float(np.quantile(sampled, 0.975)) if len(sampled) else float("nan"),
        "valid_resamples": int(len(sampled)),
        "degenerate_resamples": int(n_resamples - len(sampled)),
        "n_resamples": int(n_resamples),
    }


def holm_adjust(p_values: np.ndarray) -> np.ndarray:
    """Holm--Bonferroni adjusted p-values in original order."""
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    adjusted_sorted = np.maximum.accumulate((len(values) - np.arange(len(values))) * values[order])
    adjusted = np.empty_like(values)
    adjusted[order] = np.minimum(adjusted_sorted, 1.0)
    return adjusted
