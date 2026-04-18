# Executive Summary

This run expands the analysis beyond the Synoptic backbone into the lower-verbatim domain: John, Thomas, canonical letters, and selected apocryphal materials.

## Counts

- Canonical books parsed: **27**
- Canonical verses parsed: **7939**
- Gospel verses parsed: **3768**
- Epistle verses parsed: **2764**
- Thomas Coptic units parsed: **116**

## Automatic retrieval layers

- Epistles → Gospel windows: **12036** candidate rows.
- Epistle source units with candidates: **1077**.
- Epistle source units with exact Greek run length ≥4: **161**.
- John → Synoptic windows: **12831** candidate rows.
- John source units with candidates: **672**.
- John source units with exact Greek run length ≥4: **198**.
- Total exact phrase hits length ≥4: **11366**.

## Main methodological conclusion

For John, Thomas, James, and the Pastorals, the most reliable framework is not a Synoptic-style linear order chain. It is a network model with separate layers for exact Greek agreement, fixed sayings, oral/traditional transmission, shared scripture/liturgy, and semantic/thematic convergence.

## High-value findings

1. **1Tim 5:18 ~ Luke 10:7** is one of the strongest cases in this set. The automatic layer finds a five-token exact normalized Greek run: `ο εργατης του μισθου αυτου`. This supports either direct written dependence on a Luke-like form or a fixed written Jesus-saying tradition close to Luke. It strongly disfavors independent convergence.

2. **Jas 5:12 ~ Matt 5:34-37** is high-value but not high-scoring lexically. The reason is methodological: James compresses the oath material, Matthew expands it, and the oath verb/root forms do not align exactly. This is the kind of case that requires the curated semantic layer.

3. **1Cor 11:24-25 ~ Luke 22:19-20** produces long exact formulaic agreement, but the best burden model is liturgical/shared tradition and/or Luke using a tradition also known to Paul. It should not be treated as Paul depending on Luke on surface similarity alone.

4. **John vs. the Synoptics** shows many anchor episodes—Baptist, temple action, feeding, walking on water, anointing, entry, arrest, denial, garments—but the transformations are too large for a simple lexical pipeline. The package therefore uses anchor-level burden notes.

5. **Thomas** should be modeled as a sayings-network witness. The package parses Coptic Thomas units and provides a curated registry of 47 Thomas/canonical saying parallels, but does not pretend that Coptic semantic parallels are automatic proof of Greek literary dependence.

6. **Negative-space control is essential.** Some of the longest exact NT-letter/Gospel matches are shared scriptural quotations, such as Psalm 110 or Genesis 2, and are therefore not strong evidence of Gospel dependence by themselves.

## First files to inspect

- `07_targeted_case_studies.yaml`
- `13_intertext_network_edges.csv`
- `04_epistles_to_gospels_candidates.csv.gz`
- `05_john_to_synoptics_candidates.csv.gz`
- `09_thomas_parallel_registry.yaml`
- `14_burden_ledger.yaml`
