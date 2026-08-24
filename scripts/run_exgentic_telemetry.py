"""Analyze public Exgentic OTel telemetry without inferring task outcomes or dollars.

Input is an explicitly documented convenience sample of public Exgentic shards.
The analysis compares harness distributions within fixed benchmark-model cells;
it is not task matched, causal, or a cost/success analysis.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
SHARDS = Path("/data/workspace/telemetry_audit/exgentic_shards")
OUT = ROOT / "outputs" / "exgentic_telemetry"
DUCKDB = Path("/tmp/duckdb-bin/duckdb")


def run_sql(sql: str) -> pd.DataFrame:
    completed = subprocess.run(
        [str(DUCKDB), "-csv", "-c", sql], check=True, capture_output=True, text=True
    )
    from io import StringIO
    return pd.read_csv(StringIO(completed.stdout))


def bootstrap_median_ratio(first: np.ndarray, second: np.ndarray, *, seed: int, draws: int = 10_000) -> dict[str, float]:
    """Ratio of independent sample medians with percentile bootstrap interval."""
    generator = np.random.default_rng(seed)
    first_median = float(np.median(first))
    second_median = float(np.median(second))
    point = second_median / first_median if first_median > 0 else float("nan")
    ratios = []
    for _ in range(draws):
        a = generator.choice(first, size=len(first), replace=True)
        b = generator.choice(second, size=len(second), replace=True)
        if np.median(a) > 0:
            ratios.append(np.median(b) / np.median(a))
    med_diffs = []
    for _ in range(draws):
        idx_a = generator.integers(0, len(first), size=len(first))
        idx_b = generator.integers(0, len(second), size=len(second))
        med_diffs.append(float(np.median(second[idx_b]) - np.median(first[idx_a])))
    return {
        "median_ratio_second_over_first": float(point),
        "ratio_ci_low": float(np.quantile(ratios, 0.025)) if ratios else float("nan"),
        "ratio_ci_high": float(np.quantile(ratios, 0.975)) if ratios else float("nan"),
        "median_difference_second_minus_first": float(second_median - first_median),
        "difference_ci_low": float(np.quantile(med_diffs, 0.025)),
        "difference_ci_high": float(np.quantile(med_diffs, 0.975)),
    }


def main() -> None:
    if not DUCKDB.exists():
        raise FileNotFoundError(f"DuckDB CLI missing at {DUCKDB}")
    if not SHARDS.exists():
        raise FileNotFoundError(f"Expected local Exgentic shards at {SHARDS}")
    OUT.mkdir(parents=True, exist_ok=True)
    glob = str(SHARDS / "*.parquet")
    sql = f'''
    WITH sessions AS (
      SELECT benchmark, harness, models[1] AS model, session_id, total_tokens,
             array_length(spans) AS span_count,
             spans
      FROM read_parquet('{glob}')
    ), calls AS (
      SELECT benchmark, harness, model, session_id, total_tokens, span_count,
             SUM(CASE WHEN s.attributes."gen_ai.usage.input_tokens" IS NOT NULL THEN 1 ELSE 0 END) AS llm_calls,
             SUM(CASE WHEN s.status.code != 1 THEN 1 ELSE 0 END) AS failed_llm_calls,
             SUM(COALESCE(s.attributes."gen_ai.usage.input_tokens",0)) AS input_tokens_spans,
             SUM(COALESCE(s.attributes."gen_ai.usage.output_tokens",0)) AS output_tokens_spans
      FROM sessions, UNNEST(spans) AS u(s)
      GROUP BY 1,2,3,4,5,6
    )
    SELECT * FROM calls
    '''
    sessions = run_sql(sql)
    sessions.to_csv(OUT / "session_telemetry.csv", index=False)
    coverage = sessions.groupby(["benchmark", "model", "harness"]).size().rename("n_sessions").reset_index()
    coverage.to_csv(OUT / "coverage.csv", index=False)

    metrics = ["total_tokens", "llm_calls", "failed_llm_calls", "input_tokens_spans", "output_tokens_spans"]
    comparisons = []
    for (benchmark, model), group in sessions.groupby(["benchmark", "model"]):
        harness_counts = group.harness.value_counts()
        eligible = harness_counts[harness_counts >= 10].index.tolist()
        for i, first_harness in enumerate(eligible):
            for second_harness in eligible[i + 1 :]:
                first = group[group.harness.eq(first_harness)]
                second = group[group.harness.eq(second_harness)]
                for metric_index, metric in enumerate(metrics):
                    values_a = first[metric].to_numpy(float)
                    values_b = second[metric].to_numpy(float)
                    effect = bootstrap_median_ratio(
                        values_a, values_b,
                        seed=20260818 + len(comparisons) * 10 + metric_index,
                    )
                    test = mannwhitneyu(values_a, values_b, alternative="two-sided", method="auto")
                    comparisons.append(
                        {
                            "benchmark": benchmark,
                            "model": model,
                            "first_harness": first_harness,
                            "second_harness": second_harness,
                            "metric": metric,
                            "n_first": len(values_a),
                            "n_second": len(values_b),
                            "first_median": float(np.median(values_a)),
                            "second_median": float(np.median(values_b)),
                            **effect,
                            "mann_whitney_p": float(test.pvalue),
                        }
                    )
    comparison_frame = pd.DataFrame(comparisons)
    comparison_frame.to_csv(OUT / "multi_harness_comparisons.csv", index=False)
    meta = {
        "source": "Exgentic/agent-llm-traces",
        "source_commit": "70036b93a04e61b0ea2706a68b962f4f26774587",
        "shard_selection": "11 downloaded shards spread across 39 public shards; convenience sample, not full corpus or random sampling.",
        "unit": "session; no exact task ID or outcome field was observed.",
        "inference": "Independent harness distribution comparisons within fixed benchmark-model cells. Results are descriptive, not matched causal scaffold estimates.",
        "not_available": ["benchmark reward", "per-task success", "dollar billing", "task matching across harnesses", "latency"],
    }
    (OUT / "README.json").write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()
