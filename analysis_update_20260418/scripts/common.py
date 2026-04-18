from __future__ import annotations
import re, math, json, gzip, hashlib, unicodedata, collections, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd
import yaml

BOOKS_INFO = {'Matt': {'text': 'Matt.txt', 'morph': '61-Mt-morphgnt.txt', 'app': 'Matt.xml'}, 'Mark': {'text': 'Mark.txt', 'morph': '62-Mk-morphgnt.txt', 'app': 'Mark.xml'}, 'Luke': {'text': 'Luke.txt', 'morph': '63-Lk-morphgnt.txt', 'app': 'Luke.xml'}, 'John': {'text': 'John.txt', 'morph': '64-Jn-morphgnt.txt', 'app': 'John.xml'}, '1Cor': {'text': '1Cor.txt', 'morph': '67-1Co-morphgnt.txt', 'app': '1Cor.xml'}, '1Tim': {'text': '1Tim.txt', 'morph': '75-1Ti-morphgnt.txt', 'app': '1Tim.xml'}, '2Tim': {'text': '2Tim.txt', 'morph': '76-2Ti-morphgnt.txt', 'app': '2Tim.xml'}, 'Jas': {'text': 'Jas.txt', 'morph': '80-Jas-morphgnt.txt', 'app': 'Jas.xml'}, '1John': {'text': '1John.txt', 'morph': '83-1Jn-morphgnt.txt', 'app': '1John.xml'}}
CRIT_CHARS = '⸀⸁⸂⸃⸄⸅⸆⸇⸈⸉⸊⸋⸌⸍⸎⸏⟦⟧[](){}“”‘’«»‹›'
PUNCT = '.,;··:!?—–-…†·'
TRANS = str.maketrans({c:' ' for c in CRIT_CHARS + PUNCT + '\t\n\r'})
GREEK_STOPWORDS = {'ως', 'αυτοι', 'τινα', 'εστιν', 'γαρ', 'τινος', 'τη', 'την', 'τω', 'απο', 'αι', 'εις', 'εν', 'τε', 'τας', 'τις', 'ουχ', 'και', 'οι', 'ος', 'γε', 'ειμι', 'ουκ', 'εκεινος', 'ου', 'μου', 'μη', 'ουδε', 'ταις', 'οις', 'αυτοις', 'παρα', 'αλλα', 'προς', 'δια', 'η', 'τινες', 'ημιν', 'εκ', 'αυτην', 'μηδε', 'σοι', 'ουτος', 'ει', 'μην', 'ιδου', 'εστι', 'τοις', 'ον', 'των', 'κατα', 'που', 'ποτε', 'μοι', 'υμιν', 'αυτων', 'συ', 'ους', 'του', 'αυτου', 'ο', 'το', 'ησαν', 'αυτος', 'ουν', 'υμεις', 'τουτο', 'σου', 'μεν', 'εαν', 'τι', 'εξ', 'οτι', 'δε', 'τα', 'εγω', 'αν', 'ημεις', 'ην'}

src_base = Path('.')
books = {}

def strip_diacritics(s:str)->str:
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = s.replace('ς','σ')
    return unicodedata.normalize('NFC', s)


def normalize_greek(s:str)->str:
    s = s.translate(TRANS)
    s = s.lower()
    s = strip_diacritics(s)
    s = re.sub(r'[^0-9a-zα-ω\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def text_without_double_brackets(lines: List[str]) -> List[str]:
    """Remove text inside ⟦ ⟧ spans, allowing spans across verses."""
    out = []
    inside = False
    for line in lines:
        new = []
        for ch in line:
            if ch == '⟦':
                inside = True
                continue
            if ch == '⟧':
                inside = False
                continue
            if not inside:
                new.append(ch)
        out.append(''.join(new))
    return out


def parse_sbl_text(book: str) -> List[Dict[str,Any]]:
    path = src_base/'sblgnt'/'text'/BOOKS_INFO[book]['text']
    raw_lines = path.read_text(encoding='utf-8').splitlines()
    verses = []
    verse_lines = []
    for line in raw_lines:
        line = line.rstrip()
        if not line:
            continue
        m = re.match(rf'{re.escape(book)} (\d+):(\d+)\t(.*)$', line)
        if m:
            chap, verse, text = m.groups()
            verses.append({'book':book,'chapter':int(chap),'verse':int(verse),'ref':f'{book} {chap}:{verse}','text_raw':text.strip()})
            verse_lines.append(text.strip())
    no_double = text_without_double_brackets(verse_lines)
    for v, txt in zip(verses, no_double):
        v['text_no_double'] = txt
        v['contains_double_bracket'] = ('⟦' in v['text_raw']) or ('⟧' in v['text_raw'])
        v['contains_square_bracket'] = ('[' in v['text_raw']) or (']' in v['text_raw'])
        v['text_norm_full'] = normalize_greek(v['text_raw'])
        v['text_norm_default'] = normalize_greek(txt)
        v['tokens_full'] = v['text_norm_full'].split()
        v['tokens_default'] = v['text_norm_default'].split()
        v['token_count_full'] = len(v['tokens_full'])
        v['token_count_default'] = len(v['tokens_default'])
    return verses


def parse_morph(book:str)->Dict[str,List[Dict[str,Any]]]:
    if book not in BOOKS_INFO or 'morph' not in BOOKS_INFO[book]:
        return {}
    path = src_base/'morphgnt'/BOOKS_INFO[book]['morph']
    verse_tokens = collections.defaultdict(list)
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) % 7 != 0:
            raise ValueError((book, path, line))
        for i in range(0, len(parts), 7):
            bcvid, pos, parsing, text, word, norm, lemma = parts[i:i+7]
            chap = int(bcvid[2:4]); verse = int(bcvid[4:6])
            ref = f'{book} {chap}:{verse}'
            verse_tokens[ref].append({
                'bcvid':bcvid,'pos':pos,'parsing':parsing,'text':text,
                'word':word,'norm':normalize_greek(norm),'lemma':normalize_greek(lemma)
            })
    return verse_tokens


