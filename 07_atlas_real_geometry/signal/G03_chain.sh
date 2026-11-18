#!/bin/bash
# 07 G03 chain (2026-11-17): wait for the signal sensitivity runs (laptop has 8 GB), then 13 TeV 10k generation + extraction.
cd "$(dirname "$0")/.."
while pgrep -f S01_sens_chain.sh >/dev/null; do sleep 60; done
/home/rafia/miniconda3/envs/hep/bin/python signal/G03_13TeV_large.py gen,ext --cores 8 && echo G03_CHAIN_EXIT=0
