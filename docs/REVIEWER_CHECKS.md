# Reviewer-oriented robustness checks

This memo reports post hoc robustness checks requested during paper finalization. They are descriptive analyses of the frozen public HAL snapshot; they do not convert the study into a controlled causal experiment.

## 1. Configuration-resampling intervals: all 15 eligible benchmark pairs

We resampled shared displayed model labels with replacement 10,000 times per pair and recomputed Spearman rho separately for accuracy and dollar cost. These are **configuration-resampling sensitivity intervals**, not rollout-level or population-model confidence intervals.

### Accuracy rank

| Pair | N | rho | 95% configuration-resampling interval |
|---|---:|---:|---:|
| CORE--GAIA | 14 | 0.60 | [0.16, 0.81] |
| CORE--SciCode | 9 | 0.60 | [-0.24, 0.92] |
| CORE--SAB | 7 | 0.56 | [-0.41, 1.00] |
| CORE--SWE-mini | 14 | 0.48 | [-0.04, 0.82] |
| CORE--TAU | 12 | 0.50 | [-0.11, 0.85] |
| GAIA--SciCode | 9 | 0.58 | [-0.19, 0.98] |
| GAIA--SAB | 7 | 0.64 | [-0.18, 1.00] |
| GAIA--SWE-mini | 17 | 0.71 | [0.32, 0.91] |
| GAIA--TAU | 14 | 0.58 | [0.16, 0.85] |
| SciCode--SAB | 7 | 0.51 | [-0.64, 1.00] |
| SciCode--SWE-mini | 9 | 0.15 | [-0.66, 0.78] |
| SciCode--TAU | 9 | 0.60 | [0.00, 0.92] |
| SAB--SWE-mini | 7 | 0.02 | [-0.97, 0.65] |
| SAB--TAU | 7 | 0.36 | [-0.76, 0.96] |
| SWE-mini--TAU | 14 | 0.76 | [0.41, 0.91] |

### Dollar-cost rank

| Pair | N | rho | 95% configuration-resampling interval | Crosses 0? |
|---|---:|---:|---:|---|
| CORE--GAIA | 14 | 0.93 | [0.72, 0.99] | No |
| CORE--SciCode | 9 | -0.28 | [-0.86, 0.51] | Yes |
| CORE--SAB | 7 | -0.64 | [-1.00, 0.17] | Yes |
| CORE--SWE-mini | 14 | 0.74 | [0.27, 0.93] | No |
| CORE--TAU | 12 | 0.78 | [0.26, 0.98] | No |
| GAIA--SciCode | 9 | -0.30 | [-0.89, 0.55] | Yes |
| GAIA--SAB | 7 | -0.75 | [-1.00, 0.17] | Yes |
| GAIA--SWE-mini | 17 | 0.89 | [0.60, 0.99] | No |
| GAIA--TAU | 14 | 0.86 | [0.57, 0.97] | No |
| SciCode--SAB | 7 | 0.43 | [-0.62, 1.00] | Yes |
| SciCode--SWE-mini | 9 | 0.02 | [-0.81, 0.81] | Yes |
| SciCode--TAU | 9 | -0.13 | [-0.80, 0.76] | Yes |
| SAB--SWE-mini | 7 | -0.54 | [-1.00, 0.65] | Yes |
| SAB--TAU | 7 | -0.68 | [-1.00, 0.19] | Yes |
| SWE-mini--TAU | 14 | 0.82 | [0.46, 0.97] | No |

**Implication:** all striking negative cost estimates arise in low-overlap pairs and their configuration-resampling intervals cross zero. They are evidence of heterogeneous point estimates, not statistically stable evidence of negative association. The main paper must not headline negative cost correlation as a confirmed result.

## 2. Multiple comparisons

Holm--Bonferroni correction was applied separately to the 15 accuracy-rank and 15 cost-rank Spearman tests at alpha = 0.05.

### Surviving accuracy associations

- GAIA--SWE-mini: uncorrected p = 0.00148; Holm-adjusted p = 0.02219.
- SWE-mini--TAU: uncorrected p = 0.00170; Holm-adjusted p = 0.02381.

### Surviving cost associations

- CORE--GAIA: p < 0.00001; Holm-adjusted p = 0.00003.
- CORE--SWE-mini: p = 0.00268; Holm-adjusted p = 0.02944.
- CORE--TAU: p = 0.00299; Holm-adjusted p = 0.02993.
- GAIA--SWE-mini: p < 0.00001; Holm-adjusted p = 0.00002.
- GAIA--TAU: p = 0.00007; Holm-adjusted p = 0.00089.
- SWE-mini--TAU: p = 0.00029; Holm-adjusted p = 0.00346.

No negative cost correlation survives Holm correction. This strengthens a narrower result: some high-overlap benchmark pairs show robust positive cost-rank transfer, while evidence that any particular low-overlap pair is truly negative is weak.

## 3. Quartile rank changes

We ranked labels within each pair separately and compared top-quartile / bottom-quartile membership. Quartile boundaries use within-pair average ranks and therefore are descriptive in small samples.

### Concrete cost examples

