#!/usr/bin/env python3
"""
Build the Synoptic Problem + John Model-Comparison Atlas from included input snapshots.

Run from the package root:
    python scripts/build_synoptic_model_atlas.py

Dependencies: pandas, pyyaml, numpy. No internet required.
This script rebuilds the core derived CSV/YAML atlas layers from files under inputs/.
"""
from __future__ import annotations

import gzip, hashlib, json, re, shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INPUTS = ROOT / "inputs"
DATA.mkdir(exist_ok=True)

def load_index() -> dict[str, Path]:
    idx = yaml.safe_load(open(INPUTS / "INPUT_INDEX.yaml", encoding="utf-8"))
    return {k: ROOT / v for k, v in idx.items()}

IDX = load_index()

def yload(key: str):
    return yaml.safe_load(open(IDX[key], encoding="utf-8"))

def csvload(key: str, **kw):
    return pd.read_csv(IDX[key], **kw)

def pair_to_id(pair: str) -> str:
    return {
        "Mark↔Matthew": "Mark_Matthew",
        "Mark↔Luke": "Mark_Luke",
        "Matthew↔Luke": "Matthew_Luke",
        "John↔Mark": "John_Mark",
        "John↔Matt": "John_Matthew",
        "John↔Luke": "John_Luke",
        "John↔Synoptics": "John_Synoptics",
    }.get(pair, pair.replace("↔", "_").replace(" ", "_"))

def tok_list(s) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [t for t in s.split() if t and t != "nan"]

def longest_common_contiguous(a: list[str], b: list[str]) -> tuple[int, list[str]]:
    best_len, best_seq = 0, []
    prev = [0] * (len(b) + 1)
    for i, ta in enumerate(a, 1):
        curr = [0] * (len(b) + 1)
        for j, tb in enumerate(b, 1):
            if ta == tb:
                curr[j] = prev[j - 1] + 1
                if curr[j] > best_len:
                    best_len = curr[j]
                    best_seq = a[i - best_len : i]
        prev = curr
    return best_len, best_seq

MODEL_REGISTRY = [
    {
        "model_id": "markan_priority_matthew_and_luke",
        "short_label": "Markan priority for Matthew and Luke",
        "family": "direct-literary",
        "core_claim": "Matthew and Luke each used Mark or a Mark-like written narrative source.",
        "required_direction_hypotheses": ["matthew_used_mark", "luke_used_mark"],
        "optional_or_competing_components": ["shared_matt_luke_sayings_tradition", "luke_used_matthew", "matthew_used_luke"],
        "status_from_current_atlas": "strong for Matthew used Mark; medium-high for Luke used Mark over Mark used Luke, with shared-tradition penalty required",
    },
    {
        "model_id": "two_source_mark_q",
        "short_label": "Two-source / Mark + Q-like sayings source",
        "family": "source-critical",
        "core_claim": "Matthew and Luke used Mark independently and also drew on a shared non-Markan sayings source/tradition.",
        "required_direction_hypotheses": ["matthew_used_mark", "luke_used_mark", "shared_matt_luke_sayings_tradition"],
        "optional_or_competing_components": ["proto_mark_common_source"],
        "status_from_current_atlas": "strong model fit for broad structure, but minor agreements and Q-document reconstruction remain burdens",
    },
    {
        "model_id": "farrer_mark_matthew_luke",
        "short_label": "Farrer / Mark + Matthew → Luke",
        "family": "direct-literary",
        "core_claim": "Matthew used Mark; Luke used Mark and Matthew; Q is unnecessary.",
        "required_direction_hypotheses": ["matthew_used_mark", "luke_used_mark", "luke_used_matthew"],
        "optional_or_competing_components": ["shared_matt_luke_sayings_tradition"],
        "status_from_current_atlas": "viable major alternative; must explain Lukan redistribution and omission of Matthean discourse/framing",
    },
    {
        "model_id": "matthew_used_luke_plus_mark_like",
        "short_label": "Matthew used Luke plus Mark-like material",
        "family": "direct-literary",
        "core_claim": "Matthew used Luke and Mark-like material, collecting/discourse-arranging Lukan sayings.",
        "required_direction_hypotheses": ["matthew_used_luke", "matthew_used_mark"],
        "optional_or_competing_components": ["luke_used_mark", "shared_matt_luke_sayings_tradition"],
        "status_from_current_atlas": "possible locally, system-level burden high",
    },
    {
        "model_id": "griesbach_two_gospel",
        "short_label": "Griesbach / Two-Gospel model",
        "family": "direct-literary",
        "core_claim": "Matthew was first, Luke used Matthew, and Mark used both Matthew and Luke.",
        "required_direction_hypotheses": ["luke_used_matthew", "mark_used_matthew", "mark_used_luke"],
        "optional_or_competing_components": [],
        "status_from_current_atlas": "possible but high-burden due to Markan omission/compression and roughening obligations",
    },
    {
        "model_id": "augustinian_matthew_mark_luke",
        "short_label": "Augustinian sequence Matthew → Mark → Luke",
        "family": "direct-literary",
        "core_claim": "Matthew wrote first; Mark used Matthew; Luke used Mark and perhaps Matthew.",
        "required_direction_hypotheses": ["mark_used_matthew", "luke_used_mark"],
        "optional_or_competing_components": ["luke_used_matthew"],
        "status_from_current_atlas": "high-burden because Mark used Matthew is weaker than Matthew used Mark",
    },
    {
        "model_id": "proto_mark_plus_sayings",
        "short_label": "Proto-Mark/common narrative source + sayings tradition",
        "family": "lost-source/network",
        "core_claim": "Narrative agreements derive from a Mark-like common source plus a shared sayings layer.",
        "required_direction_hypotheses": ["proto_mark_common_source", "shared_matt_luke_sayings_tradition"],
        "optional_or_competing_components": ["matthew_used_mark", "luke_used_mark"],
        "status_from_current_atlas": "plausible hedge against canonical-form uncertainty; pays lost-source burden",
    },
    {
        "model_id": "oral_tradition_network",
        "short_label": "Stable oral/traditional network",
        "family": "non-direct/shared-tradition",
        "core_claim": "Similarities reflect stable oral/traditional narrative and sayings networks more than direct copying.",
        "required_direction_hypotheses": [
            "shared_mark_luke_tradition",
            "shared_matt_luke_sayings_tradition",
            "shared_john_mark_anchor_tradition",
            "shared_john_luke_anchor_tradition",
            "shared_john_matthew_anchor_tradition",
        ],
        "optional_or_competing_components": ["matthew_used_mark", "luke_used_mark"],
        "status_from_current_atlas": "good for sayings and John anchors; weak unless order-retention penalties are paid for Synoptic narrative",
    },
    {"model_id": "john_uses_mark", "short_label": "John used Mark", "family": "john-synoptic-direct", "core_claim": "John knew Mark or Mark-like written material.", "required_direction_hypotheses": ["john_used_mark"], "optional_or_competing_components": ["shared_john_mark_anchor_tradition"], "status_from_current_atlas": "possible locally; shared anchor tradition lower globally"},
    {"model_id": "john_uses_matthew", "short_label": "John used Matthew", "family": "john-synoptic-direct", "core_claim": "John knew Matthew or Matthean tradition.", "required_direction_hypotheses": ["john_used_matthew"], "optional_or_competing_components": ["shared_john_matthew_anchor_tradition"], "status_from_current_atlas": "weak as global direct-use model"},
    {"model_id": "john_uses_luke", "short_label": "John used Luke", "family": "john-synoptic-direct", "core_claim": "John knew Luke or Lukan tradition.", "required_direction_hypotheses": ["john_used_luke"], "optional_or_competing_components": ["shared_john_luke_anchor_tradition"], "status_from_current_atlas": "possible locally; shared anchor tradition lower globally"},
    {"model_id": "synoptics_use_john_or_johnlike", "short_label": "Synoptics used John / John-like tradition", "family": "john-reverse-or-prejohannine", "core_claim": "Synoptics drew on John or pre-Johannine traditions.", "required_direction_hypotheses": ["mark_used_john", "matthew_used_john", "luke_used_john"], "optional_or_competing_components": ["shared_john_mark_anchor_tradition", "shared_john_luke_anchor_tradition", "shared_john_matthew_anchor_tradition"], "status_from_current_atlas": "high-burden if canonical John is source"},
    {"model_id": "shared_john_synoptic_anchor_tradition", "short_label": "Shared John/Synoptic anchor tradition", "family": "non-direct/shared-tradition", "core_claim": "John and Synoptics share passion/sign/Baptist anchor traditions without global direct copying.", "required_direction_hypotheses": ["shared_john_mark_anchor_tradition", "shared_john_luke_anchor_tradition", "shared_john_matthew_anchor_tradition"], "optional_or_competing_components": ["john_used_mark", "john_used_luke", "john_used_matthew"], "status_from_current_atlas": "currently lowest burden for John-pair comparisons"},
]

