#!/usr/bin/env python3
"""Preprocess both synoptic-dependence datasets into a single compact JSON bundle.

Outputs:
    visualizations/data/bundle.json  — for fetch-based consumption
    visualizations/data/bundle.js    — window.SYNOPSIS = {...} for file:// use

Each dataset is normalized to generic a/b fields (a = earlier/source in each bundle,
b = later/target). This lets one shared code path render either Mark–Matthew
(a=Mark, b=Matt) or Matthew–Luke (a=Matt, b=Luke).
"""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "visualizations" / "data"
OUT.mkdir(parents=True, exist_ok=True)


REF_RE = re.compile(r"(Mark|Matt|Luke)\s+(\d+):(\d+)")


def infer_chapter_lengths(csv_path: Path) -> dict[str, dict[int, int]]:
    """Return max verse seen per (book, chapter) from a ref-bearing CSV."""
    counts: dict[str, dict[int, int]] = {}
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            book = r["book"]
            ref = r["ref"]
            body = ref.split(None, 1)[1]
            chap, verse = body.split(":")
            chap, verse = int(chap), int(verse)
            counts.setdefault(book, {})
            counts[book][chap] = max(counts[book].get(chap, 0), verse)
    return counts


def chapter_offsets(chapter_lens: dict[int, int]):
    running = 0
    offsets = {}
    for chap in sorted(chapter_lens):
        offsets[chap] = running
        running += chapter_lens[chap]
    return offsets, running


class Dataset:
    def __init__(self, name: str, root: Path, a_book: str, b_book: str, label: str):
        self.name = name
        self.root = root
        self.a_book = a_book
        self.b_book = b_book
        self.label = label

        # Chapter lengths derived from negative-space flags (authoritative).
        chap_lens = infer_chapter_lengths(root / "data" / "01_negative_space_flags.csv")
        self.a_chaps = chap_lens[a_book]
        self.b_chaps = chap_lens[b_book]
        self.a_offsets, self.a_total = chapter_offsets(self.a_chaps)
        self.b_offsets, self.b_total = chapter_offsets(self.b_chaps)

    def ref_idx(self, ref: str) -> int:
        m = REF_RE.match(ref)
        if not m:
            return -1
        book, chap, verse = m.group(1), int(m.group(2)), int(m.group(3))
        if book == self.a_book:
            return self.a_offsets[chap] + (verse - 1)
        if book == self.b_book:
            return self.b_offsets[chap] + (verse - 1)
        return -1

    def chap_info(self, book: str):
        if book == self.a_book:
            chaps, offsets = self.a_chaps, self.a_offsets
        else:
            chaps, offsets = self.b_chaps, self.b_offsets
        return [
            {"chapter": c, "offset": offsets[c], "length": chaps[c]}
            for c in sorted(chaps)
        ]


# ---- Mark-Matthew specific loaders ----


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


def load_mm_macro(ds: Dataset):
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


def load_mm_micro(ds: Dataset):
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


def load_mm_echoes(ds: Dataset):
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


def load_mm_detailed(ds: Dataset, limit: int | None = None):
    """Load full opcode-level diffs (for pair explorer). Trim tokens to keep size."""
    records = {}
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


# ---- Matt-Luke specific loaders ----


def load_ml_pairs(ds: Dataset) -> list[dict[str, Any]]:
    """ML CSV is sparser; enrich with detailed JSONL where available."""
    details_by_key = {}
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


def load_ml_macro(ds: Dataset):
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
                "a_var": 0,  # ML macro table doesn't carry variant counts
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


def load_ml_micro(ds: Dataset):
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


def load_ml_echoes(ds: Dataset):
    with open(ds.root / "data" / "12_secondary_echoes.yaml") as f:
        data = yaml.safe_load(f)
    # Also load the selected set, which has Greek texts.
    sel = {}
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


def load_ml_detailed(ds: Dataset, limit: int | None = None):
    records = {}
    with open(ds.root / "data" / "08_primary_chain_pairs_detailed.jsonl") as f:
        for i, line in enumerate(f):
            obj = json.loads(line)
            key = f"{obj['matt_ref']}|{obj['luke_ref']}"
            diff = obj.get("diff", {}) or {}
            opcodes = diff.get("opcodes", [])
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
                "opcodes": opcodes,
                "direction_notes": obj.get("direction_notes", {}),
                "a_variant_notes": obj.get("variant_notes", {}).get("matt", []),
                "b_variant_notes": obj.get("variant_notes", {}).get("luke", []),
            }
            if limit and i + 1 >= limit:
                break
    return records


