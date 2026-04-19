"""Loaders for the 2026-04-18 Synoptic Problem + John model-comparison atlas.

The atlas is the consolidated, expert-facing synthesis layer over the
directional dossiers. Where the dossiers track 12 pairwise directions
one at a time, the atlas groups directions into **13 explicit system
models** (Markan priority, Two-Source, Farrer, Griesbach, Augustinian,
proto-Mark + sayings, oral/tradition network, John-uses-Synoptics
variants, Synoptics-use-John-or-Johnlike, shared John-Synoptic anchor
tradition), and adds two computed model-discriminating catalogs
(triple-tradition minor agreements and Markan-masked double-tradition
order) plus a text-critical variant-sensitivity registry.

Every layer is surfaced under ``bundle.atlas`` so pages 39 (scorecard),
40 (4×4 direction matrix), 41 (minor agreements + double tradition),
and 42 (pericope dossier browser) can render from a single bundle key.

Layer map
---------
- ``system_model_registry``     — 13 system models with family, core claim,
  required direction hypotheses, optional components, status label.
- ``direction_hypothesis_registry`` — 15 directions (12 pairwise + 3 common-
  source/tradition variants: proto_mark_common_source,
  shared_matt_luke_sayings_tradition, shared_john_{mark,matthew,luke}_anchor_tradition).
- ``gospel_direction_matrix_4x4`` — 16 source→target cells identifying
  direction_id, status, method class, best response model, burden scores.
- ``direction_burden_reference`` — 20 normalized burden rows across
  burden models (direct_use, shared_tradition_adjusted, masked_direct_use,
  anchor_direct_use, shared_anchor_tradition, common_source_or_oral).
- ``model_component_direction_matrix`` — 59 rows mapping each model to
  its required and optional direction components with burden scores.
- ``system_model_comparison_scorecard`` — 13-model scorecard with
  5-problem-area fit ratings (mark_matthew_fit, mark_luke_fit,
  matt_luke_double_tradition_fit, minor_agreements_fit, john_anchor_fit),
  summed required burdens, strength/burden summary.
- ``system_model_evidence_cards`` — 13 expert-facing cards with rating,
  selected burden scores, strongest support, strongest contra/unresolved
  burden, criteria-by-problem-area.
- ``pericope_ontology``         — 102 analytical units: 92 computational
  Synoptic alignment blocks + 10 John anchor dossiers with verse ranges,
  avg scores, evidence origin and methodological status labels.
- ``pericope_obligation_summary`` — 122 rows summarizing per-unit
  obligation counts and model coverage.
- ``pericope_model_dossiers``   — Full per-unit model-specific burden
  dossiers (nested YAML keyed by unit_id).
- ``model_pericope_obligation_ledger`` — 1,945 flat rows of
  per-model × per-direction × per-unit obligations with required
  explanation, contrary evidence, and response model.
- ``minor_agreements_catalog``  — 118 algorithmically-screened
  triple-tradition rows where Matthew+Luke share tokens absent from Mark
  (the Q vs. Farrer vs. Griesbach discriminator).
- ``minor_agreements_summary``  — Summary counts and methodological notes.
- ``double_tradition_order_catalog`` — 109 Matthew↔Luke non-Markan rows
  split into primary_pair_monotonic_double_tradition (49 rows) and
  secondary_echo_after_markan_mask (60 rows).
- ``double_tradition_order_summary`` — Summary for the double-tradition layer.
- ``variant_sensitivity_registry`` — 2,682 text-critical sensitivity rows.
- ``redactional_tendency_profiles`` — 4 profiles (Matthew, Luke,
  Mark-as-redactor, John).
- ``conclusion_evidence_counterevidence_cards`` — 25 balanced claim
  cards with support, contrary evidence, linked data files.
- ``direction_support_contra_cards`` — 15 direction-level aggregate
  evidence indicator cards.
- ``direction_support_contra_matrix`` — matrix-form support/contra counts.
- ``data_layer_status_and_objectivity`` — 9 transparency declarations
  distinguishing source-derived, computed, inherited-computed, curated,
  and interpretive layers.
- ``expert_presentation_blueprint`` — Recommended visualization ordering.
- ``scholarly_limitations``     — Plain-text limitations list.
- ``executive_summary``         — Top-level package counts and headlines.
"""

from __future__ import annotations

import csv
import gzip
from typing import Any

import yaml

from .preprocess_paths import ROOT


