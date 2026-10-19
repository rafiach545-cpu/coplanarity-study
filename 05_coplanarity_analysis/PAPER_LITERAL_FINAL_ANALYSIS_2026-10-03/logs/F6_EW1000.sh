#!/bin/bash
# EW 1000 GeV for Figure 6 with the paper's method (matched + shower trigger count), 2026-10-19: low, mid, high_a bands, one process each after the other.
cd /home/rafia/coplanarity_study/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03
for b in low mid high_a; do
  for a in 1 2 3 4; do
    echo "$(date) band $b attempt $a"; BAND=$b XONLY=1 FAST=1 NWORKERS=1 /home/rafia/venvs/f6fast/bin/python scripts/F6_02_grid.py EW_1000gev >> logs/F6_EW1000_stdout.log 2>&1 && break; sleep 20
  done
done
echo "$(date) EW1000 DONE"
