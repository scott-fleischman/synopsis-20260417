# Synoptic dependence — quantitative study

**Live visualizations: <https://scott-fleischman.github.io/synopsis-20260417/>** · Source: <https://github.com/scott-fleischman/synopsis-20260417>

A layered, auditable study of literary dependence in the New Testament Gospels and related early-Christian literature. Built from the SBLGNT Greek text and apparatus, MorphGNT morphology, Coptic Scriptorium Thomas, and an inventory of the M. R. James apocrypha.

The repository does **not** settle the direction of dependence. It quantifies what each direction-hypothesis must explain, and exposes every intermediate artifact so a reviewer can audit the pipeline end-to-end.

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
├── conclusions/                         # Author-authored synthesis across all four packages
├── visualizations/                      # 29 browser views + Python build step + tests
└── docs/                                # Committed deployment snapshot (the GitHub Pages output dir)
```

All three layers — data, code, and rendered output — are committed, and a fourth layer (interpretive conclusions) sits alongside them in its own directory. Each analysis package is self-contained: it owns its raw sources (where applicable), its derived CSV/YAML artifacts, a `MANIFEST.yaml` with file hashes, a `README.md`, and an `EXECUTIVE_SUMMARY.md`.

## The five data packages

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

## Methodological note on burden

No layer in this repository claims to compute posterior probability of a given dependency hypothesis. Every score is a retrieval score, every ledger is a burden audit, and scriptural/liturgical formulas are flagged separately so they do not masquerade as Gospel dependence. See each package's `EXECUTIVE_SUMMARY.md` for the specifics.

## Interpretive conclusions

`conclusions/` is the only directory in the repo that makes directional claims. It is author-authored synthesis across all four packages, kept physically separate from the data so the burden-audit discipline stays intact. Headline findings (descending confidence):

| Question | Conclusion | Confidence |
| - | - | - |
| Mark–Matthew | Matthew most likely used Mark or a Mark-like written source. | High |
| 1 Timothy 5:18 / Luke 10:7 | Strongest case for a Luke-like written Jesus saying known to 1 Timothy. | High |
| Matthew–Luke double tradition | Shared tradition layer, not simple one-way dependence. | Medium-high |
| James / Gospel sayings | Jesus-tradition dependence likely; direct Matthew/Luke use not demonstrated. | Medium-high |
| Q | Supports a shared sayings/tradition layer; doesn't prove one discrete Q document. | Medium |
| John–Synoptics | Shared tradition, especially passion/sign; not a simple copy model. | Medium |
| Thomas–Synoptics | Sayings-network witness, not cleanly dependent on one canonical Gospel. | Medium |
| Other apocrypha | Inventory only; not enough data yet for firm conclusions. | Low |

See [`conclusions/CONCLUSIONS.md`](conclusions/CONCLUSIONS.md) for the full argument, [`conclusions/EXECUTIVE_SUMMARY.md`](conclusions/EXECUTIVE_SUMMARY.md) for the short form, and [`conclusions/data/`](conclusions/data/) for the machine-readable models and case snippets.

## Visualizations (30 browser views)

`visualizations/` is a static HTML/CSS/SVG site with no framework. A single Python build step reads the four analysis packages and the rerun, then writes a compact bundle that every page consumes.

### Synoptic pages (19)

| # | View | What it shows |
| - | - | - |
| 01 | Synoptic map | Full verse-by-verse alignment across the active dataset |
| 02 | Block ribbon | Macro and micro blocks as a ribbon |
| 03 | Burden ledger | Directional-burden ledger per loose block |
| 04 | Gap timeline | Where one Gospel has material the other does not |
| 05 | Lexical drift | Lemma-level divergence across aligned pairs |
| 06 | Score classes | Distribution of pair scores |
| 07 | Block cards | Per-block summary cards |
| 08 | Stylistic markers | Book-level stylistic features |
| 09 | Pair explorer | Browse any primary pair with full diff |
| 10 | Displacement | Where secondary echoes land vs. their primary pair |
| 11 | Echo gallery | Secondary-echo catalog |
| 12 | Variants | SBLGNT apparatus notes attached to primary pairs |
| 13 | Triangle | Three-corner view of the three Synoptic datasets |
| 14 | Mask audit | Audit of which verses were masked as Markan (dataset 3 only) |
| 15 | Q core | Residual double-tradition core after Markan masking |
| 16 | Matthew verse card | Per-verse card for Matthew |
| 27 | Sensitivity · Mark–Matthew | Score × gap-penalty grid + Mark 16:9–20 text-critical sensitivity |
| 28 | Sensitivity · masked Q-core | Strict / medium / broad regime × chain-threshold sweep |
| 30 | Reader | Full SBLGNT text for Matt · Mark · Luke · John, with per-verse parallel badges, mask striping, and bidirectional links into every viz page |

Dataset switching is via URL hash: `#mm`, `#ml`, `#mld`. The active dataset is remembered per page.

### Low-verbatim pages (11)

| # | View | What it shows |
| - | - | - |
| 17 | JTEA overview | Landing page for the low-verbatim package |
| 18 | Intertext network | Arc diagram + network edges, filterable by layer, score, run length |
| 19 | Case studies | Targeted high-value cases with token-level diffs |
| 20 | John anchors | Anchor episodes, each with two hypothesis columns |
| 21 | Thomas parallels | Thomas logia with click-to-Coptic lookup |
| 22 | Concept signatures | Cross-corpus presence matrix + per-concept burden bars |
| 23 | Exact hits | Score × run scatter plus top filterable hits |
| 24 | Epistle × Gospel heatmap | Book-matrix cells with 4 metrics × 3 scales |
| 25 | Apocrypha inventory | M. R. James apocryphal works grouped by corpus |
| 29 | Claim → evidence | 67 interpretive claims each mapped to supporting artifacts + 3-axis confidence |
| 26 | Conclusions | Cross-package synthesis with dataset-linked evidence |

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

- The Greek lexical layer uses normalized surface forms and a heuristic stemmer, not a full morphological parser.
- Coptic Thomas is parsed from Coptic Scriptorium; Greek-to-Coptic direct literary dependence is not automatically scored.
- The apocrypha file is an inventory layer, not a full primary-language comparison.
- Candidate scores are retrieval scores, not probabilities.
- Scriptural and liturgical formulas can create long exact matches without proving Gospel dependence — those are flagged separately.
- The default medium mask regime is one auditable choice among several; page 28 lets you inspect the strict and broad alternatives side by side.
