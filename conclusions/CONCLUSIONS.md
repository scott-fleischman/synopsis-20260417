# Conclusions from the generated packages

> *Revised 2026-04-19 from `revised_conclusions_review_20260419/patch/CONCLUSIONS_REVISED_20260419.md`. The prior version of this file (produced 2026-04-18) is superseded in full. Prose produced by **GPT-5.4 Pro** under human direction (prompting only); machine-readable extracts in `data/` produced by **Claude Opus 4.7**. See the repo-level README for the full authorship breakdown.*

These are LLM-authored interpretive conclusions drawn from all ten analysis packages — the four base pairwise packages, the three reproducibility/supplement/patch packages (`analysis_update_20260418`, `analysis_update_20260418b`, `analysis_update_20260418c`), the directional-dossiers package (`synoptic_john_directional_dossiers_20260418`), and the system-level model atlas (`synoptic_problem_model_atlas_20260418`). They are synthesis, not automated pipeline output. The underlying data supports these claims at the stated confidence levels; the inferences themselves are the reader's.

## Why this file was revised

The prior version of this file was written before two major evidence layers were added to the repository:

1. The **directional-obligation dossiers** (`synoptic_john_directional_dossiers_20260418/`) — twelve pairwise directional hypotheses with per-direction required explanations, contrary evidence, and best-response models.
2. The **Synoptic Problem model atlas** (`synoptic_problem_model_atlas_20260418/`) — 13 named system-level models scored against a single shared obligation ledger (1,945 pericope obligations), 118 minor agreements, 109 double-tradition order cases, and 2,682 variant-sensitivity flags.

The prior conclusions therefore (a) underrepresented direct Mark↔Luke, (b) did not incorporate the direction-by-direction obligation dossiers, (c) did not include the 13-model system scorecard, and (d) did not give minor agreements or model-level Farrer/Two-source/Griesbach tradeoffs enough prominence. The revised conclusions below treat the latest generated atlas as the most complete evidence layer, while keeping clear boundaries between **computed data**, **curated registries**, and **interpretive synthesis**.

## Headline conclusions (nine-point ladder)

| Rank | Claim | Confidence | Main caveat |
|---:|---|---|---|
| 1 | Matthew most likely used Mark or a Mark-like written narrative source. | High | Stronger as Mark-like source priority than canonical-Mark identity. |
| 2 | Luke probably used Mark or a Mark-like written narrative source. | Medium-high vs Mark-used-Luke; medium against all alternatives | Requires order-retention penalties against non-direct shared-tradition accounts. |
| 3 | Matthew–Luke double tradition is better modeled as shared sayings/tradition than simple one-way copying. | Medium-high | Supports a Q-like layer, not necessarily one discrete recoverable Q document. |
| 4 | The strongest system-level family is Markan priority plus a non-Markan sayings/tradition layer. | Medium | Farrer remains the strongest no-Q direct-contact alternative. |
| 5 | John shares anchor traditions with the Synoptics, but global direct Gospel-to-Gospel dependence is not currently lowest-burden. | Medium | Local direct use remains possible anchor by anchor. |
| 6 | Minor agreements are a central unresolved discriminator. | Medium | Current catalog is algorithmic screening, not a hand-curated final list. |
| 7 | Thomas is a curated sayings-network witness, not a proven derivative of one canonical Gospel. | Medium | No automatic Greek–Coptic dependence score exists yet. |
| 8 | Epistle–Gospel parallels must be handled case by case. | Case-specific | 1 Tim 5:18 / Luke 10:7 is strong; liturgical/formula cases require caution. |
| 9 | Apocrypha beyond Thomas remains inventory/roadmap. | Low | No firm dependence conclusions yet. |

Machine-readable form: [`data/05_revised_headline_claims.yaml`](data/05_revised_headline_claims.yaml).

## 1. Matthew used Mark or a Mark-like source

The strongest directional conclusion remains Matthew's dependence on Mark or a Mark-like written narrative source. The reproducibility-patch rerun headline is **386 primary pairs, 27 loose blocks, and 50 tight blocks**. The current burden reference still favors Matthew-used-Mark over Mark-used-Matthew (**774.87 vs. 788.66**; see [`synoptic_john_directional_dossiers_20260418/data/04_direct_use_burden_by_direction.csv`](../synoptic_john_directional_dossiers_20260418/data/04_direct_use_burden_by_direction.csv)).

