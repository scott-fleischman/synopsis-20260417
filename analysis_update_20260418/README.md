# Synopsis reproducibility patch (2026-04-18)

This package addresses the main gaps identified in the repository review for `synopsis-20260417`.

## What is included

- Fully runnable analysis-generation scripts for:
  - Mark–Matthew rerun
  - Matthew–Luke masked double-tradition rerun
  - JTEA low-verbatim rerun/augmentation
- Local source copies used in the reruns
- Explicit attribution / license notes
- JSON-schema-style field schemas
- Invariant tests
- Updated rerun outputs with sensitivity and text-critical layers

## What changed relative to the earlier thread artifacts

1. **Code gap addressed**: `scripts/common.py`, `scripts/build_mark_matthew_rerun.py`,
   `scripts/build_matt_luke_double_masked_rerun.py`, `scripts/build_jtea_low_verbatim_rerun.py`,
   and `scripts/build_all.py` are included.
2. **Text-critical handling tightened**: if a verse becomes empty after double-bracket removal, the
   default lemma layer excludes it as well.
3. **Actual verse rows vs canonical verse slots separated**.
4. **Sensitivity layers added**:
   - Mark 16:9–20 sensitivity
   - score / threshold grids
   - multiple Markan mask regimes
5. **JTEA evidence separation added**:
   - automatic retrieval confidence
   - philological case strength
   - formula risk
   - claim-to-evidence links

## Coverage note

- The Mark–Matthew and Matthew–Luke masked reruns are regenerated from the local SBLGNT / apparatus /
  MorphGNT source base in this patch.
- The JTEA patch reruns the canonical Greek targeted-case and formula-risk layers from the local
  source base, but Thomas and broader apocrypha remain curated/reused registry layers rather than a
  fresh automatic cross-lingual dependence run.

## Main output directories

- `reruns/mark_matthew_rerun_robust/`
- `reruns/matt_luke_double_masked_rerun_robust/`
- `reruns/jtea_low_verbatim_rerun_robust/`

## Tests

Run:

```bash
python tests/test_invariants.py
```

## Build

Run:

```bash
python scripts/build_all.py
```