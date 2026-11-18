#!/bin/bash
# 07 sensitivity test, second mass point (2026-11-18): as S01_sens_chain.sh (merge adjacency 0 / 1 / 2, station counts), for EW 600 GeV and colored 1500 GeV,
# so that the merge ratio is measured at two masses per channel (with EW 800 and colored 1800 of S01). Band mid (Lambda 1-10 keV), ATLAS and Ideal, laptop.
cd "$(dirname "$0")/.."; Q=/home/rafia/venvs/f6fast/bin/python; export COPLANARITY_BASE=/home/rafia/coplanarity_study G01_SENS_ADJ=0,1,2
for g in atlas stage2; do for t in EW_600gev colored_1500gev; do
  $Q signal/G01_signal_07.py $g $t mid --input signal/inputs_large/${t}_events.csv --out signal/runs/sens_merge/$g --workers 6 || { echo S01b_SENS_FAIL $g $t; exit 1; }
done; done; echo S01b_SENS_EXIT=0
