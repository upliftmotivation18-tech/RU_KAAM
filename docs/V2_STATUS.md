# V2 status: evidence hardening completed

## Completed evidence upgrades

### 1. Small HAL cohort calibration

- Reported the fixed-effect complexity explicitly: 86 observations, 30 fitted parameters, 56 residual degrees of freedom.
- Reframed \(R^2=82.0\%\) as descriptive in-sample fit, not primary evidence.
- Promoted LOBO held-out prediction as the primary portability test.
- Added leave-one-label-out diagnostics:
  - CORE: 0.73--0.91
  - GAIA: 0.84--0.92
  - SWE-mini: 0.88--0.92
  - TAU: 0.79--0.95
  across every single-label omission.
- Kept SciCode and ScienceAgentBench cautious; no domain explanation is claimed.

### 2. CPS statistical inference

- 10,000 configuration-resampling intervals for all 15 CPS pairs.
- 20,000 label-pairing permutations for all 15 CPS pairs.
- Holm correction over 15 CPS tests.
- 10,000 paired raw-minus-CPS resampling contrast.
- Robust CPS associations: CORE--GAIA, CORE--TAU, and GAIA--TAU.
- Robust raw-minus-CPS contrast: GAIA--SWE-mini only.

### 3. Matched trace effect sizes

In 977 exact task--model matches under the documented Open-SWE boundary sample:

| Metric | OpenHands / SWE-agent median ratio | 10,000-bootstrap interval | OpenHands lower fraction |
|---|---:|---:|---:|
| Trajectory turns | 0.85 | [0.82, 0.87] | 69.7% |
| Tool calls | 0.85 | [0.82, 0.86] | 69.7% |
| Trajectory characters | 0.95 | [0.92, 0.98] | 55.1% |

These are burden-proxy results only. They do not estimate tokens, dollars, retries, or FailureCostRatio.

### 4. Dataset expansion audit

Candidate datasets were inspected directly. Only `nvidia/Open-SWE-Traces` meets the V2 inclusion rule for a matched external scaffold study. TRAIL was listed but its data download was gated (HTTP 401 without access); it is not used. Other public datasets lacked the required matched treatment/outcome design or billing telemetry.

## What remains blocked by public data

- dollar cost per successful trajectory;
- FailureCostRatio;
- token/cache/provider-price decomposition;
- retries and tail-dollar risk;
- causal model--scaffold--benchmark decomposition across HAL.

## V2 conclusion

The V2 evidence makes the paper harder to attack without claiming hidden telemetry: observed raw dollar-cost portability is robust in selected held-out settings, success-adjusted portability is only partially supported, and matched public traces establish scaffold-dependent execution burden at fixed task and model.
