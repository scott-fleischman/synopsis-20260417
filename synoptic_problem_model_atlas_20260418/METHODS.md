# Methods

## Design goal

This atlas is model-first. Instead of asking only whether two passages are similar, it asks what each direction or system model must explain: preserved order, displaced order, omitted material, added material, wording changes, minor agreements, double-tradition order, John/Synoptic anchors, and text-critical sensitivity.

## Evidence layers

1. **Source-derived verse inventory.** Gospel verse rows inherit normalized/tokenized Greek text from the prior canonical units layer.
2. **Pairwise chain/block data.** Mark–Matthew, Mark–Luke, Matthew–Luke, and Markan-masked Matthew–Luke use previous primary-chain/block outputs.
3. **Pericope ontology.** Synoptic blocks are computational alignment blocks. John units are anchor dossiers. The ontology is intentionally transparent about the difference.
4. **Direction hypotheses.** Each source→target direction receives support, contrary evidence, and response-model obligations.
5. **System models.** Larger models are represented as bundles of direction hypotheses plus unresolved burdens.
6. **Minor agreements.** The catalog is computed where a Mark verse has aligned Matthew and Luke primary-chain partners. It records Matthew+Luke shared content tokens absent from Mark and Mark content tokens omitted by both.
7. **Double tradition.** The Markan-masked Matthew–Luke layer separates primary monotonic pairs from secondary/nonlocal echoes.
8. **John.** John is analyzed through anchor-level transformation ledgers rather than Synoptic-style monotonic chains.
9. **Variants.** Variant markers and attached apparatus notes are collected into a sensitivity registry.

## Burden and model score interpretation

Burden values are audit scores, not probabilities. A lower burden score indicates that the coded explanatory obligations are lower under that model or direction in the current framework. Burdens must be read with the linked qualitative contrary evidence.

## Computed vs curated

Files contain explicit provenance/objectivity notes where relevant. The atlas distinguishes:

- computed data,
- inherited computed data,
- curated registries,
- interpretive model definitions,
- expert-facing conclusion cards.

## Rebuild

Run:

```bash
python scripts/build_synoptic_model_atlas.py
```

from the package root. The script uses only files under `inputs/`.