def direction_to_models() -> dict[str, list[str]]:
    dmap = defaultdict(list)
    for m in MODEL_REGISTRY:
        for d in m["required_direction_hypotheses"]:
            dmap[d].append(m["model_id"])
        for d in m.get("optional_or_competing_components", []):
            dmap[d].append(m["model_id"] + ":optional")
    return dmap

def build_inventory():
    canonical = csvload("canonical_units")
    gospels = canonical[canonical.book.isin(["Matt", "Mark", "Luke", "John"])].copy()
    book_order = {"Matt": 1, "Mark": 2, "Luke": 3, "John": 4}
    gospels["book_order"] = gospels["book"].map(book_order)
    gospels["verse_index_in_book"] = gospels.groupby("book").cumcount() + 1
    gospels.to_csv(DATA / "01_gospel_verse_inventory.csv", index=False)
    return gospels

def build_registries():
    yaml.safe_dump(MODEL_REGISTRY, open(DATA / "02_system_model_registry.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)
    direction_registry = yload("direction_registry")
    if isinstance(direction_registry, dict):
        rows = []
        for k, v in direction_registry.items():
            if isinstance(v, dict):
                vv = dict(v)
                vv.setdefault("direction_id", k)
                rows.append(vv)
            else:
                rows.append({"direction_id": k, "description": v})
    else:
        rows = direction_registry
    existing = {r.get("direction_id") for r in rows}
    for extra in [
        {"direction_id": "proto_mark_common_source", "direction_type": "common_written_source", "description": "A Mark-like narrative source not identical to canonical Mark."},
        {"direction_id": "shared_matt_luke_sayings_tradition", "direction_type": "common_source_or_oral", "description": "Non-Markan shared sayings/tradition."},
        {"direction_id": "shared_john_synoptic_anchor_tradition", "direction_type": "shared_anchor_tradition", "description": "Shared John/Synoptic anchors."},
    ]:
        if extra["direction_id"] not in existing:
            rows.append(extra)
    yaml.safe_dump(rows, open(DATA / "03_direction_hypothesis_registry.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)

def build_pericope_ontology(per_ledger, john_pair_anchor):
    unique = []
    for (pair, block_id), grp in per_ledger.groupby(["pair", "block_id"], dropna=False):
        row = grp.iloc[0].to_dict()
        ranges = {}
        for b, col in [("Mark", "mark_range"), ("Matthew", "matt_range"), ("Luke", "luke_range")]:
            val = row.get(col)
            if pd.notna(val):
                ranges[b] = val
        unique.append({
            "pericope_id": f"{pair_to_id(pair)}_block_{block_id}",
            "unit_type": "computational_synoptic_block",
            "pair": pair,
            "block_id": block_id,
            "block_label": row.get("block_label"),
            "matthew_range": ranges.get("Matthew", ""),
            "mark_range": ranges.get("Mark", ""),
            "luke_range": ranges.get("Luke", ""),
            "john_range": "",
            "pair_count": row.get("pair_count"),
            "avg_score": row.get("avg_score"),
            "evidence_origin": "primary_chain_block_from_prior_packages",
            "methodological_status": "computed alignment block; not a traditional hand-curated pericope title",
            "representative_primary_pairs": row.get("representative_primary_pairs"),
        })
    anchors_by_id = defaultdict(list)
    for a in john_pair_anchor:
        anchors_by_id[a["anchor_id"]].append(a)
    for aid, entries in anchors_by_id.items():
        ranges = {"John": entries[0].get("john_refs", "")}
        for e in entries:
            if "Mark" in e["pair"]:
                ranges["Mark"] = e.get("synoptic_refs", "")
            elif "Matt" in e["pair"]:
                ranges["Matthew"] = e.get("synoptic_refs", "")
            elif "Luke" in e["pair"]:
                ranges["Luke"] = e.get("synoptic_refs", "")
        unique.append({
            "pericope_id": f"john_anchor_{aid}",
            "unit_type": "john_synoptic_anchor",
            "pair": "John↔Synoptics",
            "block_id": aid,
            "block_label": aid.replace("_", " "),
            "matthew_range": ranges.get("Matthew", ""),
            "mark_range": ranges.get("Mark", ""),
            "luke_range": ranges.get("Luke", ""),
            "john_range": ranges.get("John", ""),
            "pair_count": len(entries),
            "avg_score": float(np.mean([e.get("metrics_from_verse_matrix", {}).get("max_score", 0) for e in entries])),
            "evidence_origin": "curated John/Synoptic anchor registry plus pairwise lexical metrics",
            "methodological_status": "anchor-level; not monotonic chain",
            "shared_features": "; ".join(entries[0].get("shared_features", [])),
        })
    df = pd.DataFrame(unique)
    df.to_csv(DATA / "10_pericope_ontology_computational_and_anchor.csv", index=False)
    return df

def build_model_obligations(model_req, john_anchor_dir, pericope_df):
    dmap = direction_to_models()
    rows = []
    for _, r in model_req.iterrows():
        for mid in dmap.get(r.direction_id, []):
            rows.append({
                "model_id": mid, "direction_id": r.direction_id, "pair": r.pair,
                "unit_id": f"{pair_to_id(r.pair)}_block_{r.block_id}",
                "source_range": r.source_range, "target_range": r.target_range,
                "obligation_type": "pericope_direction_requirement",
                "required_explanation": r.required_explanation,
                "contrary_evidence": r.contrary_evidence,
                "response_model": r.response_model,
                "basis": "directional_model_requirements_by_pericope",
            })
    for _, r in john_anchor_dir.iterrows():
        for mid in dmap.get(r.direction_id, []):
            rows.append({
                "model_id": mid, "direction_id": r.direction_id, "pair": r.pair,
                "unit_id": f"john_anchor_{r.anchor_id}",
                "source_range": r.source_refs, "target_range": r.target_refs,
                "obligation_type": "john_anchor_direction_requirement",
                "required_explanation": r.required_explanation_if_direction,
                "contrary_evidence": r.contrary_evidence,
                "response_model": r.plausible_response_model,
                "basis": "john_synoptic_directional_anchor_ledger",
            })
    out = pd.DataFrame(rows)
    out.to_csv(DATA / "20_model_pericope_obligation_ledger.csv", index=False)
    out.groupby(["unit_id", "pair"]).agg(
        obligation_rows=("unit_id", "size"),
        direction_count=("direction_id", "nunique"),
        model_count=("model_id", "nunique"),
    ).reset_index().to_csv(DATA / "12_pericope_obligation_summary.csv", index=False)
    # YAML dossiers
    dossiers = []
    for unit_id, grp in out.groupby("unit_id"):
        ont = pericope_df[pericope_df.pericope_id == unit_id]
        obligations = grp.to_dict("records")
        dossiers.append({"unit_id": unit_id, "ontology": {} if ont.empty else ont.iloc[0].dropna().to_dict(), "obligation_count": len(obligations), "obligations": obligations})
    yaml.safe_dump(dossiers, open(DATA / "11_pericope_model_dossiers.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)
    return out

def build_minor_agreements(gospels):
    mm_primary = csvload("mark_matthew_primary")
    mlk_primary = csvload("mark_luke_primary")
    ref_tokens = {r.ref: tok_list(r.content_tokens) for _, r in gospels.iterrows()}
    ref_texts = {r.ref: r.text for _, r in gospels.iterrows()}
    mm_map, mlk_map = defaultdict(list), defaultdict(list)
    for _, r in mm_primary.iterrows():
        mm_map[r.mark_ref].append(r.matt_ref)
    for _, r in mlk_primary.iterrows():
        if r.source_book == "Mark" and r.target_book == "Luke":
            mlk_map[r.source_ref].append(r.target_ref)
    rows = []
    for mark_ref in sorted(set(mm_map) & set(mlk_map)):
        for matt_ref in mm_map[mark_ref]:
            for luke_ref in mlk_map[mark_ref]:
                mt, mk, lk = ref_tokens.get(matt_ref, []), ref_tokens.get(mark_ref, []), ref_tokens.get(luke_ref, [])
                if not (mt and mk and lk):
                    continue
                agreement_absent = sorted((set(mt) & set(lk)) - set(mk))
                mark_omitted = sorted(set(mk) - set(mt) - set(lk))
                exact_len, exact_seq = longest_common_contiguous(mt, lk)
                strength = len(agreement_absent) * 2 + len(mark_omitted) + exact_len
                if strength:
                    rows.append({
                        "minor_agreement_id": f"ma_{len(rows)+1:04d}",
                        "mark_ref": mark_ref, "matt_ref": matt_ref, "luke_ref": luke_ref,
                        "agreement_absent_from_mark_count": len(agreement_absent),
                        "agreement_absent_from_mark_tokens": ";".join(agreement_absent),
                        "mark_omitted_by_both_count": len(mark_omitted),
                        "mark_omitted_by_both_tokens": ";".join(mark_omitted),
                        "matt_luke_longest_exact_content_run_len": exact_len,
                        "matt_luke_longest_exact_content_run": " ".join(exact_seq),
                        "minor_agreement_strength": strength,
                        "agreement_type": "lexical_addition_against_mark" if agreement_absent else "shared_omission_against_mark",
                        "possible_implications": "pressure on strict independent-use-of-Mark models; possible direct contact/common source/tradition/harmonization",
                        "formula_or_commonality_risk": "unknown_unfiltered",
                        "matt_text": ref_texts.get(matt_ref, ""), "mark_text": ref_texts.get(mark_ref, ""), "luke_text": ref_texts.get(luke_ref, ""),
                    })
    df = pd.DataFrame(rows).sort_values("minor_agreement_strength", ascending=False)
    df.to_csv(DATA / "30_minor_agreements_catalog_triple_tradition.csv", index=False)
    yaml.safe_dump({
        "definition": "Algorithmic verse-level triple-tradition minor-agreement screen.",
        "rows": int(len(df)),
        "high_strength_ge_10": int((df.minor_agreement_strength >= 10).sum()) if len(df) else 0,
        "status": "screening catalog, not hand-curated standard list",
        "model_implication": "model-discriminating for Q/Farrer/Griesbach/common-source/harmonization discussions",
    }, open(DATA / "31_minor_agreements_summary.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)

def build_double_tradition():
    details = [json.loads(line) for line in open(IDX["mld_primary_detailed"], encoding="utf-8") if line.strip()]
    sec = yload("mld_secondary")
    rows = []
    for d in details:
        rows.append({
            "double_tradition_id": f"dt_primary_{int(d['pair_id']):03d}",
            "alignment_layer": "primary_monotonic_after_markan_mask",
            "matt_ref": d["matt_ref"], "luke_ref": d["luke_ref"],
            "matt_index": d["matt_original_idx"], "luke_index": d["luke_original_idx"],
            "score": d["score"], "lcs": d.get("lcs"),
            "tags": ";".join(d.get("tags", [])),
            "order_signal": "order_preserved_in_primary_chain",
            "matt_text": d.get("matt_text", ""), "luke_text": d.get("luke_text", ""),
            "shared_lemma_count": len(set(d.get("matt_lemmas", [])) & set(d.get("luke_lemmas", []))),
            "model_implication": "Part of monotonic masked chain; not by itself directional.",
            "main_counter_to_direct_use": "Direct-use models must explain displaced/secondary double-tradition material.",
        })
    for i, s in enumerate(sec, 1):
        rows.append({
            "double_tradition_id": f"dt_secondary_{i:03d}",
            "alignment_layer": "secondary_echo_after_markan_mask",
            "matt_ref": s["matt_ref"], "luke_ref": s["luke_ref"],
            "matt_index": s.get("matt_original_idx"), "luke_index": s.get("luke_original_idx"),
            "score": s.get("score"), "lcs": s.get("lcs"),
            "tags": ";".join(s.get("tags", [])),
            "order_signal": "nonlocal_or_displaced_echo" if "nonlocal_reorder" in s.get("tags", []) else "secondary_echo",
            "matt_text": s.get("matt_text", ""), "luke_text": s.get("luke_text", ""),
            "shared_lemma_count": s.get("shared_content_lemmas"),
            "model_implication": "Strong displaced sayings echo; supports real shared tradition but weakens simple linear copying unless redistribution theory is supplied.",
            "main_counter_to_direct_use": "Direct-use models need plausible relocation/clustering/redistribution explanation.",
        })
    df = pd.DataFrame(rows).sort_values(["matt_index", "luke_index"]).reset_index(drop=True)
    df["matt_rank"] = df["matt_index"].rank(method="dense").astype(int)
    df["luke_rank_by_matt_order"] = df["luke_index"].rank(method="first").astype(int)
    df["rank_distance_abs"] = (df["matt_rank"] - df["luke_rank_by_matt_order"]).abs()
    df["nonlocal_flag"] = df.alignment_layer.str.contains("secondary") | df.tags.str.contains("nonlocal", na=False)
    df.to_csv(DATA / "40_double_tradition_order_catalog_markan_masked.csv", index=False)
    yaml.safe_dump({
        "definition": "Markan-masked Matthew-Luke double-tradition primary chain plus secondary echoes.",
        "primary_rows": int((df.alignment_layer == "primary_monotonic_after_markan_mask").sum()),
        "secondary_rows": int((df.alignment_layer == "secondary_echo_after_markan_mask").sum()),
        "nonlocal_rows": int(df.nonlocal_flag.sum()),
        "model_implication": "Stable shared sayings layer; one-way direct models require redistribution/extraction explanation.",
    }, open(DATA / "41_double_tradition_order_summary.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)


def build_gospel_direction_matrix(direction_burden, support_contra):
    books = ["Matthew", "Mark", "Luke", "John"]
    direction_map = {
        ("Mark", "Matthew"): "matthew_used_mark",
        ("Matthew", "Mark"): "mark_used_matthew",
        ("Mark", "Luke"): "luke_used_mark",
        ("Luke", "Mark"): "mark_used_luke",
        ("Luke", "Matthew"): "matthew_used_luke",
        ("Matthew", "Luke"): "luke_used_matthew",
        ("Mark", "John"): "john_used_mark",
        ("Matthew", "John"): "john_used_matthew",
        ("Luke", "John"): "john_used_luke",
        ("John", "Mark"): "mark_used_john",
        ("John", "Matthew"): "matthew_used_john",
        ("John", "Luke"): "luke_used_john",
    }
    rows = []
    for source in books:
        for target in books:
            if source == target:
                rows.append({"source": source, "target": target, "direction_id": "self", "status": "not_applicable", "method_class": "self"})
                continue
            did = direction_map.get((source, target), "")
            db = direction_burden[direction_burden.direction_id == did] if did else pd.DataFrame()
            sc = support_contra[support_contra.direction_id == did] if did else pd.DataFrame()
            rows.append({
                "source": source,
                "target": target,
                "direction_id": did,
                "status": sc.current_status.iloc[0] if len(sc) else ("covered_by_anchor_or_model_level" if did else "not_scored"),
                "best_response_model": sc.best_response_model.iloc[0] if len(sc) else "",
                "available_burden_scores": "; ".join([f"{r.burden_model}:{r.burden_score}" for _, r in db.iterrows()]) if len(db) else "",
                "primary_data_files": "data/20_model_pericope_obligation_ledger.csv;data/50_direction_burden_reference.csv;data/80_direction_support_contra_cards.yaml" if did else "",
                "method_class": "synoptic_chain_or_block" if source != "John" and target != "John" else "john_anchor_low_verbatim",
            })
    df = pd.DataFrame(rows)
    df.to_csv(DATA / "04_gospel_direction_matrix_4x4.csv", index=False)
    nested = {s: {} for s in books}
    for _, r in df.iterrows():
        nested[r.source][r.target] = r.dropna().to_dict()
    yaml.safe_dump(nested, open(DATA / "04_gospel_direction_matrix_4x4.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)

def rating_from_model_id(model_id: str) -> str:
    return {
        "markan_priority_matthew_and_luke": "strong_with_mark_luke_caution",
        "two_source_mark_q": "strong_but_Q_document_and_minor_agreement_burdens",
        "farrer_mark_matthew_luke": "viable_major_alternative",
        "matthew_used_luke_plus_mark_like": "possible_but_high_burden",
        "griesbach_two_gospel": "possible_but_high_burden",
        "augustinian_matthew_mark_luke": "high_burden_due_mark_from_matthew",
        "proto_mark_plus_sayings": "plausible_lost_source_hybrid",
        "oral_tradition_network": "good_for_sayings_john_weak_for_ordered_synoptic_narrative",
        "john_uses_mark": "local_possible_global_not_favored",
        "john_uses_matthew": "weak_global_direct_model",
        "john_uses_luke": "local_possible_global_not_favored",
        "synoptics_use_john_or_johnlike": "high_burden_if_canonical_john_source",
        "shared_john_synoptic_anchor_tradition": "best_current_john_global_model",
    }.get(model_id, "unrated")

def build_model_scorecard(direction_burden):
    rows, cards = [], []
    for m in MODEL_REGISTRY:
        details, burden_scores = [], []
        for d in m["required_direction_hypotheses"]:
            matches = direction_burden[direction_burden.direction_id == d]
            if matches.empty:
                details.append(f"{d}=unscored/model-level")
            else:
                if d in ["luke_used_matthew", "matthew_used_luke"]:
                    masked = matches[matches.burden_model.astype(str).str.contains("masked")]
                    chosen = masked.iloc[0] if len(masked) else matches.iloc[matches.burden_score.astype(float).argmin()]
                else:
                    chosen = matches.iloc[matches.burden_score.astype(float).argmin()]
                burden_scores.append(float(chosen.burden_score))
                details.append(f"{d}={chosen.burden_score} ({chosen.burden_model})")
        mid = m["model_id"]
        criteria = {
            "mark_matthew_fit": "not_applicable",
            "mark_luke_fit": "not_applicable",
            "matt_luke_double_tradition_fit": "not_applicable",
            "minor_agreements_fit": "not_applicable",
            "john_anchor_fit": "not_applicable",
            "main_strength": "",
            "main_burden": "",
        }
        if mid in ["markan_priority_matthew_and_luke", "two_source_mark_q", "farrer_mark_matthew_luke", "proto_mark_plus_sayings"]:
            criteria["mark_matthew_fit"] = "strong"
            criteria["mark_luke_fit"] = "medium_high"
        if mid == "two_source_mark_q":
            criteria["matt_luke_double_tradition_fit"] = "strong_for_shared_sayings_low_burden"
            criteria["minor_agreements_fit"] = "burden_needs_catalog_evaluation"
            criteria["main_strength"] = "explains Markan backbone plus non-Markan sayings layer"
            criteria["main_burden"] = "Q/source reconstruction and minor agreements"
        elif mid == "farrer_mark_matthew_luke":
            criteria["matt_luke_double_tradition_fit"] = "viable_if_Lukan_redistribution_model_supplied"
            criteria["minor_agreements_fit"] = "stronger_than_strict_independent_two_source"
            criteria["main_strength"] = "avoids Q document and explains minor agreements via Luke-Matthew contact"
            criteria["main_burden"] = "must explain Lukan de-Mattheanization/dispersal of sayings"
        elif mid == "griesbach_two_gospel":
            criteria["mark_matthew_fit"] = "weak_to_medium_high_burden"
            criteria["mark_luke_fit"] = "medium_or_component_dependent"
            criteria["minor_agreements_fit"] = "strong"
            criteria["main_strength"] = "direct Matthew-Luke contact explains agreements against Mark"
            criteria["main_burden"] = "Markan omission/compression of major Matthean/Lukan material"
        elif mid == "markan_priority_matthew_and_luke":
            criteria["matt_luke_double_tradition_fit"] = "does_not_decide_Q_or_Farrer"
            criteria["minor_agreements_fit"] = "unresolved_burden"
            criteria["main_strength"] = "Mark-like narrative source explains most Mark-Matthew/Mark-Luke core"
            criteria["main_burden"] = "does not solve double tradition"
        elif mid == "proto_mark_plus_sayings":
            criteria["matt_luke_double_tradition_fit"] = "medium_high"
            criteria["minor_agreements_fit"] = "can_absorb_with_lost_source_but_pays_lost_source_cost"
            criteria["main_strength"] = "accounts for canonical-form uncertainty and Mark-like core"
            criteria["main_burden"] = "lost source reconstruction burden"
        elif mid == "oral_tradition_network":
            criteria["mark_matthew_fit"] = "medium_requires_order_retention"
            criteria["mark_luke_fit"] = "medium_requires_order_retention"
            criteria["matt_luke_double_tradition_fit"] = "high_for_sayings"
            criteria["minor_agreements_fit"] = "medium"
            criteria["main_strength"] = "explains mobile sayings and John anchors"
            criteria["main_burden"] = "dense order and exact wording in Synoptic narrative cores"
        elif mid.startswith("john_uses"):
            criteria["john_anchor_fit"] = "possible_local_not_lowest_global_burden"
            criteria["main_strength"] = "accounts for selected John/Synoptic anchor overlaps as direct transformation"
            criteria["main_burden"] = "weak continuous order and high Johannine transformation"
        elif mid == "shared_john_synoptic_anchor_tradition":
            criteria["john_anchor_fit"] = "strong_lowest_current_burden"
            criteria["main_strength"] = "explains anchors without forcing monotonic chain"
            criteria["main_burden"] = "local exact/specific clusters may still require case-level direct-dependence explanations"
        elif mid == "synoptics_use_john_or_johnlike":
            criteria["john_anchor_fit"] = "high_burden_for_canonical_John_as_source"
            criteria["main_strength"] = "keeps possibility of pre-Johannine shared traditions"
            criteria["main_burden"] = "de-Johannization/compression burden"
        elif mid == "matthew_used_luke_plus_mark_like":
            criteria["matt_luke_double_tradition_fit"] = "possible_if_Matthean_clustering_model_supplied"
            criteria["main_strength"] = "explains Matthew as organizer/collector"
            criteria["main_burden"] = "less economical system-level pattern and Matthew-Mark relationship"
        elif mid == "augustinian_matthew_mark_luke":
            criteria["mark_matthew_fit"] = "weak_to_medium_high_burden"
            criteria["main_strength"] = "simple canonical order tradition"
            criteria["main_burden"] = "Mark-from-Matthew burden"
        row = {
            "model_id": mid,
            "short_label": m["short_label"],
            "family": m["family"],
            "required_direction_hypotheses": ";".join(m["required_direction_hypotheses"]),
            "required_direction_burdens_selected": "; ".join(details),
            "sum_selected_burden_scores_available": sum(burden_scores) if burden_scores else np.nan,
            "current_atlas_rating": rating_from_model_id(mid),
            **criteria,
        }
        rows.append(row)
        cards.append({
            "model_id": mid,
            "short_label": m["short_label"],
            "rating": row["current_atlas_rating"],
            "required_directions": m["required_direction_hypotheses"],
            "selected_burden_scores": row["required_direction_burdens_selected"],
            "strongest_support": row["main_strength"],
            "strongest_contra_or_unresolved_burden": row["main_burden"],
            "criteria": {k: row[k] for k in ["mark_matthew_fit", "mark_luke_fit", "matt_luke_double_tradition_fit", "minor_agreements_fit", "john_anchor_fit"]},
            "reader_note": "Interpretive synthesis, not a posterior probability.",
        })
    pd.DataFrame(rows).to_csv(DATA / "52_system_model_comparison_scorecard.csv", index=False)
    yaml.safe_dump(cards, open(DATA / "53_system_model_evidence_cards.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)

def build_variant_registry(gospels):
    rows = []
    for _, r in gospels.iterrows():
        if int(r.get("variant_marker_count", 0)) > 0:
            rows.append({
                "variant_case_id": f"verse_variant_{r.ref.replace(' ', '_').replace(':', '_')}",
                "layer": "verse_inventory",
                "pair_or_context": "all_gospels",
                "ref": r.ref,
                "related_ref": "",
                "variant_marker_count": int(r.variant_marker_count),
                "variant_note_count": np.nan,
                "status": "variant_marker_present_in_SBLGNT_text",
                "potential_effect": "may affect lexical similarity or exact-run scoring if inside a compared phrase",
                "conclusion_stability": "not_assessed_case_by_case",
            })
    for key, pair_context in [("mark_matthew_variants", "Mark↔Matthew"), ("mld_variants", "Matthew↔Luke masked")]:
        data = yload(key)
        for i, item in enumerate(data, 1):
            notes = []
            for k, v in item.items():
                if k.endswith("_variant_notes") and isinstance(v, list):
                    for note in v:
                        notes.append(f"{k}:{note}")
            if notes:
                refs = [item[k] for k in ["mark_ref", "matt_ref", "luke_ref"] if k in item]
                rows.append({
                    "variant_case_id": f"{pair_context.replace('↔', '_').replace(' ', '_')}_pair_{i:04d}",
                    "layer": "primary_pair_variant_note",
                    "pair_or_context": pair_context,
                    "ref": refs[0] if refs else "",
                    "related_ref": "/".join(refs[1:]),
                    "variant_marker_count": np.nan,
                    "variant_note_count": len(notes),
                    "status": "apparatus notes attached to aligned pair",
                    "potential_effect": "could affect local lexical overlap or exact-run length if variant reading is adopted",
                    "conclusion_stability": "requires manual/text-critical sensitivity for high-value cases",
                    "variant_notes": " | ".join(notes),
                })
    rows.append({
        "variant_case_id": "mark_16_9_20_ending_sensitivity",
        "layer": "text_critical_sensitivity",
        "pair_or_context": "Mark↔Luke / Mark↔Matthew system context",
        "ref": "Mark 16:9-20",
        "status": "default exclusion from primary chain noted in prior packages",
        "potential_effect": "longer ending can create secondary parallels and should not be treated as ordinary Markan source material by default",
        "conclusion_stability": "core Synoptic conclusions not dependent on including Mark 16:9-20 in current default runs",
    })
    pd.DataFrame(rows).to_csv(DATA / "70_variant_sensitivity_registry.csv", index=False)
    yaml.safe_dump({
        "default_policy": "Use SBLGNT surface text with explicit markers; exclude empty/double-bracketed secondary ending material from primary-chain defaults where prior package did so.",
        "high_value_cases_require": "Inspect variant notes before using an exact phrase or local run as decisive evidence.",
        "limitation": "Not a substitute for full apparatus adjudication.",
    }, open(DATA / "71_text_critical_policy.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)

def build_redactional_profiles(model_req, material_dir, pairdiff, john_anchor_flat):
    profiles = [
        {"gospel": "Matthew", "profile_basis": "Mark→Matthew aligned data", "confidence": "high for aligned core", "computed_indicators": {"pericope_requirement_rows": int((model_req.direction_id == "matthew_used_mark").sum()), "material_gap_rows": int((material_dir.direction_id == "matthew_used_mark").sum()), "pair_diff_rows": int((pairdiff.direction_id == "matthew_used_mark").sum())}, "inferred_tendencies": ["uses Mark-like sequence as narrative backbone", "adds/relocates non-Markan material", "clusters teaching/discourse material", "adds fulfillment/scriptural framing where present"], "caution": "Inferred from current alignment data."},
        {"gospel": "Luke", "profile_basis": "Mark→Luke and masked Matthew-Luke data", "confidence": "medium-high for Mark-prior over reverse", "computed_indicators": {"pericope_requirement_rows": int((model_req.direction_id == "luke_used_mark").sum()), "material_gap_rows": int((material_dir.direction_id == "luke_used_mark").sum()), "pair_diff_rows": int((pairdiff.direction_id == "luke_used_mark").sum())}, "inferred_tendencies": ["selective use of Mark-like sequence", "large non-Markan additions", "local smoothing/reframing", "displacement of sayings material"], "caution": "Shared-tradition alternatives require order-retention penalties."},
        {"gospel": "Mark_as_hypothetical_redactor", "profile_basis": "Reverse-direction ledgers", "confidence": "low-to-medium as explanatory profile", "computed_indicators": {"pericope_requirement_rows": int(model_req.direction_id.isin(["mark_used_matthew", "mark_used_luke"]).sum()), "material_gap_rows": int(material_dir.direction_id.isin(["mark_used_matthew", "mark_used_luke"]).sum()), "pair_diff_rows": int(pairdiff.direction_id.isin(["mark_used_matthew", "mark_used_luke"]).sum())}, "inferred_tendencies_required_by_reverse_models": ["radical abbreviation/epitome", "omission/non-use of infancy/discourse blocks", "action-focused compression"], "caution": "Required tendency under reverse models, not independently established."},
        {"gospel": "John", "profile_basis": "John/Synoptic anchor-specific ledger", "confidence": "medium for shared anchor traditions", "computed_indicators": {"anchor_rows": int(len(john_anchor_flat)), "unique_anchors": int(john_anchor_flat.anchor_id.nunique()) if "anchor_id" in john_anchor_flat else None}, "inferred_tendencies": ["transforms shared anchors into Johannine testimony/sign/discourse frames", "weak continuous order", "strongest overlap in passion/sign/Baptist anchors"], "caution": "Anchor dossiers are partly curated."},
    ]
    yaml.safe_dump(profiles, open(DATA / "60_redactional_tendency_profiles.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)

def build_conclusion_cards(support_contra):
    model_cards = yload_generated(DATA / "53_system_model_evidence_cards.yaml")
    cards = []
    for _, r in support_contra.iterrows():
        cards.append({"card_type": "direction_hypothesis", "claim_id": r.direction_id, "claim_label": r.hypothesis, "current_status": r.current_status, "pair": r.pair, "best_response_model": r.best_response_model, "linked_data_files": ["data/20_model_pericope_obligation_ledger.csv", "data/21_material_omission_addition_by_model.csv", "data/22_reordering_displacement_by_model.csv", "data/23_primary_pair_wording_change_diffs_by_model.csv.gz"], "note": "Indicator card, not proof."})
    for mc in model_cards:
        cards.append({"card_type": "system_model", "claim_id": mc["model_id"], "claim_label": mc["short_label"], "current_status": mc["rating"], "strongest_support": mc["strongest_support"], "strongest_contra_or_unresolved_burden": mc["strongest_contra_or_unresolved_burden"], "required_directions": mc["required_directions"], "criteria": mc["criteria"], "linked_data_files": ["data/52_system_model_comparison_scorecard.csv", "data/53_system_model_evidence_cards.yaml", "data/20_model_pericope_obligation_ledger.csv", "data/30_minor_agreements_catalog_triple_tradition.csv", "data/40_double_tradition_order_catalog_markan_masked.csv"]})
    yaml.safe_dump(cards, open(DATA / "81_conclusion_evidence_counterevidence_cards.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)
    yaml.safe_dump(support_contra.to_dict("records"), open(DATA / "80_direction_support_contra_cards.yaml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)

def yload_generated(path):
    return yaml.safe_load(open(path, encoding="utf-8"))

def build_data_layer_status():
    layers = [
        {"layer_id": "gospel_verse_inventory", "file": "data/01_gospel_verse_inventory.csv", "data_type": "source-derived", "objectivity": "high", "curation": "none beyond source normalization"},
        {"layer_id": "pericope_ontology", "file": "data/10_pericope_ontology_computational_and_anchor.csv", "data_type": "alignment ontology", "objectivity": "mixed", "curation": "computed Synoptic blocks plus curated John anchors"},
        {"layer_id": "model_obligations", "file": "data/20_model_pericope_obligation_ledger.csv", "data_type": "model implication ledger", "objectivity": "mixed", "curation": "algorithmic + interpretive response labels"},
        {"layer_id": "minor_agreements", "file": "data/30_minor_agreements_catalog_triple_tradition.csv", "data_type": "computed screening catalog", "objectivity": "medium-high", "curation": "algorithmic triple-alignment filter"},
        {"layer_id": "double_tradition_order", "file": "data/40_double_tradition_order_catalog_markan_masked.csv", "data_type": "computed/order catalog", "objectivity": "medium-high", "curation": "uses Markan mask from prior package"},
        {"layer_id": "model_scorecard", "file": "data/52_system_model_comparison_scorecard.csv", "data_type": "interpretive synthesis", "objectivity": "medium", "curation": "explicit model-level synthesis"},
        {"layer_id": "variant_sensitivity", "file": "data/70_variant_sensitivity_registry.csv", "data_type": "text-critical audit", "objectivity": "medium-high", "curation": "variant-marker and apparatus-note extraction"},
        {"layer_id": "conclusion_cards", "file": "data/81_conclusion_evidence_counterevidence_cards.yaml", "data_type": "expert-facing conclusion index", "objectivity": "mixed", "curation": "explicit synthesis"},
    ]
    pd.DataFrame(layers).to_csv(DATA / "90_data_layer_status_and_objectivity.csv", index=False)

def main():
    gospels = build_inventory()
    build_registries()
    direction_burden = csvload("direction_burden_summary")
    support_contra = csvload("support_contra_matrix")
    model_req = csvload("model_requirements")
    per_ledger = csvload("direction_pericope_ledger")
    material_dir = csvload("material_burdens_direction")
    reorder = csvload("reordering_catalog")
    pairdiff = pd.read_csv(IDX["primary_pair_diffs_all_directions"])
    john_pair_anchor = yload("john_pairwise_anchors")
    john_anchor_dir = csvload("john_direction_anchor_ledger")
    pericope_df = build_pericope_ontology(per_ledger, john_pair_anchor)
    obligations = build_model_obligations(model_req, john_anchor_dir, pericope_df)
    build_minor_agreements(gospels)
    build_double_tradition()
    # copy/synthesize core reference layers
    direction_burden.to_csv(DATA / "50_direction_burden_reference.csv", index=False)
    support_contra.to_csv(DATA / "80_direction_support_contra_matrix.csv", index=False)
    # model registry/component/scorecard
    dmap = direction_to_models()
    rows = []
    for m in MODEL_REGISTRY:
        for role, ds in [("required", m["required_direction_hypotheses"]), ("optional", m.get("optional_or_competing_components", []))]:
            for d in ds:
                matches = direction_burden[direction_burden.direction_id == d]
                if matches.empty:
                    rows.append({"model_id": m["model_id"], "direction_id": d, "component_role": role, "burden_score": np.nan, "interpretive_result": "unscored/model-level"})
                else:
                    for _, r in matches.iterrows():
                        rows.append({"model_id": m["model_id"], "direction_id": d, "component_role": role, "pair": r.pair, "burden_model": r.burden_model, "burden_score": r.burden_score, "interpretive_result": r.interpretive_result})
    pd.DataFrame(rows).to_csv(DATA / "51_model_component_direction_matrix.csv", index=False)
    # material/reorder/wording by model
    out = []
    for _, r in material_dir.iterrows():
        for mid in dmap.get(r.direction_id, []):
            rr = r.to_dict(); rr["model_id"] = mid
            out.append(rr)
    pd.DataFrame(out).to_csv(DATA / "21_material_omission_addition_by_model.csv", index=False)
    out = []
    for _, r in reorder.iterrows():
        for mid in dmap.get(r.direction_id, []):
            rr = r.to_dict(); rr["model_id"] = mid; rr["atlas_unit_id"] = f"{pair_to_id(r.pair)}_block_{r.unit_id}"
            out.append(rr)
    pd.DataFrame(out).to_csv(DATA / "22_reordering_displacement_by_model.csv", index=False)
    out = []
    for _, r in pairdiff.iterrows():
        for mid in dmap.get(r.direction_id, []):
            rr = r.to_dict(); rr["model_id"] = mid
            out.append(rr)
    pd.DataFrame(out).to_csv(DATA / "23_primary_pair_wording_change_diffs_by_model.csv.gz", index=False, compression="gzip")
    build_gospel_direction_matrix(direction_burden, support_contra)
    build_model_scorecard(direction_burden)
    john_anchor_flat = csvload("john_anchor_flat")
    build_variant_registry(gospels)
    build_redactional_profiles(model_req, material_dir, pairdiff, john_anchor_flat)
    build_conclusion_cards(support_contra)
    build_data_layer_status()
    print("Built atlas data in", DATA)

if __name__ == "__main__":
    main()
