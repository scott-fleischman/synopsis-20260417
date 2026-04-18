# Gospel Dependence and Early Christian Intertextuality Workbench

**Live visualizations: <https://scott-fleischman.github.io/synopsis-20260417/>** · Source: <https://github.com/scott-fleischman/synopsis-20260417>

A layered, auditable workbench for studying literary dependence and intertextuality across the New Testament Gospels, Thomas, the canonical epistles, and the broader apocryphal corpus. Built from the SBLGNT Greek text and apparatus, MorphGNT morphology, Coptic Scriptorium Thomas, and an inventory of the M. R. James apocrypha. Eight analysis packages feed a single browser-native visualization site with 35 views; every headline number is traceable to a specific `data/*.yaml` line in its package.

The repository does **not** settle the direction of dependence. It quantifies what each direction-hypothesis must explain, and exposes every intermediate artifact so a reviewer can audit the pipeline end-to-end. The site is organized around the `analysis_update_20260418b` supplement's eight-rank priority-of-interpretation schedule — Conclusions · Canonical Gospel square · Mark↔Luke direct · John pairwise · Matt↔Luke masked Q core · Thomas matrix · Epistle case dossiers · Audit and sensitivity — rather than as a flat list of pages. Supporting Synoptic narrative views live under the Audit and reproducibility umbrella.

## Licenses and attribution

This repository combines code and data under several licenses. The project code (preprocessing, visualizations, tests) is MIT; upstream corpora retain their own licenses, which are **not overridden** by the project license.

| Component | License | Owner / source |
| - | - | - |
| Project code, visualizations, tests, build step | MIT | Scott Fleischman / project contributors |
| **SBLGNT** Greek text and apparatus | **CC BY 4.0** | Society of Biblical Literature & Logos Bible Software. See <https://sblgnt.com/> |
| **MorphGNT** morphology and lemmas | **CC BY-SA 3.0** | James Tauber et al. See <https://github.com/morphgnt/sblgnt> |
| **Coptic Scriptorium** Thomas (NHC II,2) | **CC BY 4.0** | See <https://copticscriptorium.org/> |
| M. R. James, *The Apocryphal New Testament* (1924) | Public domain | Used as inventory reference only |
| Interpretive prose in `conclusions/` | MIT (follows project) | Project contributors |

Per-file SHA256 provenance is recorded in every package's `MANIFEST.yaml`; source hashes and retrieval timestamps are in each `data/00_source_metadata.yaml`. The reproducibility-patch rerun (`analysis_update_20260418/`) has its own `MANIFEST.yaml` with SHA256 hashes for every output file.

## Authorship

All content in this repository was produced by LLMs under human direction. The human role (Scott Fleischman) was **prompting and direction only** — no manual authoring of code, data, or prose.

- **Analysis packages** — the CSV/YAML artifacts, pipeline logic, and per-package documentation in `mark_matthew_analysis/`, `matt_luke_analysis/`, `matt_luke_double_masked_analysis/`, and `john_thomas_epistles_apocrypha_analysis/` — produced by **GPT-5.4 Pro**.
- **Reproducibility-patch rerun** — `analysis_update_20260418/` (multi-regime masking, sensitivity grids, claim/evidence linkage, three-axis confidence scoring) — produced by **GPT-5.4 Pro**.
- **High-priority supplement** — `analysis_update_20260418b/` (direct Mark↔Luke, three John pairwise layers, canonical Gospel relationship square, Thomas logion matrix, 60 epistle case dossiers, conclusion → evidence → contrary navigation) — produced by **GPT-5.4 Pro**.
- **Data-analysis patch** — `analysis_update_20260418c/` (Mark↔Luke order-retention penalty model, Matthew↔Luke mask-regime robustness, John anchor-specific burden ledgers, Thomas curation status, epistle validation sample, MorphGNT lemma audit, revised data-only conclusions with nuanced confidence) — produced by **GPT-5.4 Pro**.
- **Interpretive conclusions** — the prose argument in `conclusions/CONCLUSIONS.md` — produced by **GPT-5.4 Pro**.
- **Visualizations and infrastructure** — the HTML pages in `visualizations/` and `docs/`, the `preprocess.py` build step, the test suite, the top-level and `conclusions/` READMEs, and the structured data extracts in `conclusions/data/` — produced by **Claude Opus 4.7**.

