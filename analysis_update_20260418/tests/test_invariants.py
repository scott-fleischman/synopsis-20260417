
from __future__ import annotations
from pathlib import Path
import yaml, json
import pandas as pd

def load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))

def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)

def test_mark_matthew(base: Path):
    d = base/'reruns'/'mark_matthew_rerun_robust'/'data'
    pairs = pd.read_csv(d/'07_primary_chain_pairs.csv')
    assert_true((pairs['score'].between(0,1)).all(), 'Mark-Matthew scores outside [0,1]')
    assert_true(pairs['mark_idx'].is_unique, 'Mark indices not unique in primary chain')
    assert_true(pairs['matt_idx'].is_unique, 'Matt indices not unique in primary chain')
    assert_true((pairs['mark_idx'].diff().fillna(1) >= 0).all(), 'Mark indices not monotonic')
    assert_true((pairs['matt_idx'].diff().fillna(1) >= 0).all(), 'Matt indices not monotonic')
    slots = load_yaml(d/'24_actual_vs_canonical_slots.yaml')
    assert_true(slots['Mark']['actual_unit_count'] <= slots['Mark']['canonical_slot_count'], 'Mark slots inconsistency')
    sens = pd.read_csv(d/'23_sensitivity_score_grid.csv')
    assert_true({'primary_chain_min_score','gap_penalty','pair_count','loose_block_count'} <= set(sens.columns), 'MM sensitivity columns missing')

def test_matt_luke_masked(base: Path):
    d = base/'reruns'/'matt_luke_double_masked_rerun_robust'/'data'
    pairs = pd.read_csv(d/'07_primary_chain_pairs.csv')
    assert_true((pairs['score'].between(0,1)).all(), 'Masked Matt-Luke scores outside [0,1]')
    assert_true(pairs['matt_unmasked_idx'].is_unique, 'Matt masked indices not unique')
    assert_true(pairs['luke_unmasked_idx'].is_unique, 'Luke masked indices not unique')
    mask_cmp = pd.read_csv(d/'01c_mask_regime_comparison.csv')
    strict = int(mask_cmp.loc[mask_cmp['regime']=='strict','matt_masked'].iloc[0])
    medium = int(mask_cmp.loc[mask_cmp['regime']=='medium','matt_masked'].iloc[0])
    broad = int(mask_cmp.loc[mask_cmp['regime']=='broad','matt_masked'].iloc[0])
    assert_true(strict <= medium <= broad, 'Mask regime monotonicity failed for Matthew')
    strict_l = int(mask_cmp.loc[mask_cmp['regime']=='strict','luke_masked'].iloc[0])
    medium_l = int(mask_cmp.loc[mask_cmp['regime']=='medium','luke_masked'].iloc[0])
    broad_l = int(mask_cmp.loc[mask_cmp['regime']=='broad','luke_masked'].iloc[0])
    assert_true(strict_l <= medium_l <= broad_l, 'Mask regime monotonicity failed for Luke')

def test_jtea(base: Path):
    d = base/'reruns'/'jtea_low_verbatim_rerun_robust'/'data'
    cases = load_yaml(d/'07_targeted_case_studies.yaml')
    assert_true(all('automatic_score_supports_claim' in c for c in cases), 'JTEA cases missing automatic support field')
    assert_true(all('philological_case_strength' in c for c in cases), 'JTEA cases missing philological strength field')
    assert_true(all('formula_risk' in c for c in cases), 'JTEA cases missing formula risk')
    links = load_yaml(d/'17_claim_evidence_links.yaml')
    assert_true(len(links) >= len(cases), 'Claim links unexpectedly short')
    formula = pd.read_csv(d/'18_formula_risk_summary.csv')
    assert_true({'layer','formula_risk','count'} <= set(formula.columns), 'Formula risk summary columns missing')

def main():
    base = Path(__file__).resolve().parents[1]
    test_mark_matthew(base)
    test_matt_luke_masked(base)
    test_jtea(base)
    print('ALL TESTS PASSED')

if __name__ == '__main__':
    main()
