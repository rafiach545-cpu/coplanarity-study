#!/bin/bash
# 07 test T12 (2026-11-17): the server-ready C01 / S01 (COPLANARITY_BASE, --photons, --pool, --pileup-only, S01 --xsec) with default options must reproduce
# the production runs exactly:
#  (a) atlas mu = 20, SCT both, photons 0-99 = runs/C01_atlas_mu20 chunks 0 and 50 (every column);
#  (b) stage2 mu = 20, SCT A580, photons 0-99 = runs/C01_stage2_A580_mu20 chunks 0 and 50;
#  (c) S01 on runs/C01_atlas_A580_mu50 and runs/C01_stage2_A580_mu50 = tables/S01_*.csv (all earlier columns, rel. diff < 1e-12);
#  (d) --pileup-only (atlas mu = 50, 20 photons): runs, every row has region_element PU_ONLY and n_conv_hits_raw = 0.
# Prints T12_PASS / T12_FAIL.
set -e; cd "$(dirname "$0")/../backgrounds"; W=runs/_T12; rm -rf "${W:?}"; mkdir -p $W
export PYTHIA8DATA=/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc; P=/home/rafia/miniconda3/envs/hep/bin/python; Q=/home/rafia/venvs/f6fast/bin/python
export COPLANARITY_BASE=/home/rafia/coplanarity_study
$P C01_conversion_bkg.py atlas 20 --sct both --first 100 --workers 2 --tag T12a 2>&1 | grep -v "PYTHIA\|^ \*" | tail -1
$P C01_conversion_bkg.py stage2 20 --sct A580 --first 100 --workers 2 --tag T12b 2>&1 | grep -v "PYTHIA\|^ \*" | tail -1
$P C01_conversion_bkg.py atlas 50 --sct Z0 --first 20 --workers 2 --tag T12d --pileup-only 2>&1 | grep -v "PYTHIA\|^ \*" | tail -1
cp ../tables/S01_C01_atlas_A580_mu50.csv ../tables/S01_C01_stage2_A580_mu50.csv $W/
$Q S01_conversion_summary.py runs/C01_atlas_A580_mu50 runs/C01_stage2_A580_mu50 > $W/s01.log
$Q - <<'PY'
import pandas as pd, numpy as np
ok = True
for new, ref in (("runs/C01_atlas_T12a_mu20", "runs/C01_atlas_mu20"), ("runs/C01_stage2_T12b_mu20", "runs/C01_stage2_A580_mu20")):
    for s in ("000000", "000050"):
        a = pd.read_csv(f"{new}/chunk_{s}.csv"); b = pd.read_csv(f"{ref}/chunk_{s}.csv"); same = a.shape == b.shape and a.equals(b); ok &= same
        print(f"{new} chunk {s}: {len(a)} rows, identical: {same}")
for f in ("S01_C01_atlas_A580_mu50.csv", "S01_C01_stage2_A580_mu50.csv"):
    a = pd.read_csv(f"../tables/{f}"); b = pd.read_csv(f"runs/_T12/{f}"); same = len(a) == len(b)
    for c in b.columns:
        if a[c].dtype.kind == "f": same &= bool(np.allclose(a[c].fillna(-1), b[c].fillna(-1), rtol=1e-12, atol=0))
        else: same &= bool((a[c].astype(str) == b[c].astype(str)).all())
    ok &= same; print(f"S01 {f}: identical earlier columns: {same}")
d = pd.read_csv("runs/C01_atlas_T12d_mu50/chunk_000000.csv"); pu = bool((d.region_element == "PU_ONLY").all() and (d.n_conv_hits_raw == 0).all()); ok &= pu
print(f"pile-up only: {len(d)} rows, all PU_ONLY with 0 conversion hits: {pu}; planes {int(d.plane.astype(str).eq('True').sum())}, final {int(d.final.astype(str).eq('True').sum())}")
print("T12_PASS" if ok else "T12_FAIL")
PY
rm -rf runs/C01_atlas_T12a_mu20 runs/C01_stage2_T12b_mu20 runs/C01_atlas_T12d_mu50 "${W:?}"
