# Revised executive summary

This revision updates the repository conclusions using all latest generated data layers: the reproducibility rerun, high-priority supplement, Mark–Luke order-retention reassessment, MorphGNT lemma audit, Synoptic+John directional dossiers, and Synoptic Problem model atlas.

## Revised headline findings

1. **Matthew most likely used Mark or a Mark-like written narrative source.** Confidence: high. Use the rerun headline of 386 primary pairs, 27 loose blocks, and 50 tight blocks for headline prose.
2. **Luke probably used Mark or a Mark-like written narrative source**, but this is weaker than the Matthew–Mark conclusion. Confidence: medium-high against Mark-used-Luke; medium against all alternatives. The claim requires charging non-direct shared-tradition models for dense order retention.
3. **Matthew–Luke double tradition is best treated as a shared sayings/tradition layer.** Confidence: medium-high. This supports a Q-like layer but does not prove one discrete Q document.
4. **Two-source and Farrer are the two central system-level competitors.** Two-source explains the Markan backbone plus shared sayings; Farrer avoids Q and explains minor agreements through direct Luke-Matthew contact. Neither should be declared settled by the current data.
5. **John is best modeled as shared anchor/passion/sign tradition**, not global direct dependence on Mark, Matthew, or Luke. Local direct use remains possible case by case.
6. **Minor agreements are a central unresolved discriminator.** The atlas contains 118 algorithmic minor-agreement rows, 21 high-strength, but the catalog requires hand curation before strong model claims.
7. **Thomas is a curated sayings-network witness.** No automatic Greek-Coptic dependence score is currently available.
8. **Epistle-Gospel parallels are case-specific.** 1 Tim 5:18 / Luke 10:7 remains the strongest Luke-like saying case; 1 Cor 11 / Luke 22 should be treated as liturgical/formula tradition.
9. **Apocrypha beyond Thomas remains inventory/roadmap only.**

## Repository implementation issues found during review

- The committed `conclusions/CONCLUSIONS.md` is stale relative to the latest atlas/directional data.
- `visualizations/assets/shared.js` still restricts the shared Synoptic dataset switcher to `mm`, `ml`, and `mld`; it does not include `mkl`.
- `visualizations/build/preprocess.py` imports `loaders_h18c`, `loaders_dir_dossiers`, and `loaders_atlas`, but those files are not visible in the committed `visualizations/build/` listing inspected during this review.
- `visualizations/index.html` and `docs/index.html` reference 42 visualization pages and pages 36–42, but the committed `docs/` listing inspected here shows only pages 01–35; direct raw fetches for pages 36, 39, and 41 returned 404.
- The current root README still describes six data packages and 35 browser views, while the landing page describes ten analysis packages and 42 visualizations. Consolidate the authoritative count.

## Recommended repo action

Commit this revision as a new conclusions layer, rebuild the visualizations after adding the missing loader modules and page files, and ensure every conclusion card links to both supporting and limiting evidence.
