# Aggregate deployment-efficiency analysis (Phase A)

## Scope and identifiability

This extension uses only the frozen aggregate public HAL CSV. It does **not** infer tokens, API calls, tool calls, retries, per-task success/failure cost, tail risk, provider list pricing, or trace-level execution behavior. Those require decrypted per-task traces or an aggregate usage export, neither of which is available in the public snapshot.

Primary cohort: 86 rows, six primary workloads, and the displayed HAL Generalist Agent scaffold.

## CostPerSuccess

We define aggregate dollars per expected success as:

\[
\operatorname{CPS}_{i,b}(\epsilon)=\frac{C_{i,b}}{\max(A_{i,b},\epsilon)},
\]

where cost \(C\) is the aggregate displayed dollar cost and accuracy \(A\) is expressed as a fraction. The primary denominator floor is pre-specified as \(\epsilon=0.01\). This prevents division by zero while strongly penalizing zero-accuracy rows. It is an aggregate ratio, **not** the observed mean cost of successful task runs.

Sensitivities:

- primary: 1% accuracy floor;
- sensitivity: 5% accuracy floor;
- sensitivity: exclude zero-accuracy rows.

## Pattern: raw cost is more portable than success-adjusted cost

For the six pairs with at least 12 shared labels:

- mean raw dollar-cost rank correlation: **0.84**;
- mean CPS rank correlation at 1% floor: **0.59**;
- median raw dollar-cost rank correlation: **0.84**;
- median CPS rank correlation: **0.61**.

CPS rank correlation falls in five of six high-overlap pairs. Illustrative pairs:

| Pair | Raw cost rank rho | CPS rank rho, 1% floor |
|---|---:|---:|
| GAIA--SWE-mini | 0.89 | 0.29 |
| CORE--SWE-mini | 0.74 | 0.32 |
| SWE-mini--TAU | 0.82 | 0.45 |
| CORE--GAIA | 0.93 | 0.87 |
| GAIA--TAU | 0.86 | 0.78 |
| CORE--TAU | 0.78 | 0.83 |

The conclusion is directional and descriptive: success adjustment generally reduces portability, but it is not universal.

## LOBO raw-cost prediction

For each benchmark, estimate a label's mean centered log-cost from all other benchmarks and predict its held-out raw cost rank. Predictions are computed only for labels observed on at least two other workloads.

| Held-out benchmark | N | Predicted versus observed rank rho | 20,000-permutation p |
|---|---:|---:|---:|
| CORE-Bench Hard | 14 | 0.78 | 0.0016 |
| GAIA | 16 | 0.87 | <0.0001 |
| SciCode | 9 | -0.17 | 0.6801 |
| ScienceAgentBench | 7 | -0.64 | 0.1376 |
| SWE-bench Verified Mini | 16 | 0.90 | <0.0001 |
| TAU-bench Airline | 14 | 0.83 | 0.0004 |

Thus, stable observed label-level cost propensity predicts held-out raw costs for CORE, GAIA, SWE-mini, and TAU, but not for SciCode or ScienceAgentBench. With only 7–9 labels in the latter cases, this is benchmark-specific heterogeneity, not evidence for a general scientific-domain effect.

## Interpretation

The combined evidence supports:

> Raw dollar-cost ranks can be predictable across selected workloads because of persistent displayed-label cost propensity. However, aggregate dollars per expected success are less portable, so predictable cheapness is not equivalent to predictable deployment efficiency.

It does **not** support claims about failure costs, retry dynamics, tokens, tools, list pricing, or trace-level execution mechanisms.
