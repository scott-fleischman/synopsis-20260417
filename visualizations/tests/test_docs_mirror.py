"""Drift guard for the committed ``docs/`` deployment snapshot.

``docs/`` is a committed mirror of ``visualizations/`` with the build/,
tests/, and pytest-cache directories dropped. It doubles as the GitHub Pages
output directory, so keeping it byte-identical to the source tree is a
correctness property.

Without these tests, ``docs/`` and ``visualizations/`` can silently diverge
if someone edits the source but forgets to re-mirror. Covers review item #11.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VIZ = ROOT / "visualizations"
DOCS = ROOT / "docs"


def _sha(p: Path) -> str:
    return sha256(p.read_bytes()).hexdigest()


def _mirrored_viz_files() -> list[Path]:
    """Files under visualizations/ that should appear in docs/.

    Excludes build/ (Python source for the bundle), tests/ (pytest), and
    any hidden dirs like .venv or __pycache__.
    """
    results: list[Path] = []
    for p in VIZ.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(VIZ).as_posix()
        if rel.startswith("build/"):
            continue
        if rel.startswith("tests/"):
            continue
        if "__pycache__/" in rel or "/.venv/" in rel or rel.startswith(".venv/"):
            continue
        if ".pytest_cache/" in rel:
            continue
        results.append(p)
    return results


@pytest.fixture(scope="session")
def expected_mirror_files() -> list[Path]:
    if not DOCS.exists():
        pytest.skip("docs/ snapshot not present in this checkout")
    return _mirrored_viz_files()


def test_docs_exists(expected_mirror_files):
    assert DOCS.is_dir(), "docs/ directory is missing"


def test_docs_covers_every_viz_file(expected_mirror_files):
    """Every eligible file in visualizations/ must have a counterpart in docs/."""
    missing: list[str] = []
    for src in expected_mirror_files:
        rel = src.relative_to(VIZ)
        target = DOCS / rel
        if not target.exists():
            missing.append(rel.as_posix())
    assert not missing, (
        f"docs/ is missing {len(missing)} file(s) from visualizations/: "
        f"{missing[:5]}"
    )


def test_docs_has_no_extra_source_files(expected_mirror_files):
    """docs/ may contain its own README.md but otherwise must not have files
    that are absent from visualizations/."""
    allowed_extras = {Path("README.md")}
    extras: list[str] = []
    for p in DOCS.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(DOCS)
        if rel in allowed_extras:
            continue
        if ".pytest_cache" in rel.parts:
            continue
        src = VIZ / rel
        if not src.exists():
            extras.append(rel.as_posix())
    assert not extras, (
        f"docs/ has {len(extras)} file(s) with no counterpart in visualizations/: "
        f"{extras[:5]}"
    )


def test_docs_files_are_byte_identical_to_viz(expected_mirror_files):
    """Every mirrored file must match the visualizations/ source byte-for-byte."""
    diffs: list[str] = []
    for src in expected_mirror_files:
        rel = src.relative_to(VIZ)
        target = DOCS / rel
        if not target.exists():
            continue  # covered by the previous test
        if _sha(src) != _sha(target):
            diffs.append(rel.as_posix())
    assert not diffs, (
        f"{len(diffs)} docs/ file(s) differ from visualizations/: {diffs[:5]}. "
        f"Re-mirror with: cp visualizations/*.html docs/ && "
        f"cp visualizations/assets/* docs/assets/ && "
        f"cp visualizations/data/bundle.* docs/data/"
    )
