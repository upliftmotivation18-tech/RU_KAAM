import numpy as np
import pandas as pd
import pytest

from src.price_confound import fit_cost_propensity_model, residual_pair_statistics


def test_cost_propensity_model_recovers_additive_label_and_benchmark_structure():
    rows = []
    label_effect = {"a": 0.0, "b": 1.0, "c": 2.0}
    benchmark_effect = {"x": 0.0, "y": 3.0, "z": -1.0}
    for label, label_value in label_effect.items():
        for benchmark, benchmark_value in benchmark_effect.items():
            rows.append(
                {
                    "model_configuration": label,
                    "benchmark": benchmark,
                    "total_cost": np.exp(label_value + benchmark_value),
                }
            )
    data = pd.DataFrame(rows)

    result = fit_cost_propensity_model(
        data,
        label_column="model_configuration",
        benchmark_column="benchmark",
        cost_column="total_cost",
    )

    assert result.summary["r_squared"] == pytest.approx(1.0)
    assert np.max(np.abs(result.residuals)) < 1e-10


def test_residual_pair_statistics_matches_only_shared_labels():
    data = pd.DataFrame(
        {
            "model_configuration": ["a", "b", "c", "a", "b", "c"],
            "benchmark": ["x", "x", "x", "y", "y", "y"],
            "residual_cost": [1.0, 2.0, 3.0, 3.0, 2.0, 1.0],
        }
    )

    result = residual_pair_statistics(
        data,
        benchmark_a="x",
        benchmark_b="y",
        label_column="model_configuration",
        benchmark_column="benchmark",
        residual_column="residual_cost",
        n_permutations=200,
        seed=5,
    )

    assert result["n_shared"] == 3
    assert result["residual_spearman"] == pytest.approx(-1.0)
    assert 0 <= result["permutation_p_two_sided"] <= 1
