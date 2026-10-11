#!/usr/bin/env bash
# Version-matched EW trigger pilot: shower every LHE input with every variant.
# One variable at a time:
#   S   = Beams:setProductionScalesFromLHEF (on = MG5 3.7.3 interface choice; off = Pythia default / main89)
#   PY  = Pythia 8.317 (frozen samples) or 8.212 (paper LaTeX comment)
#   LHE = MG5 3.7.3 frozen LHE (copies) or MG5 2.3.3 LHE (paper LaTeX comment)
# All other settings: settings_common.cmd (verbatim from the frozen EW2000 run).
set -euo pipefail
P=/home/rafia/hep_tools/EW_VERSION_PILOT_2026-10-02
D317=/home/rafia/hep_tools/MG5_aMC_v3_7_3/HEPTools/pythia8/share/Pythia8/xmldoc
D212=$P/install/pythia8212/share/Pythia8/xmldoc
cd $P/runs
for lhe in "$@"; do
  tag=$(basename "$lhe" .lhe)
  for py in 8317 8212; do
    for S in on off; do
      d=SHOWER_${tag}_py${py}_S${S}
      [ -f "$d/events.csv" ] && continue
      mkdir -p "$d"
      {
        cat settings_common.cmd | sed "s/^Beams:setProductionScalesFromLHEF = on/Beams:setProductionScalesFromLHEF = ${S}/"
        [ "$py" = 8317 ] && echo "StringZ:useOldAExtra = on"
        echo "Beams:LHEF = $lhe"
      } > "$d/settings.cmd"
      if [ "$py" = 8317 ]; then data=$D317; else data=$D212; fi
      (cd "$d" && PYTHIA8DATA=$data ../../driver/quirk_mlm_shower_py${py} settings.cmd events.csv > run.log 2>&1)
      echo "$d $(grep DRIVER_SUMMARY $d/run.log)"
    done
  done
done
