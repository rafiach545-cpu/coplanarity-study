#!/bin/bash
# 07 (2026-11-17): converted-photon background in the Ideal geometry (C01 stage2 mode = 06 S2 conventions: barrel only, flat 1% conversion at the beam pipe,
# T05 reproduces 06 S2 event by event) for the SCT setting A580, which 06 S2 did not run; mu = 0, 20, 50 (as the ATLAS A580 runs). Then S01.
cd "$(dirname "$0")/.."; Q=/home/rafia/venvs/f6fast/bin/python; P=/home/rafia/miniconda3/envs/hep/bin/python; export PYTHIA8DATA=/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc
for mu in 0 20 50; do $P backgrounds/C01_conversion_bkg.py stage2 $mu --sct A580 --tag A580 --workers 8 2>&1 | grep -v "PYTHIA\\|^ \\*"; [ ${PIPESTATUS[0]} -eq 0 ] || { echo "C01_STAGE2_A580_FAIL mu=$mu"; exit 1; }; done
$Q backgrounds/S01_conversion_summary.py backgrounds/runs/C01_stage2_A580_mu0 backgrounds/runs/C01_stage2_A580_mu20 backgrounds/runs/C01_stage2_A580_mu50
echo C01_STAGE2_A580_DONE
