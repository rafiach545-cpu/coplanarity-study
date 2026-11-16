#!/bin/bash
# 07, background step X01 (2026-11-15): LO cross sections of the MET-triggered backgrounds at sqrt(s) = 13.6 TeV with MG5_aMC 3.7.3,
# with the same generator settings as the reproduced Z(nunu)+gamma+j background (/home/rafia/hep_tools/zgamma_background_test, run_02 banner):
# sm model, 4-flavour p/j, NNPDF2.3 LO (nn23lo1), ptj > 20 GeV, |eta_j| < 5, misset > 200 GeV (sum of neutrino pT), dynamical scale -1 (MG5 default).
# Only change: ebeam 6800 GeV. Parton level only (no shower): this gives sigma for the event-count estimate, not events for the detector simulation.
# Processes: zvvj = p p > z j, z > vl vl~ ; wlvj = p p > w+ j / w- j, w > l nu (l = e, mu, ta).
set -e
export PATH=/home/rafia/miniconda3/envs/hep/bin:$PATH
MG=/home/rafia/hep_tools/MG5_aMC_v3_7_3/bin/mg5_aMC
RUNS=/home/rafia/hep_tools/07_bkg_xsec_runs; mkdir -p $RUNS
gen() {   # name, generate lines
  name=$1; shift
  cat > $RUNS/$name.mg5 <<EOT
import model sm
define p = g u c d s u~ c~ d~ s~
define j = g u c d s u~ c~ d~ s~
define vl = ve vm vt
define vl~ = ve~ vm~ vt~
define lall+ = e+ mu+ ta+
define lall- = e- mu- ta-
$@
output $RUNS/$name -f
launch $RUNS/$name
shower=OFF
madspin=OFF
set ebeam1 6800
set ebeam2 6800
set nevents 2000
set iseed 7001
set ptj 20
set etaj 5
set misset 200
set pdlabel nn23lo1
done
EOT
  $MG $RUNS/$name.mg5 > $RUNS/$name.log 2>&1
  grep -m1 "Cross-section" $RUNS/$name.log | sed "s/^/$name: /"
}
gen zvvj "generate p p > z j, z > vl vl~" &
gen wlvj "generate p p > w+ j, w+ > lall+ vl
add process p p > w- j, w- > lall- vl~" &
wait
echo X01_EXIT=0
