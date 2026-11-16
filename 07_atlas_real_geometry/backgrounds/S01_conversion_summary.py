#!/usr/bin/env python3
"""07 background step S01 (2026-11-15): expected converted-photon background from the C01 runs.
N = L * sum over photons and conversion regions of (sigma_per_photon * p_conv * final), with
  sigma_per_photon = sigma_generated / n_generated = 0.25205262 pb / 10000 (06_.../inputs/zgamma_xsec_13p6TeV.txt; 9130 photons pass MET > 200 GeV),
  p_conv = the material probability of that region (atlas) or the flat 1% (stage2), L = 332 fb^-1 (R13, as the 06 report).
A run over the first n_run of the 9130 photons is scaled to the full sample by 9130 / n_run.
If no event passes: 95% CL upper limit N < L * sigma_per_photon * 9130 * mean(p_conv) * 3 / n_run (Poisson, 0 observed).
Usage: S01_conversion_summary.py <run folder> [<run folder> ...]  -> prints a table and writes tables/S01_<folder name>.csv"""
import os, sys, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."
X = dict(l.split() for l in open("/home/rafia/coplanarity_study/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/inputs/zgamma_xsec_13p6TeV.txt") if l.strip())
SIG = float(X["sigma_generated_pb"]) / 10000.0; L_PB = 332.0e3
for run in sys.argv[1:]:
    d = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{run}/chunk_*.csv"))); d = d[d.status == "ok"]
    T = lambda c: d[c].astype(str) == "True"
    d = d.assign(final_b=T("final"), plane_b=T("plane"), mult_b=T("mult")); rows = []
    for (reg, sct), g in d.groupby(["region", "sct"]):
        n = g.event.nunique(); nf = int(g.final_b.sum()); sc = 9130.0 / n; N = L_PB * SIG * float((g.p_conv * g.final_b).sum()) * sc
        ul = L_PB * SIG * 9130.0 * g.p_conv.mean() * 3.0 / n if nf == 0 else np.nan
        rows.append(dict(run=os.path.basename(run), region=reg, region_elements=",".join(sorted(g.region_element.unique())[:4]), sct=sct, n_photons=n,
                         mean_p_conv=g.p_conv.mean(), planes=int(g.plane_b.sum()), plane_and_mult=int((g.plane_b & g.mult_b).sum()), final=nf,
                         N_bkg_332fb=N, N_UL95_332fb_if_zero=ul))
    S = pd.DataFrame(rows); os.makedirs(f"{ROOT}/tables", exist_ok=True); S.to_csv(f"{ROOT}/tables/S01_{os.path.basename(run)}.csv", index=False)
    pd.set_option("display.width", 250); print(S.to_string(index=False))
