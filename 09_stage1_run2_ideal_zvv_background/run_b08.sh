#!/bin/bash
# 09: B08 signal cleaning scan, EW 800/400/100/1200 GeV (13.6 TeV 10k-generated samples of 07).
# Lambda 0.1-10 keV with 2 workers, then 25 keV with 1 worker (RAM 7 GB; 25 keV trajectories reach the 2e7-step ceiling).
cd "$(dirname "$0")"; PY=/home/rafia/miniconda3/envs/g4/bin/python
for m in 800 400 100 1200; do
  $PY B08_signal_cleaning_scan.py $m --lambdas 0.1,1,4,10 --workers 2 > logs/B08_EW_${m}.log 2>&1; echo "m=$m rc=$?"; grep -E "^m |wall" logs/B08_EW_${m}.log
  [ -f data/B08_EW_${m}gev.csv ] && mv data/B08_EW_${m}gev.csv data/B08_EW_${m}gev_L0.1-10.csv
done
for m in 800 400 100 1200; do
  $PY B08_signal_cleaning_scan.py $m --lambdas 25 --workers 1 > logs/B08_EW_${m}_L25.log 2>&1; echo "m=$m L25 rc=$?"; grep -E "^m |wall" logs/B08_EW_${m}_L25.log
  [ -f data/B08_EW_${m}gev.csv ] && mv data/B08_EW_${m}gev.csv data/B08_EW_${m}gev_L25.csv
done
echo RUNB08_EXIT=0
