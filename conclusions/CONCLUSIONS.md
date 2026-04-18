# Conclusions from the generated packages

> *This prose argument was produced by **GPT-5.4 Pro** under human direction (prompting only). The four analysis packages it builds on were also produced by GPT-5.4 Pro; the machine-readable extracts in `data/` were produced by Claude Opus 4.7. See the repo-level README for the full breakdown.*

These are LLM-authored interpretive conclusions drawn from the four analysis packages. They are synthesis, not automated pipeline output. The underlying data supports these claims at the stated confidence levels; the inferences themselves are the reader's.

| Question | Conclusion I would draw | Confidence |
| - | - | - |
| Mark–Matthew | Matthew most likely used Mark or a Mark-like written text as a major narrative source. | High |
| Matthew–Luke double tradition | The isolated non-Markan material is better explained by common written/oral Jesus tradition than by a simple one-way Matthew↔Luke dependence. | Medium-high |
| Q | The data supports a shared sayings/tradition layer; it does not by itself prove one discrete Q document. | Medium |
| John–Synoptics | John shares substantial tradition with the Synoptics, especially passion/sign material, but the data does not justify a simple "John copied X Gospel" model. | Medium |
| Thomas–Synoptics | Thomas is best treated as a sayings-network witness, not as cleanly dependent on one canonical Gospel. | Medium |
| 1 Timothy 5:18 / Luke 10:7 | This is one of the strongest cases for a Luke-like written Jesus saying known to the author of 1 Timothy, though not necessarily canonical Luke in final form. | High |
| James / Gospel sayings | James likely draws on Jesus tradition; direct use of Matthew or Luke is not demonstrated by the data. | Medium-high |
| Other apocrypha beyond Thomas | The package does not yet support firm conclusions; it mostly identifies future high-value texts. | Low |

## 1. Mark–Matthew: I would infer Markan priority, or at least Mark-like priority

The Mark–Matthew package gives the clearest result. It found a large continuous shared narrative core: 385 primary chain pairs, covering 57.21% of Mark but only 36.05% of Matthew. That asymmetry matters. Matthew contains far more non-parallel material outside the aligned Markan core: 474 more Matthew gap verses across block boundaries, versus 87 more Mark gap verses. See [`mark_matthew_analysis/data/16_global_summary.yaml`](../mark_matthew_analysis/data/16_global_summary.yaml) and [`mark_matthew_analysis/data/14_direction_ledger_by_loose_block.yaml`](../mark_matthew_analysis/data/14_direction_ledger_by_loose_block.yaml).

The most natural reading is not simply "Matthew is longer." Inside the aligned core, the token counts are nearly identical: Mark 8,258 tokens and Matthew 8,259 tokens inside loose blocks. So the directional issue is not that Matthew mechanically expands Mark everywhere. Rather, Matthew preserves a Mark-like narrative skeleton, sometimes abbreviates, sometimes expands, but then adds or relocates large blocks of teaching, infancy material, fulfillment material, and discourse material.

That is an easier editing program to explain than the reverse.

Under Matthew-from-Mark, the required program is coherent:

- preserve much of Mark's narrative order;
- smooth or reframe Mark's diction;
- add infancy and fulfillment material;
- collect sayings into larger discourse blocks;
- shift "kingdom of God" language toward "kingdom of heaven";
- reduce some Markan vividness and immediacy.

Under Mark-from-Matthew, the required program is more costly:

- omit the infancy material;
- omit or ignore the Sermon on the Mount and other large Matthean discourse blocks;
- often make the narrative rougher or more vivid;
- replace some Matthean theological diction with Markan diction;
- repeatedly remove large Matthean sections while still preserving enough of Matthew's structure to create the observed alignment.

The burden is especially high in places like the Matthean-only stretches listed in the summary: Matt 4:24–7:28, Matt 9:18–11:30, Matt 24:37–26:3, and Matt 1:1–3:2. A Mark-from-Matthew hypothesis can explain them only by repeated non-use or deliberate omission of major, valuable material. That is possible, but it is a heavier cumulative burden.

So my conclusion is:

> Matthew most likely used Mark, or a Mark-like written source very close to Mark. Mark-from-Matthew is possible in isolated blocks but cumulatively less economical.

## 2. Matthew–Luke: the full comparison and the masked comparison point in different directions, and the masked one matters more

The full Matthew–Luke package showed extensive relationship but weak monotonic order. It had only 233 primary backbone pairs, but 1,033 secondary echoes. That means Matthew and Luke share a lot of material, but not in a stable shared sequence. See [`matt_luke_analysis/data/16_global_summary.yaml`](../matt_luke_analysis/data/16_global_summary.yaml).

