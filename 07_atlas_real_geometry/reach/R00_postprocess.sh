#!/bin/bash
# 07 post-processing (2026-11-17): reach (R01) -> X02 ideal vs ATLAS -> X08 reach with own background -> plot data (prepare_data_07) -> ROOT figures (make_figures_07) -> tests T11, T09 -> summary (R02). Logs in logs/. Usage: R00_postprocess.sh <tag>
set -e; cd "$(dirname "$0")/.."; T="${1:?tag}"; Q=/home/rafia/venvs/f6fast/bin/python; RQ=/home/rafia/miniconda3/envs/root-env/bin/python
nice $Q reach/R01_reach_07.py > "logs/R01_reach_07_$T.log" 2>&1
nice $Q compare/X02_ideal_vs_atlas.py > "logs/X02_ideal_vs_atlas_$T.log" 2>&1
nice $Q compare/X08_reach_with_background.py > "logs/X08_reach_with_background_$T.log" 2>&1
nice $Q FIGURES_ROOT_2026-11-17/prepare_data_07.py > "logs/prepare_data_07_$T.log" 2>&1
(cd FIGURES_ROOT_2026-11-17 && nice $RQ make_figures_07.py 2>&1 | grep -v "^Info in" > "../logs/make_figures_07_$T.log")
nice $Q tests/T11_grid_consistency.py > logs/T11_grid_consistency.log 2>&1
nice $Q tests/T09_reach_method_stage2.py > logs/T09_reach_method_stage2.log 2>&1
nice $Q reach/R02_results_summary.py > "logs/R02_results_summary_$T.log" 2>&1
echo "R00_DONE $T"
