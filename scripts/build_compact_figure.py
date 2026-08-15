"""Build a compact, paper-scale benchmark-transfer heatmap."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper" / "figures" / "rank_transfer_compact.pdf"
PNG_OUTPUT = OUTPUT.with_suffix(".png")

BENCHMARKS = [
    "corebench_hard",
    "gaia",
    "scicode",
    "scienceagentbench",
    "swebench_verified_mini",
    "taubench_airline",
]
SHORT = {
    "corebench_hard": "CORE",
    "gaia": "GAIA",
    "scicode": "SciCode",
    "scienceagentbench": "SAB",
    "swebench_verified_mini": "SWE-mini",
    "taubench_airline": "TAU",
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
PNG_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

pairs = pd.read_csv(ROOT / "outputs" / "tables" / "generalist_pairwise_transfer.csv")


def make_matrix(column: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    matrix = pd.DataFrame(np.nan, index=BENCHMARKS, columns=BENCHMARKS)
    annotations = pd.DataFrame("", index=BENCHMARKS, columns=BENCHMARKS)
    for benchmark in BENCHMARKS:
        annotations.loc[benchmark, benchmark] = "—"
    for _, row in pairs.iterrows():
        first, second = row["benchmark_a"], row["benchmark_b"]
        if first not in BENCHMARKS or second not in BENCHMARKS:
            continue
        matrix.loc[first, second] = row[column]
        matrix.loc[second, first] = row[column]
        text = f"{row[column]:.2f}\n({int(row['n_shared'])})"
        annotations.loc[first, second] = text
        annotations.loc[second, first] = text
    for benchmark in BENCHMARKS:
        matrix.loc[benchmark, benchmark] = 0.0
        annotations.loc[benchmark, benchmark] = "—"
    matrix.index = [SHORT[item] for item in matrix.index]
    matrix.columns = [SHORT[item] for item in matrix.columns]
    annotations.index = matrix.index
    annotations.columns = matrix.columns
    return matrix, annotations

accuracy, accuracy_text = make_matrix("accuracy_spearman")
cost, cost_text = make_matrix("cost_spearman")

sns.set_theme(style="white", font_scale=0.85)
figure, axes = plt.subplots(1, 2, figsize=(7.0, 3.4), constrained_layout=True)
for index, (axis, matrix, annotation, title) in enumerate(
    [
        (axes[0], accuracy, accuracy_text, "Accuracy rank"),
        (axes[1], cost, cost_text, "Dollar-cost rank"),
    ]
):
    mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)
    # Keep the full symmetric matrix visible for reliable rendering at paper scale.
    mask = matrix.isna().to_numpy()
    sns.heatmap(
        matrix,
        mask=mask,
        annot=annotation,
        fmt="",
        square=True,
        vmin=-1,
        vmax=1,
        center=0,
        cmap="vlag",
        linewidths=0.5,
        linecolor="white",
        cbar=index == 1,
        cbar_kws={"label": "Spearman $\\rho$", "shrink": 0.82, "pad": 0.02},
        annot_kws={"fontsize": 7},
        ax=axis,
    )
    axis.set_title(title, fontsize=10, pad=5)
    axis.set_xlabel("")
    axis.set_ylabel("")
    axis.tick_params(axis="x", labelrotation=35, labelsize=7)
    axis.tick_params(axis="y", labelrotation=0, labelsize=7)

figure.savefig(OUTPUT, bbox_inches="tight")
figure.savefig(PNG_OUTPUT, dpi=300, bbox_inches="tight")