## What is here

```
synopsis-20260417/
├── mark_matthew_analysis/               # Mark ↔ Matthew (triple-tradition backbone)
├── matt_luke_analysis/                  # Matthew ↔ Luke (full corpus)
├── matt_luke_double_masked_analysis/    # Matthew ↔ Luke with likely-Markan verses masked out
├── john_thomas_epistles_apocrypha_analysis/   # Low-verbatim network: John, Thomas, NT letters, apocrypha
├── analysis_update_20260418/            # Reproducibility-patch rerun — the authoritative headline numbers
├── analysis_update_20260418b/           # High-priority supplement — direct Mark↔Luke, John pairwise, Gospel square, Thomas matrix, epistle dossiers, conclusion nav
├── analysis_update_20260418c/           # Data-analysis patch — order-retention penalty, mask-regime robustness, anchor-specific John ledgers, Thomas curation status, epistle validation, MorphGNT lemma audit
├── conclusions/                         # Author-authored synthesis across all packages
├── visualizations/                      # 35 browser views, organised by the 18b 8-rank priority schedule + Python build step + tests
└── docs/                                # Committed deployment snapshot (the GitHub Pages output dir)
```

All three layers — data, code, and rendered output — are committed, and a fourth layer (interpretive conclusions) sits alongside them in its own directory. Each analysis package is self-contained: it owns its raw sources (where applicable), its derived CSV/YAML artifacts, a `MANIFEST.yaml` with file hashes, a `README.md`, and an `EXECUTIVE_SUMMARY.md`.

## The seven data packages

### 1. `mark_matthew_analysis/` — triple-tradition backbone

Layered comparison of Mark and Matthew in Greek. Negative-space flags → verse similarity matrix → 3-verse window matrix → monotonic primary chain → loose blocks → tight blocks → directional burden ledgers (both directions) → secondary-echo recovery.

### 2. `matt_luke_analysis/` — full Matthew ↔ Luke corpus

Same pipeline as Mark-Matthew, but on the full Matthew-Luke pair. Important caveat: Matthew-Luke double tradition is heavily reordered, so the monotonic backbone is intentionally sparse — read alongside the secondary-echo layer.

### 3. `matt_luke_double_masked_analysis/` — isolating the double tradition

Masks likely-Markan material from both Matthew and Luke, then reruns the full pipeline on what remains. The masking rule is algorithmic and fully auditable in `data/01_markan_mask_by_verse.csv`. Lets you inspect the double tradition without triple-tradition confounds.

### 4. `john_thomas_epistles_apocrypha_analysis/` — the low-verbatim network

A monotonic chain is the wrong model here. This package instead builds:

1. Greek surface-text retrieval for canonical texts.
2. 1–4 verse Gospel windows to catch sayings spanning verse boundaries.
3. Exact phrase / n-gram / longest-run evidence for high-precision cases.
4. Negative-space flags for OT quotations, scriptural formulas, and liturgical formulas.
5. Curated semantic registries for John, Thomas, James, and Pastorals where verbal agreement is weak.
6. A burden ledger separating five transmission hypotheses: direct literary dependence, fixed written saying, oral tradition, shared formula, and independent convergence.

### 5. `analysis_update_20260418/` — reproducibility-patch rerun

