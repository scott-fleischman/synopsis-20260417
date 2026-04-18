# Mark–Matthew literary dependence case study

## What this package contains

This package implements a layered comparison of Mark and Matthew using the Greek text and apparatus from the Faithlife SBLGNT repository and MorphGNT morphology/lemma data.

## Pipeline

1. Build a stable textual base and keep variant notes attached to aligned units.
2. Flag "negative-space" material that is cheap to share (very short verses, citation formulas, etc.).
3. Compute a full verse-by-verse similarity matrix.
4. Compute 3-verse contextual windows to find larger-order alignments.
5. Build a global monotonic primary chain of one-to-one verse alignments.
6. Segment that chain into 25 loose blocks and 51 tight blocks.
7. For each primary pair, generate surface and lemma-level diffs.
8. For each loose block, generate both-direction directional ledgers:
   - if Mark is prior, what operations must Matthew perform?
   - if Matthew is prior, what operations must Mark perform?
9. Recover secondary echoes that the primary chain does not use.

## High-level outputs

- Primary aligned verse pairs: 385
- Mark verses in primary chain: 385 / 673
- Matthew verses in primary chain: 385 / 1068
- Loose blocks: 25
- Tight blocks: 51
- Secondary echoes: 231

## Structural asymmetries surfaced by this run

- Total extra Matthew gap verses over Mark across block boundaries: 474
- Total extra Mark gap verses over Matthew across block boundaries: 87
- Mean primary-pair score: 0.438499
- Median primary-pair score: 0.409121

These figures do **not** settle direction by themselves. They quantify what each direction-hypothesis must explain.

## File inventory

- `data/00_source_metadata.yaml` — Source files, local copies, upstream URLs.
- `data/01_negative_space_flags.csv` — Per-verse flags for cheap/shared material: short verse, citation formula, etc.
- `data/02_verse_similarity_full.csv.gz` — Full 673 x 1068 verse similarity matrix (compressed).
- `data/03_verse_similarity_top20_mark_to_matt.csv` — Top 20 verse matches for each Mark verse.
- `data/04_verse_similarity_top20_matt_to_mark.csv` — Top 20 verse matches for each Matthew verse.
- `data/05_window3_similarity_top10_mark_to_matt.csv` — Top 10 contextual 3-verse-window matches for each Mark window.
- `data/06_window3_similarity_top10_matt_to_mark.csv` — Top 10 contextual 3-verse-window matches for each Matthew window.
- `data/07_primary_chain_pairs.csv` — Primary one-to-one monotonic Mark↔Matthew chain, one row per aligned pair.
- `data/08_primary_chain_pairs_detailed.jsonl` — Detailed pair objects with diff opcodes and variant notes.
- `data/09_loose_blocks.yaml` — 25 loose block alignments with block summaries and directional ledgers.
- `data/10_tight_blocks.yaml` — 51 tight block alignments for finer segmentation.
- `data/11_order_intervals.yaml` — Gap intervals between loose blocks, with comparative interpretation.
- `data/12_secondary_echoes.yaml` — 231 non-primary echoes: alternate local matches, nonlocal echoes, formulaic ties.
- `data/13_variants_by_primary_pair.yaml` — Apparatus notes attached to each primary pair.
- `data/14_direction_ledger_by_loose_block.yaml` — Both-direction editing hypotheses for every loose block.
- `data/15_direction_burden_totals.yaml` — Aggregate burden vectors, gap totals, and operation counts.
- `data/16_global_summary.yaml` — Global metrics, style markers, top lexical deltas, top gap intervals.
- `data/17_macro_block_table.csv` — Tabular summary of the 25 loose blocks.
- `data/18_micro_block_table.csv` — Tabular summary of the 51 tight blocks.
- `data/19_pair_diffs_flat.tsv` — Flat per-pair change log: inserted/deleted/moved lemmas and aligned texts.
- `data/20_top_lemma_deltas.yaml` — Top lexical asymmetries and replacement pairs.
- `data/21_selected_secondary_echoes.yaml` — Selected strongest examples from the secondary-echo set.
