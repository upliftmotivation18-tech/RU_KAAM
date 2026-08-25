# The failure-cost premium is a task-difficulty artifact

## Headline

At fixed task and model, failed agent trajectories are NOT more expensive than
successful ones. The popular "expensive failures" reading of raw data is a
selection artifact of task difficulty, not a property of failure itself.

## Evidence (Open-SWE MiniMax-M2.5 boundary sample, 977 matched pairs)

### Naive cross-task view replicates the folklore

Comparing each scaffold's resolved versus failed trajectories across tasks:

| Scaffold | Turns ratio (failed/resolved) | Characters ratio | Reasoning chars ratio |
|---|---|---|---|
| OpenHands | 1.21 [1.07, 1.36] | 1.20 [1.08, 1.36] | 1.32 [1.08, 1.63] |
| SWE-agent | 1.19 [1.07, 1.35] | 1.33 [1.11, 1.54] | 1.36 [1.05, 1.68] |

This matches SWE-Effi-style "expensive failure" claims: failures look ~20--35%
heavier. A leaderboard operator would conclude failure carries a cost premium
and price it in.

### Task-matched view makes the premium vanish

107 pairs have discordant outcomes: identical task, identical model, one
scaffold resolved, the other failed. On these:

- Raw sign test: failed side heavier 47--52 times out of 107 on every metric
  (two-sided binomial p >= 0.25).
- After dividing each trajectory by its own scaffold's median burden (removing
  the known OpenHands/SWE-agent offset): fraction 0.50--0.53, all p >= 0.56,
  normalized failed/ok median ratio 0.98--1.06 with intervals [0.75, 1.42]
  spanning 1 throughout.

So on the same task that one configuration solved, the configuration that
failed did not burn measurably more before giving up.

### Interpretation

Hard tasks make agents burn more AND fail; the observed cross-task failure
premium is explained by which tasks failed, not by failure adding burden.
Failure-cost ratios computed from unconditioned comparisons conflate workload
difficulty with execution behavior. Any leaderboard or procurement rule that
multiplies "failure rate x failure premium" inherits this artifact.

Boundary conditions: character/turn proxies, not tokens or dollars; one model;
four-shard nonrandom sample; power rules out effects beyond roughly +/-26%
(CI width); observational -- no claim that failure never adds cost, only that
no premium survives task matching here.

## Connection to the paper's thesis

This is the trajectory-level mirror of the CPS result: success-adjusting an
aggregate changes the ranking, and conditioning on outcomes without matching
the workload manufactures structure that is not there. Aggregate dollars,
failure premiums, and mean costs all inherit composition effects; only
task-matched designs separate difficulty from behavior.