Re-runs the three quantitative packages (mm, mld, jtea) with explicit source provenance, multi-regime masking (strict 0.40 / medium 0.355 / broad 0.325), a score × gap-penalty sensitivity grid for Mark-Matthew, a Mark 16:9-20 text-critical sensitivity layer, and — for the low-verbatim corpus — a three-dimensional confidence scoring system (automatic retrieval · philological · formula-risk) with explicit claim → evidence linkage. The `rerun` key on each dataset in the visualization bundle reads directly from this patch; headline numbers on every page are driven from it.

Under the default medium regime the rerun reports:

- Mark–Matthew: **386** primary pairs, **27** loose blocks, **50** tight blocks, **22** selected secondary echoes (231 retained in the full echo layer).
- Masked Matt–Luke (Q-core): **64** primary pairs, **24** loose blocks, **30** tight blocks, **54** selected secondary echoes.
- Low-verbatim: **67** claim→evidence links; formula-risk flags across **~11,000** retrieved exact runs.

### 6. `analysis_update_20260418b/` — high-priority supplement

Fills the eight gaps identified after the repo review. Every layer is surfaced in the visualization bundle under the `h18b` key and integrated into the landing page, conclusions page, Gospel square, Thomas matrix, epistle dossier, and two new dedicated views.

- **Direct Mark ↔ Luke** (`mkl`): 183 primary-chain pairs, 35 loose / 76 tight blocks, 140 secondary echoes at score ≥ 0.22. Mark 16:9–20 is excluded from the default chain and retained as a sensitivity condition. Burden totals: **254.6** Mark-prior (Luke uses Mark or Mark-like source) vs. **303.2** Luke-prior vs. **164.1** shared narrative/oral tradition (unpenalized). 18c adds the order-retention penalty (see §7 below) that adjusts shared tradition to **385.6** under moderate weights, making Mark-prior the lowest-burden model overall. This closes the missing Markan-source control for Luke that the prior packages did not model directly.
- **John pairwise dashboards**: three layers — John↔Mark (33 candidates ≥ 0.25, 10 anchors), John↔Matthew (33 candidates, 10 anchors), John↔Luke (34 candidates, 9 anchors). Anchor-level transformation analysis, not a continuous chain; supports shared-tradition readings rather than a linear copy model.
- **Canonical Gospel relationship square** (`gospel_square`): 4×4 cells with the evidence shape each pair actually supports (aligned pair counts, burden totals, anchor episodes, retrieval-only).
- **Thomas × Gospel logion matrix**: 116 logia, 46 with curated canonical parallels; relation type × matrix strength × direct-dependence burden separated as three distinct axes; per-logion dossiers. Honest about the Coptic-Greek boundary (no automatic Greek score).
- **Epistle → Gospel case dossiers**: 60 cases, 10 targeted with three-axis grading (formula risk × automatic retrieval support × philological case strength). Strongest high-value case: **1 Tim 5:18 / Luke 10:7**.
- **Conclusion → evidence → contrary navigation**: five headline claims, each with supporting and contrary evidence plus what-would-change hooks. Drives the rank-1 view on the landing page and the conclusions page.
- **Priority-of-interpretation schedule** (`42_visualization_priority_order.yaml`): the eight-rank ordering used throughout the site.

See `analysis_update_20260418b/README.md` and `analysis_update_20260418b/EXECUTIVE_SUMMARY.md` for the full specification and method notes on why each corpus uses a different transmission model rather than being forced into a single Synoptic chain.

### 7. `analysis_update_20260418c/` — data-analysis patch (interpretive burden + robustness)

Addresses the interpretive-burden issues flagged after 18b. It does not reshape the visualization layer (that work lives in `visualizations/`); instead, it delivers the corrected numbers and sensitivity layers that the visualization layer now reads.

