#!/bin/bash
# Figure 6 grid (2026-10-17): runs scripts/F6_02_grid.py for the 13 mass points one after the other (benchmarks first); resumable (append-only checkpoints).
cd /home/rafia/coplanarity_study/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03
for t in EW_800gev colored_1800gev EW_400gev colored_1200gev EW_600gev colored_1500gev EW_1000gev colored_2100gev EW_200gev colored_900gev colored_2400gev EW_100gev colored_600gev; do
  echo "$(date) start $t"
  NWORKERS=3 nice python3 scripts/F6_02_grid.py $t >> logs/F6_grid_stdout.log 2>&1
  echo "$(date) end $t (exit $?)"
done
echo "$(date) all done"