# ---- Generic shared loaders ----


def load_gaps(ds: Dataset) -> list[dict]:
    with open(ds.root / "data" / "11_order_intervals.yaml") as f:
        data = yaml.safe_load(f) or []
    out = []
    for g in data:
        ag = g.get("mark_gap") or g.get("matt_gap") or g.get("mark_gap")
        # MM uses mark_gap/matt_gap; ML uses matt_gap/luke_gap
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


def load_summary(ds: Dataset):
    with open(ds.root / "data" / "16_global_summary.yaml") as f:
        return yaml.safe_load(f)


def load_ledger(ds: Dataset):
    with open(ds.root / "data" / "14_direction_ledger_by_loose_block.yaml") as f:
        return yaml.safe_load(f)


def load_burden(ds: Dataset):
    with open(ds.root / "data" / "15_direction_burden_totals.yaml") as f:
        return yaml.safe_load(f)


def load_negspace(ds: Dataset):
    rows = []
    with open(ds.root / "data" / "01_negative_space_flags.csv") as f:
        for r in csv.DictReader(f):
            # MM uses content_lemma_count/surface_token_count/short_content/short_surface
            # ML uses content_token_count/token_count/short_verse and extra marker columns
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
                # ML-only markers (tote, simeron, kingdom, etc.)
                "tote": int(r.get("tote") or 0),
                "simeron": int(r.get("simeron") or 0),
                "kingdom_god": int(r.get("kingdom_god") or 0),
                "kingdom_heaven": int(r.get("kingdom_heaven") or 0),
                "pleroo": int(r.get("pleroo") or 0),
                "grapho": int(r.get("grapho") or 0),
            })
    return rows


def load_lemma_deltas(ds: Dataset):
    with open(ds.root / "data" / "20_top_lemma_deltas.yaml") as f:
        return yaml.safe_load(f)


def load_loose_full(ds: Dataset):
    with open(ds.root / "data" / "09_loose_blocks.yaml") as f:
        return yaml.safe_load(f)


def load_variants(ds: Dataset):
    with open(ds.root / "data" / "13_variants_by_primary_pair.yaml") as f:
        return yaml.safe_load(f)


# ---- Masked Matt-Luke (MLD) specific loaders ----


# Map MLD tags to pair-class labels shared with ML visualizations.
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
    out = []
    for t in tags:
        c = MLD_TAG_TO_CLASS.get(t)
        if c and c not in out:
            out.append(c)
    return out


def load_mld_flat_diffs(ds: Dataset) -> dict[str, dict]:
    """Read 19_pair_diffs_flat.tsv — authoritative source for lemma partitions."""
    rows = {}
    with open(ds.root / "data" / "19_pair_diffs_flat.tsv") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
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
    """MLD primary pairs — enrich from detailed JSONL + flat TSV."""
    details_by_key: dict[str, dict] = {}
    with open(ds.root / "data" / "08_primary_chain_pairs_detailed.jsonl") as f:
        for line in f:
            obj = json.loads(line)
            key = f"{obj['matt_ref']}|{obj['luke_ref']}"
            details_by_key[key] = obj

    flat = load_mld_flat_diffs(ds).get("primary_chain", {})

    pairs = []
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
                "rep": 0,  # MLD diffs are rendered text; no structured replacements
                "a_text": d.get("matt_text") or fd.get("matt_text", ""),
                "b_text": d.get("luke_text") or fd.get("luke_text", ""),
                "a_var": 0,  # filled later when variants are cross-joined
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
    variants_by_pair_id = {}
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


def load_mld_macro(ds: Dataset):
    """MLD macro blocks — no confidence column, no variant counts."""
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


def load_mld_micro(ds: Dataset):
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


def load_mld_echoes(ds: Dataset):
    """MLD echoes already embed Greek text; normalize to a/b schema.
    Computes a nonlocality proxy per echo from the primary-chain anchors,
    so the displacement arc diagram can render."""
    with open(ds.root / "data" / "12_secondary_echoes.yaml") as f:
        data = yaml.safe_load(f) or []
    # Build primary-chain anchor table for nonlocality computation
    anchors = []
    with open(ds.root / "data" / "07_primary_chain_pairs.csv") as f:
        for r in csv.DictReader(f):
            anchors.append((ds.ref_idx(r["matt_ref"]), ds.ref_idx(r["luke_ref"])))
    anchors.sort(key=lambda x: x[0])

    def expected_b(a_idx: int) -> float:
        """Linearly interpolate expected b_idx from nearest a_idx anchors."""
        if not anchors:
            return float(a_idx)
        # Before / after anchor
        before = None
        after = None
        for (ai, bi) in anchors:
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

    out = []
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