AT_ROOT = ROOT / "synoptic_problem_model_atlas_20260418"
AT_DATA = AT_ROOT / "data"
AT_REPORTS = AT_ROOT / "reports"
AT_BLUEPRINTS = AT_ROOT / "visualization_blueprints"


def _read_yaml(relpath: str, *, root=AT_DATA) -> Any:
    p = root / relpath
    if not p.exists():
        return None
    with open(p) as f:
        return yaml.safe_load(f)


def _read_csv(relpath: str, *, root=AT_DATA) -> list[dict[str, Any]]:
    p = root / relpath
    if not p.exists():
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def _read_csv_gz(relpath: str, *, root=AT_DATA) -> list[dict[str, Any]]:
    p = root / relpath
    if not p.exists():
        return []
    with gzip.open(p, mode="rt", newline="") as f:
        return list(csv.DictReader(f))


def _read_text(relpath: str, *, root=AT_ROOT) -> str:
    p = root / relpath
    if not p.exists():
        return ""
    return p.read_text()


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


def _split_semis(s: Any) -> list[str]:
    if not s:
        return []
    return [x.strip() for x in str(s).split(";") if x.strip()]


# ---- 02 System model registry ----


def load_system_model_registry() -> list[dict[str, Any]]:
    """13 system models with family, core claim, required directions, status."""
    data = _read_yaml("02_system_model_registry.yaml") or []
    if isinstance(data, dict):
        # YAML may nest under a top-level key; normalize to list
        data = data.get("system_models") or list(data.values())
    out: list[dict[str, Any]] = []
    for r in data or []:
        if not isinstance(r, dict):
            continue
        out.append(
            {
                "model_id": r.get("model_id") or "",
                "short_label": r.get("short_label") or "",
                "family": r.get("family") or "",
                "core_claim": r.get("core_claim") or "",
                "required_direction_hypotheses": r.get("required_direction_hypotheses") or [],
                "optional_or_competing_components": r.get("optional_or_competing_components") or [],
                "status_from_current_atlas": r.get("status_from_current_atlas") or "",
            }
        )
    return out


# ---- 03 Direction hypothesis registry ----


def load_direction_hypothesis_registry() -> list[dict[str, Any]]:
    """15 direction definitions (12 pairwise + 3 common-source/tradition)."""
    data = _read_yaml("03_direction_hypothesis_registry.yaml") or []
    if isinstance(data, dict):
        data = data.get("directions") or list(data.values())
    out: list[dict[str, Any]] = []
    for r in data or []:
        if not isinstance(r, dict):
            continue
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


# ---- 04 Gospel 4x4 direction matrix ----


def load_gospel_direction_matrix_4x4() -> list[dict[str, Any]]:
    """16 cells (4 sources × 4 targets) of the Gospel direction matrix."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("04_gospel_direction_matrix_4x4.csv"):
        out.append(
            {
                "source": r.get("source") or "",
                "target": r.get("target") or "",
                "direction_id": r.get("direction_id") or "",
                "status": r.get("status") or "",
                "method_class": r.get("method_class") or "",
                "best_response_model": r.get("best_response_model") or "",
                "available_burden_scores": r.get("available_burden_scores") or "",
                "primary_data_files": r.get("primary_data_files") or "",
            }
        )
    return out


# ---- 10 Pericope ontology ----


def load_pericope_ontology() -> list[dict[str, Any]]:
    """102 units: 92 computational Synoptic blocks + 10 John anchors."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("10_pericope_ontology_computational_and_anchor.csv"):
        out.append(
            {
                "pericope_id": r.get("pericope_id") or "",
                "unit_type": r.get("unit_type") or "",
                "pair": r.get("pair") or "",
                "block_id": r.get("block_id") or "",
                "block_label": r.get("block_label") or "",
                "matthew_range": r.get("matthew_range") or "",
                "mark_range": r.get("mark_range") or "",
                "luke_range": r.get("luke_range") or "",
                "john_range": r.get("john_range") or "",
                "pair_count": _i(r.get("pair_count")),
                "avg_score": _f(r.get("avg_score")),
                "evidence_origin": r.get("evidence_origin") or "",
                "methodological_status": r.get("methodological_status") or "",
                "representative_primary_pairs": r.get("representative_primary_pairs") or "",
                "shared_features": r.get("shared_features") or "",
            }
        )
    return out


# ---- 11 Pericope model dossiers (nested YAML keyed by unit_id) ----


