
from __future__ import annotations
from pathlib import Path
import pandas as pd
import yaml
import common

selected_canonical_books = ['Matt','Mark','Luke','John','Jas','1Tim','2Tim','1Cor','1John']

def main(base: Path | None = None):
    if base is None:
        base = Path(__file__).resolve().parents[1]
    common.src_base = base / 'sources' / 'repro_sources'
    common.books = {b: common.parse_book(b) for b in selected_canonical_books}
    prior = base / 'sources' / 'prior_thread_artifact' / 'jtea'

    old_case_studies = yaml.safe_load((prior/'07_targeted_case_studies.yaml').read_text(encoding='utf-8'))
    old_anchors = yaml.safe_load((prior/'08_john_synoptic_anchor_registry.yaml').read_text(encoding='utf-8'))
    old_thomas = yaml.safe_load((prior/'09_thomas_parallel_registry.yaml').read_text(encoding='utf-8'))
    old_burden = yaml.safe_load((prior/'14_burden_ledger.yaml').read_text(encoding='utf-8'))
    old_concepts = yaml.safe_load((prior/'11_concept_signature_registry.yaml').read_text(encoding='utf-8'))
    old_thomas_units = pd.read_csv(prior/'03_thomas_units.csv')
    old_apoc = pd.read_csv(prior/'12_apocrypha_inventory_from_mr_james.csv')
    old_exact_hits = pd.read_csv(prior/'06_exact_phrase_hits_len4plus.csv')
    old_edges = pd.read_csv(prior/'13_intertext_network_edges.csv')

    can_rows=[]
    for b in selected_canonical_books:
        for idx,v in enumerate(common.books[b]):
            can_rows.append({
                'book': b,'idx': idx,'ref': v['ref'],'chapter': v['chapter'],'verse': v['verse'],
                'word_count_default': len(v['tokens_default']),'lemma_count_default': len(v['lemmas']) if v['text_norm_default'] else 0,
                'text_raw': v['text_raw'],'text_norm_default': v['text_norm_default'],
                'lemmas': ' '.join(v['lemmas'] if v['text_norm_default'] else []),
                'cheap_shared': v['flags']['cheap_shared'],'citation_formula': v['flags']['citation_formula'],
                'bracketed_text': v['flags']['bracketed_text'],'variant_note_count': v['variant_note_count'],
            })
    canonical_units_df = pd.DataFrame(can_rows)
    weights_jtea = common.idf_weights([v for b in selected_canonical_books for v in common.books[b]], field='lemmas')

    def prep_agg_for_metrics_local(agg):
        lemmas = agg['lemmas']; tokens = agg['tokens_default']
        lemma_counter = __import__('collections').Counter(lemmas)
        token_counter = __import__('collections').Counter(tokens)
        bg_counter = __import__('collections').Counter(common.bigrams(tokens))
        tg_counter = __import__('collections').Counter(common.trigrams(tokens))
        content = [t for t in lemmas if t not in common.GREEK_STOPWORDS]
        content_counter = __import__('collections').Counter(content)
        return {
            **agg,'lemmas_eff': lemmas,'lemma_counter': lemma_counter,'lemma_sumw': sum(weights_jtea.get(k,1.0)*v for k,v in lemma_counter.items()),
            'token_counter': token_counter,'bg_counter': bg_counter,'tg_counter': tg_counter,
            'content_counter': content_counter,'content_sumw': sum(weights_jtea.get(k,1.0)*v for k,v in content_counter.items()),
        }

    updated_cases=[]
    for case in old_case_studies:
        src_vs = common.resolve_refspec(case['source_ref'])
        tgt_vs = common.resolve_refspec(case['target_ref'])
        src_agg = prep_agg_for_metrics_local(common.aggregate_verses(src_vs, refspec=case['source_ref']))
        tgt_agg = prep_agg_for_metrics_local(common.aggregate_verses(tgt_vs, refspec=case['target_ref']))
        pm = common.pair_metrics_fast(src_agg, tgt_agg, weights_jtea)
        frisk, frisk_type = common.formula_risk_for_case(case['source_ref'], case['target_ref'], case.get('feature',''), case.get('source_text',''), case.get('target_text',''))
        diff = common.summarize_pair_diff(src_agg, tgt_agg)
        new = dict(case)
        new['automatic_metrics_rerun_20260418'] = {
            'score': round(pm['score'],4),'lemma_dice': round(pm['lemma_dice'],4),'token_dice': round(pm['token_dice'],4),
            'bigram_dice': round(pm['bigram_dice'],4),'trigram_dice': round(pm['trigram_dice'],4),
            'lcs_len': pm['lcs_len'],'lcs_ratio': round(pm['lcs_ratio'],4),'max_exact_run_len': pm['lcs_len'],
            'max_exact_run': ' '.join(pm['lcs']),
            'shared_content_token_count': len(set(src_agg['lemmas']) & set(tgt_agg['lemmas']) - common.GREEK_STOPWORDS),
        }
        new['evidence_origin'] = {'automatic_retrieval': True,'curated_case': True,'hand_interpretation_required': True}
        new['automatic_score_supports_claim'] = common.support_label(pm['score'], pm['lcs_len'])
        new['philological_case_strength'] = common.philological_strength(case['case_id'])
        new['formula_risk'] = frisk
        new['formula_risk_type'] = frisk_type
        new['claim_id'] = f"jtea_{case['case_id']}"
        new['rerun_token_alignment_ops'] = diff['ops']
        updated_cases.append(new)

    updated_anchors=[]
    for idx,rec in enumerate(old_anchors, start=1):
        new=dict(rec)
        new['claim_id']=f"jtea_anchor_{idx:02d}"
        new['evidence_origin']={'automatic_retrieval': False,'curated_case': True,'hand_interpretation_required': True}
        new['relation_type']='shared_passion_or_event_tradition' if 'passion' in rec.get('anchor_id','') else 'shared_anchor_tradition'
        updated_anchors.append(new)

    updated_thomas=[]
    for rec in old_thomas:
        new=dict(rec)
        new['claim_id']=f"jtea_thomas_logion_{str(rec['thomas_logion']).replace(' ','_')}"
        new['evidence_origin']={'automatic_retrieval': False,'curated_case': True,'hand_interpretation_required': True}
        motif = rec.get('motif','').lower()
        if any(k in motif for k in ['sower','mustard','banquet','tenants','coin','lost sheep','pearl','treasure']):
            new['relation_type']='complex_saying_or_parable_overlap'
        else:
            new['relation_type']='portable_saying_overlap'
        updated_thomas.append(new)

    updated_concepts=[]
    for rec in old_concepts:
        new=dict(rec); new['claim_id']=f"jtea_concept_{rec['concept_id']}"; updated_concepts.append(new)

    updated_burden = dict(old_burden)
    updated_burden['scoring_interpretation']['retrieval_vs_interpretation'] = {
        'automatic_retrieval_confidence': 'How reliably the pipeline surfaces a candidate relation.',
        'philological_case_strength': 'How strongly the candidate supports a historical explanation after human review.',
        'formula_risk': 'How likely an exact match is driven by liturgy, scripture citation, or a common formula rather than Gospel-to-text dependence.'
    }
    updated_burden['scoring_interpretation']['rerun_note_2026_04_18'] = 'Targeted case metrics were recomputed from the local canonical Greek source base; Thomas/apocrypha layers remain curated/human-reviewed rather than automatically cross-lingually scored.'

    flag_map = {v['ref']: v['flags'] for b in selected_canonical_books for v in common.books[b]}
    def formula_risk_row_local(row):
        refs=[]
        for key in ['source_ref','target_ref']:
            r=row.get(key)
            if isinstance(r,str) and r in flag_map:
                refs.append(flag_map[r])
        citation = any(r['citation_formula'] for r in refs)
        cheap = any(r['cheap_shared'] for r in refs)
        src_book = row.get('source_book','')
        tgt_book = row.get('target_book','')
        if citation:
            return 'high'
        if src_book=='1Cor' and tgt_book=='Luke':
            return 'high'
        if cheap:
            return 'medium'
        return 'low'

    exact_aug = old_exact_hits.copy()
    exact_aug['formula_risk'] = exact_aug.apply(formula_risk_row_local, axis=1)
    exact_aug['evidence_origin'] = 'automatic_retrieval'
    filtered_exact = exact_aug[(exact_aug['formula_risk']!='high') & (exact_aug['max_exact_run_len']>=4)].copy()
    formula_summary = exact_aug.groupby(['layer','formula_risk']).size().reset_index(name='count')
    old_edges['formula_risk'] = old_edges.apply(lambda r: 'high' if 'scripture' in str(r.get('negative_space_flags','')).lower() or 'formula' in str(r.get('negative_space_flags','')).lower() else 'low', axis=1)

    claim_links=[]
    for case in updated_cases:
        claim_links.append({
            'claim_id': case['claim_id'],'claim_type': 'targeted_case',
            'supports': [
                {'artifact': 'data/07_targeted_case_studies.yaml', 'case_id': case['case_id']},
                {'artifact': 'data/06_exact_phrase_hits_len4plus.csv', 'match_hint': f"{case['source_ref']} -> {case['target_ref']}"},
            ],
            'confidence_dimensions': {
                'automatic_retrieval_confidence': case['automatic_score_supports_claim'],
                'philological_case_strength': case['philological_case_strength'],
                'formula_risk': case['formula_risk'],
            },
            'provisional_best_explanation': case['provisional_best_explanation'],
        })

    out_dir = base / 'reruns' / 'jtea_low_verbatim_rerun_robust'
    (out_dir/'data').mkdir(parents=True, exist_ok=True)

    common.dump_yaml(out_dir/'data'/'00_method_rethought_low_verbatim.yaml', {
        'project': 'Low-verbatim rerun/augmentation for John, Thomas, epistles, and apocrypha',
        'review_concerns_addressed': [
            'separates automatic retrieval confidence from philological case strength',
            'adds formula-risk classification for exact hits',
            'adds claim-to-evidence mapping',
            'makes explicit which layers are rerun from source and which remain curated/reused'
        ],
        'important_limitations': [
            'Thomas remains cross-lingual and curated; no automatic Greek-to-Coptic dependence scoring is claimed here.',
            'Apocrypha beyond Thomas remain inventory/registry level in this rerun.'
        ]
    })
    common.dump_yaml(out_dir/'data'/'01_source_manifest.yaml', {
        'canonical_greek_local_rerun': {'books_used': selected_canonical_books,'source_base': 'Local SBLGNT text + apparatus + MorphGNT'},
        'reused_curated_layers_from_prior_thread_artifact': {
            'thomas_units_csv': 'Copied from earlier thread artifact; used as curated source registry.',
            'thomas_parallel_registry': 'Copied and augmented with evidence-origin and relation-type labels.',
            'john_synoptic_anchor_registry': 'Copied and augmented with evidence-origin and relation-type labels.',
            'apocrypha_inventory': 'Copied as inventory layer; not automatically re-aligned in this patch.',
        }
    })
    canonical_units_df.to_csv(out_dir/'data'/'02_canonical_units.csv', index=False)
    old_thomas_units.to_csv(out_dir/'data'/'03_thomas_units.csv', index=False)
    shutil = __import__('shutil')
    for name in ['04_epistles_to_gospels_candidates.csv.gz','05_john_to_synoptics_candidates.csv.gz']:
        shutil.copy2(prior/name, out_dir/'data'/name)
    exact_aug.to_csv(out_dir/'data'/'06_exact_phrase_hits_len4plus.csv', index=False)
    common.dump_yaml(out_dir/'data'/'07_targeted_case_studies.yaml', updated_cases)
    common.dump_yaml(out_dir/'data'/'08_john_synoptic_anchor_registry.yaml', updated_anchors)
    common.dump_yaml(out_dir/'data'/'09_thomas_parallel_registry.yaml', updated_thomas)
    pd.DataFrame([{'layer':r['layer'],'source_ref':r['source_ref'],'target_ref':r['target_ref'],'max_exact_run_len':int(r['max_exact_run_len']),'formula_risk':r['formula_risk']} for _,r in exact_aug.iterrows()]).to_csv(out_dir/'data'/'10_negative_space_flags_for_exact_hits.csv', index=False)
    common.dump_yaml(out_dir/'data'/'11_concept_signature_registry.yaml', updated_concepts)
    old_apoc.to_csv(out_dir/'data'/'12_apocrypha_inventory_from_mr_james.csv', index=False)
    old_edges.to_csv(out_dir/'data'/'13_intertext_network_edges.csv', index=False)
    common.dump_yaml(out_dir/'data'/'14_burden_ledger.yaml', updated_burden)
    filtered_exact.to_csv(out_dir/'data'/'15_filtered_high_value_exact_hits.csv', index=False)
    common.dump_yaml(out_dir/'data'/'16_global_summary.yaml', {
        'project': 'John–Thomas–Epistles–Apocrypha rerun/augmentation with reproducibility patch',
        'global_metrics': {
            'canonical_units': int(len(canonical_units_df)),
            'thomas_units': int(len(old_thomas_units)),
            'targeted_cases': int(len(updated_cases)),
            'john_synoptic_anchors': int(len(updated_anchors)),
            'thomas_parallel_entries': int(len(updated_thomas)),
            'exact_hits_len4plus': int(len(exact_aug)),
            'filtered_exact_hits_non_high_formula_risk': int(len(filtered_exact)),
            'network_edges': int(len(old_edges)),
        },
        'most_important_updates': [
            'automatic retrieval support is now separated from philological case strength',
            'formula-risk classification added for exact hits',
            'claim-evidence links added',
            'canonical Greek targeted case metrics rerun against the local source base',
        ],
    })
    common.dump_yaml(out_dir/'data'/'17_claim_evidence_links.yaml', claim_links)
    formula_summary.to_csv(out_dir/'data'/'18_formula_risk_summary.csv', index=False)

if __name__ == '__main__':
    main()
