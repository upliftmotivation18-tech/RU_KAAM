# Anonymous supplement instructions

This directory is a staging checklist, not a release archive.

For an anonymous supplement, include only files required to reproduce the empirical analysis:

```text
README.md
requirements.txt
src/
scripts/
tests/
data/README.md
data/SOURCE_MANIFEST.md
data/all_leaderboards_costs_HAL.csv   # only if upstream license is re-verified
paper/tables/
```

Exclude:

```text
.git/
__pycache__/
.pytest_cache/
outputs/
paper/main.pdf
paper/main.log
paper/main.aux
paper/main.bbl
paper/main.blg
personal GitHub URLs
names, affiliations, email addresses, or local account metadata
```

Before submitting, inspect the archive contents with:

```bash
unzip -l anonymous_supplement.zip
```

and run:

```bash
python3 -m pytest -q
python3 scripts/run_analysis.py --bootstrap 5000
```

from the extracted archive.
