"""Loaders for the Markan-masked Matt-Luke (mld) package.

This package differs from the plain ``ml`` loaders in two ways:

1. The masking step removes verses, so every row carries an ``original_idx``
   (source position before masking) alongside the packed ``idx`` used for
   visualization axes.
2. The pair-class vocabulary is tag-driven, so ``_mld_classes_from_tags``
   maps the mld tag set onto the generic class labels shared with ``ml``.
"""

from __future__ import annotations

import csv
import json
from typing import Any

import yaml

from .dataset import Dataset
from .loaders_synoptic import load_variants


MLD_TAG_TO_CLASS = {
    "close_match": "close_match",
    "strong_parallel": "close_match",
    "moderate_parallel": "partial_overlap",
    "weak_parallel": "partial_overlap",
    "matt_expands_or_luke_abbreviates": "matt_expands",
    "luke_expands_or_matt_abbreviates": "luke_expands",
    "content_order_preserved": "reordering_absent",
    "nonlocal_reorder": "reordering",
    "substitution_heavy": "substitution",
    "shared_rare_vocabulary": "rare_shared",
    "multi_lemma_overlap": "multi_overlap",
    "formulaic_shared": "formulaic",
}


def _mld_classes_from_tags(tags: list[str]) -> list[str]:
    out: list[str] = []
    for t in tags:
        c = MLD_TAG_TO_CLASS.get(t)
        if c and c not in out:
            out.append(c)
    return out


def load_mld_flat_diffs(ds: Dataset) -> dict[str, dict[str, dict[str, Any]]]:
    """19_pair_diffs_flat.tsv is authoritative for lemma partitions."""
    rows: dict[str, dict[str, dict[str, Any]]] = {}
    with open(ds.root / "data" / "19_pair_diffs_flat.tsv") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            key = f"{r['matt_ref']}|{r['luke_ref']}"
            rows.setdefault(r["layer"], {})[key] = {
                "matt_only_lemmas": r["matt_only_lemmas"].split() if r["matt_only_lemmas"] else [],
                "luke_only_lemmas": r["luke_only_lemmas"].split() if r["luke_only_lemmas"] else [],
                "shared_lemmas": r["shared_lemmas"].split() if r["shared_lemmas"] else [],
                "lemma_diff": r["lemma_diff"],
                "surface_diff": r["surface_diff"],
                "matt_text": r["matt_text"],
                "luke_text": r["luke_text"],
                "score": float(r["score"]) if r["score"] else 0.0,
                "lcs": float(r["lcs"]) if r["lcs"] else 0.0,
                "tags": r["tags"].split(";") if r["tags"] else [],
            }
    return rows


def load_mld_pairs(ds: Dataset) -> list[dict[str, Any]]:
    details_by_key: dict[str, dict[str, Any]] = {}
    with open(ds.root / "data" / "08_primary_chain_pairs_detailed.jsonl") as f:
        for line in f:
            obj = json.loads(line)
            key = f"{obj['matt_ref']}|{obj['luke_ref']}"
            details_by_key[key] = obj

    flat = load_mld_flat_diffs(ds).get("primary_chain", {})

    pairs: list[dict[str, Any]] = []
    with open(ds.root / "data" / "07_primary_chain_pairs.csv") as f:
        for r in csv.DictReader(f):
            key = f"{r['matt_ref']}|{r['luke_ref']}"
            d = details_by_key.get(key, {})
            fd = flat.get(key, {})
            tags = r["tags"].split(";") if r["tags"] else []
            pairs.append({
                "pair_id": int(r["pair_id"]),
                "a_ref": r["matt_ref"],
                "b_ref": r["luke_ref"],
                "a_idx": ds.ref_idx(r["matt_ref"]),
                "b_idx": ds.ref_idx(r["luke_ref"]),
                "a_original_idx": int(r["matt_original_idx"]),
                "b_original_idx": int(r["luke_original_idx"]),
                "macro": None,
                "micro": None,
                "score": float(r["score"]),
                "lcs": float(r["lcs"] or 0),
                "classes": _mld_classes_from_tags(tags),
                "tags": tags,
                "ins": len(fd.get("luke_only_lemmas", [])),
                "del": len(fd.get("matt_only_lemmas", [])),
                "rep": 0,
                "a_text": d.get("matt_text") or fd.get("matt_text", ""),
                "b_text": d.get("luke_text") or fd.get("luke_text", ""),
                "a_var": 0,
                "b_var": 0,
                "a_tokens": int(r.get("matt_token_count") or 0),
                "b_tokens": int(r.get("luke_token_count") or 0),
                "common": fd.get("shared_lemmas", []),
                "a_only_lemmas": fd.get("matt_only_lemmas", []),
                "b_only_lemmas": fd.get("luke_only_lemmas", []),
                "lemma_diff": fd.get("lemma_diff", ""),
                "surface_diff": fd.get("surface_diff", ""),
            })

    # Join variant counts from the variants YAML
    variants_by_pair_id: dict[int, dict[str, Any]] = {}
    try:
        with open(ds.root / "data" / "13_variants_by_primary_pair.yaml") as f:
            for v in yaml.safe_load(f) or []:
                variants_by_pair_id[v["pair_id"]] = v
    except FileNotFoundError:
        pass
    for p in pairs:
        v = variants_by_pair_id.get(p["pair_id"], {})
        p["a_var"] = len(v.get("matt_variant_notes", []))
        p["b_var"] = len(v.get("luke_variant_notes", []))
    return pairs


