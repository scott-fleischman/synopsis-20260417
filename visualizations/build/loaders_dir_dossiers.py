"""Loaders for the 2026-04-18 Synoptic + John directional hypothesis dossiers.

The dossiers package answers a direction-specific question that pairwise
similarity matrices cannot: *if this Gospel used that Gospel, what exactly
must the redactor have changed, added, omitted, or reordered, and what
evidence counts against the direction?*

Every dataset in the package is surfaced under ``bundle.dir_dossiers`` so
pages 36 (registry), 37 (per-direction dossier), and 38 (system hypothesis
space) can render from a single bundle key. Governance prose in
AUTHORITATIVE_NUMBERS.yaml, METHODS.md, and README.md cites the same
burden-summary numbers to keep prose and bundle in step.

Layer map
---------
- ``registry``              — 12 direction hypotheses with required
  explanations, contrary evidence, and best-response models.
- ``burden_summary``        — direct-use burden scores across the main
  directional pairs; lower is better, not a probability.
- ``support_contra_matrix`` — per-direction support and contrary counts
  with John anchor counts.
- ``conclusion_ranking``    — current ranked conclusions and additional
  key-direction notes.
- ``system_hypothesis_space`` — five system-level models beyond pairwise
  directions (two-source, Farrer, Griesbach, proto-Mark, John shared-anchor).
- ``order_displacement_summary`` — pair-level displacement behavior
  (primary blocks, secondary echoes, chain character).
- ``pair_change_summary``   — per-direction token-level pair metrics
  (mean score, mean Jaccard, mean exact-run length, target-longer
  percentage) across 12 directions.
- ``top_gap_burdens``       — flat table of the largest material-gap
  burdens across all directions.
- ``response_models``       — per-direction YAML dossiers with ``hypothesis``,
  ``supporting_evidence``, ``contrary_evidence``, ``best_response_model``,
  ``quantitative_indicators``, ``top_material_gap_burdens``, and
  ``what_would_{strengthen,weaken}_this_hypothesis`` lists.
- ``john_anchor_dossiers``  — per-direction grouped John anchor dossiers
  with best-pair data and best-current-model fields for all 6 John-related
  directions.
"""

from __future__ import annotations

import csv
from typing import Any

import yaml

from .preprocess_paths import ROOT


DD_ROOT = ROOT / "synoptic_john_directional_dossiers_20260418"
DD_DATA = DD_ROOT / "data"
DD_REPORTS = DD_ROOT / "reports"


def _read_yaml(relpath: str, *, root=DD_DATA) -> Any:
    p = root / relpath
    if not p.exists():
        return None
    with open(p) as f:
        return yaml.safe_load(f)