- **Mark↔Luke burden reassessment with order-retention penalty**: 18b's three-way ledger gave the lowest raw burden to *shared narrative/oral tradition* (164.1), but that baseline did not charge shared tradition for the narrative order, cluster density, and bridging sequences it must still explain. 18c's sensitivity grid adds an order-retention/cluster-density/narrative-bridge penalty. Under moderate weights (0.75 / 1.0 / 1.0) shared tradition adjusts to **385.6** — and Mark-prior (254.6) becomes the lowest-burden model. Mark-prior wins in **211 of 245** grid combinations.
- **Matt↔Luke mask-regime robustness**: the strict/medium/broad mask sweep shows pair counts of 60–76 / 58–71 / 57–69 and loose-block counts of 25–29 / 23–25 / 23–25. Counts move with mask strictness, but the qualitative reading — retained material as a sayings/echo problem, not a stable narrative-chain relationship — is stable across regimes.
- **John anchor-specific burden ledgers**: replaces 18b's templated per-pair framing with per-anchor × per-pair × four-model ledgers. Aggregate totals: John↔Mark 59.7 / 64.0 / **23.5** / 111.0 ; John↔Matt 55.9 / 60.2 / **24.8** / 119.5 ; John↔Luke 58.6 / 61.7 / **20.8** / 91.6 (John-uses-synoptic / synoptic-uses-John / **shared anchor tradition** / independent convergence). Shared anchor tradition wins at *every* anchor on *every* pair (10/10, 10/10, 9/9).
- **Thomas curation status**: augments the 116-logion matrix with parallel-certainty labels. Of 46 curated parallels, only **3 are directional-claim-ready**; the remaining 43 are sayings-network witnesses (28 "overlapping tradition, uncertain direction", 14 "shared sayings or parable tradition", 4 "possible synoptic influence or harmonization").
- **Epistle validation sample**: 160 rows stratified across 7 strata with machine-audit classifier. The top-500 candidate pool contains **317 low / 17 medium / 166 high** formula-risk rows; machine classes are **59 uncertain / 41 strong-low-formula / 26 scriptural-formula / 18 moderate / 13 targeted-known / 3 high-formula-needs-review**.
- **MorphGNT lemma audit layer**: re-scores the 183 Mark-Luke primary pairs on lemmas (surface mean 0.4042 → lemma mean 0.4836; lemma improves/retains on 153/183, worse on 30). Audit metric only — not a replacement pipeline.
- **Revised data-only conclusions**: `reports/updated_data_analysis_conclusions.yaml` restates six headline claims with nuanced confidence (e.g., Mark-Luke: "medium-high for Mark-prior over Luke-prior among direct-use models; medium for direct-use over shared-tradition alone").

See `analysis_update_20260418c/README.md` and `EXECUTIVE_SUMMARY.yaml` for the full patch specification, and `AUTHORITATIVE_NUMBERS.yaml` at the repo root for which number supersedes which.

## Methodological note on burden

No layer in this repository claims to compute posterior probability of a given dependency hypothesis. Every score is a retrieval score, every ledger is a burden audit, and scriptural/liturgical formulas are flagged separately so they do not masquerade as Gospel dependence. See each package's `EXECUTIVE_SUMMARY.md` for the specifics.

## Interpretive conclusions

`conclusions/` is the only directory in the repo that makes directional claims. It is author-authored synthesis across all four packages, kept physically separate from the data so the burden-audit discipline stays intact. Headline findings (descending confidence):