def load_mld_detailed(ds: Dataset):
    """Return pair-explorer records keyed by a_ref|b_ref."""
    records = {}
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


def load_mld_gaps(ds: Dataset):
    """Normalize mld gaps to the {a_gap: {verse_count, start_ref, end_ref}} shape
    that 02_block_ribbon and 04_gap_timeline expect."""
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
        interp = []
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


def load_mld_negspace(ds: Dataset):
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


def load_mld_mask_audit(ds: Dataset):
    """01_markan_mask_by_verse.csv — per-verse mask decisions and nearest Mark ref."""
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


def load_mld_ledger(ds: Dataset):
    """3-hypothesis ledger, normalized to per-block records."""
    with open(ds.root / "data" / "14_direction_ledger_by_loose_block.yaml") as f:
        return yaml.safe_load(f)


def load_mld_burden(ds: Dataset):
    with open(ds.root / "data" / "15_direction_burden_totals.yaml") as f:
        return yaml.safe_load(f)


def load_mld_loose_full(ds: Dataset):
    with open(ds.root / "data" / "09_loose_blocks.yaml") as f:
        return yaml.safe_load(f)


def load_mld_summary(ds: Dataset):
    with open(ds.root / "data" / "16_global_summary.yaml") as f:
        return yaml.safe_load(f)


def load_mld_lemma_deltas(ds: Dataset):
    with open(ds.root / "data" / "20_top_lemma_deltas.yaml") as f:
        return yaml.safe_load(f)


def build_mld():
    ds = Dataset(
        "mld",
        ROOT / "matt_luke_double_masked_analysis",
        a_book="Matt",
        b_book="Luke",
        label="Matt ↔ Luke (Markan-masked)",
    )
    mask_audit = load_mld_mask_audit(ds)
    # Precompute per-book mask rule counts for UI.
    rule_counts_by_book: dict[str, dict[str, int]] = {}
    masked_idx_by_book: dict[str, list[int]] = {"Matt": [], "Luke": []}
    for row in mask_audit:
        rule_counts_by_book.setdefault(row["book"], {}).setdefault(row["mask_rule"], 0)
        rule_counts_by_book[row["book"]][row["mask_rule"]] += 1
        if row["masked_as_markan"]:
            masked_idx_by_book.setdefault(row["book"], []).append(row["idx"])

    payload = {
        "name": ds.name,
        "a_book": ds.a_book,
        "b_book": ds.b_book,
        "label": ds.label,
        "meta": {
            "a_total_verses": ds.a_total,
            "b_total_verses": ds.b_total,
            "a_chapters": ds.chap_info(ds.a_book),
            "b_chapters": ds.chap_info(ds.b_book),
            "mask_rule_counts": rule_counts_by_book,
            "masked_idx": masked_idx_by_book,
        },
        "pairs": load_mld_pairs(ds),
        "macro": load_mld_macro(ds),
        "micro": load_mld_micro(ds),
        "echoes": load_mld_echoes(ds),
        "gaps": load_mld_gaps(ds),
        "summary": load_mld_summary(ds),
        "ledger": load_mld_ledger(ds),
        "burden": load_mld_burden(ds),
        "negspace": load_mld_negspace(ds),
        "mask_audit": mask_audit,
        "lemma_deltas": load_mld_lemma_deltas(ds),
        "loose_full": load_mld_loose_full(ds),
        "variants": load_variants(ds),
        "detailed": load_mld_detailed(ds),
    }
    return payload


def build_mm():
    ds = Dataset(
        "mm",
        ROOT / "mark_matthew_analysis",
        a_book="Mark",
        b_book="Matt",
        label="Mark ↔ Matthew",
    )
    payload = {
        "name": ds.name,
        "a_book": ds.a_book,
        "b_book": ds.b_book,
        "label": ds.label,
        "meta": {
            "a_total_verses": ds.a_total,
            "b_total_verses": ds.b_total,
            "a_chapters": ds.chap_info(ds.a_book),
            "b_chapters": ds.chap_info(ds.b_book),
        },
        "pairs": load_mm_pairs(ds),
        "macro": load_mm_macro(ds),
        "micro": load_mm_micro(ds),
        "echoes": load_mm_echoes(ds),
        "gaps": load_gaps(ds),
        "summary": load_summary(ds),
        "ledger": load_ledger(ds),
        "burden": load_burden(ds),
        "negspace": load_negspace(ds),
        "lemma_deltas": load_lemma_deltas(ds),
        "loose_full": load_loose_full(ds),
        "variants": load_variants(ds),
        "detailed": load_mm_detailed(ds),
    }
    return payload


