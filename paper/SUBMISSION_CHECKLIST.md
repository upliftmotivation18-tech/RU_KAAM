# AgenticOS submission checklist

## Status

- [x] Anonymous PDF compiles with the official NeurIPS 2026 style file.
- [x] Workshop double-blind option enabled: `dblblindworkshop`.
- [x] Workshop title set to `AgenticOS @ NeurIPS 2026`.
- [x] Paper title, author block, and PDF metadata are anonymous.
- [x] Main submission PDF is exactly 6 pages total; its 4 pages of technical content satisfy the AgenticOS regular-paper limit, with references and checklist following.
- [x] Expanded robustness tables and reproduction materials are packaged in a separate anonymous supplement.
- [x] Public URLs in references point to third-party papers/data sources rather than an author-controlled repository.
- [x] Full paper compilation completes without LaTeX warnings or overfull boxes.
- [x] Research test suite passes.

## Before upload

- [ ] Re-check the AgenticOS portal for its current page limit, supplemental-material policy, and required OpenReview fields.
- [ ] Confirm that the workshop requires `dblblindworkshop`; switch only if the portal explicitly specifies another NeurIPS 2026 workshop track.
- [ ] Review the rendered PDF at 100% zoom, especially all figures and tables.
- [ ] Run the reproducibility pipeline from a clean environment and refresh the PDF if any source table changes.
- [ ] Create an anonymized supplement archive if supplemental materials are allowed. Include code, scripts, source manifest, `requirements.txt`, and generated tables; exclude `.git/`, cached files, and author-identifying metadata.
- [ ] Do not include a personal GitHub account, institution, acknowledgments, commit author identity, or identifying repository URL in the anonymous submission.
- [ ] Verify the OpenReview author list/profile requirements independently before submitting.
- [ ] Upload well before the stated AoE deadline and download/check the rendered OpenReview PDF.

## Files produced

- Submission PDF: `paper/main.pdf`
- Anonymous LaTeX source: `paper/main.tex`
- Bibliography: `paper/references.bib`
- Checklist: `paper/checklist.tex`
- Vector figures: `paper/figures/*.pdf`
- Generated tables: `paper/tables/*.tex`, `paper/appendix/*.tex`

## Post-review / public release

After anonymous review permits public disclosure:

- replace `Anonymous Author(s)` with author names and affiliations;
- change the style option from `dblblindworkshop` to the workshop's camera-ready option if accepted;
- publish the repository and add its stable URL to the paper;
- release a concise public project summary and portfolio write-up;
- preserve the source-data attribution and license information in `data/SOURCE_MANIFEST.md`.
