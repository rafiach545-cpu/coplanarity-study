#!/bin/bash
# 09: B09 cleaning variants on the background, chunks 0-10 (4 workers; B08 runs beside it with 2)
cd "$(dirname "$0")"; PY=/home/rafia/miniconda3/envs/hep/bin/python
for c in $(seq 0 10); do $PY B09_cleaning_variants_bkg.py $c --workers 4 > logs/B09_c$(printf %02d $c).log 2>&1; grep "^B09 chunk" logs/B09_c$(printf %02d $c).log; done
echo RUNB09_EXIT=0
