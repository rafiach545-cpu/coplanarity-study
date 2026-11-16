#!/bin/bash
# 07 signal, step S00 (2026-11-16): build the two MG5 process directories that L01_generate.py copies (templates colored_1200gev, EW_400gev)
# on a machine that does not have /home/rafia/hep_tools/S2_13p6TeV_runs.
#   1. installs the quirk UFO model (quirk_model.tar.gz = /home/rafia/hep_tools/MG5_aMC_v3_7_3/models/quirk, without __pycache__) into MG5 if absent;
#   2. runs MG5 with the Stage 2 proc cards (only the output line changed);
#   3. copies the Stage 2 run_card, param_card, pythia8_card (unchanged, sha256 checked) into Cards/.
# Usage: S00_make_templates.sh <MG5 dir> <output dir>     e.g. S00_make_templates.sh $HOME/hep_tools/MG5_aMC_v3_7_3 $HOME/hep_tools/S2_13p6TeV_runs
# MG5 must be 3.7.3 with Pythia8 installed (in MG5: install pythia8), as on the original machine.
set -euo pipefail
MG="${1:?MG5 dir}"; OUT="${2:?output dir}"; HERE="$(cd "$(dirname "$0")" && pwd)"
[ -x "$MG/bin/mg5_aMC" ] || { echo "no $MG/bin/mg5_aMC"; exit 1; }
grep -q "3.7.3" "$MG/VERSION" || echo "WARNING: MG5 version is not 3.7.3: $(cat "$MG/VERSION" | head -2)"
[ -d "$MG/models/quirk" ] || tar -xzf "$HERE/quirk_model.tar.gz" -C "$MG/models"
mkdir -p "$OUT"
for T in colored_1200gev EW_400gev; do
  if [ -d "$OUT/$T" ]; then echo "$OUT/$T exists: not rebuilt"; else
    sed "s#^output .*#output $OUT/$T#" "$HERE/$T/proc_card_mg5.dat" > "$OUT/proc_$T.mg5"
    "$MG/bin/mg5_aMC" "$OUT/proc_$T.mg5" > "$OUT/proc_$T.log" 2>&1
  fi
  for c in run_card.dat param_card.dat pythia8_card.dat; do cp "$HERE/$T/$c" "$OUT/$T/Cards/$c"; done
  (cd "$HERE/$T" && sha256sum run_card.dat param_card.dat pythia8_card.dat) | (cd "$OUT/$T/Cards" && sha256sum -c --quiet) && echo "$T: cards identical to Stage 2"
done
echo S00_DONE
