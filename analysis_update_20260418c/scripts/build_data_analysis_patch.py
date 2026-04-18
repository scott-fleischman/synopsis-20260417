#!/usr/bin/env python3
"""
Rebuild the synopsis data-analysis patch from local package inputs.

Run from the package root:
    python scripts/build_data_analysis_patch.py

This regenerates the analysis-layer files in data/ from:
    - inputs/previous_artifacts/...  (copied prior generated artifacts)
    - sources/morphgnt/*.txt         (selected MorphGNT snapshots)

It intentionally does not fetch from the internet.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import math, re, unicodedata, yaml, pandas as pd, numpy as np, hashlib, datetime, shutil, random

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INP = ROOT / "inputs" / "previous_artifacts"
MORPH = ROOT / "sources" / "morphgnt"
DATA.mkdir(exist_ok=True)

def native(x):
    if isinstance(x, dict):
        return {native(k): native(v) for k, v in x.items()}
    if isinstance(x, list):
        return [native(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x

def yload(rel: str):
    return yaml.safe_load(open(INP / rel, encoding="utf-8"))

def ydump(data, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(native(data), f, allow_unicode=True, sort_keys=False, width=120)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def strip_accents(s: str) -> str:
    s = str(s)
    s = s.replace("⸂","").replace("⸃","").replace("⸀","").replace("⟦","").replace("⟧","")
    s = s.lower()
    s = re.sub(r'[·.,;:!?—"“”‘’ʼ\(\)\[\]{}<>«»]', "", s)
    s = "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")
    return s.replace("ς","σ")

def toks(s):
    if not isinstance(s, str) or not s or s == "nan":
        return []
    return [x for x in s.split() if x and x != "nan"]

def jaccard(a,b):
    A=set(a); B=set(b)
    return len(A&B)/len(A|B) if A or B else 0.0

def dice_ngrams(a,b,n=2):
    if len(a)<n or len(b)<n: return 0.0
    A=[tuple(a[i:i+n]) for i in range(len(a)-n+1)]
    B=[tuple(b[i:i+n]) for i in range(len(b)-n+1)]
    ca=Counter(A); cb=Counter(B)
    inter=sum(min(ca[k],cb[k]) for k in set(ca)&set(cb))
    return 2*inter/(sum(ca.values())+sum(cb.values())) if (ca or cb) else 0.0

def lcs_len(a,b):
    if not a or not b: return 0
    prev=[0]*(len(b)+1)
    for x in a:
        cur=[0]*(len(b)+1)
        for j,y in enumerate(b,1):
            cur[j]=prev[j-1]+1 if x==y else max(prev[j],cur[j-1])
        prev=cur
    return int(prev[-1])

def max_exact_run(a,b):
    if not a or not b: return (0,"")
    dp=[0]*(len(b)+1); best=0; best_end=0
    for i,x in enumerate(a,1):
        new=[0]*(len(b)+1)
        for j,y in enumerate(b,1):
            if x==y:
                new[j]=dp[j-1]+1
                if new[j]>best:
                    best=new[j]; best_end=i
        dp=new
    return int(best), " ".join(a[best_end-best:best_end])

def metric_row(a,b,prefix="lemma"):
    lcs=lcs_len(a,b)
    maxrun, run=max_exact_run(a,b)
    overlap=len(set(a)&set(b))
    score=0.40*jaccard(a,b)+0.18*dice_ngrams(a,b,2)+0.12*dice_ngrams(a,b,3)+0.20*(lcs/min(len(a),len(b)) if min(len(a),len(b)) else 0)+0.10*(overlap/max(len(set(a)),len(set(b))) if max(len(set(a)),len(set(b))) else 0)
    return {
        f"{prefix}_jaccard": round(jaccard(a,b),4),
        f"{prefix}_bigram_dice": round(dice_ngrams(a,b,2),4),
        f"{prefix}_trigram_dice": round(dice_ngrams(a,b,3),4),
        f"{prefix}_lcs_len": lcs,
        f"{prefix}_lcs_ratio": round(lcs/min(len(a),len(b)),4) if min(len(a),len(b)) else 0,
        f"{prefix}_max_exact_run_len": maxrun,
        f"{prefix}_max_exact_run": run,
        f"{prefix}_shared_content_token_count": overlap,
        f"{prefix}_shared_content_tokens": " ".join(sorted(set(a)&set(b))),
        f"{prefix}_score": round(score,4),
    }

# Local copied artifact paths.
P = {
 "mm_summary": "synopsis_repro_patch_20260418/reruns/mark_matthew_rerun_robust/data/16_global_summary.yaml",
 "mkl_summary": "synopsis_high_priority_missing_20260418/data/19_mark_luke_global_summary.yaml",
 "mkl_ledger": "synopsis_high_priority_missing_20260418/data/17_mark_luke_direction_ledger_by_loose_block.yaml",
 "mkl_burdens": "synopsis_high_priority_missing_20260418/data/18_mark_luke_burden_totals.yaml",
 "mkl_primary": "synopsis_high_priority_missing_20260418/data/11_mark_luke_primary_chain_pairs.csv",
 "mkl_matrix": "synopsis_high_priority_missing_20260418/data/10_mark_luke_verse_similarity_full.csv.gz",
 "ml_full_summary": "matt_luke_analysis/data/16_global_summary.yaml",
 "mld_summary": "synopsis_repro_patch_20260418/reruns/matt_luke_double_masked_rerun_robust/data/16_global_summary.yaml",
 "mld_sensitivity": "synopsis_repro_patch_20260418/reruns/matt_luke_double_masked_rerun_robust/data/17_mask_regime_sensitivity.yaml",
 "mld_mask_compare": "synopsis_repro_patch_20260418/reruns/matt_luke_double_masked_rerun_robust/data/01c_mask_regime_comparison.csv",
 "john_summary": "synopsis_high_priority_missing_20260418/data/38_john_synoptic_pairwise_global_summary.yaml",
 "john_anchors": "synopsis_high_priority_missing_20260418/data/37_john_synoptic_pairwise_anchor_registry.yaml",
 "thomas_matrix": "synopsis_high_priority_missing_20260418/data/50_thomas_gospel_logion_matrix.csv",
 "ep_top500": "synopsis_high_priority_missing_20260418/data/62_epistle_gospel_ranked_candidate_cases_top500.csv",
 "ep_targeted": "synopsis_high_priority_missing_20260418/data/61_epistle_gospel_targeted_case_table.csv",
 "jtea_summary": "john_thomas_epistles_apocrypha_analysis/data/16_global_summary.yaml",
}

# Authoritative numbers and reproducibility levels.
mm_sum=yload(P["mm_summary"]); mkl_sum=yload(P["mkl_summary"]); mld_sum=yload(P["mld_summary"])
ml_full_sum=yload(P["ml_full_summary"]); jtea_sum=yload(P["jtea_summary"]); john_pair_sum=yload(P["john_summary"])
thomas_matrix=pd.read_csv(INP/P["thomas_matrix"]); ep_top500=pd.read_csv(INP/P["ep_top500"]); ep_targeted=pd.read_csv(INP/P["ep_targeted"])
ydump({
  "status":"data-analysis patch authoritative-number reconciliation",
  "date":"2026-04-18",
  "rule":"Use rerun/patch artifacts for headline numbers when available; older package numbers remain prior-package comparanda.",
  "units":{
    "Mark_Matthew":{"headline_source":P["mm_summary"],"primary_pairs":mm_sum["global_metrics"]["matched_pair_count"],"loose_blocks":mm_sum["global_metrics"]["loose_block_count"],"tight_blocks":mm_sum["global_metrics"]["tight_block_count"],"secondary_echoes":mm_sum["global_metrics"]["secondary_echo_count"],"directional_burden_totals":mm_sum["burden_totals"]},
    "Mark_Luke":{"headline_source":P["mkl_summary"],"primary_pairs":mkl_sum["primary_chain_pairs"],"loose_blocks":mkl_sum["loose_blocks"],"tight_blocks":mkl_sum["tight_blocks"],"secondary_echoes_score_ge_0_22":mkl_sum["secondary_echoes_score_ge_0_22"],"directional_burden_totals_original":mkl_sum["burden_totals"]},
    "Matthew_Luke_full":{"headline_source":P["ml_full_summary"],"primary_pairs":ml_full_sum["global_metrics"]["matched_pair_count"],"loose_blocks":ml_full_sum["global_metrics"]["loose_block_count"],"tight_blocks":ml_full_sum["global_metrics"]["tight_block_count"],"secondary_echoes":ml_full_sum["global_metrics"]["secondary_echo_count"]},
    "Matthew_Luke_masked_double_tradition":{"headline_source":P["mld_summary"],"default_mask_regime":mld_sum["method_summary"]["default_parameters"]["mask_regime_default"],"primary_pairs_default_medium":mld_sum["global_metrics"]["matched_pair_count_default_medium"],"loose_blocks_default_medium":mld_sum["global_metrics"]["loose_block_count_default_medium"],"tight_blocks_default_medium":mld_sum["global_metrics"]["tight_block_count_default_medium"],"secondary_echoes_default_medium":mld_sum["global_metrics"]["secondary_echo_count_default_medium"],"mask_regimes":mld_sum["method_summary"]["mask_regimes"]},
    "John_Synoptic_pairwise":{"headline_source":P["john_summary"],"pair_summaries":john_pair_sum},
    "Thomas":{"headline_source":P["thomas_matrix"],"total_logion_units":int(thomas_matrix.shape[0]),"logia_with_curated_canonical_parallels":int((thomas_matrix["registered_parallel_count"]>0).sum()),"automatic_coptic_greek_scoring":False},
    "Epistles_Gospels":{"headline_source":P["ep_top500"],"top500_rows":int(ep_top500.shape[0]),"targeted_case_rows":int(ep_targeted.shape[0]),"candidate_rows_prior_layer":int(jtea_sum["automatic_layers"]["epistles_to_gospels"]["candidate_rows"])}
  }
}, DATA/"01_authoritative_numbers.yaml")
ydump({
 "purpose":"clarify what is regenerated, inherited, and curated",
 "level_1_regenerated_in_this_patch":["MorphGNT token/verse layer","Mark-Luke morphology audit","Mark-Luke shared-tradition penalty sensitivity","John anchor ledgers","Thomas curation-status augmentation","Epistle validation sample","Epistle targeted morphology audit","Q/mask-regime robustness summary"],
 "level_2_regenerated_from_prior_artifact_inputs":["authoritative numbers","Q robustness table","John aggregate summaries","epistle validation strata"],
 "level_3_curated_or_interpretive":["Mark-Luke interpretive caution","apocrypha roadmap","updated data-only conclusions"],
 "not_done_in_this_patch":["fresh apocrypha primary-text comparison beyond Thomas","automatic Coptic-to-Greek Thomas scoring","human philological validation","visualization integration"]
}, DATA/"02_reproducibility_levels.yaml")

# Mark-Luke burden reassessment.
ml_burd=yload(P["mkl_burdens"]); ml_ledger=yload(P["mkl_ledger"])
penalty_rows=[]
for b in ml_ledger:
    cf=b.get("coded_features",{})
    pc=int(b["pair_count"]); mean=float(b["mean_score"]); mark_gap=int(cf.get("mark_gap_verses_inside_block",0) or 0); luke_gap=int(cf.get("luke_gap_verses_inside_block",0) or 0)
    penalty_rows.append({"block_id":b["block_id"],"span_mark":b["span"]["Mark"],"span_luke":b["span"]["Luke"],"pair_count":pc,"mean_score":round(mean,4),"close_pairs":int(cf.get("close_pairs_score_ge_0_45_or_run_ge_4",0) or 0),"mark_gap_inside_block":mark_gap,"luke_gap_inside_block":luke_gap,"base_shared_burden":round(float(b["hypotheses"]["shared_narrative_or_oral_tradition_without_direct_use"]["burden_score"]),4),"order_retention_signal_paircount_x_mean_score":round(pc*mean,4),"local_exact_signal_from_prior_ledger":round(float(cf.get("exact_agreement_pressure_against_pure_common_tradition",0) or 0),4),"cluster_density_signal_log_paircount_x_mean_score":round(math.log1p(pc)*mean,4),"narrative_bridge_signal_multiverse_sequence":int(max(0,pc-1) if pc>=3 else 0),"low_gap_continuity_signal":int(1 if pc>=3 and mark_gap<=3 and luke_gap<=3 else 0)})
penalty_df=pd.DataFrame(penalty_rows); penalty_df.to_csv(DATA/"10_mark_luke_tradition_retention_audit_by_block.csv",index=False)
base_shared=float(ml_burd["shared_narrative_or_oral_tradition_without_direct_use"]); mark_prior=float(ml_burd["Mark_prior_Luke_uses_Mark_or_Mark_like_source"]); luke_prior=float(ml_burd["Luke_prior_Mark_uses_Luke_or_Luke_like_source"])
grid=[]
for ow in [0,0.25,0.5,0.75,1.0,1.25,1.5]:
  for cw in [0,0.5,1.0,1.5,2.0]:
    for bw in [0,0.25,0.5,0.75,1.0,1.5,2.0]:
      add=float((penalty_df["order_retention_signal_paircount_x_mean_score"]*ow+penalty_df["cluster_density_signal_log_paircount_x_mean_score"]*cw+penalty_df["narrative_bridge_signal_multiverse_sequence"]*bw).sum())
      adjusted=base_shared+add
      vals={"Mark_prior_Luke_uses_Mark_or_Mark_like_source":mark_prior,"Luke_prior_Mark_uses_Luke_or_Luke_like_source":luke_prior,"shared_tradition_adjusted_for_order_retention":adjusted}
      winner=min(vals,key=vals.get)
      grid.append({"order_retention_weight":ow,"cluster_density_weight":cw,"narrative_bridge_weight":bw,"added_shared_tradition_penalty":round(add,4),"adjusted_shared_tradition_burden":round(adjusted,4),"mark_prior_burden":mark_prior,"luke_prior_burden":luke_prior,"lowest_burden_model":winner,"shared_still_lower_than_mark_prior":adjusted<mark_prior,"shared_still_lower_than_luke_prior":adjusted<luke_prior})
grid_df=pd.DataFrame(grid); grid_df.to_csv(DATA/"11_mark_luke_shared_tradition_penalty_sensitivity.csv",index=False)
moderate=grid_df[(grid_df.order_retention_weight==0.75)&(grid_df.cluster_density_weight==1.0)&(grid_df.narrative_bridge_weight==1.0)].iloc[0].to_dict()
ydump({"original_three_way_burden_totals":ml_burd,"direct_use_only_result":{"lower_direct_use_model":"Mark_prior_Luke_uses_Mark_or_Mark_like_source","difference_Luke_prior_minus_Mark_prior":round(luke_prior-mark_prior,4)},"unpenalized_three_way_result":{"lowest_model":min(ml_burd,key=ml_burd.get),"caution":"Unpenalized shared tradition is lower than either direct-use model."},"order_retention_penalty_model":{"moderate_weights":{"order_retention_weight":0.75,"cluster_density_weight":1.0,"narrative_bridge_weight":1.0},"moderate_weight_result":{"added_shared_tradition_penalty":round(float(moderate["added_shared_tradition_penalty"]),4),"adjusted_shared_tradition_burden":round(float(moderate["adjusted_shared_tradition_burden"]),4),"mark_prior_burden":mark_prior,"luke_prior_burden":luke_prior,"lowest_burden_model":moderate["lowest_burden_model"]},"grid_outcome_counts":grid_df["lowest_burden_model"].value_counts().to_dict()}}, DATA/"12_mark_luke_direct_burden_reassessment.yaml")
ydump({"claim_id":"mark_luke_revised_interpretive_claim","recommended_public_wording":"Mark-Luke strengthens the broader Mark-like-source model, but the Mark-Luke data alone should be reported as Mark-prior-over-Luke-prior among direct-use alternatives, not as standalone proof that Luke used canonical Mark."}, DATA/"13_mark_luke_revised_interpretive_claim.yaml")

# Matthew-Luke mask robustness.
mask_sens=pd.DataFrame(yload(P["mld_sensitivity"])); mask_comp=pd.read_csv(INP/P["mld_mask_compare"])
rob=mask_sens.merge(mask_comp,on="regime",how="left"); rob.to_csv(DATA/"20_matt_luke_mask_regime_robustness_table.csv",index=False)
rob_summary=rob.groupby("regime").agg(pair_count_min=("pair_count","min"),pair_count_max=("pair_count","max"),loose_block_count_min=("loose_block_count","min"),loose_block_count_max=("loose_block_count","max"),matt_masked=("matt_masked","first"),matt_unmasked=("matt_unmasked","first"),luke_masked=("luke_masked","first"),luke_unmasked=("luke_unmasked","first"),threshold=("threshold","first")).reset_index()
rob_summary.to_csv(DATA/"21_matt_luke_mask_regime_robustness_summary.csv",index=False)
ydump({"default_medium_mask":{"matched_pair_count":mld_sum["global_metrics"]["matched_pair_count_default_medium"],"loose_block_count":mld_sum["global_metrics"]["loose_block_count_default_medium"]},"regime_summary":rob_summary.to_dict(orient="records"),"interpretation":"Strict/medium/broad masks alter counts, but the retained material remains a sayings/echo problem rather than a stable narrative-chain relationship."}, DATA/"22_matt_luke_double_tradition_robustness.yaml")

# John anchor-specific ledgers.
def score_anchor(row):
    m=row.get("metrics_from_verse_matrix",{}) or {}; max_score=float(m.get("max_score") or 0); max_run=int(m.get("max_exact_run_len") or 0)
    feat_count=len(row.get("shared_features") or []); text=" ".join(row.get("shared_features") or []).lower(); ct=(row.get("common_tradition_assessment") or "").lower(); tj=(row.get("john_transformation_if_synoptics_prior") or "").lower(); ts=(row.get("synoptic_transformation_if_john_prior") or "").lower()
    local_lex=min(4.0,max_score*6); exact=min(4.0,max_run*0.65); specificity=min(5.0,0.75*feat_count+(1.5 if any(k in text for k in ["ear","servant","garment","lots","poor","denial","anointing","king","stone","temple"]) else 0)+(1.0 if max_run>=4 else 0)); displacement=2.0 if any(k in tj for k in ["relocat","reorder","displac","beginning"]) else 0.5
    burdens={"john_uses_synoptic_or_synoptic_like_source":round(4.0+displacement+max(0,2.0-local_lex)+max(0,1.5-exact)+(0.5 if "portable" in ct or "low-burden" in ct else 0),3),"synoptic_uses_john_or_john_like_source":round(4.4+(1.3 if "johannine" in ts or "discourse" in ts or "theological" in ts else 0.7)+max(0,2.0-local_lex)+max(0,1.5-exact),3),"shared_anchor_tradition":max(0.75,round(2.0+max(0,specificity-3.0)*0.7+max(0,exact-2.0)*0.5-(1.0 if "low-burden" in ct or "portable" in ct or "plausible" in ct else 0)+(0.6 if "must be explained" in ct else 0),3)),"independent_convergence":round(5.0+specificity+local_lex+exact,3)}
    return {"anchor_id":row["anchor_id"],"pair":row["pair"],"john_refs":row["john_refs"],"synoptic_refs":row["synoptic_refs"],"feature_count":feat_count,"local_lexical_signal":round(local_lex,3),"exact_run_signal":round(exact,3),"specificity_signal":round(specificity,3),"order_or_reframing_displacement_signal":round(displacement,3),"burdens":burdens,"best_lowest_burden_model":min(burdens,key=burdens.get),"supporting_evidence":{"shared_features":row.get("shared_features"),"metrics":m,"best_pair":m.get("best_pair") if isinstance(m,dict) else None},"directional_notes":{"if_john_uses_synoptic":row.get("john_transformation_if_synoptics_prior"),"if_synoptic_uses_john":row.get("synoptic_transformation_if_john_prior"),"common_tradition_assessment":row.get("common_tradition_assessment"),"prior_registry_provisional_explanation":row.get("provisional_best_explanation")}}
anchors=yload(P["john_anchors"]); ledgers=[score_anchor(r) for r in anchors]; ydump(ledgers, DATA/"30_john_anchor_specific_burden_ledgers.yaml")
flat=[]
for a in ledgers:
    row={k:a[k] for k in ["anchor_id","pair","john_refs","synoptic_refs","feature_count","local_lexical_signal","exact_run_signal","specificity_signal","order_or_reframing_displacement_signal","best_lowest_burden_model"]}
    for k,v in a["burdens"].items(): row["burden_"+k]=v
    flat.append(row)
anchor_flat=pd.DataFrame(flat); anchor_flat.to_csv(DATA/"31_john_anchor_specific_burden_ledgers_flat.csv",index=False)
agg=[]
for pair,g in anchor_flat.groupby("pair"):
    burdens={c.replace("burden_",""):round(float(g[c].sum()),3) for c in g.columns if c.startswith("burden_")}
    agg.append({"pair":pair,"anchor_count":int(len(g)),"total_burdens":burdens,"lowest_total_burden_model":min(burdens,key=burdens.get),"anchors_best_model_counts":{str(k):int(v) for k,v in g["best_lowest_burden_model"].value_counts().items()}})
ydump(agg, DATA/"32_john_anchor_specific_aggregate_summary.yaml")

# Thomas status.
tm=thomas_matrix.copy()
def thomas_cert(row):
    if row["registered_parallel_count"]<=0: return ("not_assessed","no curated parallel")
    if row["matrix_strength"]=="high" and "possible_synoptic" in str(row["relation_type"]): return ("medium_high","motif + structured canonical parallel; direction uncertain")
    if row["matrix_strength"]=="high": return ("high","strong curated motif/structure parallel")
    if row["matrix_strength"]=="medium": return ("medium","curated motif/structure parallel")
    return ("low","weak or generic curated parallel")
certs=tm.apply(thomas_cert,axis=1)
tm["curation_status"]="curated_from_prior_registry"; tm.loc[tm["registered_parallel_count"]<=0,"curation_status"]="no_curated_canonical_parallel_in_prior_registry"; tm["automatic_coptic_greek_candidate_generation"]=False; tm["automatic_coptic_greek_lexical_score_available"]=False; tm["parallel_certainty"]=certs.map(lambda x:x[0]); tm["parallel_certainty_basis"]=certs.map(lambda x:x[1]); tm["analysis_ready_for_directional_claim"]=tm.apply(lambda r: bool(r["registered_parallel_count"]>0 and r["parallel_certainty"] in ["high","medium_high"] and "possible_synoptic" in str(r["relation_type"])),axis=1)
tm.to_csv(DATA/"40_thomas_logion_matrix_with_curation_status.csv",index=False)
ydump({"total_logia":int(tm.shape[0]),"curation_status_counts":tm["curation_status"].value_counts().to_dict(),"parallel_certainty_counts":tm["parallel_certainty"].value_counts().to_dict(),"relation_type_counts":tm["relation_type"].value_counts().to_dict(),"directional_claim_ready_count":int(tm["analysis_ready_for_directional_claim"].sum()),"methodological_warning":"curated logion statuses; no automatic Greek-Coptic dependence score"}, DATA/"41_thomas_curation_status_summary.yaml")
tm[["thomas_logion","relation_type","matrix_strength","parallel_certainty"]].groupby(["relation_type","matrix_strength","parallel_certainty"]).size().reset_index(name="count").to_csv(DATA/"42_thomas_relation_counts.csv",index=False)

# Epistle validation and formula risk.
top=ep_top500.copy(); target=ep_targeted.copy(); target_keys=set(zip(target["source_ref"],target["target_ref"]))
def classify(row):
    flags=str(row.get("negative_space_flags","")); risk=str(row.get("formula_risk","")); maxrun=int(row.get("max_exact_run_len") or 0); score=float(row.get("score") or 0); key=(str(row.get("source_ref")),str(row.get("target_ref")))
    if key in target_keys: return ("targeted_known_case","targeted dossier")
    if risk=="high": return ("scriptural_formula_shared_source" if any(x in flags for x in ["ps","gen","isa","deut","one_flesh","footstool"]) else "high_formula_risk_needs_manual_review","formula risk")
    if maxrun>=5 and score>=0.30: return ("strong_low_formula_candidate","low formula risk + long exact run")
    if maxrun>=3 and score>=0.25: return ("moderate_low_formula_candidate","moderate lexical signal")
    if score<0.18 and maxrun<=2: return ("weak_or_generic_candidate","low score and short exact run")
    return ("uncertain_candidate","intermediate signal")
frames=[]
for _,tr in target.iterrows():
    match=top[(top.source_ref==tr.source_ref)&(top.target_ref==tr.target_ref)]
    if len(match):
        d=match.iloc[[0]].copy(); d["sample_stratum"]="targeted_dossier_present_in_top500"; frames.append(d)
    else:
        r={col:None for col in top.columns}; r.update({"source_ref":tr.source_ref,"target_ref":tr.target_ref,"source_book":str(tr.source_ref).split()[0],"target_book":str(tr.target_ref).split()[0],"score":tr.score,"max_exact_run_len":tr.max_exact_run_len,"formula_risk":tr.formula_risk,"negative_space_flags":"","source_text":"","target_text":"","sample_stratum":"targeted_dossier_not_in_top500"}); frames.append(pd.DataFrame([r]))
for name,df in [("low_formula_high_score_top30",top[top.formula_risk=="low"].sort_values(["score","max_exact_run_len"],ascending=False).head(30)),("high_formula_top30",top[top.formula_risk=="high"].sort_values(["score","max_exact_run_len"],ascending=False).head(30)),("low_formula_exact_run_ge4_top30",top[(top.formula_risk=="low")&(top.max_exact_run_len>=4)].sort_values(["max_exact_run_len","score"],ascending=False).head(30)),("low_formula_random30_seed42",top[top.formula_risk=="low"].sample(n=min(30,len(top[top.formula_risk=="low"])),random_state=42)),("weak_low_score_random30_seed43",top[top.score<0.20].sample(n=min(30,len(top[top.score<0.20])),random_state=43))]:
    d=df.copy(); d["sample_stratum"]=name; frames.append(d)
sample=pd.concat(frames,ignore_index=True).drop_duplicates(subset=["source_ref","target_ref","sample_stratum"])
classes=sample.apply(classify,axis=1); sample["machine_audit_class"]=classes.map(lambda x:x[0]); sample["machine_audit_reason"]=classes.map(lambda x:x[1]); sample["validation_status"]="machine_stratified_audit_not_human_philological_validation"
sample.to_csv(DATA/"50_epistle_candidate_validation_sample.csv",index=False)
ydump({"sample_rows":int(sample.shape[0]),"stratum_counts":sample["sample_stratum"].value_counts().to_dict(),"machine_audit_class_counts":sample["machine_audit_class"].value_counts().to_dict(),"formula_risk_counts_in_top500":top["formula_risk"].value_counts().to_dict(),"targeted_case_rows":int(target.shape[0]),"warning":"machine triage; not human philological validation"}, DATA/"51_epistle_candidate_validation_summary.yaml")
ydump({"formula_risk_definition":{"high":"known scriptural/liturgical/formulaic overlap risk","medium":"some formula/common-tradition risk","low":"less likely formula-only but still needs close reading"},"top500_formula_counts":top["formula_risk"].value_counts().to_dict(),"targeted_formula_counts":target["formula_risk"].value_counts().to_dict()}, DATA/"53_epistle_formula_risk_model.yaml")

# MorphGNT parse, units, Mark-Luke morphology audit, targeted epistle morph audit.
CONTENT_POS_PREFIXES=("N","V","A","D")
BOOK_FILES={"Matt":"61-Mt-morphgnt.txt","Mark":"62-Mk-morphgnt.txt","Luke":"63-Lk-morphgnt.txt","John":"64-Jn-morphgnt.txt","1Cor":"67-1Co-morphgnt.txt","Eph":"70-Eph-morphgnt.txt","1Tim":"75-1Ti-morphgnt.txt","2Tim":"76-2Ti-morphgnt.txt","Heb":"79-Heb-morphgnt.txt","Jas":"80-Jas-morphgnt.txt","1John":"83-1Jn-morphgnt.txt"}
def parse_morph(path,book):
    rows=[]
    for line in open(path,encoding="utf-8"):
        parts=line.strip().split()
        if len(parts)!=7: continue
        bcv,pos,parse,text,word,norm,lemma=parts; chap=int(bcv[2:4]); verse=int(bcv[4:6])
        rows.append({"book":book,"ref":f"{book} {chap}:{verse}","chapter":chap,"verse":verse,"bcv":bcv,"pos":pos,"parse":parse,"text":text,"word":word,"norm":strip_accents(norm),"lemma":strip_accents(lemma),"is_content":pos.startswith(CONTENT_POS_PREFIXES),"is_mark_long_ending":book=="Mark" and chap==16 and verse>=9})
    return pd.DataFrame(rows)
morph_df=pd.concat([parse_morph(MORPH/fn,book) for book,fn in BOOK_FILES.items() if (MORPH/fn).exists()],ignore_index=True)
morph_df.to_csv(DATA/"80_morphgnt_token_layer_selected_books.csv.gz",index=False,compression="gzip")
units=[]
for (book,ref,chapter,verse),g in morph_df.groupby(["book","ref","chapter","verse"],sort=False):
    units.append({"book":book,"ref":ref,"chapter":int(chapter),"verse":int(verse),"token_count_morphgnt":int(len(g)),"content_token_count_morphgnt":int(g["is_content"].sum()),"normalized_tokens_morphgnt":" ".join(g["norm"].tolist()),"content_tokens_morphgnt":" ".join(g.loc[g["is_content"],"norm"].tolist()),"lemma_tokens_all":" ".join(g["lemma"].tolist()),"lemma_tokens_content":" ".join(g.loc[g["is_content"],"lemma"].tolist()),"pos_sequence":" ".join(g["pos"].tolist()),"long_ending_status":"long_ending" if bool(g["is_mark_long_ending"].any()) else "main_text"})
morph_units=pd.DataFrame(units); morph_units.to_csv(DATA/"81_morphgnt_verse_units_selected_books.csv",index=False); unit_by_ref=morph_units.set_index("ref").to_dict(orient="index")
ml_primary=pd.read_csv(INP/P["mkl_primary"])
audit=[]
for _,r in ml_primary.iterrows():
    a=toks(unit_by_ref.get(r.source_ref,{}).get("lemma_tokens_content","")); b=toks(unit_by_ref.get(r.target_ref,{}).get("lemma_tokens_content","")); met=metric_row(a,b,"lemma")
    row={k:r[k] for k in ["chain_rank","source_ref","target_ref","score","max_exact_run_len","max_exact_run","shared_content_token_count","source_text_critical_status"] if k in r}; row.update(met); row["lemma_minus_surface_score"]=round(met["lemma_score"]-float(r["score"]),4); row["lemma_retains_or_improves_surface_signal"]=met["lemma_score"]>=float(r["score"])-0.02; row["source_lemma_tokens_content"]=" ".join(a); row["target_lemma_tokens_content"]=" ".join(b); audit.append(row)
ml_lemma_audit=pd.DataFrame(audit); ml_lemma_audit.to_csv(DATA/"82_mark_luke_primary_chain_morphology_audit.csv",index=False)
ml_full=pd.read_csv(INP/P["mkl_matrix"]); ml_full_default=ml_full[ml_full.source_text_critical_status!="long_ending"].copy(); cand=ml_full_default[(ml_full_default.score>=0.12)|(ml_full_default.max_exact_run_len>=2)|(ml_full_default.shared_content_token_count>=2)].copy()
lemma_rows=[]
for _,r in cand.iterrows():
    a=toks(unit_by_ref.get(r.source_ref,{}).get("lemma_tokens_content","")); b=toks(unit_by_ref.get(r.target_ref,{}).get("lemma_tokens_content","")); met=metric_row(a,b,"lemma")
    if met["lemma_score"]>=0.12 or float(r.score)>=0.18 or met["lemma_max_exact_run_len"]>=2:
        row=r.to_dict(); row.update(met); row["lemma_minus_surface_score"]=round(met["lemma_score"]-float(r.score),4); lemma_rows.append(row)
lemma_cand=pd.DataFrame(lemma_rows).sort_values(["lemma_score","score"],ascending=False); lemma_cand.to_csv(DATA/"83_mark_luke_morphology_candidate_pairs.csv.gz",index=False,compression="gzip")
surface_high=set(zip(ml_full_default[ml_full_default.score>=0.25]["source_ref"],ml_full_default[ml_full_default.score>=0.25]["target_ref"])); lemma_high=set(zip(lemma_cand[lemma_cand.lemma_score>=0.25]["source_ref"],lemma_cand[lemma_cand.lemma_score>=0.25]["target_ref"]))
ydump({"token_layer_rows":int(morph_df.shape[0]),"verse_unit_rows":int(morph_units.shape[0]),"mark_luke_primary_chain":{"pairs_audited":int(ml_lemma_audit.shape[0]),"surface_score_mean":round(float(ml_lemma_audit["score"].mean()),4),"lemma_score_mean":round(float(ml_lemma_audit["lemma_score"].mean()),4),"lemma_improves_or_retains_count":int(ml_lemma_audit["lemma_retains_or_improves_surface_signal"].sum()),"lemma_worse_count":int((~ml_lemma_audit["lemma_retains_or_improves_surface_signal"]).sum()),"mean_lemma_minus_surface_score":round(float(ml_lemma_audit["lemma_minus_surface_score"].mean()),4)},"mark_luke_candidate_threshold_comparison_score_ge_0_25":{"surface_high_pairs":len(surface_high),"lemma_high_pairs":len(lemma_high),"overlap_pairs":len(surface_high&lemma_high),"surface_only_pairs":len(surface_high-lemma_high),"lemma_only_pairs":len(lemma_high-surface_high)},"limitations":["lemma score is audit metric, not replacement pipeline","no full morphology-based chain rebuild is claimed"]}, DATA/"84_morphology_rerun_summary.yaml")
def parse_ref_range(ref):
    m=re.match(r"^([1-3]?[A-Za-z]+)\s+(\d+):(\d+)(?:-(\d+))?$",str(ref).strip())
    if not m: return [ref]
    book,ch,v1,v2=m.group(1),int(m.group(2)),int(m.group(3)),m.group(4)
    return [f"{book} {ch}:{v}" for v in range(v1,int(v2 or v1)+1)]
def concat_lemma(ref):
    out=[]
    for r in parse_ref_range(ref): out+=toks(unit_by_ref.get(r,{}).get("lemma_tokens_content",""))
    return out
trows=[]
for _,tr in target.iterrows():
    a=concat_lemma(tr.source_ref); b=concat_lemma(tr.target_ref); met=metric_row(a,b,"lemma"); row=tr.to_dict(); row.update(met); row["lemma_minus_prior_score"]=round(met["lemma_score"]-float(tr.score),4); row["source_lemma_content_tokens"]=" ".join(a); row["target_lemma_content_tokens"]=" ".join(b); trows.append(row)
pd.DataFrame(trows).to_csv(DATA/"52_epistle_targeted_cases_morphology_audit.csv",index=False); shutil.copy2(DATA/"52_epistle_targeted_cases_morphology_audit.csv",DATA/"85_epistle_targeted_cases_morphology_audit.csv")

# Apocrypha roadmap and conclusions.
ydump({"status":"not a completed primary-text analysis layer","why_not_fully_addressed_here":["no critical primary text layer for non-Thomas apocrypha","prior apocrypha file is inventory, not parsed aligned corpus"],"recommended_next_ingestion_priorities":[{"text":"Gospel of Peter","priority":"high"},{"text":"Protevangelium of James","priority":"medium_high"},{"text":"Infancy Gospel of Thomas","priority":"medium"},{"text":"Gospel of Nicodemus / Acts of Pilate","priority":"medium"}]}, DATA/"60_apocrypha_analysis_status_and_ingestion_roadmap.yaml")
ydump({"scope":"data-analysis conclusions after this patch; visualization changes not included","claims":[{"claim_id":"mark_matthew_mark_like_priority","confidence":"high","conclusion":"Matthew most likely used Mark or a Mark-like written narrative source."},{"claim_id":"mark_luke_mark_prior_direct_model","confidence":"medium_high for Mark-prior over Luke-prior among direct-use models; medium for direct-use over shared-tradition alone","conclusion":"Mark-prior is lower burden than Luke-prior among direct-use explanations. Direct Mark-like source dependence becomes lower than shared tradition only when shared tradition is charged for dense narrative order and bridge sequences."},{"claim_id":"matt_luke_double_tradition","confidence":"medium_high for shared non-Markan sayings/tradition; medium for any discrete Q-document claim","conclusion":"After Markan masking, the retained Matthew-Luke material remains a non-Markan sayings/echo problem rather than a stable narrative-chain relationship."},{"claim_id":"john_synoptic_pairwise","confidence":"medium","conclusion":"John shares anchor traditions with the Synoptics; aggregate anchor ledgers favor shared anchor/passion/sign tradition over simple Gospel-to-Gospel copying."},{"claim_id":"thomas","confidence":"medium for overlapping sayings tradition, low for global direction","conclusion":"Thomas remains a curated logion-level sayings-network witness; current data cannot support automatic Greek-Coptic direct-dependence."},{"claim_id":"epistles_gospels","confidence":"high for selected targeted cases, exploratory for top-500","conclusion":"1Tim 5:18/Luke 10:7 remains a high-value Luke-like saying case; formula-risk filtering remains essential."}]}, ROOT/"reports/updated_data_analysis_conclusions.yaml")

print("Rebuilt data-analysis patch files in", DATA)