def parse_apparatus(book:str)->Dict[str,List[str]]:
    path = src_base/'sblgntapp'/'xml'/BOOKS_INFO[book]['app']
    if not path.exists():
        return {}
    root = ET.fromstring(path.read_text(encoding='utf-8'))
    notes = collections.defaultdict(list)
    current_ref = None
    for child in root:
        tag = child.tag.split('}')[-1]
        if tag == 'verse':
            current_ref = (child.text or '').strip()
        elif tag == 'note' and current_ref:
            txt = ''.join(child.itertext()).strip()
            if txt:
                notes[current_ref].append(txt)
    return notes


def negative_space_flags(v:Dict[str,Any])->Dict[str,Any]:
    text = v['text_norm_default']
    toks = v['tokens_default']
    short = len(toks) <= 3
    citation_patterns = ['καθως γεγραπται','γεγραπται','ινα πληρωθη','το ρηθεν','λεγει η γραφη','καθως ειπεν','ειπεν ο θεος']
    has_formula = any(p in text for p in citation_patterns)
    bracket = v['contains_double_bracket'] or v['contains_square_bracket'] or (v['text_raw'].strip() and not v['text_norm_default'])
    return {
        'short_verse': short,
        'citation_formula': has_formula,
        'bracketed_text': bracket,
        'text_critical_empty_after_default': bool(v['text_raw'].strip() and not v['text_norm_default']),
        'cheap_shared': bool(short or has_formula),
    }


def canonical_slot_info(verses:List[Dict[str,Any]])->Dict[str,Any]:
    maxv = collections.defaultdict(int)
    seen = collections.defaultdict(set)
    for v in verses:
        c, n = v['chapter'], v['verse']
        maxv[c] = max(maxv[c], n)
        seen[c].add(n)
    missing = []
    for c, m in sorted(maxv.items()):
        for i in range(1, m+1):
            if i not in seen[c]:
                missing.append(f"{verses[0]['book']} {c}:{i}")
    return {
        'actual_unit_count': len(verses),
        'canonical_slot_count': sum(maxv.values()),
        'missing_canonical_slots': missing,
        'chapter_max_verses': {int(k):int(v) for k,v in sorted(maxv.items())},
    }


def parse_book(book:str)->List[Dict[str,Any]]:
    verses = parse_sbl_text(book)
    morph = parse_morph(book)
    app = parse_apparatus(book)
    for v in verses:
        ref = v['ref']
        toks = morph.get(ref, [])
        v['morph_tokens'] = toks
        v['lemmas'] = [t['lemma'] for t in toks if t['lemma']]
        v['lemma_counts'] = collections.Counter(v['lemmas'])
        v['flags'] = negative_space_flags(v)
        v['variant_notes'] = app.get(ref, [])
        v['variant_note_count'] = len(v['variant_notes'])
    return verses


def bigrams(tokens):
    return [tuple(tokens[i:i+2]) for i in range(len(tokens)-1)]


def trigrams(tokens):
    return [tuple(tokens[i:i+3]) for i in range(len(tokens)-2)]


def idf_weights(verses, field='lemmas'):
    docs = []
    for v in verses:
        toks = v.get(field, [])
        docs.append(set(toks))
    N = len(docs)
    df = collections.Counter()
    for d in docs:
        df.update(d)
    return {tok: math.log((N+1)/(count+1))+1 for tok,count in df.items()}


def weighted_dice_pre(counter_a, counter_b, weights, sum_a=None, sum_b=None):
    if sum_a is None:
        sum_a = sum(weights.get(k,1.0)*v for k,v in counter_a.items())
    if sum_b is None:
        sum_b = sum(weights.get(k,1.0)*v for k,v in counter_b.items())
    if not sum_a and not sum_b:
        return 0.0
    inter = 0.0
    if len(counter_a) < len(counter_b):
        for k, va in counter_a.items():
            vb = counter_b.get(k)
            if vb:
                inter += weights.get(k,1.0) * min(va, vb)
    else:
        for k, vb in counter_b.items():
            va = counter_a.get(k)
            if va:
                inter += weights.get(k,1.0) * min(va, vb)
    return (2*inter)/(sum_a+sum_b)


