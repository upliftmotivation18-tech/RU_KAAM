# Public-source manifest

This study uses a **frozen local analysis copy** of the public data file below. It is not a claim that the upstream repository is immutable.

| Field | Value |
|---|---|
| Dataset repository | `https://github.com/fsndzomga/efficient-benchmarking-ai-agents` |
| Upstream repository commit inspected | `cd734cced26cdb9bbf59e704088daaaaca126b6e` |
| Upstream path | `data/all_leaderboards_costs_HAL.csv` |
| Local analysis file | `data/all_leaderboards_costs_HAL.csv` |
| Local SHA-256 | `f8a07cbe6aae2801f592df3db7432a91c32a3de63dcf3ac4e0b5896bd34731f0` |
| Retrieval / local freeze date | 2026-08-15 UTC |
| Upstream repository license | MIT, per the repository README at the inspected commit |
| HAL Pareto reference repository | `https://github.com/peterkirgis/hal-paper-analysis` |
| HAL Pareto reference commit inspected | `92ff146a83e054b4171731d1b72c2b9067534b48` |

## Acquisition

To re-acquire the exact version when GitHub retains the commit:

```bash
git clone https://github.com/fsndzomga/efficient-benchmarking-ai-agents.git
cd efficient-benchmarking-ai-agents
git checkout cd734cced26cdb9bbf59e704088daaaaca126b6e
sha256sum data/all_leaderboards_costs_HAL.csv
```

The expected hash is recorded above and is enforced by `scripts/run_analysis.py` for the default frozen input.

## Redistribution note

The upstream project declares an MIT license. This repository retains attribution to the data/paper authors and the source repository. Before a public paper/repository release, re-check the upstream repository's license at the cited commit and any licenses or usage constraints inherited from HAL traces.
