"""Loaders for the 2026-04-18b high-priority supplement.

The supplement fills eight data gaps the review flagged: direct Mark-Luke,
three John pairwise packages (John-Mark, John-Matthew, John-Luke), a
canonical Gospel relationship square with real numbers, a Thomas logion
matrix, 60 epistle-Gospel case dossiers, a structured conclusion-evidence-
contrary navigation model, and a visualization priority order.

Every one of those layers is surfaced in the bundle under ``h18b`` so
downstream visualizations can read from a single source without branching
between "prior" and "new" shapes. The loader is deterministic: the same
input directory produces byte-identical output, which ``test_build_idempotence``
enforces.
"""

from __future__ import annotations

import csv
import json
from typing import Any

import yaml

from .preprocess_paths import ROOT


H18B_ROOT = ROOT / "analysis_update_20260418b"
H18B_DATA = H18B_ROOT / "data"


def _read_yaml(name: str) -> Any:
    p = H18B_DATA / name
    if not p.exists():
        return None
    with open(p) as f:
        return yaml.safe_load(f)


def _read_csv(name: str) -> list[dict[str, Any]]:
    p = H18B_DATA / name
    if not p.exists():
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


# ---- Mark-Luke direct (mkl) ----

def load_mkl_pairs() -> list[dict[str, Any]]:
    """Return Mark-Luke primary-chain pairs as a list of dicts shaped like
    mm/ml pairs where possible (a_* = source = Mark, b_* = target = Luke)."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("11_mark_luke_primary_chain_pairs.csv"):
        out.append({
            "rank": int(r["chain_rank"]),
            "a_ref": r["source_ref"],
            "b_ref": r["target_ref"],
            "a_idx": int(r["source_idx"]),
            "b_idx": int(r["target_idx"]),
            "a_tok": int(r["source_token_count"] or 0),
            "b_tok": int(r["target_token_count"] or 0),
            "score": float(r["score"]),
            "token_jaccard": float(r["token_jaccard"] or 0),
            "stem_jaccard": float(r["stem_jaccard"] or 0),
            "bigram_dice": float(r["bigram_dice"] or 0),
            "trigram_dice": float(r["trigram_dice"] or 0),
            "weighted_jaccard": float(r["weighted_jaccard"] or 0),
            "lcs_len": int(r["lcs_len"] or 0),
            "lcs_ratio": float(r["lcs_ratio"] or 0),
            "max_exact_run_len": int(r["max_exact_run_len"] or 0),
            "max_exact_run": r["max_exact_run"],
            "shared_content_token_count": int(r["shared_content_token_count"] or 0),
            "shared_content_tokens": r["shared_content_tokens"],
            "text_critical_status": r["source_text_critical_status"],
        })
    return out


def load_mkl_loose_blocks() -> list[dict[str, Any]]:
    return _read_yaml("12_mark_luke_loose_blocks.yaml") or []


def load_mkl_tight_blocks() -> list[dict[str, Any]]:
    return _read_yaml("13_mark_luke_tight_blocks.yaml") or []


def load_mkl_order_intervals() -> list[dict[str, Any]]:
    return _read_yaml("14_mark_luke_order_intervals.yaml") or []


def load_mkl_echoes() -> list[dict[str, Any]]:
    return _read_yaml("15_mark_luke_secondary_echoes.yaml") or []


def load_mkl_direction_ledger() -> list[dict[str, Any]]:
    return _read_yaml("17_mark_luke_direction_ledger_by_loose_block.yaml") or []


def load_mkl_burden_totals() -> dict[str, Any]:
    return _read_yaml("18_mark_luke_burden_totals.yaml") or {}


def load_mkl_summary() -> dict[str, Any]:
    return _read_yaml("19_mark_luke_global_summary.yaml") or {}


def load_mkl_sensitivity_grid() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in _read_csv("20_mark_luke_sensitivity_score_grid.csv"):
        out.append({
            "threshold": float(r["threshold"]),
            "source_gap_allowance": int(r["source_gap_allowance"]),
            "target_gap_allowance": int(r["target_gap_allowance"]),
            "chain_pair_count": int(r["chain_pair_count"]),
            "chain_score_sum": float(r["chain_score_sum"]),
            "block_count": int(r["block_count"]),
            "avg_pairs_per_block": float(r["avg_pairs_per_block"]),
        })
    return out


def load_mkl_mark_ending_sensitivity() -> dict[str, Any]:
    return _read_yaml("21_mark_luke_mark_ending_sensitivity.yaml") or {}


def load_mkl_pair_diffs_detailed() -> list[dict[str, Any]]:
    """Load 16b detailed pair diffs as a list of JSONL dicts (token-level diffs)."""
    p = H18B_DATA / "16b_mark_luke_pair_diffs_detailed.jsonl"
    if not p.exists():
        return []
    out: list[dict[str, Any]] = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def build_mkl() -> dict[str, Any]:
    """Build the Mark-Luke direct dataset in a shape parallel to mm/ml."""
    summary = load_mkl_summary()
    burden = load_mkl_burden_totals()
    pairs = load_mkl_pairs()
    loose = load_mkl_loose_blocks()
    tight = load_mkl_tight_blocks()
    order = load_mkl_order_intervals()
    echoes = load_mkl_echoes()
    ledger = load_mkl_direction_ledger()
    grid = load_mkl_sensitivity_grid()
    ending = load_mkl_mark_ending_sensitivity()
    diffs = load_mkl_pair_diffs_detailed()

    return {
        "name": "mkl",
        "a_book": "Mark",
        "b_book": "Luke",
        "label": "Mark ↔ Luke (direct)",
        "summary": summary,
        "burden_totals": burden,
        "pairs": pairs,
        "loose_blocks": loose,
        "tight_blocks": tight,
        "order_intervals": order,
        "echoes": echoes,
        "direction_ledger": ledger,
        "sensitivity_grid": grid,
        "mark_ending_sensitivity": ending,
        "pair_diffs_detailed": diffs,
    }


# ---- Canonical Gospel relationship square ----

def load_gospel_square() -> dict[str, Any]:
    rows = _read_yaml("41_canonical_gospel_relationship_square.yaml")
    if not rows:
        return {}
    return {
        "rows": rows.get("rows", []) if isinstance(rows, dict) else rows,
        "purpose": rows.get("purpose", "") if isinstance(rows, dict) else "",
        "important_note": rows.get("important_note", "") if isinstance(rows, dict) else "",
    }


# ---- John pairwise ----

def load_john_pairwise_anchors() -> list[dict[str, Any]]:
    return _read_yaml("37_john_synoptic_pairwise_anchor_registry.yaml") or []


def load_john_pairwise_summary() -> list[dict[str, Any]]:
    return _read_yaml("38_john_synoptic_pairwise_global_summary.yaml") or []


def load_john_pairwise_support_contra() -> list[dict[str, Any]]:
    return _read_yaml("39_john_synoptic_pairwise_support_contra.yaml") or []


def load_john_window_candidates() -> dict[str, list[dict[str, Any]]]:
    """Top-5 window candidates in both directions for each Gospel pair."""
    def _read(name: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for r in _read_csv(name):
            out.append({k: (v if isinstance(v, str) else v) for k, v in r.items()})
        return out

    return {
        "mark_to_john_top5": _read("33_mark_to_john_window_candidates_top5.csv"),
        "matt_to_john_top5": _read("34_matthew_to_john_window_candidates_top5.csv"),
        "luke_to_john_top5": _read("35_luke_to_john_window_candidates_top5.csv"),
    }


def build_john_pairwise() -> dict[str, Any]:
    return {
        "anchors": load_john_pairwise_anchors(),
        "summary": load_john_pairwise_summary(),
        "support_contra": load_john_pairwise_support_contra(),
        "windows": load_john_window_candidates(),
    }


# ---- Thomas matrix + dossiers ----

def load_thomas_matrix_rows() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in _read_csv("50_thomas_gospel_logion_matrix.csv"):
        out.append({
            "logion": r["thomas_logion"],
            "word_count": int(r["word_count"] or 0),
            "lemma_count": int(r["lemma_count"] or 0),
            "registered_parallel_count": int(r["registered_parallel_count"] or 0),
            "motifs": r["motifs"],
            "matthew_refs": r["matthew_refs"],
            "mark_refs": r["mark_refs"],
            "luke_refs": r["luke_refs"],
            "john_refs": r["john_refs"],
            "relation_type": r["relation_type"],
            "matrix_strength": r["matrix_strength"],
            "direct_dependence_burden_labels": r["direct_dependence_burden_labels"],
            "best_first_model": r["best_first_model"],
            "coptic_greek_caveat": r["coptic_greek_caveat"],
        })
    return out


def load_thomas_dossiers() -> list[dict[str, Any]]:
    return _read_yaml("51_thomas_logion_dossiers.yaml") or []


def load_thomas_global() -> dict[str, Any]:
    return _read_yaml("52_thomas_global_summary.yaml") or {}


def build_thomas() -> dict[str, Any]:
    return {
        "matrix": load_thomas_matrix_rows(),
        "dossiers": load_thomas_dossiers(),
        "summary": load_thomas_global(),
    }


# ---- Epistle dossiers ----

def load_epistle_dossiers() -> list[dict[str, Any]]:
    return _read_yaml("60_epistle_gospel_case_dossiers.yaml") or []


def load_epistle_targeted_table() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in _read_csv("61_epistle_gospel_targeted_case_table.csv"):
        out.append({
            "case_id": r["case_id"],
            "source_ref": r["source_ref"],
            "target_ref": r["target_ref"],
            "feature": r["feature"],
            "formula_risk": r["formula_risk"],
            "automatic_retrieval_support": r["automatic_retrieval_support"],
            "philological_case_strength": r["philological_case_strength"],
            "best_current_model": r["best_current_model"],
            "max_exact_run_len": int(r["max_exact_run_len"] or 0),
            "score": float(r["score"] or 0),
        })
    return out


def load_epistle_ranked_candidates() -> list[dict[str, Any]]:
    """Top 500 ranked epistle-to-Gospel candidates; keep compact and string-clean."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("62_epistle_gospel_ranked_candidate_cases_top500.csv"):
        out.append({k: (v if v is not None else "") for k, v in r.items()})
    return out


