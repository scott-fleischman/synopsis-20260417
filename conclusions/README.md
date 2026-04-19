# conclusions/ — interpretive synthesis across all ten packages

> *Revised 2026-04-19 to reflect the `revised_conclusions_review_20260419` package. The prose argument (`CONCLUSIONS.md`, `EXECUTIVE_SUMMARY.md`) was produced by **GPT-5.4 Pro**; the machine-readable extracts in `data/` and this README were produced by **Claude Opus 4.7**. Human role: prompting only. See the repo-level README for the full authorship breakdown.*

This directory holds **LLM-authored conclusions** drawn from the ten analysis packages. It is the only directory in this repo that is *inference*, not data or code. Every claim here builds on specific artifacts in the other packages and cites them by path.

## Why this is a separate directory

The ten analysis packages (`mark_matthew_analysis/`, `matt_luke_analysis/`, `matt_luke_double_masked_analysis/`, `john_thomas_epistles_apocrypha_analysis/`, `analysis_update_20260418/`, `analysis_update_20260418b/`, `analysis_update_20260418c/`, `synoptic_john_directional_dossiers_20260418/`, `synoptic_problem_model_atlas_20260418/`, plus the MorphGNT lemma supplement) are deliberately neutral. They produce burden ledgers, retrieval scores, aligned pairs, obligation rosters, and variant-sensitivity flags — never posterior probabilities or "winners." Keeping inference in a separate directory preserves that discipline: a reader who wants the data without the author's take can ignore this directory entirely, and a reader who wants the author's take knows exactly where to find it.

## What's here

- [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) — nine-point revised confidence ladder and three load-bearing findings.
- [`CONCLUSIONS.md`](CONCLUSIONS.md) — the full revised argument, organized as 9 sections plus methodological conclusion and overall model.
- [`data/01_confidence_table.csv`](data/01_confidence_table.csv) — machine-readable confidence table (12 rows, covering the nine-point ladder plus the 1 Cor/Luke liturgical-formula caution and the Q-as-discrete-document question).
- [`data/02_per_comparison_models.yaml`](data/02_per_comparison_models.yaml) — structured YAML models for Synoptic (Mark–Matthew, Mark–Luke, Matthew–Luke double tradition) and John↔Synoptics relationships, plus the six system-level models.
- [`data/03_case_snippets.yaml`](data/03_case_snippets.yaml) — structured summaries of the four high-value individual cases (1 Tim 5:18, Jas 5:12, 1 Cor 11:24, 1 John 3:13).
- [`data/04_overall_model.yaml`](data/04_overall_model.yaml) — the final `current_best_model_family` block with burden evidence, system-level ranking, methodological conclusion, and strongest-findings summary.
- [`data/05_revised_headline_claims.yaml`](data/05_revised_headline_claims.yaml) — nine machine-readable claim cards with three-axis confidence (retrieval · interpretive · directional), supporting evidence, counterevidence/limits, best response model, and explicit revision notes against the prior 2026-04-18 conclusions.
- [`data/05_revised_headline_claims.csv`](data/05_revised_headline_claims.csv) — flat version of the same claim cards.
- [`MANIFEST.yaml`](MANIFEST.yaml) — file inventory with sizes and sha256 hashes.

## Revision history

- **2026-04-19 (current).** Superseded the 2026-04-18 conclusions in full, following the `revised_conclusions_review_20260419` review. Promoted Mark↔Luke to its own rank, added the Luke-used-Mark order-retention caveat, separated "shared sayings/tradition" from "discrete Q document" more sharply, added Farrer as a live no-Q alternative, added minor agreements to headline status, and added an explicit system-level model ranking across 13 named models as rank 4.
- **2026-04-18 (superseded).** Original eight-point confidence table driven by the four base pairwise packages.

## Confidence scale

The scale is intentionally coarse (High / Medium-high / Medium / Low). It reflects how hard the alternative explanations are to sustain given the data in the packages — not a calibrated probability.

- **High** — the alternative explanations require materially heavier editing or coincidence burdens than the stated conclusion. A reader would need new data to overturn it.
- **Medium-high** — the conclusion is the most economical reading of what the package produces, but sibling hypotheses remain live.
- **Medium** — the conclusion is the best current model, but several competing models remain credible.
- **Low** — the package does not yet support a firm conclusion.

Revised claim cards in [`data/05_revised_headline_claims.yaml`](data/05_revised_headline_claims.yaml) additionally carry **three-axis** confidence (retrieval / interpretive / directional), so a reader can see whether a claim's uncertainty is driven by retrieval breadth, interpretive judgment, or directional evidence.

## Critical methodological note

Every burden score cited in the conclusions is an **audit prompt, not a posterior probability**. Two models with different burden sums are *not* claimed to have different Bayesian posteriors; they are claimed to commit defenders to different explanatory obligations. A defender may legitimately argue that a particular high-burden obligation is acceptable under a specific model extension — the atlas makes those obligations explicit so that argument can be made in the open.

## Relationship to the other packages

Every claim in [`CONCLUSIONS.md`](CONCLUSIONS.md) cites a specific file in one of the ten analysis packages. The citations are explicit repo-relative paths, so a reader can click through to the raw YAML or CSV and verify the claim against the data.
