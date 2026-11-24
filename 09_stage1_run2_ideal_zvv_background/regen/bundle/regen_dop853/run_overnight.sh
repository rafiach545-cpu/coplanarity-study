#!/bin/bash
# regen_dop853/run_overnight.sh (2026-11-23): unattended signal regeneration with the error-controlled DOP853 integrator.
# Run from $COPLANARITY_BASE after `tar xzf regen_overnight.tar.gz`:   bash regen_dop853/run_overnight.sh
# Everything is read from and written to regen_dop853/ only (regen_dop853/base = a self-contained copy of the code and inputs used as
# COPLANARITY_BASE; the repository itself is not read or changed). No git commands; nothing is deleted or overwritten.
# Order: STEP 0 (reproduce the laptop reference; any difference -> report and exit) -> C (13.6 TeV, 8-layer + ATLAS) -> A (13 TeV 8-layer)
#        -> B (13 TeV full events, EW) -> D (13.6 TeV full events, EW) -> checks -> reach -> MORNING_REPORT.md (also written on a crash).
# Env (optional): PY (python of the g4 env; default <conda base>/envs/g4/bin/python), DRYRUN=1 (2 events: step 0 + one point of C + one tiny job of A, B, D),
#   STEP0_TOL_MM (step-0 crossing tolerance, default 1e-6 mm).
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$R"
OUT="$R/out"; LOGS="$R/logs"; REP="$R/MORNING_REPORT.md"; T0=$(date +%s); WHY=""
if [ -e "$OUT" ] || [ -e "$LOGS" ] || [ -e "$REP" ]; then
  echo "regen_dop853: out/, logs/ or MORNING_REPORT.md already exist; refusing to overwrite (move them away to run again)"; exit 2
fi
mkdir "$OUT" "$LOGS"
PY="${PY:-$(conda info --base 2>/dev/null)/envs/g4/bin/python}"
finish() {
  rc=$?; set +e
  "$PY" "$R/scripts/report.py" "$R" "$rc" "$T0" "$WHY" > "$LOGS/report.log" 2>&1 || {
    { echo "# regen_dop853: morning report (fallback)"; echo; echo "- exit code $rc ${WHY:+($WHY)}; the report script failed, see logs/report.log";
      echo "- step 0: $(cat "$OUT/STEP0.txt" 2>/dev/null || echo 'not finished')"; echo "- status: out/status.tsv"; } > "$REP"; }
  echo "regen_dop853 finished (exit $rc). Report: $REP"
}
trap finish EXIT
[ -x "$PY" ] || { WHY="python of the g4 env not found ($PY); set PY=..."; echo "$WHY"; exit 3; }

export COPLANARITY_BASE="$R/base" HEP_TOOLS="$R/base/hep_tools" QUIRK_INTEGRATOR=dop853 PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$R/base/03_trajectory_sim${PYTHONPATH:+:$PYTHONPATH}"
DRY="${DRYRUN:-0}"; NMAX=(); [ "$DRY" = 1 ] && NMAX=(--nmax 2)

# code checksums
( cd "$R"; find run_overnight.sh scripts base -type f \( -name '*.py' -o -name '*.sh' -o -name '*.yaml' -o -name '*.npz' \) -print0 | sort -z | xargs -0 md5sum ) > "$OUT/CODE_MD5.txt"

