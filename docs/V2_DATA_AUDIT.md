# External trace sources evaluated for V2

| Dataset | Direct access tested | Success label | Usage/cost telemetry | Exact cross-scaffold matching | V2 decision |
|---|---|---|---|---|---|
| `nvidia/Open-SWE-Traces` | Yes, public Parquet | `resolved` | No tokens or dollars | Yes, exact `instance_id` + model for SWE-agent/OpenHands | Include matched trajectory-burden study |
| `nebius/SWE-agent-trajectories` | Yes, public Parquet | `target` | No tokens or dollars | No matched alternate scaffold established | Do not merge into primary effect estimate |
| `nvidia/SWE-Hero-openhands-trajectories` | Yes, public Parquet | No observed resolved field in sampled schema | No tokens or dollars | No matched counterpart established | Exclude from outcome analysis |
| `PatronusAI/TRAIL` | Download tested, HTTP 401 gated | Not inspected due to gating | Not inspected due to gating | Not available | Exclude; do not claim use |
| `ibm-research/ITBench-Trajectories` | Yes, public JSON/JSONL | Judge outputs | Sampled metadata had no usable token/cost fields | Current public panel one model | Exclude from causal/matched study |

## Inclusion standard

A V2 dataset enters a quantitative result only when it provides:

1. public reproducible access;
2. a task identifier;
3. exact model and scaffold identifiers;
4. an outcome label; and
5. an exact matching or credible repeated-measures design.

A dataset supports dollar cost or FailureCostRatio only when it additionally provides documented billing/token components. Public trace text alone is insufficient.
