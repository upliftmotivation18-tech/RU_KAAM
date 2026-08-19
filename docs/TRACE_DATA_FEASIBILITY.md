# Trace-data feasibility audit for Phase B

Audit date: 2026-08-18. This document distinguishes accessible fields from requested-but-unavailable deployment variables. No field is inferred from text without an explicit proxy label.

| Source | Access tested | Tasks / models / scaffolds | Success label | Tokens or dollars | Calls / tools | Matched scaffold design | Permitted Phase B use |
|---|---|---|---|---|---|---|---|
| `nvidia/Open-SWE-Traces` | Public, unencrypted parquet files | SWE-rebench-V2; MiniMax-M2.5 and Qwen3.5; SWE-agent and OpenHands | `resolved` (0/1/-1) | No token or cost fields | Tool-call structure and trajectory messages | Yes, partial exact `instance_id` overlap across SWE-agent/OpenHands within model | Matched trajectory-burden, success, tool-call, and text-volume proxies |
| `nebius/SWE-agent-trajectories` | Public, unencrypted parquet files | SWE-bench-extra/dev; multiple SWE-agent model labels | `target` | No token or cost fields | Message trajectory | No matching OpenHands counterpart established | Within-SWE-agent trajectory-length proxy only |
| `nvidia/SWE-Hero-openhands-trajectories` | Public, unencrypted parquet files | R2E-Gym subset; OpenHands | No resolved/success field in observed schema | No token or cost fields | Tool-call structure and trajectory messages | No matched counterpart established | Descriptive trajectory schema only |
| `PatronusAI/TRAIL` | Listed public but download returned HTTP 401 without authenticated gated access | GAIA and SWE-Bench annotated traces | Error annotations | Not inspected, gated | Not inspected, gated | Not available to this analysis | Blocked; do not claim use |
| `ibm-research/ITBench-Trajectories` | Public unencrypted JSON/JSONL files | ITBench SRE; currently GPT-OSS-120B with three runs/scenario | Judge scores | Sample judge metadata reports duration/inference count 0; no billing/token fields observed | Session/tool transcript | One model currently; no matched model/scaffold panel | Descriptive future extension only |

## Consequences

1. **True dollar FailureCostRatio, token cost, P90/P95 dollar cost, retries, and list-price decomposition remain blocked.** These require provider usage or cost fields absent from accessible trace schemas.
2. `nvidia/Open-SWE-Traces` enables a distinct Phase B study: matched, within-task/model comparison of **trajectory burden** across SWE-agent and OpenHands. Valid measurable proxies are assistant turns, tool calls, tool-result turns, total message characters, reasoning characters, and success status.
3. Trajectory text volume is not a token count and must not be billed or named as cost. It is a tokenizer-agnostic burden proxy.
4. The Open-SWE study is external to the HAL primary cohort. It supplies mechanism-oriented evidence about scaffold trajectory burden, not direct validation of HAL dollar rankings.