def load_pericope_model_dossiers() -> dict[str, Any]:
    """Per-unit model-specific burden dossiers (keyed by unit_id)."""
    data = _read_yaml("11_pericope_model_dossiers.yaml")
    if data is None:
        return {}
    if isinstance(data, list):
        return {(r or {}).get("unit_id") or str(i): r for i, r in enumerate(data)}
    return data


# ---- 12 Pericope obligation summary ----


def load_pericope_obligation_summary() -> list[dict[str, Any]]:
    """122-row summary of obligations per pericope unit."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("12_pericope_obligation_summary.csv"):
        out.append(
            {
                "unit_id": r.get("unit_id") or "",
                "pair": r.get("pair") or "",
                "obligation_rows": _i(r.get("obligation_rows")),
                "direction_count": _i(r.get("direction_count")),
                "model_count": _i(r.get("model_count")),
            }
        )
    return out


# ---- 20 Model/pericope obligation ledger (1,945 rows — main work file) ----


def load_model_pericope_obligation_ledger() -> list[dict[str, Any]]:
    """Core 1,945-row ledger: model × direction × unit → obligation + response."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("20_model_pericope_obligation_ledger.csv"):
        out.append(
            {
                "model_id": r.get("model_id") or "",
                "direction_id": r.get("direction_id") or "",
                "pair": r.get("pair") or "",
                "unit_id": r.get("unit_id") or "",
                "source_range": r.get("source_range") or "",
                "target_range": r.get("target_range") or "",
                "obligation_type": r.get("obligation_type") or "",
                "required_explanation": r.get("required_explanation") or "",
                "contrary_evidence": r.get("contrary_evidence") or "",
                "response_model": r.get("response_model") or "",
                "basis": r.get("basis") or "",
            }
        )
    return out


# ---- 30 Minor agreements catalog (triple-tradition discriminator) ----


def load_minor_agreements_catalog() -> list[dict[str, Any]]:
    """118-row triple-tradition minor agreements screen."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("30_minor_agreements_catalog_triple_tradition.csv"):
        out.append(
            {
                "minor_agreement_id": r.get("minor_agreement_id") or "",
                "mark_ref": r.get("mark_ref") or "",
                "matt_ref": r.get("matt_ref") or "",
                "luke_ref": r.get("luke_ref") or "",
                "agreement_absent_from_mark_count": _i(r.get("agreement_absent_from_mark_count")),
                "agreement_absent_from_mark_tokens": r.get("agreement_absent_from_mark_tokens") or "",
                "mark_omitted_by_both_count": _i(r.get("mark_omitted_by_both_count")),
                "mark_omitted_by_both_tokens": r.get("mark_omitted_by_both_tokens") or "",
                "matt_luke_longest_exact_content_run_len": _i(
                    r.get("matt_luke_longest_exact_content_run_len")
                ),
                "matt_luke_longest_exact_content_run": r.get("matt_luke_longest_exact_content_run") or "",
                "minor_agreement_strength": _i(r.get("minor_agreement_strength")),
                "agreement_type": r.get("agreement_type") or "",
                "possible_implications": r.get("possible_implications") or "",
                "formula_or_commonality_risk": r.get("formula_or_commonality_risk") or "",
                "matt_text": r.get("matt_text") or "",
                "mark_text": r.get("mark_text") or "",
                "luke_text": r.get("luke_text") or "",
            }
        )
    return out


# ---- 31 Minor agreements summary ----


def load_minor_agreements_summary() -> dict[str, Any]:
    data = _read_yaml("31_minor_agreements_summary.yaml")
    return data if isinstance(data, dict) else {}


# ---- 40 Double-tradition order catalog (Markan-masked) ----


def load_double_tradition_order_catalog() -> list[dict[str, Any]]:
    """109 rows: 49 primary pairs + 60 secondary echoes."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("40_double_tradition_order_catalog_markan_masked.csv"):
        out.append(
            {
                "double_tradition_id": r.get("double_tradition_id") or "",
                "alignment_layer": r.get("alignment_layer") or "",
                "matt_ref": r.get("matt_ref") or "",
                "luke_ref": r.get("luke_ref") or "",
                "matt_index": _i(r.get("matt_index")),
                "luke_index": _i(r.get("luke_index")),
                "score": _f(r.get("score")),
                "lcs": _f(r.get("lcs")),
                "tags": r.get("tags") or "",
                "order_signal": r.get("order_signal") or "",
                "matt_text": r.get("matt_text") or "",
                "luke_text": r.get("luke_text") or "",
                "shared_lemma_count": _i(r.get("shared_lemma_count")),
                "model_implication": r.get("model_implication") or "",
                "main_counter_to_direct_use": r.get("main_counter_to_direct_use") or "",
                "matt_rank": _i(r.get("matt_rank")) if r.get("matt_rank") else None,
                "luke_rank_by_matt_order": _i(r.get("luke_rank_by_matt_order"))
                if r.get("luke_rank_by_matt_order")
                else None,
                "rank_distance_abs": _i(r.get("rank_distance_abs"))
                if r.get("rank_distance_abs")
                else None,
                "nonlocal_flag": r.get("nonlocal_flag") or "",
            }
        )
    return out


