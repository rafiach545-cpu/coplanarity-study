#!/bin/bash
# G02 chain (2026-11-16): gen + ext, then prop only if T08 passed.
cd "$(dirname "$0")/.."; Q=/home/rafia/venvs/f6fast/bin/python
$Q signal/G02_large_samples.py gen,ext --cores 8 || { echo G02_CHAIN_STOP_GEN; exit 1; }
while ! grep -q "T08_PASS\|T08_FAIL" logs/T08_g01_input_option.log; do sleep 30; done
grep -q T08_PASS logs/T08_g01_input_option.log || { echo G02_CHAIN_STOP_T08; exit 1; }
$Q signal/G02_large_samples.py prop --workers 4 --workers-high 3 && echo G02_CHAIN_EXIT=0