| Question | Conclusion | Confidence |
| - | - | - |
| Mark–Matthew | Matthew most likely used Mark or a Mark-like written source. | High |
| Mark–Luke (direct, 18b + 18c) | Mark-prior is the lighter *direct-use* hypothesis (254.6 vs. 303.2); once shared tradition is charged a fair order-retention cost, Mark-prior also becomes the lowest-burden model overall (Mark-prior 254.6 vs. shared-tradition-adjusted 385.6, moderate weights). | Medium-high for Mark-prior over Luke-prior among direct-use; medium for direct-use over shared-tradition alone |
| 1 Timothy 5:18 / Luke 10:7 | Strongest case for a Luke-like written Jesus saying known to 1 Timothy. | High (targeted case); exploratory for the top-500 pool, where 166 of 500 are already flagged high formula-risk |
| Matthew–Luke double tradition | Shared tradition layer, not simple one-way dependence; stable across strict/medium/broad mask regimes (18c). | Medium-high |
| James / Gospel sayings | Jesus-tradition dependence likely; direct Matthew/Luke use not demonstrated. | Medium-high |
| Q | Supports a shared sayings/tradition layer; doesn't prove one discrete Q document. | Medium-high for shared non-Markan sayings; medium for any discrete Q-document claim |
| John–Synoptics (18b pairwise + 18c anchor ledgers) | Shared passion/sign/anchor tradition rather than simple Gospel-to-Gospel copying; `shared_anchor_tradition` is the lowest-burden model at every anchor on every pair (9/9, 10/10, 10/10). | Medium |
| Thomas–Synoptics (18b matrix + 18c curation) | Sayings-network witness; 46 of 116 logia carry curated canonical parallels, of which only 3 are directional-claim-ready; Coptic–Greek automatic dependence scoring not implemented. | Medium for overlapping sayings tradition, low for global direction |
| Other apocrypha | Inventory only; not enough data yet for firm conclusions. 18c's analysis-status note confirms "not a completed primary-text analysis layer". | Low |

See [`conclusions/CONCLUSIONS.md`](conclusions/CONCLUSIONS.md) for the full argument, [`conclusions/EXECUTIVE_SUMMARY.md`](conclusions/EXECUTIVE_SUMMARY.md) for the short form, and [`conclusions/data/`](conclusions/data/) for the machine-readable models and case snippets.

## Visualizations (35 browser views, 18b priority-ranked)

`visualizations/` is a static HTML/CSS/SVG site with no framework. A single Python build step reads the five analysis packages and the rerun, then writes a compact bundle that every page consumes. The landing page and this README are both organized by the 18b **priority-of-interpretation** schedule (rank 1 Conclusions → rank 8 Audit) so a reader with a question ("is there a direct Mark↔Luke link?", "what is the Q burden?", "what can Thomas tell us?") can land in the right section without needing to know which CSV produced which number.

### Rank 1 · Conclusions, claim ladder, reader — the interpretive entry surface

| # | View | What it shows |
| - | - | - |
| 26 | Conclusions | Leads with the **h18b claim-navigation model**: five headline claims with supporting and contrary evidence and what-would-change hooks, then the existing 10 curated-conclusion cards with dataset-linked evidence and falsifiability panels. |
| 29 | Claim → evidence | 67 interpretive claims each mapped to supporting artifacts with a three-axis confidence ladder (retrieval, philological, formula-risk). |
| 30 | Reader | Full SBLGNT text for Matt · Mark · Luke · John with per-verse parallel badges, mask striping, and bidirectional links into every viz page. **The primary entry surface for verse-level inspection.** |

### Rank 2 · Canonical Gospel relationship square (18b)

| # | View | What it shows |
| - | - | - |
| 31 | Gospel square | 4×4 relationship matrix across Matt · Mark · Luke · John. Each cell records the method that actually applies (aligned pair count, burden totals, anchor episodes, retrieval-only) from the h18b `gospel_square` data. |

### Rank 3 · Mark ↔ Luke direct (18b)

| # | View | What it shows |
| - | - | - |
| 34 | Mark↔Luke | 183 primary-chain pairs, 35 loose / 76 tight blocks, direction ledger by loose block, three-way burden card (Mark-prior · Luke-prior · shared narrative/oral), Mark 16:9–20 ending sensitivity, secondary-echo reel. |

### Rank 4 · John ↔ Synoptics pairwise (18b)

| # | View | What it shows |
| - | - | - |
| 35 | John pairwise | John↔Mark, John↔Matthew, John↔Luke dashboards: global summary counts, anchor registry, pair-level candidate table at score ≥ 0.25, per-anchor support-vs-contrary columns. Anchor-level transformation analysis, not a continuous chain. |
| 20 | John anchors (legacy) | Anchor episodes (Baptist, temple, feeding, walking on water, anointing, entry, arrest, denial, garments) each with two hypothesis columns. |
| 18 | Intertext network | Arc diagram + network edges, filterable by layer, score, run length. |

