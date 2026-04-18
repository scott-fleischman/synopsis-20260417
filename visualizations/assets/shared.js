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

  // Unified 8-section research-question nav. Every page renders the full
  // map of the project grouped by the question it answers; section labels
  // are compact small-caps on the left, page links flow to the right.
  //
  // `dsaware` per page: true  → link appends `#<dataset>` and can be disabled
  //                            when the active dataset is not in availableOn.
  //                     false → plain link (JTEA, conclusions, reader).
  //
  // Legacy callers buildNav/buildJteaNav both delegate here; the distinction
  // between "Synoptic-side" and "JTEA-side" pages no longer matters for the
  // navigation — readers should see the same map from every page.
  const NAV_SECTIONS = [
    { id: 'start', label: 'Start here', pages: [
      ['index.html', 'Overview'],
      ['26_conclusions.html', 'Conclusions'],
      ['29_jtea_claim_evidence.html', 'Claim → evidence'],
      ['30_reader.html', 'Reader'],
      ['31_gospel_square.html', 'Gospel Square'],
    ]},
    { id: 'directional', label: 'Directional hypotheses (20260418)', pages: [
      ['36_directional_registry.html', 'Registry · 12 directions'],
      ['37_direction_dossier.html', 'Per-direction dossier'],
      ['38_system_hypotheses.html', 'System hypothesis space'],
    ]},
    { id: 'mkl', label: 'Mark ↔ Luke (18b)', pages: [
      ['34_mark_luke.html', 'Mark↔Luke direct'],
      ['13_triangle.html', 'Synoptic matrix'],
    ]},
    { id: 'john', label: 'John pairwise (18b)', pages: [
      ['35_john_pairwise.html', 'John pairwise'],
      ['20_john_anchors.html', 'John anchors (legacy)'],
      ['18_intertext_network.html', 'Intertext network'],
    ]},
    { id: 'synoptic', label: 'Synoptic (mm · ml · mld)', pages: [
      ['01_synoptic_map.html', 'Map', { ds: true }],
      ['02_block_ribbon.html', 'Ribbon', { ds: true }],
      ['03_burden_ledger.html', 'Burden', { ds: true }],
      ['04_gap_timeline.html', 'Gaps', { ds: true }],
      ['05_lexical_drift.html', 'Lexical drift', { ds: true, availableOn: ['mm', 'ml'] }],
      ['06_score_classes.html', 'Pair classes', { ds: true }],
      ['07_block_cards.html', 'Block cards', { ds: true }],
      ['08_stylistic_markers.html', 'Stylistic', { ds: true, availableOn: ['mm', 'ml'] }],
      ['09_pair_explorer.html', 'Pair explorer', { ds: true }],
      ['12_variants.html', 'Variants', { ds: true }],
    ]},
    { id: 'q', label: 'Q & double tradition', pages: [
      ['10_displacement.html', 'Displacement', { ds: true, availableOn: ['ml', 'mld'] }],
      ['11_echo_gallery.html', 'Echo gallery', { ds: true }],
      ['14_mask_audit.html', 'Mask audit', { ds: true, availableOn: ['mld'] }],
      ['15_q_core.html', 'Q core reader', { ds: true, availableOn: ['mld'] }],
      ['16_matt_verse_card.html', 'Matt verse card ⓘ'],
    ]},
    { id: 'thomas', label: 'Thomas (18b)', pages: [
      ['32_thomas_matrix.html', 'Thomas × canon'],
      ['21_thomas_parallels.html', 'Thomas parallels (legacy)'],
    ]},
    { id: 'epistles', label: 'Epistles (18b)', pages: [
      ['33_epistle_dossier.html', 'Dossier'],
      ['19_case_studies.html', 'Case studies (legacy)'],
      ['22_concept_signatures.html', 'Concept signatures'],
      ['23_exact_hits.html', 'Exact hits'],
      ['24_epistle_gospel_heatmap.html', 'Epistle × Gospel'],
    ]},
    { id: 'apocrypha', label: 'Apocrypha', pages: [
      ['25_apocrypha_inventory.html', 'Inventory ⓘ'],
    ]},
    { id: 'audit', label: 'Audit & reproducibility', pages: [
      ['17_jtea_overview.html', 'Low-verbatim tour'],
      ['27_mm_sensitivity.html', 'Sensitivity · mm', { ds: true, availableOn: ['mm'] }],
      ['28_mld_regime_sensitivity.html', 'Sensitivity · mld', { ds: true, availableOn: ['mld'] }],
    ]},
  ];

  function buildNav8(current) {
    const nav = document.getElementById('topnav');
    if (!nav) return;
    nav.classList.add('topnav-8');
    while (nav.firstChild) nav.removeChild(nav.firstChild);
    const currentDs = D ? D.name : null;
    for (const section of NAV_SECTIONS) {
      const wrap = document.createElement('div');
      wrap.className = 'nav-section';
      const lbl = document.createElement('span');
      lbl.className = 'nav-section-label';
      lbl.textContent = section.label;
      wrap.appendChild(lbl);
      for (const p of section.pages) {
        const [h, t, opts] = p;
        const o = opts || {};
        const a = document.createElement('a');
        const availableOn = o.availableOn || null;
        const isDisabled = !!(o.ds && availableOn && currentDs && availableOn.indexOf(currentDs) < 0);
        if (o.ds && currentDs) {
          a.href = h + '#' + (isDisabled ? availableOn[0] : currentDs);
        } else {
          a.href = h;
        }
        a.textContent = t;
        const classes = [];
        if (h === current) classes.push('current');
        if (isDisabled) {
          classes.push('disabled');
          a.title = 'Only available for: ' + availableOn.join(', ');
        }
        if (classes.length) a.className = classes.join(' ');
        wrap.appendChild(a);
      }
      nav.appendChild(wrap);
    }
  }

  // Legacy wrappers — kept so existing pages don't need to be edited to call
  // the new function. Both produce the same 8-section nav.
  function buildNav(current) { buildNav8(current); }
  function buildJteaNav(current) { buildNav8(current); }

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
    // Mark↔Luke (18b) is a separate data shape; surface it as a navigation redirect
    // rather than pretending it shares the mm/ml/mld pipeline. Hidden when `only`
    // is set (mld-only pages, etc.) and when the h18b supplement is unavailable.
    if (!opts.only && !opts.hideMkl && BUNDLE.h18b && BUNDLE.h18b.mkl) {
      const sep = document.createElement('span');
      sep.style.cssText = 'display:inline-block;width:1px;background:var(--rule);';
      wrap.appendChild(sep);
      const a = document.createElement('a');
      a.href = '34_mark_luke.html';
      a.textContent = 'Mark ↔ Luke (direct) →';
      a.title = 'Opens the dedicated Mark↔Luke page (different data shape; not hash-switchable here)';
      a.style.cssText = 'padding:6px 12px;background:#fdf6ea;color:var(--ink);font-size:12px;text-decoration:none;white-space:nowrap;border-left:1px dashed var(--rule);';
      wrap.appendChild(a);
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

  // Footer — license attribution and provenance. Attached once per page, after
  // the main .wrap. Kept small but explicit because the corpora have different
  // upstream licenses (CC BY 4.0, CC-BY-SA, CC-BY) and the project MIT does not
  // override them.
  function buildFooter() {
    if (document.querySelector('footer.site-footer')) return;
    const foot = document.createElement('footer');
    foot.className = 'site-footer';
    foot.style.cssText = 'max-width:1200px;margin:40px auto 24px;padding:20px 24px;' +
      'border-top:1px solid var(--rule);font-size:11px;color:var(--ink-mute);' +
      'line-height:1.65;font-family:var(--serif);';

    // DOM-composition helpers: strong label, link, em, code, plain text, row.
    const s = (t) => { const e = document.createElement('strong'); e.textContent = t; return e; };
    const a = (href, t) => {
      const e = document.createElement('a');
      e.href = href; e.style.color = 'inherit'; e.textContent = t; return e;
    };
    const em = (t) => { const e = document.createElement('em'); e.textContent = t; return e; };
    const code = (t) => { const e = document.createElement('code'); e.textContent = t; return e; };
    const row = (...kids) => {
      const d = document.createElement('div');
      for (const k of kids) {
        if (k == null) continue;
        d.appendChild(typeof k === 'string' ? document.createTextNode(k) : k);
      }
      return d;
    };

    foot.appendChild(row(
      s('Project'), ' · MIT (code & visualizations) · ',
      a('https://scott-fleischman.github.io/synopsis-20260417/',
        'scott-fleischman.github.io/synopsis-20260417'),
    ));
    foot.appendChild(row(
      s('Sources'), ' · ',
      a('https://sblgnt.com/', 'SBLGNT'),
      ' (CC BY 4.0, Society of Biblical Literature & Logos) · ',
      a('https://github.com/morphgnt/sblgnt', 'MorphGNT'),
      ' (CC BY-SA 3.0, James Tauber) · ',
      a('https://copticscriptorium.org/', 'Coptic Scriptorium'),
      ' Thomas (CC BY 4.0) · M.R. James, ',
      em('The Apocryphal New Testament'), ' (1924, public domain)',
    ));
    foot.appendChild(row(
      s('Rerun'), ' · Reproducibility-patch analyses from ',
      code('analysis_update_20260418/'),
      ' · per-file SHA256 hashes in each package\u2019s MANIFEST.yaml · ',
      'all headline numbers, burden totals, and sensitivity grids on these pages are driven from that patch\u2019s outputs.',
    ));
    document.body.appendChild(foot);
  }

  // ---- Reader links: turn any "Matt 13:3" / "John 1:29-34" into a clickable ----
  // chip that jumps into 30_reader.html with a scroll target. Non-gospel refs
  // (epistles, Rev, etc.) return null so callers can decide what to render.
  const READER_BOOKS = new Set(['Matt', 'Mark', 'Luke', 'John']);

  function refBook(ref) {
    const m = (ref || '').match(/^([1-3]?[A-Za-z]+)\s+\d/);
    return m ? m[1] : null;
  }

  function readerHref(ref) {
    const bk = refBook(ref);
    if (!bk || !READER_BOOKS.has(bk)) return null;
    // Strip any verse range (e.g. "John 1:29-34" → jump to first verse).
    const first = (ref.match(/^([1-3]?[A-Za-z]+\s+\d+:\d+)/) || [])[1] || ref;
    return '30_reader.html#' + bk + '/' + encodeURIComponent(first);
  }

  function readerLink(ref, label) {
    const href = readerHref(ref);
    if (!href) return null;
    const a = document.createElement('a');
    a.href = href;
    a.className = 'reader-chip';
    a.textContent = label || ('read ' + ref + ' →');
    a.style.cssText = 'display:inline-block;font-size:11px;padding:1px 7px;' +
      'background:#e7f1ef;color:#0f766e;border-radius:2px;text-decoration:none;' +
      'margin-left:4px;vertical-align:middle;';
    return a;
  }

  // ---- MorphGNT word-level rendering for Matt/Mark/Luke/John ----
  // Called by readers and by any viz that wants per-word lemma hovers.
  // ``BUNDLE.morph[book][ref]`` is a space-separated string where each
  // space-delimited token is ``surface|lemma|code`` (code is 10 chars:
  // 2-char POS + 8-slot morph). See loaders_morph.py for the encoding.
  function morphWords(ref) {
    const bk = refBook(ref);
    if (!bk || !BUNDLE.morph || !BUNDLE.morph[bk]) return null;
    const s = BUNDLE.morph[bk][ref];
    if (!s) return null;
    return s.split(' ').map(tok => {
      const parts = tok.split('|');
      return { surface: parts[0] || '', lemma: parts[1] || '', code: parts[2] || '' };
    });
  }

  // Decode a MorphGNT 10-char parse code to a short human description.
  // POS (first 2 chars) determines which slots in the remaining 8 are used.
  const _POS_NAME = {
    'A-': 'adj', 'C-': 'conj', 'D-': 'adv', 'I-': 'interj',
    'N-': 'noun', 'P-': 'prep',
    'RA': 'art', 'RD': 'demon', 'RI': 'interr', 'RP': 'pers',
    'RR': 'rel', 'RS': 'poss',
    'V-': 'verb', 'X-': 'part',
  };
  const _TENSE = { P: 'pres', I: 'impf', F: 'fut', A: 'aor', X: 'perf', Y: 'pluperf' };
  const _VOICE = { A: 'act', M: 'mid', P: 'pass', E: 'mid/pass', D: 'mid-dep', O: 'pass-dep', N: 'mid/pass-dep' };
  const _MOOD  = { I: 'ind', D: 'imp', S: 'subj', O: 'opt', N: 'inf', P: 'ptc' };
  const _PERS  = { '1': '1', '2': '2', '3': '3' };
  const _NUM   = { S: 'sg', P: 'pl', D: 'du' };
  const _CASE  = { N: 'nom', G: 'gen', D: 'dat', A: 'acc', V: 'voc' };
  const _GEND  = { M: 'masc', F: 'fem', N: 'neut' };

  function morphDecode(code) {
    if (!code || code.length < 4) return '';
    const pos = code.slice(0, 2);
    const slot = code.slice(2);
    const label = _POS_NAME[pos] || pos;
    // Slot order: person, tense, voice, mood, case|number, number|case, gender, degree
    // For verbs we read tense at slot[1], voice slot[2], mood slot[3], person slot[0], number slot[4].
    // For nouns/adj/article/pron, case is slot[4], number slot[5], gender slot[6].
    const p = slot[0], t = slot[1], v = slot[2], m = slot[3];
    const n = slot[4], cs = slot[5], g = slot[6];
    const parts = [];
    if (pos === 'V-') {
      if (t && t !== '-') parts.push(_TENSE[t] || t);
      if (v && v !== '-') parts.push(_VOICE[v] || v);
      if (m && m !== '-') parts.push(_MOOD[m] || m);
      if (p && p !== '-') parts.push(_PERS[p] || p);
      if (n && n !== '-') parts.push(_NUM[n] || n);
      if (cs && cs !== '-') parts.push(_CASE[cs] || cs);
      if (g && g !== '-') parts.push(_GEND[g] || g);
    } else {
      if (n && n !== '-') parts.push(_CASE[n] || n);
      if (cs && cs !== '-') parts.push(_NUM[cs] || cs);
      if (g && g !== '-') parts.push(_GEND[g] || g);
    }
    return label + (parts.length ? ' · ' + parts.join(' ') : '');
  }

  // Wrap a Greek verse with per-word spans so each word is hoverable for
  // lemma + morph. Returns a DocumentFragment. If morph data is unavailable
  // (non-gospel, or ref lookup fails), returns a plain text node instead.
  function greekVerseFragment(ref, fallbackText) {
    const words = morphWords(ref);
    if (!words || !words.length) return document.createTextNode(fallbackText || '');
    const frag = document.createDocumentFragment();
    // Walk fallbackText character-by-character, emitting word spans that match
    // each morphgnt surface in order; characters between surfaces (punctuation,
    // whitespace, critical marks ⸀ ⸂ ⸃ etc.) pass through as-is. This lets us
    // preserve the SBLGNT's text-critical punctuation while making each
    // morphgnt-tokenized word a hover target.
    const ft = fallbackText || words.map(w => w.surface).join(' ');
    let ftIdx = 0;
    for (const w of words) {
      const s = w.surface;
      const found = ft.indexOf(s, ftIdx);
      if (found < 0) {
        // Surface not present — fall back to naive inter-word space.
        if (ftIdx > 0) frag.appendChild(document.createTextNode(' '));
        const span = _makeLemmaSpan(w);
        frag.appendChild(span);
        continue;
      }
      if (found > ftIdx) frag.appendChild(document.createTextNode(ft.slice(ftIdx, found)));
      frag.appendChild(_makeLemmaSpan(w));
      ftIdx = found + s.length;
    }
    if (ftIdx < ft.length) frag.appendChild(document.createTextNode(ft.slice(ftIdx)));
    return frag;
  }

  function _makeLemmaSpan(w) {
    const span = document.createElement('span');
    span.className = 'gw';
    span.textContent = w.surface;
    span.setAttribute('data-lemma', w.lemma);
    span.setAttribute('data-code', w.code);
    span.addEventListener('mouseenter', (e) => {
      const wrap = document.createElement('div');
      wrap.appendChild(tipLine(w.lemma, 'g'));
      const parse = morphDecode(w.code);
      if (parse) wrap.appendChild(tipLine(parse, 'small'));
      wrap.appendChild(tipLine('lemma · hover ✳ click nothing', 'small'));
      showTip(wrap, e.clientX, e.clientY);
    });
    span.addEventListener('mouseleave', hideTip);
    return span;
  }

  // ---- Evidence ladder: three-way confidence from the rerun ----
  // (retrieval, philological, formula_risk). Renders a compact badge with
  // three coloured dots + a chip summarizing the best-case label. Used by
  // pair explorer, echo gallery, case studies, concept signatures — anywhere
  // a single rerun claim drives the view.
  function _levelColor(level, isRisk) {
    const l = (level || '').toLowerCase();
    if (l === 'strong')  return '#0f766e';
    if (l === 'medium')  return isRisk ? '#a35d1a' : '#22506c';
    if (l === 'weak')    return '#8b2e2e';
    if (l === 'low')     return '#0f766e';   // low formula risk = good
    if (l === 'high')    return '#8b2e2e';   // high formula risk = bad
    if (l.indexOf('n/a') === 0) return '#9a7500';
    return '#bdb095';
  }

  function evidenceBadge(dims) {
    const d = document.createElement('span');
    d.className = 'ev-badge';
    d.style.cssText = 'display:inline-flex;align-items:center;gap:5px;font-size:10px;' +
      'color:var(--ink-mute);white-space:nowrap;line-height:1;';
    const mkDot = (level, isRisk, title) => {
      const dot = document.createElement('span');
      dot.style.cssText = 'width:10px;height:10px;border-radius:50%;display:inline-block;' +
        'background:' + _levelColor(level, isRisk) + ';' +
        'border:1px solid rgba(0,0,0,.18);';
      dot.title = title + ': ' + (level || '—');
      return dot;
    };
    d.appendChild(mkDot(dims.retrieval, false, 'retrieval'));
    d.appendChild(mkDot(dims.philological, false, 'philological'));
    d.appendChild(mkDot(dims.formula_risk, true, 'formula risk'));
    const lbl = document.createElement('span');
    lbl.textContent = 'ret/phil/risk';
    lbl.style.cssText = 'font-variant:all-small-caps;letter-spacing:0.05em;';
    d.appendChild(lbl);
    d.addEventListener('mouseenter', (e) => {
      const wrap = document.createElement('div');
      wrap.appendChild(tipLine('Evidence ladder', null));
      wrap.appendChild(tipRow('retrieval', dims.retrieval || '—'));
      wrap.appendChild(tipRow('philological', dims.philological || '—'));
      wrap.appendChild(tipRow('formula risk', dims.formula_risk || '—'));
      wrap.appendChild(tipLine('automatic · close reading · formulaic overlap', 'small'));
      showTip(wrap, e.clientX, e.clientY);
    });
    d.addEventListener('mouseleave', hideTip);
    return d;
  }

  // ---- Concept + anchor lookups: turn a ref into its pericope/theme ----
  // Used by reader and by any viz that wants to surface "this verse is part
  // of the 'worker_wages' concept cluster" or "…of the 'feeding_5000' anchor".
  let _conceptByRef = null;
  function _buildConceptByRef() {
    const map = new Map();
    const concepts = (BUNDLE.jtea && BUNDLE.jtea.concepts) || [];
    for (const c of concepts) {
      const refs = []
        .concat(c.canonical_refs || [])
        .concat(c.epistle_refs || []);
      for (const r of refs) {
        for (const ref of _expandRange(r)) {
          if (!map.has(ref)) map.set(ref, []);
          map.get(ref).push(c);
        }
      }
    }
    return map;
  }

  let _anchorByRef = null;
  function _buildAnchorByRef() {
    const map = new Map();
    const anchors = (BUNDLE.jtea && BUNDLE.jtea.anchors) || [];
    for (const a of anchors) {
      const johnRefs = (a.john_refs || '').split(';').map(s => s.trim()).filter(Boolean);
      const synRefs = Array.isArray(a.synoptic_refs) ? a.synoptic_refs :
                      (a.synoptic_refs || '').split(';').map(s => s.trim()).filter(Boolean);
      for (const g of johnRefs.concat(synRefs)) {
        for (const ref of _expandRange(g)) {
          if (!map.has(ref)) map.set(ref, []);
          map.get(ref).push(a);
        }
      }
    }
    return map;
  }

  function _expandRange(s) {
    const m = (s || '').match(/^([1-3]?[A-Za-z]+)\s+(\d+):(\d+)(?:-(\d+))?$/);
    if (!m) return [s];
    const book = m[1], ch = m[2], v1 = parseInt(m[3], 10);
    const v2 = m[4] ? parseInt(m[4], 10) : v1;
    const out = [];
    for (let v = v1; v <= v2; v++) out.push(book + ' ' + ch + ':' + v);
    return out;
  }

  function conceptsForRef(ref) {
    if (!_conceptByRef) _conceptByRef = _buildConceptByRef();
    return _conceptByRef.get(ref) || [];
  }

  function anchorsForRef(ref) {
    if (!_anchorByRef) _anchorByRef = _buildAnchorByRef();
    return _anchorByRef.get(ref) || [];
  }

  // ---- Ref chip: standardized clickable reference with Greek-on-hover ----
  // Every viz that surfaces a reference should render it this way, so users
  // have one consistent mental model: hover = Greek text preview, click =
  // jump to the reader anchored at that verse.
  function refChip(ref, opts) {
    opts = opts || {};
    const href = readerHref(ref);
    const el_ = document.createElement(href ? 'a' : 'span');
    el_.className = 'ref-chip' + (opts.className ? ' ' + opts.className : '');
    if (href) el_.href = href;
    el_.textContent = opts.label || ref;
    // Order matters: defaults first, caller style last so a caller-supplied
    // color/border can override. `opts.plain` suppresses the default focus
    // color + dotted underline (useful when the ref chip inherits its styling
    // from a surrounding CSS class, e.g. .corpus-row.canon .ref-chip).
    const plain = !!opts.plain;
    el_.style.cssText =
      'font-variant-numeric:tabular-nums;font-size:' + (opts.fontSize || '12px') + ';' +
      (href && !plain ? 'color:var(--focus);text-decoration:none;border-bottom:1px dotted var(--focus);' : 'text-decoration:none;') +
      'cursor:' + (href ? 'pointer' : 'default') + ';' +
      (opts.style || '');
    if (href) {
      el_.addEventListener('mouseenter', (e) => {
        const words = morphWords(ref);
        const reader = BUNDLE.reader || [];
        let text = '';
        const bk = refBook(ref);
        if (bk) {
          const book = reader.find(b => b.book === bk);
          if (book) {
            for (const ch of book.chapters) {
              for (const v of ch.verses) if (v.ref === ref) { text = v.text; break; }
              if (text) break;
            }
          }
        }
        const wrap = document.createElement('div');
        wrap.appendChild(tipLine(ref, null));
        if (text) {
          const g = document.createElement('div');
          g.className = 'g';
          g.style.marginTop = '4px';
          g.style.maxWidth = '420px';
          g.textContent = text;
          wrap.appendChild(g);
        }
        if (words && !text) {
          wrap.appendChild(tipGreek(words.map(w => w.surface).join(' ')));
        }
        wrap.appendChild(tipLine('click · open reader at this verse', 'small'));
        showTip(wrap, e.clientX, e.clientY);
      });
      el_.addEventListener('mouseleave', hideTip);
    }
    return el_;
  }

  // ---- Reader → viz highlight overlay ---------------------------------
  // Convention: destination pages link with `?hi=<ref>` query param. Pages
  // can mark candidate elements with `data-hi-ref="<ref>"` and call
  // `SH.applyHighlight()` after rendering to focus + scroll the first match.
  // Pages can opt into richer matching by passing a `match(ref, el)` predicate.
  function getHighlightRef() {
    try {
      const p = new URLSearchParams(window.location.search);
      const v = p.get('hi');
      return v ? decodeURIComponent(v) : null;
    } catch (e) { return null; }
  }

  function applyHighlight(opts) {
    const ref = getHighlightRef();
    if (!ref) return null;
    opts = opts || {};
    const container = opts.container || document.body;
    let matches;
    if (typeof opts.match === 'function') {
      matches = Array.from(container.querySelectorAll(opts.selector || '[data-hi-ref]'))
        .filter(el => opts.match(ref, el));
    } else {
      matches = Array.from(container.querySelectorAll(
        '[data-hi-ref="' + ref.replace(/"/g, '\\"') + '"]'
      ));
    }
    matches.forEach(el => el.classList.add('ref-hi'));
    if (matches.length) {
      const first = matches[0];
      // Defer scroll so any just-appended DOM has settled and CSS applied.
      setTimeout(() => first.scrollIntoView({ block: 'center', behavior: 'smooth' }), 40);
    }
    return { ref, count: matches.length };
  }

  // Build a viz URL that highlights a given ref when the destination page loads.
  function vizHrefWithHighlight(href, ref) {
    if (!ref) return href;
    const [pre, hash] = href.split('#');
    const sep = pre.indexOf('?') >= 0 ? '&' : '?';
    return pre + sep + 'hi=' + encodeURIComponent(ref) + (hash ? '#' + hash : '');
  }

  window.SH = {
    BUNDLE,
    get D() { return D; },
    setDataset,
    currentDataset,
    showTip, hideTip, tipLine, tipRow, tipGreek,
    scoreColor, buildNav, buildJteaNav, buildNav8, buildDatasetSwitcher, buildFooter, svgEl, svgElText, scale, clamp,
    chapterLookup,
    el,
    // Reader + morph + evidence helpers
    READER_BOOKS, refBook, readerHref, readerLink,
    morphWords, morphDecode, greekVerseFragment,
    evidenceBadge,
    conceptsForRef, anchorsForRef,
    refChip,
    // Highlight overlay
    getHighlightRef, applyHighlight, vizHrefWithHighlight,
  };

  // Auto-attach footer once DOM is ready — no need to edit every page.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildFooter);
  } else {
    buildFooter();
  }
})();
