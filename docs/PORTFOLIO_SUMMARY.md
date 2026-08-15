# Does Cost-Efficiency Travel? — public project summary

## One-sentence finding

Across six public HAL workloads evaluated with the repeated HAL Generalist Agent display label, accuracy ranks often agree across workloads more than dollar-cost ranks do; cost--accuracy frontier membership is therefore not reliably portable from one benchmark to another.

## Plain-language version

A model that looks cheap for its performance on one AI-agent benchmark is not automatically a cheap choice for another kind of task. Accuracy ordering sometimes travels; the relative amount an agent spends can change much more, likely because different workloads produce different tool calls, retries, and execution loops.

## What we did

We conducted a reproducible secondary analysis of public Holistic Agent Leaderboard data:

- held the displayed agent scaffold fixed to HAL Generalist Agent;
- compared repeated public model labels across six benchmarks;
- measured accuracy-rank and dollar-cost-rank agreement;
- measured nondominated cost--accuracy frontier overlap;
- separated standard nondominance from a HAL-inspired randomized-policy convex-hull reconstruction;
- documented data provenance, source hash, analysis choices, and limitations.

## What we found

- GAIA and SWE-bench Mini show strong agreement in both accuracy and dollar-cost ranks.
- Other pairs do not: GAIA and ScienceAgentBench have positive accuracy rank association but strongly negative dollar-cost rank association in this snapshot.
- No display label tested on at least five primary workloads is nondominated on every one of them.
- These are descriptive public-leaderboard results, not causal claims about a base model independent of all benchmark-specific setup details.

## Reproduce

```bash
python3 -m pip install --user -r requirements.txt
python3 -m pytest -q
python3 scripts/run_analysis.py --bootstrap 5000
python3 scripts/build_paper_tables.py
python3 scripts/build_compact_figure.py
```

Source provenance and licensing notes are in `data/SOURCE_MANIFEST.md`.