def _read_csv(relpath: str, *, root=DD_DATA) -> list[dict[str, Any]]:
    p = root / relpath
    if not p.exists():
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def _f(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _i(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---- 01 Direction hypotheses registry ----


def load_registry() -> list[dict[str, Any]]:
    """Twelve-direction registry with required explanations and response models."""
    data = _read_yaml("01_direction_hypotheses_registry.yaml") or []
    out: list[dict[str, Any]] = []
    for r in data:
        out.append(
            {
                "direction_id": r.get("direction_id") or "",
                "short_label": r.get("short_label") or "",
                "source": r.get("source") or "",
                "target": r.get("target") or "",
                "pair": r.get("pair") or "",
                "model_family": r.get("model_family") or "",
                "current_status": r.get("current_status") or "",
                "core_required_explanations": r.get("core_required_explanations") or [],
                "core_contrary_evidence": r.get("core_contrary_evidence") or [],
                "best_response_model": r.get("best_response_model") or "",
            }
        )
    return out


# ---- 03 Direction burden summary ----


def load_burden_summary() -> list[dict[str, Any]]:
    """Comparable burden scores across directions and burden models."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("03_direction_burden_summary.csv"):
        out.append(
            {
                "direction_id": r.get("direction_id") or "",
                "pair": r.get("pair") or "",
                "burden_model": r.get("burden_model") or "",
                "burden_score": _f(r.get("burden_score")),
                "notes": r.get("notes") or "",
            }
        )
    return out


# ---- 04 System hypothesis space ----


def load_system_hypothesis_space() -> dict[str, Any]:
    """Five system-level models beyond pairwise directions."""
    return _read_yaml("04_system_hypothesis_space.yaml") or {}


# ---- 32 Order preservation / displacement summary ----


def load_order_displacement_summary() -> list[dict[str, Any]]:
    """Pair-level displacement character."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("32_order_preservation_and_displacement_summary.csv"):
        out.append(
            {
                "pair": r.get("pair") or "",
                "pair_primary_block_count": _i(r.get("pair_primary_block_count")),
                "pair_secondary_echo_count": _i(r.get("pair_secondary_echo_count")),
                "characterization": r.get("characterization") or "",
            }
        )
    return out


# ---- 52 Per-direction pair change summary ----


def load_pair_change_summary() -> list[dict[str, Any]]:
    """Per-direction token-level aggregates across 12 directions."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("52_primary_pair_change_summary_by_direction.csv"):
        out.append(
            {
                "direction_id": r.get("direction_id") or "",
                "pair_count": _i(r.get("pair_count")),
                "mean_score": _f(r.get("mean_score")),
                "mean_token_jaccard": _f(r.get("mean_token_jaccard")),
                "mean_exact_run_len": _f(r.get("mean_exact_run_len")),
                "max_exact_run_len": _i(r.get("max_exact_run_len")),
                "mean_source_token_count": _f(r.get("mean_source_token_count")),
                "mean_target_token_count": _f(r.get("mean_target_token_count")),
                "target_longer_pct": _f(r.get("target_longer_pct")),
            }
        )
    return out


# ---- 61 Support / contra evidence matrix ----


def load_support_contra_matrix() -> list[dict[str, Any]]:
    """Per-direction support and contra counts with John anchor numbers."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("61_support_contra_evidence_matrix.csv"):
        out.append(
            {
                "direction_id": r.get("direction_id") or "",
                "pair": r.get("pair") or "",
                "primary_support_count": _i(r.get("primary_support_count")),
                "primary_contra_count": _i(r.get("primary_contra_count")),
                "gap_interval_count": _i(r.get("gap_interval_count")),
                "major_gap_count_abs_diff_ge_20": _i(r.get("major_gap_count_abs_diff_ge_20")),
                "max_gap_abs_difference": _i(r.get("max_gap_abs_difference")),
                "reordering_or_secondary_echo_rows": _i(r.get("reordering_or_secondary_echo_rows")),
                "primary_pair_count": _i(r.get("primary_pair_count")),
                "mean_primary_pair_score": _f(r.get("mean_primary_pair_score")),
                "mean_token_jaccard": _f(r.get("mean_token_jaccard")),
                "john_anchor_count": _i(r.get("john_anchor_count")) if r.get("john_anchor_count") else None,
                "john_anchors_where_shared_tradition_best": (
                    _i(r.get("john_anchors_where_shared_tradition_best"))
                    if r.get("john_anchors_where_shared_tradition_best")
                    else None
                ),
            }
        )
    return out


# ---- 62 Directional conclusion ranking ----


def load_conclusion_ranking() -> dict[str, Any]:
    """Current ranked conclusions plus missing key directions."""
    return _read_yaml("62_directional_conclusion_ranking_and_missing_key_directions.yaml") or {}


# ---- 21 Top material-gap burdens ----


def load_top_gap_burdens() -> list[dict[str, Any]]:
    """Largest material-gap burdens across all directions."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("21_top_major_gap_and_material_burdens.csv"):
        out.append(
            {
                "pair": r.get("pair") or "",
                "interval_id": r.get("interval_id") or "",
                "direction_id": r.get("direction_id") or "",
                "source": r.get("source") or "",
                "target": r.get("target") or "",
                "source_gap_range": r.get("source_gap_range") or "",
                "target_gap_range": r.get("target_gap_range") or "",
                "source_gap_count": _i(r.get("source_gap_count")),
                "target_gap_count": _i(r.get("target_gap_count")),
                "dominant_material_issue": r.get("dominant_material_issue") or "",
                "directional_implication": r.get("directional_implication") or "",
                "plausible_response": r.get("plausible_response") or "",
                "contrary_evidence_value": _i(r.get("contrary_evidence_value")),
                "interpretation": r.get("interpretation") or "",
            }
        )
    return out


# ---- 60 Contrary evidence & response-model dossiers ----


def load_response_models() -> dict[str, Any]:
    """Per-direction contrary-evidence and best-response-model dossiers.

    Each direction has: hypothesis, supporting_evidence, contrary_evidence,
    best_response_model, quantitative_indicators (burden_scores,
    gap_interval_count, major_gap_count_abs_diff_ge_20, reordering rows,
    primary_pair_count, mean_primary_pair_score), top_material_gap_burdens,
    top_john_anchor_burdens, and what_would_{strengthen,weaken} lists.
    """
    return _read_yaml("60_contrary_evidence_and_response_models_by_direction.yaml") or {}


# ---- 17 John anchor dossiers ----


def load_john_anchor_dossiers() -> dict[str, Any]:
    """Per-direction grouped John anchor dossiers."""
    return _read_yaml("17_john_synoptic_directional_anchor_dossiers.yaml") or {}


# ---- 16 John anchor ledger ----


def load_john_anchor_ledger() -> list[dict[str, Any]]:
    """Flat John anchor ledger with 58 rows (29 anchors × 2 directions)."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("16_john_synoptic_directional_anchor_ledger.csv"):
        out.append(
            {
                "direction_id": r.get("direction_id") or "",
                "pair": r.get("pair") or "",
                "anchor_id": r.get("anchor_id") or "",
                "source": r.get("source") or "",
                "target": r.get("target") or "",
                "source_refs": r.get("source_refs") or "",
                "target_refs": r.get("target_refs") or "",
                "best_current_model": r.get("best_current_model") or "",
                "direct_use_burden": _f(r.get("direct_use_burden")),
                "shared_tradition_burden": _f(r.get("shared_tradition_burden")),
                "independent_convergence_burden": _f(r.get("independent_convergence_burden")),
                "specific_features": r.get("specific_features") or "",
                "required_explanation_if_direction": r.get("required_explanation_if_direction") or "",
                "contrary_evidence": r.get("contrary_evidence") or "",
                "plausible_response_model": r.get("plausible_response_model") or "",
            }
        )
    return out


# ---- 00 Scope map ----


def load_scope_map() -> dict[str, Any]:
    """Top-level scope / what-was-missing summary."""
    return _read_yaml("00_scope_and_missing_data_map.yaml") or {}


# ---- Build ----


def build_dir_dossiers() -> dict[str, Any]:
    """Assemble the directional-dossiers bundle key.

    Layer keys map 1-to-1 to the source package files; pages choose the
    layer(s) they need.
    """
    return {
        "scope_map": load_scope_map(),
        "registry": load_registry(),
        "burden_summary": load_burden_summary(),
        "system_hypothesis_space": load_system_hypothesis_space(),
        "order_displacement_summary": load_order_displacement_summary(),
        "pair_change_summary": load_pair_change_summary(),
        "support_contra_matrix": load_support_contra_matrix(),
        "conclusion_ranking": load_conclusion_ranking(),
        "top_gap_burdens": load_top_gap_burdens(),
        "response_models": load_response_models(),
        "john_anchor_dossiers": load_john_anchor_dossiers(),
        "john_anchor_ledger": load_john_anchor_ledger(),
    }
