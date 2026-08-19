import numpy as np
import pandas as pd
import pytest

from src.cps_inference import bootstrap_rank_pair, paired_raw_cps_contrast, holm_adjust


def test_bootstrap_rank_pair_returns_interval_and_valid_counts():
    first = np.array([1, 2, 3, 4, 5], dtype=float)
    second = np.array([1, 2, 3, 4, 5], dtype=float)
    result = bootstrap_rank_pair(first, second, n_resamples=100, seed=1)
    assert result["point_rho"] == pytest.approx(1.0)
    assert result["valid_resamples"] > 0
    assert result["ci_low"] <= result["point_rho"] <= result["ci_high"]


def test_paired_raw_cps_contrast_uses_shared_configuration_resampling():
    raw_a = np.array([1, 2, 3, 4, 5], dtype=float)
    raw_b = np.array([1, 2, 3, 4, 5], dtype=float)
    cps_a = np.array([1, 2, 3, 4, 5], dtype=float)
    cps_b = np.array([5, 4, 3, 2, 1], dtype=float)
    result = paired_raw_cps_contrast(raw_a, raw_b, cps_a, cps_b, n_resamples=100, seed=2)
    assert result["point_difference"] == pytest.approx(2.0)
    assert result["ci_low"] <= 2.0 <= result["ci_high"]


def test_holm_adjust_monotone():
    values = holm_adjust(np.array([0.01, 0.02, 0.5]))
    assert np.all(values >= np.array([0.01, 0.02, 0.5]))
    assert np.all(values <= 1)
