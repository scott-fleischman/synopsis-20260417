"""Loaders for the Mark-Matthew (mm) and Matthew-Luke (ml) packages.

Both packages expose a primary chain, macro/micro block tables, secondary
echoes, directional burden ledger, variants-by-pair registry, and a shared
global summary. The ML package uses sparser CSVs enriched from detailed
JSONL, hence the extra join step in ``load_ml_pairs``.
"""

from __future__ import annotations

import csv
import json
from typing import Any

import yaml

from .dataset import Dataset


# ---- Mark-Matthew (mm) ----


def load_mm_pairs(ds: Dataset) -> list[dict[str, Any]]:
    pairs = []
    with open(ds.root / "data" / "07_primary_chain_pairs.csv") as f:
        for r in csv.DictReader(f):
            pairs.append({
                "a_ref": r["mark_ref"],
                "b_ref": r["matt_ref"],
                "a_idx": ds.ref_idx(r["mark_ref"]),
                "b_idx": ds.ref_idx(r["matt_ref"]),
                "macro": int(r["macro_block"]),
                "micro": int(r["micro_block"]),
                "score": float(r["score"]),
                "classes": r["pair_classes"].split(";") if r["pair_classes"] else [],
                "ins": int(r["lemma_insertions"] or 0),
                "del": int(r["lemma_deletions"] or 0),
                "rep": int(r["lemma_replacements"] or 0),
                "a_text": r["mark_text"],
                "b_text": r["matt_text"],
                "a_var": int(r["mark_variant_note_count"] or 0),
                "b_var": int(r["matt_variant_note_count"] or 0),
                "wj_content": float(r["wj_content"] or 0),
                "wj_bigram": float(r["wj_bigram"] or 0),
                "sr_content": float(r["sr_content"] or 0),
                "rare_inter": float(r["rare_inter"] or 0),
                "common": r["common_lemmas"].split(";") if r["common_lemmas"] else [],
                "a_only_lemmas": r["mark_only_lemmas"].split(";") if r["mark_only_lemmas"] else [],
                "b_only_lemmas": r["matt_only_lemmas"].split(";") if r["matt_only_lemmas"] else [],
            })
    return pairs


def load_mm_macro(ds: Dataset) -> list[dict[str, Any]]:
    blocks = []
    with open(ds.root / "data" / "17_macro_block_table.csv") as f:
        for r in csv.DictReader(f):
            blocks.append({
                "id": int(r["block_id"]),
                "a_start": r["mark_start_ref"],
                "a_end": r["mark_end_ref"],
                "b_start": r["matt_start_ref"],
                "b_end": r["matt_end_ref"],
                "a_start_idx": ds.ref_idx(r["mark_start_ref"]),
                "a_end_idx": ds.ref_idx(r["mark_end_ref"]),
                "b_start_idx": ds.ref_idx(r["matt_start_ref"]),
                "b_end_idx": ds.ref_idx(r["matt_end_ref"]),
                "pair_count": int(r["pair_count"]),
                "avg_score": float(r["avg_score"]),
                "confidence": r["confidence"],
                "a_unmatched": int(r["mark_unmatched_verse_count"]),
                "b_unmatched": int(r["matt_unmatched_verse_count"]),
                "a_tokens": int(r["mark_token_count"]),
                "b_tokens": int(r["matt_token_count"]),
                "a_var": int(r["mark_variant_count"]),
                "b_var": int(r["matt_variant_count"]),
                "density": float(r["span_density"]),
                "a_prior_ops": r["mark_prior_operations"].split(";") if r["mark_prior_operations"] else [],
                "b_prior_ops": r["matt_prior_operations"].split(";") if r["matt_prior_operations"] else [],
            })
    return blocks


def load_mm_micro(ds: Dataset) -> list[dict[str, Any]]:
    blocks = []
    with open(ds.root / "data" / "18_micro_block_table.csv") as f:
        for r in csv.DictReader(f):
            blocks.append({
                "id": int(r["block_id"]),
                "a_start": r["mark_start_ref"],
                "a_end": r["mark_end_ref"],
                "b_start": r["matt_start_ref"],
                "b_end": r["matt_end_ref"],
                "a_start_idx": ds.ref_idx(r["mark_start_ref"]),
                "b_start_idx": ds.ref_idx(r["matt_start_ref"]),
                "pair_count": int(r["pair_count"]),
                "avg_score": float(r["avg_score"]),
                "confidence": r["confidence"],
                "a_tokens": int(r["mark_token_count"]),
                "b_tokens": int(r["matt_token_count"]),
            })
    return blocks