def simple_dice_pre(counter_a, counter_b):
    sa = sum(counter_a.values()); sb = sum(counter_b.values())
    if not sa and not sb:
        return 0.0
    inter = 0
    if len(counter_a) < len(counter_b):
        for k, va in counter_a.items():
            vb = counter_b.get(k)
            if vb:
                inter += min(va, vb)
    else:
        for k, vb in counter_b.items():
            va = counter_a.get(k)
            if va:
                inter += min(va, vb)
    return (2*inter)/(sa+sb)


def longest_common_run(tokens_a, tokens_b):
    # exact contiguous longest run
    if not tokens_a or not tokens_b:
        return 0, []
    m, n = len(tokens_a), len(tokens_b)
    prev = [0]*(n+1)
    best = 0; end_a = 0
    for i in range(1,m+1):
        curr = [0]*(n+1)
        ta = tokens_a[i-1]
        for j in range(1,n+1):
            if ta == tokens_b[j-1]:
                curr[j] = prev[j-1] + 1
                if curr[j] > best:
                    best = curr[j]
                    end_a = i
        prev = curr
    return best, tokens_a[end_a-best:end_a]


def prep_verse_features(verses, weights):
    out=[]
    for v in verses:
        # text-critical update: if default text is empty after bracket removal, exclude from lemma layer too
        if v['text_norm_default']:
            lemmas = v['lemmas'] if v['lemmas'] else v['tokens_default']
        else:
            lemmas = []
        lemma_counter = collections.Counter(lemmas)
        token_counter = collections.Counter(v['tokens_default'])
        bg_counter = collections.Counter(bigrams(v['tokens_default']))
        tg_counter = collections.Counter(trigrams(v['tokens_default']))
        content = [t for t in lemmas if t not in GREEK_STOPWORDS]
        content_counter = collections.Counter(content)
        out.append({
            **v,
            'lemmas_eff': lemmas,
            'lemma_counter': lemma_counter,
            'lemma_sumw': sum(weights.get(k,1.0)*v for k,v in lemma_counter.items()),
            'token_counter': token_counter,
            'bg_counter': bg_counter,
            'tg_counter': tg_counter,
            'content_counter': content_counter,
            'content_sumw': sum(weights.get(k,1.0)*v for k,v in content_counter.items()),
        })
    return out


def pair_metrics_fast(v1, v2, weights):
    wd_lem = weighted_dice_pre(v1['lemma_counter'], v2['lemma_counter'], weights, v1['lemma_sumw'], v2['lemma_sumw'])
    tok_dice = simple_dice_pre(v1['token_counter'], v2['token_counter'])
    bg_dice = simple_dice_pre(v1['bg_counter'], v2['bg_counter'])
    tg_dice = simple_dice_pre(v1['tg_counter'], v2['tg_counter'])
    lcs_len, lcs = longest_common_run(v1['tokens_default'], v2['tokens_default'])
    lcs_ratio = lcs_len / max(1, min(len(v1['tokens_default']), len(v2['tokens_default'])))
    content_wd = weighted_dice_pre(v1['content_counter'], v2['content_counter'], weights, v1['content_sumw'], v2['content_sumw'])
    score = 0.40*wd_lem + 0.18*tok_dice + 0.17*bg_dice + 0.05*tg_dice + 0.10*lcs_ratio + 0.10*content_wd
    if v1['flags']['cheap_shared'] and v2['flags']['cheap_shared']:
        score *= 0.85
    if v1['flags']['bracketed_text'] or v2['flags']['bracketed_text']:
        score *= 0.8
    return {
        'score': float(score),
        'lemma_dice': float(wd_lem),
        'token_dice': float(tok_dice),
        'bigram_dice': float(bg_dice),
        'trigram_dice': float(tg_dice),
        'lcs_len': int(lcs_len),
        'lcs_ratio': float(lcs_ratio),
        'lcs': lcs,
        'content_dice': float(content_wd),
    }


def prep_books_pair(book_a, book_b, field='lemmas'):
    A = books[book_a]; B = books[book_b]
    weights = idf_weights(A+B, field=field)
    A2 = prep_verse_features(A, weights)
    B2 = prep_verse_features(B, weights)
    return A2, B2, weights


def compute_score_matrix(A2, B2, weights, with_details=False):
    m, n = len(A2), len(B2)
    scores = np.zeros((m,n), dtype=np.float32)
    details = None
    if with_details:
        details = [[None]*n for _ in range(m)]
    for i, va in enumerate(A2):
        for j, vb in enumerate(B2):
            pm = pair_metrics_fast(va, vb, weights)
            scores[i,j] = pm['score']
            if with_details:
                details[i][j] = pm
    return scores, details


