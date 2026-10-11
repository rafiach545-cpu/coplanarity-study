#!/usr/bin/env bash
# usage: shower_screen.sh <ID> <EW_lhe> <COL_lhe> [extra settings lines...]
set -euo pipefail
W=/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02
ID=$1; EWL=$2; COLL=$3; shift 3
for B in EW COL; do
  d=$W/runs/$ID/$B; mkdir -p $d
  lhe=$EWL; [ $B = COL ] && lhe=$COLL
  { cat $W/runs/base_$B.cmd
    for s in "$@"; do
      key=${s%%=*}; key=$(echo $key | xargs)
      echo "! override: $s"
    done
    for s in "$@"; do echo "$s"; done
    echo "Beams:LHEF = $lhe"; } > $d/settings.cmd
  # later lines override earlier ones in Pythia readString order
  (cd $d && PYTHIA8DATA=/home/rafia/hep_tools/MG5_aMC_v3_7_3/HEPTools/pythia8/share/Pythia8/xmldoc \
     $W/driver/shower_py8317 settings.cmd events.csv $B > run.log 2>&1)
  echo "$ID $B $(grep DRIVER_SUMMARY $d/run.log)"
done