# python packages (into the g4 env, only if missing; the pip configuration is not changed)
for p in scipy:scipy yaml:pyyaml fastjet:fastjet contourpy:contourpy numba:numba pandas:pandas pythia8:none; do
  mod=${p%%:*}; pkg=${p##*:}
  if ! "$PY" -c "import $mod" 2>/dev/null; then
    if [ "$pkg" = none ]; then WHY="python module $mod missing in the g4 env (install the env from env/g4_lock_linux64.txt)"; echo "$WHY"; exit 4; fi
    echo "installing $pkg"; "$PY" -m pip install --index-url https://pypi.org/simple "$pkg" > "$LOGS/pip_$pkg.log" 2>&1 || { WHY="pip install $pkg failed"; exit 4; }
  fi
done
"$PY" -c "import scipy, yaml, fastjet, contourpy, numba, pandas; print('packages: scipy', scipy.__version__, 'numba', numba.__version__, 'pandas', pandas.__version__)" > "$OUT/PACKAGES.txt"

# workers, disk, deadline
NW=$(( $(nproc) - 4 )); [ "$NW" -lt 1 ] && NW=1
FREE=$(df -P "$R" | awk 'NR==2 {printf "%d", 100 * $4 / ($3 + $4)}')
echo "cores $(nproc), workers $NW, free disk ${FREE}%" | tee "$OUT/MACHINE.txt"
if [ "$FREE" -lt 20 ]; then WHY="free disk ${FREE}% < 20%"; echo "$WHY"; exit 5; fi
read -r DEADLINE DEADLINE_TXT < <("$PY" "$R/scripts/deadline.py"); echo "no new job after $DEADLINE_TXT (China time)" | tee -a "$OUT/MACHINE.txt"

printf "job\tstep\tstatus\tstart\tend\tworkers\ttries\n" > "$OUT/status.tsv"
run_job() {   # run_job <name> <step> <workers> <command...>: retried once; status ok / missing / skipped_deadline
  local name=$1 step=$2 w=$3; shift 3; local s e t=0 st=missing
  s=$(date +%s)
  if [ "$s" -ge "$DEADLINE" ]; then printf "%s\t%s\tskipped_deadline\t%s\t%s\t%s\t0\n" "$name" "$step" "$s" "$s" "$w" >> "$OUT/status.tsv"; return 0; fi
  for t in 1 2; do
    if "$@" >> "$LOGS/$name.log" 2>&1; then st=ok; break; fi
    echo "--- attempt $t failed ($(date))" >> "$LOGS/$name.log"
  done
  e=$(date +%s); printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$name" "$step" "$st" "$s" "$e" "$w" "$t" >> "$OUT/status.tsv"
}
N09="$R/base/09_stage1_run2_ideal_zvv_background"; R7="$R/base/07_atlas_real_geometry"

# ---------------- STEP 0
run_job step0_S10 0 "$NW" env NWORKERS="$NW" "$PY" "$N09/g4/G07_dt_impact.py" EW_800gev 7,10 S10 --nmax 16 --out "$OUT/step0"
if ! "$PY" "$R/scripts/step0_compare.py" "$R/ref/EW_800gev_L7-10_FS10_n16.jsonl" "$OUT/step0/EW_800gev_L7-10_FS10_n16.jsonl" "$OUT" > "$LOGS/step0_compare.log" 2>&1; then
  [ -e "$OUT/STEP0.txt" ] || echo "FAIL: step 0 run or comparison did not complete (see logs/step0_S10.log, logs/step0_compare.log)" > "$OUT/STEP0.txt"
  WHY="STEP 0 failed: $(cat "$OUT/STEP0.txt")"; echo "$WHY"; exit 10
fi
echo "STEP 0: $(cat "$OUT/STEP0.txt")"

EW136="100 200 400 600 800 1000 1200"; COL136="600 900 1200 1500 1800 2100 2400"
EW13="100 200 400 600 800 1000"; COL13="600 900 1200 1500 1800 2100 2400"
LOW=0.1,0.2,0.3,0.5,0.7; MID=1,2,3,4,5,7,10; HIGH=15,20,25,30,35
TAGS136=$(for m in $EW136; do echo EW_${m}gev; done; for m in $COL136; do echo colored_${m}gev; done)
TAGS13=$(for m in $EW13; do echo EW_${m}gev; done; for m in $COL13; do echo colored_${m}gev; done)
if [ "$DRY" = 1 ]; then TAGS136=EW_800gev; fi

# ---------------- C: 13.6 TeV, 07 stage2 (8-layer) and atlas, bands as 07 (mid, low, high_a); A580 / Z0 / Z1160 are all evaluated
for geom in stage2 atlas; do
  for band in mid low high_a; do
    [ "$DRY" = 1 ] && [ "$band" != mid ] && continue
    for t in $TAGS136; do
      run_job "C_${geom}_${t}_${band}" C "$NW" "$PY" "$R/launch07_dop853.py" "$geom" "$t" "$band" --input "$R7/signal/inputs_large/${t}_events.csv" \
        --out "$OUT/C_13p6TeV_${geom}" --workers "$NW" ${NMAX[@]+"${NMAX[@]}"}
    done
  done
done

if [ "$DRY" = 1 ]; then      # dry run: one tiny job of A, B and D as well (2 events), to exercise their code paths
  TAGS13=EW_800gev; MID=4; LOW=; HIGH=; EW13=800; D_MASSES=800; LAM_B=4; LAM_D=4
else
  D_MASSES="100 400 800 1200"; LAM_B="$LOW,$MID,$HIGH"; LAM_D=0.1,1,4,10,25
fi
if true; then
  # ---------------- A: 13 TeV, 8-layer, quirk hits (Stage 1 grid events)
  for t in $TAGS13; do
    for L in $MID $LOW $HIGH; do
      run_job "A_${t}_L${L//,/-}" A "$NW" env NWORKERS="$NW" "$PY" "$N09/g4/G07_dt_impact.py" "$t" "$L" S10 --out "$OUT/A_13TeV_8layer" ${NMAX[@]+"${NMAX[@]}"}
    done
  done
  # ---------------- B: 13 TeV full events (EW)
  for m in $EW13; do
    run_job "B_EW_${m}" B "$NW" "$PY" "$N09/B08_signal_cleaning_scan.py" "$m" --lambdas "$LAM_B" --workers "$NW" --tag 13TeV_dop853_ ${NMAX[@]+"${NMAX[@]}"} \
      --hepmc-glob "$HEP_TOOLS/figure6_full_v1_runs/EW_{m}gev/Events/run_fig6/tag_1_pythia8_events.hepmc.gz"
  done
  # ---------------- D: 13.6 TeV full events (EW)
  for m in $D_MASSES; do
    run_job "D_EW_${m}" D "$NW" env SIGNAL_10K_RUNS="$HEP_TOOLS/07_large_runs" "$PY" "$N09/B08_signal_cleaning_scan.py" "$m" --lambdas "$LAM_D" ${NMAX[@]+"${NMAX[@]}"} \
      --workers "$NW" --tag 13p6TeV_dop853_
  done
fi

# ---------------- checks and reach (always, also with missing jobs)
"$PY" "$R/scripts/checks.py" "$R" > "$LOGS/checks.log" 2>&1 || echo "checks.py failed (see logs/checks.log)"
"$PY" "$R/scripts/reach_new.py" "$R" > "$LOGS/reach_new.log" 2>&1 || echo "reach_new.py failed (see logs/reach_new.log)"
WHY="completed"
