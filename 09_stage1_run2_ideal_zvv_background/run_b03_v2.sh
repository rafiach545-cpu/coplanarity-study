#!/bin/bash
# 09: rerun B03 on chunks 0-10 with track_cleaning v2 (SCT-seeded inward pass). v1 outputs are kept in data/v1/.
set -e; cd "$(dirname "$0")"; PY=/home/rafia/miniconda3/envs/hep/bin/python
for c in $(seq 0 10); do $PY B03_hits_and_planes.py $c --workers 8 > logs/B03v2_c$(printf %02d $c).log 2>&1; tail -4 logs/B03v2_c$(printf %02d $c).log; done
echo RUNB03V2_EXIT=0
