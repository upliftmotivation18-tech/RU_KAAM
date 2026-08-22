# V2 evidence-hardening plan

## Goal

V2 should answer a narrower, harder-to-attack question:

> What can public leaderboard aggregates and public trajectories establish about the portability of observable agent-system efficiency signals, without treating hidden provider telemetry as observed?

## Claim hierarchy

### Claim A: supported now, retain

Raw observed dollar-cost ranks are predictable in some high-overlap HAL workloads and in LOBO for CORE, GAIA, SWE-mini, and TAU.

Evidence: overlap counts, rank correlations, resampling intervals, raw-cost Holm tests, and LOBO permutation tests.

### Claim B: supported now, retain with explicit scope

Observed label plus benchmark cost propensity absorbs high-overlap raw cost structure. This is descriptive, not a list-price or causal execution adjustment.

Evidence: 86-row / 30-parameter / 56-residual-df model, residual rank permutation tests, LOBO out-of-sample evidence.

### Claim C: supported now, narrow

Aggregate CostPerSuccess can be less portable than raw cost, but this is not universal. The robust formal contrast is GAIA--SWE-mini; the 0.84 vs 0.59 high-overlap mean is descriptive.

Evidence: 10,000 configuration-resampling intervals, 20,000 CPS permutations, CPS Holm correction, paired raw-minus-CPS resampling.

### Claim D: supported now, separate external mechanism evidence

At fixed task and model in a reproducible Open-SWE boundary sample, scaffold choice changes observable trajectory-burden proxies.

Evidence: 977 exact task-model pairs, paired medians, paired effect sizes/intervals, success difference testing.

### Claims blocked until new telemetry arrives

- dollar FailureCostRatio;
- token costs / cache usage / provider prices;
- retry counts and true tail cost;
- causal decomposition of model versus scaffold versus workload in HAL;
- explanation of LOBO benchmark failure by scientific-domain identity.

## V2 additions

1. Report paired effect size, bootstrap interval, and paired success effect for every trace burden metric.
2. Add leave-one-label-out influence diagnostics for each LOBO held-out result.
3. Add benchmark observable-characteristic diagnostics only as descriptive/exploratory because there are six benchmarks.
4. State why LOBO heterogeneity cannot be attributed to domain from six outcomes.
5. Add an external-data feasibility table with inclusion criteria, access state, fields, matching validity, and excluded datasets.
6. Require an additional snapshot only if it has exact model, task, scaffold, success, and usage fields sufficient for a matched design.

## V2 decision gates

- Integrate an external dataset into results only if the schema has success labels and an exact matching key across a treatment comparison.
- Call a quantity cost only with documented billing/token fields; otherwise call it a trace-burden proxy.
- Promote a small-cohort pattern to a headline claim only if it survives leave-one-label-out diagnostics and its interval excludes the qualitative null relevant to the claim.
- Do not use cross-benchmark "domain" explanations unless more than six benchmark-level units support them.
