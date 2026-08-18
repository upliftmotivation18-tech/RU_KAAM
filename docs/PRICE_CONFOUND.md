# Price-tier / cost-propensity confound analysis

## Question

Could the robust raw dollar-cost rank correlations simply reflect stable model-level price/cost tiers rather than portable workload-specific agent behavior?

## What can and cannot be identified

The frozen public CSV has no provider alias, token counts, input/output split, cache fields, price-card snapshot, or routing metadata. Therefore it cannot support a source-grounded historical **list-price adjustment** or a token-cost reconstruction. Public trace archives exist but are encrypted, so raw usage cannot currently be recovered reproducibly.

We instead perform an explicitly observational **displayed-model-label cost-propensity adjustment**. It removes each label's cross-workload average observed log-cost propensity and each benchmark's average log-cost level. It does not prove that the removed effect is list price, and it does not identify a causal execution-dynamics effect.

## Model

For the 86 HAL Generalist rows across six primary benchmarks and 25 displayed labels, we fit:

\[
\log C_{ib} = \alpha_b + \gamma_i + \epsilon_{ib},
\]

where \(\alpha_b\) is a benchmark fixed effect and \(\gamma_i\) is a displayed-model-label fixed effect.

Fit summary:

- observations: 86
- labels: 25
- benchmarks: 6
- parameters: 30
- residual degrees of freedom: 56
- \(R^2=0.8203\)
- adjusted \(R^2=0.7273\)
- residual SD: 0.6922 log dollars

## Result

Strong raw cost-rank transfer does not remain after adjusting for observed label and benchmark cost propensity:

| Pair | Raw cost rank rho | Residual-cost rank rho | 20,000-permutation p |
|---|---:|---:|---:|
| CORE--GAIA | 0.925 | 0.231 | 0.426 |
| CORE--SWE-mini | 0.736 | -0.490 | 0.079 |
| CORE--TAU | 0.776 | -0.035 | 0.921 |
| GAIA--SWE-mini | 0.892 | 0.027 | 0.917 |
| GAIA--TAU | 0.864 | 0.134 | 0.648 |
| SWE-mini--TAU | 0.824 | -0.165 | 0.570 |

## Interpretation

The robust positive raw cost-rank correlations are consistent with being largely driven by stable displayed-label cost propensity. This propensity may include provider price tier, reasoning mode, token use, cached-token treatment, provider routing, and undocumented setup choices. It cannot be labeled ``list pricing'' from the frozen CSV alone.

The correct paper claim is therefore:

> Raw dollar-cost rankings transfer across several high-overlap HAL workloads, but this transfer is largely absorbed by stable displayed-model-label cost propensity. The public data do not establish portable workload-specific execution-cost dynamics after that adjustment.

## Historical pricing route for future work

A proper list-price/tokens analysis requires decrypted aggregate token usage or decrypted trace files and date-matched provider/model pricing. Relevant historical HAL harness snapshots are:

- April--May 2025 price table: `fd5b8919e1a0d5cf6fa8a37fa3606233ad6645fe`
- September 2025 cache-aware accounting: `1255aef785803e595274ee056cbdb3dd6610adfd`

The public encrypted trace artifacts cannot currently provide a reproducible token reprice without a HAL-supplied decryption path or an aggregate usage export.
