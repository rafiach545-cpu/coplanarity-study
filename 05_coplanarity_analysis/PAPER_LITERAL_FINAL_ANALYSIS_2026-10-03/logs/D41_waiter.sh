#!/bin/bash
# D41: wait for the main run (3000 events) to end, then run the showered sensitivity (inputs copied to inputs_D41/).
cd /home/rafia/coplanarity_study/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03
while pgrep -f "D41_ew_lo_ratio_pipeline.py .*unweighted_events.lhe.gz mg5_373_lo$" > /dev/null; do sleep 60; done
echo "$(date) main run ended; checkpoint lines: $(wc -l < logs/D41_mg5_373_lo_events.jsonl)"
if [ "$(wc -l < logs/D41_mg5_373_lo_events.jsonl)" -ge 3000 ]; then
  NWORKERS=3 nice python3 scripts/D41_ew_lo_ratio_pipeline.py inputs_D41/EW_B_mg5_373_ptj200_py8317_noMatch.csv mg5_373_lo_showered > logs/D41_showered_stdout.log 2>&1
  echo "$(date) showered run ended"
else
  echo "$(date) main run ended before 3000 events; showered run NOT started"
fi
