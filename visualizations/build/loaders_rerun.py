"""Loaders for the reproducibility-patch reruns under ``analysis_update_20260418/``.

This package is the authoritative source for headline numbers, sensitivity
layers, source-file SHA256 provenance, and new claim/evidence linkage. It is
loaded as a supplementary ``rerun`` key on each synoptic dataset and on
``jtea`` — the pair-level CSVs in the original packages are still used for
per-pair detail because the rerun emits a minimal, reproducibility-first
schema that omits fields the viz depends on (``pair_classes``,
``common_lemmas``, variant-count markers). The rerun's authoritative data is
what is exposed here.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from .preprocess_paths import ROOT

UPDATE_ROOT = ROOT / "analysis_update_20260418"
MM_ROOT = UPDATE_ROOT / "reruns" / "mark_matthew_rerun_robust" / "data"
MLD_ROOT = UPDATE_ROOT / "reruns" / "matt_luke_double_masked_rerun_robust" / "data"
JTEA_ROOT = UPDATE_ROOT / "reruns" / "jtea_low_verbatim_rerun_robust" / "data"


def _yaml(path: Path) -> Any:
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def _csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _python_literal_dict(s: str) -> dict[str, Any]:
    """Parse a Python-dict-literal cell like ``{'a': 1, 'b': 2}`` safely.

    ``01c_mask_regime_comparison.csv`` embeds dict literals inside CSV cells
    because the upstream script uses ``repr(dict)``. We convert single quotes
    to double quotes so ``json.loads`` can read it — no code execution.
    """
    if not s or not s.strip():
        return {}
    try:
        return json.loads(s.replace("'", '"'))
    except (json.JSONDecodeError, ValueError):
        return {}


# ---- Mark-Matthew rerun ----

def load_mm_rerun_summary() -> Any:
    return _yaml(MM_ROOT / "16_global_summary.yaml")


def load_mm_rerun_metadata() -> Any:
    return _yaml(MM_ROOT / "00_source_metadata.yaml")


def load_mm_rerun_mark_ending_sensitivity() -> Any:
    return _yaml(MM_ROOT / "22_sensitivity_mark_ending.yaml")


def load_mm_rerun_score_grid() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for r in _csv_rows(MM_ROOT / "23_sensitivity_score_grid.csv"):
        rows.append({
            "primary_chain_min_score": float(r.get("primary_chain_min_score") or 0),
            "gap_penalty": float(r.get("gap_penalty") or 0),
            "pair_count": int(r.get("pair_count") or 0),
            "loose_block_count": int(r.get("loose_block_count") or 0),
        })
    return rows


def load_mm_rerun_actual_vs_canonical() -> Any:
    return _yaml(MM_ROOT / "24_actual_vs_canonical_slots.yaml")


def load_mm_rerun() -> dict[str, Any]:
    return {
        "summary": load_mm_rerun_summary(),
        "source_metadata": load_mm_rerun_metadata(),
        "mark_ending_sensitivity": load_mm_rerun_mark_ending_sensitivity(),
        "score_grid": load_mm_rerun_score_grid(),
        "actual_vs_canonical": load_mm_rerun_actual_vs_canonical(),
    }


# ---- MLD rerun (Markan-masked Matt-Luke) ----

def load_mld_rerun_summary() -> Any:
    return _yaml(MLD_ROOT / "16_global_summary.yaml")


def load_mld_rerun_metadata() -> Any:
    return _yaml(MLD_ROOT / "00_source_metadata.yaml")


def load_mld_rerun_mask_audit_medium() -> list[dict[str, str]]:
    return _csv_rows(MLD_ROOT / "01b_mask_audit_default_medium.csv")


def load_mld_rerun_regime_comparison() -> list[dict[str, Any]]:
    """Parse 01c which packs dict-literals inside CSV cells."""
    rows: list[dict[str, Any]] = []
    for r in _csv_rows(MLD_ROOT / "01c_mask_regime_comparison.csv"):
        rows.append({
            "regime": r.get("regime", ""),
            "threshold": float(r.get("threshold") or 0),
            "matt_masked": int(r.get("matt_masked") or 0),
            "matt_unmasked": int(r.get("matt_unmasked") or 0),
            "matt_reason_counts": _python_literal_dict(r.get("matt_reason_counts", "")),
            "luke_masked": int(r.get("luke_masked") or 0),
            "luke_unmasked": int(r.get("luke_unmasked") or 0),
            "luke_reason_counts": _python_literal_dict(r.get("luke_reason_counts", "")),
        })
    return rows


def load_mld_rerun_regime_sensitivity() -> list[dict[str, Any]]:
    data = _yaml(MLD_ROOT / "17_mask_regime_sensitivity.yaml") or []
    rows: list[dict[str, Any]] = []
    for e in data:
        rows.append({
            "regime": e.get("regime", ""),
            "primary_chain_min_score": float(e.get("primary_chain_min_score") or 0),
            "pair_count": int(e.get("pair_count") or 0),
            "loose_block_count": int(e.get("loose_block_count") or 0),
        })
    return rows


def load_mld_rerun_actual_vs_canonical() -> Any:
    return _yaml(MLD_ROOT / "18_actual_vs_canonical_slots.yaml")


def load_mld_rerun_mask_audit_rows() -> list[dict[str, Any]]:
    """Parse 01b_mask_audit_default_medium.csv with typed columns.

    The rerun's per-verse mask audit carries the top-Mark score and ref that
    drove the masking decision — strictly richer than the orig package, which
    only labels verses boolean-wise without the supporting evidence.
    """
    rows: list[dict[str, Any]] = []
    for r in _csv_rows(MLD_ROOT / "01b_mask_audit_default_medium.csv"):
        try:
            score = float(r.get("top_mark_score") or 0)
        except ValueError:
            score = 0.0
        masked_str = (r.get("masked_default_medium") or "").strip().lower()
        rows.append({
            "book": r.get("book", ""),
            "idx": int(r.get("idx") or 0),
            "ref": r.get("ref", ""),
            "top_mark_score": score,
            "top_mark_ref": r.get("top_mark_ref", ""),
            "masked": masked_str == "true",
            "mask_reason": r.get("mask_reason_default_medium", ""),
        })
    return rows


def load_mld_rerun() -> dict[str, Any]:
    return {
        "summary": load_mld_rerun_summary(),
        "source_metadata": load_mld_rerun_metadata(),
        "regime_comparison": load_mld_rerun_regime_comparison(),
        "regime_sensitivity": load_mld_rerun_regime_sensitivity(),
        "actual_vs_canonical": load_mld_rerun_actual_vs_canonical(),
        "mask_audit_medium": load_mld_rerun_mask_audit_rows(),
    }


# ---- JTEA rerun ----

def load_jtea_rerun_summary() -> Any:
    return _yaml(JTEA_ROOT / "16_global_summary.yaml")


def load_jtea_rerun_method() -> Any:
    return _yaml(JTEA_ROOT / "00_method_rethought_low_verbatim.yaml")


def load_jtea_rerun_claim_evidence_links() -> list[dict[str, Any]]:
    """Normalize the rerun's 17_claim_evidence_links.yaml into a viz-friendly shape.

    Raw YAML has ``claim_id``, ``confidence_dimensions.{automatic_retrieval_confidence,
    philological_case_strength, formula_risk}``, and a ``supports`` list where one
    entry carries ``case_id``. The viz layer wants a flat ``{claim_id, case_id,
    confidence:{retrieval, philological, formula_risk}, provisional_best_explanation,
    supports}`` shape keyed on ``case_id`` for pair lookup.
    """
    data = _yaml(JTEA_ROOT / "17_claim_evidence_links.yaml") or []
    if not isinstance(data, list):
        return []
    out: list[dict[str, Any]] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        supports = row.get("supports") or []
        case_id = ""
        for s in supports:
            if isinstance(s, dict) and s.get("case_id"):
                case_id = str(s["case_id"])
                break
        dims = row.get("confidence_dimensions") or {}
        confidence = {
            "retrieval": dims.get("automatic_retrieval_confidence", ""),
            "philological": dims.get("philological_case_strength", ""),
            "formula_risk": dims.get("formula_risk", ""),
        }
        out.append({
            "claim_id": row.get("claim_id", ""),
            "claim_type": row.get("claim_type", ""),
            "case_id": case_id,
            "confidence": confidence,
            "provisional_best_explanation": row.get("provisional_best_explanation", ""),
            "supports": supports,
        })
    return out


def load_jtea_rerun_formula_risk_summary() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for r in _csv_rows(JTEA_ROOT / "18_formula_risk_summary.csv"):
        rows.append({
            "layer": r.get("layer", ""),
            "formula_risk": r.get("formula_risk", ""),
            "count": int(r.get("count") or 0),
        })
    return rows


def load_jtea_rerun_rich_exact_hits() -> list[dict[str, Any]]:
    """Load the rerun's ``15_filtered_high_value_exact_hits.csv`` in full.

    This is the authoritative high-value exact-hit set: ~11K rows with
    ``formula_risk``, ``evidence_origin``, full Greek ``source_text`` and
    ``target_text``, plus token/bigram/trigram/fourgram overlap counts. The
    orig jtea package only shipped a 200-row curated subset; this is the
    full automatic retrieval layer with formula-risk classification.
    """
    rows: list[dict[str, Any]] = []
    path = JTEA_ROOT / "15_filtered_high_value_exact_hits.csv"
    if not path.exists():
        return rows
    for r in _csv_rows(path):
        try:
            score = float(r.get("score") or 0)
        except ValueError:
            score = 0.0
        try:
            run = int(r.get("max_exact_run_len") or 0)
        except ValueError:
            run = 0
        try:
            lcs_len = int(r.get("lcs_len") or 0)
        except ValueError:
            lcs_len = 0
        rows.append({
            "layer": r.get("layer", ""),
            "source_book": r.get("source_book", ""),
            "source_ref": r.get("source_ref", ""),
            "target_book": r.get("target_book", ""),
            "target_ref": r.get("target_ref", ""),
            "score": score,
            "max_exact_run_len": run,
            "max_exact_run": r.get("max_exact_run", ""),
            "lcs_len": lcs_len,
            "source_text": r.get("source_text", ""),
            "target_text": r.get("target_text", ""),
            "formula_risk": r.get("formula_risk", ""),
            "evidence_origin": r.get("evidence_origin", ""),
        })
    rows.sort(key=lambda x: (-x["max_exact_run_len"], -x["score"]))
    return rows


def load_jtea_rerun() -> dict[str, Any]:
    return {
        "summary": load_jtea_rerun_summary(),
        "method": load_jtea_rerun_method(),
        "claim_evidence_links": load_jtea_rerun_claim_evidence_links(),
        "formula_risk_summary": load_jtea_rerun_formula_risk_summary(),
        "rich_exact_hits": load_jtea_rerun_rich_exact_hits(),
    }


__all__ = [
    "UPDATE_ROOT",
    "MM_ROOT",
    "MLD_ROOT",
    "JTEA_ROOT",
    "load_mm_rerun",
    "load_mm_rerun_summary",
    "load_mm_rerun_metadata",
    "load_mm_rerun_mark_ending_sensitivity",
    "load_mm_rerun_score_grid",
    "load_mm_rerun_actual_vs_canonical",
    "load_mld_rerun",
    "load_mld_rerun_summary",
    "load_mld_rerun_metadata",
    "load_mld_rerun_mask_audit_medium",
    "load_mld_rerun_regime_comparison",
    "load_mld_rerun_regime_sensitivity",
    "load_mld_rerun_actual_vs_canonical",
    "load_jtea_rerun",
    "load_jtea_rerun_summary",
    "load_jtea_rerun_method",
    "load_jtea_rerun_claim_evidence_links",
    "load_jtea_rerun_formula_risk_summary",
]
