"""Shared pytest fixtures for visualization tests.

These tests exist primarily to ensure the visualization bundle stays
in sync with changes to the upstream analysis packages. They
deliberately avoid pinning exact counts (which would churn on real
data updates) and instead validate structure, ranges, and cross-
references between bundle and source.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
VIZ = ROOT / "visualizations"
DATA = VIZ / "data"
BUNDLE_PATH = DATA / "bundle.json"
PREPROCESS = VIZ / "build" / "preprocess.py"


def _build_bundle() -> None:
    """Regenerate the bundle from source so tests always run on current data."""
    subprocess.run(
        [sys.executable, str(PREPROCESS)],
        cwd=VIZ,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session")
def bundle() -> dict[str, Any]:
    _build_bundle()
    with BUNDLE_PATH.open() as f:
        return json.load(f)


@pytest.fixture(scope="session")
def jtea(bundle) -> dict[str, Any]:
    assert "jtea" in bundle, "bundle missing jtea key"
    return bundle["jtea"]


@pytest.fixture(scope="session")
def html_files() -> list[Path]:
    return sorted(VIZ.glob("*.html"))


@pytest.fixture(scope="session")
def jtea_html_files(html_files) -> list[Path]:
    return [h for h in html_files if h.name[:2].isdigit() and int(h.name[:2]) >= 17]


@pytest.fixture(scope="session")
def synoptic_html_files(html_files) -> list[Path]:
    return [h for h in html_files if h.name[:2].isdigit() and 1 <= int(h.name[:2]) <= 16]


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
