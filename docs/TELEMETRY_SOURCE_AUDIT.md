# Telemetry-source audit, implementation outcome

## Sources verified directly

| Source | Public access | Verified schema | Outcome label | Token telemetry | Tool/retry/latency | Valid role in study |
|---|---|---|---|---|---|---|
| HAL aggregate CSV | yes | benchmark/scaffold/display label/accuracy/total cost | aggregate accuracy only | no | no | Primary held-out leaderboard analysis |
| HAL trace archive | artifacts public, content encrypted | encrypted upload only | inaccessible | inaccessible | inaccessible | Not usable for Phase B |
| Open-SWE-Traces | yes | task ID, model, scaffold, resolved, structured trajectory, tool calls | yes | no | tool calls/turns/text | Exact matched external scaffold burden study |
| Exgentic agent-llm-traces | yes | benchmark, harness, model, total tokens, OTel spans, per-call input/output tokens and status | no benchmark reward observed | yes | call counts and error spans; no duration fields observed in sample | Descriptive benchmark/model/harness telemetry anatomy |
| TraceLab SyFI coding trace | yes | session/model/round token composition, tool latency, errors, timing events | no task success observed | yes, including cache fields | tool latency/error | Real-session telemetry anatomy, separate from benchmark efficacy |
| Terminal-Bench traces local | yes | task/agent/model/conversations/episode/run ID | no reward/cost fields observed in top-level schema | no top-level telemetry | conversation transcript | Not yet usable for success/cost claims |
| MIMO Claude Code traces | yes | timestamped messages, Anthropic-style token/cache usage, tool events | unverified task outcome | yes | tool events/error fields | Single-system telemetry anatomy if session outcome can be verified |
| Lightcap runtime telemetry small | yes | operations/events/errors/duration | operation status, provenance unclear | no verified LLM token fields in inspected operation schema | duration/error | Demonstration/observability schema only |
| AgentKit sessions | yes | status/duration/tokens/retries/tool calls | yes | sparse | yes | Too small/demo-like (9 rows), exclude from findings |

## New candidate: Exgentic

The inspected 11-shard sample contains multiple agent benchmarks and models. It includes same benchmark/model cells under multiple harnesses, for example:

- TAU2 Telecom, Azure GPT-4.1: `claude_code` (16 sessions), `smolagents_code` (15), `tool_calling` (24).
- TAU2 Retail, Azure GPT-4.1: `claude_code` (14), `smolagents_code` (45).
- TAU2 Airline, Azure GPT-4.1: `smolagents_code` (38), `openai_solo` (8).

Each session has total tokens and per-call OTel fields for input/output tokens and error status. The current data do not expose a benchmark reward/success variable, dollar billing, task matching across harnesses, or clear session-duration field. Therefore it cannot support cost-per-success, FailureCostRatio, or paired causal scaffold claims. It can support a descriptive token/call/error anatomy within fixed benchmark-model cells.

## Inclusion rules

A source enters main-paper evidence only if its claim matches its schema:

- Say **cost** only with billing fields or reproducible dated tariff reconstruction.
- Say **success/failure** only with an observed task outcome.
- Say **matched scaffold difference** only with exact task and model matching.
- Otherwise say **descriptive telemetry pattern**, report the scope, and keep it separate from HAL claims.
