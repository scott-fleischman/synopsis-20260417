
from __future__ import annotations
from pathlib import Path
import build_mark_matthew_rerun
import build_matt_luke_double_masked_rerun
import build_jtea_low_verbatim_rerun

def main():
    base = Path(__file__).resolve().parents[1]
    build_mark_matthew_rerun.main(base)
    build_matt_luke_double_masked_rerun.main(base)
    build_jtea_low_verbatim_rerun.main(base)

if __name__ == '__main__':
    main()
