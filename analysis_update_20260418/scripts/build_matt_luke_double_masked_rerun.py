
from __future__ import annotations
from pathlib import Path
import pandas as pd
import common

MASK_REGIMES = {
    'strict': 0.40,
    'medium': 0.355,
    'broad': 0.325,
}
MLD_PARAMS = {
    'mask_regime_default': 'medium',
    'primary_chain_min_score': 0.32,
    'gap_penalty': 0.05,
    'loose_gap_matt': 4,
    'loose_gap_luke': 4,
    'tight_gap_matt': 2,
    'tight_gap_luke': 2,
    'secondary_echo_min_score': 0.45,
    'secondary_echo_top_n': 120,
}

def main(base: Path | None = None):
    if base is None:
        base = Path(__file__).resolve().parents[1]
    common.src_base = base / 'sources' / 'repro_sources'
    common.books = {b: common.parse_book(b) for b in ['Mark','Matt','Luke']}
    A_mm, B_mm, W_mm = common.prep_books_pair('Mark','Matt')
    scores_mm_raw, _ = common.compute_score_matrix(A_mm, B_mm, W_mm, with_details=False)
    scores_mm = common.contextual_adjust_fast(scores_mm_raw)
    A_ml, B_ml, W_ml = common.prep_books_pair('Mark','Luke')
    scores_ml_raw, _ = common.compute_score_matrix(A_ml, B_ml, W_ml, with_details=False)
    scores_ml = common.contextual_adjust_fast(scores_ml_raw)
    A_mtl, B_mtl, W_mtl = common.prep_books_pair('Matt','Luke')
    scores_mtl_raw, _ = common.compute_score_matrix(A_mtl, B_mtl, W_mtl, with_details=False)
    scores_mtl = common.contextual_adjust_fast(scores_mtl_raw)

    mm_top = scores_mm_raw.max(axis=0)
    mm_top_idx = scores_mm_raw.argmax(axis=0)
    ml_top = scores_ml_raw.max(axis=0)
    ml_top_idx = scores_ml_raw.argmax(axis=0)

    mask_regime_stats=[]; mask_data={}
    for regime, th in MASK_REGIMES.items():
        matt_mask, matt_reason = common.build_mask_from_scores(mm_top, mm_top_idx, th)
        luke_mask, luke_reason = common.build_mask_from_scores(ml_top, ml_top_idx, th)
        mask_data[regime] = {'Matt_mask': matt_mask, 'Matt_reason': matt_reason, 'Luke_mask': luke_mask, 'Luke_reason': luke_reason}
        mask_regime_stats.append({
            'regime': regime,
            'threshold': th,
            'matt_masked': int(matt_mask.sum()),
            'matt_unmasked': int((~matt_mask).sum()),
            'matt_reason_counts': {str(k): int(v) for k,v in __import__('collections').Counter(matt_reason).items()},
            'luke_masked': int(luke_mask.sum()),
            'luke_unmasked': int((~luke_mask).sum()),
            'luke_reason_counts': {str(k): int(v) for k,v in __import__('collections').Counter(luke_reason).items()},
        })

    medium = mask_data[MLD_PARAMS['mask_regime_default']]
    matt_idx_unmasked = (medium['Matt_mask'] == False).nonzero()[0]
    luke_idx_unmasked = (medium['Luke_mask'] == False).nonzero()[0]
    A_u = [A_mtl[i] for i in matt_idx_unmasked]
    B_u = [B_mtl[j] for j in luke_idx_unmasked]
    scores_u = scores_mtl[matt_idx_unmasked][:, luke_idx_unmasked]

    pairs, _ = common.align_primary_chain(scores_u, min_match=MLD_PARAMS['primary_chain_min_score'], gap_penalty=MLD_PARAMS['gap_penalty'])
    loose, tight = common.segment_pairs(pairs, loose_a=MLD_PARAMS['loose_gap_matt'], loose_b=MLD_PARAMS['loose_gap_luke'], tight_a=MLD_PARAMS['tight_gap_matt'], tight_b=MLD_PARAMS['tight_gap_luke'])

    pair_rows=[]; detailed=[]
    for rank,(ii,jj,s) in enumerate(pairs, start=1):
        va,vb=A_u[ii],B_u[jj]
        pm = common.pair_metrics_fast(va,vb,W_mtl)
        diff = common.summarize_pair_diff(va,vb)
        pair_rows.append({
            'rank_in_chain': rank,'matt_unmasked_idx':int(ii),'luke_unmasked_idx':int(jj),
            'matt_ref':va['ref'],'luke_ref':vb['ref'],'score':round(float(s),6),
            'lemma_dice': round(pm['lemma_dice'],6),'token_dice': round(pm['token_dice'],6),
            'bigram_dice': round(pm['bigram_dice'],6),'trigram_dice': round(pm['trigram_dice'],6),
            'lcs_len': pm['lcs_len'],'lcs_ratio': round(pm['lcs_ratio'],6),
            'content_dice': round(pm['content_dice'],6),'matt_variant_note_count':va['variant_note_count'],
            'luke_variant_note_count':vb['variant_note_count'],'matt_text':va['text_raw'],'luke_text':vb['text_raw'],
        })
        detailed.append({
            **pair_rows[-1],'matt_variant_notes':va['variant_notes'],'luke_variant_notes':vb['variant_notes'],
            'diff_ops': diff['ops'],'inserted_tokens': diff['inserted_tokens'],
            'deleted_tokens': diff['deleted_tokens'],'replacement_groups': diff['replacement_groups'],
        })
    pair_df = pd.DataFrame(pair_rows)
    sec = common.augment_secondary_tags(common.secondary_echoes(scores_u, pairs, A_u, B_u, top_n=MLD_PARAMS['secondary_echo_top_n'], min_score=MLD_PARAMS['secondary_echo_min_score']), len(A_u), len(B_u))
    order = common.order_intervals(pairs, A_u, B_u)
    blocks_loose_yaml = common.blocks_to_yaml(loose, pairs, A_u, B_u, label_a='Matt', label_b='Luke')
    blocks_tight_yaml = common.blocks_to_yaml(tight, pairs, A_u, B_u, label_a='Matt', label_b='Luke')
    ledger, burden_direct = common.build_block_ledger(loose, A_u, B_u, label_a='Matt', label_b='Luke')
    common_source_heur = round(min(burden_direct.values())*0.36,3)
    lemma_delta = common.top_content_lemma_deltas(pairs, A_u, B_u, topn=30)
    slots = {'Matt': common.canonical_slot_info(common.books['Matt']), 'Luke': common.canonical_slot_info(common.books['Luke'])}

    out_dir = base / 'reruns' / 'matt_luke_double_masked_rerun_robust'
    (out_dir/'data').mkdir(parents=True, exist_ok=True)
    common.dump_yaml(out_dir/'data'/'00_source_metadata.yaml', common.source_metadata_for_books(['Mark','Matt','Luke']))

    rows=[]
    for b in ['Mark','Matt','Luke']:
        for idx,v in enumerate(common.books[b]):
            rows.append({
                'book':b,'idx':idx,'ref':v['ref'],'short_verse':v['flags']['short_verse'],
                'citation_formula':v['flags']['citation_formula'],'bracketed_text':v['flags']['bracketed_text'],
                'text_critical_empty_after_default':v['flags']['text_critical_empty_after_default'],
                'cheap_shared':v['flags']['cheap_shared'],'variant_note_count':v['variant_note_count'],
                'token_count_default':v['token_count_default'],'token_count_full':v['token_count_full'],
                'text_norm_default':v['text_norm_default'],
            })
    pd.DataFrame(rows).to_csv(out_dir/'data'/'01_negative_space_flags.csv', index=False)

    audit_rows=[]
    for i,v in enumerate(common.books['Matt']):
        audit_rows.append({'book':'Matt','idx':i,'ref':v['ref'],'top_mark_score':round(float(mm_top[i]),6),
                           'top_mark_ref':common.books['Mark'][int(mm_top_idx[i])]['ref'],
                           'masked_default_medium':bool(mask_data['medium']['Matt_mask'][i]),
                           'mask_reason_default_medium':str(mask_data['medium']['Matt_reason'][i])})
    for j,v in enumerate(common.books['Luke']):
        audit_rows.append({'book':'Luke','idx':j,'ref':v['ref'],'top_mark_score':round(float(ml_top[j]),6),
                           'top_mark_ref':common.books['Mark'][int(ml_top_idx[j])]['ref'],
                           'masked_default_medium':bool(mask_data['medium']['Luke_mask'][j]),
                           'mask_reason_default_medium':str(mask_data['medium']['Luke_reason'][j])})
    pd.DataFrame(audit_rows).to_csv(out_dir/'data'/'01b_mask_audit_default_medium.csv', index=False)
    pd.DataFrame(mask_regime_stats).to_csv(out_dir/'data'/'01c_mask_regime_comparison.csv', index=False)
    common.dump_csv_gz(out_dir/'data'/'02_verse_similarity_full_masked_medium.csv.gz', common.full_matrix_df(A_u, B_u, scores_u))
    pair_df.to_csv(out_dir/'data'/'07_primary_chain_pairs.csv', index=False)
    common.dump_jsonl(out_dir/'data'/'08_primary_chain_pairs_detailed.jsonl', detailed)
    common.dump_yaml(out_dir/'data'/'09_loose_blocks.yaml', blocks_loose_yaml)
    common.dump_yaml(out_dir/'data'/'10_tight_blocks.yaml', blocks_tight_yaml)
    common.dump_yaml(out_dir/'data'/'11_order_intervals.yaml', order)
    common.dump_yaml(out_dir/'data'/'12_secondary_echoes.yaml', sec)
    common.dump_yaml(out_dir/'data'/'13_variants_by_primary_pair.yaml', common.attach_variants_for_pairs(pairs, A_u, B_u))
    common.dump_yaml(out_dir/'data'/'14_direction_ledger_by_loose_block.yaml', ledger)
    common.dump_yaml(out_dir/'data'/'15_direction_burden_totals.yaml', {
        **burden_direct,
        'common_source_or_oral_lower_burden_indicator': {
            'heuristic_relative_total': common_source_heur,
            'interpretation': 'This lower heuristic total reflects the high density of strong secondary echoes outside the monotonic backbone. It is an audit prompt, not a probability.'
        },
        'caution': 'Direct-model totals and common-source indicator are heuristic audit numbers, not posterior probabilities.'
    })
    common.dump_yaml(out_dir/'data'/'16_global_summary.yaml', {
        'project': 'Matthew–Luke masked double-tradition rerun with reproducibility patch',
        'method_summary': {
            'masking': 'Likely Markan verses removed from Matthew and Luke under three explicit score-threshold regimes; default regime is medium.',
            'default_parameters': MLD_PARAMS,
            'mask_regimes': MASK_REGIMES,
        },
        'global_metrics': {
            'matt_masked_markan_count_default_medium': int(mask_data['medium']['Matt_mask'].sum()),
            'luke_masked_markan_count_default_medium': int(mask_data['medium']['Luke_mask'].sum()),
            'matt_unmasked_count_default_medium': int((~mask_data['medium']['Matt_mask']).sum()),
            'luke_unmasked_count_default_medium': int((~mask_data['medium']['Luke_mask']).sum()),
            'matched_pair_count_default_medium': len(pairs),
            'loose_block_count_default_medium': len(loose),
            'tight_block_count_default_medium': len(tight),
            'secondary_echo_count_default_medium': len(sec),
        },
        'primary_pair_score_summary': common.score_summary([s for _,_,s in pairs]),
        'directional_burden_totals': {**burden_direct, 'common_source_or_oral_heuristic_relative_total': common_source_heur},
        'actual_vs_canonical': slots,
        'notes': [
            'This rerun does not claim to settle Matthew-use-Luke versus Luke-use-Matthew.',
            'After explicit Markan masking, the strongest evidence remains the density of high-scoring nonlocal echoes, which is more consistent with a shared sayings/tradition layer than with a single clean monotonic dependence chain.',
            'The default medium regime is one auditable choice among several, not the only defensible mask.'
        ]
    })

    regime_sens=[]
    for regime in MASK_REGIMES:
        matt_mask = mask_data[regime]['Matt_mask']; luke_mask = mask_data[regime]['Luke_mask']
        scores_reg = scores_mtl[(matt_mask == False).nonzero()[0]][:, (luke_mask == False).nonzero()[0]]
        for th in [0.28,0.30,0.32,0.34]:
            pairs_reg,_=common.align_primary_chain(scores_reg, min_match=th, gap_penalty=0.05)
            loose_reg,_=common.segment_pairs(pairs_reg, loose_a=MLD_PARAMS['loose_gap_matt'], loose_b=MLD_PARAMS['loose_gap_luke'], tight_a=MLD_PARAMS['tight_gap_matt'], tight_b=MLD_PARAMS['tight_gap_luke'])
            regime_sens.append({'regime':regime,'primary_chain_min_score':th,'pair_count':len(pairs_reg),'loose_block_count':len(loose_reg)})
    common.dump_yaml(out_dir/'data'/'17_mask_regime_sensitivity.yaml', regime_sens)
    common.dump_yaml(out_dir/'data'/'18_actual_vs_canonical_slots.yaml', slots)

    flat_rows=[]
    for rec in detailed:
        for opi,op in enumerate(rec['diff_ops'], start=1):
            flat_rows.append({'rank_in_chain':rec['rank_in_chain'],'matt_ref':rec['matt_ref'],'luke_ref':rec['luke_ref'],
                              'score':rec['score'],'op_index':opi,'op':op['op'],'matt_segment':op['a'],'luke_segment':op['b']})
    pd.DataFrame(flat_rows).to_csv(out_dir/'data'/'19_pair_diffs_flat.tsv', index=False, sep='\t')
    common.dump_yaml(out_dir/'data'/'20_top_lemma_deltas.yaml', {
        'top_matt_only_content_lemmas_in_primary_pairs': lemma_delta['a_only'],
        'top_luke_only_content_lemmas_in_primary_pairs': lemma_delta['b_only'],
        'top_lemma_replacement_pairs': lemma_delta['replacements'],
        'pair_class_counts': lemma_delta['pair_class_counts'],
    })

if __name__ == '__main__':
    main()
