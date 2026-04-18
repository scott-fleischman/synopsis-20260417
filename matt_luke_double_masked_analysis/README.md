# Matthew-Luke masked double-tradition analysis package

This package filters Matthew-Luke comparison data after explicitly masking likely Markan material from Matthew and Luke. It then rebuilds the primary chain, blocks, secondary echoes, pair diffs, apparatus notes, and directional burden ledger on the remaining Matthew-Luke material.

## Core counts

- Matthew masked as Markan: 389 / 1068
- Luke masked as Markan: 226 / 1149
- Matthew unmasked: 679
- Luke unmasked: 923
- Masked matrix rows: 626717
- Primary chain pairs: 49
- Loose blocks: 13
- Tight blocks: 22
- Secondary echoes retained: 60

## Important files

- `data/01_markan_mask_by_verse.csv` — audit of all Matthew/Luke verses and Markan mask rules.
- `data/01_negative_space_flags.csv` — stock/common-material flags used as interpretive negative space.
- `data/02_verse_similarity_full.csv.gz` — filtered Matthew × Luke matrix after Markan masking.
- `data/03_verse_similarity_top20_matt_to_luke.csv` — top Luke candidates for each unmasked Matthew verse.
- `data/04_verse_similarity_top20_luke_to_matt.csv` — top Matthew candidates for each unmasked Luke verse.
- `data/07_primary_chain_pairs.csv` — monotonic backbone rerun on the masked matrix.
- `data/09_loose_blocks.yaml` — broader block structure.
- `data/10_tight_blocks.yaml` — stricter micro-block structure.
- `data/12_secondary_echoes.yaml` — displaced/high-score echoes after masking.
- `data/13_variants_by_primary_pair.yaml` — SBLGNT apparatus notes on primary-chain pairs.
- `data/14_direction_ledger_by_loose_block.yaml` — directional burden ledger.
- `data/19_pair_diffs_flat.tsv` — lemma/surface diffs for primary pairs and top secondary echoes.

## Caution

The Markan mask is algorithmic and auditable, not a hand-coded synopsis. Borderline cases remain visible in `data/01_markan_mask_by_verse.csv`. The directional ledger is a burden-audit aid, not a posterior-probability model.
