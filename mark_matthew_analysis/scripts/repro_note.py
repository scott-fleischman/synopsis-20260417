"""
This project was generated interactively in Python.

The raw source files used are saved under ../sources/.
The derived files in ../data/ are sufficient for inspection even without rerunning the full pipeline.

Core stages used:
- parse SBLGNT verse text
- parse MorphGNT lemma/morphology rows
- normalize Greek tokens
- compute IDF-weighted lexical and bigram similarities
- compute 3-verse contextual window similarities
- derive a monotonic Mark↔Matthew primary chain
- segment into loose/tight blocks
- compute pair-level diffs and block-level directional ledgers
- attach SBLGNT apparatus notes per verse/pair
"""
