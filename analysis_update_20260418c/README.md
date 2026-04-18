# Synopsis data-analysis patch — 2026-04-18

This package addresses the data-analysis issues identified in the latest repository review. It does not rewrite the visual interface. It adds authoritative-number reconciliation, Mark↔Luke burden reassessment, Matthew↔Luke mask-regime robustness, John anchor-specific ledgers, Thomas curation status, epistle validation triage, apocrypha analysis-status planning, and a MorphGNT lemma audit layer.

## Key outputs

- `data/01_authoritative_numbers.yaml`
- `data/02_reproducibility_levels.yaml`
- `data/10_mark_luke_tradition_retention_audit_by_block.csv`
- `data/11_mark_luke_shared_tradition_penalty_sensitivity.csv`
- `data/12_mark_luke_direct_burden_reassessment.yaml`
- `data/20_matt_luke_mask_regime_robustness_table.csv`
- `data/22_matt_luke_double_tradition_robustness.yaml`
- `data/30_john_anchor_specific_burden_ledgers.yaml`
- `data/32_john_anchor_specific_aggregate_summary.yaml`
- `data/40_thomas_logion_matrix_with_curation_status.csv`
- `data/50_epistle_candidate_validation_sample.csv`
- `data/52_epistle_targeted_cases_morphology_audit.csv`
- `data/84_morphology_rerun_summary.yaml`
- `reports/updated_data_analysis_conclusions.yaml`

## Most important correction

The Mark↔Luke direct comparison should be reported carefully. The original direct-use comparison makes Mark-prior lighter than Luke-prior. But the original three-way ledger also gave the lowest raw burden to shared tradition. This patch adds an explicit order-retention/narrative-bridge penalty sensitivity layer. With moderate penalties, Mark-prior becomes the lowest-burden model; without those penalties, shared tradition remains lower. The conclusion should therefore be nuanced.

## Source base

This package includes MorphGNT source snapshots for Matthew, Mark, Luke, John, selected epistles, Ephesians, and Hebrews in `sources/morphgnt/`, plus copied prior artifact inputs in `inputs/previous_artifacts/`.

Generated: 2026-04-18T22:18:21.929154