def load_mm_echoes(ds: Dataset) -> list[dict[str, Any]]:
    with open(ds.root / "data" / "12_secondary_echoes.yaml") as f:
        data = yaml.safe_load(f)
    out = []
    for e in data:
        out.append({
            "a_ref": e["mark_ref"],
            "b_ref": e["matt_ref"],
            "a_idx": ds.ref_idx(e["mark_ref"]),
            "b_idx": ds.ref_idx(e["matt_ref"]),
            "score": float(e["score"]),
            "category": e.get("category", ""),
            "nonlocal": bool(e.get("nonlocal", False)),
        })
    return out


def load_mm_detailed(ds: Dataset, limit: int | None = None) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    with open(ds.root / "data" / "08_primary_chain_pairs_detailed.jsonl") as f:
        for i, line in enumerate(f):
            obj = json.loads(line)
            key = f"{obj['mark_ref']}|{obj['matt_ref']}"
            records[key] = {
                "a_ref": obj["mark_ref"],
                "b_ref": obj["matt_ref"],
                "score": obj["score"],
                "classes": obj["pair_classes"],
                "a_text": obj["mark_text"],
                "b_text": obj["matt_text"],
                "common_lemmas": obj.get("common_lemmas", []),
                "a_only": obj.get("mark_only_lemmas", []),
                "b_only": obj.get("matt_only_lemmas", []),
                "surface_opcodes": obj.get("surface_diff", {}).get("opcodes", []),
                "lemma_opcodes": obj.get("lemma_diff", {}).get("opcodes", []),
                "a_variant_notes": obj.get("mark_variant_notes", []),
                "b_variant_notes": obj.get("matt_variant_notes", []),
            }
            if limit and i + 1 >= limit:
                break
    return records


# ---- Matthew-Luke (ml) ----


def load_ml_pairs(ds: Dataset) -> list[dict[str, Any]]:
    """ML CSV is sparser; enrich with detailed JSONL where available."""
    details_by_key: dict[str, dict[str, Any]] = {}
    with open(ds.root / "data" / "08_primary_chain_pairs_detailed.jsonl") as f:
        for line in f:
            obj = json.loads(line)
            key = f"{obj['matt_ref']}|{obj['luke_ref']}"
            details_by_key[key] = obj

    pairs = []
    with open(ds.root / "data" / "07_primary_chain_pairs.csv") as f:
        for r in csv.DictReader(f):
            key = f"{r['matt_ref']}|{r['luke_ref']}"
            d = details_by_key.get(key, {})
            diff = d.get("diff", {})
            pairs.append({
                "a_ref": r["matt_ref"],
                "b_ref": r["luke_ref"],
                "a_idx": ds.ref_idx(r["matt_ref"]),
                "b_idx": ds.ref_idx(r["luke_ref"]),
                "macro": None,
                "micro": None,
                "score": float(r["score"]),
                "score_content": float(r.get("score_content") or 0),
                "score_all": float(r.get("score_all") or 0),
                "neighbor_support": float(r.get("neighbor_support") or 0),
                "classes": r["pair_classes"].split(";") if r["pair_classes"] else [],
                "ins": len(diff.get("lemma_insertions", [])) if diff else 0,
                "del": len(diff.get("lemma_deletions", [])) if diff else 0,
                "rep": len(diff.get("lemma_replacements", [])) if diff else 0,
                "a_text": d.get("matt_text", ""),
                "b_text": d.get("luke_text", ""),
                "a_var": len(d.get("variant_notes", {}).get("matt", [])),
                "b_var": len(d.get("variant_notes", {}).get("luke", [])),
                "a_tokens": int(r.get("matt_token_count") or 0),
                "b_tokens": int(r.get("luke_token_count") or 0),
            })
    return pairs


