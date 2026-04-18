// Shared helpers for dual-dataset synopsis visualizations.
(function () {
  const BUNDLE = window.SYNOPSIS;
  if (!BUNDLE || !BUNDLE.mm || !BUNDLE.ml) {
    console.error('SYNOPSIS bundle missing mm/ml');
    return;
  }
  const VALID_DS = ['mm', 'ml', 'mld'].filter(n => BUNDLE[n]);

  // Dataset is chosen by URL hash or localStorage; default mm.
  // Hash can be either a bare dataset name (#mm, #ml, #mld) or a nested form
  // like #mm/Matt 1:3|Mark 1:3 used by the pair explorer.
  function currentDataset() {
    const h = (window.location.hash || '').replace('#', '');
    const prefix = h.split('/')[0];
    if (VALID_DS.indexOf(prefix) >= 0) return prefix;
    try {
      const saved = localStorage.getItem('synopsis_ds');
      if (VALID_DS.indexOf(saved) >= 0) return saved;
    } catch (e) { /* ignore */ }
    return 'mm';
  }

  function setDataset(name) {
    try { localStorage.setItem('synopsis_ds', name); } catch (e) { /* ignore */ }
    window.location.hash = name;
    window.location.reload();
  }

  let D = BUNDLE[currentDataset()];

  // Tooltip
  const tip = document.createElement('div');
  tip.className = 'tooltip';
  tip.style.display = 'none';
  document.body.appendChild(tip);

  function showTip(content, x, y) {
    while (tip.firstChild) tip.removeChild(tip.firstChild);
    if (typeof content === 'string') tip.textContent = content;
    else if (Array.isArray(content)) content.forEach(n => tip.appendChild(n));
    else tip.appendChild(content);
    tip.style.display = 'block';
    const rect = tip.getBoundingClientRect();
    let tx = x + 14;
    let ty = y + 10;
    if (tx + rect.width > window.innerWidth - 10) tx = x - rect.width - 14;
    if (ty + rect.height > window.innerHeight - 10) ty = y - rect.height - 10;
    tip.style.left = tx + 'px';
    tip.style.top = ty + 'px';
  }

  function hideTip() { tip.style.display = 'none'; }

  function el(tag, attrs, ...children) {
    const e = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      if (k === 'class') e.className = attrs[k];
      else if (k === 'style') e.style.cssText = attrs[k];
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    }
    for (const c of children.flat()) {
      if (c === null || c === undefined) continue;
      if (c instanceof Node) e.appendChild(c);
      else e.appendChild(document.createTextNode(String(c)));
    }
    return e;
  }

  function tipLine(text, cls) {
    const d = document.createElement('div');
    if (cls) d.className = cls;
    d.textContent = text;
    return d;
  }

  function tipRow(label, value) {
    const d = document.createElement('div');
    const b = document.createElement('b'); b.textContent = label + ': ';
    d.appendChild(b);
    d.appendChild(document.createTextNode(value));
    return d;
  }

  function tipGreek(text) {
    const d = document.createElement('div');
    d.className = 'g';
    d.style.marginTop = '6px';
    d.textContent = text;
    return d;
  }

  function scoreColor(s) {
    const stops = [
      [0, [244, 239, 223]],
      [0.3, [221, 189, 133]],
      [0.55, [185, 128, 76]],
      [0.8, [138, 72, 35]],
      [1, [92, 36, 12]],
    ];
    for (let i = 0; i < stops.length - 1; i++) {
      if (s <= stops[i + 1][0]) {
        const t = (s - stops[i][0]) / (stops[i + 1][0] - stops[i][0] || 1);
        const a = stops[i][1];
        const b = stops[i + 1][1];
        return `rgb(${Math.round(a[0] + (b[0] - a[0]) * t)},${Math.round(a[1] + (b[1] - a[1]) * t)},${Math.round(a[2] + (b[2] - a[2]) * t)})`;
      }
    }
    return 'rgb(92,36,12)';
  }

  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  // Some pages only make sense for one or a subset of datasets. When current
  // dataset is not in `availableOn`, the link is disabled but still shown
  // so users see it exists and can understand why it is inactive.
  function buildNav(current) {
    const nav = document.getElementById('topnav');
    if (!nav) return;
    const links = [
      ['index.html', 'Overview', null],
      ['01_synoptic_map.html', 'Synoptic map', null],
      ['02_block_ribbon.html', 'Block ribbon', null],
      ['03_burden_ledger.html', 'Direction burden', null],
      ['04_gap_timeline.html', 'Gap timeline', null],
      ['05_lexical_drift.html', 'Lexical drift', ['mm', 'ml']],
      ['06_score_classes.html', 'Pair classes', null],
      ['07_block_cards.html', 'Block cards', null],
      ['08_stylistic_markers.html', 'Stylistic markers', ['mm', 'ml']],
      ['09_pair_explorer.html', 'Pair explorer', null],
      ['10_displacement.html', 'Displacement', ['ml', 'mld']],
      ['11_echo_gallery.html', 'Echo gallery', null],
      ['12_variants.html', 'Variants', null],
      ['13_triangle.html', 'Synoptic triangle', null],
      ['14_mask_audit.html', 'Mask audit', ['mld']],
      ['15_q_core.html', 'Q core reader', ['mld']],
      ['16_matt_verse_card.html', 'Matthew verse card', null],
      ['17_jtea_overview.html', 'Low-verbatim →', '__jtea'],
    ];
    while (nav.firstChild) nav.removeChild(nav.firstChild);
    for (const [h, t, avail] of links) {
      const a = document.createElement('a');
      const isJteaLink = avail === '__jtea';
      const isDisabled = !isJteaLink && avail && avail.indexOf(D.name) < 0;
      a.href = isJteaLink ? h : (h + '#' + (isDisabled ? avail[0] : D.name));
      a.textContent = t;
      const classes = [];
      if (h === current) classes.push('current');
      if (isDisabled) {
        classes.push('disabled');
        a.title = 'Only available for: ' + avail.join(', ');
      }
      if (isJteaLink) classes.push('section-link');
      if (classes.length) a.className = classes.join(' ');
      nav.appendChild(a);
    }
  }

  // Nav for the low-verbatim (jtea) package. Kept separate from the synoptic
  // pages because the data model and switcher semantics are different.
  function buildJteaNav(current) {
    const nav = document.getElementById('topnav');
    if (!nav) return;
    const links = [
      ['index.html', 'Synoptic overview'],
      ['17_jtea_overview.html', 'Low-verbatim overview'],
      ['18_intertext_network.html', 'Intertext network'],
      ['19_case_studies.html', 'Case studies'],
      ['20_john_anchors.html', 'John/Synoptic anchors'],
      ['21_thomas_parallels.html', 'Thomas parallels'],
      ['22_concept_signatures.html', 'Concept signatures'],
      ['23_exact_hits.html', 'Exact-phrase hits'],
      ['24_epistle_gospel_heatmap.html', 'Epistle × Gospel'],
      ['25_apocrypha_inventory.html', 'Apocrypha inventory'],
    ];
    while (nav.firstChild) nav.removeChild(nav.firstChild);
    for (const [h, t] of links) {
      const a = document.createElement('a');
      a.href = h;
      a.textContent = t;
      if (h === current) a.className = 'current';
      nav.appendChild(a);
    }
  }

  function buildDatasetSwitcher(container, opts) {
    opts = opts || {};
    const wrap = document.createElement('div');
    wrap.className = 'ds-switcher';
    wrap.style.cssText = 'display:inline-flex;gap:0;border:1px solid var(--rule);border-radius:3px;overflow:hidden;';
    const labels = {
      mm: 'Mark ↔ Matthew',
      ml: 'Matt ↔ Luke',
      mld: 'Matt ↔ Luke (masked)',
    };
    // `only` lets a page restrict the switcher to a subset (e.g. mld-only pages).
    const allowed = opts.only || VALID_DS;
    const mk = (name, label) => {
      const btn = document.createElement('button');
      btn.textContent = label;
      btn.style.cssText = 'border:0;padding:6px 12px;background:' + (D.name === name ? 'var(--ink)' : '#fff') +
        ';color:' + (D.name === name ? '#fff' : 'var(--ink)') + ';font-size:12px;cursor:pointer;white-space:nowrap;';
      btn.addEventListener('click', () => { setDataset(name); });
      return btn;
    };
    for (const n of allowed) {
      if (BUNDLE[n]) wrap.appendChild(mk(n, labels[n] || n));
    }
    if (container) container.appendChild(wrap);
    return wrap;
  }

  function svgEl(name, attrs) {
    const e = document.createElementNS('http://www.w3.org/2000/svg', name);
    if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }

  function svgElText(text, attrs) {
    const e = svgEl('text', attrs);
    e.textContent = text;
    return e;
  }

  function scale(domainMin, domainMax, rangeMin, rangeMax) {
    const d = domainMax - domainMin || 1;
    const r = rangeMax - rangeMin;
    return v => rangeMin + ((v - domainMin) / d) * r;
  }

  function chapterLookup(chapters) {
    return function (idx) {
      for (let i = chapters.length - 1; i >= 0; i--) {
        if (idx >= chapters[i].offset) {
          return { chapter: chapters[i].chapter, verse: idx - chapters[i].offset + 1 };
        }
      }
      return { chapter: 1, verse: idx + 1 };
    };
  }

  window.SH = {
    BUNDLE,
    get D() { return D; },
    setDataset,
    currentDataset,
    showTip, hideTip, tipLine, tipRow, tipGreek,
    scoreColor, buildNav, buildJteaNav, buildDatasetSwitcher, svgEl, svgElText, scale, clamp,
    chapterLookup,
    el,
  };
})();
