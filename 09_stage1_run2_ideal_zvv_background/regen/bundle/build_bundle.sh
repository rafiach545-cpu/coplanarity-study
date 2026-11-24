#!/bin/bash
# Build regen_overnight.tar.gz (laptop, 2026-11-23). The tarball contains only regen_dop853/:
#   run_overnight.sh, launch07_dop853.py, scripts/, ref/ (laptop S10 reference), base/ (self-contained copy of the code and inputs,
#   used as COPLANARITY_BASE on the server), base/hep_tools/ (the 2.1 GB HepMC inputs of steps B and D).
# Usage: build_bundle.sh <stage dir> [nohepmc]   (nohepmc: for the laptop dry run; the tarball is only written with HepMC)
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$SRC/../../.." && pwd)"; HT=/home/rafia/hep_tools
ST="$1"; MODE="${2:-full}"; D="$ST/regen_dop853"; B="$D/base"
[ -e "$D" ] && { echo "stage $D exists"; exit 2; }
mkdir -p "$B"
cp -a "$SRC/regen_dop853/." "$D/"; cp "$REPO/09_stage1_run2_ideal_zvv_background/regen/launch07_dop853.py" "$D/"
mkdir -p "$D/ref"; cp "$REPO/09_stage1_run2_ideal_zvv_background/g4/out_G01/G07/ref_g4env/EW_800gev_L7-10_FS10_n16.jsonl" "$D/ref/"   # laptop, env g4 (the server env), DOP853 S10
cd "$REPO"
put() { for f in "$@"; do [ -e "$f" ] || { echo "missing $f"; exit 3; }; mkdir -p "$B/$(dirname "$f")"; cp -a "$f" "$B/$f"; done; }
P5=05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03; FO=05_coplanarity_analysis/PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02
# code
put 02_backgrounds/pileup/*.py 02_backgrounds/photon_conversion/*.py 03_trajectory_sim/*.py 03_trajectory_sim/quirk_dop853_coefficients.npz 04_detector_sim/*.py
put 05_coplanarity_analysis/*.py $P5/scripts/*.py $P5/config/* $FO/scripts/*.py
put 07_atlas_real_geometry/sim/*.py 07_atlas_real_geometry/signal/*.py 07_atlas_real_geometry/reach/*.py 07_atlas_real_geometry/FIGURES_ROOT_2026-11-17/prepare_data_07.py
put 09_stage1_run2_ideal_zvv_background/*.py 09_stage1_run2_ideal_zvv_background/g4/G07_dt_impact.py
# inputs
put $P5/fig6/inputs/*.csv 07_atlas_real_geometry/signal/inputs_large/* 07_atlas_real_geometry/geometry/*
put 07_atlas_real_geometry/tables/X08_background_used.csv 07_atlas_real_geometry/REPORT_KNAPEN_FIGURES_2026-11-18/data/fig6_reach.csv
[ -f "$SRC/extra_files.txt" ] && while read -r f; do [ -n "$f" ] && put "$f"; done < "$SRC/extra_files.txt"
# old results (references for the checks and the old reach)
put 07_atlas_real_geometry/signal/runs/large_atlas/*.jsonl 07_atlas_real_geometry/signal/runs/large_ideal/*.jsonl
for f in $P5/logs/F6_*gev_events.jsonl $P5/logs/F6_*gev_low_events.jsonl $P5/logs/F6_*gev_high_a_events.jsonl; do put "$f"; done
put 09_stage1_run2_ideal_zvv_background/data/B08_EW_*gev_L0.1-10.csv
if [ "$MODE" != nohepmc ]; then
  for m in 100 200 400 600 800 1000; do
    f=figure6_full_v1_runs/EW_${m}gev/Events/run_fig6/tag_1_pythia8_events.hepmc.gz; mkdir -p "$B/hep_tools/$(dirname $f)"; ln "$HT/$f" "$B/hep_tools/$f"
  done
  for m in 100 400 800 1200; do
    for f in $(cd "$HT" && ls 07_large_runs/EW_${m}gev_c0?/Events/*/tag_1_pythia8_events.hepmc.gz); do mkdir -p "$B/hep_tools/$(dirname $f)"; ln "$HT/$f" "$B/hep_tools/$f"; done
  done
  ( cd "$ST" && tar czf regen_overnight.tar.gz regen_dop853 && md5sum regen_overnight.tar.gz > regen_overnight.tar.gz.md5 )
  echo "bundle: $ST/regen_overnight.tar.gz ($(du -h "$ST/regen_overnight.tar.gz" | cut -f1))"
fi
echo "stage: $D ($(du -sh "$D" | cut -f1))"
