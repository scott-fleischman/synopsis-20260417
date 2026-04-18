"""Bundle structure invariants.

Validates that the bundle.json keeps a shape the HTML pages rely on.
If upstream analysis YAML/CSV changes shape, these tests fail early.
"""

from __future__ import annotations


def test_bundle_has_four_datasets(bundle):
    for key in ("mm", "ml", "mld", "jtea"):
        assert key in bundle, f"missing dataset: {key}"


def test_synoptic_datasets_have_required_shape(bundle):
    for key in ("mm", "ml", "mld"):
        d = bundle[key]
        for required in ("name", "label", "summary", "pairs", "macro", "micro", "echoes", "burden"):
            assert required in d, f"{key} missing {required}"
        assert d["name"] == key
        assert isinstance(d["pairs"], list)
        assert len(d["pairs"]) > 0, f"{key} has no pairs"


def test_jtea_has_required_keys(jtea):
    required = {
        "name", "label", "summary", "method",
        "case_studies", "anchors", "thomas_registry", "thomas_units",
        "concepts", "burden_ledger", "exact_hits", "network_edges",
        "negspace_flags", "book_matrix", "books", "apocrypha",
    }
    missing = required - set(jtea.keys())
    assert not missing, f"jtea missing keys: {missing}"


def test_jtea_name_label(jtea):
    assert jtea["name"] == "jtea"
    assert "John" in jtea["label"] and "Thomas" in jtea["label"]


def test_jtea_summary_has_counts(jtea):
    s = jtea["summary"]
    assert "canonical_books_parsed" in s
    assert s["canonical_books_parsed"] > 20  # NT has 27 books
    assert s["gospel_verses_parsed"] > 3000
    assert s["epistle_verses_parsed"] > 2000


def test_jtea_network_edges_are_well_formed(jtea):
    edges = jtea["network_edges"]
    assert len(edges) > 1000, "expected many network edges"
    sample = edges[0]
    required = {"layer", "source_ref", "target_ref", "score", "max_exact_run_len"}
    assert required.issubset(sample.keys())
    layers = {e["layer"] for e in edges}
    # Two automatic Greek layers must always be present.
    assert "epistles_to_gospels" in layers
    assert "john_to_synoptics" in layers


def test_jtea_exact_hits_are_well_formed(jtea):
    hits = jtea["exact_hits"]
    assert len(hits) > 0
    for h in hits[:5]:
        assert "source_ref" in h
        assert "target_ref" in h
        assert "max_exact_run" in h
        assert isinstance(h["max_exact_run_len"], int)
        assert 0.0 <= h["score"] <= 1.0


def test_jtea_book_matrix_cells_well_formed(jtea):
    m = jtea["book_matrix"]
    assert len(m) > 0
    required = {"source_book", "target_book", "n_candidates", "n_score_ge_035",
                "n_exact_4plus", "max_score", "best"}
    for cell in m[:5]:
        assert required.issubset(cell.keys()), f"cell missing: {required - set(cell.keys())}"
        assert cell["target_book"] in {"Matt", "Mark", "Luke", "John"}


def test_jtea_anchors_shape(jtea):
    for a in jtea["anchors"]:
        assert "anchor_id" in a
        assert "john_refs" in a
        assert "synoptic_refs" in a
        # Most anchors carry both if-prior scenarios.
        assert "common_tradition_assessment" in a


def test_jtea_thomas_registry_shape(jtea):
    for r in jtea["thomas_registry"]:
        assert "thomas_logion" in r
        assert "canonical_refs" in r
        assert isinstance(r["canonical_refs"], list)
        assert "direct_dependence_burden" in r


def test_jtea_concept_burdens(jtea):
    # Each concept carries the four burden scores consulted by 22_concept_signatures.html
    for c in jtea["concepts"]:
        assert "concept_id" in c
        for field in ("direct_literary_burden", "oral_tradition_burden",
                      "common_written_source_burden", "independence_burden"):
            assert field in c, f"concept {c.get('concept_id')} missing {field}"


def test_jtea_apocrypha_has_corpus_groups(jtea):
    groups = {r["corpus_group"] for r in jtea["apocrypha"]}
    assert len(groups) >= 3, "expect multiple apocryphal corpus groups"


def test_jtea_scores_in_range(jtea):
    for e in jtea["network_edges"]:
        assert 0.0 <= e["score"] <= 1.0
    for h in jtea["exact_hits"]:
        assert 0.0 <= h["score"] <= 1.0


def test_jtea_case_studies_nonempty(jtea):
    assert len(jtea["case_studies"]) > 0


def test_jtea_thomas_units_parsed(jtea):
    units = jtea["thomas_units"]
    # Gospel of Thomas has 114 logia in canonical numbering
    assert len(units) > 100, f"expected ~114 Thomas units, got {len(units)}"
