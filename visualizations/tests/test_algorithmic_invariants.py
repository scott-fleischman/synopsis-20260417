"""Algorithmic invariants on the bundled data.

Where earlier tests verify that the bundle *shape* matches what pages expect
(structure, required keys, layer values), these tests verify properties the
pipeline's **algorithms** must satisfy: monotonicity of the primary chain,
uniqueness of pair endpoints, score ranges, no duplication of primaries as
secondaries, and consistency of block interval tables with pair rows.

Violations here indicate that the bundle is structurally valid but the
underlying data is internally inconsistent — a stronger check than simple
"loaded OK". Covers review item #10.
"""

from __future__ import annotations


def _synoptic_keys():
    return ("mm", "ml", "mld")


# --- Primary chain monotonicity ---------------------------------------------


def test_primary_chain_is_strictly_monotonic_in_a(bundle):
    """For each synoptic dataset the primary chain must be strictly increasing
    in the ``a`` (source) index: no verse revisited, no out-of-order pair."""
    for key in _synoptic_keys():
        pairs = bundle[key]["pairs"]
        a_idxs = [p["a_idx"] for p in pairs if p["a_idx"] >= 0]
        for i in range(1, len(a_idxs)):
            assert a_idxs[i] > a_idxs[i - 1], (
                f"{key} primary chain not strictly monotonic in a at pair #{i}: "
                f"{a_idxs[i - 1]} → {a_idxs[i]}"
            )


def test_primary_chain_is_strictly_monotonic_in_b(bundle):
    """Monotonicity in ``b`` (target) index is required by the chain-building
    algorithm; violations mean two primary pairs cross."""
    for key in _synoptic_keys():
        pairs = bundle[key]["pairs"]
        b_idxs = [p["b_idx"] for p in pairs if p["b_idx"] >= 0]
        for i in range(1, len(b_idxs)):
            assert b_idxs[i] > b_idxs[i - 1], (
                f"{key} primary chain not strictly monotonic in b at pair #{i}: "
                f"{b_idxs[i - 1]} → {b_idxs[i]}"
            )


def test_primary_chain_no_duplicate_refs(bundle):
    """No verse appears on either side of the chain more than once."""
    for key in _synoptic_keys():
        pairs = bundle[key]["pairs"]
        a_refs = [p["a_ref"] for p in pairs]
        b_refs = [p["b_ref"] for p in pairs]
        assert len(a_refs) == len(set(a_refs)), f"{key} duplicate a_ref in primary chain"
        assert len(b_refs) == len(set(b_refs)), f"{key} duplicate b_ref in primary chain"


# --- Score ranges ------------------------------------------------------------


def test_pair_scores_are_in_unit_range(bundle):
    for key in _synoptic_keys():
        for p in bundle[key]["pairs"]:
            assert 0.0 <= p["score"] <= 1.0, f"{key} pair score out of range: {p['score']}"


def test_echo_scores_are_in_unit_range(bundle):
    for key in _synoptic_keys():
        for e in bundle[key]["echoes"]:
            assert 0.0 <= e["score"] <= 1.0, f"{key} echo score out of range: {e['score']}"


def test_macro_block_avg_scores_are_in_unit_range(bundle):
    for key in _synoptic_keys():
        for b in bundle[key]["macro"]:
            assert 0.0 <= b["avg_score"] <= 1.0, (
                f"{key} macro block {b.get('id')} avg_score out of range: {b['avg_score']}"
            )


# --- Secondary echoes vs primary pairs --------------------------------------


def test_secondary_echoes_do_not_duplicate_primary_pairs(bundle):
    """Primary pairs and secondary echoes partition the alignment evidence;
    overlap would double-count the same pair in visualizations."""
    for key in _synoptic_keys():
        pair_keys = {(p["a_ref"], p["b_ref"]) for p in bundle[key]["pairs"]}
        echo_keys = {(e["a_ref"], e["b_ref"]) for e in bundle[key]["echoes"]}
        overlap = pair_keys & echo_keys
        assert not overlap, (
            f"{key}: {len(overlap)} pair(s) appear in both primary chain and echoes, "
            f"e.g. {next(iter(overlap))}"
        )