def contextual_adjust_fast(scores: np.ndarray) -> np.ndarray:
    m,n = scores.shape
    pads = []
    def shifted(di,dj):
        arr = np.zeros_like(scores)
        src_i_start = max(0, -di)
        src_i_end = m - max(0, di)
        dst_i_start = max(0, di)
        dst_i_end = dst_i_start + (src_i_end - src_i_start)
        src_j_start = max(0, -dj)
        src_j_end = n - max(0, dj)
        dst_j_start = max(0, dj)
        dst_j_end = dst_j_start + (src_j_end - src_j_start)
        arr[dst_i_start:dst_i_end, dst_j_start:dst_j_end] = scores[src_i_start:src_i_end, src_j_start:src_j_end]
        return arr
    support = np.maximum.reduce([
        shifted(-1,-1), shifted(1,1), shifted(-1,0), shifted(0,-1), shifted(1,0), shifted(0,1)
    ])
    return 0.8*scores + 0.2*support


def align_primary_chain(scores: np.ndarray, min_match=0.26, gap_penalty=0.05):
    m,n = scores.shape
    dp = np.zeros((m+1,n+1), dtype=np.float32)
    bt = np.zeros((m+1,n+1), dtype=np.int8)  # 1 up,2 left,3 diag
    for i in range(1,m+1):
        for j in range(1,n+1):
            best = dp[i-1,j]; b=1
            if dp[i,j-1] > best:
                best = dp[i,j-1]; b=2
            s = float(scores[i-1,j-1])
            if s >= min_match:
                cand = dp[i-1,j-1] + (s - gap_penalty)
                if cand > best:
                    best = cand; b=3
            dp[i,j] = best; bt[i,j]=b
    pairs=[]
    i,j=m,n
    while i>0 and j>0:
        b = bt[i,j]
        if b == 3:
            s=float(scores[i-1,j-1])
            if s >= min_match:
                pairs.append((i-1,j-1,s))
            i-=1; j-=1
        elif b == 1:
            i-=1
        else:
            j-=1
    pairs.reverse()
    return pairs, float(dp[m,n])


def segment_pairs(pairs, loose_a=3, loose_b=6, tight_a=1, tight_b=2):
    def seg(maxa, maxb):
        blocks=[]
        cur=[]
        prev=None
        for p in pairs:
            if prev is None:
                cur=[p]
            else:
                da = p[0]-prev[0]
                db = p[1]-prev[1]
                if da<=maxa and db<=maxb:
                    cur.append(p)
                else:
                    blocks.append(cur); cur=[p]
            prev=p
        if cur: blocks.append(cur)
        return blocks
    return seg(loose_a, loose_b), seg(tight_a, tight_b)


def pair_diff_ops(tokens_a, tokens_b):
    import difflib
    sm = difflib.SequenceMatcher(a=tokens_a, b=tokens_b)
    ops=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal':
            ops.append({'op':'equal','a':tokens_a[i1:i2],'b':tokens_b[j1:j2]})
        elif tag=='delete':
            ops.append({'op':'delete','a':tokens_a[i1:i2],'b':[]})
        elif tag=='insert':
            ops.append({'op':'insert','a':[],'b':tokens_b[j1:j2]})
        else:
            ops.append({'op':'replace','a':tokens_a[i1:i2],'b':tokens_b[j1:j2]})
    return ops


def summarize_pair_diff(v1, v2):
    ops = pair_diff_ops(v1['tokens_default'], v2['tokens_default'])
    inserted = []; deleted=[]; repl=[]
    eq=0
    for op in ops:
        if op['op']=='insert':
            inserted.extend(op['b'])
        elif op['op']=='delete':
            deleted.extend(op['a'])
        elif op['op']=='replace':
            if op['a'] or op['b']:
                repl.append((' '.join(op['a']), ' '.join(op['b'])))
        else:
            eq += len(op['a'])
    return {
        'inserted_tokens': inserted,
        'deleted_tokens': deleted,
        'replacement_groups': repl,
        'equal_tokens': eq,
        'ops': [{'op':x['op'],'a':' '.join(x['a']),'b':' '.join(x['b'])} for x in ops],
    }


def attach_variants_for_pairs(pairs, A2, B2):
    out=[]
    for i,j,s in pairs:
        va, vb = A2[i], B2[j]
        out.append({
            'a_ref':va['ref'],'b_ref':vb['ref'],'score':round(float(s),6),
            'a_variant_note_count':va['variant_note_count'],'b_variant_note_count':vb['variant_note_count'],
            'a_variant_notes':va['variant_notes'],'b_variant_notes':vb['variant_notes'],
            'a_bracketed':bool(va['flags']['bracketed_text']),'b_bracketed':bool(vb['flags']['bracketed_text']),
        })
    return out


def top_hits_df(A2, B2, scores, topn=20, direction='A_to_B'):
    rows=[]
    if direction=='A_to_B':
        for i, va in enumerate(A2):
            js = np.argsort(scores[i])[::-1][:topn]
            for rank, j in enumerate(js, start=1):
                rows.append({'source_ref':va['ref'],'target_ref':B2[j]['ref'],'rank':rank,'score':float(scores[i,j])})
    else:
        for j, vb in enumerate(B2):
            is_ = np.argsort(scores[:,j])[::-1][:topn]
            for rank, i in enumerate(is_, start=1):
                rows.append({'source_ref':vb['ref'],'target_ref':A2[i]['ref'],'rank':rank,'score':float(scores[i,j])})
    return pd.DataFrame(rows)


