"""Build the failure-burden figure: naive premium versus task-matched null.

Panel A: per-scaffold failed/resolved burden ratios across tasks (the naive
view) with bootstrap intervals. Panel B: fraction of discordant pairs where
the failed side is heavier, raw and scaffold-normalized, against the 0.5
coin-flip null.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'paper' / 'figures'
DEEP = ROOT / 'outputs' / 'failure_burden'

CI_Z = 1.96


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    per_scaffold = pd.read_csv(DEEP / 'per_scaffold_failure_burden.csv')
    sign_raw = pd.read_csv(DEEP / 'discordant_sign_tests.csv')
    sign_norm = pd.read_csv(DEEP / 'discordant_normalized_sign_tests.csv')

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7), constrained_layout=True)

    # Panel A: naive cross-task ratios for two headline metrics.
    ax = axes[0]
    metrics = ['trajectory_turns', 'trajectory_characters']
    labels = ['Turns', 'Characters']
    width = 0.35
    x = np.arange(len(metrics))
    colors = {'openhands': '#0072B2', 'sweagent': '#D55E00'}
    for offset, (scaffold, label) in enumerate(
            [('openhands', 'OpenHands'), ('sweagent', 'SWE-agent')]):
        rows = per_scaffold[per_scaffold.scaffold == scaffold].set_index('metric').loc[metrics]
        med = rows.failed_over_resolved_ratio.to_numpy()
        lo = rows.ci_low.to_numpy()
        hi = rows.ci_high.to_numpy()
        err = np.vstack([med - lo, hi - med])
        ax.bar(x + (offset - 0.5) * width, med, width * 0.92,
               yerr=err, capsize=3, color=colors[scaffold], label=label)
    ax.axhline(1.0, color='black', lw=0.8)
    ax.set_xticks(x, labels)
    ax.set_ylabel('Failed / resolved burden ratio')
    ax.set_ylim(0.8, 1.6)
    ax.set_title('Across tasks: failures look 20-33% heavier', fontsize=9)

    # Panel B: discordant pairs collapse to the coin-flip null.
    ax = axes[1]
    n = int(sign_raw.discordant_pairs.iloc[0])
    frac_raw = sign_raw.fraction_failed_heavier.to_numpy()
    frac_norm = sign_norm.fraction.to_numpy()
    metric_order = ['trajectory_turns', 'assistant_turns', 'tool_calls',
                    'tool_result_turns', 'trajectory_characters', 'reasoning_characters']
    idx = [metric_order.index(m) for m in metric_order]
    frac_raw = frac_raw[idx]
    frac_norm = frac_norm[idx]
    xs = np.arange(len(metric_order))
    for frac, marker, name in [(frac_raw, 'o', 'Raw'), (frac_norm, 's', 'Scaffold-normalized')]:
        k = np.round(frac * n).astype(int)
        half = np.array([CI_Z * np.sqrt(p * (1 - p) / n) for p in frac])
        ax.errorbar(xs + (0 if marker == 'o' else 0.02), frac, yerr=half,
                    fmt=marker, ms=4, lw=0, elinewidth=1.1, capsize=2, label=name)
    ax.axhline(0.5, color='black', lw=0.8, ls='--')
    ax.text(0.02, 0.515, 'no premium (p=0.5)', fontsize=6.5, transform=ax.get_yaxis_transform())
    ax.set_xticks(xs, ['Turns', 'Asst', 'Tools', 'Tool res.', 'Chars', 'Reason'], fontsize=7)
    ax.set_ylabel('Fraction of 107 discordant pairs\nwhere failed side is heavier')
    ax.set_ylim(0.15, 0.85)
    ax.set_title('Same task: the premium vanishes', fontsize=9)
    ax.legend(fontsize=7, loc='upper right')

    fig.savefig(FIG / 'failure_burden_discordant.pdf', bbox_inches='tight')
    fig.savefig(FIG / 'failure_burden_discordant.png', dpi=300, bbox_inches='tight')
    print('wrote failure_burden_discordant.pdf/png')


if __name__ == '__main__':
    main()
