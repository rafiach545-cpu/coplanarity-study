#!/bin/bash
# 07 sensitivity test (2026-11-17): signal with pixel-merge adjacency 0 / 1 / 2 and station counts (multiplicity threshold after the fact).
# EW 800 GeV and colored 1800 GeV (near the A580 reach), band mid (Lambda 1-10 keV), all triggered events, ATLAS and Ideal geometry, laptop.
cd "$(dirname "$0")/.."; Q=/home/rafia/venvs/f6fast/bin/python; export COPLANARITY_BASE=/home/rafia/coplanarity_study G01_SENS_ADJ=0,1,2
for g in atlas stage2; do for t in EW_800gev colored_1800gev; do
  $Q signal/G01_signal_07.py $g $t mid --input signal/inputs_large/${t}_events.csv --out signal/runs/sens_merge/$g --workers 5 || { echo S01_SENS_FAIL $g $t; exit 1; }
done; done; echo S01_SENS_EXIT=0
