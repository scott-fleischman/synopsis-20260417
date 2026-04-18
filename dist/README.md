# dist/ — deployment snapshot

> *Snapshot of a site produced by **Claude Opus 4.7** (visualizations + build infrastructure) from data produced by **GPT-5.4 Pro** (the four analysis packages). Human role: prompting only. See the repo-level README for the full authorship breakdown.*

This directory is a committed build artifact: everything a static host needs to serve the visualizations, with no build step required.

**Do not edit files here directly.** The source of truth is `visualizations/`. Rebuild this directory from source after any change (see below).

## What's inside

```
dist/
├── index.html              # landing page
├── 01_*.html … 25_*.html   # 25 visualization pages
├── assets/
│   ├── shared.js           # DOM helpers, nav, dataset switcher
│   └── style.css           # site stylesheet
└── data/
    ├── bundle.js           # window.SYNOPSIS = {...} (for file:// use)
    └── bundle.json         # same payload, fetch-friendly
```

No external runtime dependencies. All data is embedded in `data/bundle.js`.

## Serve it

Any static file server works. Locally:

```bash
cd dist
python3 -m http.server 8000
```

Then open <http://localhost:8000/index.html>. Dataset switching on Synoptic pages is via URL hash (`#mm`, `#ml`, `#mld`).

Because `bundle.js` assigns to `window.SYNOPSIS` directly, the pages also work when opened as `file://…/dist/index.html` without any server.

## Rebuilding this snapshot

From the repo root:

```bash
python3 visualizations/build/preprocess.py
rm -rf dist
mkdir -p dist/assets dist/data
cp visualizations/*.html dist/
cp visualizations/assets/shared.js visualizations/assets/style.css dist/assets/
cp visualizations/data/bundle.js  visualizations/data/bundle.json  dist/data/
```

The preprocess step is deterministic — re-running on unchanged data produces a byte-identical bundle (enforced by `visualizations/tests/test_build_idempotence.py`).

## Why commit build output?

So the repository, as a single frozen artifact, contains all three layers end-to-end:

1. **Raw data** — the four analysis packages (`mark_matthew_analysis/`, `matt_luke_analysis/`, `matt_luke_double_masked_analysis/`, `john_thomas_epistles_apocrypha_analysis/`).
2. **Code** — the visualization pages and the Python build script (`visualizations/`).
3. **Output** — this directory (`dist/`).

A reviewer can inspect what was produced without having to run the build, and a diff of `dist/` across commits shows exactly what changed in the rendered site.
