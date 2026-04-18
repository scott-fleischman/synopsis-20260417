# High-priority missing comparison supplement

Package: `synopsis_high_priority_missing_20260418`

This supplement fills the eight high-priority gaps identified in the repository review:

1. Direct **Mark ↔ Luke** package.
2. **John ↔ Mark** pairwise data.
3. **John ↔ Matthew** pairwise data.
4. **John ↔ Luke** pairwise data.
5. Canonical **Gospel relationship square**.
6. **Thomas × Gospel logion matrix**.
7. **Epistle–Gospel case dossier** layer.
8. **Conclusion → evidence → contrary-evidence** navigation.

## Most important outputs

- `data/19_mark_luke_global_summary.yaml`
- `data/11_mark_luke_primary_chain_pairs.csv`
- `data/17_mark_luke_direction_ledger_by_loose_block.yaml`
- `data/38_john_synoptic_pairwise_global_summary.yaml`
- `data/40_canonical_gospel_relationship_square.csv`
- `data/50_thomas_gospel_logion_matrix.csv`
- `data/60_epistle_gospel_case_dossiers.yaml`
- `data/70_conclusion_evidence_contrary_navigation.yaml`
- `visualizations/index.html`

## Main counts

- Mark–Luke full verse matrix rows: 773,277
- Mark–Luke default matrix rows excluding Mark 16:9–20: 759,489
- Mark–Luke primary chain pairs: 183
- Mark–Luke loose / tight blocks: 35 / 76
- John–Mark / John–Matthew / John–Luke full matrix rows: 580,358 / 937,704 / 1,008,822
- Thomas logia represented: 116 total, 46 with curated canonical parallels
- Epistle–Gospel dossiers: 60 total, including 10 targeted cases

## Methodological note

This supplement does not force John, Thomas, or epistolary material into the same method as Mark–Matthew. Mark–Luke is treated as a Synoptic narrative-alignment problem. John is treated as anchor/candidate pairwise evidence. Thomas is treated logion-by-logion. Epistle material is treated case-first with formula risk separated from retrieval support.

## Rebuild

The computational core can be rebuilt with:

```bash
cd synopsis_high_priority_missing_20260418
python scripts/build_high_priority_supplement.py
```

The script is internet-free and uses the included source snapshots in `sources/`.

## Limitations

- The package uses source snapshots and prior artifacts generated in the same thread; it does not newly fetch SBLGNT, MorphGNT, or Coptic Scriptorium data.
- John pairwise analysis is not a continuous chain model.
- Thomas is not automatically Greek-Coptic scored.
- Apocrypha beyond Thomas remains a future package.