The full unmasked burden totals actually favored a Luke-prior / Matthew-uses-Luke model numerically:

- Matt prior / Luke uses Matthew: 142.559
- Luke prior / Matthew uses Luke: 75.477

But I would not treat that as the main result for the Q/double-tradition question. The full comparison includes Markan material, infancy material, passion material, and other order effects. It is useful, but it is not the cleanest test of Matthew–Luke dependence.

The masked double-tradition package is more important. Once likely Markan material was removed, the result changed. The directional burdens became symmetrical:

- Luke uses Matthew: 26.446
- Matthew uses Luke: 26.446
- common source or oral tradition: 8.86

See [`matt_luke_double_masked_analysis/data/16_global_summary.yaml`](../matt_luke_double_masked_analysis/data/16_global_summary.yaml) and [`matt_luke_double_masked_analysis/data/15_direction_burden_totals.yaml`](../matt_luke_double_masked_analysis/data/15_direction_burden_totals.yaml).

That is a major result. It says that once Markan material is stripped out, the remaining Matthew–Luke parallels do not naturally resolve into "Luke copied Matthew" or "Matthew copied Luke." They look more like shared sayings material: sometimes verbally close, often displaced, and frequently arranged differently.

The strongest double-tradition echoes are exactly the kind of material that can circulate as fixed sayings:

- Matt 7:8 ↔ Luke 11:10;
- Matt 8:20 ↔ Luke 9:58;
- Matt 12:41–42 ↔ Luke 11:31–32;
- Matt 6:24 ↔ Luke 16:13;
- Matt 7:7 ↔ Luke 11:9;
- Matt 6:11 ↔ Luke 11:3;
- Matt 23:37 ↔ Luke 13:34.

These are not random similarities. The burden of pure independence is too high. But the nonlocal placement weakens a simple direct-copy model.

So my conclusion is:

> The Matthew–Luke double tradition is real shared tradition, often verbally fixed, but the data favors a common sayings/tradition model over direct one-way dependence.

That can be called "Q" only if Q is defined cautiously. The data supports a shared source/tradition layer. It does not require that this layer was one tidy document with the exact shape traditionally reconstructed as Q.

## 3. Mark and Q-like material behave differently

This is one of the most important methodological conclusions.

Mark–Matthew looks like **narrative-source dependence**. It has a durable backbone, stable block order, and repeated local alignment.

Matthew–Luke double tradition looks like **sayings-source or tradition dependence**. It has strong verbal echoes but weak macro-order. The strongest parallels often appear in the secondary-echo layer rather than in the monotonic chain.

That difference matters. It suggests that the Synoptic relationships are not all the same kind of relationship.

I would model the data like this:

```yaml
synoptic_model_inferred_from_packages:
  mark_matthew:
    best_model: Matthew uses Mark or Mark-like written narrative source
    evidence_type:
      - broad narrative alignment
      - many primary chain pairs
      - coherent Matthean expansion/discourse clustering
      - lower burden than Mark omitting major Matthean blocks
  matthew_luke_double_tradition:
    best_model: shared sayings source/tradition
    evidence_type:
      - strong verbal echoes
      - nonlocal placement
      - weak monotonic order
      - symmetric direct-dependence burden after Mark masking
  implication:
    q_question: supports a shared sayings layer, not necessarily a single recoverable document
```

## 4. John: shared tradition is clear; direct Synoptic dependence is not yet clear

The John package shows many anchor episodes shared with the Synoptics: Baptist material, temple action, feeding, walking on water, anointing, entry, arrest, denial, passion, and garment division. See [`john_thomas_epistles_apocrypha_analysis/data/08_john_synoptic_anchor_registry.yaml`](../john_thomas_epistles_apocrypha_analysis/data/08_john_synoptic_anchor_registry.yaml).

But John does not behave like Matthew using Mark. It does not preserve a continuous Synoptic narrative backbone in the same way. The lexical matches are often local, formulaic, scriptural, or embedded in a heavily transformed Johannine narrative.

Some cases are too specific for pure independence:

- sword / high priest's servant / ear in the arrest scene;
- garment division and lots;
- Peter's denial structure;
- feeding and walking-on-water clusters;
- anointing and "poor you always have" material;
- triumphal-entry acclamation.

But these are also the kinds of materials that could belong to a shared passion or miracle tradition. The package's burden ledger therefore treats John as a network case, not as a clean direct-dependence case. See [`john_thomas_epistles_apocrypha_analysis/data/14_burden_ledger.yaml`](../john_thomas_epistles_apocrypha_analysis/data/14_burden_ledger.yaml).

My conclusion:

