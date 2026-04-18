# Attribution and Provenance

This atlas is a derivative consolidation package. It bundles copied input snapshots from earlier generated packages and records their hashes in `data/00_source_provenance_and_input_manifest.yaml` and `MANIFEST.yaml`.

## Ultimate text/morphology sources

- SBL Greek New Testament / SBLGNT: Greek text source used in prior packages. The Faithlife repository describes it as a critically edited Greek New Testament and lists a CC BY 4.0 license.
- MorphGNT SBLGNT: morphology and lemma layer. The MorphGNT repository states that the SBLGNT text is subject to the SBLGNT EULA and that the morphological parsing and lemmatization are CC-BY-SA.
- Coptic Thomas layer: inherited from the prior Thomas package; the current atlas does not introduce automatic Coptic-Greek dependence scoring.

## Derived artifacts

The atlas consumes prior generated artifacts from this thread:
- Mark–Matthew package.
- Matthew–Luke package.
- Markan-masked Matthew–Luke package.
- John/Thomas/epistles/apocrypha package.
- High-priority missing-data supplement.
- Data-analysis patch.
- Directional-dossier package.

All such inputs are copied under `inputs/` and hashed.
