#!/bin/bash
# 2026-11-16: the user dropped A580 mu = 60. Waits for the running A580 mu = 50 production (PID given as $1) to finish, then the S01 summary of
# A580 mu = 0/20/50, S02 over all runs (Z0/Z1160 mu = 0-60, A580 mu = 0-50), then the rest of test T07 (3 workers).
cd "$(dirname "$0")"; while kill -0 "$1" 2>/dev/null; do sleep 60; done
Q=/home/rafia/venvs/f6fast/bin/python
$Q S01_conversion_summary.py runs/C01_atlas_A580_mu0 runs/C01_atlas_A580_mu20 runs/C01_atlas_A580_mu50 >> ../logs/C01_chain_A580.log 2>&1
$Q S02_conversion_breakdown.py runs/C01_atlas_mu0 runs/C01_atlas_mu20 runs/C01_atlas_mu50 runs/C01_atlas_mu60 \
   runs/C01_atlas_A580_mu0 runs/C01_atlas_A580_mu20 runs/C01_atlas_A580_mu50 >> ../logs/C01_chain_A580.log 2>&1
echo C01_A580_CHAIN_EXIT=0 >> ../logs/C01_chain_A580.log
cd ..; T07_WORKERS=3 bash tests/T07_run.sh > logs/T07_signal_stage2_reproduction.log 2>&1