def build_windows(book_name, window=3):
    vs = books[book_name]
    out=[]
    for i in range(len(vs)-window+1):
        chunk = vs[i:i+window]
        out.append({
            'book':book_name,
            'start_ref':chunk[0]['ref'],
            'end_ref':chunk[-1]['ref'],
            'ref':f"{chunk[0]['ref']}–{chunk[-1]['ref']}",
            'tokens_default': sum((v['tokens_default'] for v in chunk), []),
            'lemmas': sum((v['lemmas'] if v['lemmas'] else v['tokens_default'] for v in chunk), []),
            'flags': {
                'cheap_shared': any(v['flags']['cheap_shared'] for v in chunk),
                'bracketed_text': any(v['flags']['bracketed_text'] for v in chunk)
            }
        })
    return out


def prep_window_features(wins, weights):
    out=[]
    for w in wins:
        lemmas = w['lemmas']
        tokens = w['tokens_default']
        lemma_counter = collections.Counter(lemmas)
        token_counter = collections.Counter(tokens)
        bg_counter = collections.Counter(bigrams(tokens))
        tg_counter = collections.Counter(trigrams(tokens))
        content = [t for t in lemmas if t not in GREEK_STOPWORDS]
        content_counter = collections.Counter(content)
        out.append({
            **w,
            'lemma_counter': lemma_counter,
            'lemma_sumw': sum(weights.get(k,1.0)*v for k,v in lemma_counter.items()),
            'token_counter': token_counter,
            'bg_counter': bg_counter,
            'tg_counter': tg_counter,
            'content_counter': content_counter,
            'content_sumw': sum(weights.get(k,1.0)*v for k,v in content_counter.items()),
        })
    return out


def secondary_echoes(scores, pairs, A2, B2, top_n=200, min_score=0.40):
    primary = {(i,j) for i,j,_ in pairs}
    rows=[]
    m,n = scores.shape
    for i in range(m):
        for j in range(n):
            s=float(scores[i,j])
            if s < min_score or (i,j) in primary:
                continue
            # exclude near duplicates to primary within 1 verse both sides
            near=False
            for pi,pj,_ in pairs:
                if abs(i-pi)<=1 and abs(j-pj)<=1:
                    near=True; break
            if near: continue
            rows.append({
                'a_ref':A2[i]['ref'],'b_ref':B2[j]['ref'],'a_idx':i,'b_idx':j,'score':s,
                'tags': ['strong_verbal_echo' if s>=0.7 else 'moderate_verbal_echo']
            })
    rows.sort(key=lambda x:(-x['score'], x['a_idx'], x['b_idx']))
    return rows[:top_n]


def sha256_file(path: Path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def dump_yaml(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,'w',encoding='utf-8') as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False)


def dump_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,'w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False)+'\n')


def dump_csv_gz(path: Path, df: pd.DataFrame):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, 'wt', encoding='utf-8', newline='') as gz:
        df.to_csv(gz, index=False)


def top_content_lemma_deltas(pairs, A2, B2, topn=30):
    # within primary pairs, count lemmas present only on each side (all occurrences)
    only_a=collections.Counter()
    only_b=collections.Counter()
    repl=collections.Counter()
    class_counts=collections.Counter()
    for i,j,s in pairs:
        v1,v2=A2[i],B2[j]
        diff=summarize_pair_diff(v1,v2)
        # classify
        if len(diff['inserted_tokens']) > len(diff['deleted_tokens']) + 4:
            class_counts['b_expands'] += 1
        elif len(diff['deleted_tokens']) > len(diff['inserted_tokens']) + 4:
            class_counts['a_expands'] += 1
        elif diff['replacement_groups']:
            class_counts['substitution'] += 1
        else:
            class_counts['close_match'] += 1
        if any(op['op']=='replace' for op in diff['ops']):
            class_counts['reordering'] += 1
        c1=collections.Counter(v1['lemmas_eff']); c2=collections.Counter(v2['lemmas_eff'])
        keys=set(c1)|set(c2)
        for k in keys:
            a=c1.get(k,0); b=c2.get(k,0)
            if a>b:
                only_a[k]+=a-b
            elif b>a:
                only_b[k]+=b-a
        for a,b in diff['replacement_groups']:
            aa=a.split(); bb=b.split()
            if len(aa)==1 and len(bb)==1 and aa[0] and bb[0]:
                repl[(aa[0],bb[0])] += 1
    return {
        'a_only': only_a.most_common(topn),
        'b_only': only_b.most_common(topn),
        'replacements': [[a,b,c] for (a,b),c in repl.most_common(topn)],
        'pair_class_counts': dict(class_counts)
    }


def order_intervals(pairs, A2, B2):
    rows=[]
    prev=None
    for idx,(i,j,s) in enumerate(pairs):
        if prev is not None:
            pi,pj,ps = prev
            da=i-pi; db=j-pj
            rows.append({
                'from_a_ref':A2[pi]['ref'],'to_a_ref':A2[i]['ref'],
                'from_b_ref':B2[pj]['ref'],'to_b_ref':B2[j]['ref'],
                'delta_a':int(da),'delta_b':int(db),
                'reorder_pressure': int(abs(da-db)),
                'score_from': round(float(ps),6),'score_to': round(float(s),6),
            })
        prev=(i,j,s)
    return rows


