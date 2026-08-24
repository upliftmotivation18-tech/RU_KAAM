# Deep telemetry analysis: cross-source findings

## 1. Repeated context, not fresh generation, dominates observable inference volume

### TraceLab

Across 665,453 rounds in 8,058 real coding-agent sessions, the median round carries 132,092 input tokens but emits 249 output tokens. Mean cache-read share is 93.7%. Median fresh append is about 1,045 tokens.

Across session-position deciles, median input rises from 68,246 tokens in the first decile to 159,809 in the last, while median fresh append remains around 1,000 and output around 240--280. Median final-round context is 3.6x the initial-round context; P90 is 9.9x.

### MIMO

Across 1,017 MIMO Claude Code sessions, median session usage is 19,775 uncached input tokens, 401,920 cache-read tokens, and 5,100 output tokens. Corpus totals are 46.3M uncached input, 753.0M cache-read, and 12.0M output tokens. Cache-read volume is 16.3x uncached input and 63.0x output.

### Cross-source interpretation

Two independent sources replicate the same qualitative result: agent inference is dominated by repeatedly carrying accumulated context. This is not a dollar-cost claim because cached-token tariffs differ by provider.

## 2. Agent resource burden is extremely heavy tailed

In TraceLab, the top 1% of sessions account for 48.3% of all summed input-token volume; the top 10% account for 88.2%. Median per-session summed input is 0.73M tokens, P90 18.0M, P99 268.5M, and the maximum 3.09B.

This means aggregate mean cost can be dominated by a small set of runaway trajectories. Median-only reporting also misses the deployment risk; both center and tail should be reported.

## 3. Tool errors cluster into recovery spirals

After a successful tool call, the next observed tool call is erroneous 4.9% of the time. After an erroneous tool call, the next is erroneous 21.0% of the time, a 4.29x conditional increase.

Session burden rises sharply with observed tool-error count:

| Tool errors | Median rounds | Median tool calls | Median summed input tokens |
|---|---:|---:|---:|
| 0 | 9 | 14 | 0.34M |
| 1 | 16 | 23 | 0.74M |
| 2--5 | 30 | 39 | 1.63M |
| 6+ | 130 | 146 | 14.65M |

The top 1% of token-heavy sessions average 105.8 tool errors, versus 3.37 for the other 99%. These are observational associations. Long sessions create more opportunities for errors, and errors may prolong sessions; direction cannot be identified without intervention/outcome data.

## 4. Large tool outputs are a concrete context-growth channel

When the current round contains under 1k tool-result characters, median next-input growth is 443 tokens. For 1k--10k characters it is 1,412 tokens; for outputs over 10k characters it is 5,420 tokens. This supplies an observable mechanism linking tool verbosity to subsequent context burden.

## 5. Tool failures are slower and less informative

Across 743,819 TraceLab tool calls, successful calls have median latency 140 ms and median result size 602 characters. Failed calls have median latency 313 ms and median result size 208 characters; P95 latency is 85.6s versus 15.8s. Failures therefore consume more wall time while yielding less information.

## 6. Public-data fragmentation remains the key measurement gap

TraceLab and MIMO reveal token/cache/tool anatomy without benchmark outcomes. Open-SWE supplies exact task/model/scaffold matching and resolved status but no token/billing telemetry. Exgentic supplies multi-benchmark/model/harness OTel usage but no reward or task matching. HAL supplies benchmark accuracy and dollar totals but encrypts trace content.

No audited source jointly exposes exact task, model, scaffold, outcome, token/cache use, retries, latency, and billing. The cross-source evidence therefore motivates a minimum public telemetry standard rather than a false merged causal analysis.
