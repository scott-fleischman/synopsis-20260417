"""MorphGNT word-level loader.

Reads the MorphGNT per-word files shipped with the reproducibility-patch
repro_sources and returns a per-book, per-verse list of word tokens. Each
token carries the lemma, morphology code, and normalized surface form — this
is what makes "hover a Greek word → see lemma + morph" possible on the reader
and on every pair-view that shows Greek text.

File format (one token per line, whitespace-delimited):

    BBCCVV POS MORPH surface normalized norm_lemma dict_lemma

where

    BBCCVV   — book(2) + chapter(2) + verse(2) zero-padded
    POS      — part-of-speech code (e.g. N-, V-, RA, C-)
    MORPH    — 8-char morph slot: ``-tvmpncg`` (tense/voice/mood/person/number/case/gender)
    surface  — the inflected form as printed in SBLGNT
    normalized — punctuation-stripped, lower-case form
    norm_lemma — dictionary lemma without critical marks
    dict_lemma — dictionary lemma with marks (the canonical headword)

The loader emits a compact encoding suitable for in-browser use: per verse,
a tab-separated string "surface|lemma|morph surface|lemma|morph ...", which
keeps the bundle well under 2MB for all four gospels combined. On the client
this is split back into word spans with hoverable tooltips.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .preprocess_paths import ROOT

MORPH_ROOT = ROOT / "analysis_update_20260418" / "sources" / "repro_sources" / "morphgnt"

# Map book short-name → filename prefix in the morphgnt directory.
_FILE_FOR_BOOK: dict[str, str] = {
    "Matt": "61-Mt-morphgnt.txt",
    "Mark": "62-Mk-morphgnt.txt",
    "Luke": "63-Lk-morphgnt.txt",
    "John": "64-Jn-morphgnt.txt",
}


def _parse_book(path: Path) -> dict[tuple[int, int], list[tuple[str, str, str]]]:
    """Returns {(chapter, verse) → [(surface, lemma, morph), ...]}."""
    out: dict[tuple[int, int], list[tuple[str, str, str]]] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) < 7:
                continue
            bcv = parts[0]
            if len(bcv) != 6 or not bcv.isdigit():
                continue
            pos = parts[1]
            morph = parts[2]
            surface = parts[3]
            lemma = parts[6]
            try:
                ch = int(bcv[2:4])
                vs = int(bcv[4:6])
            except ValueError:
                continue
            # MorphGNT fixed-width code: POS is 2 chars (e.g. "N-", "V-", "RA"),
            # morph is 8 positional slots (e.g. "----NSF-"). We concatenate to
            # a fixed 10-char code so the client can parse without ambiguity —
            # positions 0..1 = POS, 2..9 = morph slots (person, tense, voice,
            # mood, number, case, gender, degree, depending on POS family).
            code = pos + morph
            out.setdefault((ch, vs), []).append((surface, lemma, code))
    return out


def load_morph_for_books(books: list[str]) -> dict[str, dict[str, str]]:
    """Returns {book → {ref → "surface|lemma|morph surface|lemma|morph ..."}}.

    The per-ref value is a space-separated string of ``|``-delimited triplets,
    one triplet per word. This encoding is ~3× more compact than a nested
    array of objects while still trivially decodable on the client.
    """
    result: dict[str, dict[str, str]] = {}
    for book in books:
        fname = _FILE_FOR_BOOK.get(book)
        if not fname:
            continue
        path = MORPH_ROOT / fname
        if not path.exists():
            continue
        words_by_cv = _parse_book(path)
        by_ref: dict[str, str] = {}
        for (ch, vs), words in words_by_cv.items():
            ref = f"{book} {ch}:{vs}"
            parts = []
            for surface, lemma, morph in words:
                # Replace any stray pipe in source (extremely rare) with U+2758
                s = surface.replace("|", "\u2758")
                l = lemma.replace("|", "\u2758")
                m = morph.replace("|", "\u2758")
                parts.append(f"{s}|{l}|{m}")
            by_ref[ref] = " ".join(parts)
        result[book] = by_ref
    return result


__all__ = ["MORPH_ROOT", "load_morph_for_books"]
