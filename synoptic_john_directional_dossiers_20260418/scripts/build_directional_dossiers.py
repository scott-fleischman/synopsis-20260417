#!/usr/bin/env python3
"""
Build the Synoptic + John directional hypothesis dossiers from included input snapshots.

Run from package root:
    python scripts/build_directional_dossiers.py

The script rebuilds the analytical CSV/YAML files in data/ from inputs/previous_artifacts/.
It does not fetch any external data.
"""
from pathlib import Path
import re, json, yaml, pandas as pd
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "inputs" / "previous_artifacts"
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

def yload(name):
    with open(IN / name, encoding="utf-8") as f:
        return yaml.safe_load(f)

def ywrite(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=120)

def ref_sort_key(ref):
    m = re.match(r'([1-3]?[A-Za-z]+)\s+(\d+):(\d+)', str(ref))
    book_order = {'Matt':1,'Mark':2,'Luke':3,'John':4}
    if not m: return (999,999,999)
    return (book_order.get(m.group(1),99), int(m.group(2)), int(m.group(3)))

def token_jaccard(a,b):
    A=set(a); B=set(b)
    if not A and not B: return 1.0
    if not A or not B: return 0.0
    return len(A&B)/len(A|B)

def exact_run_func(a,b):
    best=[]
    for i in range(len(a)):
        for j in range(len(b)):
            k=0
            while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]:
                k+=1
            if k>len(best):
                best=a[i:i+k]
    return best

def list_short(xs,n=12):
    xs=list(xs or [])
    return xs if len(xs)<=n else xs[:n]+[f"...+{len(xs)-n} more"]

canon = pd.read_csv(IN/'canonical_units.csv')
canon_by_ref = dict(zip(canon['ref'], canon.to_dict('records')))

def ref_text(ref):
    return canon_by_ref.get(ref,{}).get('text','')

def ref_tokens(ref, col='content_tokens'):
    s=canon_by_ref.get(ref,{}).get(col,'')
    return [] if pd.isna(s) or not str(s).strip() else str(s).split()

def refs_between(book, start_ref, end_ref):
    ks=ref_sort_key(start_ref); ke=ref_sort_key(end_ref)
    sub=canon[(canon['book']==book) & (canon['ref'].apply(lambda x: ref_sort_key(x) >= ks and ref_sort_key(x) <= ke))]
    return sub.sort_values(['chapter','verse'])['ref'].tolist()

def span_text(refs, max_chars=1200):
    txt=' '.join(ref_text(r) for r in refs if ref_text(r))
    return txt if len(txt)<=max_chars else txt[:max_chars]+' …'

def get_gap_count(gap, key):
    try:
        val=(gap or {}).get(key,{})
        if val is None: return 0
        return val.get('verse_count',0) or 0
    except Exception:
        return 0

def classify_gap(src_gap, tgt_gap):
    if tgt_gap > src_gap + 5: return 'target_addition_or_interposition'
    if src_gap > tgt_gap + 5: return 'source_material_omitted_or_compressed_by_target'
    if src_gap or tgt_gap: return 'minor_gap_or_local_relocation'
    return 'continuous_alignment'

