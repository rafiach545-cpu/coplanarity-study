#!/bin/bash
# 09: B07 pT-threshold cleaning on all Z(nunu)+jets chunks 0-10
set -e; cd "$(dirname "$0")"; PY=/home/rafia/miniconda3/envs/hep/bin/python
for c in $(seq 0 10); do $PY B07_cleaning_pt_threshold_bkg.py $c --workers 7 > logs/B07_c$(printf %02d $c).log 2>&1; tail -2 logs/B07_c$(printf %02d $c).log | head -1; done
echo RUNB07_EXIT=0
