"""Build idempotence: running preprocess twice produces byte-identical output."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from conftest import VIZ, PREPROCESS, BUNDLE_PATH


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_build_idempotent():
    subprocess.run([sys.executable, str(PREPROCESS)], cwd=VIZ, check=True, capture_output=True)
    first = _sha256(BUNDLE_PATH)
    subprocess.run([sys.executable, str(PREPROCESS)], cwd=VIZ, check=True, capture_output=True)
    second = _sha256(BUNDLE_PATH)
    assert first == second, "preprocess.py should produce the same bundle on repeated runs"