def build_ml():
    ds = Dataset(
        "ml",
        ROOT / "matt_luke_analysis",
        a_book="Matt",
        b_book="Luke",
        label="Matthew ↔ Luke",
    )
    payload = {
        "name": ds.name,
        "a_book": ds.a_book,
        "b_book": ds.b_book,
        "label": ds.label,
        "meta": {
            "a_total_verses": ds.a_total,
            "b_total_verses": ds.b_total,
            "a_chapters": ds.chap_info(ds.a_book),
            "b_chapters": ds.chap_info(ds.b_book),
        },
        "pairs": load_ml_pairs(ds),
        "macro": load_ml_macro(ds),
        "micro": load_ml_micro(ds),
        "echoes": load_ml_echoes(ds),
        "gaps": load_gaps(ds),
        "summary": load_summary(ds),
        "ledger": load_ledger(ds),
        "burden": load_burden(ds),
        "negspace": load_negspace(ds),
        "lemma_deltas": load_lemma_deltas(ds),
        "loose_full": load_loose_full(ds),
        "variants": load_variants(ds),
        "detailed": load_ml_detailed(ds),
    }
    return payload


# ---- john_thomas_epistles_apocrypha (jtea) loaders ----
# Fundamentally different from mm/ml/mld: multi-layer network-style data
# (no single primary chain). The payload packs curated registries (YAML)
# plus aggregated/filtered lexical retrieval layers.

JTEA_ROOT = ROOT / "john_thomas_epistles_apocrypha_analysis"


def _yaml(path: Path):
    with open(path) as f:
        return yaml.safe_load(f)


def _csv_rows(path: Path) -> list[dict[str, str]]:
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def _book_order(book: str) -> int:
    # Canonical ordering used for axis labeling / sort.
    order = [
        "Matt", "Mark", "Luke", "John", "Acts",
        "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil", "Col",
        "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm",
        "Heb", "Jas", "1Pet", "2Pet", "1John", "2John", "3John",
        "Jude", "Rev",
    ]
    try:
        return order.index(book)
    except ValueError:
        return 99


def _yaml_list_or_key(path: Path, *keys: str) -> list:
    data = _yaml(path)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in keys:
            v = data.get(k)
            if isinstance(v, list):
                return v
    return []


def load_jtea_case_studies():
    return _yaml_list_or_key(JTEA_ROOT / "data" / "07_targeted_case_studies.yaml", "cases", "case_studies")


def load_jtea_anchors():
    return _yaml_list_or_key(JTEA_ROOT / "data" / "08_john_synoptic_anchor_registry.yaml", "anchors")


def load_jtea_thomas_registry():
    return _yaml_list_or_key(JTEA_ROOT / "data" / "09_thomas_parallel_registry.yaml", "entries", "parallels")


def load_jtea_concepts():
    return _yaml_list_or_key(JTEA_ROOT / "data" / "11_concept_signature_registry.yaml", "concepts", "signatures")


def load_jtea_burden_ledger():
    return _yaml(JTEA_ROOT / "data" / "14_burden_ledger.yaml")


def load_jtea_method():
    return _yaml(JTEA_ROOT / "data" / "00_method_rethought_low_verbatim.yaml")


def load_jtea_summary():
    return _yaml(JTEA_ROOT / "data" / "16_global_summary.yaml")


def load_jtea_thomas_units() -> list[dict[str, Any]]:
    units = []
    for r in _csv_rows(JTEA_ROOT / "data" / "03_thomas_units.csv"):
        raw_id = (r.get("thomas_logion", "") or "").strip()
        # Some rows carry non-numeric ids (e.g., "subtitle"); keep them as strings.
        try:
            idx_val: Any = int(raw_id)
        except ValueError:
            idx_val = raw_id
        units.append({
            "idx": idx_val,
            "word_count": int(r.get("word_count", "0") or 0),
            "lemma_count": int(r.get("lemma_count", "0") or 0),
            "coptic_text": r.get("coptic_text", ""),
            "lemmas": r.get("lemmas", ""),
            "pos_types": r.get("pos_types", ""),
        })
    return units


