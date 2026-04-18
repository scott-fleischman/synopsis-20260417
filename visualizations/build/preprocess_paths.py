"""Shared path constants so loader modules can import without cycles."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "visualizations" / "data"
