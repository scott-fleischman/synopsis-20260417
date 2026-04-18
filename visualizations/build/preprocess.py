#!/usr/bin/env python3
"""Preprocess the four analysis packages into a single compact JSON bundle.

Outputs:
    visualizations/data/bundle.json — for fetch-based consumption
    visualizations/data/bundle.js   — ``window.SYNOPSIS = {...}`` for file:// use

Each synoptic dataset is normalized to generic a/b fields (a = earlier/source,
b = later/target), so one shared JS code path renders Mark–Matthew,
Matthew–Luke, or the Markan-masked Matt–Luke views interchangeably. The
low-verbatim JTEA package is packed separately because it has no single
primary chain — see ``loaders_jtea``.

The build is deterministic: re-running on unchanged inputs produces a
byte-identical bundle. This is enforced by ``test_build_idempotence.py``.

Modules
-------
- ``dataset``           — ``Dataset`` class, ref→index mapping, verse counts.
- ``loaders_synoptic``  — mm + ml loaders and shared helpers.
- ``loaders_mld``       — Markan-masked Matt–Luke loaders.
- ``loaders_jtea``      — John/Thomas/Epistles/Apocrypha loaders.
- ``preprocess_paths``  — shared path constants.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running as a script (``python3 visualizations/build/preprocess.py``)
# by inserting the parent of the ``build`` package onto sys.path.
if __package__ in (None, ""):
    _HERE = Path(__file__).resolve().parent
    sys.path.insert(0, str(_HERE.parent))
    from build.dataset import Dataset  # type: ignore[no-redef]
    from build.loaders_synoptic import (  # type: ignore[no-redef]
        load_burden,
        load_gaps,
        load_ledger,
        load_lemma_deltas,
        load_loose_full,
        load_mm_detailed,
        load_mm_echoes,
        load_mm_macro,
        load_mm_micro,
        load_mm_pairs,
        load_ml_detailed,
        load_ml_echoes,
        load_ml_macro,
        load_ml_micro,
        load_ml_pairs,
        load_negspace,
        load_summary,
        load_variants,
    )
    from build.loaders_mld import (  # type: ignore[no-redef]
        load_mld_burden,
        load_mld_detailed,
        load_mld_echoes,
        load_mld_gaps,
        load_mld_ledger,
        load_mld_lemma_deltas,
        load_mld_loose_full,
        load_mld_macro,
        load_mld_mask_audit,
        load_mld_micro,
        load_mld_negspace,
        load_mld_pairs,
        load_mld_summary,
    )
    from build.loaders_jtea import (  # type: ignore[no-redef]
        JTEA_ROOT,
        load_jtea_anchors,
        load_jtea_apocrypha,
        load_jtea_book_matrix,
        load_jtea_burden_ledger,
        load_jtea_canonical_book_counts,
        load_jtea_case_studies,
        load_jtea_concepts,
        load_jtea_exact_hit_flags_by_ref,
        load_jtea_exact_hits,
        load_jtea_method,
        load_jtea_negspace_flags,
        load_jtea_network_edges,
        load_jtea_summary,
        load_jtea_thomas_registry,
        load_jtea_thomas_units,
    )
    from build.preprocess_paths import OUT, ROOT  # type: ignore[no-redef]
else:  # imported as a package member
    from .dataset import Dataset
    from .loaders_synoptic import (
        load_burden,
        load_gaps,
        load_ledger,
        load_lemma_deltas,
        load_loose_full,
        load_mm_detailed,
        load_mm_echoes,
        load_mm_macro,
        load_mm_micro,
        load_mm_pairs,
        load_ml_detailed,
        load_ml_echoes,
        load_ml_macro,
        load_ml_micro,
        load_ml_pairs,
        load_negspace,
        load_summary,
        load_variants,
    )
    from .loaders_mld import (
        load_mld_burden,
        load_mld_detailed,
        load_mld_echoes,
        load_mld_gaps,
        load_mld_ledger,
        load_mld_lemma_deltas,
        load_mld_loose_full,
        load_mld_macro,
        load_mld_mask_audit,
        load_mld_micro,
        load_mld_negspace,
        load_mld_pairs,
        load_mld_summary,
    )
    from .loaders_jtea import (
        JTEA_ROOT,
        load_jtea_anchors,
        load_jtea_apocrypha,
        load_jtea_book_matrix,
        load_jtea_burden_ledger,
        load_jtea_canonical_book_counts,
        load_jtea_case_studies,
        load_jtea_concepts,
        load_jtea_exact_hit_flags_by_ref,
        load_jtea_exact_hits,
        load_jtea_method,
        load_jtea_negspace_flags,
        load_jtea_network_edges,
        load_jtea_summary,
        load_jtea_thomas_registry,
        load_jtea_thomas_units,
    )
    from .preprocess_paths import OUT, ROOT


OUT.mkdir(parents=True, exist_ok=True)


def _meta_with_counts(ds: Dataset) -> dict:
    """Bundle metadata including actual vs canonical verse counts (review #4)."""
    return {
        "a_total_verses": ds.a_total,
        "b_total_verses": ds.b_total,
        "a_chapters": ds.chap_info(ds.a_book),
        "b_chapters": ds.chap_info(ds.b_book),
        "a_verse_counts": ds.verse_counts(ds.a_book),
        "b_verse_counts": ds.verse_counts(ds.b_book),
    }


def build_mm() -> dict:
    ds = Dataset(
        "mm",
        ROOT / "mark_matthew_analysis",
        a_book="Mark",
        b_book="Matt",
        label="Mark ↔ Matthew",
    )
    return {
        "name": ds.name,
        "a_book": ds.a_book,
        "b_book": ds.b_book,
        "label": ds.label,
        "meta": _meta_with_counts(ds),
        "pairs": load_mm_pairs(ds),
        "macro": load_mm_macro(ds),
        "micro": load_mm_micro(ds),
        "echoes": load_mm_echoes(ds),
        "gaps": load_gaps(ds),
        "summary": load_summary(ds),
        "ledger": load_ledger(ds),
        "burden": load_burden(ds),
        "negspace": load_negspace(ds),
        "lemma_deltas": load_lemma_deltas(ds),
        "loose_full": load_loose_full(ds),
        "variants": load_variants(ds),
        "detailed": load_mm_detailed(ds),
    }


def build_ml() -> dict:
    ds = Dataset(
        "ml",
        ROOT / "matt_luke_analysis",
        a_book="Matt",
        b_book="Luke",
        label="Matthew ↔ Luke",
    )
    return {
        "name": ds.name,
        "a_book": ds.a_book,
        "b_book": ds.b_book,
        "label": ds.label,
        "meta": _meta_with_counts(ds),
        "pairs": load_ml_pairs(ds),
        "macro": load_ml_macro(ds),
        "micro": load_ml_micro(ds),
        "echoes": load_ml_echoes(ds),
        "gaps": load_gaps(ds),
        "summary": load_summary(ds),
        "ledger": load_ledger(ds),
        "burden": load_burden(ds),
        "negspace": load_negspace(ds),
        "lemma_deltas": load_lemma_deltas(ds),
        "loose_full": load_loose_full(ds),
        "variants": load_variants(ds),
        "detailed": load_ml_detailed(ds),
    }


def build_mld() -> dict:
    ds = Dataset(
        "mld",
        ROOT / "matt_luke_double_masked_analysis",
        a_book="Matt",
        b_book="Luke",
        label="Matt ↔ Luke (Markan-masked)",
    )
    mask_audit = load_mld_mask_audit(ds)

    rule_counts_by_book: dict[str, dict[str, int]] = {}
    masked_idx_by_book: dict[str, list[int]] = {"Matt": [], "Luke": []}
    for row in mask_audit:
        rule_counts_by_book.setdefault(row["book"], {}).setdefault(row["mask_rule"], 0)
        rule_counts_by_book[row["book"]][row["mask_rule"]] += 1
        if row["masked_as_markan"]:
            masked_idx_by_book.setdefault(row["book"], []).append(row["idx"])

    meta = _meta_with_counts(ds)
    meta["mask_rule_counts"] = rule_counts_by_book
    meta["masked_idx"] = masked_idx_by_book

    return {
        "name": ds.name,
        "a_book": ds.a_book,
        "b_book": ds.b_book,
        "label": ds.label,
        "meta": meta,
        "pairs": load_mld_pairs(ds),
        "macro": load_mld_macro(ds),
        "micro": load_mld_micro(ds),
        "echoes": load_mld_echoes(ds),
        "gaps": load_mld_gaps(ds),
        "summary": load_mld_summary(ds),
        "ledger": load_mld_ledger(ds),
        "burden": load_mld_burden(ds),
        "negspace": load_mld_negspace(ds),
        "mask_audit": mask_audit,
        "lemma_deltas": load_mld_lemma_deltas(ds),
        "loose_full": load_mld_loose_full(ds),
        "variants": load_variants(ds),
        "detailed": load_mld_detailed(ds),
    }


def build_jtea() -> dict:
    return {
        "name": "jtea",
        "label": "John · Thomas · Epistles · Apocrypha",
        "summary": load_jtea_summary(),
        "method": load_jtea_method(),
        "case_studies": load_jtea_case_studies(),
        "anchors": load_jtea_anchors(),
        "thomas_registry": load_jtea_thomas_registry(),
        "thomas_units": load_jtea_thomas_units(),
        "concepts": load_jtea_concepts(),
        "burden_ledger": load_jtea_burden_ledger(),
        "exact_hits": load_jtea_exact_hits(),
        "network_edges": load_jtea_network_edges(),
        "negspace_flags": load_jtea_negspace_flags(),
        "exact_hit_flags_by_ref": load_jtea_exact_hit_flags_by_ref(),
        "book_matrix": load_jtea_book_matrix(),
        "books": load_jtea_canonical_book_counts(),
        "apocrypha": load_jtea_apocrypha(),
    }


def _load_conclusions() -> dict:
    """Bundle ``conclusions/data/`` so 26_conclusions.html can render from the live bundle.

    Returns an empty dict if the conclusions directory is absent (e.g. in a
    partial checkout). This keeps the bundle backwards compatible.
    """
    import csv as _csv
    import yaml as _yaml

    conc_root = ROOT / "conclusions" / "data"
    if not conc_root.exists():
        return {}

    def _read_yaml(name: str):
        p = conc_root / name
        if not p.exists():
            return None
        with open(p) as f:
            return _yaml.safe_load(f)

    def _read_csv(name: str):
        p = conc_root / name
        if not p.exists():
            return []
        with open(p, newline="") as f:
            return list(_csv.DictReader(f))

    return {
        "confidence_table": _read_csv("01_confidence_table.csv"),
        "per_comparison_models": _read_yaml("02_per_comparison_models.yaml"),
        "case_snippets": _read_yaml("03_case_snippets.yaml"),
        "overall_model": _read_yaml("04_overall_model.yaml"),
    }


def main() -> None:
    print("Building mm (Mark–Matthew)...")
    mm = build_mm()
    print(f"  {len(mm['pairs'])} pairs, {len(mm['macro'])} macro blocks, {len(mm['echoes'])} echoes")

    print("Building ml (Matthew–Luke)...")
    ml = build_ml()
    print(f"  {len(ml['pairs'])} pairs, {len(ml['macro'])} macro blocks, {len(ml['echoes'])} echoes")

    print("Building mld (Matt–Luke, Markan-masked)...")
    mld = build_mld()
    print(
        f"  {len(mld['pairs'])} pairs, {len(mld['macro'])} macro blocks, "
        f"{len(mld['echoes'])} echoes, {len(mld['mask_audit'])} mask rows"
    )

    print("Building jtea (John · Thomas · Epistles · Apocrypha)...")
    jtea = build_jtea()
    print(
        f"  {len(jtea['case_studies'])} case studies, {len(jtea['anchors'])} anchors, "
        f"{len(jtea['thomas_registry'])} thomas parallels, {len(jtea['concepts'])} concepts, "
        f"{len(jtea['network_edges'])} network edges, {len(jtea['exact_hits'])} exact hits, "
        f"{len(jtea['book_matrix'])} matrix cells"
    )

    conclusions = _load_conclusions()
    if conclusions:
        print(
            f"Bundling conclusions/: {len(conclusions.get('confidence_table') or [])} rows, "
            f"{len(conclusions.get('case_snippets') or [])} case snippets"
        )

    bundle = {"mm": mm, "ml": ml, "mld": mld, "jtea": jtea, "conclusions": conclusions}

    jsfile = OUT / "bundle.js"
    with open(jsfile, "w") as f:
        f.write("window.SYNOPSIS = ")
        json.dump(bundle, f, separators=(",", ":"), ensure_ascii=False)
        f.write(";\n")
    print(f"Wrote {jsfile} ({jsfile.stat().st_size:,} bytes)")

    jsonfile = OUT / "bundle.json"
    with open(jsonfile, "w") as f:
        json.dump(bundle, f, separators=(",", ":"), ensure_ascii=False)
    print(f"Wrote {jsonfile} ({jsonfile.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