The conclusion should be phrased carefully: the data supports a **Mark-like source very close to Mark**, not necessarily the exact canonical Mark text in every detail.

### Supporting evidence

- Large continuous Mark–Matthew narrative backbone. See [`mark_matthew_analysis/data/16_global_summary.yaml`](../mark_matthew_analysis/data/16_global_summary.yaml) and [`analysis_update_20260418/data/16_mm_global_summary.yaml`](../analysis_update_20260418/data/16_mm_global_summary.yaml).
- Asymmetric gap pattern: Matthew contains far more non-parallel material outside the aligned Markan core (474 extra Matt gap verses vs. 87 extra Mark gap verses). See [`mark_matthew_analysis/data/14_direction_ledger_by_loose_block.yaml`](../mark_matthew_analysis/data/14_direction_ledger_by_loose_block.yaml).
- Coherent Matthean redactional explanation: expansion, discourse grouping, fulfillment citation, infancy/genealogy, and theological reframing.
- Reverse Mark-from-Matthew model requires repeated omission of major Matthean material (Sermon on the Mount, Matt 4:24–7:28, Matt 9:18–11:30, Matt 24:37–26:3, Matt 1:1–3:2).
- The Matthew-from-Mark model can accept Matthew's non-Markan material as additional sources/traditions without destabilizing the Markan backbone.

### Counterevidence and limits

- Matthew contains major non-Markan material; Mark alone cannot explain Matthew.
- Some local Markan vividness or roughness can be argued secondary in isolated passages.
- Some agreements may be mediated by shared tradition rather than direct copying.
- Variant sensitivity is still not assessed case by case for all loci; see the atlas's 2,682-row variant-sensitivity registry.

### Best current response model

> Matthew used a Mark-like written narrative source and supplemented it with sayings, fulfillment, infancy, and discourse traditions.

## 2. Luke used Mark or a Mark-like source

The direct Mark↔Luke package closes a major earlier gap. It found **183 primary-chain pairs, 35 loose blocks, 76 tight blocks, and 140 secondary echoes**. The direct-use burden favors Mark-prior/Luke-used-Mark over Mark-used-Luke: **254.6466 vs. 303.1966**. See [`analysis_update_20260418b/`](../analysis_update_20260418b/) for the pairwise package and [`synoptic_john_directional_dossiers_20260418/data/04_direct_use_burden_by_direction.csv`](../synoptic_john_directional_dossiers_20260418/data/04_direct_use_burden_by_direction.csv) for the direction comparison.

However, the conclusion needs a caveat. The unpenalized three-way ledger favored **shared narrative/oral tradition at 164.1468**. Only after applying order-retention, cluster-density, and narrative-bridge penalties does the adjusted shared-tradition burden rise above Mark-prior in the moderate penalty model: **385.6134 vs. 254.6466** (Mark-prior wins in **211 of 245** grid combinations). See [`analysis_update_20260418c/`](../analysis_update_20260418c/).

### Supporting evidence

- Direct Mark↔Luke alignment exists and is substantial (183 primary-chain pairs).
- Mark-prior is lower burden than Luke-prior among direct-use alternatives (254.6466 vs. 303.1966).
- The MorphGNT lemma audit strengthens Mark↔Luke local alignment rather than weakening it (surface mean 0.4042 → lemma mean 0.4836; lemma improves/retains on 153/183 pairs).
- Shared-tradition models must explain retained narrative order and bridge material, not merely similar episodes.

### Counterevidence and limits

- Mark↔Luke is less decisive than Mark↔Matthew.
- Unpenalized shared tradition initially looks cheaper (164.15) than either direct-use direction.
- Luke has large non-Markan material and meaningful redactional reordering.
- The Mark-prior conclusion depends on whether dense narrative order retention should be charged as a burden against non-direct tradition — an analytical choice rather than a purely computed result.

### Best current response model

> Luke used Mark or a Mark-like narrative source selectively, while also drawing on other traditions/sources and reorganizing material for Lukan literary and theological aims.

## 3. Matthew–Luke double tradition: shared sayings/tradition, not simple direct copying

