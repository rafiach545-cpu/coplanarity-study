#!/usr/bin/env bash
# Overnight queue: wait for the literal pile-up run (P8) to finish, then run P9 (literal conversion) and
# P10 (literal conversion + mu=50 overlay). Append-only logs; chunk files make every stage resumable.
cd "$(dirname "$0")/.."
until grep -q "P8_EXIT=" logs/P8_literal.log 2>/dev/null; do sleep 30; done
echo "[$(date -u +%FT%TZ)] P9 LITERAL start" >> logs/P9_literal.log
/home/rafia/miniconda3/envs/hep/bin/python scripts/P9_literal_conversion.py LITERAL >> logs/P9_literal.log 2>&1
echo "P9_EXIT=$?" >> logs/P9_literal.log
echo "[$(date -u +%FT%TZ)] P10 start" >> logs/P10_literal.log
/home/rafia/miniconda3/envs/hep/bin/python scripts/P10_literal_overlay.py >> logs/P10_literal.log 2>&1
echo "P10_EXIT=$?" >> logs/P10_literal.log
