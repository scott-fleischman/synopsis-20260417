# Executive summary

> *Revised 2026-04-19 from `revised_conclusions_review_20260419/patch/EXECUTIVE_SUMMARY_REVISED_20260419.md`. The prior version of this file (produced 2026-04-18) is superseded in full. Source prose in [`CONCLUSIONS.md`](CONCLUSIONS.md) produced by **GPT-5.4 Pro**; this summary produced by **Claude Opus 4.7**. Human role: prompting only. See the repo-level README for the full authorship breakdown.*

This revision updates the repository conclusions using all latest generated data layers: the four base pairwise packages, the reproducibility rerun (`analysis_update_20260418`), the high-priority supplement (`analysis_update_20260418b`), the Mark–Luke order-retention reassessment (`analysis_update_20260418c`), the MorphGNT lemma audit, the Synoptic+John directional dossiers (`synoptic_john_directional_dossiers_20260418`), and the Synoptic Problem model atlas (`synoptic_problem_model_atlas_20260418`).

## Revised headline findings (nine-point ladder)

1. **Matthew most likely used Mark or a Mark-like written narrative source.** Confidence: **high**. Use the rerun headline of 386 primary pairs, 27 loose blocks, and 50 tight blocks for headline prose. Burden favors Matthew-used-Mark over Mark-used-Matthew (774.87 vs. 788.66).
2. **Luke probably used Mark or a Mark-like written narrative source**, but this is weaker than the Matthew–Mark conclusion. Confidence: **medium-high** against Mark-used-Luke; **medium** against all alternatives. Direct-use burden favors Mark-prior (254.6) over Luke-prior (303.2); shared-tradition adjusts to 385.6 under moderate order-retention weights. The claim requires charging non-direct shared-tradition models for dense order retention.
3. **Matthew–Luke double tradition is best treated as a shared sayings/tradition layer.** Confidence: **medium-high**. Masked burdens are symmetric (26.446 / 26.446) and higher than common-source burden (8.86); stable across strict/medium/broad mask regimes. This supports a Q-like layer but does not prove one discrete Q document.
4. **Two-source and Farrer are the two central system-level competitors.** Two-source explains the Markan backbone plus shared sayings; Farrer avoids Q and explains minor agreements through direct Luke–Matthew contact. Neither should be declared settled by the current data. Griesbach, Augustinian, proto-Mark, and oral/tradition-network models remain possible but pay higher burdens.
5. **John is best modeled as shared anchor/passion/sign tradition**, not global direct dependence on Mark, Matthew, or Luke. Shared anchor tradition wins at every anchor on every John↔Synoptic pair (10/10, 10/10, 9/9). Local direct use remains possible case by case.
6. **Minor agreements are a central unresolved discriminator.** The atlas contains 118 algorithmic minor-agreement rows, 21 high-strength, but the catalog requires hand curation before strong model claims.
7. **Thomas is a curated sayings-network witness.** 116 logia, 46 curated canonical parallels, only 3 directional-claim-ready. No automatic Greek–Coptic dependence score is currently available.
8. **Epistle–Gospel parallels are case-specific.** 1 Tim 5:18 / Luke 10:7 remains the strongest Luke-like saying case; 1 Cor 11 / Luke 22 should be treated as liturgical/formula tradition; James reflects Jesus tradition without demonstrated direct Matthew/Luke use.
9. **Apocrypha beyond Thomas remains inventory/roadmap only.** Gospel of Peter and passion apocrypha flagged as highest-value next test cases.

## Three load-bearing findings

1. **Matthew's dependence on Mark (or a Mark-like source)** is the strongest individual directional conclusion. Under Matthew-from-Mark, the editing program is coherent; under Mark-from-Matthew it requires repeated omission of major Matthean blocks — a heavier cumulative burden.

2. **Luke's dependence on Mark is now directly testable** through the 18b Mark↔Luke package. Mark-prior beats Luke-prior among direct-use alternatives (254.6 vs. 303.2). But the result is conditional on an order-retention penalty against shared-tradition models — the unpenalized three-way ledger preferred shared tradition (164.1). This is an interpretive choice, not a purely computed result.

3. **Minor agreements are now headline evidence, not a footnote.** With 118 rows (21 high-strength) now catalogued, the Two-source / Farrer / Griesbach debate can no longer be resolved by pairwise backbone evidence alone. The catalog is algorithmic screening — not a final scholarly list — but it is the single most important discriminator now visible in the repository.

## The shape of the field

The early Christian textual field is not one tree. It is a mixed network:

- one strong written narrative backbone around Mark (used by both Matthew and Luke);
- a sayings/tradition layer behind Matthew–Luke double tradition;
- shared passion and sign traditions overlapping John;
- epistolary reuse of fixed Jesus sayings and liturgical formulas.

Different questions need different models — an order-sensitive literary-dependence model for Mark–Matthew and Mark–Luke, a sayings-source model for Matthew–Luke double tradition, anchor-based transformation analysis for John, sayings-network analysis for Thomas, formula/saying detection plus burden analysis for James and the epistles, and a system-level burden profile across 13 named models (not a winner-takes-all ranking) for the Synoptic Problem as a whole.

## Critical methodological note

Every burden score in this repository is an **audit prompt, not a posterior probability**. Two models with different burden sums are *not* claimed to have different Bayesian posteriors; they are claimed to commit defenders to different explanatory obligations. The model atlas makes those obligations explicit so specialists can inspect, contest, or revise them.

See [`CONCLUSIONS.md`](CONCLUSIONS.md) for the full argument and [`data/05_revised_headline_claims.yaml`](data/05_revised_headline_claims.yaml) for the machine-readable claim cards.
