"""Create V2 robustness tables for the trace and LOBO studies."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "paper" / "appendix"
TABLES.mkdir(parents=True, exist_ok=True)

trace = pd.read_csv(ROOT / "outputs" / "external_trace_study" / "paired_scaffold_burden_summary.csv")
keep = trace[trace.metric.isin(["trajectory_turns", "tool_calls", "trajectory_characters"])].copy()
names = {"trajectory_turns": "Trajectory turns", "tool_calls": "Tool calls", "trajectory_characters": "Trajectory characters"}
keep["Metric"] = keep.metric.map(names)
keep["OpenHands/SWE-agent"] = keep.median_ratio_openhands_over_sweagent.map(lambda x: f"{x:.2f}")
keep["95\\% bootstrap interval"] = keep.apply(lambda r: f"[{r.median_ratio_ci_low:.2f}, {r.median_ratio_ci_high:.2f}]", axis=1)
keep["OpenHands lower"] = keep.openhands_lower_fraction.map(lambda x: f"{100*x:.1f}\\%")
keep["Paired $p$"] = keep.wilcoxon_p.map(lambda x: f"{x:.1e}")
(TABLES / "v2_trace_effects.tex").write_text(
    keep[["Metric", "OpenHands/SWE-agent", "95\\% bootstrap interval", "OpenHands lower", "Paired $p$"]].to_latex(
        index=False, escape=False, column_format="lrrrr"
    )
)

lolo = pd.read_csv(ROOT / "outputs" / "v2_robustness" / "lobo_leave_one_label_out_summary.csv")
labels = {"corebench_hard": "CORE", "gaia": "GAIA", "scicode": "SciCode", "scienceagentbench": "SAB", "swebench_verified_mini": "SWE-mini", "taubench_airline": "TAU"}
lolo["Held-out"] = lolo.held_out_benchmark.map(labels)
lolo["LOLO range"] = lolo.apply(lambda r: f"[{r['min']:.2f}, {r['max']:.2f}]", axis=1)
lolo["Omissions"] = lolo["count"].astype(int)
(TABLES / "v2_lobo_influence.tex").write_text(
    lolo[["Held-out", "LOLO range", "Omissions"]].to_latex(index=False, escape=False, column_format="lrr")
)
