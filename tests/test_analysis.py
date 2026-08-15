import pandas as pd
import pytest

from src.analysis import (
    bootstrap_rank_correlation,
    convex_hull_frontier,
    pairwise_rank_statistics,
    weak_pareto_frontier,
)


def test_weak_pareto_keeps_non_dominated_point_below_convex_hull():
    frame = pd.DataFrame(
        {
            "cost": [1.0, 2.0, 3.0, 4.0],
            "accuracy": [1.0, 1.2, 1.5, 3.0],
        },
        index=["a", "b", "c", "d"],
    )

    frontier = weak_pareto_frontier(frame, cost_column="cost", accuracy_column="accuracy")

    assert frontier.to_dict() == {"a": True, "b": True, "c": True, "d": True}


def test_convex_hull_excludes_non_dominated_point_when_mixture_dominates_it():
    frame = pd.DataFrame(
        {
            "cost": [1.0, 2.0, 3.0, 4.0],
            "accuracy": [1.0, 1.2, 1.5, 3.0],
        },
        index=["a", "b", "c", "d"],
    )

    frontier = convex_hull_frontier(frame, cost_column="cost", accuracy_column="accuracy")

    assert frontier.to_dict() == {"a": True, "b": False, "c": False, "d": True}


def test_pairwise_statistics_only_uses_shared_configurations_and_reports_jaccard():
    first = pd.DataFrame(
        {
            "configuration": ["a", "b", "c", "first_only"],
            "accuracy": [1.0, 2.0, 3.0, 99.0],
            "cost": [3.0, 2.0, 1.0, 0.01],
            "frontier": [True, False, True, True],
        }
    )
    second = pd.DataFrame(
        {
            "configuration": ["a", "b", "c", "second_only"],
            "accuracy": [3.0, 2.0, 1.0, 99.0],
            "cost": [1.0, 2.0, 3.0, 0.01],
            "frontier": [True, True, False, True],
        }
    )

    result = pairwise_rank_statistics(
        first,
        second,
        configuration_column="configuration",
        accuracy_column="accuracy",
        cost_column="cost",
        frontier_column="frontier",
    )

    assert result["n_shared"] == 3
    assert result["accuracy_spearman"] == pytest.approx(-1.0)
    assert result["cost_spearman"] == pytest.approx(-1.0)
    assert result["frontier_jaccard"] == pytest.approx(1 / 3)


def test_bootstrap_rank_correlation_is_reproducible_with_seed():
    first = [1, 2, 3, 4, 5, 6]
    second = [2, 1, 4, 3, 6, 5]

    first_result = bootstrap_rank_correlation(first, second, method="spearman", n_bootstrap=200, seed=7)
    second_result = bootstrap_rank_correlation(first, second, method="spearman", n_bootstrap=200, seed=7)

    assert first_result == second_result
    assert first_result["n"] == 6
    assert first_result["estimate"] == pytest.approx(0.8285714285714287)
    assert first_result["ci_low"] <= first_result["estimate"] <= first_result["ci_high"]


def test_bootstrap_rank_correlation_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        bootstrap_rank_correlation([1, 2], [1], method="spearman")