def load_mld_macro(ds: Dataset) -> list[dict[str, Any]]:
    blocks = []
    with open(ds.root / "data" / "17_macro_block_table.csv") as f:
        for r in csv.DictReader(f):
            blocks.append({
                "id": int(r["block_id"]),
                "a_start": r["matt_start"],
                "a_end": r["matt_end"],
                "b_start": r["luke_start"],
                "b_end": r["luke_end"],
                "a_start_idx": ds.ref_idx(r["matt_start"]),
                "a_end_idx": ds.ref_idx(r["matt_end"]),
                "b_start_idx": ds.ref_idx(r["luke_start"]),
                "b_end_idx": ds.ref_idx(r["luke_end"]),
                "pair_count": int(r["pair_count"]),
                "avg_score": float(r["mean_score"]),
                "min_score": float(r["min_score"]),
                "max_score": float(r["max_score"]),
                "confidence": "",
                "a_unmatched": 0,
                "b_unmatched": 0,
                "a_tokens": 0,
                "b_tokens": 0,
                "a_var": 0,
                "b_var": 0,
                "density": 0.0,
                "a_original_start_idx": int(r["matt_original_start_idx"]),
                "a_original_end_idx": int(r["matt_original_end_idx"]),
                "b_original_start_idx": int(r["luke_original_start_idx"]),
                "b_original_end_idx": int(r["luke_original_end_idx"]),
            })
    return blocks


def load_mld_micro(ds: Dataset) -> list[dict[str, Any]]:
    blocks = []
    with open(ds.root / "data" / "18_micro_block_table.csv") as f:
        for r in csv.DictReader(f):
            blocks.append({
                "id": int(r["block_id"]),
                "a_start": r["matt_start"],
                "a_end": r["matt_end"],
                "b_start": r["luke_start"],
                "b_end": r["luke_end"],
                "a_start_idx": ds.ref_idx(r["matt_start"]),
                "b_start_idx": ds.ref_idx(r["luke_start"]),
                "pair_count": int(r["pair_count"]),
                "avg_score": float(r["mean_score"]),
                "confidence": "",
                "a_tokens": 0,
                "b_tokens": 0,
            })
    return blocks


