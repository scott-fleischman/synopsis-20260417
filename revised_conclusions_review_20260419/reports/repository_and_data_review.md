# Review of current repository state against latest generated data

## Scope

Reviewed current GitHub source, conclusions, visualization source, committed `docs/` snapshot, build/test listings, and the latest generated data packages created in this thread.

## Data-analysis findings

### Strengths

- The repository is now correctly framed as a Gospel dependence and intertextuality workbench rather than just a Synoptic comparison.
- The high-priority supplement added the major missing evidence layers: Mark↔Luke, John pairwise, Gospel square, Thomas matrix, epistle dossiers, and conclusion-to-evidence navigation.
- The later generated model atlas adds the missing system-level comparison across 13 models.
- The latest data distinguishes computed, curated, and interpretive layers.

### Problems requiring correction

1. **Conclusions are stale.** The current `conclusions/CONCLUSIONS.md` does not incorporate direct Mark↔Luke, the Mark–Luke order-retention reassessment, system-model scorecard, minor-agreement catalog, or John anchor-specific burden totals.
2. **Mark↔Luke needs careful phrasing.** Mark-prior beats Luke-prior among direct-use alternatives, but direct use beats shared tradition only when shared tradition is charged for order-retention/cluster/bridge burdens.
3. **System-model conclusions are missing.** The current conclusions remain mostly pairwise; the latest data supports model-level discussion of Two-source, Farrer, Griesbach, Augustinian, proto-Mark/network, oral tradition, and John anchor models.
4. **Minor agreements need headline treatment.** The algorithmic catalog is not final, but it is a central discriminator for Q/Farrer/Griesbach debates.
5. **Variant sensitivity is too coarse.** The atlas has 2,682 variant-sensitivity rows, but many are `not_assessed_case_by_case`. This is acceptable as a registry but not as final text-critical assessment.
6. **Pericope ontology is mixed.** The atlas has a computational/anchor ontology; for publication-grade use it needs hand-curated synopsis boundaries and scholarly labels.

## Code and visualization findings

1. **Dataset switcher still excludes Mark↔Luke.** `shared.js` lists `VALID_DS = ['mm', 'ml', 'mld']`; `mkl` should be added to all reusable Synoptic views.
2. **Missing build modules.** The inspected `preprocess.py` imports `loaders_h18c`, `loaders_dir_dossiers`, and `loaders_atlas`; the inspected GitHub build directory listing did not show those modules. Either commit them or remove the imports.
3. **Docs/source mismatch.** Landing pages reference 42 visualizations and pages 36–42, but the inspected committed `docs/` listing contains pages 01–35. Raw fetches for several page-36+ URLs returned 404.
4. **Root README and landing page disagree.** Root README says six data packages / 35 views; landing page says ten packages / 42 visualizations. A single authoritative project map is needed.
5. **Visualization priority is conceptually right.** Start with claims, then Gospel square, then pairwise evidence, directional dossiers, model atlas, and audits. But the pages must actually exist and be linked from source and docs.

## Revised conclusions

See `patch/CONCLUSIONS_REVISED_20260419.md` and `data/revised_headline_claims.yaml`.
