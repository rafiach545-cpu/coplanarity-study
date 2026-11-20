#!/bin/bash
# 09: 100k Z(nunu)+jet events (chunks 1-10, 10k each), then B03 on every chunk. Chunk 0 is the 1k pilot.
set -e; cd "$(dirname "$0")"; PY=/home/rafia/miniconda3/envs/hep/bin/python
for c in $(seq 1 10); do
  $PY B01_generate_zvv.py 1 $c --nev 10000
  $PY B03_hits_and_planes.py $c --workers 8 > logs/B03_c$(printf %02d $c).log 2>&1
  tail -2 logs/B03_c$(printf %02d $c).log
done
echo RUN100K_EXIT=0
