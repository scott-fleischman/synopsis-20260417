# Robustness summary

## Mark–Matthew

Primary chain size across threshold/gap grid is recorded in
`reruns/mark_matthew_rerun_robust/data/23_sensitivity_score_grid.csv`.

Default run:
- threshold = 0.25
- gap penalty = 0.05
- pairs = 386

## Matthew–Luke masked

Mask regimes:
- strict: Matthew 337, Luke 173
- medium: Matthew 387, Luke 232
- broad: Matthew 431, Luke 268

Primary-chain counts vary across regimes and thresholds; see
`reruns/matt_luke_double_masked_rerun_robust/data/17_mask_regime_sensitivity.yaml`.

## JTEA

The patch does not over-claim corpus-wide reruns for Thomas/apocrypha. Instead it improves
classification of existing evidence:

- automatic retrieval support
- philological case strength
- formula risk