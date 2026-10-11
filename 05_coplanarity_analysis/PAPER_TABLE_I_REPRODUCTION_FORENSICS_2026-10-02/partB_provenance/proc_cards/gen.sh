#!/usr/bin/env bash
# usage: gen.sh <ID> <EW|COL> <seed> [key=value ...]   (run_card edits, one setting per screen)
set -euo pipefail
W=/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02
ID=$1; B=$2; SEED=$3; shift 3
T=/home/rafia/hep_tools/quirk_ew_800gev_4kev; [ $B = COL ] && T=/home/rafia/hep_tools/quirk_signal_1800gev_2kev
[ -n "${TEMPLATE_OVERRIDE:-}" ] && T=$TEMPLATE_OVERRIDE
D=$W/proc/${ID}_$B
rsync -a --exclude='Events/*' --exclude='HTML/run_*' $T/ $D/
rm -f $D/Cards/pythia8_card.dat $D/Cards/delphes_card.dat $D/Cards/madspin_card.dat
grep -q '^nb_core' $D/Cards/me5_configuration.txt || echo 'nb_core = 4' >> $D/Cards/me5_configuration.txt
sed -i -E 's/^\s*#?\s*nb_core\s*=.*/nb_core = 4/' $D/Cards/me5_configuration.txt
RC=$D/Cards/run_card.dat
sed -i -E "s/^\s*[0-9]+\s*=\s*nevents\b/  2000 = nevents/; s/^\s*[0-9]+\s*=\s*iseed\b/  $SEED = iseed/" $RC
for kv in "$@"; do k=${kv%%=*}; v=${kv#*=}
  grep -qE "=\s*$k\b" $RC || { echo "KEY $k NOT FOUND"; exit 3; }
  sed -i -E "s/^(\s*)[^=!]*=(\s*$k\b)/\1 $v =\2/" $RC
done
cp $RC $W/proc/${ID}_${B}_run_card_used.dat
# clean rebuild with the hep env toolchain (gcc/gfortran 16.2, same as the source machine)
find $D/lib -maxdepth 1 -name 'lib*.a' -delete
find $D/Source $D/SubProcesses -name '*.o' -delete
find $D/SubProcesses -maxdepth 2 \( -name madevent -o -name madevent_forhel -o -name gensym \) -type f -delete
bash -lc "source /home/rafia/miniconda3/etc/profile.d/conda.sh && conda activate hep && unset PYTHIA8DATA && cd $D && which gfortran && ./bin/generate_events run -f" > $W/logs/gen_${ID}_${B}.log 2>&1
zcat $D/Events/run/unweighted_events.lhe.gz > $W/inputs/${ID}_${B}.lhe
grep -E 'iseed|Integrated weight|Number of Events' $D/Events/run/run_tag_1_banner.txt | head -3 | sed "s/^/$ID $B: /"
