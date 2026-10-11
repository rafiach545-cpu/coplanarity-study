#!/usr/bin/env python3
"""Phase 3: classification of every generation / detector / analysis setting (tables/unresolved_setting_matrix.csv)."""
import csv, os
import pandas as pd
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables", "unresolved_setting_matrix.csv")
ROWS = """setting|benchmark|project_value|paper_text_or_reference|classification|enters_literal_result|effect_tested|notes
EW representation|EW|spin 1/2, colour singlet, Q=-1 (qe-), photon coupling -i e|paper: vector-like (1,1)_1|PAPER-STATED|yes|-|correct
EW Z coupling|EW|SM-electron chiral coupling (left (e/sWcW)(-1/2+sW^2), right e sW/cW)|paper (1,1)_1 vector-like => vector coupling i e sW/cW|PAPER-STATED|frozen samples carry the chiral coupling (IMPLEMENTATION ERROR)|trigger 0.166 with the correct coupling vs 0.174 frozen (Fisher p=0.60); sigma -24%|genuine implementation error; trigger-neutral; matters for cross-section-based results
colored representation|COL|spin 1/2, colour triplet, Q=2/3, QCD-only (QC-g vertex)|paper: (3,1)_2/3; only QCD contributions|PAPER-STATED|yes|-|correct (UFO name QC; cards use t1 = pdg 1000006)
production|both|p p > X X~ @0 + p p > X X~ j @1 (4-flavour p/j)|paper: up to 1 jet; EW Drell-Yan; colored QCD|PAPER-STATED|yes|up to 2 jets / 0 jets tested (paper-contradicting diagnostics)|
matching scheme|both|MLM (ickkw=1); Pythia JetMatchingMadgraph scheme 1|paper: matched using Pythia8|PAPER-STATED (matching) / UNDOCUMENTED (scheme)|frozen value|shower-kT MLM tested|
xqcut|both|30 GeV|none|UNDOCUMENTED|frozen value (unavoidable)|15, 60 GeV tested|
qCut|both|45 GeV|none|UNDOCUMENTED|frozen value (unavoidable)|30, 60, 90 GeV tested|
nJetMax|both|1|paper: up to 1 jet|PAPER-STATED|yes|-|
collision energy|both|13 TeV|none (Run-2 trigger context)|UNDOCUMENTED|frozen value (unavoidable)|14 TeV tested|
PDF|both|NN23LO1|none|UNDOCUMENTED|frozen value (unavoidable)|cteq6l1 tested|
renormalisation/factorisation scale|both|dynamical_scale_choice -1 (CKKW)|none|UNDOCUMENTED|frozen value (unavoidable)|HT/2, x0.5, x2 tested|
Pythia tune|both|Monash (Pythia 8.317 default)|none|UNDOCUMENTED|frozen value (unavoidable)|4C, A14 tested|
generator versions|both|MG5 3.7.3 / Pythia 8.317|TeX comment only: MG5 v2.3.3, Pythia 8.212|UNDOCUMENTED (comment, not paper text)|frozen value|MG5 2.3.3 + Pythia 8.212 tested (EW trigger 0.167)|
LHE production scales|both|setProductionScalesFromLHEF on|none|UNDOCUMENTED|frozen value (unavoidable)|off tested|
ISR pTmaxMatch|both|default|none|UNDOCUMENTED|frozen value|1, 2 tested: inert under LHE + MLM|
hadronisation (colored)|COL|R-hadrons on, decays off|paper: quirk-hadrons (Pythia8)|PAPER-STATED|yes|-|
trigger definition|both|pT of quirk-pair CM system > 200 GeV (strict), final state|paper Sec. III B|PAPER-STATED|yes|hard-process / post-shower / visible-MET / leading-jet variants tested|level not stated; final state = MET-equivalent
trigger denominator|both|matched events|not stated|DERIVED DIRECTLY|yes|trigger/generated rejected (breaks colored)|matched reproduces colored 0.24 in every sample
colored charge requirement|COL|both R-hadrons non-zero charge, between trigger and fiducial|paper: both quirk-hadrons non-zero charge|PAPER-STATED (placement INFERRED)|yes|-|
detector radii|both|33.25, 50.5, 88.5, 122.5, 299, 371, 443, 514 mm|ref [27] + ATLAS JINST; IBL inferred|REFERENCE-STATED / INFERRED (IBL)|yes|-|paper Fig. 4 hit spacing consistent with 8 Run-2 layers
barrel lengths|both|pixel 400.5, SCT 749, IBL 330.15 mm|ref [27]; IBL arXiv:1803.00844|REFERENCE-STATED / INFERRED (IBL)|yes (literal geometry B)|eta-cone systematic|
eta acceptance|both|none (finite barrel only)|paper: barrel only, effectively abs(eta) <~ 1.8|PAPER-STATED as a consequence|no explicit eta cut|eta-cone systematic|
pixel response|both|centre of hit pixel, 50x400 um (IBL 50x250 inferred)|paper + ref [27]|PAPER-STATED + REFERENCE-STATED|yes|-|
SCT response|both|Gaussian 34 um R-phi / 1160 um z|paper: 2 x intrinsic accuracy of ref [27] (17 / 580 um)|PAPER-STATED + REFERENCE-STATED|yes|z 0 / 34 / 580 um envelope|literal reading contradicts paper Fig. 5
pixel merging|both|neighbouring pixels (incl. diagonal) merged to the cluster centroid|paper|PAPER-STATED (details INFERRED)|yes|-|
beam spot|both|common per-event z shift N(0, 45 mm)|paper: uniform gaussian 45 mm on z of all hits|DERIVED DIRECTLY|yes|-|
timing|both|max of 16 crossing times < 25 ns|paper: 25 ns timing cut in eps_fid|PAPER-STATED (location INFERRED)|yes|-|
crossings per layer|both|first outward crossing|paper: most likely intersect each layer only once|INFERRED|yes|-|
plane-finding algorithm|both|literal Sec. III C|paper|PAPER-STATED|yes|growth-rule reference (seed vs current) tested|
Delta_w definition|both|sqrt(lambda_2) (Eq. 11)|paper Eqs. 10-11; paper Fig. 4 quotes 0.5 sqrt(lambda_2)|PAPER-STATED (conflicts with paper figure)|yes (Eq. definition)|W2 convention tested: no effect on any efficiency|
signal region|both|plane; 7 layers with 2 hits + 1 with >=1; Dw<1 cm; Ds<0.01 cm|paper Sec. IV|PAPER-STATED|yes|-|
eps_reco definition|both|full SR / (trigger AND fiducial)|paper Sec. IV|PAPER-STATED|yes|plane-only reported as diagnostic|
pile-up mu|bkg|50|paper|PAPER-STATED|yes|-|
pile-up pool size|bkg|20000 Pythia8 min-bias events|paper: 125000|PAPER-STATED (project value differs)|pool size differs (documented)|-|
pile-up detector simulation|bkg|exact helix, 8 barrel layers, 25 ns per hit, tracking-efficiency suppression; no energy loss / brems / endcaps / TRT / ECAL|paper -> arXiv:1612.00850 App. A (includes energy loss and brems)|PAPER-STATED (project simplification)|simplification retained (documented, effect unquantified)|-|
pile-up pixel merging|bkg|literal: merged; frozen pile-up-only driver: not merged|paper (detector response)|PAPER-STATED|yes (literal)|-|frozen pile-up-only driver omitted merging
conversion sample|bkg|Z(nunu)+gamma+j LO, MET > 200 GeV, sigma 0.231 pb|paper: ~1 pb fiducial (MG5_aMC@NLO)|PAPER-STATED (value differs; UNRESOLVED)|project sigma kept separate|-|
conversion probability|bkg|0.01 per photon (event weight)|paper: ~1 pb -> ~10 fb (PDG Figs. 33.16/33.17)|DERIVED DIRECTLY (ratio of paper numbers)|yes|-|
conversion e+e- simulation|bkg|literal: pile-up detector helix from the beam-pipe conversion point; frozen: signal simulator with Lambda = 0|paper: same detector simulation as for pile-up|PAPER-STATED|yes (literal)|-|
conversion fit origin|bkg|literal: primary vertex; frozen: conversion point|paper Sec. III C: primary vertex at the origin|PAPER-STATED|yes (literal)|conversion-point origin systematic|"""
with open(OUT, "w", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    for r in ROWS.split("\n"):
        parts = r.split("|"); assert len(parts) == 8, r
        w.writerow(parts)
d = pd.read_csv(OUT); print(d.shape); print(d.classification.value_counts().to_dict())
