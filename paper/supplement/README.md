# Anonymous supplemental material

## Contents

This supplement supports the regular-paper submission **“Does Cost-Efficiency Travel? Rank Transfer and Frontier Stability in Fixed-Scaffold Agent Evaluation.”** It contains:

- frozen public HAL data snapshot and source provenance;
- reproducible analysis code and tests;
- 10,000-draw configuration-resampling intervals for every eligible pair;
- Holm--Bonferroni correction tables;
- label-permutation null analyses;
- cost-quartile rank-change results;
- frontier-definition sensitivity analyses;
- missingness summaries;
- rank-change supplementary figure;
- commands needed to regenerate all results.

## Reproduce

```bash
python3 -m pip install --user -r requirements.txt
python3 -m pytest -q
python3 scripts/run_analysis.py --bootstrap 5000
python3 scripts/run_reviewer_checks.py
python3 scripts/build_paper_tables.py
python3 scripts/build_reviewer_tables.py
python3 scripts/build_compact_figure.py
```

The primary analysis uses exact public display-label strings, an overlap threshold of 5, 10,000 configuration-resampling draws, 10,000 permutation draws, and seed `20260816` for the reviewer checks.

## Interpretation caveat

The configuration-resampling intervals quantify sensitivity to the finite observed set of shared HAL display labels. They are not rollout-level confidence intervals and should not be interpreted as a causal model-effect estimate. Public display labels do not fully encode all benchmark-specific prompt, tool, budget, or harness settings.
