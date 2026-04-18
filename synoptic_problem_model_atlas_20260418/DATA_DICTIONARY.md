# Data Dictionary

## Key files

### `data/01_gospel_verse_inventory.csv`
Verse-level Gospel inventory. Contains book, reference, chapter, verse, token counts, normalized/content tokens, and Greek text.

### `data/04_gospel_direction_matrix_4x4.csv`
A 4×4 source→target Gospel matrix. Each non-diagonal cell identifies the direction hypothesis and available burden/status information.

### `data/10_pericope_ontology_computational_and_anchor.csv`
Computational units used in the atlas. Synoptic entries are alignment blocks; John entries are anchor episodes.

### `data/20_model_pericope_obligation_ledger.csv`
Main scholarly work file. Each row states what a model/direction must explain for a pericope/anchor, plus contrary evidence and plausible response model.

### `data/21_material_omission_addition_by_model.csv`
Gap/material burden rows mapped onto system models.

### `data/22_reordering_displacement_by_model.csv`
Order/displacement rows mapped onto system models.

### `data/23_primary_pair_wording_change_diffs_by_model.csv.gz`
Verse/pair-level wording changes mapped onto system models.

### `data/30_minor_agreements_catalog_triple_tradition.csv`
Algorithmic minor-agreement screen in triple-tradition aligned verses.

### `data/40_double_tradition_order_catalog_markan_masked.csv`
Matthew–Luke non-Markan/double-tradition order and echo catalog.

### `data/52_system_model_comparison_scorecard.csv`
System-model scorecard. Interpretive synthesis, not a probability table.

### `data/70_variant_sensitivity_registry.csv`
Text-critical/variant sensitivity registry.

### `data/81_conclusion_evidence_counterevidence_cards.yaml`
Balanced conclusion cards with support, contrary evidence, and linked data files.

## Schema files

JSON schemas are in `schemas/`.
