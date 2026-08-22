import numpy as np
import pytest

from src.v2_robustness import paired_effect_summary


def test_paired_effect_summary_reports_expected_ratio_and_interval():
    swe = np.array([10, 20, 30, 40], dtype=float)
    hands = np.array([5, 10, 15, 20], dtype=float)
    result = paired_effect_summary(swe, hands, n_resamples=100, seed=1)
    assert result["median_difference"] == pytest.approx(-12.5)
    assert result["median_ratio_openhands_over_sweagent"] == pytest.approx(0.5)
    assert result["openhands_lower_fraction"] == 1.0
    assert result["median_ratio_ci_low"] <= 0.5 <= result["median_ratio_ci_high"]
