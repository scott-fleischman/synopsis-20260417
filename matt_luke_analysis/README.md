# Matthew–Luke literary dependence case study package

> *Produced by GPT-5.4 Pro under human direction (prompting only). See the repo-level README for the full authorship breakdown.*

This package mirrors the earlier Mark–Matthew package structure but expands it into a fuller multi-layer set.

## Scope

Texts analyzed:
- Matthew (SBLGNT text base + apparatus; MorphGNT lemma/morph stream)
- Luke (SBLGNT text base + apparatus; MorphGNT lemma/morph stream)

## Pipeline

1. Negative-space flagging for low-information verses and cheap-shared material proxies.
2. Full verse-by-verse similarity matrix on content lemmas and all lemmas.
3. Three-verse contextual window similarity.
4. Conservative monotonic primary chain.
5. Loose and tight block segmentation.
6. Pair-level lemma/surface diffs.
7. Variant-note attachment from the SBLGNT apparatus.
8. Directional burden ledgers in both directions.
9. Secondary-echo recovery for non-monotonic parallels.

## Important interpretation note

Primary chain is intentionally conservative and monotonic. Strong reordered material, especially in the double tradition, is expected to surface in the secondary-echo layer rather than being forced into the backbone.

That matters especially for Matthew–Luke, where reordered double-tradition material is substantial. The backbone is therefore intentionally incomplete and should be read together with the secondary-echo files.

## Package map

- `data/00_source_metadata.yaml` — source provenance and hashes
- `data/01_negative_space_flags.csv` — low-information / formulaic flags by verse
- `data/02_verse_similarity_full.csv.gz` — full Matthew × Luke score matrix
- `data/03_verse_similarity_top20_matt_to_luke.csv` — best Luke candidates for each Matthew verse
- `data/04_verse_similarity_top20_luke_to_matt.csv` — best Matthew candidates for each Luke verse
- `data/05_window3_similarity_top10_matt_to_luke.csv` — 3-verse window candidates from Matthew side
- `data/06_window3_similarity_top10_luke_to_matt.csv` — 3-verse window candidates from Luke side
- `data/07_primary_chain_pairs.csv` — conservative one-to-one monotonic backbone
- `data/08_primary_chain_pairs_detailed.jsonl` — richer pair-level records
- `data/09_loose_blocks.yaml` — macro blocks built from the backbone
- `data/10_tight_blocks.yaml` — micro blocks built from the backbone
- `data/11_order_intervals.yaml` — gap intervals between macro blocks
- `data/12_secondary_echoes.yaml` — non-monotonic or displaced strong echoes
- `data/13_variants_by_primary_pair.yaml` — apparatus notes linked to primary pairs
- `data/14_direction_ledger_by_loose_block.yaml` — hypothesis ledgers for Matt→Luke and Luke→Matt
- `data/15_direction_burden_totals.yaml` — aggregate directional strain totals
- `data/16_global_summary.yaml` — package-level summary
- `data/17_macro_block_table.csv` — flat macro summary table
- `data/18_micro_block_table.csv` — flat micro summary table
- `data/19_pair_diffs_flat.tsv` — per-pair token/lemma change summaries
- `data/20_top_lemma_deltas.yaml` — aggregate lemma insertions/deletions/replacements
- `data/21_selected_secondary_echoes.yaml` — trimmed top secondary echoes
- `MANIFEST.yaml` — hashes and sizes for all generated files

## High-level outputs

- Primary-chain pairs: 233
- Matthew verses in primary chain: 233 / 1068 (21.82%)
- Luke verses in primary chain: 233 / 1149 (20.28%)
- Loose blocks: 32
- Tight blocks: 66
- Secondary echoes: 1033

## Style and diction markers inside the matched backbone

- Matthew `τότε`: 24
- Luke `τότε`: 4
- Matthew `kingdom of God`: 1
- Matthew `kingdom of heaven`: 4
- Luke `kingdom of God`: 10
- Luke `kingdom of heaven`: 0
- Matthew present-indicative ratio: 0.3638
- Luke present-indicative ratio: 0.3023

## Pair-class distribution in the primary chain

luke_expands: 64
reordering: 84
matt_expands: 93
substitution: 113
close_match: 5
partial_overlap: 24


## Largest gap stretches (backbone gaps, not proof of uniqueness)

Matthew-side largest:
- start_ref: Matt 4:24
  end_ref: Matt 7:27
  verse_count: 111
- start_ref: Matt 24:36
  end_ref: Matt 26:2
  verse_count: 64
- start_ref: Matt 15:11
  end_ref: Matt 16:13
  verse_count: 42
- start_ref: Matt 8:5
  end_ref: Matt 9:1
  verse_count: 31
- start_ref: Matt 12:5
  end_ref: Matt 12:30
  verse_count: 26


Luke-side largest:
- start_ref: Luke 9:49
  end_ref: Luke 15:2
  verse_count: 241
- start_ref: Luke 1:32
  end_ref: Luke 2:9
  verse_count: 58
- start_ref: Luke 15:8
  end_ref: Luke 17:1
  verse_count: 57
- start_ref: Luke 2:11
  end_ref: Luke 3:3
  verse_count: 45
- start_ref: Luke 19:1
  end_ref: Luke 19:28
  verse_count: 28

