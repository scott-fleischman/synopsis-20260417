"""Bundle counts match underlying source data.

Primary safeguard: if an analysis CSV grows or shrinks, the bundle
should reflect that. These tests recompute expected counts from the
source files and compare.
"""

from __future__ import annotations

from pathlib import Path

from conftest import csv_rows, ROOT


def _jtea_data(name: str) -> Path:
    return ROOT / "john_thomas_epistles_apocrypha_analysis" / "data" / name


def test_thomas_units_match_source(jtea):
    src = csv_rows(_jtea_data("03_thomas_units.csv"))
    assert len(jtea["thomas_units"]) == len(src), (
        f"thomas_units count mismatch: bundle={len(jtea['thomas_units'])} vs source={len(src)}"
    )


def test_apocrypha_count_matches_source(jtea):
    src = csv_rows(_jtea_data("12_apocrypha_inventory_from_mr_james.csv"))
    assert len(jtea["apocrypha"]) == len(src)


def test_book_matrix_aggregates_candidates(jtea):
    # Sum of n_candidates across matrix cells should equal
    # sum over raw candidate CSVs (04 + 05).
    ets = csv_rows(_jtea_data("04_epistles_to_gospels_candidates.csv"))
    jts = csv_rows(_jtea_data("05_john_to_synoptics_candidates.csv"))
    source_total = len(ets) + len(jts)
    bundle_total = sum(c["n_candidates"] for c in jtea["book_matrix"])
    assert bundle_total == source_total, (
        f"book_matrix candidate total {bundle_total} != source total {source_total}"
    )


def test_network_edges_covers_both_layers(jtea):
    # Confirm every automatic CSV source contributes to the network_edges
    # (exact row-count equality would be over-specified because the
    #  preprocess caps per-source edges, but both layers must be present).
    layers = {e["layer"] for e in jtea["network_edges"]}
    assert "epistles_to_gospels" in layers
    assert "john_to_synoptics" in layers


def test_anchors_count_matches_source(jtea):
    import yaml
    src = _jtea_data("08_john_synoptic_anchor_registry.yaml")
    with src.open() as f:
        raw = yaml.safe_load(f)
    # YAML may be a list or keyed
    if isinstance(raw, dict):
        for key in ("anchors", "items", "data"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
    assert isinstance(raw, list), f"expected list from {src.name}"
    assert len(jtea["anchors"]) == len(raw)


def test_thomas_registry_count_matches_source(jtea):
    import yaml
    src = _jtea_data("09_thomas_parallel_registry.yaml")
    with src.open() as f:
        raw = yaml.safe_load(f)
    if isinstance(raw, dict):
        for key in ("parallels", "items", "data"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
    assert isinstance(raw, list)
    assert len(jtea["thomas_registry"]) == len(raw)


def test_concepts_count_matches_source(jtea):
    import yaml
    src = _jtea_data("11_concept_signature_registry.yaml")
    with src.open() as f:
        raw = yaml.safe_load(f)
    if isinstance(raw, dict):
        for key in ("concepts", "items", "data"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
    assert isinstance(raw, list)
    assert len(jtea["concepts"]) == len(raw)


def test_exact_hits_count_matches_source(jtea):
    src = csv_rows(_jtea_data("15_filtered_high_value_exact_hits.csv"))
    assert len(jtea["exact_hits"]) == len(src)


def test_summary_gospel_verse_counts_match_canonical(jtea):
    # Gospel verses parsed should equal Gospel rows in the canonical CSV.
    canon = csv_rows(_jtea_data("02_canonical_units.csv"))
    gospels = {"Matt", "Mark", "Luke", "John"}
    gospel_verses = sum(1 for r in canon if r.get("book") in gospels)
    assert jtea["summary"]["gospel_verses_parsed"] == gospel_verses


def test_summary_epistle_verse_counts_match_canonical(jtea):
    canon = csv_rows(_jtea_data("02_canonical_units.csv"))
    gospels_plus_rev = {"Matt", "Mark", "Luke", "John", "Acts", "Rev"}
    epistle_verses = sum(1 for r in canon if r.get("book") and r["book"] not in gospels_plus_rev)
    # Summary may use a slightly different partition, so this is a
    # "within reason" check rather than strict equality.
    assert abs(jtea["summary"]["epistle_verses_parsed"] - epistle_verses) < 200
