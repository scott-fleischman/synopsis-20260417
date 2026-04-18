# What was missing for the Synoptic Problem including John

The missing layer was a direction-by-direction explanatory obligation model.

The previous packages supplied pairwise similarity, chains, blocks, gaps, anchors, and some burden ledgers. What remained underdeveloped was the ability to select a direction such as `Matthew used Mark` or `John used Luke` and immediately see:

1. what the target text must have changed,
2. what material the target must have omitted,
3. what material the target must have added,
4. what pericopes must have been reordered,
5. what evidence counts against the direction,
6. what the best response model would be if one still wanted to defend that direction.

## Added datasets

- `01_direction_hypotheses_registry.yaml`
- `10_synoptic_pericope_directional_change_ledger.csv`
- `14_directional_pericope_explanation_dossiers.yaml`
- `16_john_synoptic_directional_anchor_ledger.csv`
- `20_material_omission_addition_catalog_by_direction.csv`
- `30_reordering_and_displacement_catalog.csv`
- `50_primary_pair_change_diffs_all_directions.csv.gz`
- `60_contrary_evidence_and_response_models_by_direction.yaml`
- `61_support_contra_evidence_matrix.csv`

## Short answer by direction

### Matthew used Mark

This remains the strongest direct-use model. It must explain Matthean additions, discourse clustering, fulfillment additions, and occasional omission/compression of Mark. The contrary evidence is mainly that Matthew has much non-Markan material, but that is not fatal if Mark is a major source rather than the only source.

### Mark used Matthew

This is formally possible but must explain large-scale Markan non-use of Matthew: infancy, Sermon, discourse blocks, fulfillment material, and Matthean theological diction. The best defense is a Markan epitome model, but that is cumulatively costly.

### Luke used Mark

This is lower burden than Mark used Luke among direct-use models. It must explain Lukan additions, omissions, and relocations, especially infancy/travel/teaching material. A shared-tradition model must also explain dense order retention, so the revised package includes order-retention penalties.

### Mark used Luke

This reverse direction is included. It must explain Mark's omission of Luke's infancy/travel/teaching material and the de-Lukanization of style and theology. It remains higher burden than Luke used Mark.

### Matthew used Luke

This is possible locally but not favored by the masked double-tradition package. It must explain Matthean clustering, fulfillment additions, and replacement or omission of Lukan distinctive material.

### Luke used Matthew

This is possible locally and important for Farrer-type models. It must explain Lukan redistribution of Matthew's discourse material, reduction of Matthean fulfillment framing, and replacement of Matthean infancy material. The masked data does not force it.

### John used Mark / Matthew / Luke

These are now modeled anchor by anchor. Under each direct-use model, John must heavily transform Synoptic material into sign/testimony/discourse form, omit much Synoptic structure, and preserve only selected anchor details. In all three pairwise summaries, shared anchor tradition is currently lower burden than direct use.

### Reverse John directions

Mark/Matthew/Luke used John are included as completeness hypotheses. They require the Synoptic writers to condense and de-Johannize long Johannine discourse/sign material. They are not currently strong models but are now explicitly documented.
