#!/bin/bash
# 07 test T07 driver (2026-11-16): G01 in the stage2 configuration on full Stage 2 samples (all three Lambda bands, colored and EW), then the comparison.
set -e; cd "$(dirname "$0")/../signal"; P=/home/rafia/venvs/f6fast/bin/python; W=${T07_WORKERS:-4}
for a in "EW_800gev mid" "colored_1800gev mid" "colored_900gev high_a" "EW_100gev low" "EW_400gev high_a" "colored_1200gev low"; do
  $P G01_signal_07.py stage2 $a --workers $W 2>&1 | grep -v "^ *[0-9]*/[0-9]*$"
done
cd ..; $P tests/T07_signal_stage2_reproduction.py signal/runs/stage2/G01_EW_800gev_mid.jsonl signal/runs/stage2/G01_colored_1800gev_mid.jsonl \
  signal/runs/stage2/G01_colored_900gev_high_a.jsonl signal/runs/stage2/G01_EW_100gev_low.jsonl signal/runs/stage2/G01_EW_400gev_high_a.jsonl \
  signal/runs/stage2/G01_colored_1200gev_low.jsonl
