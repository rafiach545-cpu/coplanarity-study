#!/bin/bash
# 09 regen (2026-11-22): full signal regeneration with the error-controlled DOP853 integrator (rtol 1e-10), same events and seeds as before.
# NOT RUN YET. See README.md in this folder for the setup, the checks and the cost.
#   A  13 TeV, 8-layer, quirk hits only (Stage 1 grid, F6 events):   G07 mode S10  -> regen/out/A_13TeV_8layer/
#   B  13 TeV, 8-layer, full events (EW, B08 on the Stage 1 HepMC):  B08 --tag 13TeV_dop853_  -> data/B08_13TeV_dop853_EW_<m>gev.csv
#   C  13.6 TeV, 07 large samples, stage2 (8-layer) and atlas:        launch07_dop853.py -> regen/out/C_13p6TeV_<geom>/
#   D  13.6 TeV, full events (EW, B08 on the 07 10k HepMC):           B08 --tag 13p6TeV_dop853_ -> data/B08_13p6TeV_dop853_EW_<m>gev.csv
# Usage: regen_all.sh <A|B|C|D|all> ; env: NW (workers per job, default 8), PYF (python with numba+scipy+yaml), PYG4 (env g4 python).
set -euo pipefail
cd "$(dirname "$0")"; R=$PWD; N09=$(dirname "$R"); BASE=$(dirname "$N09")
export COPLANARITY_BASE=$BASE QUIRK_INTEGRATOR=dop853
NW=${NW:-8}; PYF=${PYF:-python}; PYG4=${PYG4:-python}; HT=${HEP_TOOLS:-$(dirname "$BASE")/hep_tools}
mkdir -p out logs
EW13="100 200 400 600 800 1000"; COL13="600 900 1200 1500 1800 2100 2400"
EW136="100 200 400 600 800 1000 1200"; COL136="600 900 1200 1500 1800 2100 2400"
LOW=0.1,0.2,0.3,0.5,0.7; MID=1,2,3,4,5,7,10; HIGH=15,20,25,30,35
step=${1:-all}

if [[ $step == A || $step == all ]]; then        # ~16 core-hours
  for t in $(for m in $EW13; do echo EW_${m}gev; done) $(for m in $COL13; do echo colored_${m}gev; done); do
    for L in $MID $LOW $HIGH; do
      NWORKERS=$NW $PYF "$N09/g4/G07_dt_impact.py" $t $L S10 --out "$R/out/A_13TeV_8layer" > "logs/A_${t}_L${L//,/-}.log" 2>&1
    done
  done
fi

if [[ $step == B || $step == all ]]; then        # ~12 core-hours (EW only: there is no colored full-event code)
  for m in $EW13; do
    $PYG4 "$N09/B08_signal_cleaning_scan.py" $m --lambdas $LOW,$MID,$HIGH --workers $NW --tag 13TeV_dop853_ \
      --hepmc-glob "$HT/figure6_full_v1_runs/EW_{m}gev/Events/run_fig6/tag_1_pythia8_events.hepmc.gz" > "logs/B_EW_${m}.log" 2>&1
  done
fi

if [[ $step == C || $step == all ]]; then        # ~120 core-hours (bands as 07: mid, low, high_a = 15, 20, 25 keV)
  for geom in stage2 atlas; do
    for band in mid low high_a; do
      for t in $(for m in $EW136; do echo EW_${m}gev; done) $(for m in $COL136; do echo colored_${m}gev; done); do
        $PYF "$R/launch07_dop853.py" $geom $t $band --input "$BASE/07_atlas_real_geometry/signal/inputs_large/${t}_events.csv" \
          --out "$R/out/C_13p6TeV_${geom}" --workers $NW > "logs/C_${geom}_${t}_${band}.log" 2>&1
      done
    done
  done
fi

if [[ $step == D || $step == all ]]; then        # ~9 core-hours
  for m in 100 400 800 1200; do
    SIGNAL_10K_RUNS="$HT/07_large_runs" $PYG4 "$N09/B08_signal_cleaning_scan.py" $m --lambdas 0.1,1,4,10,25 --workers $NW --tag 13p6TeV_dop853_ \
      > "logs/D_EW_${m}.log" 2>&1
  done
fi
echo "REGEN_${step}_EXIT=0"
