import numpy as np
import pandas as pd
import pytest

from src.portability import leave_one_benchmark_out_cost_prediction, cost_per_success


def test_cost_per_success_returns_missing_for_zero_accuracy_without_floor():
    costs = pd.Series([10.0, 20.0])
    accuracies = pd.Series([0.5, 0.0])

    result = cost_per_success(costs, accuracies, minimum_accuracy=None)

    assert result.iloc[0] == pytest.approx(20.0)
    assert np.isnan(result.iloc[1])


def test_cost_per_success_uses_prespecified_accuracy_floor_when_requested():
    costs = pd.Series([10.0, 20.0])
    accuracies = pd.Series([0.5, 0.0])

    result = cost_per_success(costs, accuracies, minimum_accuracy=0.05)

    assert result.tolist() == pytest.approx([20.0, 400.0])


def test_leave_one_benchmark_out_uses_only_other_benchmarks_for_label_propensity():
    data = pd.DataFrame(
        {
            "benchmark": ["a", "a", "b", "b", "c", "c"],
            "label": ["x", "y", "x", "y", "x", "y"],
            "cost": [10.0, 100.0, 20.0, 200.0, 30.0, 300.0],
        }
    )

    result = leave_one_benchmark_out_cost_prediction(
        data,
        benchmark_column="benchmark",
        label_column="label",
        cost_column="cost",
        min_training_benchmarks=2,
    )

    held_out_a = result[result["held_out_benchmark"].eq("a")]
    assert set(held_out_a["label"]) == {"x", "y"}
    # x/y propensities come from b and c only; the resulting predicted order is x cheaper than y.
    ordered = held_out_a.sort_values("predicted_log_cost")["label"].tolist()
    assert ordered == ["x", "y"]