# ---- 41 Double-tradition order summary ----


def load_double_tradition_order_summary() -> dict[str, Any]:
    data = _read_yaml("41_double_tradition_order_summary.yaml")
    return data if isinstance(data, dict) else {}


# ---- 50 Direction burden reference (20 rows) ----


def load_direction_burden_reference() -> list[dict[str, Any]]:
    """Normalized burden scores across burden-model types, comparable within type."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("50_direction_burden_reference.csv"):
        out.append(
            {
                "direction_id": r.get("direction_id") or "",
                "pair": r.get("pair") or "",
                "burden_model": r.get("burden_model") or "",
                "burden_score": _f(r.get("burden_score")),
                "lower_is_better": (str(r.get("lower_is_better") or "").strip().lower() == "true"),
                "comparison_basis": r.get("comparison_basis") or "",
                "interpretive_result": r.get("interpretive_result") or "",
            }
        )
    return out


# ---- 51 Model component direction matrix (59 rows) ----


def load_model_component_direction_matrix() -> list[dict[str, Any]]:
    """Each row maps (model, direction) component to its burden score and role."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("51_model_component_direction_matrix.csv"):
        out.append(
            {
                "model_id": r.get("model_id") or "",
                "direction_id": r.get("direction_id") or "",
                "component_role": r.get("component_role") or "",
                "pair": r.get("pair") or "",
                "burden_model": r.get("burden_model") or "",
                "burden_score": _f(r.get("burden_score")) if r.get("burden_score") else None,
                "interpretive_result": r.get("interpretive_result") or "",
            }
        )
    return out


# ---- 52 System-model comparison scorecard ----


def load_system_model_comparison_scorecard() -> list[dict[str, Any]]:
    """13-model scorecard with 5-area fit ratings and strength/burden summary."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("52_system_model_comparison_scorecard.csv"):
        out.append(
            {
                "model_id": r.get("model_id") or "",
                "short_label": r.get("short_label") or "",
                "family": r.get("family") or "",
                "required_direction_hypotheses": _split_semis(r.get("required_direction_hypotheses")),
                "required_direction_burdens_selected": r.get("required_direction_burdens_selected") or "",
                "sum_selected_burden_scores_available": _f(r.get("sum_selected_burden_scores_available")),
                "current_atlas_rating": r.get("current_atlas_rating") or "",
                "mark_matthew_fit": r.get("mark_matthew_fit") or "",
                "mark_luke_fit": r.get("mark_luke_fit") or "",
                "matt_luke_double_tradition_fit": r.get("matt_luke_double_tradition_fit") or "",
                "minor_agreements_fit": r.get("minor_agreements_fit") or "",
                "john_anchor_fit": r.get("john_anchor_fit") or "",
                "main_strength": r.get("main_strength") or "",
                "main_burden": r.get("main_burden") or "",
            }
        )
    return out


# ---- 53 System-model evidence cards ----


def load_system_model_evidence_cards() -> list[dict[str, Any]]:
    data = _read_yaml("53_system_model_evidence_cards.yaml")
    if isinstance(data, dict):
        data = data.get("evidence_cards") or list(data.values())
    out: list[dict[str, Any]] = []
    for r in data or []:
        if not isinstance(r, dict):
            continue
        out.append(r)
    return out


# ---- 60 Redactional tendency profiles ----


def load_redactional_tendency_profiles() -> list[dict[str, Any]]:
    data = _read_yaml("60_redactional_tendency_profiles.yaml")
    if isinstance(data, dict):
        data = data.get("profiles") or list(data.values())
    out: list[dict[str, Any]] = []
    for r in data or []:
        if not isinstance(r, dict):
            continue
        out.append(r)
    return out


# ---- 70 Variant sensitivity registry ----


def load_variant_sensitivity_registry() -> list[dict[str, Any]]:
    """2,682-row text-critical sensitivity registry."""
    return _read_csv("70_variant_sensitivity_registry.csv")


# ---- 71 Text-critical policy ----


def load_text_critical_policy() -> dict[str, Any]:
    data = _read_yaml("71_text_critical_policy.yaml")
    return data if isinstance(data, dict) else {}


# ---- 80 Direction support/contra cards and matrix ----


def load_direction_support_contra_cards() -> list[dict[str, Any]]:
    data = _read_yaml("80_direction_support_contra_cards.yaml")
    if isinstance(data, dict):
        data = data.get("cards") or list(data.values())
    out: list[dict[str, Any]] = []
    for r in data or []:
        if not isinstance(r, dict):
            continue
        out.append(r)
    return out


def load_direction_support_contra_matrix() -> list[dict[str, Any]]:
    return _read_csv("80_direction_support_contra_matrix.csv")


# ---- 81 Conclusion evidence/counterevidence cards (25 cards) ----


def load_conclusion_evidence_counterevidence_cards() -> list[dict[str, Any]]:
    data = _read_yaml("81_conclusion_evidence_counterevidence_cards.yaml")
    if isinstance(data, dict):
        data = data.get("cards") or list(data.values())
    out: list[dict[str, Any]] = []
    for r in data or []:
        if not isinstance(r, dict):
            continue
        out.append(r)
    return out


# ---- 90 Data layer status / objectivity ----


def load_data_layer_status_and_objectivity() -> list[dict[str, Any]]:
    """9-row transparency declarations for each major data category."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("90_data_layer_status_and_objectivity.csv"):
        out.append(
            {
                "layer_id": r.get("layer_id") or "",
                "file": r.get("file") or "",
                "data_type": r.get("data_type") or "",
                "objectivity": r.get("objectivity") or "",
                "curation": r.get("curation") or "",
            }
        )
    return out


