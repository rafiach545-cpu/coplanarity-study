#!/usr/bin/env bash
W=/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02
args=(); T=""
for a in "$@"; do case $a in TEMPLATE=*) T=$W/proc/TEMPLATE_${a#TEMPLATE=};; *) args+=("$a");; esac; done
TEMPLATE_OVERRIDE=$T $W/proc/gen.sh "${args[@]}" || echo "FAILED ${args[*]}"