def blocks_to_yaml(blocks, pairs, A2, B2, label_a='A', label_b='B'):
    out=[]
    for bi,block in enumerate(blocks, start=1):
        i0,j0,_=block[0]; i1,j1,_=block[-1]
        out.append({
            'block_id': bi,
            f'{label_a.lower()}_span_refs': f"{A2[i0]['ref']}–{A2[i1]['ref']}",
            f'{label_b.lower()}_span_refs': f"{B2[j0]['ref']}–{B2[j1]['ref']}",
            'pair_count': len(block),
            'mean_score': round(float(np.mean([p[2] for p in block])),6),
            'min_score': round(float(np.min([p[2] for p in block])),6),
            'max_score': round(float(np.max([p[2] for p in block])),6),
            'pairs': [{'a_ref':A2[i]['ref'],'b_ref':B2[j]['ref'],'score':round(float(s),6)} for i,j,s in block]
        })
    return out


def build_block_ledger(blocks, A2, B2, label_a='A', label_b='B'):
    out=[]
    total_aprior=0.0; total_bprior=0.0
    for bi,block in enumerate(blocks, start=1):
        i_idx=[p[0] for p in block]; j_idx=[p[1] for p in block]
        i0,i1=min(i_idx),max(i_idx); j0,j1=min(j_idx),max(j_idx)
        a_span=A2[i0:i1+1]; b_span=B2[j0:j1+1]
        matched_a=set(i_idx); matched_b=set(j_idx)
        a_un=[v for k,v in enumerate(a_span,start=i0) if k not in matched_a]
        b_un=[v for k,v in enumerate(b_span,start=j0) if k not in matched_b]
        inserted=deleted=repls=reorders=0
        rationale_ap=[]; rationale_bp=[]
        for i,j,s in block:
            diff=summarize_pair_diff(A2[i], B2[j])
            inserted += len(diff['inserted_tokens'])
            deleted += len(diff['deleted_tokens'])
            repls += len(diff['replacement_groups'])
        # reorder events in block
        prev=None
        for p in block:
            if prev:
                da=p[0]-prev[0]; db=p[1]-prev[1]
                if abs(da-db) >= 2:
                    reorders += 1
            prev=p
        # heuristics
        if len(b_un) > len(a_un):
            rationale_ap.append(f"{label_b} has {len(b_un)-len(a_un)} more unaligned verses inside span; later {label_b} expansion/clustering is easier under {label_a}-prior.")
            rationale_bp.append(f"{label_a} would need omission/non-use of material if {label_b} were prior.")
        elif len(a_un) > len(b_un):
            rationale_bp.append(f"{label_a} has {len(a_un)-len(b_un)} more unaligned verses inside span; later {label_a} expansion/clustering is easier under {label_b}-prior.")
            rationale_ap.append(f"{label_b} would need omission/non-use of material if {label_a} were prior.")
        if inserted>deleted:
            rationale_ap.append(f"More inserted-than-deleted tokens ({inserted}>{deleted}) fit {label_b} expansion from {label_a}.")
            rationale_bp.append(f"{label_a} would have to compress/delete more if derived from {label_b}.")
        elif deleted>inserted:
            rationale_bp.append(f"More deleted-than-inserted tokens ({deleted}>{inserted}) fit {label_a} expansion from {label_b}.")
            rationale_ap.append(f"{label_b} would have to compress/delete more if derived from {label_a}.")
        if repls:
            rationale_ap.append(f"{repls} replacement groups imply targeted redaction under either direction.")
            rationale_bp.append(f"{repls} replacement groups imply targeted redaction under either direction.")
        if reorders:
            rationale_ap.append(f"{reorders} local reorder events increase transformation burden.")
            rationale_bp.append(f"{reorders} local reorder events increase transformation burden.")
        a_prior = round(0.8*len(b_un) + 1.2*len(a_un) + 0.05*inserted + 0.08*deleted + 0.5*repls + 0.3*reorders, 3)
        b_prior = round(0.8*len(a_un) + 1.2*len(b_un) + 0.05*deleted + 0.08*inserted + 0.5*repls + 0.3*reorders, 3)
        total_aprior += a_prior; total_bprior += b_prior
        out.append({
            'block_id': bi,
            f'{label_a.lower()}_span_refs': f"{A2[i0]['ref']}–{A2[i1]['ref']}",
            f'{label_b.lower()}_span_refs': f"{B2[j0]['ref']}–{B2[j1]['ref']}",
            'matched_pairs': len(block),
            f'{label_a.lower()}_unaligned_count': len(a_un),
            f'{label_b.lower()}_unaligned_count': len(b_un),
            'inserted_tokens_a_to_b': inserted,
            'deleted_tokens_a_to_b': deleted,
            'replacement_groups': repls,
            'reorder_events': reorders,
            f'hypothesis_{label_a.lower()}_prior_numeric_burden': a_prior,
            f'hypothesis_{label_b.lower()}_prior_numeric_burden': b_prior,
            f'hypothesis_{label_a.lower()}_prior_rationales': rationale_ap,
            f'hypothesis_{label_b.lower()}_prior_rationales': rationale_bp,
        })
    return out, {
        f'{label_a.lower()}_prior_{label_b}_uses_{label_a}': round(total_aprior,3),
        f'{label_b.lower()}_prior_{label_a}_uses_{label_b}': round(total_bprior,3),
    }


