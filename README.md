# Does Cost-Efficiency Travel?

**A fixed-scaffold analysis of public HAL data finds that model-configuration accuracy ranks often transfer across workloads more consistently than dollar-cost ranks; frontier membership is correspondingly unstable.**

**A configuration that is comparatively inexpensive on one agent benchmark cannot safely be assumed to remain inexpensive—or cost-efficient—on another workload. Under standard weak Pareto membership, no broadly tested configuration appears on the frontier in more than 4 of 6 evaluated primary-cohort workloads.**

> Working paper title: *Does Cost-Efficiency Travel? Accuracy and Cost Rank Transfer in Fixed-Scaffold Agent Evaluation*

## Research question

When the agent scaffold is held fixed, how stable are model configurations' accuracy, dollar-cost, and accuracy--cost frontier positions across agent workloads?

The study deliberately avoids a causal decomposition of model, scaffold, and workload effects. The public HAL snapshot has sparse and unbalanced scaffold-by-benchmark coverage; most scaffolds appear on only one benchmark. The primary cohort therefore fixes the scaffold to **HAL Generalist Agent** and analyzes the six benchmarks with adequate pairwise model overlap:

- CORE-Bench Hard
- GAIA
- SciCode
- ScienceAgentBench
- SWE-bench Verified Mini
- TAU-bench Airline

## Reproduce

```bash
python3 -m pip install --user -r requirements.txt
python3 -m pytest -q
python3 scripts/run_analysis.py --bootstrap 5000
```

Outputs are written to `outputs/tables/` and `outputs/figures/`.

The analysis uses a frozen local copy of `all_leaderboards_costs_HAL.csv`. Its source snapshot has SHA-256:

```text
f8a07cbe6aae2801f592df3db7432a91c32a3de63dcf3ac4e0b5896bd34731f0
```

See `data/README.md` before redistributing source data: retain upstream attribution and verify licensing, or replace the local copy with a download-and-hash step.

## Method

For each pair of benchmarks sharing at least five model configurations, the pipeline reports:

- Spearman \(\rho\) and Kendall \(\tau_b\) for accuracy ranks;
- Spearman \(\rho\) and Kendall \(\tau_b\) for total-dollar-cost ranks;
- percentile-bootstrap intervals over shared configurations;
- Jaccard similarity of frontier sets.

Bootstrap intervals quantify sensitivity to the finite shared configuration set; because nearly all CSV rows represent one run, they are **not** rollout-level uncertainty intervals.

### Two frontier definitions

The repository computes and reports both definitions because they answer different deployment questions:

1. **Weak Pareto frontier:** no observed discrete configuration achieves at least the same accuracy at no greater cost, with one inequality strict.
2. **HAL-style convex-hull frontier:** adds the origin and retains the upper cost--accuracy convex envelope. This has a randomized-policy interpretation: a point can be excluded if a mixture of two configurations dominates it in expected cost and accuracy.

The `outputs/tables/pareto_label_reproducibility.csv` audit compares both reconstructions with the source CSV's `Is Pareto` labels.

## Repository layout

```text
src/analysis.py                  Core Pareto, correlation, and bootstrap routines
tests/                           Unit and source-data regression tests
scripts/run_analysis.py          End-to-end reproducible pipeline
data/                            Source-data provenance and frozen analysis input
outputs/tables/                  Generated analysis tables
outputs/figures/                 Generated publication figures
```

## Primary sources and acknowledgments

This research is a secondary analysis of public results. It relies on and should cite:

- Kapoor et al., **Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation**. https://arxiv.org/abs/2510.11977
- HAL leaderboard. https://hal.cs.princeton.edu/
- Ndzomga, **Efficient Benchmarking of AI Agents** and its public data repository. https://arxiv.org/abs/2603.23749 ; https://github.com/fsndzomga/efficient-benchmarking-ai-agents
- Kirgis et al., public HAL Pareto-analysis code used as a methodological reference for the HAL-style convex-hull implementation. https://github.com/peterkirgis/hal-paper-analysis

Related work includes *AI Agents That Matter*, SWE-Effi, and Benchmark². This repository's cross-workload analysis is distinct from within-benchmark task-subset ranking preservation.

## Limits

- The 242-row public snapshot is sparse across scaffold × benchmark combinations.
- 235 rows are single-run evaluations; only seven have two runs.
- Dollar cost combines token behavior with pricing assumptions and model release/configuration.
- The supplied CSV lacks total-token columns, so dollar-vs-token robustness requires raw HAL traces or databases.
- Findings describe this HAL snapshot and should not be generalized to all models, agent frameworks, or workloads.
