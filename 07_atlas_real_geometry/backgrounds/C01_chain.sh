#!/bin/bash
# 07 C01 production (2026-11-15): Z(nunu)+gamma conversions, atlas configuration, mu = 20, 50, 60 (mu = 0 already done), both SCT settings,
# then the S01 summary of every run. Resumable (C01 skips finished chunks). Log: ../logs/C01_chain.log
set -e; cd "$(dirname "$0")"
export PYTHIA8DATA=/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc; P=/home/rafia/miniconda3/envs/hep/bin/python
for mu in 20 50 60; do
  $P C01_conversion_bkg.py atlas $mu --sct both --workers ${C01_WORKERS:-10} 2>&1 | grep -v "PYTHIA\|^ \*"
done
/home/rafia/venvs/f6fast/bin/python S01_conversion_summary.py runs/C01_atlas_mu0 runs/C01_atlas_mu20 runs/C01_atlas_mu50 runs/C01_atlas_mu60
echo C01_CHAIN_EXIT=0