> John almost certainly shares substantial tradition with the Synoptics. Pure independence is implausible for several detail clusters. But the data does not yet justify saying John directly used Mark, Matthew, or Luke as a dominant written source.

The most likely model is:

```yaml
john_synoptic_relation:
  global_model: overlapping tradition network
  direct_literary_dependence:
    possible_locally: true
    globally_demonstrated: false
  strongest_zones:
    - passion narrative
    - feeding / sea material
    - anointing
    - triumphal entry
    - arrest and denial details
  weakest_evidence:
    - broad theology alone
    - generic shared phrases
    - scriptural/liturgical formulas
```

## 5. Thomas: too much overlap for independence, but not enough for simple direct dependence

The Thomas package parsed 116 Coptic Thomas units and registered 47 Thomas/canonical parallels. See [`john_thomas_epistles_apocrypha_analysis/data/09_thomas_parallel_registry.yaml`](../john_thomas_epistles_apocrypha_analysis/data/09_thomas_parallel_registry.yaml).

The dominant conclusion is not "Thomas used Matthew" or "Thomas used Luke." The better conclusion is:

> Thomas participates in a sayings network that overlaps substantially with Synoptic Jesus tradition.

Some Thomas parallels are highly portable sayings:

- hidden / revealed;
- lamp not hidden;
- blind leading blind;
- whoever has will receive;
- seek / find / knock;
- prophet without honor.

These have low direct-dependence value because they can circulate orally and independently within a shared teaching tradition.

Other Thomas parallels are stronger because they involve more structured material:

- sower;
- mustard seed;
- banquet excuses;
- wicked tenants / rejected stone;
- Caesar's coin;
- lost sheep;
- treasure hidden in field;
- pearl;
- inheritance divider;
- womb / breasts blessing;
- rest / easy yoke.

For these, pure independence becomes less plausible. But because Thomas is sayings-only and preserved in Coptic, the package cannot automatically infer direct Greek literary dependence. The evidence has to be assessed logion by logion.

My conclusion:

> Thomas is not best explained as an independent creation. It preserves or reworks many Jesus-tradition units known also from canonical material. But its relation is network-like, not a simple branch from one canonical Gospel.

## 6. 1 Timothy 5:18 and Luke 10:7: this is one of the strongest non-Gospel cases

This is the strongest epistle-to-Gospel case in the generated package. The relevant segment is:

```yaml
case: 1Tim 5:18 ~ Luke 10:7
exact_run: "ο εργατης του μισθου αυτου"
max_exact_run_len: 5
best_explanation:
  - direct use of Luke-like written form
  - or fixed written Jesus-saying tradition close to Luke
disfavored:
  - independent convergence
```

See [`john_thomas_epistles_apocrypha_analysis/data/07_targeted_case_studies.yaml`](../john_thomas_epistles_apocrypha_analysis/data/07_targeted_case_studies.yaml).

The important detail is that 1 Timothy agrees more closely with Luke than Matthew. Matthew has the worker worthy of food/support formulation; Luke has the worker worthy of wages, matching 1 Timothy's μισθός form.

So I would conclude:

> 1 Timothy 5:18 very probably knows a fixed Jesus saying in a Luke-like form. It is stronger evidence for a Luke-like written or stabilized sayings tradition than for independent oral convergence.

Whether that means the author of 1 Timothy used canonical Luke depends on the dating model one accepts. The textual data alone says "Luke-like form," not necessarily "the final Gospel of Luke in our exact form."

## 7. James: Jesus-tradition dependence is likely; direct Matthew dependence is not proven

James is different from 1 Timothy. The James parallels are often semantically strong but lexically weak.

The oath saying is the highest-value case:

```yaml
case: Jas 5:12 ~ Matt 5:34-37
shared_features:
  - no oaths
  - heaven / earth
  - yes / yes and no / no
best_explanation: shared Jesus tradition
direct_matthew_use: possible but not required
independence: high burden
```

James 5:12 is too close conceptually to dismiss. But the lexical form is compressed and paraenetic. James does not look like he is mechanically copying Matthew's expanded antithesis. He looks like he is using a compact form of a Jesus ethical saying.

The same pattern appears elsewhere:

- Jas 2:5 with poor / kingdom material;
- Jas 1:5–6 with ask / receive / faith motifs;
- Jas 1:22–25 with hearing and doing the word;
- Jas 4:10 with humble / exalt;
- Jas 2:13 and 4:11–12 with mercy, judgment, and judging.

My conclusion:

> James probably reflects Jesus tradition, but the package does not support direct dependence on Matthew or Luke as the simplest explanation. Shared oral or written catechetical tradition has lower burden.