# --- Block interval consistency ---------------------------------------------


def test_macro_block_intervals_are_non_degenerate(bundle):
    """Start ≤ end in both a and b dimensions for every macro block."""
    for key in _synoptic_keys():
        for b in bundle[key]["macro"]:
            assert b["a_start_idx"] <= b["a_end_idx"], (
                f"{key} macro block {b['id']}: a_start_idx > a_end_idx"
            )
            assert b["b_start_idx"] <= b["b_end_idx"], (
                f"{key} macro block {b['id']}: b_start_idx > b_end_idx"
            )


def test_macro_block_pair_counts_match_pairs_in_interval(bundle):
    """Mark–Matthew pairs carry explicit ``macro`` IDs; count the pairs per
    macro and compare to the block table's ``pair_count`` column."""
    pairs = bundle["mm"]["pairs"]
    counts_by_macro: dict[int, int] = {}
    for p in pairs:
        m = p.get("macro")
        if m is not None:
            counts_by_macro[m] = counts_by_macro.get(m, 0) + 1
    for b in bundle["mm"]["macro"]:
        expected = counts_by_macro.get(b["id"], 0)
        assert b["pair_count"] == expected, (
            f"mm macro block {b['id']}: table says {b['pair_count']} pairs, "
            f"primary chain contains {expected}"
        )


# --- Verse counts (review #4) -----------------------------------------------


def test_bundle_exposes_actual_and_canonical_verse_counts(bundle):
    for key in _synoptic_keys():
        meta = bundle[key]["meta"]
        for side in ("a_verse_counts", "b_verse_counts"):
            vc = meta.get(side)
            assert vc is not None, f"{key}.meta.{side} missing"
            assert "canonical_slot_count" in vc
            assert "actual_unit_count" in vc
            assert "missing_canonical_slots" in vc
            # By definition the number of missing slots equals the difference.
            gap = vc["canonical_slot_count"] - vc["actual_unit_count"]
            assert len(vc["missing_canonical_slots"]) == gap, (
                f"{key}.meta.{side} missing-slot count mismatch: "
                f"{len(vc['missing_canonical_slots'])} listed, {gap} expected"
            )


def test_mark_canonical_slots_exceed_actual_units(bundle):
    """Mark's SBLGNT text omits several traditional verse numbers (e.g. 7:16,
    9:44, 9:46, 11:26, 15:28), so canonical_slot_count must exceed
    actual_unit_count for Mark."""
    vc = bundle["mm"]["meta"]["a_verse_counts"]  # Mark is the ``a`` book in mm
    assert vc["canonical_slot_count"] > vc["actual_unit_count"], (
        f"Mark: canonical={vc['canonical_slot_count']} should exceed "
        f"actual={vc['actual_unit_count']}"
    )
    # Spot-check a couple of known-omitted verses if Mark reaches those chapters.
    missing_set = set(vc["missing_canonical_slots"])
    for ref in ("Mark 9:44", "Mark 9:46"):
        assert ref in missing_set, f"expected {ref} to be in Mark's missing_canonical_slots"


# --- JTEA invariants ---------------------------------------------------------


def test_jtea_network_edge_scores_in_unit_range(bundle):
    for e in bundle["jtea"]["network_edges"]:
        assert 0.0 <= e["score"] <= 1.0, f"jtea edge score out of range: {e['score']}"


def test_jtea_exact_hit_run_lengths_nonneg(bundle):
    for h in bundle["jtea"]["exact_hits"]:
        assert h["max_exact_run_len"] >= 0


def test_jtea_exact_hit_flags_by_ref_shape(bundle):
    flags = bundle["jtea"].get("exact_hit_flags_by_ref", {})
    assert isinstance(flags, dict)
    if flags:
        sample_key, sample_val = next(iter(flags.items()))
        assert "|" in sample_key, "flag lookup key should be 'source_ref|target_ref'"
        assert set(sample_val.keys()) >= {"flags", "rule", "risk"}
        assert sample_val["risk"] in ("low", "medium", "high")
