#!/bin/bash
# 07 C01 production (2026-11-16, decision D4): Z(nunu)+gamma conversions, atlas configuration, SCT setting A580 (ATLAS intrinsic 17 / 580 um),
# mu = 0, 20, 50, 60 (same photons, seeds and pile-up as the Z0 / Z1160 runs), then S01 for these runs and S02 for all runs.
# Resumable (C01 skips finished chunks). Log: ../logs/C01_chain_A580.log
set -e; cd "$(dirname "$0")"
export PYTHIA8DATA=/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc; P=/home/rafia/miniconda3/envs/hep/bin/python
for mu in 0 20 50 60; do
  $P C01_conversion_bkg.py atlas $mu --sct A580 --tag A580 --workers ${C01_WORKERS:-10} 2>&1 | grep -v "PYTHIA\|^ \*"
done
Q=/home/rafia/venvs/f6fast/bin/python
$Q S01_conversion_summary.py runs/C01_atlas_A580_mu0 runs/C01_atlas_A580_mu20 runs/C01_atlas_A580_mu50 runs/C01_atlas_A580_mu60
$Q S02_conversion_breakdown.py runs/C01_atlas_mu0 runs/C01_atlas_mu20 runs/C01_atlas_mu50 runs/C01_atlas_mu60 \
   runs/C01_atlas_A580_mu0 runs/C01_atlas_A580_mu20 runs/C01_atlas_A580_mu50 runs/C01_atlas_A580_mu60
echo C01_A580_CHAIN_EXIT=0
