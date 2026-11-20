#!/bin/bash
# 09 (2026-11-20, after the WSL restart): B07 chunks 2-10, then B08 (EW 800/400/100/1200 GeV), one after the other (RAM: 7 GB)
set -e; cd "$(dirname "$0")"; PY=/home/rafia/miniconda3/envs/hep/bin/python
for c in $(seq 2 10); do $PY B07_cleaning_pt_threshold_bkg.py $c --workers 7 > logs/B07_c$(printf %02d $c).log 2>&1; tail -2 logs/B07_c$(printf %02d $c).log | head -1; done
echo RUNB07_EXIT=0
source /home/rafia/miniconda3/etc/profile.d/conda.sh; conda activate g4
for m in 800 400 100 1200; do python B08_signal_cleaning_scan.py $m --workers 4 > logs/B08_EW_${m}.log 2>&1; grep -E "^m |wall" logs/B08_EW_${m}.log; done
echo RUNB08_EXIT=0
