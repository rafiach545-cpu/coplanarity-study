#!/bin/bash
# One lane of the Fig. 6 15-25 keV run (2026-10-18): runs the given points one after the other with 1 in-process worker (numba, positions-only);
# a run killed by the memory watchdog (non-zero exit) is restarted and resumes from its checkpoint (max 6 attempts per point).
cd /home/rafia/coplanarity_study/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03
LANE=$1; shift
for t in "$@"; do
  for a in 1 2 3 4 5 6; do
    echo "$(date) lane $LANE start $t attempt $a"
    BAND=high_a XONLY=1 FAST=1 NWORKERS=1 /home/rafia/venvs/f6fast/bin/python scripts/F6_02_grid.py $t >> logs/F6_highA_stdout_$LANE.log 2>&1
    rc=$?; echo "$(date) lane $LANE end $t exit $rc"
    [ $rc -eq 0 ] && break
    sleep 20
  done
done
echo "$(date) lane $LANE DONE"
