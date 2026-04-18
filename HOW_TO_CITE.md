# How to cite

This repository is a **provisional research artifact**. It is not peer reviewed, and every interpretive claim should be treated as exploratory pending scholarly review. See the review-status table in `METHODS.md` section 16.

## Citing the workbench as a whole

> Fleischman, S. (2026). *Gospel Dependence and Early Christian Intertextuality Workbench.* Computational analysis produced by GPT-5.4 Pro; visualizations and infrastructure by Claude Opus 4.7; human direction by Scott Fleischman (prompting only). Available at <https://github.com/scott-fleischman/synopsis-20260417>.

When citing, make LLM-authorship explicit. Do not attribute analytical conclusions to the human author — the human role was prompting and curation only.

## Citing a specific layer

Cite the package directory and commit hash:

```
Fleischman, S. (2026). Mark–Matthew rerun. In Gospel Dependence Workbench,
analysis_update_20260418/reruns/mark_matthew_rerun_robust/, commit <hash>.
```

Authoritative layers by claim:

| Claim family | Cite this layer |
| - | - |
| Mark–Matthew headline counts | `analysis_update_20260418/reruns/mark_matthew_rerun_robust/` |
| Mark–Luke (direct) headline counts | `analysis_update_20260418b/` |
| Matt–Luke masked (Q core) | `analysis_update_20260418/reruns/matt_luke_double_masked_rerun_robust/` |
| John ↔ Synoptic pairwise | `analysis_update_20260418b/` |
| Gospel relationship square | `analysis_update_20260418b/` |
| Thomas logion matrix | `analysis_update_20260418b/` |
| Epistle ↔ Gospel case dossiers | `analysis_update_20260418b/` |
| Interpretive synthesis | `conclusions/CONCLUSIONS.md` |
| Apocrypha inventory (pre-ingestion) | `john_thomas_epistles_apocrypha_analysis/` |

See `AUTHORITATIVE_NUMBERS.yaml` for the exact values and the "prior package" cross-references.

## Citing upstream sources

| Upstream | Citation |
| - | - |
| SBLGNT | *The Greek New Testament: SBL Edition*, edited by Michael W. Holmes. Society of Biblical Literature and Logos Bible Software, 2010. CC BY 4.0. |
| MorphGNT | Tauber, J. et al. *MorphGNT*. <https://github.com/morphgnt/sblgnt>. CC BY-SA 3.0. |
| Coptic Scriptorium Thomas | *Gospel of Thomas* (NHC II,2). Coptic Scriptorium. <https://copticscriptorium.org>. CC BY 4.0. |
| M. R. James | James, M. R. *The Apocryphal New Testament.* Oxford: Clarendon, 1924. Public domain. |

## What NOT to cite from this workbench

- **Do not cite prose conclusions as a source for scholarly claims.** Every claim on `conclusions/CONCLUSIONS.md`, `26_conclusions.html`, and the README should be treated as provisional LLM synthesis.
- **Do not treat a retrieval score as a probability of dependence.** See `METHODS.md` §4.
- **Do not treat the per-pair John burden ledger as anchor-specific evidence.** It is templated framing; per-anchor ledgers are future work.
- **Do not treat the Mark–Luke shared-tradition burden (164.1) as dispositive.** Without a separate shared-tradition penalty model, it is structurally under-penalized.

## Reproducibility tiers

Different layers rebuild with different fidelity. See `REPRODUCIBILITY_LEVELS.md`.
