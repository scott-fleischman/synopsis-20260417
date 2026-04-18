"""Loaders for the full-text reader view.

The reader (`30_reader.html`) needs complete verse text for every gospel, not
just the snippets carried alongside pair/echo records. This loader reads the
SBLGNT text files shipped with the reproducibility-patch repro_sources and
returns a per-book structure keyed by chapter and verse:

    {
        "book": "Matt",
        "display": "ΚΑΤΑ ΜΑΘΘΑΙΟΝ",
        "chapters": [
            {
                "chapter": 1,
                "verses": [
                    {"verse": 1, "ref": "Matt 1:1", "text": "..."},
                    ...
                ],
            },
            ...
        ],
    }

Each file begins with a Greek title line (ΚΑΤΑ ...) followed by
tab-separated ``Book C:V\\tGreek text`` lines. Critical marks (⸀, ⸂, ⸃, etc.)
are preserved because the variant markers are meaningful to expert readers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .preprocess_paths import ROOT

TEXT_ROOT = (
    ROOT / "analysis_update_20260418" / "sources" / "repro_sources" / "sblgnt" / "text"
)


def _parse_text_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    display = ""
    chapters_map: dict[int, list[dict[str, Any]]] = {}
    with open(path) as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if i == 0 and "\t" not in line:
                display = line.strip()
                continue
            if "\t" not in line:
                continue
            ref, text = line.split("\t", 1)
            ref = ref.strip()
            text = text.strip()
            parts = ref.rsplit(" ", 1)
            if len(parts) != 2:
                continue
            book = parts[0].strip()
            cv = parts[1].strip()
            if ":" not in cv:
                continue
            try:
                ch_s, vs_s = cv.split(":", 1)
                ch = int(ch_s)
                vs = int(vs_s)
            except ValueError:
                continue
            chapters_map.setdefault(ch, []).append(
                {"verse": vs, "ref": ref, "text": text}
            )
    chapters = []
    for ch in sorted(chapters_map.keys()):
        verses = sorted(chapters_map[ch], key=lambda r: r["verse"])
        chapters.append({"chapter": ch, "verses": verses})
    return {"book": path.stem, "display": display, "chapters": chapters}


def load_reader_books(books: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for b in books:
        rec = _parse_text_file(TEXT_ROOT / f"{b}.txt")
        if rec is not None:
            out.append(rec)
    return out


__all__ = ["TEXT_ROOT", "load_reader_books"]
