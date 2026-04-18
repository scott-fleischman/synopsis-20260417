# Executive summary

## Scope

This package is a comprehensive Mark–Matthew case study built from the SBLGNT Greek text, SBLGNT apparatus, and MorphGNT lemmas/morphology.

## Main quantitative picture

- Primary chain pairs: 385
- Mark verses in the primary chain: 385 / 673 (57.21%)
- Matthew verses in the primary chain: 385 / 1068 (36.05%)
- Loose blocks: 25
- Tight blocks: 51
- Secondary echoes: 231

## Structural asymmetry

Across block boundaries, Matthew has **474** more non-parallel gap verses than Mark, while Mark has **87** more than Matthew.  
This does not by itself prove direction, but it means the two major directional hypotheses have different structural burdens:

- **Matthew from Mark** must explain many Matthean additions / preserved non-Markan materials.
- **Mark from Matthew** must explain many Markan omissions / non-use of Matthean materials.

Inside the aligned loose blocks, the total token counts are almost identical:

- Mark tokens inside loose blocks: 8258
- Matthew tokens inside loose blocks: 8259

So the big asymmetry is mainly **outside** the aligned core, not inside it.

## Stylistic tendencies surfaced by the aligned core

- Mark has more εὐθύς / εὐθέως in matched material: 25 vs 17
- Mark has more "kingdom of God" in matched material: 9 vs Matthew 1
- Matthew has "kingdom of heaven" where Mark has none in the matched material: 5
- Present-indicative ratio is slightly higher in Mark: 0.3639 vs Matthew 0.3314

## Strongest Matthean-only non-parallel stretches

- Matt 4:24 – Matt 7:28 (112 verses)
- Matt 9:18 – Matt 11:30 (93 verses)
- Matt 24:37 – Matt 26:3 (64 verses)
- Matt 1:1 – Matt 3:2 (50 verses)
- Matt 22:46 – Matt 23:39 (39 verses)
- Matt 8:6 – Matt 9:1 (30 verses)
- Matt 18:10 – Matt 19:3 (28 verses)
- Matt 13:35 – Matt 13:53 (19 verses)
- Matt 21:43 – Matt 22:14 (18 verses)
- Matt 20:1 – Matt 20:16 (16 verses)

## Strongest Mark-only non-parallel stretches

- Mark 4:35 – Mark 6:1 (51 verses)
- Mark 9:20 – Mark 9:41 (22 verses)
- Mark 1:23 – Mark 1:39 (17 verses)
- Mark 3:8 – Mark 3:20 (13 verses)
- Mark 16:8 – Mark 16:20 (13 verses)
- Mark 4:21 – Mark 4:30 (10 verses)
- Mark 7:30 – Mark 8:1 (9 verses)
- Mark 6:6 – Mark 6:13 (8 verses)
- Mark 9:48 – Mark 10:5 (8 verses)
- Mark 12:38 – Mark 12:44 (7 verses)

## Highest-confidence loose blocks by average pair score

- Block 4: Mark 1:22 – Mark 1:22  ||  Matt 7:29 – Matt 7:29  (avg 0.714)
- Block 1: Mark 1:3 – Mark 1:6  ||  Matt 3:3 – Matt 3:4  (avg 0.662)
- Block 22: Mark 13:1 – Mark 13:32  ||  Matt 24:1 – Matt 24:36  (avg 0.630)
- Block 9: Mark 3:31 – Mark 4:11  ||  Matt 12:46 – Matt 13:11  (avg 0.532)
- Block 17: Mark 9:42 – Mark 9:47  ||  Matt 18:6 – Matt 18:9  (avg 0.510)
- Block 10: Mark 4:14 – Mark 4:20  ||  Matt 13:18 – Matt 13:23  (avg 0.490)
- Block 5: Mark 1:40 – Mark 2:1  ||  Matt 8:2 – Matt 8:5  (avg 0.479)
- Block 20: Mark 11:21 – Mark 12:10  ||  Matt 21:20 – Matt 21:42  (avg 0.468)
- Block 18: Mark 10:6 – Mark 10:31  ||  Matt 19:4 – Matt 19:30  (avg 0.461)
- Block 6: Mark 2:5 – Mark 2:22  ||  Matt 9:2 – Matt 9:17  (avg 0.458)

## Lowest-confidence loose blocks by average pair score

- Block 11: Mark 4:31 – Mark 4:34  ||  Matt 13:31 – Matt 13:34  (avg 0.243)
- Block 8: Mark 3:21 – Mark 3:29  ||  Matt 12:23 – Matt 12:32  (avg 0.314)
- Block 15: Mark 8:2 – Mark 8:20  ||  Matt 15:32 – Matt 16:10  (avg 0.342)
- Block 2: Mark 1:8 – Mark 1:13  ||  Matt 3:11 – Matt 4:2  (avg 0.348)
- Block 24: Mark 15:2 – Mark 15:47  ||  Matt 27:11 – Matt 27:61  (avg 0.363)
- Block 13: Mark 6:14 – Mark 7:3  ||  Matt 14:2 – Matt 15:2  (avg 0.376)
- Block 7: Mark 2:23 – Mark 3:7  ||  Matt 12:1 – Matt 12:15  (avg 0.378)
- Block 14: Mark 7:9 – Mark 7:29  ||  Matt 15:3 – Matt 15:28  (avg 0.385)
- Block 25: Mark 16:6 – Mark 16:7  ||  Matt 28:6 – Matt 28:7  (avg 0.386)
- Block 3: Mark 1:15 – Mark 1:21  ||  Matt 4:17 – Matt 4:23  (avg 0.398)

## How to use the files

1. Start with `README.md`, `manifest.yaml`, and `data/16_global_summary.yaml`.
2. Open `data/17_macro_block_table.csv` and `data/09_loose_blocks.yaml` for the macro organization.
3. Open `data/11_order_intervals.yaml` for order/gap reorganization.
4. Open `data/07_primary_chain_pairs.csv` and `data/19_pair_diffs_flat.tsv` for verse-level lexical changes.
5. Open `data/08_primary_chain_pairs_detailed.jsonl` when you need opcode-level diffs.
6. Open `data/14_direction_ledger_by_loose_block.yaml` and `data/15_direction_burden_totals.yaml` for the two-direction burden analysis.
7. Open `data/13_variants_by_primary_pair.yaml` when you want the variant apparatus connected directly to the aligned verses.

## Caution

This package quantifies alignments and burdens. It does **not** encode a final theorem on direction.  
The strongest use is comparative: which direction-hypothesis must shoulder which kinds of additions, omissions, redistributions, scripturalizations, or tempo shifts in each block and across the whole book.
