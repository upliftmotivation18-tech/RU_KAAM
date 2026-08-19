"""Tokenizer-free trajectory-burden extraction for unencrypted trace records."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd


def trajectory_metrics(record: dict[str, Any]) -> dict[str, int]:
    """Extract transparent trajectory-burden proxies from one trace record.

    Character volume is intentionally not called tokens or cost. Tool calls are
    explicit calls in assistant messages; tool-result turns are messages with a
    tool role. The routine supports the Open-SWE structured message schema.
    """
    trajectory = record.get("trajectory")
    if trajectory is None:
        trajectory = []
    else:
        trajectory = list(trajectory)
    assistant_turns = 0
    tool_calls = 0
    tool_result_turns = 0
    trajectory_characters = 0
    reasoning_characters = 0
    for message in trajectory:
        role = message.get("role") or ""
        content = message.get("content") or message.get("text") or ""
        reasoning = message.get("reasoning_content") or ""
        trajectory_characters += len(content) + len(reasoning)
        reasoning_characters += len(reasoning)
        if role in {"assistant", "ai"}:
            assistant_turns += 1
            tool_calls += len(message.get("tool_calls") or [])
        if role == "tool":
            tool_result_turns += 1
    return {
        "trajectory_turns": len(trajectory),
        "assistant_turns": assistant_turns,
        "tool_calls": tool_calls,
        "tool_result_turns": tool_result_turns,
        "trajectory_characters": trajectory_characters,
        "reasoning_characters": reasoning_characters,
    }


def matched_pairs(data: pd.DataFrame, *, metric_columns: Iterable[str]) -> pd.DataFrame:
    """Exact task/model matched scaffold pairs, retaining one row per pairing.

    Inputs require columns ``instance_id``, ``model``, and ``scaffold``. Exact
    duplicate task/model/scaffold rows are excluded rather than arbitrarily
    selected, preserving a transparent matched design.
    """
    required = {"instance_id", "model", "scaffold", *metric_columns}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    subset = data[data["scaffold"].isin(["sweagent", "openhands"])].copy()
    duplicated = subset.duplicated(["instance_id", "model", "scaffold"], keep=False)
    subset = subset.loc[~duplicated]
    swe = subset[subset["scaffold"].eq("sweagent")].set_index(["instance_id", "model"])
    hands = subset[subset["scaffold"].eq("openhands")].set_index(["instance_id", "model"])
    common = swe.index.intersection(hands.index)
    rows: list[dict[str, Any]] = []
    for instance_id, model in common:
        result: dict[str, Any] = {"instance_id": instance_id, "model": model}
        for metric in metric_columns:
            result[f"{metric}_sweagent"] = swe.loc[(instance_id, model), metric]
            result[f"{metric}_openhands"] = hands.loc[(instance_id, model), metric]
        rows.append(result)
    return pd.DataFrame(rows)
