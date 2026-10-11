#!/bin/bash
cd "$(dirname "$0")/.."
echo "[$(date -u +%FT%TZ)] P10f start" >> logs/P10f_eta_noz.log
/home/rafia/miniconda3/envs/hep/bin/python scripts/P10f_overlay_eta_noz.py >> logs/P10f_eta_noz.log 2>&1; echo "P10f_EXIT=$?" >> logs/P10f_eta_noz.log
