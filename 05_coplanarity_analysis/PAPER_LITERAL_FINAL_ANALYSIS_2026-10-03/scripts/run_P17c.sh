#!/bin/bash
cd "$(dirname "$0")/.."
echo "[$(date -u +%FT%TZ)] P17c start" >> logs/P17c_overlay_ref34_z580.log
/home/rafia/miniconda3/envs/hep/bin/python scripts/P17c_overlay_ref34_z580.py >> logs/P17c_overlay_ref34_z580.log 2>&1; echo "P17c_EXIT=$?" >> logs/P17c_overlay_ref34_z580.log