After Markan masking, the retained Matthew–Luke material behaves unlike Mark–Matthew or Mark–Luke narrative dependence. It is sayings-heavy, displaced, and partly nonlocal. The earlier masked ledger favored common source/oral tradition over either direct direction (**common source 8.86 vs. Luke-uses-Matthew 26.446 vs. Matthew-uses-Luke 26.446**), and the later mask-regime work preserved the qualitative conclusion across strict / medium / broad regimes (pair counts 60–76 / 58–71 / 57–69). See [`matt_luke_double_masked_analysis/data/15_direction_burden_totals.yaml`](../matt_luke_double_masked_analysis/data/15_direction_burden_totals.yaml) and [`analysis_update_20260418c/`](../analysis_update_20260418c/) for the robustness sweep.

This supports a **Q-like sayings/tradition layer**, but not automatically a single recoverable Q document. The atlas double-tradition order layer records **49 primary rows and 60 secondary/nonlocal rows**, making displacement central to the question; see [`synoptic_problem_model_atlas_20260418/data/40_double_tradition_order_catalog.csv`](../synoptic_problem_model_atlas_20260418/data/40_double_tradition_order_catalog.csv).

### Supporting evidence

- Masked direct-use burdens were symmetric and higher than common-source/oral burden.
- The double-tradition order catalog contains many nonlocal/secondary rows.
- The material is more sayings-like than narrative-chain-like.
- Simple Matthew-used-Luke or Luke-used-Matthew is not forced by the current data.
- The strongest double-tradition echoes are the kind of material that can circulate as fixed sayings: Matt 7:7–11 / Luke 11:9–13, Matt 8:20 / Luke 9:58, Matt 12:41–42 / Luke 11:31–32, Matt 6:24 / Luke 16:13, Matt 6:9–13 / Luke 11:2–4, Matt 23:37–39 / Luke 13:34–35.

### Counterevidence and limits

- **Farrer remains viable**: Luke-Matthew contact can explain minor agreements without a Q document.
- A direct-use model may work if it supplies a strong editorial model for redistribution.
- The Markan mask is an analytical choice and needs continued sensitivity audit.
- Q as a discrete document requires more than shared sayings/tradition evidence.

### Best current response model

> A shared sayings/tradition layer is the lowest-burden representation of the masked material. Two-source and Farrer remain the key competing system-level explanations.

## 4. System-level model ranking

The project should no longer present only pairwise conclusions. The model atlas adds **13 system-level models** and makes clear that each model solves some problems while paying different burdens. See [`synoptic_problem_model_atlas_20260418/data/01_system_model_registry.yaml`](../synoptic_problem_model_atlas_20260418/data/01_system_model_registry.yaml) and [`synoptic_problem_model_atlas_20260418/data/52_system_model_comparison_scorecard.csv`](../synoptic_problem_model_atlas_20260418/data/52_system_model_comparison_scorecard.csv).

### Revised system-level assessment

- **Best-supported family:** Markan priority plus a shared non-Markan sayings/tradition layer.
- **Two-source / Mark + Q-like source:** strong if Q means a shared sayings/tradition layer; less certain if Q means one discrete recoverable document.
- **Farrer / Mark + Matthew → Luke:** strongest no-Q direct-contact alternative. Its chief burden is explaining Lukan de-Mattheanization and redistribution of sayings.
- **Griesbach / Two-Gospel:** possible but high burden because Mark must omit/compress large Matthean and Lukan material.
- **Augustinian sequence:** high burden because Mark-from-Matthew remains costly.
- **Proto-Mark + sayings:** plausible lost-source/network model, but it pays reconstruction burden.
- **Oral/tradition network:** good for sayings and John anchors, weak for dense ordered Synoptic narrative unless order-retention is explained.

**The model scorecard should be presented as a burden profile, not a probability ranking.** Every burden score in the atlas is an audit prompt, not a posterior probability. Two models with different burden sums are *not* claimed to have different Bayesian posteriors; they are claimed to commit defenders to different explanatory obligations.

## 5. John and the Synoptics

John should be treated through **anchor-specific transformation analysis**, not a Synoptic chain model.

The latest anchor-specific ledgers favor shared anchor tradition for all three pairs; shared anchor tradition wins at *every* anchor on *every* pair (10/10, 10/10, 9/9):

| Pair | John-used-Synoptic | Synoptic-used-John | Shared anchor tradition | Independent convergence |
|---|---:|---:|---:|---:|
| John ↔ Mark | 59.741 | 64.041 | **23.5** | 111.0 |
| John ↔ Matthew | 55.862 | 60.162 | **24.8** | 119.5 |
| John ↔ Luke | 58.598 | 61.698 | **20.8** | 91.6 |

