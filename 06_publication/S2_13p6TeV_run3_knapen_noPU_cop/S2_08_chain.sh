#!/bin/bash
# Stage 2: 13.6 TeV converted photons, then all background runs (mu = 0, 20, 50, 60). Log: logs/S2_08_chain.log
set -e; cd "$(dirname "$0")"; P=/home/rafia/miniconda3/envs/hep/bin/python
$P S2_06_zgamma_generate.py 13p6TeV 6800
mkdir -p inputs/zgamma_13p6TeV; cp inputs/zgamma_photons_13p6TeV.csv inputs/zgamma_13p6TeV/zgamma_photons.csv
$P S2_08_background.py P10 0; $P S2_08_background.py P17b 0
for mu in 20 50 60; do for r in P10 P17b P8; do $P S2_08_background.py $r $mu; done; done
echo CHAIN_EXIT=0
