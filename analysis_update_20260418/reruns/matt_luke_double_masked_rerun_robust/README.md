# Matthew–Luke masked rerun (robust patch)

Default parameters:

```yaml
mask_regime_default: medium
primary_chain_min_score: 0.32
gap_penalty: 0.05
loose_gap_matt: 4
loose_gap_luke: 4
tight_gap_matt: 2
tight_gap_luke: 2
secondary_echo_min_score: 0.45
secondary_echo_top_n: 120

```

Mask regimes:

```yaml
strict: 0.4
medium: 0.355
broad: 0.325

```

Key additions:

- `01b_mask_audit_default_medium.csv`
- `01c_mask_regime_comparison.csv`
- `17_mask_regime_sensitivity.yaml`
- `18_actual_vs_canonical_slots.yaml`