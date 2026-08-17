# AgenticOS 2026 packaging decision

## Official policy checked

AgenticOS's official workshop page states:

- Regular papers may contain **up to 6 pages of technical content**.
- References and appendices are **not subject to the page limit**.
- The main paper must be self-contained; reviewers are not required to consult appendices.
- Submissions must be anonymized for double-blind review.

Source: https://agentic-fmos.github.io/

## Submission artifacts

Use these files:

| Artifact | Path | Purpose |
|---|---|---|
| Main submission PDF | `paper/main_submission.pdf` | Exactly 6 pages total: 4 technical-content pages, 1 references page, 1 checklist page. No appendix. |
| Anonymous supplement | `paper/supplement/agenticos_anonymous_supplement.zip` | Robustness outputs, source snapshot/hash, code, tests, generated tables, and supplementary figures. |

Supplement SHA-256:

```text
a8a60fd0b5818a1193791b08e2f1a48a3c05934824d7dad1f320a44c87471675
```

## Why this package is safe for the limit

The main PDF contains every claim needed to assess the contribution: data scope, method, high-overlap positive transfer result, non-robustness of low-overlap negatives, frontier conclusion, and validity threats. The supplement supplies exhaustive tables and reproduction material without being required to understand the main claim.

## Final portal check

Before upload, confirm that the AgenticOS OpenReview form exposes a supplementary-material upload field. If it does not, upload only `main_submission.pdf`; the main paper remains self-contained.