def score_summary(scores):
    vals = [float(s) for s in scores]
    return {
        'mean': round(float(np.mean(vals)),6) if vals else None,
        'median': round(float(np.median(vals)),6) if vals else None,
        'min': round(float(np.min(vals)),6) if vals else None,
        'max': round(float(np.max(vals)),6) if vals else None,
        'ge_0.80': int(sum(v>=0.8 for v in vals)),
        'ge_0.70': int(sum(v>=0.7 for v in vals)),
        'ge_0.60': int(sum(v>=0.6 for v in vals)),
        'ge_0.50': int(sum(v>=0.5 for v in vals)),
        'lt_0.40': int(sum(v<0.4 for v in vals)),
    }


def source_metadata_for_books(book_names):
    md = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'books': {},
        'notes': {
            'canonical_text_base': 'Faithlife SBLGNT text files downloaded locally',
            'apparatus': 'Faithlife SBLGNT apparatus XML downloaded locally',
            'morphology': 'MorphGNT local files downloaded locally',
            'text_critical_default_policy': 'double-bracketed text removed from default surface layer; if surface is empty after removal, lemma layer is also excluded by default',
        }
    }
    for b in book_names:
        info=BOOKS_INFO[b]
        textp=src_base/'sblgnt'/'text'/info['text']
        appp=src_base/'sblgntapp'/'xml'/info['app']
        morphp=src_base/'morphgnt'/info['morph']
        md['books'][b] = {
            'text_file': info['text'],
            'text_sha256': sha256_file(textp),
            'apparatus_file': info['app'],
            'apparatus_sha256': sha256_file(appp) if appp.exists() else None,
            'morph_file': info['morph'],
            'morph_sha256': sha256_file(morphp) if morphp.exists() else None,
            'actual_vs_canonical': canonical_slot_info(books[b]),
        }
    return md


def matched_subset(verses, idxs):
    idxs=set(idxs)
    return [v for k,v in enumerate(verses) if k in idxs]


def count_lemma(verses, lemma):
    return sum(v['lemmas'].count(lemma) for v in verses)


def present_indicative_ratio(verses):
    total=0; pi=0
    for v in verses:
        for t in v['morph_tokens']:
            parsing=t['parsing']
            if len(parsing)>=4 and parsing[3] in 'IDSONP':  # verb forms
                total += 1
                if parsing[1]=='P' and parsing[3]=='I':
                    pi += 1
    return round(pi/total,4) if total else None


def full_matrix_df(A2, B2, scores):
    m,n=scores.shape
    a_refs=np.repeat([v['ref'] for v in A2], n)
    b_refs=np.tile([v['ref'] for v in B2], m)
    return pd.DataFrame({
        'a_ref': a_refs,
        'b_ref': b_refs,
        'score': scores.reshape(-1),
    })


def build_mask_from_scores(top_scores, top_idx, primary_threshold=0.355, bridge_threshold=None):
    n=len(top_scores)
    masked=np.array(top_scores>=primary_threshold)
    reason=np.where(masked,'score_ge_threshold','unmasked')
    if bridge_threshold is None:
        bridge_threshold = primary_threshold*0.92
    # fill isolated gaps i where i-1 and i+1 masked and current score >= bridge_threshold
    added=True
    while added:
        added=False
        for i in range(1,n-1):
            if masked[i]:
                continue
            if masked[i-1] and masked[i+1] and top_scores[i] >= bridge_threshold:
                # require nearby top Mark indices
                if abs(int(top_idx[i-1])-int(top_idx[i]))<=4 and abs(int(top_idx[i+1])-int(top_idx[i]))<=4:
                    masked[i]=True; reason[i]='local_bridge'; added=True
    return masked, reason


def resolve_refspec(refspec: str):
    m = re.match(r'^(?P<book>[1-3]?[A-Za-z]+)\s+(?P<chap>\d+):(?P<v1>\d+)(?:-(?:(?P<chap2>\d+):)?(?P<v2>\d+))?$', refspec.strip())
    if not m:
        raise ValueError(f"Unsupported refspec: {refspec}")
    book = m.group('book')
    chap = int(m.group('chap')); v1 = int(m.group('v1'))
    chap2 = int(m.group('chap2')) if m.group('chap2') else chap
    v2 = int(m.group('v2')) if m.group('v2') else v1
    selected=[]
    for v in books[book]:
        if chap == chap2:
            if v['chapter']==chap and v1 <= v['verse'] <= v2:
                selected.append(v)
        else:
            # rare; include from chap:v1 to chap2:v2
            if (v['chapter'] > chap and v['chapter'] < chap2) or \
               (v['chapter']==chap and v['verse']>=v1) or \
               (v['chapter']==chap2 and v['verse']<=v2):
                selected.append(v)
    return selected