def load_ml_macro(ds: Dataset) -> list[dict[str, Any]]:
    blocks = []
    with open(ds.root / "data" / "17_macro_block_table.csv") as f:
        for r in csv.DictReader(f):
            blocks.append({
                "id": int(r["id"]),
                "a_start": r["matt_start_ref"],
                "a_end": r["matt_end_ref"],
                "b_start": r["luke_start_ref"],
                "b_end": r["luke_end_ref"],
                "a_start_idx": ds.ref_idx(r["matt_start_ref"]),
                "a_end_idx": ds.ref_idx(r["matt_end_ref"]),
                "b_start_idx": ds.ref_idx(r["luke_start_ref"]),
                "b_end_idx": ds.ref_idx(r["luke_end_ref"]),
                "pair_count": int(r["pair_count"]),
                "avg_score": float(r["avg_score"]),
                "confidence": r["confidence"],
                "a_unmatched": int(r["unmatched_matt_count"]),
                "b_unmatched": int(r["unmatched_luke_count"]),
                "a_tokens": int(r["matt_token_count"]),
                "b_tokens": int(r["luke_token_count"]),
                "a_var": 0,
                "b_var": 0,
                "density": 0.0,
                "a_prior_strain": r.get("matt_prior_overall_strain", ""),
                "b_prior_strain": r.get("luke_prior_overall_strain", ""),
                "markers": {
                    "a_tote": int(r.get("matt_tote") or 0),
                    "b_tote": int(r.get("luke_tote") or 0),
                    "a_simeron": int(r.get("matt_simeron") or 0),
                    "b_simeron": int(r.get("luke_simeron") or 0),
                    "a_kingdom_god": int(r.get("matt_kingdom_god") or 0),
                    "a_kingdom_heaven": int(r.get("matt_kingdom_heaven") or 0),
                    "b_kingdom_god": int(r.get("luke_kingdom_god") or 0),
                    "b_kingdom_heaven": int(r.get("luke_kingdom_heaven") or 0),
                    "a_present_ratio": float(r.get("matt_present_indicative_ratio") or 0),
                    "b_present_ratio": float(r.get("luke_present_indicative_ratio") or 0),
                    "secondary_echo_count": int(r.get("secondary_echo_count") or 0),
                },
            })
    return blocks


def load_ml_micro(ds: Dataset) -> list[dict[str, Any]]:
    blocks = []
    with open(ds.root / "data" / "18_micro_block_table.csv") as f:
        for r in csv.DictReader(f):
            blocks.append({
                "id": int(r["id"]),
                "a_start": r["matt_start_ref"],
                "a_end": r["matt_end_ref"],
                "b_start": r["luke_start_ref"],
                "b_end": r["luke_end_ref"],
                "a_start_idx": ds.ref_idx(r["matt_start_ref"]),
                "b_start_idx": ds.ref_idx(r["luke_start_ref"]),
                "pair_count": int(r["pair_count"]),
                "avg_score": float(r["avg_score"]),
                "confidence": r["confidence"],
                "a_tokens": int(r["matt_token_count"]),
                "b_tokens": int(r["luke_token_count"]),
            })
    return blocks


def load_ml_echoes(ds: Dataset) -> list[dict[str, Any]]:
    with open(ds.root / "data" / "12_secondary_echoes.yaml") as f:
        data = yaml.safe_load(f)
    sel: dict[str, dict[str, Any]] = {}
    with open(ds.root / "data" / "21_selected_secondary_echoes.yaml") as f:
        for e in yaml.safe_load(f) or []:
            key = f"{e['matt_ref']}|{e['luke_ref']}"
            sel[key] = e
    out = []
    for e in data:
        key = f"{e['matt_ref']}|{e['luke_ref']}"
        extra = sel.get(key, {})
        out.append({
            "a_ref": e["matt_ref"],
            "b_ref": e["luke_ref"],
            "a_idx": ds.ref_idx(e["matt_ref"]),
            "b_idx": ds.ref_idx(e["luke_ref"]),
            "score": float(e.get("score", 0)),
            "window_support": float(e.get("window_support") or 0),
            "composite_score": float(e.get("composite_score") or 0),
            "tags": e.get("tags", []),
            "sources": e.get("sources", []),
            "nonlocality": float(e.get("nonlocality_vs_primary") or 0),
            "nonlocal": "nonlocal_reorder" in e.get("tags", []),
            "category": "",
            "a_text": extra.get("matt_text", e.get("matt_text", "")),
            "b_text": extra.get("luke_text", e.get("luke_text", "")),
        })
    return out