def load_mld_echoes(ds: Dataset) -> list[dict[str, Any]]:
    """Echoes plus a nonlocality proxy computed against the primary chain."""
    with open(ds.root / "data" / "12_secondary_echoes.yaml") as f:
        data = yaml.safe_load(f) or []

    anchors: list[tuple[int, int]] = []
    with open(ds.root / "data" / "07_primary_chain_pairs.csv") as f:
        for r in csv.DictReader(f):
            anchors.append((ds.ref_idx(r["matt_ref"]), ds.ref_idx(r["luke_ref"])))
    anchors.sort(key=lambda x: x[0])

    def expected_b(a_idx: int) -> float:
        if not anchors:
            return float(a_idx)
        before: tuple[int, int] | None = None
        after: tuple[int, int] | None = None
        for ai, bi in anchors:
            if ai <= a_idx:
                before = (ai, bi)
            if ai >= a_idx and after is None:
                after = (ai, bi)
        if before and after and before[0] != after[0]:
            frac = (a_idx - before[0]) / (after[0] - before[0])
            return before[1] + frac * (after[1] - before[1])
        if before:
            return float(before[1])
        if after:
            return float(after[1])
        return float(a_idx)

    out: list[dict[str, Any]] = []
    for e in data:
        tags = e.get("tags", [])
        a_idx = ds.ref_idx(e["matt_ref"])
        b_idx = ds.ref_idx(e["luke_ref"])
        nl = abs(b_idx - expected_b(a_idx))
        out.append({
            "a_ref": e["matt_ref"],
            "b_ref": e["luke_ref"],
            "a_idx": a_idx,
            "b_idx": b_idx,
            "score": float(e.get("score", 0)),
            "lcs": float(e.get("lcs", 0) or 0),
            "shared_content_lemmas": int(e.get("shared_content_lemmas") or 0),
            "shared_content_lemma_list": e.get("shared_content_lemma_list", []),
            "tags": tags,
            "nonlocality": round(nl, 2),
            "nonlocal": "nonlocal_reorder" in tags,
            "category": "",
            "composite_score": float(e.get("score", 0)),
            "a_text": e.get("matt_text", ""),
            "b_text": e.get("luke_text", ""),
        })
    return out


def load_mld_detailed(ds: Dataset) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    flat = load_mld_flat_diffs(ds).get("primary_chain", {})
    with open(ds.root / "data" / "08_primary_chain_pairs_detailed.jsonl") as f:
        for line in f:
            obj = json.loads(line)
            key = f"{obj['matt_ref']}|{obj['luke_ref']}"
            fd = flat.get(key, {})
            records[key] = {
                "a_ref": obj["matt_ref"],
                "b_ref": obj["luke_ref"],
                "score": obj["score"],
                "classes": _mld_classes_from_tags(obj.get("tags", [])),
                "tags": obj.get("tags", []),
                "a_text": obj["matt_text"],
                "b_text": obj["luke_text"],
                "a_lemmas": obj.get("matt_lemmas", []),
                "b_lemmas": obj.get("luke_lemmas", []),
                "lemma_diff": obj.get("lemma_diff", ""),
                "surface_diff": obj.get("surface_diff", ""),
                "common_lemmas": fd.get("shared_lemmas", []),
                "a_only": fd.get("matt_only_lemmas", []),
                "b_only": fd.get("luke_only_lemmas", []),
            }
    return records


def load_mld_gaps(ds: Dataset) -> list[dict[str, Any]]:
    """Normalize mld gaps to {a_gap: {verse_count, start_ref, end_ref}}."""
    with open(ds.root / "data" / "11_order_intervals.yaml") as f:
        data = yaml.safe_load(f) or []
    out = []
    for g in data:
        mv = g.get("matt_gap_unmasked_verse_count") or 0
        lv = g.get("luke_gap_unmasked_verse_count") or 0
        a_gap = None
        if mv:
            a_gap = {
                "verse_count": mv,
                "start_ref": g.get("matt_gap_start") or "",
                "end_ref": g.get("matt_gap_end") or "",
            }
        b_gap = None
        if lv:
            b_gap = {
                "verse_count": lv,
                "start_ref": g.get("luke_gap_start") or "",
                "end_ref": g.get("luke_gap_end") or "",
            }
        asym = g.get("asymmetry_abs")
        interp: list[str] = []
        if asym is not None:
            interp.append(f"|Δ| = {asym} unmasked verses")
        out.append({
            "before_block": g.get("before_block"),
            "after_block": g.get("after_block"),
            "a_gap": a_gap,
            "b_gap": b_gap,
            "asymmetry_abs": asym,
            "interpretation": interp,
        })
    return out


