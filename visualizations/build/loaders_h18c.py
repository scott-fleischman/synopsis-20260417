"""Loaders for the 2026-04-18c data-analysis patch.

The 18c patch is the second supplement. Where 18b filled eight data gaps,
18c tightens the *interpretations* those data could bear:

- Mark-Luke burden reassessment with an explicit order-retention penalty
  sensitivity (the 164.1 shared-tradition figure from 18b was lower than
  either directed model, but only because shared tradition was not charged
  for the narrative order it must still explain — 18c makes that cost
  visible).
- Matt-Luke mask-regime robustness across strict/medium/broad.
- John anchor-specific burden ledgers replacing the prior 18b templated
  per-pair ledger.
- Thomas curation-status and parallel-certainty annotations.
- Epistle validation sample with machine-audit class distribution and
  formula-risk counts across the top-500 candidate pool.
- MorphGNT lemma audit layer (183 Mark-Luke primary pairs re-scored on
  lemmas — an audit signal, not a full replacement pipeline).
- Revised data-analysis conclusions with nuanced per-claim confidence.

Every 18c layer is surfaced under ``bundle.h18c`` alongside ``bundle.h18b``.
Pages that are the natural home for the 18c number read from h18c directly;
the governance layer (AUTHORITATIVE_NUMBERS.yaml, METHODS.md,
REPRODUCIBILITY_LEVELS.md) cites the same numbers so prose and bundle
stay in step.
"""

from __future__ import annotations

import csv
from typing import Any

import yaml

from .preprocess_paths import ROOT


H18C_ROOT = ROOT / "analysis_update_20260418c"
H18C_DATA = H18C_ROOT / "data"
H18C_REPORTS = H18C_ROOT / "reports"


def _read_yaml(relpath: str, *, root=H18C_DATA) -> Any:
    p = root / relpath
    if not p.exists():
        return None
    with open(p) as f:
        return yaml.safe_load(f)


def _read_csv(relpath: str, *, root=H18C_DATA) -> list[dict[str, Any]]:
    p = root / relpath
    if not p.exists():
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


# ---- Mark-Luke burden reassessment (order-retention penalty) ----

def load_mark_luke_reassessment() -> dict[str, Any]:
    """18c Mark-Luke direct-burden reassessment.

    The 18b three-way burden showed:
        Mark-prior       254.6466
        Luke-prior       303.1966
        shared tradition 164.1468 (lowest)

    18c adds an order-retention / cluster-density / narrative-bridge penalty
    for the shared-tradition model (because shared tradition must still
    account for the *sequence* and *density* of the agreement, not just its
    lexical content). Under moderate weights (0.75 / 1.0 / 1.0) the
    adjusted shared-tradition burden becomes 385.6134 and Mark-prior
    (254.6466) is the lowest-burden model overall. The penalty sensitivity
    grid shows Mark-prior winning in 211 of 245 parameter combinations.
    """
    return _read_yaml("12_mark_luke_direct_burden_reassessment.yaml") or {}


def load_mark_luke_revised_claim() -> dict[str, Any]:
    """Recommended public wording for the Mark-Luke claim under 18c."""
    return _read_yaml("13_mark_luke_revised_interpretive_claim.yaml") or {}


def load_mark_luke_penalty_sensitivity() -> list[dict[str, Any]]:
    """Full parameter grid (order-retention × cluster-density × narrative-bridge)."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("11_mark_luke_shared_tradition_penalty_sensitivity.csv"):
        out.append({
            "order_retention_weight": float(r.get("order_retention_weight") or 0),
            "cluster_density_weight": float(r.get("cluster_density_weight") or 0),
            "narrative_bridge_weight": float(r.get("narrative_bridge_weight") or 0),
            "added_shared_tradition_penalty": float(r.get("added_shared_tradition_penalty") or 0),
            "adjusted_shared_tradition_burden": float(r.get("adjusted_shared_tradition_burden") or 0),
            "mark_prior_burden": float(r.get("mark_prior_burden") or 0),
            "luke_prior_burden": float(r.get("luke_prior_burden") or 0),
            "lowest_burden_model": r.get("lowest_burden_model") or "",
        })
    return out


def load_mark_luke_retention_audit() -> list[dict[str, Any]]:
    """Per-loose-block tradition-retention audit backing the penalty."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("10_mark_luke_tradition_retention_audit_by_block.csv"):
        out.append({k: v for k, v in r.items()})
    return out


