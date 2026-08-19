"""Analyze a documented matched Open-SWE trajectory-burden sample.

This is external evidence, not HAL data. It uses exact task/model matches across
SWE-agent and OpenHands and reports transparent burden proxies, never tokens or
dollar cost.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.trace_burden import matched_pairs, trajectory_metrics

DATA = ROOT / "data" / "external" / "open_swe_traces"
OUT = ROOT / "outputs" / "external_trace_study"
FILES = {
    "openhands": ["minimax_openhands_shard00.parquet", "minimax_openhands_shard19.parquet"],
    "sweagent": ["minimax_sweagent_shard00.parquet", "minimax_sweagent_shard22.parquet"],
}
METRICS = [
    "trajectory_turns",
    "assistant_turns",
    "tool_calls",
    "tool_result_turns",
    "trajectory_characters",
    "reasoning_characters",
    "resolved",
]


def load_rows() -> pd.DataFrame:
    outputs = []
    columns = ["instance_id", "trajectory", "resolved"]
    for scaffold, files in FILES.items():
        for filename in files:
            parquet = pq.ParquetFile(DATA / filename)
            for batch in parquet.iter_batches(batch_size=64, columns=columns):
                frame = batch.to_pandas()
                records = []
                for record in frame.to_dict("records"):
                    metrics = trajectory_metrics(record)
                    records.append(
                        {
                            "instance_id": record["instance_id"],
                            "model": "MiniMax-M2.5",
                            "scaffold": scaffold,
                            "source_shard": filename,
                            "resolved": int(record["resolved"]),
                            **metrics,
                        }
                    )
                outputs.append(pd.DataFrame(records))
    return pd.concat(outputs, ignore_index=True)


def paired_summary(pairs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        swe = pairs[f"{metric}_sweagent"].to_numpy(float)
        hands = pairs[f"{metric}_openhands"].to_numpy(float)
        difference = hands - swe
        test = wilcoxon(difference, zero_method="wilcox", alternative="two-sided", method="auto")
        rows.append(
            {
                "metric": metric,
                "n_pairs": int(len(pairs)),
                "sweagent_median": float(np.median(swe)),
                "openhands_median": float(np.median(hands)),
                "median_openhands_minus_sweagent": float(np.median(difference)),
                "mean_openhands_minus_sweagent": float(np.mean(difference)),
                "openhands_greater_fraction": float(np.mean(difference > 0)),
                "wilcoxon_p": float(test.pvalue),
            }
        )
    return pd.DataFrame(rows)


def success_burden(rows: pd.DataFrame) -> pd.DataFrame:
    known = rows[rows["resolved"].isin([0, 1])].copy()
    return (
        known.groupby(["scaffold", "resolved"])[
            ["trajectory_turns", "assistant_turns", "tool_calls", "tool_result_turns", "trajectory_characters", "reasoning_characters"]
        ]
        .agg(["count", "median", "mean"])
        .reset_index()
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    rows.to_csv(OUT / "trajectory_burden_rows.csv", index=False)
    pairs = matched_pairs(rows, metric_columns=METRICS)
    pairs.to_csv(OUT / "exact_matched_scaffold_pairs.csv", index=False)
    summary = paired_summary(pairs)
    summary.to_csv(OUT / "paired_scaffold_burden_summary.csv", index=False)
    success_burden(rows).to_csv(OUT / "success_burden_by_scaffold.csv", index=False)
    meta = {
        "source": "nvidia/Open-SWE-Traces",
        "source_commit": "ad4805a5aa7de70d99cab0bb8f99b15304c76de0",
        "sample": "First and last public MiniMax-M2.5 shards for each scaffold; four-shard boundary sample, not random/full-corpus inference.",
        "matched_design": "Exact instance_id and same model across SWE-agent and OpenHands; duplicates excluded.",
        "allowed_interpretation": "Trajectory burden and success differences in this external matched sample.",
        "prohibited_interpretation": "Tokens, dollar cost, true failure cost ratio, retries, list price, or direct validation of HAL dollar findings.",
    }
    (OUT / "README.json").write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()
