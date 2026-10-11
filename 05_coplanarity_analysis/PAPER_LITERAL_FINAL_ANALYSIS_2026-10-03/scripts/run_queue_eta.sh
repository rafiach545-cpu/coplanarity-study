#!/bin/bash
# 2026-10-03 queue: pile-up |eta|<1.8 + merging (P8e), then conversion + pile-up |eta|<1.8, vertex fit (P10e). Existing events only.
cd "$(dirname "$0")/.."
PY=/home/rafia/miniconda3/envs/hep/bin/python
echo "[$(date -u +%FT%TZ)] P8e ETA_MERGE start" >> logs/P8e_eta_merge.log
$PY scripts/P8e_pileup_eta_merge.py ETA_MERGE 5000 >> logs/P8e_eta_merge.log 2>&1; echo "P8e_EXIT=$?" >> logs/P8e_eta_merge.log
echo "[$(date -u +%FT%TZ)] P10e start" >> logs/P10e_eta.log
$PY scripts/P10e_overlay_eta.py >> logs/P10e_eta.log 2>&1; echo "P10e_EXIT=$?" >> logs/P10e_eta.log