def load_epistle_summary() -> dict[str, Any]:
    return _read_yaml("63_epistle_gospel_global_summary.yaml") or {}


def build_epistle_dossiers() -> dict[str, Any]:
    return {
        "cases": load_epistle_dossiers(),
        "targeted_table": load_epistle_targeted_table(),
        "ranked_top500": load_epistle_ranked_candidates(),
        "summary": load_epistle_summary(),
    }


# ---- Conclusion navigation + priority order ----

def load_conclusion_nav() -> list[dict[str, Any]]:
    return _read_yaml("70_conclusion_evidence_contrary_navigation.yaml") or []


def load_priority_order() -> list[dict[str, Any]]:
    return _read_yaml("42_visualization_priority_order.yaml") or []


def load_method() -> dict[str, Any]:
    return _read_yaml("01_method_high_priority_supplement.yaml") or {}


def load_missing_data_status() -> dict[str, Any]:
    return _read_yaml("72_missing_data_status.yaml") or {}


# ---- Top-level build ----

def build_h18b() -> dict[str, Any]:
    """Assemble the entire 18b supplement as a single bundle key."""
    return {
        "method": load_method(),
        "mkl": build_mkl(),
        "gospel_square": load_gospel_square(),
        "john_pairwise": build_john_pairwise(),
        "thomas": build_thomas(),
        "epistle_dossiers": build_epistle_dossiers(),
        "conclusion_nav": load_conclusion_nav(),
        "priority_order": load_priority_order(),
        "missing_data_status": load_missing_data_status(),
    }