def load_ml_detailed(ds: Dataset, limit: int | None = None) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    with open(ds.root / "data" / "08_primary_chain_pairs_detailed.jsonl") as f:
        for i, line in enumerate(f):
            obj = json.loads(line)
            key = f"{obj['matt_ref']}|{obj['luke_ref']}"
            diff = obj.get("diff", {}) or {}
            records[key] = {
                "a_ref": obj["matt_ref"],
                "b_ref": obj["luke_ref"],
                "score": obj["score"],
                "classes": obj["pair_classes"],
                "a_text": obj["matt_text"],
                "b_text": obj["luke_text"],
                "lemma_insertions": diff.get("lemma_insertions", []),
                "lemma_deletions": diff.get("lemma_deletions", []),
                "lemma_replacements": diff.get("lemma_replacements", []),
                "moved_lemmas": diff.get("moved_lemmas", []),
                "order_divergence": diff.get("order_divergence", 0),
                "opcodes": diff.get("opcodes", []),
                "direction_notes": obj.get("direction_notes", {}),
                "a_variant_notes": obj.get("variant_notes", {}).get("matt", []),
                "b_variant_notes": obj.get("variant_notes", {}).get("luke", []),
            }
            if limit and i + 1 >= limit:
                break
    return records


# ---- Shared (mm + ml, used by generic pages) ----


def load_gaps(ds: Dataset) -> list[dict[str, Any]]:
    with open(ds.root / "data" / "11_order_intervals.yaml") as f:
        data = yaml.safe_load(f) or []
    out = []
    for g in data:
        if ds.name == "mm":
            a = g.get("mark_gap")
            b = g.get("matt_gap")
        else:
            a = g.get("matt_gap")
            b = g.get("luke_gap")
        out.append({
            "before_block": g.get("before_block"),
            "a_gap": a if a else None,
            "b_gap": b if b else None,
            "interpretation": g.get("interpretation", []),
        })
    return out


def load_summary(ds: Dataset) -> Any:
    with open(ds.root / "data" / "16_global_summary.yaml") as f:
        return yaml.safe_load(f)


def load_ledger(ds: Dataset) -> Any:
    with open(ds.root / "data" / "14_direction_ledger_by_loose_block.yaml") as f:
        return yaml.safe_load(f)


def load_burden(ds: Dataset) -> Any:
    with open(ds.root / "data" / "15_direction_burden_totals.yaml") as f:
        return yaml.safe_load(f)


def load_negspace(ds: Dataset) -> list[dict[str, Any]]:
    rows = []
    with open(ds.root / "data" / "01_negative_space_flags.csv") as f:
        for r in csv.DictReader(f):
            # MM uses content_lemma_count/surface_token_count/short_content/short_surface
            # ML uses content_token_count/token_count/short_verse + extra marker columns
            content = r.get("content_lemma_count") or r.get("content_token_count") or "0"
            token = r.get("surface_token_count") or r.get("token_count") or "0"
            short = r.get("short_content") or r.get("short_verse") or "False"
            rows.append({
                "book": r["book"],
                "ref": r["ref"],
                "idx": ds.ref_idx(r["ref"]),
                "lemma_count": int(content),
                "token_count": int(token),
                "short_content": short == "True",
                "citation_formula": r.get("citation_formula", "False") == "True",
                "short_surface": (r.get("short_surface") or r.get("short_verse") or "False") == "True",
                "tote": int(r.get("tote") or 0),
                "simeron": int(r.get("simeron") or 0),
                "kingdom_god": int(r.get("kingdom_god") or 0),
                "kingdom_heaven": int(r.get("kingdom_heaven") or 0),
                "pleroo": int(r.get("pleroo") or 0),
                "grapho": int(r.get("grapho") or 0),
            })
    return rows


def load_lemma_deltas(ds: Dataset) -> Any:
    with open(ds.root / "data" / "20_top_lemma_deltas.yaml") as f:
        return yaml.safe_load(f)


def load_loose_full(ds: Dataset) -> Any:
    with open(ds.root / "data" / "09_loose_blocks.yaml") as f:
        return yaml.safe_load(f)


def load_variants(ds: Dataset) -> Any:
    with open(ds.root / "data" / "13_variants_by_primary_pair.yaml") as f:
        return yaml.safe_load(f)
