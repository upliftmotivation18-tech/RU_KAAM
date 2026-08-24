# Telemetry implementation findings

## Analyses completed

### Exgentic agent-llm-traces

A convenience sample of 11 public shards was inspected using the public source revision `70036b93a04e61b0ea2706a68b962f4f26774587`.

The source exposes session-level total tokens and per-call input/output-token usage, call status, benchmark, harness, and model/provider. It does not expose task reward, exact task IDs for cross-harness matching, dollar billing, or observed session latency in the analyzed schema.

We evaluated independent harness distributions only inside benchmark--model cells having at least 10 sessions per harness. Examples include TAU2 Telecom/Azure GPT-4.1 and TAU2 Retail/Azure GPT-4.1.

### Result

No harness token-burden comparison in the available independent-session panels met a conservative robustness bar: median-ratio bootstrap intervals were wide and crossed one, and Mann--Whitney tests were non-significant. For example, in AppWorld/Azure Kimi-K2.5, the tool-calling versus Claude Code total-token median ratio was 0.62, but its 95% independent-bootstrap interval was [0.45, 1.32] and Mann--Whitney p=0.0535.

This is not evidence of no harness effect. It means the sampled data lack exact task matching and have insufficient precision for a robust comparative claim.

## Additional source-specific decisions

- TraceLab: authentic rich round/tool telemetry; no verified task outcome. Retain as a candidate for a future real-session cache/context study, but do not merge into benchmark success/cost claims.
- MIMO Claude Code traces: real per-round usage including cache fields and timestamped tools; task outcome and cost remain unverified. Do not use as benchmark efficacy evidence.
- Terminal-Bench local traces: task/agent/model/conversation data; no top-level reward/cost/token fields observed. Do not use for success/cost claims unless outcome fields are recovered from a documented source.
- Lightcap: operation telemetry rather than a clearly benchmarked agent evaluation panel. Exclude.
- AgentKit: only 9 demo-like rows. Exclude.

## Conclusion

The new public sources improve the telemetry audit and confirm that token/call-level data are available in some settings. They do not yet furnish the jointly task-matched, outcome-labeled, billed-cost panel required to repair the central causal and failure-cost limitations of the paper. The paper should retain the matched Open-SWE trace study as its only external causal-style scaffold evidence, because it satisfies exact task and model matching.
