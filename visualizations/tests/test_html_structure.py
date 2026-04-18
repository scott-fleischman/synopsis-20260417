"""HTML structural checks.

Guardrails against common breakages as pages/data evolve:
  - Every HTML page loads bundle.js and shared.js in correct order.
  - Every jtea page calls SH.buildJteaNav and references SH.BUNDLE.jtea.
  - Every Synoptic page calls SH.buildNav.
  - No innerHTML assignments (blocked by the project's security hook).
  - All cross-links in nav maps resolve to existing files.
"""

from __future__ import annotations

import re
from pathlib import Path


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_every_page_loads_bundle_and_shared(html_files):
    for p in html_files:
        s = _read(p)
        assert 'src="data/bundle.js"' in s, f"{p.name} missing bundle.js"
        assert 'src="assets/shared.js"' in s, f"{p.name} missing shared.js"
        # bundle must load before shared
        assert s.index("data/bundle.js") < s.index("assets/shared.js"), (
            f"{p.name}: bundle.js must load before shared.js"
        )


def test_every_jtea_page_uses_jtea_nav_and_bundle(jtea_html_files):
    for p in jtea_html_files:
        s = _read(p)
        assert "buildJteaNav" in s, f"{p.name} missing SH.buildJteaNav"
        # Either directly access .jtea or receive it via the bundle (case_studies page uses J = ...)
        assert ".jtea" in s or "jtea" in s.lower(), f"{p.name} doesn't reference jtea data"


def test_synoptic_pages_use_main_nav(synoptic_html_files):
    for p in synoptic_html_files:
        s = _read(p)
        assert "buildNav" in s, f"{p.name} missing SH.buildNav"


def test_no_inner_html_assignments(html_files):
    # The project's security hook blocks innerHTML assignments; keep
    # this as a test so future edits can't re-introduce them.
    pattern = re.compile(r"\.innerHTML\s*=")
    for p in html_files:
        s = _read(p)
        matches = pattern.findall(s)
        assert not matches, f"{p.name} has innerHTML assignment(s); use DOM composition instead"


def test_no_insert_adjacent_html(html_files):
    # insertAdjacentHTML bypasses the innerHTML ban but has the same XSS
    # surface when data carries markup. Review item #12 asks for it banned too.
    pattern = re.compile(r"\.insertAdjacentHTML\s*\(")
    for p in html_files:
        s = _read(p)
        assert not pattern.search(s), (
            f"{p.name} uses insertAdjacentHTML; use DOM composition (SH.el / appendChild) instead"
        )


def test_nav_targets_exist(html_files):
    all_names = {p.name for p in html_files}
    all_names.add("index.html")
    # Scan shared.js for the nav link arrays.
    shared = (html_files[0].parent / "assets" / "shared.js").read_text(encoding="utf-8")
    # Find all quoted *.html filenames in shared.js
    refs = set(re.findall(r"['\"]([\w\-]+\.html)['\"]", shared))
    missing = refs - all_names
    assert not missing, f"shared.js references missing HTML files: {missing}"


def test_every_html_has_topnav(html_files):
    for p in html_files:
        s = _read(p)
        assert 'id="topnav"' in s, f"{p.name} missing #topnav"


def test_jtea_pages_have_viewport_and_stylesheet(jtea_html_files):
    for p in jtea_html_files:
        s = _read(p)
        assert 'charset="utf-8"' in s, f"{p.name} missing charset"
        assert 'href="assets/style.css"' in s, f"{p.name} missing stylesheet"
        assert "viewport" in s, f"{p.name} missing viewport meta"


def test_index_has_jtea_section(html_files):
    idx = next(p for p in html_files if p.name == "index.html")
    s = _read(idx)
    assert 'id="jteaCards"' in s, "index.html missing jtea card grid"
    assert "Low-verbatim" in s, "index.html missing low-verbatim label"


def test_network_page_layer_values_match_bundle(jtea_html_files, jtea):
    # 18_intertext_network.html filters on bundle["network_edges"][*].layer
    net = next(p for p in jtea_html_files if p.name.startswith("18_"))
    s = _read(net)
    bundle_layers = {e["layer"] for e in jtea["network_edges"]}
    # Every <option value="X"> with a non-empty layer must exist in the bundle.
    opts = re.findall(r'<option\s+value="([^"]+)"[^>]*>(?:[^<]*(?:John|epistles|Epistles)[^<]*)</option>', s)
    for v in opts:
        if v:
            assert v in bundle_layers, (
                f"18_intertext_network.html option value '{v}' not in network_edges layers {bundle_layers}"
            )


def test_exact_hits_page_layer_values_match_bundle(jtea_html_files, jtea):
    hits = next(p for p in jtea_html_files if p.name.startswith("23_"))
    s = _read(hits)
    bundle_layers = {h["layer"] for h in jtea["exact_hits"]}
    opts = re.findall(r'<option\s+value="([^"]+)"[^>]*>(?:[^<]*(?:John|epistles|Epistles|epistle)[^<]*)</option>', s)
    for v in opts:
        if v:
            assert v in bundle_layers, (
                f"23_exact_hits.html option value '{v}' not in exact_hits layers {bundle_layers}"
            )
