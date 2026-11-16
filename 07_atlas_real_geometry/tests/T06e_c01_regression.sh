#!/bin/bash
# 07 test T06 (e) (2026-11-16): after the D4 code change, C01 (atlas, mu = 20, SCT both) on photons 0-99 must reproduce the production rows of
# runs/C01_atlas_mu20 (made before D4) exactly, every column. Prints T06e_PASS / T06e_FAIL.
set -e; cd "$(dirname "$0")/../backgrounds"
export PYTHIA8DATA=/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc; P=/home/rafia/miniconda3/envs/hep/bin/python
$P C01_conversion_bkg.py atlas 20 --sct both --first 100 --workers 2 --tag T06e 2>&1 | grep -v "PYTHIA\|^ \*"
/home/rafia/venvs/f6fast/bin/python - <<'PY'
import pandas as pd
ok = True
for s in ("000000", "000050"):
    a = pd.read_csv(f"runs/C01_atlas_T06e_mu20/chunk_{s}.csv"); b = pd.read_csv(f"runs/C01_atlas_mu20/chunk_{s}.csv")
    same = a.shape == b.shape and a.equals(b); ok &= same; print(f"chunk {s}: {len(a)} rows, identical to production: {same}")
print("T06e_PASS" if ok else "T06e_FAIL")
PY
