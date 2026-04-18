# Mark–Matthew rerun (robust patch)

Default parameters:

```yaml
primary_chain_min_score: 0.25
gap_penalty: 0.05
loose_gap_mark: 4
loose_gap_matt: 7
tight_gap_mark: 3
tight_gap_matt: 3
secondary_echo_min_score: 0.45
secondary_echo_top_n: 250

```

Key outputs are in `data/`.

Most important additions relative to the earlier artifact:

- `00_source_metadata.yaml`
- `15_direction_burden_totals.yaml`
- `22_sensitivity_mark_ending.yaml`
- `23_sensitivity_score_grid.csv`
- `24_actual_vs_canonical_slots.yaml`