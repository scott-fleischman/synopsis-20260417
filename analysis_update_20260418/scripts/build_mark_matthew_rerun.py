
from __future__ import annotations
from pathlib import Path
import collections
import pandas as pd
import numpy as np
import common

MM_PARAMS = {
    'primary_chain_min_score': 0.25,
    'gap_penalty': 0.05,
    'loose_gap_mark': 4,
    'loose_gap_matt': 7,
    'tight_gap_mark': 3,
    'tight_gap_matt': 3,
    'secondary_echo_min_score': 0.45,
    'secondary_echo_top_n': 250,
}

def main(base: Path | None = None):
    if base is None:
        base = Path(__file__).resolve().parents[1]
    common.src_base = base / 'sources' / 'repro_sources'
    common.books = {b: common.parse_book(b) for b in ['Mark','Matt']}
    A_mm, B_mm, W_mm = common.prep_books_pair('Mark','Matt')
    scores_mm_raw, _ = common.compute_score_matrix(A_mm, B_mm, W_mm, with_details=False)
    scores_mm = common.contextual_adjust_fast(scores_mm_raw)
    pairs_mm, chain_score_mm = common.align_primary_chain(
        scores_mm, min_match=MM_PARAMS['primary_chain_min_score'], gap_penalty=MM_PARAMS['gap_penalty'])
    loose_mm, tight_mm = common.segment_pairs(
        pairs_mm,
        loose_a=MM_PARAMS['loose_gap_mark'], loose_b=MM_PARAMS['loose_gap_matt'],
        tight_a=MM_PARAMS['tight_gap_mark'], tight_b=MM_PARAMS['tight_gap_matt'])

    pair_rows_mm=[]; detailed_mm=[]
    for rank,(i,j,s) in enumerate(pairs_mm, start=1):
        va,vb=A_mm[i],B_mm[j]
        pm = common.pair_metrics_fast(va,vb,W_mm)
        diff = common.summarize_pair_diff(va,vb)
        pair_rows_mm.append({
            'rank_in_chain': rank,
            'mark_idx': i, 'matt_idx': j,
            'mark_ref': va['ref'], 'matt_ref': vb['ref'],
            'score': round(float(s),6),
            'lemma_dice': round(pm['lemma_dice'],6),
            'token_dice': round(pm['token_dice'],6),
            'bigram_dice': round(pm['bigram_dice'],6),
            'trigram_dice': round(pm['trigram_dice'],6),
            'lcs_len': pm['lcs_len'],
            'lcs_ratio': round(pm['lcs_ratio'],6),
            'content_dice': round(pm['content_dice'],6),
            'mark_variant_note_count': va['variant_note_count'],
            'matt_variant_note_count': vb['variant_note_count'],
            'mark_bracketed': va['flags']['bracketed_text'],
            'matt_bracketed': vb['flags']['bracketed_text'],
            'mark_text': va['text_raw'],
            'matt_text': vb['text_raw'],
        })
        detailed_mm.append({
            **pair_rows_mm[-1],
            'mark_variant_notes': va['variant_notes'],
            'matt_variant_notes': vb['variant_notes'],
            'diff_ops': diff['ops'],
            'inserted_tokens': diff['inserted_tokens'],
            'deleted_tokens': diff['deleted_tokens'],
            'replacement_groups': diff['replacement_groups'],
        })
    pair_df_mm = pd.DataFrame(pair_rows_mm)

    top20_mark_to_matt = common.top_hits_df(A_mm, B_mm, scores_mm, topn=20, direction='A_to_B')
    top20_matt_to_mark = common.top_hits_df(A_mm, B_mm, scores_mm, topn=20, direction='B_to_A')
    sec_mm = common.augment_secondary_tags(
        common.secondary_echoes(scores_mm, pairs_mm, A_mm, B_mm, top_n=MM_PARAMS['secondary_echo_top_n'], min_score=MM_PARAMS['secondary_echo_min_score']),
        len(A_mm), len(B_mm))
    order_mm = common.order_intervals(pairs_mm, A_mm, B_mm)
    blocks_loose_yaml_mm = common.blocks_to_yaml(loose_mm, pairs_mm, A_mm, B_mm, label_a='Mark', label_b='Matt')
    blocks_tight_yaml_mm = common.blocks_to_yaml(tight_mm, pairs_mm, A_mm, B_mm, label_a='Mark', label_b='Matt')
    ledger_mm, burden_totals_mm = common.build_block_ledger(loose_mm, A_mm, B_mm, label_a='Mark', label_b='Matt')
    lemma_delta_mm = common.top_content_lemma_deltas(pairs_mm, A_mm, B_mm, topn=30)
    mark_matched = common.matched_subset(A_mm, [i for i,_,_ in pairs_mm])
    matt_matched = common.matched_subset(B_mm, [j for _,j,_ in pairs_mm])
    style_mm = {
        'matched_mark_euthys': common.count_lemma(mark_matched,'ευθυσ'),
        'matched_matt_euthys': common.count_lemma(matt_matched,'ευθυσ'),
        'matched_mark_kingdom_god': sum(v['text_norm_default'].count('βασιλεια του θεου') for v in mark_matched),
        'matched_mark_kingdom_heaven': sum(v['text_norm_default'].count('βασιλεια των ουρανων') for v in mark_matched),
        'matched_matt_kingdom_god': sum(v['text_norm_default'].count('βασιλεια του θεου') for v in matt_matched),
        'matched_matt_kingdom_heaven': sum(v['text_norm_default'].count('βασιλεια των ουρανων') for v in matt_matched),
        'matched_mark_present_indicative_ratio': common.present_indicative_ratio(mark_matched),
        'matched_matt_present_indicative_ratio': common.present_indicative_ratio(matt_matched),
    }
    slots_mm = {'Mark': common.canonical_slot_info(common.books['Mark']), 'Matt': common.canonical_slot_info(common.books['Matt'])}

    out_dir = base / 'reruns' / 'mark_matthew_rerun_robust'
    (out_dir / 'data').mkdir(parents=True, exist_ok=True)

    common.dump_yaml(out_dir/'data'/'00_source_metadata.yaml', common.source_metadata_for_books(['Mark','Matt']))

    rows=[]
    for b in ['Mark','Matt']:
        for idx,v in enumerate(common.books[b]):
            rows.append({
                'book':b,'idx':idx,'ref':v['ref'],
                'short_verse':v['flags']['short_verse'],
                'citation_formula':v['flags']['citation_formula'],
                'bracketed_text':v['flags']['bracketed_text'],
                'text_critical_empty_after_default':v['flags']['text_critical_empty_after_default'],
                'cheap_shared':v['flags']['cheap_shared'],
                'variant_note_count':v['variant_note_count'],
                'token_count_default':v['token_count_default'],
                'token_count_full':v['token_count_full'],
                'text_norm_default':v['text_norm_default'],
            })
    pd.DataFrame(rows).to_csv(out_dir/'data'/'01_negative_space_flags.csv', index=False)

    common.dump_csv_gz(out_dir/'data'/'02_verse_similarity_full.csv.gz', common.full_matrix_df(A_mm, B_mm, scores_mm))
    top20_mark_to_matt.to_csv(out_dir/'data'/'03_verse_similarity_top20_mark_to_matt.csv', index=False)
    top20_matt_to_mark.to_csv(out_dir/'data'/'04_verse_similarity_top20_matt_to_mark.csv', index=False)
    pair_df_mm.to_csv(out_dir/'data'/'07_primary_chain_pairs.csv', index=False)
    common.dump_jsonl(out_dir/'data'/'08_primary_chain_pairs_detailed.jsonl', detailed_mm)
    common.dump_yaml(out_dir/'data'/'09_loose_blocks.yaml', blocks_loose_yaml_mm)
    common.dump_yaml(out_dir/'data'/'10_tight_blocks.yaml', blocks_tight_yaml_mm)
    common.dump_yaml(out_dir/'data'/'11_order_intervals.yaml', order_mm)
    common.dump_yaml(out_dir/'data'/'12_secondary_echoes.yaml', sec_mm)
    common.dump_yaml(out_dir/'data'/'13_variants_by_primary_pair.yaml', common.attach_variants_for_pairs(pairs_mm, A_mm, B_mm))
    common.dump_yaml(out_dir/'data'/'14_direction_ledger_by_loose_block.yaml', ledger_mm)
    common.dump_yaml(out_dir/'data'/'15_direction_burden_totals.yaml', burden_totals_mm)

    summary_mm = {
        'project': 'Mark–Matthew literary dependence rerun with reproducibility patch',
        'method_summary': {
            'text_base': 'Local SBLGNT text + apparatus + MorphGNT',
            'updates_in_this_rerun': [
                'committed-style runnable scripts included in package',
                'actual verse rows separated from canonical verse-slot counts',
                'double-bracketed text excluded from default lemma layer when surface becomes empty',
                'score-threshold and gap-penalty sensitivity grid added',
                'Mark 16:9–20 sensitivity run added',
                'claim/evidence mapping added at package level',
            ],
            'default_parameters': MM_PARAMS,
        },
        'global_metrics': {
            'matched_pair_count': len(pairs_mm),
            'mark_total_verse_count': len(common.books['Mark']),
            'matt_total_verse_count': len(common.books['Matt']),
            'mark_matched_pct': round(len({i for i,_,_ in pairs_mm})/len(common.books['Mark']),4),
            'matt_matched_pct': round(len({j for _,j,_ in pairs_mm})/len(common.books['Matt']),4),
            'loose_block_count': len(loose_mm),
            'tight_block_count': len(tight_mm),
            'secondary_echo_count': len(sec_mm),
        },
        'global_style': style_mm,
        'pair_score_summary': common.score_summary([s for _,_,s in pairs_mm]),
        'pair_class_counts': lemma_delta_mm['pair_class_counts'],
        'burden_totals': burden_totals_mm,
        'actual_vs_canonical': slots_mm,
        'notes': [
            'This rerun is close to, but not identical with, the earlier thread artifact because the default text-critical handling is stricter and the package now exposes sensitivity layers rather than a single opaque default.',
            'The burden totals are heuristic audit numbers, not probabilities.',
        ]
    }
    common.dump_yaml(out_dir/'data'/'16_global_summary.yaml', summary_mm)

    pd.DataFrame([{
        'block_id':b['block_id'],'mark_span_refs':b['mark_span_refs'],'matt_span_refs':b['matt_span_refs'],
        'pair_count':b['pair_count'],'mean_score':b['mean_score']
    } for b in blocks_loose_yaml_mm]).to_csv(out_dir/'data'/'17_macro_block_table.csv', index=False)
    pd.DataFrame([{
        'block_id':b['block_id'],'mark_span_refs':b['mark_span_refs'],'matt_span_refs':b['matt_span_refs'],
        'pair_count':b['pair_count'],'mean_score':b['mean_score']
    } for b in blocks_tight_yaml_mm]).to_csv(out_dir/'data'/'18_micro_block_table.csv', index=False)

    flat_rows=[]
    for rec in detailed_mm:
        for opi,op in enumerate(rec['diff_ops'], start=1):
            flat_rows.append({
                'rank_in_chain': rec['rank_in_chain'],
                'mark_ref': rec['mark_ref'],
                'matt_ref': rec['matt_ref'],
                'score': rec['score'],
                'op_index': opi,
                'op': op['op'],
                'mark_segment': op['a'],
                'matt_segment': op['b'],
            })
    pd.DataFrame(flat_rows).to_csv(out_dir/'data'/'19_pair_diffs_flat.tsv', index=False, sep='\t')
    common.dump_yaml(out_dir/'data'/'20_top_lemma_deltas.yaml', {
        'top_mark_only_content_lemmas_in_primary_pairs': lemma_delta_mm['a_only'],
        'top_matt_only_content_lemmas_in_primary_pairs': lemma_delta_mm['b_only'],
        'top_lemma_replacement_pairs': lemma_delta_mm['replacements'],
        'pair_class_counts': lemma_delta_mm['pair_class_counts'],
    })
    common.dump_yaml(out_dir/'data'/'21_selected_secondary_echoes.yaml', sec_mm[:25])

    # sensitivity run
    def prep_verse_features_include_bracketed(verses, weights):
        out=[]
        for v in verses:
            lemmas = v['lemmas'] if v['lemmas'] else v['tokens_full']
            lemma_counter = collections.Counter(lemmas)
            token_counter = collections.Counter(v['tokens_full'])
            bg_counter = collections.Counter(common.bigrams(v['tokens_full']))
            tg_counter = collections.Counter(common.trigrams(v['tokens_full']))
            content = [t for t in lemmas if t not in common.GREEK_STOPWORDS]
            content_counter = collections.Counter(content)
            out.append({
                **v,'lemmas_eff':lemmas,'lemma_counter':lemma_counter,'lemma_sumw':sum(weights.get(k,1.0)*v for k,v in lemma_counter.items()),
                'token_counter':token_counter,'bg_counter':bg_counter,'tg_counter':tg_counter,
                'content_counter':content_counter,'content_sumw':sum(weights.get(k,1.0)*v for k,v in content_counter.items()),
                'tokens_default': v['tokens_full'],
            })
        return out

    A_mm_full = prep_verse_features_include_bracketed(common.books['Mark'], W_mm)
    B_mm_full = prep_verse_features_include_bracketed(common.books['Matt'], W_mm)
    scores_mm_full, _ = common.compute_score_matrix(A_mm_full, B_mm_full, W_mm, with_details=False)
    scores_mm_full = common.contextual_adjust_fast(scores_mm_full)
    pairs_mm_full,_ = common.align_primary_chain(scores_mm_full, min_match=MM_PARAMS['primary_chain_min_score'], gap_penalty=MM_PARAMS['gap_penalty'])
    common.dump_yaml(out_dir/'data'/'22_sensitivity_mark_ending.yaml', {
        'default_exclude_double_bracketed_from_surface_and_empty_lemma': {
            'pair_count': len(pairs_mm),
            'last_five_pairs': [{'mark_ref':A_mm[i]['ref'],'matt_ref':B_mm[j]['ref'],'score':round(float(s),6)} for i,j,s in pairs_mm[-5:]],
            'mark16_9_20_aligned_pairs': [ {'mark_ref':A_mm[i]['ref'],'matt_ref':B_mm[j]['ref'],'score':round(float(s),6)} for i,j,s in pairs_mm if A_mm[i]['ref'].startswith('Mark 16:') and int(A_mm[i]['ref'].split(':')[1])>=9 ],
        },
        'include_bracketed_surface_and_lemma': {
            'pair_count': len(pairs_mm_full),
            'last_five_pairs': [{'mark_ref':A_mm_full[i]['ref'],'matt_ref':B_mm_full[j]['ref'],'score':round(float(s),6)} for i,j,s in pairs_mm_full[-5:]],
            'mark16_9_20_aligned_pairs': [ {'mark_ref':A_mm_full[i]['ref'],'matt_ref':B_mm_full[j]['ref'],'score':round(float(s),6)} for i,j,s in pairs_mm_full if A_mm_full[i]['ref'].startswith('Mark 16:') and int(A_mm_full[i]['ref'].split(':')[1])>=9 ],
        },
        'observation': 'Under the current chain threshold, the primary chain still terminates before Mark 16:9–20; the text-critical sensitivity run affects candidate space more than final chain alignment.'
    })
    grid_rows=[]
    for th in [0.24,0.25,0.26,0.27]:
        for gp in [0.04,0.05,0.06]:
            pairs,_=common.align_primary_chain(scores_mm, min_match=th, gap_penalty=gp)
            loose,_=common.segment_pairs(pairs, loose_a=MM_PARAMS['loose_gap_mark'], loose_b=MM_PARAMS['loose_gap_matt'], tight_a=MM_PARAMS['tight_gap_mark'], tight_b=MM_PARAMS['tight_gap_matt'])
            grid_rows.append({'primary_chain_min_score':th,'gap_penalty':gp,'pair_count':len(pairs),'loose_block_count':len(loose)})
    pd.DataFrame(grid_rows).to_csv(out_dir/'data'/'23_sensitivity_score_grid.csv', index=False)
    common.dump_yaml(out_dir/'data'/'24_actual_vs_canonical_slots.yaml', slots_mm)

if __name__ == '__main__':
    main()
