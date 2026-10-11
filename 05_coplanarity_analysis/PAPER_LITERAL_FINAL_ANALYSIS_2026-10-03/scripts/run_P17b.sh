#!/bin/bash
cd "$(dirname "$0")/.."
echo "[$(date -u +%FT%TZ)] P17b start" >> logs/P17b_overlay_ref34.log
/home/rafia/miniconda3/envs/hep/bin/python scripts/P17b_overlay_ref34.py >> logs/P17b_overlay_ref34.log 2>&1; echo "P17b_EXIT=$?" >> logs/P17b_overlay_ref34.log
