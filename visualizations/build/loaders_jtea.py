"""Loaders for the John/Thomas/Epistles/Apocrypha (jtea) low-verbatim package.

Fundamentally different from mm/ml/mld: no single primary chain, no
monotonic order expectation. The bundle packs curated registries (YAML)
plus aggregated/filtered lexical retrieval layers (CSV).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml

from .preprocess_paths import ROOT

JTEA_ROOT = ROOT / "john_thomas_epistles_apocrypha_analysis"

_BOOK_ORDER = [
    "Matt", "Mark", "Luke", "John", "Acts",
    "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil", "Col",
    "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm",
    "Heb", "Jas", "1Pet", "2Pet", "1John", "2John", "3John",
    "Jude", "Rev",
]


def _book_order(book: str) -> int:
    try:
        return _BOOK_ORDER.index(book)
    except ValueError:
        return 99


def _yaml(path: Path) -> Any:
    with open(path) as f:
        return yaml.safe_load(f)


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _yaml_list_or_key(path: Path, *keys: str) -> list[Any]:
    data = _yaml(path)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in keys:
            v = data.get(k)
            if isinstance(v, list):
                return v
    return []


def load_jtea_case_studies() -> list[Any]:
    return _yaml_list_or_key(JTEA_ROOT / "data" / "07_targeted_case_studies.yaml", "cases", "case_studies")


def load_jtea_anchors() -> list[Any]:
    return _yaml_list_or_key(JTEA_ROOT / "data" / "08_john_synoptic_anchor_registry.yaml", "anchors")


def load_jtea_thomas_registry() -> list[Any]:
    return _yaml_list_or_key(JTEA_ROOT / "data" / "09_thomas_parallel_registry.yaml", "entries", "parallels")


def load_jtea_concepts() -> list[Any]:
    return _yaml_list_or_key(JTEA_ROOT / "data" / "11_concept_signature_registry.yaml", "concepts", "signatures")


def load_jtea_burden_ledger() -> Any:
    return _yaml(JTEA_ROOT / "data" / "14_burden_ledger.yaml")


def load_jtea_method() -> Any:
    return _yaml(JTEA_ROOT / "data" / "00_method_rethought_low_verbatim.yaml")


def load_jtea_summary() -> Any:
    return _yaml(JTEA_ROOT / "data" / "16_global_summary.yaml")


def load_jtea_thomas_units() -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for r in _csv_rows(JTEA_ROOT / "data" / "03_thomas_units.csv"):
        raw_id = (r.get("thomas_logion", "") or "").strip()
        idx_val: Any
        try:
            idx_val = int(raw_id)
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


def load_jtea_apocrypha() -> list[dict[str, str]]:
    return _csv_rows(JTEA_ROOT / "data" / "12_apocrypha_inventory_from_mr_james.csv")


def load_jtea_exact_hits() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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


def load_jtea_network_edges() -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
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


def load_jtea_negspace_flags() -> list[dict[str, Any]]:
    """Count flag occurrences + keep one sample row per flag family."""
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
    items: list[dict[str, Any]] = []
    for flg, ct in sorted(flag_counts.items(), key=lambda x: -x[1]):
        items.append({
            "flag": flg,
            "count": ct,
            "sample": sample_row[flg],
            "rule": rules[flg],
        })
    return items


_OT_BOOK_PREFIXES = (
    "gen", "exod", "lev", "num", "deut",
    "josh", "judg", "ruth", "sam", "kgs", "kings",
    "chr", "ezra", "neh", "esth", "job",
    "ps",
    "prov", "eccl", "song", "isa", "jer", "lam", "ezek", "dan",
    "hos", "joel", "amos", "obad", "jonah", "mic", "nah", "hab",
    "zeph", "hag", "zech", "mal",
)

_HIGH_CONTAINS = (
    "scripture", "ot_quote", "creed", "liturg", "eucharist", "kyrie",
    "lord_supper", "new_covenant", "shema", "decalog",
)

_MEDIUM_CONTAINS = (
    "formula", "citation", "proverb", "doxolog", "paraenetic",
    "hymn", "benediction", "commandment", "household_code",
)

_LOW_EXPLICIT = ("nonfungible_phrase_candidate", "thin_lexical_basis")


def _risk_tier_for_flag(flag: str) -> str:
    f = flag.lower()
    if f in _LOW_EXPLICIT:
        return "low"
    # Flag names of the form "<ot_book><chapter>_<topic>" (e.g. ``gen2_one_flesh``,
    # ``ps110_right_hand``) signal a shared OT quotation — the #1 false-positive
    # source for exact Gospel/epistle matches. Tier these high.
    for prefix in _OT_BOOK_PREFIXES:
        if f.startswith(prefix) and len(f) > len(prefix) and (f[len(prefix)].isdigit() or f[len(prefix)] == "_"):
            return "high"
    if any(k in f for k in _HIGH_CONTAINS):
        return "high"
    if any(k in f for k in _MEDIUM_CONTAINS):
        return "medium"
    return "low"


def load_jtea_exact_hit_flags_by_ref() -> dict[str, dict[str, Any]]:
    """Keyed flag lookup for the exact-hits page (review #18).

    Returns a mapping {source_ref|target_ref → {flags, rule, risk}} so that
    the exact-hits view can paint a per-row formula-risk badge. Risk is the
    max tier across all flags on the row — any high-risk flag promotes the
    whole row.
    """
    tier_rank = {"high": 3, "medium": 2, "low": 1}
    result: dict[str, dict[str, Any]] = {}

    for r in _csv_rows(JTEA_ROOT / "data" / "10_negative_space_flags_for_exact_hits.csv"):
        flags = r.get("negative_space_flags", "").strip()
        if not flags:
            continue
        key = f"{r.get('source_ref', '')}|{r.get('target_ref', '')}"
        flag_list = [f.strip() for f in flags.split("|") if f.strip()]
        tiers = [_risk_tier_for_flag(f) for f in flag_list]
        risk = max(tiers, key=lambda t: tier_rank.get(t, 0)) if tiers else "low"
        result[key] = {
            "flags": flag_list,
            "rule": r.get("interpretation_rule", ""),
            "risk": risk,
        }
    return result


def load_jtea_book_matrix() -> list[dict[str, Any]]:
    """Aggregate 04 (epistles→gospels) and 05 (john→synoptics) into book×book cells."""
    cells: dict[tuple[str, str], dict[str, Any]] = {}

    def _agg(path: Path) -> None:
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


def load_jtea_canonical_book_counts() -> list[dict[str, Any]]:
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
    books: list[dict[str, Any]] = []
    for bk in sorted(book_chaps, key=_book_order):
        total = sum(book_chaps[bk].values())
        books.append({
            "book": bk,
            "order": _book_order(bk),
            "chapter_count": len(book_chaps[bk]),
            "verse_count": total,
        })
    return books
