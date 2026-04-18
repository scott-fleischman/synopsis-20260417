# Matthew–Luke executive summary

## What this package is

A comprehensive Matthew–Luke case-study package using the same general structure as the earlier Mark–Matthew package, but expanded for a harder comparison where major material is displaced rather than simply aligned.

## Main quantitative picture

- Primary monotonic backbone: 233 one-to-one verse pairs.
- Matthew coverage in that backbone: 233 / 1068 (21.82%).
- Luke coverage in that backbone: 233 / 1149 (20.28%).
- Macro blocks: 32.
- Micro blocks: 66.
- Secondary echoes recovered outside the backbone: 1033.

## Why the backbone is intentionally sparse

The Matthew–Luke comparison is dominated by order dislocation. A single monotonic chain cannot safely absorb both Matthew's sermon/discourse clustering and Luke's different placements without forcing false local alignments. For that reason, the package keeps:

- a conservative backbone for stable local continuity, and
- a secondary-echo layer for strong nonlocal parallels.

This means the low backbone percentages are expected and should not be misread as low overall relatedness.

## Strongest signals

1. Several exact or near-exact sayings parallels appear not in the main backbone but in the secondary-echo layer because they occur far from the expected order position.
2. The secondary-echo layer therefore carries much of the classic double-tradition material.
3. The backbone still captures stable local shared narrative sequences such as John the Baptist material, temptation material, parts of the centurion tradition, and large stretches of the passion narrative.

## Directional burden ledger

The directional ledger is heuristic, not a proof. It asks what kind of editing program would have to be accepted under each direction.

Aggregate numeric strain totals:
- Matt prior hypothesis (Luke uses Matthew): overall 142.559
- Luke prior hypothesis (Matthew uses Luke): overall 75.477

These totals are driven mainly by the amount of large-scale redistribution the model must absorb, plus whether distinctive diction is being reduced or added. Because Matthew–Luke involves substantial reorderings regardless of direction, the residual burden remains high under both hypotheses.

## Selected strong secondary echoes

- Matt 7:8 ↔ Luke 11:10 | score=1.000 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 12:41 ↔ Luke 11:32 | score=1.000 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 8:20 ↔ Luke 9:58 | score=1.000 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 12:42 ↔ Luke 11:31 | score=0.943 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 12:27 ↔ Luke 11:19 | score=0.954 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 11:21 ↔ Luke 10:13 | score=0.920 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 7:7 ↔ Luke 11:9 | score=0.918 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 8:9 ↔ Luke 7:8 | score=0.919 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 6:24 ↔ Luke 16:13 | score=0.936 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 24:47 ↔ Luke 12:44 | score=0.838 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 11:22 ↔ Luke 10:14 | score=0.753 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources
- Matt 24:46 ↔ Luke 12:43 | score=0.783 | tags=strong_verbal_echo,strong_window_echo,nonlocal_reorder,multiple_sources

## Most important files to inspect first

1. `data/16_global_summary.yaml`
2. `data/07_primary_chain_pairs.csv`
3. `data/09_loose_blocks.yaml`
4. `data/11_order_intervals.yaml`
5. `data/12_secondary_echoes.yaml`
6. `data/14_direction_ledger_by_loose_block.yaml`
7. `data/19_pair_diffs_flat.tsv`

## Caution

This package is a structured data analysis artifact. It does not itself decide the Synoptic Problem. What it does do is separate:
- stable local alignment,
- large-scale order dislocation,
- lexical / lemma changes,
- variant-sensitive loci, and
- the directional burdens each hypothesis must carry.
