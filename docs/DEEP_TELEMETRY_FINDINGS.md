# Deep cross-source telemetry findings

## Finding 1: Long-horizon coding-agent inference is context dominated

Two independent public real-session sources show that agent inference is dominated by large repeated contexts rather than fresh output.

### TraceLab

- 665,453 LLM rounds across 8,058 sessions.
- 743,819 tool calls.
- Median round input context: 132,092 tokens.
- Median output: 249 tokens.
- Mean cache-read share among rounds with input: 93.7%.
- Median session context growth: 47,267 tokens; P90 205,248; P99 492,202.

### MIMO Claude Code traces

- 1,017 sessions, one model (`mimo-v2.5-pro`).
- Median session: 19,775 uncached input tokens, 401,920 cache-read tokens, 5,100 output tokens, and 4 explicit tool calls.
- Corpus totals: 46.3M uncached input, 753.0M cache-read, 12.0M output tokens.
- Aggregate cache-read volume is 16.3x uncached input and 63.0x output volume.

### Interpretation

Across two independent coding-agent telemetry sources, the dominant observable inference volume is repeated/cached context. A benchmark's single dollar total hides whether spending comes from model price, cache policy, context growth, or fresh generation. These results concern token composition, not billed dollars: cached-token tariffs differ by provider and are not reconstructed here.

## Finding 2: Agent context grows substantially within sessions

TraceLab sessions have median input-context growth of 47k tokens, with a heavy tail: 205k at P90 and 492k at P99. This supports the interpretation that long-horizon agent cost is path dependent: later calls repeatedly carry state accumulated through earlier reasoning and tool observations.

This is not evidence that context growth causes failure because TraceLab has no task outcome label.

## Finding 3: Tool failures add latency and return less information

Across 743,819 TraceLab tool calls:

- successful calls: median wall latency 140 ms; median result 602 characters;
- failed calls: median wall latency 313 ms; median result 208 characters.

Failed calls therefore have about 2.24x median wall latency while returning roughly one-third as much text. This is an execution-waste signature, not a dollar FailureCostRatio.

Tool-level behavior is heterogeneous. For common tools, error rates and tail latency vary widely; interactive/waiting tools should not be naively interpreted as failures because some datasets encode control-state tools with `is_error=true` by convention.

## Finding 4: Public telemetry remains outcome fragmented

- TraceLab and MIMO expose rich usage and tool telemetry but no verified benchmark success label.
- Exgentic exposes multiple benchmarks, harnesses, models, total tokens, per-call usage and span status, but the inspected schema lacks task reward, dollar cost, and exact task matching across harnesses.
- Open-SWE exposes exact task/model/scaffold matching and resolved status, but no token or dollar fields.

No single public source among those audited jointly exposes exact task, model, scaffold, outcome, tokens, calls, retries, latency, and billing. This fragmentation is itself a reproducibility finding and motivates a minimum public agent-telemetry schema.

## Exgentic negative robustness result

Within benchmark-model cells with at least 10 sessions per harness, apparent harness median-token differences had wide independent-bootstrap intervals and did not meet a conservative robustness bar. Example: AppWorld/Kimi-K2.5 tool-calling versus Claude Code median ratio 0.62, 95% interval [0.45, 1.32], Mann--Whitney p=0.0535. Without exact task matching, these are not causal scaffold effects and are not promoted to the paper's headline evidence.