def aggregate_verses(verses, book=None, refspec=None):
    tokens = sum((v['tokens_default'] for v in verses), [])
    lemmas = sum(((v['lemmas'] if v['text_norm_default'] else []) for v in verses), [])
    agg = {
        'book': book or verses[0]['book'],
        'ref': refspec or (verses[0]['ref'] if len(verses)==1 else f"{verses[0]['ref']}–{verses[-1]['ref']}"),
        'tokens_default': tokens,
        'lemmas': lemmas,
        'text_raw': ' '.join(v['text_raw'] for v in verses),
        'text_norm_default': ' '.join(v['text_norm_default'] for v in verses if v['text_norm_default']),
        'flags': {
            'cheap_shared': any(v['flags']['cheap_shared'] for v in verses),
            'citation_formula': any(v['flags']['citation_formula'] for v in verses),
            'bracketed_text': any(v['flags']['bracketed_text'] for v in verses),
        },
        'morph_tokens': sum((v['morph_tokens'] for v in verses), []),
        'variant_notes': sum((v['variant_notes'] for v in verses), []),
        'variant_note_count': sum(v['variant_note_count'] for v in verses),
    }
    return agg


def prep_agg_for_metrics(agg):
    lemmas = agg['lemmas']
    tokens = agg['tokens_default']
    lemma_counter = collections.Counter(lemmas)
    token_counter = collections.Counter(tokens)
    bg_counter = collections.Counter(bigrams(tokens))
    tg_counter = collections.Counter(trigrams(tokens))
    content = [t for t in lemmas if t not in GREEK_STOPWORDS]
    content_counter = collections.Counter(content)
    return {
        **agg,
        'lemmas_eff': lemmas,
        'lemma_counter': lemma_counter,
        'lemma_sumw': sum(weights_jtea.get(k,1.0)*v for k,v in lemma_counter.items()),
        'token_counter': token_counter,
        'bg_counter': bg_counter,
        'tg_counter': tg_counter,
        'content_counter': content_counter,
        'content_sumw': sum(weights_jtea.get(k,1.0)*v for k,v in content_counter.items()),
    }


def formula_risk_for_case(source_ref, target_ref, feature_text='', source_text='', target_text=''):
    refs = []
    for spec in [source_ref, target_ref]:
        try:
            refs.extend(resolve_refspec(spec))
        except Exception:
            pass
    citation = any(v['flags']['citation_formula'] for v in refs)
    cheap = any(v['flags']['cheap_shared'] for v in refs)
    # liturgical/formulaic cues
    texts = ' '.join([normalize_greek(feature_text), normalize_greek(source_text), normalize_greek(target_text)])
    if 'αναμνησιν' in texts or 'ποτηριον' in texts or 'σωμα' in texts:
        return 'high', 'liturgical_formula'
    if citation:
        return 'high', 'scriptural_citation_formula'
    if 'μισθου αυτου' in texts:
        return 'low', 'non_formulaic_jesus_saying_segment'
    if cheap:
        return 'medium', 'short_or_formulaic_context'
    return 'low', 'no_primary_formula_flag'


def support_label(score, max_exact_run_len, shared_content_count=None):
    if score >= 0.30 or max_exact_run_len >= 5:
        return 'strong'
    if score >= 0.15 or max_exact_run_len >= 3:
        return 'medium'
    return 'weak'


def philological_strength(case_id):
    if '1tim_5_18' in case_id:
        return 'strong'
    if '1cor_11' in case_id:
        return 'strong'
    if 'james_5_12' in case_id:
        return 'medium'
    if '2tim_2_12' in case_id:
        return 'medium'
    if '1john_3_13' in case_id:
        return 'medium'
    return 'medium'


def formula_risk_row(row):
    refs=[]
    for key in ['source_ref','target_ref']:
        r=row.get(key)
        if isinstance(r,str) and r in flag_map:
            refs.append(flag_map[r])
    citation = any(r['citation_formula'] for r in refs)
    cheap = any(r['cheap_shared'] for r in refs)
    layer = row.get('layer','')
    text = normalize_greek(str(row.get('max_exact_run','')))
    src_book = row.get('source_book','')
    tgt_book = row.get('target_book','')
    if citation:
        return 'high'
    if src_book=='1Cor' and tgt_book=='Luke':
        return 'high'
    if 'μισθου' in str(row.get('max_exact_run','')) or 'μισθου' in str(row.get('source_text','')) or 'μισθου' in str(row.get('target_text','')):
        return 'low'
    if cheap:
        return 'medium'
    return 'low'


def augment_secondary_tags(sec, lenA, lenB):
    out=[]
    for row in sec:
        r=dict(row)
        tags=list(r.get('tags',[]))
        if abs((r['a_idx']/max(1,lenA)) - (r['b_idx']/max(1,lenB))) > 0.07:
            if 'nonlocal_reorder' not in tags:
                tags.append('nonlocal_reorder')
        r['tags']=tags
        out.append(r)
    return out

