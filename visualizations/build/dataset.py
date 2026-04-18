"""Dataset object and verse-index helpers shared across loaders.

Each synoptic dataset (mm, ml, mld) uses a ``Dataset`` instance to map
book+chapter+verse references to dense integer indices suitable for x/y axes
in the visualizations. Two separate counts are exposed per book:

- ``canonical_slot_count`` — sum of max verse-numbers per chapter, i.e. the
  total number of canonical verse *slots* (even those omitted by modern
  editions, like Mark 7:16). This is the axis length used by visualizations.
- ``actual_unit_count`` — count of actual verse rows present in the source
  CSV. This is the correct denominator for percentages/coverage.
- ``missing_slots`` — explicit list of canonical refs that are counted in the
  slot axis but absent from the source data.

See review item #4: the visualization x-axis must remain the canonical slot
layout, but any percentage/summary should cite ``actual_unit_count``.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

REF_RE = re.compile(r"(Mark|Matt|Luke)\s+(\d+):(\d+)")


def infer_chapter_lengths(csv_path: Path) -> dict[str, dict[int, int]]:
    """Return max verse number seen per (book, chapter)."""
    counts: dict[str, dict[int, int]] = {}
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            book = r["book"]
            _, body = r["ref"].split(None, 1)
            chap, verse = (int(x) for x in body.split(":"))
            counts.setdefault(book, {})
            counts[book][chap] = max(counts[book].get(chap, 0), verse)
    return counts


def actual_refs_by_book(csv_path: Path) -> dict[str, set[str]]:
    """Return set of actual refs present per book (for missing-slot detection)."""
    seen: dict[str, set[str]] = {}
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            seen.setdefault(r["book"], set()).add(r["ref"])
    return seen


def chapter_offsets(chapter_lens: dict[int, int]) -> tuple[dict[int, int], int]:
    running = 0
    offsets: dict[int, int] = {}
    for chap in sorted(chapter_lens):
        offsets[chap] = running
        running += chapter_lens[chap]
    return offsets, running


def missing_slots(book: str, chap_lens: dict[int, int], present_refs: set[str]) -> list[str]:
    """Every canonical slot that isn't present in the source CSV."""
    missing = []
    for chap, max_v in sorted(chap_lens.items()):
        for v in range(1, max_v + 1):
            ref = f"{book} {chap}:{v}"
            if ref not in present_refs:
                missing.append(ref)
    return missing


class Dataset:
    def __init__(self, name: str, root: Path, a_book: str, b_book: str, label: str):
        self.name = name
        self.root = root
        self.a_book = a_book
        self.b_book = b_book
        self.label = label

        flags_csv = root / "data" / "01_negative_space_flags.csv"
        chap_lens = infer_chapter_lengths(flags_csv)
        refs_by_book = actual_refs_by_book(flags_csv)

        self.a_chaps = chap_lens[a_book]
        self.b_chaps = chap_lens[b_book]
        self.a_offsets, self.a_total = chapter_offsets(self.a_chaps)
        self.b_offsets, self.b_total = chapter_offsets(self.b_chaps)

        # Actual vs canonical counts (review #4)
        self.a_actual = len(refs_by_book.get(a_book, set()))
        self.b_actual = len(refs_by_book.get(b_book, set()))
        self.a_missing = missing_slots(a_book, self.a_chaps, refs_by_book.get(a_book, set()))
        self.b_missing = missing_slots(b_book, self.b_chaps, refs_by_book.get(b_book, set()))

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

    def chap_info(self, book: str) -> list[dict[str, int]]:
        if book == self.a_book:
            chaps, offsets = self.a_chaps, self.a_offsets
        else:
            chaps, offsets = self.b_chaps, self.b_offsets
        return [
            {"chapter": c, "offset": offsets[c], "length": chaps[c]}
            for c in sorted(chaps)
        ]

    def verse_counts(self, book: str) -> dict[str, Any]:
        """Expose both counts and the missing-slot list for one book."""
        if book == self.a_book:
            return {
                "canonical_slot_count": self.a_total,
                "actual_unit_count": self.a_actual,
                "missing_canonical_slots": self.a_missing,
            }
        return {
            "canonical_slot_count": self.b_total,
            "actual_unit_count": self.b_actual,
            "missing_canonical_slots": self.b_missing,
        }