def load_mld_negspace(ds: Dataset) -> list[dict[str, Any]]:
    rows = []
    with open(ds.root / "data" / "01_negative_space_flags.csv") as f:
        for r in csv.DictReader(f):
            rows.append({
                "book": r["book"],
                "ref": r["ref"],
                "idx": ds.ref_idx(r["ref"]),
                "original_idx": int(r.get("original_idx") or 0),
                "lemma_count": int(r.get("content_token_count") or 0),
                "token_count": int(r.get("token_count") or 0),
                "cheap_lemma_ratio": float(r.get("cheap_lemma_ratio") or 0),
                "low_information": r.get("low_information", "False") == "True",
                "formulaic_proxy": r.get("formulaic_proxy", "False") == "True",
                "variant_note_count": int(r.get("variant_note_count") or 0),
                "masked_as_markan": r.get("masked_as_markan", "False") == "True",
                "mask_rule": r.get("mask_rule", ""),
                "short_content": False,
                "citation_formula": False,
                "short_surface": False,
            })
    return rows


def load_mld_mask_audit(ds: Dataset) -> list[dict[str, Any]]:
    rows = []
    with open(ds.root / "data" / "01_markan_mask_by_verse.csv") as f:
        for r in csv.DictReader(f):
            rows.append({
                "book": r["book"],
                "ref": r["ref"],
                "idx": ds.ref_idx(r["ref"]),
                "original_idx": int(r.get("original_idx") or 0),
                "masked_as_markan": r.get("masked_as_markan", "False") == "True",
                "mask_rule": r.get("mask_rule", ""),
                "best_mark_ref": r.get("best_mark_ref", ""),
                "best_mark_score": float(r.get("best_mark_score") or 0),
                "best_mark_base_score": float(r.get("best_mark_base_score") or 0),
                "best_mark_lcs": float(r.get("best_mark_lcs") or 0),
                "shared_content_lemmas": int(r.get("best_mark_shared_content_lemmas") or 0),
                "rare_shared": int(r.get("best_mark_rare_shared_lemmas") or 0),
                "best_window_mark_ref": r.get("best_window_mark_ref", ""),
                "best_window_score": float(r.get("best_window_score") or 0),
                "in_markan_chain": r.get("in_markan_chain", "False") == "True",
                "chain_mark_ref": r.get("chain_mark_ref", ""),
                "chain_score": float(r.get("chain_score") or 0),
                "local_cluster": r.get("local_cluster", "False") == "True",
                "token_count": int(r.get("token_count") or 0),
                "content_token_count": int(r.get("content_token_count") or 0),
                "text": r.get("text", ""),
            })
    return rows


def load_mld_ledger(ds: Dataset) -> Any:
    with open(ds.root / "data" / "14_direction_ledger_by_loose_block.yaml") as f:
        return yaml.safe_load(f)


def load_mld_burden(ds: Dataset) -> Any:
    with open(ds.root / "data" / "15_direction_burden_totals.yaml") as f:
        return yaml.safe_load(f)


def load_mld_loose_full(ds: Dataset) -> Any:
    with open(ds.root / "data" / "09_loose_blocks.yaml") as f:
        return yaml.safe_load(f)


def load_mld_summary(ds: Dataset) -> Any:
    with open(ds.root / "data" / "16_global_summary.yaml") as f:
        return yaml.safe_load(f)


def load_mld_lemma_deltas(ds: Dataset) -> Any:
    with open(ds.root / "data" / "20_top_lemma_deltas.yaml") as f:
        return yaml.safe_load(f)


__all__ = [
    "MLD_TAG_TO_CLASS",
    "load_mld_pairs",
    "load_mld_macro",
    "load_mld_micro",
    "load_mld_echoes",
    "load_mld_detailed",
    "load_mld_gaps",
    "load_mld_negspace",
    "load_mld_mask_audit",
    "load_mld_ledger",
    "load_mld_burden",
    "load_mld_loose_full",
    "load_mld_summary",
    "load_mld_lemma_deltas",
    "load_variants",
]
