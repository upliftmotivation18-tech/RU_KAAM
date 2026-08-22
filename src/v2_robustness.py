"""Bootstrap effect sizes for paired external trace-burden metrics."""

from __future__ import annotations

import numpy as np


def paired_effect_summary(
    sweagent: np.ndarray,
    openhands: np.ndarray,
    *,
    n_resamples: int = 10_000,
    seed: int = 20260818,
) -> dict[str, float | int]:
    """Return paired median difference/ratio and percentile bootstrap intervals."""
    sweagent = np.asarray(sweagent, dtype=float)
    openhands = np.asarray(openhands, dtype=float)
    if len(sweagent) != len(openhands) or len(sweagent) < 2:
        raise ValueError("paired arrays with length at least two are required")
    difference = openhands - sweagent
    if np.any(sweagent <= 0):
        ratio = np.full_like(sweagent, np.nan)
        valid_ratio = np.zeros_like(sweagent, dtype=bool)
    else:
        ratio = openhands / sweagent
        valid_ratio = np.isfinite(ratio)
    generator = np.random.default_rng(seed)
    median_diffs = []
    median_ratios = []
    for _ in range(n_resamples):
        idx = generator.integers(0, len(sweagent), size=len(sweagent))
        median_diffs.append(float(np.median(difference[idx])))
        if valid_ratio.any():
            median_ratios.append(float(np.median(ratio[idx][np.isfinite(ratio[idx])])))
    return {
        "n_pairs": int(len(sweagent)),
        "median_difference": float(np.median(difference)),
        "median_difference_ci_low": float(np.quantile(median_diffs, 0.025)),
        "median_difference_ci_high": float(np.quantile(median_diffs, 0.975)),
        "median_ratio_openhands_over_sweagent": float(np.nanmedian(ratio)) if valid_ratio.any() else float("nan"),
        "median_ratio_ci_low": float(np.quantile(median_ratios, 0.025)) if median_ratios else float("nan"),
        "median_ratio_ci_high": float(np.quantile(median_ratios, 0.975)) if median_ratios else float("nan"),
        "openhands_lower_fraction": float(np.mean(openhands < sweagent)),
    }