# ---- Matt-Luke mask-regime robustness ----

def load_matt_luke_robustness() -> dict[str, Any]:
    """18c mask-regime (strict/medium/broad) robustness summary.

    Conclusion: pair counts move with mask strictness but the qualitative
    reading is stable — the retained material remains a sayings/echo
    problem, not a stable narrative-chain relationship.
    """
    return _read_yaml("22_matt_luke_double_tradition_robustness.yaml") or {}


def load_matt_luke_robustness_table() -> list[dict[str, Any]]:
    """Full regime × threshold sweep table."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("20_matt_luke_mask_regime_robustness_table.csv"):
        out.append({k: v for k, v in r.items()})
    return out


# ---- John anchor-specific burden ledgers ----

def load_john_anchor_ledgers() -> list[dict[str, Any]]:
    """18c per-anchor × per-pair burden ledger (replaces 18b templated ledger)."""
    return _read_yaml("30_john_anchor_specific_burden_ledgers.yaml") or []


def load_john_anchor_ledgers_flat() -> list[dict[str, Any]]:
    """Flat-CSV version of the per-anchor × per-pair burden ledger."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("31_john_anchor_specific_burden_ledgers_flat.csv"):
        out.append({
            "anchor_id": r["anchor_id"],
            "pair": r["pair"],
            "john_refs": r["john_refs"],
            "synoptic_refs": r["synoptic_refs"],
            "feature_count": int(r.get("feature_count") or 0),
            "local_lexical_signal": float(r.get("local_lexical_signal") or 0),
            "exact_run_signal": float(r.get("exact_run_signal") or 0),
            "specificity_signal": float(r.get("specificity_signal") or 0),
            "order_or_reframing_displacement_signal": float(r.get("order_or_reframing_displacement_signal") or 0),
            "best_lowest_burden_model": r["best_lowest_burden_model"],
            "burden_john_uses_synoptic_or_synoptic_like_source": float(r.get("burden_john_uses_synoptic_or_synoptic_like_source") or 0),
            "burden_synoptic_uses_john_or_john_like_source": float(r.get("burden_synoptic_uses_john_or_john_like_source") or 0),
            "burden_shared_anchor_tradition": float(r.get("burden_shared_anchor_tradition") or 0),
            "burden_independent_convergence": float(r.get("burden_independent_convergence") or 0),
        })
    return out


def load_john_anchor_aggregate() -> list[dict[str, Any]]:
    """Per-pair totals summing across anchors (3 rows: J↔Mk, J↔Mt, J↔Lk).

    Every pair shows ``shared_anchor_tradition`` as the lowest total burden;
    anchors_best_model_counts is 100% shared_anchor_tradition across all
    three pairs (9 of 9, 10 of 10, 10 of 10).
    """
    return _read_yaml("32_john_anchor_specific_aggregate_summary.yaml") or []


# ---- Thomas curation status ----

def load_thomas_curation() -> dict[str, Any]:
    """18c Thomas curation-status + parallel-certainty distribution.

    Key numbers:
        total_logia 116
        curated_from_prior_registry 46
        parallel_certainty: high 8, medium_high 3, medium 35, not_assessed 70
        directional_claim_ready_count 3
    """
    return _read_yaml("41_thomas_curation_status_summary.yaml") or {}


def load_thomas_relation_counts() -> list[dict[str, Any]]:
    """relation_type × matrix_strength × parallel_certainty crosstab."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("42_thomas_relation_counts.csv"):
        out.append({
            "relation_type": r["relation_type"],
            "matrix_strength": r["matrix_strength"],
            "parallel_certainty": r["parallel_certainty"],
            "count": int(r.get("count") or 0),
        })
    return out


def load_thomas_matrix_with_curation() -> list[dict[str, Any]]:
    """Full 116-row Thomas matrix with 18c curation/certainty fields attached."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("40_thomas_logion_matrix_with_curation_status.csv"):
        out.append({k: v for k, v in r.items()})
    return out


# ---- Epistle validation sample ----

