# conclusions/ — interpretive synthesis across all four packages

This directory holds **author-authored conclusions** drawn from the four analysis packages. It is the only directory in this repo that is *inference*, not data or code. Every claim here builds on specific artifacts in the other packages and cites them by path.

## Why this is a separate directory

The four analysis packages (`mark_matthew_analysis/`, `matt_luke_analysis/`, `matt_luke_double_masked_analysis/`, `john_thomas_epistles_apocrypha_analysis/`) are deliberately neutral. They produce burden ledgers, retrieval scores, and aligned pairs — never posterior probabilities or "winners." Keeping inference in a separate directory preserves that discipline: a reader who wants the data without the author's take can ignore this directory entirely, and a reader who wants the author's take knows exactly where to find it.

## What's here

- [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) — confidence table and three load-bearing findings.
- [`CONCLUSIONS.md`](CONCLUSIONS.md) — the full argument, organized as 10 sections (Mark–Matthew, Matthew–Luke, Q, John, Thomas, 1 Timothy, James, Paul/Lord's Supper, Johannine letters, apocrypha) plus overall model.
- [`data/01_confidence_table.csv`](data/01_confidence_table.csv) — machine-readable confidence table (8 rows).
- [`data/02_per_comparison_models.yaml`](data/02_per_comparison_models.yaml) — structured YAML models for Synoptic relationships and John↔Synoptics.
- [`data/03_case_snippets.yaml`](data/03_case_snippets.yaml) — structured summaries of the four high-value individual cases (1 Tim 5:18, Jas 5:12, 1 Cor 11:24, 1 John 3:13).
- [`data/04_overall_model.yaml`](data/04_overall_model.yaml) — the final `best_current_model_from_generated_data` block with methodological conclusion and strongest-findings summary.
- [`MANIFEST.yaml`](MANIFEST.yaml) — file inventory with sizes and sha256 hashes.

## Confidence scale

The scale is intentionally coarse (High / Medium-high / Medium / Low). It reflects how hard the alternative explanations are to sustain given the data in the packages — not a calibrated probability.

- **High** — the alternative explanations require materially heavier editing or coincidence burdens than the stated conclusion. A reader would need new data to overturn it.
- **Medium-high** — the conclusion is the most economical reading of what the package produces, but sibling hypotheses remain live.
- **Medium** — the conclusion is the best current model, but several competing models remain credible.
- **Low** — the package does not yet support a firm conclusion.

## Relationship to the other packages

Every claim in [`CONCLUSIONS.md`](CONCLUSIONS.md) cites a specific file in one of the four analysis packages. The citations are explicit repo-relative paths, so a reader can click through to the raw YAML or CSV and verify the claim against the data.
