# Synoptic Problem + John Model-Comparison Atlas

Package id: `synoptic_problem_model_atlas_20260418`

This package consolidates the prior Gospel-comparison datasets into a single expert-facing data atlas for the Synoptic Problem, including John as a first-class comparison problem. It is designed to help scholars inspect concrete data, compare models, and evaluate support/counterevidence without forcing a single conclusion.

## Scope

The atlas covers:

- Matthew ↔ Mark
- Mark ↔ Luke
- Matthew ↔ Luke, including Markan-masked double tradition
- John ↔ Mark, John ↔ Matthew, John ↔ Luke
- major system models: Markan priority, Two-source/Mark+Q, Farrer, Griesbach/Two-Gospel, Augustinian sequence, proto-Mark + sayings, oral/tradition network, John-used-Synoptics, Synoptics-used-John/John-like, and shared John/Synoptic anchor tradition.

## Package contents

- `102` copied input snapshots under `inputs/`, totaling about `62.4` MB.
- `3768` Gospel verse rows in `data/01_gospel_verse_inventory.csv`.
- `13` system models in `data/02_system_model_registry.yaml`.
- `15` direction hypotheses in `data/03_direction_hypothesis_registry.yaml`.
- `16` cells in the 4×4 Gospel direction matrix.
- `102` pericope/anchor units: `92` computational Synoptic blocks and `10` John/Synoptic anchor units.
- `1945` model/pericope obligation rows.
- `1310` material omission/addition rows mapped to models.
- `7578` order/displacement rows mapped to models.
- `6029` primary-pair wording-change rows mapped to models.
- `118` algorithmic triple-tradition minor-agreement screening rows.
- `109` Matthew–Luke Markan-masked double-tradition rows, including `60` secondary echoes.
- `2682` variant-sensitivity rows.
- `25` conclusion/evidence/counterevidence cards.

## How to use

Start with these files:

1. `data/52_system_model_comparison_scorecard.csv` — model-level overview.
2. `data/04_gospel_direction_matrix_4x4.csv` — source→target direction matrix for all four canonical Gospels.
3. `data/20_model_pericope_obligation_ledger.csv` — what each direction/model must explain per unit.
4. `data/30_minor_agreements_catalog_triple_tradition.csv` — Matthew+Luke agreements against Mark in triple-tradition alignments.
5. `data/40_double_tradition_order_catalog_markan_masked.csv` — Markan-masked Matthew–Luke sayings/order evidence.
6. `data/81_conclusion_evidence_counterevidence_cards.yaml` — balanced conclusion cards with counterevidence.
7. `data/70_variant_sensitivity_registry.csv` — variant-sensitive loci.

## Reproducibility

The package includes:

- `inputs/INPUT_INDEX.yaml` mapping input keys to copied input snapshots.
- `scripts/build_synoptic_model_atlas.py` to rebuild the main derived CSV/YAML layers from `inputs/`.
- `schemas/` JSON schemas for major row types.
- `tests/TEST_RESULTS.md` with validation checks.
- `MANIFEST.yaml` with SHA-256 hashes for all files.

## Important limitations

- The Synoptic block ontology is computational, not a fully hand-curated traditional synopsis.
- John is handled as anchor-level / low-verbatim evidence, not as a monotonic Synoptic-style chain.
- The minor-agreement catalog is an algorithmic screen, not a replacement for a hand-curated scholarly minor-agreements list.
- Model scores and burden ledgers are explanatory audits, not posterior probabilities.
- Text-critical flags identify sensitivity; they do not replace full apparatus adjudication.
- Some source-layer inputs are generated artifacts from earlier packages in this thread; this atlas declares and bundles those inputs rather than silently hiding that dependency.