See [`analysis_update_20260418c/`](../analysis_update_20260418c/) and [`synoptic_john_directional_dossiers_20260418/data/07_john_anchor_three_way_comparison.csv`](../synoptic_john_directional_dossiers_20260418/data/07_john_anchor_three_way_comparison.csv).

### Supporting evidence

- John shares important passion/sign anchors with the Synoptics (sword / high priest's servant / ear in the arrest scene; garment division and lots; Peter's denial structure; feeding and walking-on-water clusters; anointing and "poor you always have" material; triumphal-entry acclamation).
- Pure independence is implausibly cheap for several specific clusters.
- Shared anchor tradition explains the overlap without forcing continuous Synoptic order.

### Counterevidence and limits

- Some anchors may still be local direct-use cases.
- The anchor ledger is partly interpretive.
- John heavily transforms chronology, discourse, symbolism, and narrative structure.
- Reverse Synoptic-use-of-John models are possible only with substantial de-Johannization/compression burden.

### Best current response model

> Shared passion/sign/anchor tradition, with local direct dependence evaluated anchor by anchor.

## 6. Minor agreements

Minor agreements now need **headline status**. The atlas adds **118 triple-tradition minor-agreement rows, including 21 high-strength rows**. These are important because they discriminate among Two-source, Farrer, Griesbach, shared-source, and harmonization explanations. See [`synoptic_problem_model_atlas_20260418/data/30_minor_agreements_catalog.csv`](../synoptic_problem_model_atlas_20260418/data/30_minor_agreements_catalog.csv).

The current catalog is an **algorithmic screen, not a final hand-curated scholarly list**. It should not decide the model by itself, but it should constrain the discussion. Minor agreements can result from direct contact, shared non-Markan source, scribal harmonization, coincidence, or redactional similarity — the catalog does not itself adjudicate among these.

### Best current response model

> Use the minor-agreement catalog as a discriminator dashboard: it strengthens direct-contact alternatives (especially Farrer) but does not itself decide Farrer vs. Two-source vs. Griesbach.

## 7. Thomas

Thomas remains a sayings-network witness. The matrix contains **116 logia and 46 curated canonical parallels**. Current data does not provide automatic Coptic–Greek dependence scoring, so the conclusion must remain logion-level and cautious. 18c's curation-status annotations confirm the consequences: of 46 curated parallels, only **3 are directional-claim-ready**; the remaining 43 are sayings-network witnesses (28 "overlapping tradition, uncertain direction"; 14 "shared sayings or parable tradition"; 4 "possible synoptic influence or harmonization"). See [`analysis_update_20260418b/`](../analysis_update_20260418b/) for the matrix and [`analysis_update_20260418c/`](../analysis_update_20260418c/) for the curation layer.

