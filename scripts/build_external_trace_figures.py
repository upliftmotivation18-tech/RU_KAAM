"""Build compact figures/tables for the external matched trajectory-burden study."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "external_trace_study"
FIGURES = ROOT / "paper" / "figures"
TABLES = ROOT / "paper" / "tables"
FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

summary = pd.read_csv(SOURCE / "paired_scaffold_burden_summary.csv")
selected_names = {
    "trajectory_turns": "Trajectory turns",
    "assistant_turns": "Assistant turns",
    "tool_calls": "Tool calls",
    "trajectory_characters": "Trajectory characters",
}
selected = summary[summary["metric"].isin(selected_names)].copy()
selected["label"] = selected["metric"].map(selected_names)
selected = selected.set_index("metric").loc[list(selected_names)].reset_index()

fig, ax = plt.subplots(figsize=(6.7, 3.1), constrained_layout=True)
y = np.arange(len(selected))
ax.scatter(selected["sweagent_median"], y, color="#D55E00", marker="o", s=55, label="SWE-agent")
ax.scatter(selected["openhands_median"], y, color="#0072B2", marker="s", s=55, label="OpenHands")
for _, row in selected.iterrows():
    yy = selected.index.get_loc(row.name)
    ax.plot([row["sweagent_median"], row["openhands_median"]], [yy, yy], color="#9ca3af", lw=1.1, zorder=0)
    ax.text(row["sweagent_median"] * 1.04, yy + 0.12, f"{row['sweagent_median']:,.0f}", color="#D55E00", fontsize=6.5)
    ax.text(row["openhands_median"] * 1.04, yy - 0.23, f"{row['openhands_median']:,.0f}", color="#0072B2", fontsize=6.5)
ax.set_yticks(y, selected["label"])
ax.set_xscale("log")
ax.set_xlabel("Median burden proxy, log scale")
ax.set_title("Matched tasks: OpenHands has lower median trace proxies")
ax.grid(axis="x", which="major", color="#d1d5db", lw=0.7, alpha=0.8)
ax.legend(frameon=False, loc="lower right", fontsize=8)
fig.savefig(FIGURES / "matched_trace_burden.pdf", bbox_inches="tight")
fig.savefig(FIGURES / "matched_trace_burden.png", dpi=300, bbox_inches="tight")
plt.close(fig)

selected["Metric"] = selected["label"]
selected["SWE-agent median"] = selected["sweagent_median"].map(lambda x: f"{x:,.0f}")
selected["OpenHands median"] = selected["openhands_median"].map(lambda x: f"{x:,.0f}")
selected["Paired $p$"] = selected["wilcoxon_p"].map(lambda x: f"{x:.1e}")
TABLES.joinpath("matched_trace_burden.tex").write_text(
    selected[["Metric", "SWE-agent median", "OpenHands median", "Paired $p$"]].to_latex(
        index=False, escape=False, column_format="lrrr"
    )
)

success = pd.read_csv(SOURCE / "success_burden_by_scaffold.csv", header=[0, 1])
success.columns = [a if not b or b.startswith("Unnamed") else f"{a}_{b}" for a, b in success.columns]
success.to_csv(SOURCE / "success_burden_flat.csv", index=False)