### Rank 5 · Matt ↔ Luke masked double tradition / Q-core

| # | View | What it shows |
| - | - | - |
| 15 | Q core | Residual double-tradition core after Markan masking. |
| 14 | Mask audit | Audit of which verses were masked as Markan (dataset 3 only). |
| 10 | Displacement | Where secondary echoes land vs. their primary pair. |
| 11 | Echo gallery | Secondary-echo catalog. |
| 16 | Matthew verse card | Per-verse card for Matthew. **Superseded by the Reader (page 30).** |

### Rank 6 · Thomas × Gospel logion matrix (18b)

| # | View | What it shows |
| - | - | - |
| 32 | Thomas × canon | 116-logion × 4-Gospel matrix from the h18b dossier; three axes — relation type (syn-influenced · shared-sayings · overlap · no-parallel) × matrix strength (high · medium · none) × direct-dependence burden labels; per-logion dossiers; honest about the Coptic-Greek boundary. |
| 21 | Thomas parallels (legacy) | Thomas logia with click-to-Coptic lookup. |

### Rank 7 · Epistle → Gospel case dossiers (18b)

| # | View | What it shows |
| - | - | - |
| 33 | Epistle dossier | 60 case dossiers (10 targeted, 50 screening), three-axis grading (formula risk × retrieval support × philological strength), strongest-case banner, dossier body with exact-run headline, token alignment diff, metrics grid, best-current-model accent band, supporting vs. limiting evidence, hypothesis classifier. |
| 19 | Case studies (legacy) | Targeted high-value cases with token-level diffs. |
| 24 | Epistle × Gospel heatmap | Book-matrix cells with 4 metrics × 3 scales. |
| 23 | Exact hits | Score × run scatter plus top filterable hits. |
| 22 | Concept signatures | Cross-corpus presence matrix + per-concept burden bars. |

### Rank 8 · Audit and sensitivity

| # | View | What it shows |
| - | - | - |
| 27 | Sensitivity · Mark–Matthew | Score × gap-penalty grid + Mark 16:9–20 text-critical sensitivity. |
| 28 | Sensitivity · masked Q-core | Strict / medium / broad regime × chain-threshold sweep. |
| 17 | JTEA overview | Landing page for the low-verbatim package. |
| 25 | Apocrypha inventory | M. R. James apocryphal works grouped by corpus. **Inventory only, not analysis.** |

### Supporting Synoptic narrative pages (mm-anchored)

| # | View | What it shows |
| - | - | - |
| 01 | Synoptic map | Full verse-by-verse alignment across the active dataset (mm / ml / mld). |
| 02 | Block ribbon | Macro and micro blocks as a ribbon. |
| 03 | Burden ledger | Directional-burden ledger per loose block. |
| 04 | Gap timeline | Where one Gospel has material the other does not. |
| 05 | Lexical drift | Lemma-level divergence across aligned pairs. |
| 06 | Score classes | Distribution of pair scores. |
| 07 | Block cards | Per-block summary cards. |
| 08 | Stylistic markers | Book-level stylistic features. |
| 09 | Pair explorer | Browse any primary pair with full diff. |
| 12 | Variants | SBLGNT apparatus notes attached to primary pairs. |
| 13 | Triangle | Three-corner view of the Synoptic datasets (now four-way once Mark↔Luke is added). |

Dataset switching on Synoptic pages is via URL hash: `#mm`, `#ml`, `#mld`. The active dataset is remembered per page.

## How to run

Prerequisites: Python 3.11+. No Node, no framework, no database.

### Quickest path — serve the committed snapshot

```bash
cd docs
python3 -m http.server 8000
```

