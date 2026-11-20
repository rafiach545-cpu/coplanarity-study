#!/bin/bash
# 09 server driver (2026-11-20): one background chunk end to end: B01 (MG5 + Pythia8) -> B03 (hits, planes, 'all' and 'orp') -> B09 (cleaning
# variants c100 / cinf / iso / iso20). Run many chunks side by side, e.g.  seq 11 60 | xargs -P 8 -I{} ./server_chunk.sh zvv {}
# Needs: conda envs mg5 and g4 (env/), COPLANARITY_BASE and HEP_TOOLS exported, MG5 in $HEP_TOOLS/MG5_aMC_v3_7_3.
# Env vars: NEV (10000), MG5_CORES (2), WORKERS (2), KEEP_HEPMC (0: the HepMC is deleted after B09; regenerable from the seed).
set -euo pipefail; S=$1; C=$2; cd "$(dirname "$0")"; mkdir -p logs
NEV=${NEV:-10000}; MG5_CORES=${MG5_CORES:-2}; WORKERS=${WORKERS:-2}; KEEP_HEPMC=${KEEP_HEPMC:-0}
CB=$(conda info --base); PYMG5=$CB/envs/mg5/bin/python; PYG4=$CB/envs/g4/bin/python; T=$(printf %02d $C); P=$([ "$S" = zvv ] && echo "" || echo "${S}_")
[ -f data/${P}B09_events_c$T.csv ] && { echo "$S chunk $C already done"; exit 0; }
$PYMG5 B01_generate_zvv.py 1 $C --nev $NEV --sample $S --cores $MG5_CORES > logs/${P}B01_c$T.log 2>&1
$PYG4 B03_hits_and_planes.py $C --workers $WORKERS --sample $S > logs/${P}B03_c$T.log 2>&1
$PYG4 B09_cleaning_variants_bkg.py $C --workers $WORKERS --sample $S > logs/${P}B09_c$T.log 2>&1
H=$($PYG4 -c "import paths09 as P, pandas as pd; c=pd.read_csv('data/'+P.SAMPLES['$S']['chunks']).set_index('chunk'); print(P.hepmc_of('$S', $C, c.loc[$C,'hepmc']))")
[ "$KEEP_HEPMC" = 1 ] || rm -f -- "${H:?}"
echo "$S chunk $C done: $(grep '^B09 chunk' logs/${P}B09_c$T.log)"