# ---- Visualization blueprint ----


def load_expert_presentation_blueprint() -> dict[str, Any]:
    p = AT_BLUEPRINTS / "expert_presentation_blueprint.yaml"
    if not p.exists():
        return {}
    with open(p) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


# ---- Executive summary ----


def load_executive_summary() -> dict[str, Any]:
    p = AT_ROOT / "EXECUTIVE_SUMMARY.yaml"
    if not p.exists():
        return {}
    with open(p) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


# ---- Build ----


def build_atlas() -> dict[str, Any]:
    """Assemble the atlas bundle key.

    Each layer maps 1-to-1 to a source file; pages choose the layer(s) they
    need. Heaviest by row count are ``variant_sensitivity_registry`` (2,682)
    and ``model_pericope_obligation_ledger`` (1,945).
    """
    return {
        "executive_summary": load_executive_summary(),
        "system_model_registry": load_system_model_registry(),
        "direction_hypothesis_registry": load_direction_hypothesis_registry(),
        "gospel_direction_matrix_4x4": load_gospel_direction_matrix_4x4(),
        "direction_burden_reference": load_direction_burden_reference(),
        "model_component_direction_matrix": load_model_component_direction_matrix(),
        "system_model_comparison_scorecard": load_system_model_comparison_scorecard(),
        "system_model_evidence_cards": load_system_model_evidence_cards(),
        "pericope_ontology": load_pericope_ontology(),
        "pericope_obligation_summary": load_pericope_obligation_summary(),
        "pericope_model_dossiers": load_pericope_model_dossiers(),
        "model_pericope_obligation_ledger": load_model_pericope_obligation_ledger(),
        "minor_agreements_catalog": load_minor_agreements_catalog(),
        "minor_agreements_summary": load_minor_agreements_summary(),
        "double_tradition_order_catalog": load_double_tradition_order_catalog(),
        "double_tradition_order_summary": load_double_tradition_order_summary(),
        "variant_sensitivity_registry": load_variant_sensitivity_registry(),
        "text_critical_policy": load_text_critical_policy(),
        "direction_support_contra_cards": load_direction_support_contra_cards(),
        "direction_support_contra_matrix": load_direction_support_contra_matrix(),
        "conclusion_evidence_counterevidence_cards": load_conclusion_evidence_counterevidence_cards(),
        "redactional_tendency_profiles": load_redactional_tendency_profiles(),
        "data_layer_status_and_objectivity": load_data_layer_status_and_objectivity(),
        "expert_presentation_blueprint": load_expert_presentation_blueprint(),
    }