def load_jtea_apocrypha():
    return _csv_rows(JTEA_ROOT / "data" / "12_apocrypha_inventory_from_mr_james.csv")


def load_jtea_exact_hits():
    rows = []
    for r in _csv_rows(JTEA_ROOT / "data" / "15_filtered_high_value_exact_hits.csv"):
        rows.append({
            "layer": r.get("layer", ""),
            "source_ref": r.get("source_ref", ""),
            "target_ref": r.get("target_ref", ""),
            "score": float(r.get("score", "0") or 0),
            "max_exact_run_len": int(r.get("max_exact_run_len", "0") or 0),
            "max_exact_run": r.get("max_exact_run", ""),
            "shared_content_tokens": r.get("shared_content_tokens", ""),
            "note": r.get("note", ""),
        })
    rows.sort(key=lambda r: (-r["score"], -r["max_exact_run_len"]))
    return rows


def load_jtea_network_edges():
    edges = []
    for r in _csv_rows(JTEA_ROOT / "data" / "13_intertext_network_edges.csv"):
        try:
            score = float(r.get("score", "0") or 0)
        except ValueError:
            score = 0.0
        try:
            run_len = int(r.get("max_exact_run_len", "0") or 0)
        except ValueError:
            run_len = 0
        edges.append({
            "layer": r.get("layer", ""),
            "source_ref": r.get("source_ref", ""),
            "target_ref": r.get("target_ref", ""),
            "edge_basis": r.get("edge_basis", ""),
            "score": score,
            "max_exact_run_len": run_len,
            "max_exact_run": r.get("max_exact_run", ""),
            "flags": r.get("negative_space_flags", ""),
            "reading": r.get("provisional_reading", ""),
        })
    return edges


def load_jtea_negspace_flags():
    # Count flag occurrences + keep a small sample row per flag family.
    flag_counts: dict[str, int] = {}
    sample_row: dict[str, dict[str, Any]] = {}
    rules: dict[str, str] = {}
    for r in _csv_rows(JTEA_ROOT / "data" / "10_negative_space_flags_for_exact_hits.csv"):
        flags = r.get("negative_space_flags", "").strip()
        if not flags:
            continue
        for flg in flags.split("|"):
            flg = flg.strip()
            if not flg:
                continue
            flag_counts[flg] = flag_counts.get(flg, 0) + 1
            if flg not in sample_row:
                sample_row[flg] = {
                    "source_ref": r.get("source_ref", ""),
                    "target_ref": r.get("target_ref", ""),
                    "score": float(r.get("score", "0") or 0),
                    "max_exact_run_len": int(r.get("max_exact_run_len", "0") or 0),
                    "max_exact_run": r.get("max_exact_run", ""),
                }
                rules[flg] = r.get("interpretation_rule", "")
    items = []
    for flg, ct in sorted(flag_counts.items(), key=lambda x: -x[1]):
        items.append({
            "flag": flg,
            "count": ct,
            "sample": sample_row[flg],
            "rule": rules[flg],
        })
    return items


def load_jtea_book_matrix():
    """Aggregate 04 (epistles→gospels) and 05 (john→synoptics) into book×book cells.

    Each cell holds: n_candidates, n_score_ge_0.35, max_score, best_hit (source→target
    with score + exact run). This collapses ~25k candidate rows into a small matrix
    that ships cheaply in the bundle and supports a heatmap view.
    """
    cells: dict[tuple[str, str], dict[str, Any]] = {}

    def _agg(path: Path):
        with open(path) as f:
            for r in csv.DictReader(f):
                sb = r.get("source_book", "")
                tb = r.get("target_book", "")
                if not sb or not tb:
                    continue
                try:
                    sc = float(r.get("score", "0") or 0)
                except ValueError:
                    sc = 0.0
                try:
                    run = int(r.get("max_exact_run_len", "0") or 0)
                except ValueError:
                    run = 0
                key = (sb, tb)
                c = cells.setdefault(key, {
                    "source_book": sb,
                    "target_book": tb,
                    "n_candidates": 0,
                    "n_score_ge_035": 0,
                    "n_exact_4plus": 0,
                    "max_score": 0.0,
                    "best": None,
                })
                c["n_candidates"] += 1
                if sc >= 0.35:
                    c["n_score_ge_035"] += 1
                if run >= 4:
                    c["n_exact_4plus"] += 1
                if sc > c["max_score"]:
                    c["max_score"] = sc
                    c["best"] = {
                        "source_ref": r.get("source_ref", ""),
                        "target_ref": r.get("target_ref", ""),
                        "score": sc,
                        "max_exact_run_len": run,
                        "max_exact_run": r.get("max_exact_run", ""),
                    }

    _agg(JTEA_ROOT / "data" / "04_epistles_to_gospels_candidates.csv")
    _agg(JTEA_ROOT / "data" / "05_john_to_synoptics_candidates.csv")

    out = list(cells.values())
    out.sort(key=lambda c: (_book_order(c["source_book"]), _book_order(c["target_book"])))
    return out


