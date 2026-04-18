# docs/ — deployment snapshot (GitHub Pages output directory)

> *Snapshot of a site produced by **Claude Opus 4.7** (visualizations + build infrastructure) from data produced by **GPT-5.4 Pro** (the four analysis packages). Human role: prompting only. See the repo-level README for the full authorship breakdown.*

This directory is a committed build artifact: everything a static host needs to serve the visualizations, with no build step required. It is named `docs/` because GitHub Pages can serve a repo's `docs/` directory directly from the default branch — the name is structural, not documentary.

**Do not edit files here directly.** The source of truth is `visualizations/`. Rebuild this directory from source after any change (see below).

## What's inside

```
docs/
├── index.html              # research-question landing page (8 sections)
├── 01_*.html … 33_*.html   # 33 visualization pages (incl. reader, conclusions, claim/evidence, gospel square, thomas matrix, epistle dossier)
├── assets/
│   ├── shared.js           # DOM helpers, nav, dataset switcher
│   └── style.css           # site stylesheet
└── data/
    ├── bundle.js           # window.SYNOPSIS = {...} (for file:// use)
    └── bundle.json         # same payload, fetch-friendly
```

The 33 pages are grouped on the landing page into 8 research-question sections: Start here · Synoptic narrative · Q and double tradition · John and Synoptics · Thomas · Epistles and sayings · Apocrypha · Audit and reproducibility. See the repo-level README for the full per-page listing.

No external runtime dependencies. All data is embedded in `data/bundle.js`.

## Serve it

Any static file server works. Locally:

```bash
cd docs
python3 -m http.server 8000
```

Then open <http://localhost:8000/index.html>. Dataset switching on Synoptic pages is via URL hash (`#mm`, `#ml`, `#mld`).

Because `bundle.js` assigns to `window.SYNOPSIS` directly, the pages also work when opened as `file://…/docs/index.html` without any server.

## Rebuilding this snapshot

From the repo root:

```bash
python3 visualizations/build/preprocess.py
rm -rf docs
mkdir -p docs/assets docs/data
cp visualizations/*.html docs/
cp visualizations/assets/shared.js visualizations/assets/style.css docs/assets/
cp visualizations/data/bundle.js  visualizations/data/bundle.json  docs/data/
```

The preprocess step is deterministic — re-running on unchanged data produces a byte-identical bundle (enforced by `visualizations/tests/test_build_idempotence.py`).

## Why commit build output?

So the repository, as a single frozen artifact, contains all three layers end-to-end:

1. **Raw data** — the four analysis packages (`mark_matthew_analysis/`, `matt_luke_analysis/`, `matt_luke_double_masked_analysis/`, `john_thomas_epistles_apocrypha_analysis/`).
2. **Code** — the visualization pages and the Python build script (`visualizations/`).
3. **Output** — this directory (`docs/`).

A reviewer can inspect what was produced without having to run the build, and a diff of `docs/` across commits shows exactly what changed in the rendered site. GitHub Pages can also serve this directory as-is.