The strongest-looking parallels (sower; mustard seed; banquet excuses; wicked tenants / rejected stone; Caesar's coin; lost sheep; treasure hidden in field; pearl; inheritance divider; womb / breasts blessing; rest / easy yoke) make pure independence less plausible, but cannot by themselves decide direction.

### Best current response model

> Logion-by-logion sayings-network analysis rather than corpus-level dependence.

## 8. Epistles and Gospel/Jesus traditions

Epistle–Gospel cases should be presented as **case dossiers, not global dependence claims**.

- **1 Tim 5:18 / Luke 10:7** remains the strongest non-Gospel case. The exact normalized Greek run `ο εργατης του μισθου αυτου` matches Luke's μισθός form, not Matthew's worker-worthy-of-food form. Best read as **knowledge of a Luke-like worker/wages saying**; need not prove the final canonical Gospel of Luke. See [`john_thomas_epistles_apocrypha_analysis/data/07_targeted_case_studies.yaml`](../john_thomas_epistles_apocrypha_analysis/data/07_targeted_case_studies.yaml).
- **James** likely reflects Jesus tradition, especially in the oath material (Jas 5:12 / Matt 5:34–37), but direct Matthew/Luke dependence is not demonstrated. Shared oral or written catechetical tradition has lower burden.
- **Paul/Luke eucharistic overlap** (1 Cor 11:24 / Luke 22:19, six-token run `τουτο ποιειτε εις την εμην αναμνησιν`) should be treated as **liturgical/formula tradition** unless additional directional evidence is supplied. This is a crucial negative-space control: long exact agreement does not always mean one canonical text copied the other.
- **Johannine letters / Gospel of John overlap** (e.g., 1 John 3:13 / John 15:18–19) is best treated as **intra-corpus idiolectal continuity** (shared Johannine school, discourse world, or compositional environment), not single-verse proof of direction.

Across the top-500 epistle candidate pool, 18c reports **166 high / 17 medium / 317 low** formula-risk rows and classes **59 uncertain / 41 strong-low-formula / 26 scriptural-formula / 18 moderate / 13 targeted-known / 3 high-formula-needs-review**.

### Best current response model

> Three-axis case grading: retrieval support, philological strength, and formula risk. 1 Timothy high; Paul/Luke and James within tradition/formula categories.

## 9. Apocrypha beyond Thomas

No firm conclusion. Gospel of Peter, Protevangelium of James, Infancy Thomas, and Gospel of Nicodemus / Acts of Pilate are future ingestion targets. Current apocrypha data is **inventory/roadmap only**. 18c's analysis-status note reconfirms "not a completed primary-text analysis layer"; see [`john_thomas_epistles_apocrypha_analysis/data/12_apocrypha_inventory_from_mr_james.csv`](../john_thomas_epistles_apocrypha_analysis/data/12_apocrypha_inventory_from_mr_james.csv).

Gospel of Peter and passion apocrypha are probably the highest-value next test cases, because passion material has dense shared narrative detail. Infancy and childhood gospels are also valuable, but they require a different model because they often expand into narrative gaps rather than directly rewriting canonical pericopae.

## Final revised model

```yaml
current_best_model_family:
  synoptic_narrative_backbone:
    model: Markan priority / Mark-like written source
    confidence:
      Matthew_used_Mark_like: high
      Luke_used_Mark_like: medium_high_with_caveat
  matthew_luke_non_markan_material:
    model: shared sayings/tradition layer
    confidence: medium_high
    q_document_claim: medium_low_without_further_argument
    strongest_alternative: Farrer / Luke used Matthew plus Mark
  john:
    model: shared anchor/passion/sign tradition
    confidence: medium
    local_direct_use: possible_case_by_case
  minor_agreements:
    status: unresolved_central_discriminator
    catalog_state: algorithmic_screen_not_hand_curated
  thomas:
    model: sayings-network witness
    confidence: medium_for_overlap_low_for_direction
    directional_claim_ready_logia: 3_of_46_curated_parallels
  epistles:
    model: case-by-case fixed sayings / formula / tradition analysis
    strongest_case: 1Tim 5:18 / Luke 10:7
    liturgical_caution: 1Cor 11 / Luke 22
  apocrypha:
    model: inventory_only_currently
    next_priority: Gospel of Peter, passion apocrypha
```

## The main methodological conclusion

The generated data argues against using one method for all these texts:

- For **Mark–Matthew**, an order-sensitive literary-dependence model works well.
- For **Mark–Luke**, an order-sensitive direct-use model is lowest-burden **once shared tradition is fairly charged for order retention** — not before.
- For **Matthew–Luke double tradition**, a sayings-source/tradition model works better than a single linear order-chain model.
- For **John**, the right model is anchor-based transformation analysis.
- For **Thomas**, the right model is sayings-network analysis.
- For **James and the epistles**, the right model is formula/saying detection plus burden analysis, because exact wording often disappears while conceptual structure remains.
- For **minor agreements**, the right treatment is a curated discriminator dashboard — not an input to a single model's posterior.
- At the **system level**, the right frame is a burden profile across 13 named models — not a winner-takes-all ranking.

So the core conclusion is:

> The early Christian textual field is not one tree. It is a mixed network: one strong written narrative backbone around Mark (used by both Matthew and Luke), a sayings/tradition layer behind Matthew–Luke material, shared passion and sign traditions overlapping John, and epistolary reuse of fixed Jesus sayings and liturgical formulas. The two system-level alternatives that remain live are **Two-source** (with Q understood as a tradition layer rather than a single discrete document) and **Farrer** (Mark + Matthew → Luke, no Q); minor agreements are the key unresolved discriminator between them.

The strongest individual directional conclusion is **Matthew's dependence on Mark or a Mark-like source**. The strongest non-Gospel saying case is **1 Timothy 5:18's dependence on a Luke-like worker/wages saying**. The strongest cautionary result is that **exact verbal agreement can indicate liturgy or shared tradition rather than direct literary copying**, as with 1 Corinthians 11 and Luke 22.
