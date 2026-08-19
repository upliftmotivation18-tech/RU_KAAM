"""Create supplemental tables for CPS inference."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "outputs" / "aggregate_efficiency" / "cost_per_success_inference_1pct.csv"
out = ROOT / "paper" / "appendix" / "cps_inference.tex"
out.parent.mkdir(parents=True, exist_ok=True)
labels = {
    "corebench_hard": "CORE",
    "gaia": "GAIA",
    "scicode": "SciCode",
    "scienceagentbench": "SAB",
    "swebench_verified_mini": "SWE-mini",
    "taubench_airline": "TAU",
}
frame = pd.read_csv(source)
frame["Pair"] = frame["benchmark_a"].map(labels) + "--" + frame["benchmark_b"].map(labels)
frame["N"] = frame["n_shared"].astype(int)
frame["CPS $\\rho$"] = frame["point_rho"].map(lambda v: f"{v:.2f}")
frame["95\\% sensitivity interval"] = frame.apply(lambda r: f"[{r.ci_low:.2f}, {r.ci_high:.2f}]", axis=1)
frame["Perm. $p$"] = frame["permutation_p_two_sided"].map(lambda v: f"{v:.4f}")
frame["Holm $p$"] = frame["holm_adjusted_p"].map(lambda v: f"{v:.4f}")
out.write_text(
    frame[["Pair", "N", "CPS $\\rho$", "95\\% sensitivity interval", "Perm. $p$", "Holm $p$"]].to_latex(
        index=False, escape=False, column_format="lrlrrr"
    )
)
