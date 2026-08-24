# Reviewer weakness response and remediation matrix

This document maps anticipated critiques to implemented fixes, resulting claim scope, and remaining data requirements.

| Weakness | What was changed | Claim after remediation | What remains unavailable |
|---|---|---|---|
| Small HAL cohort / thin LOBO N | Every pair reports N; 10,000 shared-label resampling intervals; 20,000 permutation tests; leave-one-label-out influence checks | Positive LOBO results for CORE, GAIA, SWE-mini, TAU are finite-cohort robust to omitting any one label, not population estimates | Larger balanced model × benchmark panel; rollout replication |
| In-sample fixed-effect R² | Reported 86 rows, 30 parameters, 56 residual df; called R² descriptive; LOBO is primary evidence | Stable observed label cost propensity is a diagnostic, not a causal mechanism or headline estimator | Provider pricing, tokens, routing, cache fields |
| Wide GAIA--SWE CPS contrast | Reports 0.60 [0.14, 1.13] as directionally supported but imprecise; labels 0.84 vs 0.59 mean descriptive | One concrete raw-vs-CPS divergence, not a universal gap estimate | More repeated labels / per-task success-cost data |
| One-model external trace study | Reports exact task/model matching, four-shard boundary sample, effect ratios and bootstrap intervals; excludes token/dollar claims | In this sample, scaffold changes trace burden at fixed task/model | Multiple matched model panels, random/full-corpus sampling, billing telemetry |
| Related work omission | Submission now cites HAL, AI Agents That Matter, Efficient Benchmarking, SWE-Effi, Benchmark², Open-SWE-Traces and gives explicit distinctions | This work studies held-out raw cost and CPS portability under a fixed agent scaffold, not static benchmark consistency or task-subset selection | None; this is framing work |
| Nonstandard resampling label | Defines resampling directly: resample shared displayed labels with replacement, recompute rank statistic; intervals are finite-label sensitivity, not CIs | Transparent finite-set sensitivity analysis | Rollout uncertainty needs repeated evaluation |
| Broader impacts checklist | Changed from N/A to Yes and added balanced benefits/risks | Better cost reporting can reduce waste; poor leaderboard interpretation may distort selection | No social-group or human-subject outcomes studied |
| Methodological novelty concern | States contribution as a coverage-aware held-out measurement framework plus matched trace evidence, not a new estimator | A careful empirical methodology / evaluation paper, appropriate for workshop or benchmark-evaluation venues | A novel algorithm would be a separate contribution |

## Claim discipline used in V2

We use **predicts within this observed held-out cohort**, not generalizes universally. We use **trace-burden proxy**, not cost or tokens. We use **observed displayed-label propensity**, not list price or intrinsic model efficiency. We use **descriptive diagnostic**, not causal benchmark explanation.

## Data required for the next evidence tier

A stronger future study needs an openly accessible, matched evaluation export with task ID, exact provider/model/scaffold version, success/failure, input/output/cache tokens, per-call cost, tool calls, retries, wall-clock time, and repeated rollouts. Without these fields, dollar FailureCostRatio, tail-dollar-risk, and causal cost decomposition remain unsupported.