This is exactly the kind of case where exact-word methods under-detect real relationship. The relationship is probably real, but not necessarily literary dependence on a canonical Gospel.

## 8. Paul / Luke eucharistic material: formulaic tradition, not simple literary dependence

The 1 Corinthians 11 / Luke 22 case is lexically strong. The package finds a long exact run:

```yaml
case: 1Cor 11:24 ~ Luke 22:19
exact_run: "τουτο ποιειτε εις την εμην αναμνησιν"
max_exact_run_len: 6
best_explanation:
  - shared liturgical tradition
  - or Luke using a tradition also represented by Paul
not_best_explanation:
  - Paul simply copied Luke
```

The reason is not lexical; lexically the case is strong. The reason is causal and chronological. Formulaic liturgical material can be shared because both texts draw from a preexisting ritual tradition. So this is a crucial negative-space control: long exact agreement does not always mean one canonical text copied the other.

My conclusion:

> The Lord's Supper overlap shows strong shared formula, but it should be treated as liturgical tradition rather than direct Gospel dependence unless additional directional evidence is supplied.

## 9. Johannine letters: shared school/idiolect, not one-verse proof of direction

The case 1 John 3:13 / John 15:18–19 has a notable exact run around "the world hates you." The package treats this as a Johannine idiom case.

My conclusion:

> 1 John and John share Johannine language and conceptual tradition. That is strong evidence of a shared school, discourse world, or compositional environment, but one motif does not decide whether the epistle used the Gospel or the Gospel used epistolary tradition.

This category is different from Gospel-to-Gospel dependence. It is intra-corpus idiolectal continuity.

## 10. Apocrypha beyond Thomas: not enough data yet for firm dependence conclusions

The package includes an apocrypha inventory, but not a full parsed, aligned, language-sensitive analysis of Gospel of Peter, Protevangelium of James, Infancy Thomas, Gospel of Nicodemus, Jewish-Christian gospel fragments, and related texts. See [`john_thomas_epistles_apocrypha_analysis/data/12_apocrypha_inventory_from_mr_james.csv`](../john_thomas_epistles_apocrypha_analysis/data/12_apocrypha_inventory_from_mr_james.csv).

So I would not make strong conclusions there yet. I would only say:

> Gospel of Peter and passion apocrypha are probably the highest-value next test cases, because passion material has dense shared narrative detail. Infancy and childhood gospels are also valuable, but they require a different model because they often expand into narrative gaps rather than directly rewriting canonical pericopae.

## Overall model I would adopt

Given all of the generated packages, I would model early Christian textual relationships like this:

```yaml
best_current_model_from_generated_data:
  mark:
    role: major written narrative source
    relation_to_matthew: Matthew probably uses Mark or Mark-like source
  matthew_luke_double_tradition:
    role: shared sayings/tradition layer
    best_explanation: common written/oral Jesus tradition
    q_implication: supports Q-like layer, not necessarily a single recoverable Q document
  john:
    role: independent literary-theological Gospel using overlapping Jesus/passion/sign traditions
    direct_synoptic_use: possible locally, not globally proven
  thomas:
    role: sayings-network witness
    direct_dependence_on_canonical_gospels: varies by logion, not globally established
  james:
    role: epistolary paraenesis saturated with Jesus-tradition motifs
    direct_gospel_use: not demonstrated
  first_timothy:
    role: strong witness to a Luke-like fixed Jesus saying
    independent_convergence: very unlikely
  paul_lord_supper:
    role: liturgical/traditional formula
    direct_luke_dependence: not the best explanation
```

## The main methodological conclusion

The generated data argues against using one method for all these texts.

For **Mark–Matthew**, an order-sensitive literary-dependence model works well.

For **Matthew–Luke double tradition**, a sayings-source/tradition model works better than a single linear order-chain model.

For **John**, the right model is anchor-based transformation analysis.

For **Thomas**, the right model is sayings-network analysis.

For **James and the epistles**, the right model is formula/saying detection plus burden analysis, because exact wording often disappears while conceptual structure remains.

So the core conclusion is:

> The early Christian textual field is not one tree. It is a mixed network: one strong written narrative backbone around Mark, a sayings/tradition layer behind Matthew–Luke material, shared passion and sign traditions overlapping John, and epistolary reuse of fixed Jesus sayings and liturgical formulas.

The strongest individual directional conclusion is **Matthew's dependence on Mark or a Mark-like source**. The strongest non-Gospel saying case is **1 Timothy 5:18's dependence on a Luke-like worker/wages saying**. The strongest cautionary result is that **exact verbal agreement can indicate liturgy or shared tradition rather than direct literary copying**, as with 1 Corinthians 11 and Luke 22.