direction_registry = [
    {'direction_id':'matthew_used_mark','short_label':'Matthew used Mark','source':'Mark','target':'Matthew','pair':'Mark↔Matthew','model_family':'direct written narrative dependence','current_status':'supported / high confidence relative to reverse','core_required_explanations':['Matthew preserves a Mark-like narrative backbone while inserting large non-Markan blocks.','Matthew omits, abbreviates, regularizes, or rephrases some Markan details.','Matthew relocates or collects sayings into discourse structures.','Matthew adds fulfillment, infancy, genealogy, and ecclesial/teaching material from other sources or composition.'],'core_contrary_evidence':['Matthew has major additional material, so Mark cannot be the only source.','Some Markan vividness and roughness could look secondary if judged locally.','Some agreements could be mediated by shared tradition rather than direct copying.','Text-critical variation and pericope-level displacement complicate strict one-source claims.'],'best_response_model':'Matthean redaction of Mark-like narrative source plus additional sayings, fulfillment, infancy, and discourse traditions.'},
    {'direction_id':'mark_used_matthew','short_label':'Mark used Matthew','source':'Matthew','target':'Mark','pair':'Mark↔Matthew','model_family':'direct written narrative dependence, reverse direction','current_status':'possible locally, higher cumulative burden','core_required_explanations':['Mark repeatedly omits large Matthean blocks.','Mark often makes the narrative shorter but also rougher, more vivid, and less discourse-organized.','Mark removes or transforms Matthean theological markers.','Mark preserves enough Matthean order to create extensive alignment while discarding much Matthean material.'],'core_contrary_evidence':['Repeated omission of high-value Matthean material has high cumulative burden.','Mark’s shorter form is often easier to explain as source than as drastic abridgment of Matthew.','Matthean discourse clustering looks like expansion/organization rather than material Mark split apart.','The global Mark–Matthew alignment favors Mark-like source priority.'],'best_response_model':'Markan epitome/abbreviation model with deliberate focus on action narrative and omission of long discourse/infancy material.'},
    {'direction_id':'luke_used_mark','short_label':'Luke used Mark','source':'Mark','target':'Luke','pair':'Mark↔Luke','model_family':'direct written narrative dependence','current_status':'supported over reverse among direct-use alternatives; medium-high with order-retention penalties','core_required_explanations':['Luke preserves many Mark-like narrative sequences but adds infancy, travel narrative, and distinctive teaching material.','Luke omits/compresses some Markan blocks and relocates or reframes others.','Luke regularizes diction and style while retaining local exact or near-exact Markan phrases.','Luke’s non-Markan material must be explained as additional source/tradition/composition.'],'core_contrary_evidence':['An unpenalized shared-tradition model had lower burden than either direct-use direction.','Luke has major non-Markan blocks and different theological/narrative aims.','Some Mark–Luke parallels are low-score or could reflect common tradition.','The Mark–Luke data alone is not as decisive as Mark–Matthew.'],'best_response_model':'Luke used Mark-like narrative source selectively, combining it with other sources/traditions and extensive Lukan redaction.'},
    {'direction_id':'mark_used_luke','short_label':'Mark used Luke','source':'Luke','target':'Mark','pair':'Mark↔Luke','model_family':'direct written narrative dependence, reverse direction','current_status':'possible locally, higher burden than Luke used Mark among direct-use alternatives','core_required_explanations':['Mark omits Luke’s infancy narratives, travel narrative, and large teaching blocks.','Mark compresses or removes Lukan universalizing and historiographical framing.','Mark turns some Lukan smoother discourse into shorter, rougher narrative.','Mark preserves enough Lukan order and wording to create the observed chain.'],'core_contrary_evidence':['Mark must omit more distinctive Lukan material than Luke must add under Mark-prior.','Luke-prior direct-use burden is higher.','Mark’s style/order fit better as a shorter narrative source in broader Synoptic system.','Matthew’s relation to Mark independently supports a Mark-like source.'],'best_response_model':'Markan epitome of Luke with radical abbreviation and narrative concentration.'},
    {'direction_id':'matthew_used_luke','short_label':'Matthew used Luke','source':'Luke','target':'Matthew','pair':'Matthew↔Luke','model_family':'direct written dependence in double tradition / infancy / sayings','current_status':'not demonstrated after Markan masking; possible locally','core_required_explanations':['Matthew relocates Lukan sayings into large discourse clusters.','Matthew rewrites or replaces Lukan infancy material with genealogy, Joseph/Magi/fulfillment framing.','Matthew adds characteristic scriptural fulfillment and kingdom-of-heaven language.','Matthew omits substantial Lukan material.'],'core_contrary_evidence':['After Markan masking, direct-dependence burdens were symmetric and common source/oral tradition lower.','Many double-tradition items are displaced rather than arranged in a simple chain.','The material behaves more like sayings/tradition than narrative source copying.','Matthew’s grouping often looks like topical clustering.'],'best_response_model':'Matthew used Luke-like sayings/tradition or Luke selectively, reorganizing sayings into discourse blocks.'},
    {'direction_id':'luke_used_matthew','short_label':'Luke used Matthew','source':'Matthew','target':'Luke','pair':'Matthew↔Luke','model_family':'direct written dependence in double tradition / Farrer-type direction','current_status':'possible locally; not demonstrated by masked data alone','core_required_explanations':['Luke disperses Matthean discourse material into narrative/travel contexts.','Luke reduces Matthean fulfillment framing and kingdom-of-heaven diction.','Luke rewrites or replaces Matthean infancy material.','Luke omits or rearranges large Matthean blocks while preserving some sayings closely.'],'core_contrary_evidence':['The masked double-tradition result favors common source/oral tradition.','Luke must intentionally break up highly organized Matthean discourses.','Some agreements are portable sayings compatible with shared tradition.','The full Matthew–Luke numeric result is not clean because it mixes layers.'],'best_response_model':'Luke deliberately de-Mattheanizes and redistributes sayings.'},
    {'direction_id':'john_used_mark','short_label':'John used Mark','source':'Mark','target':'John','pair':'John↔Mark','model_family':'anchor/episode dependence or shared tradition','current_status':'possible locally; shared anchor tradition currently lower burden','core_required_explanations':['John transforms Markan narrative episodes into theological sign/testimony scenes.','John relocates some material and omits many Markan units.','John expands discourses and identity claims while preserving selected anchors.','Low continuous lexical/order signal must be explained as heavy rewriting.'],'core_contrary_evidence':['Anchor-specific ledgers favor shared anchor tradition.','John lacks a continuous Markan chain.','Many anchors could circulate independently.','Lexical overlap is often low.'],'best_response_model':'John knew Mark or Mark-like tradition selectively; strongest only for local anchors.'},
    {'direction_id':'john_used_matthew','short_label':'John used Matthew','source':'Matthew','target':'John','pair':'John↔Matthew','model_family':'anchor/episode dependence or shared tradition','current_status':'possible locally; shared anchor tradition currently lower burden','core_required_explanations':['John transforms Matthean/Synoptic material into signs, testimonies, and discourses.','John omits much Matthean teaching structure, infancy material, and fulfillment framing.','John relocates/reframes shared passion/entry/anointing/temple material.','Low lexical signal must be explained as radical paraphrase.'],'core_contrary_evidence':['Anchor-specific ledgers favor shared tradition.','John does not preserve Matthew’s discourse architecture.','Some overlap is generic Gospel tradition or scriptural/passion formula.','A Matthew-specific signal is weaker than shared Synoptic/passion tradition.'],'best_response_model':'John knew Matthew-like tradition selectively; assess anchor by anchor.'},
    {'direction_id':'john_used_luke','short_label':'John used Luke','source':'Luke','target':'John','pair':'John↔Luke','model_family':'anchor/episode dependence or shared tradition','current_status':'possible locally; shared anchor tradition currently lower burden','core_required_explanations':['John transforms Lukan/Synoptic anchors into theological narrative.','John omits Lukan infancy, travel, parables, and distinctive material.','John retains selected passion/sign details.','Low lexical/order signal must be explained by selective non-sequential use.'],'core_contrary_evidence':['John↔Luke anchor ledger favors shared tradition.','Many overlaps are passion tradition rather than Lukan-specific wording.','John lacks Luke’s order and framing.','Low exact-run evidence weakens direct literary dependence.'],'best_response_model':'John knew Luke-like traditions/shared source; direct use remains local possibility.'},
    {'direction_id':'mark_used_john','short_label':'Mark used John','source':'John','target':'Mark','pair':'John↔Mark','model_family':'reverse John/Synoptic direction','current_status':'low support; included for completeness','core_required_explanations':['Mark narrativizes Johannine testimony/discourse into compact scenes.','Mark omits Johannine discourses, I-am language, Lazarus, and much theology.','Mark recontextualizes Johannine anchors.','Mark produces shorter rougher narrative retaining only selected anchors.'],'core_contrary_evidence':['Synoptic structure does not look like abridged John.','Shared anchor tradition lower burden.','Triple tradition is better explained without John priority.','Mark lacks central Johannine features.'],'best_response_model':'Radical Synoptic condensation of Johannine tradition; high burden.'},
    {'direction_id':'matthew_used_john','short_label':'Matthew used John','source':'John','target':'Matthew','pair':'John↔Matthew','model_family':'reverse John/Synoptic direction','current_status':'low support; included for completeness','core_required_explanations':['Matthew converts Johannine anchors into Synoptic form while omitting discourses/signs.','Matthew adds/preserves Mark-like narrative sequence independently.','Matthew replaces Johannine theology with fulfillment/discourse architecture.','Matthew uses John selectively in anchor zones.'],'core_contrary_evidence':['Matthew’s strongest relation is Mark-like.','Shared anchor tradition lower burden.','Matthew lacks Johannine structure/vocabulary.','No continuous John→Matthew chain evident.'],'best_response_model':'Matthew knew a Johannine-like anchor tradition, not necessarily John.'},
    {'direction_id':'luke_used_john','short_label':'Luke used John','source':'John','target':'Luke','pair':'John↔Luke','model_family':'reverse John/Synoptic direction','current_status':'low support; included for completeness','core_required_explanations':['Luke turns Johannine anchors into Lukan/Synoptic narrative contexts.','Luke omits Johannine discourses/signs while retaining selected anchors.','Luke combines John-derived anchors with Mark-like sequence and Lukan material.','Luke de-Johannizes vocabulary/theology almost completely.'],'core_contrary_evidence':['Luke’s Mark-like narrative relation is stronger.','John↔Luke anchor ledger favors shared tradition.','Luke lacks Johannine discourse architecture.','No continuous John→Luke chain evident.'],'best_response_model':'Luke knew shared Johannine-like passion/sign tradition rather than canonical John.'},
]

