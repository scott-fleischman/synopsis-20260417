# John, Thomas, Epistles, and Apocrypha Dependence Analysis

This package extends the earlier Synoptic-style pipeline to lower-verbatim material:
John vs. the Synoptics, Gospel of Thomas vs. canonical sayings, NT letters vs. the Gospels,
and a first-pass inventory of other apocryphal texts.

## Major methodological change

A single monotonic order-chain model is not appropriate here. The package uses multiple layers:

1. **Greek surface-text retrieval** for canonical texts.
2. **1–4 verse Gospel windows** to catch sayings spanning verse boundaries.
3. **Exact phrase / n-gram / longest-run evidence** for high-precision cases.
4. **Negative-space flags** for OT quotations, scriptural formulas, and liturgical formulas.
5. **Curated semantic registries** for John, Thomas, James, and Pastorals where verbal agreement is weak.
6. **Burden ledger** separating direct literary dependence, fixed written saying, oral tradition, shared formula, and independent convergence.

## Files

- `00_method_rethought_low_verbatim.yaml` — revised method for low-verbatim / semantic-traditional comparison.
- `01_source_manifest.yaml` — source/layer manifest.
- `02_canonical_units.csv` — SBLGNT canonical units parsed by verse with normalized-token fields.
- `03_thomas_units.csv` — Coptic Scriptorium Thomas div/logion units with Coptic text, lemmas, POS types.
- `04_epistles_to_gospels_candidates.csv` and `.csv.gz` — automatic Greek candidate retrieval from all NT epistles to Gospel windows.
- `05_john_to_synoptics_candidates.csv` and `.csv.gz` — automatic Greek candidate retrieval from John to Synoptic windows.
- `06_exact_phrase_hits_len4plus.csv` — exact contiguous normalized-Greek runs of length 4+.
- `07_targeted_case_studies.yaml` — high-value cases with token-level diffs and burden notes.
- `08_john_synoptic_anchor_registry.yaml` — curated John/Synoptic episode anchors.
- `09_thomas_parallel_registry.yaml` — curated Thomas/canonical saying registry.
- `10_negative_space_flags_for_exact_hits.csv` — flags for scripture/formula/common-source noise.
- `11_concept_signature_registry.yaml` — cross-text concept/saying signatures.
- `12_apocrypha_inventory_from_mr_james.csv` — apocryphal corpus inventory for future primary-language comparison.
- `13_intertext_network_edges.csv` — network edge table combining automatic and curated evidence.
- `14_burden_ledger.yaml` — hypothesis-burden ledger.
- `15_filtered_high_value_exact_hits.csv` — deduplicated exact hits after scripture/liturgy-pattern filtering.
- `16_global_summary.yaml` — package-wide counts and headline findings.

## Important limitations

- The Greek lexical layer uses normalized surface forms and a heuristic stemmer, not a full morphological parser.
- Thomas is represented from Coptic Scriptorium TEI/CoNLL-U; Greek-to-Coptic direct dependence is not automatically scored.
- The apocrypha file is an inventory layer, not a full primary-language comparison.
- Candidate scores are retrieval scores, not probabilities.
- Scriptural and liturgical formulas can create long exact matches without proving Gospel dependence.
