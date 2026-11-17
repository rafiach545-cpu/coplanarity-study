#!/bin/bash
# 07 (2026-11-17): waits until the G02 chain has finished (G02_CHAIN_EXIT=0 in logs/G02_large_samples.log), then runs R00_postprocess.sh final.
# If the chain stops without that line (no G02_large_samples.py process left), it writes R00_WAIT_ABORT and does nothing.
cd "$(dirname "$0")/.."
while true; do
  grep -q "G02_CHAIN_EXIT=0" logs/G02_large_samples.log && break
  pgrep -f "G02_large_samples.py" > /dev/null || { sleep 60; grep -q "G02_CHAIN_EXIT=0" logs/G02_large_samples.log && break; echo "R00_WAIT_ABORT $(date)"; exit 1; }
  sleep 120
done
echo "chain finished $(date)"; bash reach/R00_postprocess.sh final; echo "R00_WAIT_DONE $(date)"
