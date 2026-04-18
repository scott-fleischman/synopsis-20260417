# Synoptic + John Directional Hypothesis Dossiers — 2026-04-18

This package adds the missing data-analysis layer for the Synoptic Problem, including John.

The purpose is to answer a directional question that ordinary similarity matrices do not answer:

> If this Gospel used that Gospel, what exactly must be explained per pericope, per gap, per reordering, and per local wording change? What evidence counts against the direction, and what is the best response model under that hypothesis?

## Directions covered

Primary directions requested:

- Matthew used Mark
- Mark used Matthew
- Luke used Mark
- Matthew used Luke
- Luke used Matthew
- John used Mark
- John used Luke
- John used Matthew

Additional key directions included for completeness:

- Mark used Luke
- Mark used John
- Matthew used John
- Luke used John
- shared Matthew–Luke sayings/tradition
- shared John/Synoptic anchor tradition
- proto-Mark/common narrative-source models
- two-source / Mark + Q-like model
- Farrer-type Luke-used-Matthew-plus-Mark model
- Griesbach/two-gospel Mark-used-Matthew-and-Luke model

## Core outputs

Start with these files:

1. `data/60_contrary_evidence_and_response_models_by_direction.yaml`
2. `data/10_synoptic_pericope_directional_change_ledger.csv`
3. `data/16_john_synoptic_directional_anchor_ledger.csv`
4. `data/20_material_omission_addition_catalog_by_direction.csv`
5. `data/30_reordering_and_displacement_catalog.csv`
6. `data/50_primary_pair_change_diffs_all_directions.csv.gz`
7. `data/61_support_contra_evidence_matrix.csv`
8. `data/62_directional_conclusion_ranking_and_missing_key_directions.yaml`

## Main conclusion

The remaining missing data layer was not another raw similarity matrix. It was a direction-by-direction explanatory-obligation layer.

The strongest current directional result remains **Matthew used Mark or a Mark-like written source**. The added Mark–Luke and morphology/penalty work supports **Luke used Mark or a Mark-like source** over the reverse among direct-use alternatives, but the Mark–Luke result requires explicit order-retention penalties against pure shared tradition. Matthew–Luke double tradition remains better treated as a shared sayings/tradition problem than as a simple one-way direct-use problem. John should be handled anchor-by-anchor; shared anchor tradition is still lower burden than a global claim that John used Mark, Matthew, or Luke.

## Reproducibility

The package includes the previous artifact snapshots used as inputs under:

`inputs/previous_artifacts/`

The build script is:

`scripts/build_directional_dossiers.py`

It regenerates the direction registry, pericope/gap/anchor/change-diff ledgers, support/contra matrix, and summary files from those input snapshots.

## Limitation

This package does not add a hand-coded critical synopsis with conventional pericope titles, nor does it produce probabilistic posterior estimates. The burden scores are audit prompts, not probabilities.