- **GAIA--SAB (N=7):** 1/7 (14.3%) labels move from the cheapest quartile on GAIA to the most expensive quartile on SAB; 3/7 (42.9%) make an extreme top/bottom flip in either direction; 6/7 (85.7%) change quartile.
- **SAB--SWE-mini (N=7):** 2/7 (28.6%) go from cheapest on SAB to most expensive on SWE-mini; 3/7 (42.9%) make an extreme flip; all 7/7 change quartile.
- **SciCode--SWE-mini (N=9):** 2/9 (22.2%) go from cheapest on SciCode to most expensive on SWE-mini; 3/9 (33.3%) make an extreme flip; 5/9 (55.6%) change quartile.
- **CORE--GAIA (N=14):** no top-to-bottom cost flips; 4/14 (28.6%) change quartile.
- **GAIA--SWE-mini (N=17):** no extreme cost flips; 3/17 (17.6%) change quartile.

This provides a concrete conditional statement: in selected low-overlap pairs involving ScienceAgentBench or SciCode, 14--29% of shared labels move from the cheapest quartile to the most expensive quartile. It should be reported alongside the wide uncertainty intervals, not as a general-rate estimate.

## 4. Frontier-definition sensitivity

| Definition | Max appearances, all labels | Max appearances, labels tested on 5+ workloads | Broad universal winner? |
|---|---:|---:|---|
| Standard nondominated | 4 | 4 | No |
| HAL-inspired convex hull | 3 | 3 | No |
| Nondominated with 5% relative cost/accuracy tolerance | 5 | 5 | No |

The conclusion **``no broadly tested label wins every available workload''** holds under all three definitions. But the stronger statement **``no label wins more than 4/6''** is not robust: under the 5% tolerance sensitivity, o4-mini Low is retained on 5/6 workloads. The tolerant definition is deliberately conservative: a point dominates only with at least 5% better accuracy and 5% lower cost. It is a near-tie sensitivity check, not a calibrated measurement-error model.

## 5. Placebo/null label-shuffle baseline

For each pair, the null permutes pairing between the two observed rank vectors 10,000 times while preserving N and the marginal values. It tests whether the observed magnitude differs from random pairing at that overlap; it does **not** test whether model labels were missing at random.

### Cost-rank results versus the permutation null

Robust non-null positive associations include:

- CORE--GAIA: observed rho = 0.93, null 95% range [-0.53, 0.54], empirical p = 0.0001.
- CORE--SWE-mini: rho = 0.74, null range [-0.53, 0.53], p = 0.0033.
- CORE--TAU: rho = 0.78, null range [-0.58, 0.59], p = 0.0045.
- GAIA--SWE-mini: rho = 0.89, null range [-0.48, 0.48], p = 0.0001.
- GAIA--TAU: rho = 0.86, null range [-0.53, 0.53], p = 0.0002.
- SWE-mini--TAU: rho = 0.82, null range [-0.53, 0.54], p = 0.0005.

No negative cost association is distinguishable from this finite-N permutation null at 0.05. GAIA--SAB is closest: rho = -0.75, null range [-0.75, 0.75], empirical p = 0.0675.

**Implication:** the original wording that cost transfer is generally ``unstable'' is too broad if it relies on low-N negative pairs. The defensible headline is more nuanced: cost-rank transfer is strongly positive for several high-overlap pairs, but it is not uniformly established across workloads; low-overlap pairs are indeterminate rather than confirmed reversals.

## 6. Missing-data check

The fixed-Generalist matrix is strongly unbalanced by evaluation recency and benchmark coverage. Seven labels occur on all six primary benchmarks. Two labels occur on five: DeepSeek R1 and Gemini 2.0 Flash are both absent from ScienceAgentBench. The public CSV contains no failure/error status explaining these omissions.

This pattern is not enough to infer that ScienceAgentBench exclusions were caused by model failure or cost: DeepSeek R1 has the highest average dollar cost among the broad labels (about $152 across its available five benchmarks), whereas Gemini 2.0 Flash has the lowest (about $17). The missingness is compatible with non-random evaluation scheduling, budget allocation, model availability, or unreported failures. It must be treated as an unidentifiable selection mechanism.

## 7. Threats to validity paragraph

> **Threats to validity.** Our conclusions are subject to construct, internal, and external validity threats. Construct validity is limited because the public `Models` and `Agent Name` display strings do not fully encode benchmark-specific prompts, tools, budgets, harness versions, or pricing assumptions; matching a displayed label under the displayed Generalist scaffold is therefore not a controlled base-model comparison. Internal validity is limited by sparse, unbalanced coverage and primarily single-run evaluations. Two broadly covered labels are absent from ScienceAgentBench, but the public table provides no failure code or exclusion rationale; this prevents us from assuming missingness at random or attributing exclusions to capability or cost. Configuration-resampling intervals quantify sensitivity to the observed shared-label set rather than rollout variance, and all negative dollar-cost correlations occur in low-overlap pairs whose intervals cross zero and whose permutation tests do not reject random pairing. Finally, external validity is restricted to this frozen HAL snapshot, its then-current dollar prices, and six workloads under one repeated displayed scaffold. We therefore interpret robust positive high-overlap correlations as descriptive evidence of transfer in selected workload pairs, and interpret low-overlap reversals as unresolved heterogeneity that motivates rather than proves workload-specific cost dynamics.
