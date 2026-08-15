# Paper-ready results notes

## Main finding

Holding the displayed HAL Generalist Agent scaffold fixed, rank transfer for repeated HAL displayed model labels is heterogeneous: accuracy-rank association is often positive across the six retained workloads, whereas dollar-cost-rank association ranges from strongly positive to strongly negative. The resulting cost--accuracy frontier membership is not reliably portable across benchmarks. Because the display labels do not encode all benchmark-specific setup details, these findings are descriptive of the public HAL rows rather than a controlled causal model comparison.

## Data and coverage

The frozen source file contains 242 displayed evaluations across 9 benchmarks, 11 scaffolds, and 29 model configurations. Most scaffolds appear on only one benchmark. HAL Generalist Agent is the only scaffold with broad multi-workload coverage: 21 configurations on CORE-Bench Hard, 17 on GAIA, 9 on SciCode, 7 on ScienceAgentBench, 18 on SWE-bench Mini, and 14 on TAU Airline. USACO has only one Generalist row and is excluded from rank-transfer analyses.

The data contain complete accuracy and total-dollar-cost fields, but 235 of 242 rows have one run and only seven report two runs. Confidence intervals are reported in the source CSV for only seven rows.

## Frontier reproducibility

The source CSV's `Is Pareto` labels align almost perfectly with the **HAL-inspired origin-anchored convex-hull reconstruction**: 30 supplied frontier rows are recovered, with two row-level discrepancies. The standard nondominance definition identifies 19 additional non-dominated rows. The paper should explicitly distinguish these two objects:

- nondominated Pareto: discrete configuration selection;
- convex hull: randomized-policy / agent-mixture interpretation.

## Main pairwise examples

| Pair | Shared displayed labels | Accuracy Spearman rho [configuration-resampling interval] | Cost Spearman rho [configuration-resampling interval] |
|---|---:|---:|---:|
| GAIA -- SWE-bench Mini | 17 | 0.71 [0.31, 0.91] | 0.89 [0.61, 0.99] |
| SWE-bench Mini -- TAU Airline | 14 | 0.76 [0.40, 0.91] | 0.82 [0.46, 0.97] |
| GAIA -- ScienceAgentBench | 7 | 0.64 [-0.18, 1.00] | -0.75 [-1.00, 0.18] |
| CORE-Bench Hard -- ScienceAgentBench | 7 | 0.56 [-0.41, 1.00] | -0.64 [-1.00, 0.17] |
| SciCode -- SWE-bench Mini | 9 | 0.15 [-0.66, 0.78] | 0.02 [-0.81, 0.82] |

The small-overlap configuration-resampling intervals are wide and should not be used for hypothesis tests. Treat the high-overlap pairs as the most stable descriptive evidence and describe the remaining pairs as descriptive heterogeneity.

## Fragile-pair sanity check: SciCode--SWE-bench Mini

The low-correlation pair has exactly 9 shared Generalist model configurations. The reproduced estimates are accuracy rho = 0.150466 and cost rho = 0.016667. Its wide intervals include large positive and negative values. It supports the claim that transfer is not guaranteed, but it must not be cited as precise evidence of zero association.

## Pareto membership

Under standard nondominated Pareto membership within the fixed-Generalist cohorts, no broadly tested displayed label appears on the frontier in every workload. Among labels tested on five or more benchmarks, the highest nondominated-frontier rate is 4/6 for Claude-3.7 Sonnet High; several labels appear on only one or no frontiers. Pairwise common-cohort nondominated-frontier Jaccard similarity ranges from 0.17 to 0.43 in many pairs, with some values lower; this should be interpreted alongside continuous rank metrics.

## Domain analysis

Use only as exploratory context. Under HAL's categories, only three same-domain Scientific Programming pairs are available in the primary cohort. This is inadequate for a general within-domain versus cross-domain claim. Do not headline it.

## Scaffold analysis

The within-benchmark paired-model table confirms known scaffold sensitivity but is not the main novelty. Keep it compact, perhaps in the appendix or as one table. Examples include:

- CORE-Agent versus Generalist on CORE-Bench: Generalist lower accuracy on average and lower cost.
- SWE-Agent versus Generalist on SWE-bench Mini: SWE-Agent much higher accuracy on average but higher median cost.
- SAB Self-Debug versus Generalist on ScienceAgentBench: Self-Debug higher accuracy and lower cost among seven shared models.

The direction varies by benchmark, reinforcing why the main cross-workload analysis fixes scaffold rather than attempting an unsupported variance decomposition.
