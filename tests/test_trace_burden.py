import pandas as pd

from src.trace_burden import trajectory_metrics, matched_pairs


def test_trajectory_metrics_counts_tools_and_text_without_calling_text_tokens_tokens():
    row = {
        "trajectory_id": "x",
        "instance_id": "task",
        "resolved": 1,
        "trajectory": [
            {"role": "system", "content": "setup", "reasoning_content": None, "tool_calls": None},
            {"role": "assistant", "content": "answer", "reasoning_content": "think", "tool_calls": [{"id": "1"}]},
            {"role": "tool", "content": "result", "reasoning_content": None, "tool_calls": None},
        ],
    }
    result = trajectory_metrics(row)
    assert result["assistant_turns"] == 1
    assert result["tool_calls"] == 1
    assert result["tool_result_turns"] == 1
    assert result["trajectory_characters"] == len("setupanswerthinkresult")


def test_matched_pairs_uses_exact_task_and_model_scaffold_records():
    data = pd.DataFrame(
        {
            "instance_id": ["a", "a", "b", "b"],
            "model": ["m", "m", "m", "m"],
            "scaffold": ["sweagent", "openhands", "sweagent", "openhands"],
            "tool_calls": [1, 2, 3, 4],
        }
    )
    result = matched_pairs(data, metric_columns=["tool_calls"])
    assert len(result) == 2
    assert set(result["instance_id"]) == {"a", "b"}
    assert result.loc[result.instance_id.eq("a"), "tool_calls_openhands"].iloc[0] == 2
