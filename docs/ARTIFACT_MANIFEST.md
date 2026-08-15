# Research artifact manifest

## Study identifier

**Working title:** *Does Cost-Efficiency Travel? Accuracy and Cost Rank Transfer in Fixed-Scaffold Agent Evaluation*

## Frozen input

| Item | Value |
|---|---|
| Local source file | `data/all_leaderboards_costs_HAL.csv` |
| SHA-256 | `f8a07cbe6aae2801f592df3db7432a91c32a3de63dcf3ac4e0b5896bd34731f0` |
| Public upstream repository | https://github.com/fsndzomga/efficient-benchmarking-ai-agents |
| Upstream file | `data/all_leaderboards_costs_HAL.csv` |
| Upstream repository snapshot examined | `cd734cced26cdb9bbf59e704088daaaaca126b6e` |
| HAL Pareto reference snapshot examined | `92ff146a83e054b4171731d1b72c2b9067534b48` |

## Analysis decisions frozen before manuscript drafting

- Primary scaffold: `HAL Generalist Agent`.
- Primary benchmark set: CORE-Bench Hard, GAIA, SciCode, ScienceAgentBench, SWE-bench Verified Mini, TAU-bench Airline.
- Excluded from primary transfer analysis: USACO, because it contains one HAL Generalist evaluation.
- Minimum shared model configurations for a benchmark pair: 5.
- Model unit: exact public `Models` display string paired within the exact public `Agent Name` display string. The displayed labels do not fully specify all benchmark-specific prompt, tool, budget, or harness details; they are not treated as controlled base-model identities.
- Rank metrics: Spearman rho and Kendall tau-b.
- Uncertainty: 5,000-resample percentile configuration-resampling sensitivity intervals over shared displayed labels, fixed seed `20260816`; not rollout-level or population-model confidence intervals.
- Frontier definitions: nondominated Pareto for discrete selection; HAL-inspired origin-anchored convex-hull reconstruction for randomized-policy interpretation.

## Interpretation constraints

- Bootstrap intervals reflect sensitivity to the finite shared model-configuration set, not rollout-level variance.
- The study does not estimate causal model/scaffold/workload variance components.
- The public displayed labels do not fully encode benchmark-specific prompts, tools, budgets, or harness details; repeated labels are not controlled base-model identities.
- Dollar cost should not be interpreted as token efficiency because the input CSV does not contain total-token usage.
- Domain comparisons are exploratory because only three same-domain pairs are available in the primary cohort.