def load_jtea_canonical_book_counts():
    """From 02_canonical_units.csv emit per-book verse counts + chapter layout."""
    book_chaps: dict[str, dict[int, int]] = {}
    for r in _csv_rows(JTEA_ROOT / "data" / "02_canonical_units.csv"):
        book = r.get("book", "")
        try:
            chap = int(r.get("chapter", "0") or 0)
            verse = int(r.get("verse", "0") or 0)
        except ValueError:
            continue
        book_chaps.setdefault(book, {})
        book_chaps[book][chap] = max(book_chaps[book].get(chap, 0), verse)
    books = []
    for bk in sorted(book_chaps, key=_book_order):
        total = sum(book_chaps[bk].values())
        books.append({
            "book": bk,
            "order": _book_order(bk),
            "chapter_count": len(book_chaps[bk]),
            "verse_count": total,
        })
    return books


def build_jtea():
    return {
        "name": "jtea",
        "label": "John · Thomas · Epistles · Apocrypha",
        "summary": load_jtea_summary(),
        "method": load_jtea_method(),
        "case_studies": load_jtea_case_studies(),
        "anchors": load_jtea_anchors(),
        "thomas_registry": load_jtea_thomas_registry(),
        "thomas_units": load_jtea_thomas_units(),
        "concepts": load_jtea_concepts(),
        "burden_ledger": load_jtea_burden_ledger(),
        "exact_hits": load_jtea_exact_hits(),
        "network_edges": load_jtea_network_edges(),
        "negspace_flags": load_jtea_negspace_flags(),
        "book_matrix": load_jtea_book_matrix(),
        "books": load_jtea_canonical_book_counts(),
        "apocrypha": load_jtea_apocrypha(),
    }


def main():
    print("Building mm (Mark–Matthew)...")
    mm = build_mm()
    print(f"  {len(mm['pairs'])} pairs, {len(mm['macro'])} macro blocks, {len(mm['echoes'])} echoes")

    print("Building ml (Matthew–Luke)...")
    ml = build_ml()
    print(f"  {len(ml['pairs'])} pairs, {len(ml['macro'])} macro blocks, {len(ml['echoes'])} echoes")

    print("Building mld (Matt–Luke, Markan-masked)...")
    mld = build_mld()
    print(f"  {len(mld['pairs'])} pairs, {len(mld['macro'])} macro blocks, "
          f"{len(mld['echoes'])} echoes, {len(mld['mask_audit'])} mask rows")

    print("Building jtea (John · Thomas · Epistles · Apocrypha)...")
    jtea = build_jtea()
    print(f"  {len(jtea['case_studies'])} case studies, {len(jtea['anchors'])} anchors, "
          f"{len(jtea['thomas_registry'])} thomas parallels, {len(jtea['concepts'])} concepts, "
          f"{len(jtea['network_edges'])} network edges, {len(jtea['exact_hits'])} exact hits, "
          f"{len(jtea['book_matrix'])} matrix cells")

    bundle = {"mm": mm, "ml": ml, "mld": mld, "jtea": jtea}

    # Write JS bundle (usable via file://)
    jsfile = OUT / "bundle.js"
    with open(jsfile, "w") as f:
        f.write("window.SYNOPSIS = ")
        json.dump(bundle, f, separators=(",", ":"), ensure_ascii=False)
        f.write(";\n")
    print(f"Wrote {jsfile} ({jsfile.stat().st_size:,} bytes)")

    # Also write a plain JSON bundle
    jsonfile = OUT / "bundle.json"
    with open(jsonfile, "w") as f:
        json.dump(bundle, f, separators=(",", ":"), ensure_ascii=False)
    print(f"Wrote {jsonfile} ({jsonfile.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
