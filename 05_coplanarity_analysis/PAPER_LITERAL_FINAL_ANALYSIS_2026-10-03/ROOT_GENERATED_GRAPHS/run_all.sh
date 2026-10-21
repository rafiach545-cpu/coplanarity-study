#!/bin/bash
# Run every figure macro with ROOT in batch mode (from this folder) and keep one log per macro.
cd "$(dirname "$0")"
source /home/rafia/miniconda3/etc/profile.d/conda.sh && conda activate /home/rafia/miniconda3/envs/root-env
echo "ROOT $(root-config --version)" > logs/run_all.log
rm -f macros/*_C.so macros/*_C.d macros/*_C_ACLiC_dict_rdict.pcm
for m in fig3 fig4 fig5 fig6 fig7; do
  root -l -b -q "macros/$m.C+" > logs/$m.log 2>&1; echo "$m exit $?" >> logs/run_all.log
done
cat logs/run_all.log