Open <http://localhost:8000/index.html>. No build step needed; `docs/` is a committed artifact. See `docs/README.md` for what's inside.

The full development workflow below is for when you change the pages, the bundle, or the source data.

### 1. Build the bundle

From the repo root:

```bash
python3 visualizations/build/preprocess.py
```

This reads the four analysis packages and the reproducibility-patch rerun, then writes:

- `visualizations/data/bundle.json` — for fetch-based consumption
- `visualizations/data/bundle.js` — `window.SYNOPSIS = {...}` for `file://` use

The build is deterministic: re-running it on unchanged data produces a byte-identical bundle (enforced by `test_build_idempotence.py`).

### 2. Serve the site

```bash
cd visualizations
python3 -m http.server 8000
```

Then open <http://localhost:8000/index.html>. The index lists every Synoptic and low-verbatim view. Dataset switching on Synoptic pages uses the URL hash (`#mm`, `#ml`, `#mld`).

### 3. Run the tests

Tests validate that the bundle stays consistent with the source data, that every page is wired up correctly, and that no page introduces an `innerHTML =` assignment (a CSP-style restriction enforced by a hook).

First-time setup (creates a local venv, ignored by git):

```bash
python3 -m venv visualizations/tests/.venv
visualizations/tests/.venv/bin/pip install pytest pyyaml
```

Run:

```bash
visualizations/tests/.venv/bin/pytest visualizations/tests/
```

## Sources and provenance

- **Greek text base**: Society of Biblical Literature Greek New Testament (SBLGNT). License: **CC BY 4.0**. © Society of Biblical Literature & Logos Bible Software; see <https://sblgnt.com/>.
- **Apparatus / variants**: SBLGNT apparatus (same license).
- **Morphology and lemmas**: MorphGNT. License: **CC BY-SA 3.0**. See <https://github.com/morphgnt/sblgnt>.
- **Coptic Thomas**: Coptic Scriptorium TEI/CoNLL-U for NHC II,2. License: **CC BY 4.0**. See <https://copticscriptorium.org/>.
- **Apocryphal inventory**: derived from M. R. James, *The Apocryphal New Testament* (1924, public domain). Used as a list, not a primary-text comparison.

Each package records its source hashes in `MANIFEST.yaml` (or `manifest.yaml`) and `data/00_source_metadata.yaml`. The rerun adds its own per-file SHA256 provenance in `analysis_update_20260418/MANIFEST.yaml`.

## Limitations

- The Greek lexical layer uses normalized surface forms and a heuristic stemmer, not a full morphological parser. 18c adds a **lemma audit layer** for the Mark-Luke primary chain (surface mean 0.4042 vs. lemma mean 0.4836, lemma improves/retains on 153 of 183 pairs) — but this is an audit, not a full morphology-based rerun of the retrieval pipeline.
- Coptic Thomas is parsed from Coptic Scriptorium; Greek-to-Coptic direct literary dependence is not automatically scored. 18c's curation-status annotations make the consequences explicit — only 3 of 116 logia are directional-claim-ready.
- The apocrypha file is an inventory layer, not a full primary-language comparison. 18c's analysis-status note reconfirms this and lists the next-ingestion priorities.
- Candidate scores are retrieval scores, not probabilities.
- Scriptural and liturgical formulas can create long exact matches without proving Gospel dependence — those are flagged separately. Across the 500-row top epistle-Gospel pool, 18c reports **166 high / 17 medium / 317 low** formula-risk rows.
- The default medium mask regime is one auditable choice among several; page 28 lets you inspect the strict and broad alternatives side by side. 18c's mask-regime robustness table shows the qualitative reading is stable across all three regimes even though pair counts vary.
- The shared-tradition penalty model in the Mark-Luke ledger is structurally under-penalized unless an explicit order-retention penalty is applied. 18c's sensitivity grid is the current best calibration — a proven posterior would require a prior model that this repository does not supply.
