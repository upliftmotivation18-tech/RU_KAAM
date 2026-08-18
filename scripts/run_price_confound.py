"""Run the observed model-label cost-propensity confound analysis.

This analysis is intentionally not called a list-price adjustment: the frozen
public CSV lacks historical provider alias, input/output/cache token counts, and
an immutable price-card field required for source-grounded repricing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_analysis import GENERALIST, PRIMARY_BENCHMARKS, add_frontiers, load_data, verify_frozen_input
from src.price_confound import fit_cost_propensity_model, residual_pair_statistics

INPUT = ROOT / "data" / "all_leaderboards_costs_HAL.csv"
OUT = ROOT / "outputs" / "price_confound"
SEED = 20260818


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    verify_frozen_input(INPUT)
    data = add_frontiers(load_data(INPUT))
    cohort = data[
        data["scaffold"].eq(GENERALIST) & data["benchmark"].isin(PRIMARY_BENCHMARKS)
    ].copy()
    fit = fit_cost_propensity_model(
        cohort,
        label_column="model_configuration",
        benchmark_column="benchmark",
        cost_column="total_cost",
    )
    cohort["observed_log_cost_fitted"] = fit.fitted
    cohort["residual_log_cost"] = fit.residuals
    cohort.to_csv(OUT / "generalist_cost_propensity_residuals.csv", index=False)

    rows = []
    for position, first in enumerate(PRIMARY_BENCHMARKS):
        for second in PRIMARY_BENCHMARKS[position + 1 :]:
            result = residual_pair_statistics(
                cohort,
                benchmark_a=first,
                benchmark_b=second,
                label_column="model_configuration",
                benchmark_column="benchmark",
                residual_column="residual_log_cost",
                n_permutations=20_000,
                seed=SEED + position * 100 + len(rows),
            )
            rows.append(
                {
                    "benchmark_a": first,
                    "benchmark_b": second,
                    "benchmark_a_label": first,
                    "benchmark_b_label": second,
                    **result,
                }
            )
    pd.DataFrame(rows).to_csv(OUT / "residual_cost_rank_pairs.csv", index=False)
    (OUT / "model_summary.json").write_text(json.dumps(fit.summary, indent=2) + "\n")
    (OUT / "README.md").write_text(
        "# Observed model-label cost-propensity adjustment\n\n"
        "This table residualizes log total dollar cost using displayed-model-label and benchmark fixed effects. "
        "It tests sensitivity of raw cost-rank transfer to stable observed label-level cost propensity. "
        "It is not a list-price adjustment and is not a causal execution-dynamics estimate because the frozen CSV lacks provider alias, token components, and historical price-card data.\n"
    )


if __name__ == "__main__":
    main()
