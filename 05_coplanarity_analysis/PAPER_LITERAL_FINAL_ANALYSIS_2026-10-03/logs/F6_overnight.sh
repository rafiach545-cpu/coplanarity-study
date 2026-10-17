#!/bin/bash
# Figure 6 overnight run (2026-10-17): low band (0.1-0.7 keV) for all needed points, then mid band (1-10 keV); 9 workers; resumable.
# Not run (bound N_max = L*sigma*eps_trig[*f_charged] < 3 even with eps_fid = eps_reco = 1): EW_1000gev, colored_2400gev.
cd /home/rafia/coplanarity_study/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03
PTS="colored_1800gev EW_800gev colored_1500gev EW_600gev colored_1200gev EW_400gev colored_900gev EW_200gev colored_600gev EW_100gev colored_2100gev"
for t in $PTS; do echo "$(date) low $t"; BAND=low NWORKERS=9 nice python3 scripts/F6_02_grid.py $t >> logs/F6_overnight_stdout.log 2>&1; done
for t in $PTS; do echo "$(date) mid $t"; BAND=mid NWORKERS=9 nice python3 scripts/F6_02_grid.py $t >> logs/F6_overnight_stdout.log 2>&1; done
echo "$(date) ALL DONE"
