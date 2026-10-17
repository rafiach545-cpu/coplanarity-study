#!/bin/bash
# Figure 6, Lambda = 15-35 keV ("high band") for arXiv:1708.02243 reproduction. Run from the unpacked bundle:  bash RUN_FIG6_HIGH_BAND.sh [NWORKERS]
# NWORKERS: at most (free RAM in GB) / 3 -- at 30-35 keV one trajectory can need ~2-3 GB. Resumable: rerun the same command after an interruption.
set -e
cd "$(dirname "$0")"; export COPLANARITY_BASE="$PWD"
A=05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03
NW=${1:-4}; PY=${PYTHON:-python3}
$PY -c "import numba, numpy, pandas, scipy, yaml, matplotlib; print('python OK, numba', numba.__version__)"
echo "== 1. validation: numba integrator vs the stored v2 results (must say PASSED)"
for t in colored_1800gev EW_800gev EW_100gev colored_900gev; do FAST=1 NWORKERS=$NW $PY $A/scripts/F6_02_grid.py $t 12; done
BAND=low FAST=1 NWORKERS=$NW $PY $A/scripts/F6_02_grid.py EW_600gev 12
NV=12 $PY $A/scripts/F6_06_validate_numba.py
echo "== 2. high band, 11 mass points (EW 1000 and colored 2400 cannot reach 3 events and are not needed)"
for t in colored_1800gev EW_800gev colored_1500gev EW_600gev colored_1200gev EW_400gev colored_900gev EW_200gev colored_600gev EW_100gev colored_2100gev; do
  echo "$(date) high $t"; BAND=high FAST=1 NWORKERS=$NW $PY $A/scripts/F6_02_grid.py $t
done
echo "== 3. grid, reach, figures"
$PY $A/scripts/F6_03_contours.py && $PY $A/scripts/F6_04_summary.py && $PY $A/scripts/F6_05_sensitivity.py && $PY $A/scripts/F6_03_contours.py
echo "DONE. Send back: $A/logs/F6_*_high_events.jsonl, $A/fig6/, $A/FINAL_FIGURES/F6_fig6/, $A/FINAL_FIGURES/F6_kfactor/"
