# Attribution and provenance

This package is a derivative analysis layer built from prior local artifacts generated in the same research thread.

The input snapshots are stored under `inputs/previous_artifacts/`.

Ultimate text/data provenance represented in the previous artifacts:

- SBLGNT Greek text snapshots from the Faithlife / Logos SBLGNT repository.
- MorphGNT morphology/lemma layer for selected Greek books.
- Prior Mark–Matthew, Mark–Luke, Matthew–Luke, and John/Synoptic ledgers generated from those sources.

This package does not fetch external sources at build time. It uses the included input snapshots only.

## Important license note

The Greek text and morphology sources have their own licensing terms. This package is an analytical derivative and preserves provenance notes, but downstream users should verify licensing terms before redistribution in a different context.
