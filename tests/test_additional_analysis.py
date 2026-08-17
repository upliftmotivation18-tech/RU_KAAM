import numpy as np
import pandas as pd
import pytest

from src.additional_analysis import (
    holm_bonferroni,
    null_label_shuffle,
    tolerant_nondominated_frontier,
)


def test_holm_bonferroni_rejects_only_smallest_p_values():
    result = holm_bonferroni([0.001, 0.02, 0.04, 0.8], alpha=0.05)

    assert result["reject"].tolist() == [True, False, False, False]
    assert result["adjusted_p"].tolist() == pytest.approx([0.004, 0.06, 0.08, 0.8])


def test_tolerant_frontier_requires_material_accuracy_and_cost_improvement():
    frame = pd.DataFrame(
        {"cost": [100.0, 96.0, 94.0], "accuracy": [50.0, 51.0, 52.0]},
        index=["baseline", "near_tie", "better"],
    )

    frontier = tolerant_nondominated_frontier(
        frame,
        cost_column="cost",
        accuracy_column="accuracy",
        relative_tolerance=0.05,
    )

    assert frontier.to_dict() == {"baseline": True, "near_tie": True, "better": True}


def test_null_label_shuffle_preserves_observed_sample_size_and_returns_tail_probability():
    first = [1, 2, 3, 4, 5]
    second = [5, 4, 3, 2, 1]

    result = null_label_shuffle(first, second, n_simulations=200, seed=3)

    assert result["n"] == 5
    assert result["observed_rho"] == pytest.approx(-1.0)
    assert 0 <= result["two_sided_empirical_p"] <= 1
    assert result["null_q025"] <= result["null_q975"]