def load_epistle_validation_summary() -> dict[str, Any]:
    """18c epistle validation sample summary.

    Key numbers:
        sample_rows 160 (stratified across 7 strata)
        machine_audit_class_counts (uncertain 59, strong_low_formula 41, ...)
        formula_risk_counts_in_top500 (low 317, high 166, medium 17)
    """
    return _read_yaml("51_epistle_candidate_validation_summary.yaml") or {}


def load_epistle_formula_risk_model() -> dict[str, Any]:
    return _read_yaml("53_epistle_formula_risk_model.yaml") or {}


def load_epistle_validation_sample() -> list[dict[str, Any]]:
    """160-row stratified validation sample."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("50_epistle_candidate_validation_sample.csv"):
        out.append({k: v for k, v in r.items()})
    return out


def load_epistle_targeted_morphology_audit() -> list[dict[str, Any]]:
    """MorphGNT lemma audit applied to the 10 targeted epistle cases."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("52_epistle_targeted_cases_morphology_audit.csv"):
        out.append({k: v for k, v in r.items()})
    return out


# ---- MorphGNT rerun / lemma audit ----

def load_morphology_rerun_summary() -> dict[str, Any]:
    """18c MorphGNT lemma audit headline numbers.

    Audit layer, not a replacement pipeline:
        token_layer_rows 85364
        verse_unit_rows 5060
        mark_luke_primary_chain:
            pairs_audited 183
            surface_score_mean 0.4042
            lemma_score_mean 0.4836
            lemma_improves_or_retains_count 153 (of 183)
            lemma_worse_count 30
    """
    return _read_yaml("84_morphology_rerun_summary.yaml") or {}


def load_morphology_mark_luke_audit() -> list[dict[str, Any]]:
    """Per-pair surface vs. lemma score for the 183 Mark-Luke primary pairs."""
    out: list[dict[str, Any]] = []
    for r in _read_csv("82_mark_luke_primary_chain_morphology_audit.csv"):
        out.append({k: v for k, v in r.items()})
    return out


# ---- Apocrypha analysis-status ----

def load_apocrypha_status() -> dict[str, Any]:
    """18c apocrypha analysis-status + next-ingestion priority list."""
    return _read_yaml("60_apocrypha_analysis_status_and_ingestion_roadmap.yaml") or {}


# ---- Governance: authoritative numbers, reproducibility levels, response map ----

def load_authoritative_numbers() -> dict[str, Any]:
    """18c package-internal authoritative numbers registry."""
    return _read_yaml("01_authoritative_numbers.yaml") or {}


def load_reproducibility_levels() -> dict[str, Any]:
    """18c reproducibility-level annotation (L1/L2/L3 per new layer)."""
    return _read_yaml("02_reproducibility_levels.yaml") or {}


def load_review_response_map() -> dict[str, Any]:
    return _read_yaml("00_review_response_map.yaml") or {}


# ---- Updated conclusions ----

def load_updated_conclusions() -> dict[str, Any]:
    """18c updated data-analysis conclusions (6 claims with revised confidence)."""
    return _read_yaml("updated_data_analysis_conclusions.yaml", root=H18C_REPORTS) or {}


# ---- Top-level build ----

def build_h18c() -> dict[str, Any]:
    """Assemble the 18c patch as a single bundle key."""
    return {
        "authoritative_numbers": load_authoritative_numbers(),
        "reproducibility_levels": load_reproducibility_levels(),
        "review_response_map": load_review_response_map(),
        "updated_conclusions": load_updated_conclusions(),
        "mark_luke_reassessment": load_mark_luke_reassessment(),
        "mark_luke_revised_claim": load_mark_luke_revised_claim(),
        "mark_luke_penalty_sensitivity": load_mark_luke_penalty_sensitivity(),
        "matt_luke_robustness": load_matt_luke_robustness(),
        "matt_luke_robustness_table": load_matt_luke_robustness_table(),
        "john_anchor_ledgers": load_john_anchor_ledgers(),
        "john_anchor_ledgers_flat": load_john_anchor_ledgers_flat(),
        "john_anchor_aggregate": load_john_anchor_aggregate(),
        "thomas_curation": load_thomas_curation(),
        "thomas_relation_counts": load_thomas_relation_counts(),
        "epistle_validation_summary": load_epistle_validation_summary(),
        "epistle_formula_risk_model": load_epistle_formula_risk_model(),
        "morphology_rerun_summary": load_morphology_rerun_summary(),
        "apocrypha_status": load_apocrypha_status(),
    }
