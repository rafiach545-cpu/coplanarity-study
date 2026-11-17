#!/bin/bash
# 07 D01 runs (2026-11-17): points and Lambda values of the end-cap-gain diagnostic.
cd "$(dirname "$0")/.."; export COPLANARITY_BASE=/home/rafia/coplanarity_study
for a in "EW_1000gev 4" "colored_900gev 4" "colored_1800gev 4" "EW_400gev 1" "colored_900gev 1" "EW_400gev 15"; do
  /home/rafia/venvs/f6fast/bin/python compare/D01_endcap_gain.py $a --workers 3 || echo "D01_FAIL $a"
done
echo D01_ALL_DONE