def main():
    # Write registry
    ywrite(OUT/'01_direction_hypotheses_registry.yaml', direction_registry)
    pd.DataFrame(direction_registry).drop(columns=['core_required_explanations','core_contrary_evidence']).to_csv(OUT/'01_direction_hypotheses_registry.csv', index=False)

    # Load all relevant ledgers
    mm_global=yload('mark_matthew_global_summary.yaml')
    mm_blocks=yload('mark_matthew_loose_blocks.yaml')
    mm_ledger=yload('mark_matthew_direction_ledger_by_loose_block.yaml')
    mm_intervals=yload('mark_matthew_order_intervals.yaml')
    mlk_blocks=yload('mark_luke_loose_blocks.yaml')
    mlk_ledger=yload('mark_luke_direction_ledger_by_loose_block.yaml')
    mlk_intervals=yload('mark_luke_order_intervals.yaml')
    mlk_reassess=yload('mark_luke_direct_burden_reassessment.yaml')
    mtl_ledger=yload('matt_luke_direction_ledger_by_loose_block.yaml')
    mtl_intervals=yload('matt_luke_order_intervals.yaml')
    mtl_burden=yload('matt_luke_direction_burden_totals.yaml')
    john_ledger=yload('john_anchor_specific_burden_ledgers.yaml')
    john_agg=yload('john_anchor_specific_aggregate_summary.yaml')

    # Burden summary
    burden_rows=[]
    mm_b=mm_global.get('burden_totals',{})
    burden_rows += [
        {'direction_id':'matthew_used_mark','pair':'Mark↔Matthew','burden_model':'direct_use','burden_score':mm_b.get('mark_prior_Matt_uses_Mark'),'lower_is_better':True,'comparison_basis':'Mark–Matthew rerun global summary','interpretive_result':'lower burden than Mark used Matthew'},
        {'direction_id':'mark_used_matthew','pair':'Mark↔Matthew','burden_model':'direct_use','burden_score':mm_b.get('matt_prior_Mark_uses_Matt'),'lower_is_better':True,'comparison_basis':'Mark–Matthew rerun global summary','interpretive_result':'higher burden than Matthew used Mark'},
        {'direction_id':'luke_used_mark','pair':'Mark↔Luke','burden_model':'direct_use_adjusted','burden_score':mlk_reassess['order_retention_penalty_model']['moderate_weight_result']['mark_prior_burden'],'lower_is_better':True,'comparison_basis':'Mark–Luke reassessment','interpretive_result':'lower than Mark used Luke'},
        {'direction_id':'mark_used_luke','pair':'Mark↔Luke','burden_model':'direct_use_adjusted','burden_score':mlk_reassess['order_retention_penalty_model']['moderate_weight_result']['luke_prior_burden'],'lower_is_better':True,'comparison_basis':'Mark–Luke reassessment','interpretive_result':'higher than Luke used Mark'},
        {'direction_id':'luke_used_matthew','pair':'Matthew↔Luke','burden_model':'full_pair_direct_use','burden_score':mtl_burden['matt_prior']['numeric_totals']['overall'],'lower_is_better':True,'comparison_basis':'Full Matthew–Luke ledger','interpretive_result':'not decisive after Mark masking'},
        {'direction_id':'matthew_used_luke','pair':'Matthew↔Luke','burden_model':'full_pair_direct_use','burden_score':mtl_burden['luke_prior']['numeric_totals']['overall'],'lower_is_better':True,'comparison_basis':'Full Matthew–Luke ledger','interpretive_result':'not decisive after Mark masking'},
    ]
    pair_to_dir={'John↔Luke':('john_used_luke','luke_used_john'),'John↔Mark':('john_used_mark','mark_used_john'),'John↔Matt':('john_used_matthew','matthew_used_john')}
    for item in john_agg:
        p=item['pair']; b=item['total_burdens']; jd,sd=pair_to_dir[p]
        burden_rows += [
            {'direction_id':jd,'pair':p,'burden_model':'anchor_direct_use','burden_score':b['john_uses_synoptic_or_synoptic_like_source'],'lower_is_better':True,'comparison_basis':'John anchor ledgers','interpretive_result':'higher than shared anchor tradition'},
            {'direction_id':sd,'pair':p,'burden_model':'anchor_reverse_direct_use','burden_score':b['synoptic_uses_john_or_john_like_source'],'lower_is_better':True,'comparison_basis':'John anchor ledgers','interpretive_result':'higher than shared anchor tradition'},
            {'direction_id':'shared_'+p.lower().replace('↔','_')+'_anchor_tradition','pair':p,'burden_model':'shared_anchor_tradition','burden_score':b['shared_anchor_tradition'],'lower_is_better':True,'comparison_basis':'John anchor ledgers','interpretive_result':'lowest burden'},
        ]
    pd.DataFrame(burden_rows).to_csv(OUT/'03_direction_burden_summary.csv', index=False)

    # Pericope rows
    pericope_rows=[]
    ledger_by_id={x['block_id']:x for x in mm_ledger}
    for b in mm_blocks:
        bid=b['id']; l=ledger_by_id.get(bid,{})
        mark_refs=b.get('mark_span_refs',[]) or []; matt_refs=b.get('matt_span_refs',[]) or []
        gap=l.get('gap_before_block',{})
        mg=get_gap_count(gap,'mark_gap'); tg=get_gap_count(gap,'matt_gap')
        common={'pair':'Mark↔Matthew','block_id':bid,'block_label':f'{b.get("mark_start_ref")}–{b.get("mark_end_ref")} / {b.get("matt_start_ref")}–{b.get("matt_end_ref")}',
                'pair_count':b.get('pair_count'),'avg_score':b.get('avg_score'),'gap_category':classify_gap(mg,tg),
                'mark_range':f'{b.get("mark_start_ref")}–{b.get("mark_end_ref")}','matt_range':f'{b.get("matt_start_ref")}–{b.get("matt_end_ref")}',
                'representative_primary_pairs':'; '.join([f"{p['mark_ref']}~{p['matt_ref']}" for p in (b.get('matched_pairs',[]) or [])[:5]]),
                'mark_text_preview':span_text(mark_refs[:3],500),'matt_text_preview':span_text(matt_refs[:3],500)}
        pericope_rows.append({**common,'direction_id':'matthew_used_mark','source':'Mark','target':'Matthew','source_range':common['mark_range'],'target_range':common['matt_range'],'operations':'; '.join(l.get('mark_prior_operations',[]) or []),'required_explanations':' | '.join(l.get('mark_prior_notes',[]) or []),'contrary_evidence':'Matthean additions/interpositions and low-score/reordered pairs require redactional explanation.','plausible_response_model':'Matthean expansion/discourse clustering/fulfillment framing.'})
        pericope_rows.append({**common,'direction_id':'mark_used_matthew','source':'Matthew','target':'Mark','source_range':common['matt_range'],'target_range':common['mark_range'],'operations':'; '.join(l.get('matt_prior_operations',[]) or []),'required_explanations':' | '.join(l.get('matt_prior_notes',[]) or []),'contrary_evidence':'Mark must omit/non-use much Matthean material.','plausible_response_model':'Markan epitome/abbreviation.'})
    ledger_by_id={x['block_id']:x for x in mlk_ledger}
    for b in mlk_blocks:
        bid=b['block_id']; l=ledger_by_id.get(bid,{})
        span=l.get('span',{}); mark_range=span.get('Mark') or f"{b.get('source_start_ref')}–{b.get('source_end_ref')}"; luke_range=span.get('Luke') or f"{b.get('target_start_ref')}–{b.get('target_end_ref')}"
        hyps=l.get('hypotheses',{})
        common={'pair':'Mark↔Luke','block_id':bid,'block_label':f'{mark_range} / {luke_range}','pair_count':b.get('pair_count'),'avg_score':b.get('mean_score'),'gap_category':classify_gap(b.get('source_gap_verses_inside_block',0), b.get('target_gap_verses_inside_block',0)),'mark_range':mark_range,'luke_range':luke_range,'representative_primary_pairs':'; '.join([f"{p['source_ref']}~{p['target_ref']}" for p in (b.get('primary_pairs',[]) or [])[:5]])}
        pericope_rows.append({**common,'direction_id':'luke_used_mark','source':'Mark','target':'Luke','source_range':mark_range,'target_range':luke_range,'operations':'lukan_addition_or_relocation; lukan_omission_or_compression; lukan_reframing','burden_score':hyps.get('Mark_prior_Luke_uses_Mark_or_Mark_like_source',{}).get('burden_score'),'required_explanations':' | '.join(hyps.get('Mark_prior_Luke_uses_Mark_or_Mark_like_source',{}).get('must_explain',[])),'contrary_evidence':'Shared-tradition model can explain some local parallels; Lukan gap material requires explanation.','plausible_response_model':'Luke uses Mark-like sequence with additional traditions.'})
        pericope_rows.append({**common,'direction_id':'mark_used_luke','source':'Luke','target':'Mark','source_range':luke_range,'target_range':mark_range,'operations':'markan_omission_of_lukan_material; markan_abbreviation; markan_vividization','burden_score':hyps.get('Luke_prior_Mark_uses_Luke_or_Luke_like_source',{}).get('burden_score'),'required_explanations':' | '.join(hyps.get('Luke_prior_Mark_uses_Luke_or_Luke_like_source',{}).get('must_explain',[])),'contrary_evidence':'Mark must omit large Lukan blocks; direct-use burden higher than Luke used Mark.','plausible_response_model':'Markan epitome of Luke.'})
    for l in mtl_ledger:
        bid=l['block_id']; ms=l.get('matt_span',[]); ls=l.get('luke_span',[])
        matt_range=f'{ms[0]}–{ms[1] if len(ms)>1 else ms[0]}'; luke_range=f'{ls[0]}–{ls[1] if len(ls)>1 else ls[0]}'
        d=l.get('direction_ledger',{}); mp=d.get('matt_prior',{}); lp=d.get('luke_prior',{})
        common={'pair':'Matthew↔Luke','block_id':bid,'block_label':f'{matt_range} / {luke_range}','pair_count':l.get('pair_count'),'avg_score':l.get('avg_score'),'matt_range':matt_range,'luke_range':luke_range}
        pericope_rows.append({**common,'direction_id':'luke_used_matthew','source':'Matthew','target':'Luke','source_range':matt_range,'target_range':luke_range,'operations':'; '.join([x.get('type','') for x in mp.get('operation_profile',[])]),'burden_score':mp.get('burden_summary',{}).get('numeric',{}).get('overall'),'required_explanations':' | '.join(mp.get('concise_reasoning',[])),'contrary_evidence':'Masked data favors common sayings/tradition; direct use requires Lukan redistribution.','plausible_response_model':'Luke disperses/de-Mattheanizes sayings.'})
        pericope_rows.append({**common,'direction_id':'matthew_used_luke','source':'Luke','target':'Matthew','source_range':luke_range,'target_range':matt_range,'operations':'; '.join([x.get('type','') for x in lp.get('operation_profile',[])]),'burden_score':lp.get('burden_summary',{}).get('numeric',{}).get('overall'),'required_explanations':' | '.join(lp.get('concise_reasoning',[])),'contrary_evidence':'Masked data favors common sayings/tradition; direct use requires Matthean clustering.','plausible_response_model':'Matthew clusters/scripturalizes sayings.'})
    pd.DataFrame(pericope_rows).to_csv(OUT/'10_synoptic_pericope_directional_change_ledger.csv', index=False)
    for pair_name, fname in [('Mark↔Matthew','11_mark_matthew_directional_pericope_ledger.csv'),('Mark↔Luke','12_mark_luke_directional_pericope_ledger.csv'),('Matthew↔Luke','13_matthew_luke_directional_pericope_ledger.csv')]:
        pd.DataFrame([r for r in pericope_rows if r['pair']==pair_name]).to_csv(OUT/fname, index=False)
    bydir=defaultdict(list)
    for r in pericope_rows: bydir[r['direction_id']].append(r)
    ywrite(OUT/'14_directional_pericope_explanation_dossiers.yaml', {k:{'pericope_or_block_count':len(v),'pericope_obligations':v} for k,v in bydir.items()})
    req=[]
    for r in pericope_rows:
        for i,x in enumerate([z.strip() for z in str(r.get('required_explanations','')).split('|') if z.strip()] or ['No specific requirement coded; inspect pair data.'],1):
            req.append({'direction_id':r['direction_id'],'pair':r['pair'],'block_id':r['block_id'],'source':r['source'],'target':r['target'],'source_range':r['source_range'],'target_range':r['target_range'],'requirement_no':i,'required_explanation':x,'contrary_evidence':r.get('contrary_evidence'),'response_model':r.get('plausible_response_model')})
    pd.DataFrame(req).to_csv(OUT/'15_directional_model_requirements_by_pericope.csv', index=False)

    # John rows
    john_rows=[]
    for item in john_ledger:
        pair=item['pair']; syn_book={'John↔Mark':'Mark','John↔Matt':'Matthew','John↔Luke':'Luke'}[pair]
        syn_key={'Mark':'mark','Matthew':'matthew','Luke':'luke'}[syn_book]
        b=item.get('burdens',{}); notes=item.get('directional_notes',{})
        bp=item.get('supporting_evidence',{}).get('best_pair',{})
        john_rows.append({'direction_id':f'john_used_{syn_key}','pair':pair,'anchor_id':item['anchor_id'],'source':syn_book,'target':'John','source_refs':item['synoptic_refs'],'target_refs':item['john_refs'],'best_current_model':item.get('best_lowest_burden_model'),'direct_use_burden':b.get('john_uses_synoptic_or_synoptic_like_source'),'shared_tradition_burden':b.get('shared_anchor_tradition'),'specific_features':'; '.join(item.get('supporting_evidence',{}).get('shared_features',[])),'best_pair':json.dumps(bp, ensure_ascii=False),'required_explanation_if_direction':notes.get('if_john_uses_synoptic'),'contrary_evidence':'Shared anchor tradition is lower burden.','plausible_response_model':'Johannine theological transformation.'})
        john_rows.append({'direction_id':f'{syn_key}_used_john','pair':pair,'anchor_id':item['anchor_id'],'source':'John','target':syn_book,'source_refs':item['john_refs'],'target_refs':item['synoptic_refs'],'best_current_model':item.get('best_lowest_burden_model'),'direct_use_burden':b.get('synoptic_uses_john_or_john_like_source'),'shared_tradition_burden':b.get('shared_anchor_tradition'),'specific_features':'; '.join(item.get('supporting_evidence',{}).get('shared_features',[])),'best_pair':json.dumps(bp, ensure_ascii=False),'required_explanation_if_direction':notes.get('if_synoptic_uses_john'),'contrary_evidence':'Synoptic target must omit/de-Johannize major Johannine material.','plausible_response_model':'Synoptic condensation/narrativization.'})
    pd.DataFrame(john_rows).to_csv(OUT/'16_john_synoptic_directional_anchor_ledger.csv', index=False)
    bydir=defaultdict(list)
    for r in john_rows: bydir[r['direction_id']].append(r)
    ywrite(OUT/'17_john_synoptic_directional_anchor_dossiers.yaml', {k:{'anchor_count':len(v),'anchors':v} for k,v in bydir.items()})

    # Gap catalog simplified
    gap_rows=[]
    def add_gap(pair, interval_id, did, source, target, sc, tc, sr, tr, note, resp):
        gap_rows.append({'pair':pair,'interval_id':interval_id,'direction_id':did,'source':source,'target':target,'source_gap_range':sr,'target_gap_range':tr,'source_gap_count':sc,'target_gap_count':tc,'dominant_material_issue':'target_addition' if tc>sc else ('target_omission_of_source' if sc>tc else 'balanced_gap'),'directional_implication':note,'plausible_response':resp,'contrary_evidence_value':abs(tc-sc)})
    for i,it in enumerate(mm_intervals):
        mg=it.get('mark_gap') or {}; tg=it.get('matt_gap') or {}; mc=mg.get('verse_count',0) or 0; tc=tg.get('verse_count',0) or 0
        mr=f"{mg.get('start_ref')}–{mg.get('end_ref')}" if mc else ''; tr=f"{tg.get('start_ref')}–{tg.get('end_ref')}" if tc else ''
        add_gap('Mark↔Matthew',f'mm_gap_{i:03d}','matthew_used_mark','Mark','Matthew',mc,tc,mr,tr,'Matthew must explain addition/omission around this interval.','Matthean added source/tradition or abbreviation.')
        add_gap('Mark↔Matthew',f'mm_gap_{i:03d}','mark_used_matthew','Matthew','Mark',tc,mc,tr,mr,'Mark must explain omission/addition around this interval.','Markan epitome/abbreviation.')
    for it in mlk_intervals:
        sc=it.get('source_gap_count',0) or 0; tc=it.get('target_gap_count',0) or 0
        sr='; '.join(list_short(it.get('source_gap_refs',[]),4)); tr='; '.join(list_short(it.get('target_gap_refs',[]),4))
        add_gap('Mark↔Luke',it.get('interval_id'),'luke_used_mark','Mark','Luke',sc,tc,sr,tr,'Luke must explain addition/omission around this interval.','Lukan additional sources or abbreviation.')
        add_gap('Mark↔Luke',it.get('interval_id'),'mark_used_luke','Luke','Mark',tc,sc,tr,sr,'Mark must explain omission/addition around this interval.','Markan epitome/abbreviation.')
    for i,it in enumerate(mtl_intervals):
        mg=it.get('matt_gap') or {}; lg=it.get('luke_gap') or {}; mc=mg.get('verse_count',0) or 0; lc=lg.get('verse_count',0) or 0
        mr=f"{mg.get('start_ref')}–{mg.get('end_ref')}" if mc else ''; lr=f"{lg.get('start_ref')}–{lg.get('end_ref')}" if lc else ''
        add_gap('Matthew↔Luke',f'ml_gap_{i:03d}','luke_used_matthew','Matthew','Luke',mc,lc,mr,lr,'Luke must explain addition/omission around this interval.','Lukan redistribution/alternate source.')
        add_gap('Matthew↔Luke',f'ml_gap_{i:03d}','matthew_used_luke','Luke','Matthew',lc,mc,lr,mr,'Matthew must explain addition/omission around this interval.','Matthean clustering/alternate source.')
    gd=pd.DataFrame(gap_rows); gd.to_csv(OUT/'20_material_omission_addition_catalog_by_direction.csv', index=False)
    gd.sort_values('contrary_evidence_value', ascending=False).head(100).to_csv(OUT/'21_top_major_gap_and_material_burdens.csv', index=False)
    ywrite(OUT/'22_major_material_burdens_by_direction.yaml', gd[gd['contrary_evidence_value']>=20].to_dict('records'))

    # Change diffs
    def mk_change_row(direction_id,pair,source,target,source_ref,target_ref,score,pair_classes='',source_text='',target_text='',repl='',moved='',hint=''):
        source_text = source_text if source_text and not pd.isna(source_text) else ref_text(source_ref)
        target_text = target_text if target_text and not pd.isna(target_text) else ref_text(target_ref)
        st=ref_tokens(source_ref); tt=ref_tokens(target_ref); er=exact_run_func(st,tt)
        return {'direction_id':direction_id,'pair':pair,'source':source,'target':target,'source_ref':source_ref,'target_ref':target_ref,'score':score,'pair_classes':pair_classes,'source_token_count':len(st),'target_token_count':len(tt),'shared_content_token_count':len(set(st)&set(tt)),'token_jaccard':round(token_jaccard(st,tt),4),'max_exact_run_len':len(er),'max_exact_run':' '.join(er) if er else hint,'target_inserted_or_source_absent_tokens':';'.join(sorted(set(tt)-set(st))[:50]),'source_deleted_or_target_absent_tokens':';'.join(sorted(set(st)-set(tt))[:50]),'lemma_replacements_or_substitutions':str(repl) if pd.notna(repl) else '','moved_lemmas':str(moved) if pd.notna(moved) else '','source_text':source_text,'target_text':target_text}
    changes=[]
    df=pd.read_csv(IN/'mark_matthew_pair_diffs_flat.tsv', sep='\t')
    for _,r in df.iterrows():
        changes.append(mk_change_row('matthew_used_mark','Mark↔Matthew','Mark','Matthew',r['mark_ref'],r['matt_ref'],r['score'],r.get('pair_classes',''),r.get('mark_text',''),r.get('matt_text',''),r.get('lemma_replacements',''),r.get('moved_lemmas','')))
        changes.append(mk_change_row('mark_used_matthew','Mark↔Matthew','Matthew','Mark',r['matt_ref'],r['mark_ref'],r['score'],r.get('pair_classes',''),r.get('matt_text',''),r.get('mark_text',''),r.get('lemma_replacements',''),r.get('moved_lemmas','')))
    df=pd.read_csv(IN/'mark_luke_primary_chain_pairs.csv')
    for _,r in df.iterrows():
        changes.append(mk_change_row('luke_used_mark','Mark↔Luke','Mark','Luke',r['source_ref'],r['target_ref'],r['score'],'primary_chain',hint=r.get('max_exact_run','')))
        changes.append(mk_change_row('mark_used_luke','Mark↔Luke','Luke','Mark',r['target_ref'],r['source_ref'],r['score'],'primary_chain',hint=r.get('max_exact_run','')))
    df=pd.read_csv(IN/'matt_luke_pair_diffs_flat.tsv', sep='\t')
    for _,r in df.iterrows():
        changes.append(mk_change_row('luke_used_matthew','Matthew↔Luke','Matthew','Luke',r['matt_ref'],r['luke_ref'],r['score'],r.get('pair_classes',''),r.get('matt_text',''),r.get('luke_text',''),r.get('lemma_replacements',''),r.get('moved_lemmas','')))
        changes.append(mk_change_row('matthew_used_luke','Matthew↔Luke','Luke','Matthew',r['luke_ref'],r['matt_ref'],r['score'],r.get('pair_classes',''),r.get('luke_text',''),r.get('matt_text',''),r.get('lemma_replacements',''),r.get('moved_lemmas','')))
    for row in john_rows:
        bp=json.loads(row['best_pair']) if row.get('best_pair') else {}
        sref=bp.get('synoptic_ref') if row['source']!='John' else bp.get('john_ref')
        tref=bp.get('john_ref') if row['source']!='John' else bp.get('synoptic_ref')
        if sref and tref:
            changes.append(mk_change_row(row['direction_id'],row['pair'],row['source'],row['target'],sref,tref,bp.get('score'),'john_anchor_best_pair',hint=bp.get('max_exact_run','')))
    cd=pd.DataFrame(changes); cd.to_csv(OUT/'50_primary_pair_change_diffs_all_directions.csv.gz', index=False, compression='gzip')
    pd.concat([cd.sort_values('max_exact_run_len',ascending=False).head(200),cd.sort_values('token_jaccard').head(200),cd.sort_values('score',ascending=False).head(200)]).drop_duplicates(subset=['direction_id','source_ref','target_ref']).head(500).to_csv(OUT/'51_top_primary_pair_change_cases.csv', index=False)
    summ=[]
    for did,g in cd.groupby('direction_id'):
        summ.append({'direction_id':did,'pair_count':len(g),'mean_score':round(pd.to_numeric(g['score'], errors='coerce').mean(),4),'mean_token_jaccard':round(g['token_jaccard'].mean(),4),'mean_exact_run_len':round(g['max_exact_run_len'].mean(),3),'max_exact_run_len':int(g['max_exact_run_len'].max()),'target_longer_pct':round(float((g['target_token_count']>g['source_token_count']).mean()),3)})
    pd.DataFrame(summ).to_csv(OUT/'52_primary_pair_change_summary_by_direction.csv', index=False)

    # Support/contra matrix using registry and generated gap/change/john data
    df_b=pd.DataFrame(burden_rows); df_g=gd; df_c=pd.DataFrame(summ); df_j=pd.DataFrame(john_rows)
    details={}; matrix=[]
    for d in direction_registry:
        did=d['direction_id']; g=df_g[df_g['direction_id']==did]; c=df_c[df_c['direction_id']==did]; j=df_j[df_j['direction_id']==did]
        details[did]={'hypothesis':d['short_label'],'source':d['source'],'target':d['target'],'current_status':d['current_status'],'supporting_evidence':[],'contrary_evidence':d['core_contrary_evidence'],'best_response_model':d['best_response_model'],'quantitative_indicators':{'gap_interval_count':int(len(g)),'major_gap_count_abs_diff_ge_20':int((g['contrary_evidence_value']>=20).sum()) if len(g) else 0,'max_gap_abs_difference':int(g['contrary_evidence_value'].max()) if len(g) else None,'primary_pair_count':int(c['pair_count'].iloc[0]) if len(c) else None,'john_anchor_count':int(len(j)) if len(j) else None},'top_material_gap_burdens':g.sort_values('contrary_evidence_value',ascending=False).head(5).to_dict('records') if len(g) else [],'top_john_anchor_burdens':j.sort_values('direct_use_burden',ascending=False).head(5).to_dict('records') if len(j) else []}
        matrix.append({'direction_id':did,'hypothesis':d['short_label'],'pair':d['pair'],'current_status':d['current_status'],'major_gap_count_abs_diff_ge_20':details[did]['quantitative_indicators']['major_gap_count_abs_diff_ge_20'],'max_gap_abs_difference':details[did]['quantitative_indicators']['max_gap_abs_difference'],'primary_pair_count':details[did]['quantitative_indicators']['primary_pair_count'],'john_anchor_count':details[did]['quantitative_indicators']['john_anchor_count'],'best_response_model':d['best_response_model']})
    ywrite(OUT/'60_contrary_evidence_and_response_models_by_direction.yaml', details)
    pd.DataFrame(matrix).to_csv(OUT/'61_support_contra_evidence_matrix.csv', index=False)
    ywrite(OUT/'99_data_dictionary.yaml', {'purpose':'Data dictionary for directional dossier package.','warning':'Burden scores are audit prompts, not probabilities.'})

    print(f"Wrote {len(direction_registry)} directions, {len(pericope_rows)} pericope rows, {len(john_rows)} John-anchor rows, {len(changes)} change-diff rows.")

if __name__ == '__main__':
    main()
