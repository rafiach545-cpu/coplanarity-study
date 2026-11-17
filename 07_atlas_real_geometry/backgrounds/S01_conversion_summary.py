#!/usr/bin/env python3
"""07 background step S01 (2026-11-15): expected converted-photon background from the C01 runs.
N = L * sum over photons and conversion regions of (sigma_per_photon * p_conv * final), with
  sigma_per_photon = sigma_generated / n_generated = 0.25205262 pb / 10000 (06_.../inputs/zgamma_xsec_13p6TeV.txt; 9130 photons pass MET > 200 GeV),
  p_conv = the material probability of that region (atlas) or the flat 1% (stage2), L = 332 fb^-1 (R13, as the 06 report).
A run over the first n_run of the 9130 photons is scaled to the full sample by 9130 / n_run.
If no event passes: 95% CL upper limit N < L * sigma_per_photon * 9130 * mean(p_conv) * 3 / n_run (Poisson, 0 observed).
Usage: S01_conversion_summary.py [--xsec FILE] <run folder> [<run folder> ...]   (FILE keys: sigma_generated_pb, n_events_after_MET, optional n_generated (default 10000))
For --pileup-only runs (region_element PU_ONLY) read pass_prob_per_event / pass_prob_UL95_if_zero, not N_bkg.  -> prints a table and writes tables/S01_<folder name>.csv"""
import os, sys, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."
BASE = os.environ.get("COPLANARITY_BASE", "/home/rafia/coplanarity_study")
ARGS = sys.argv[1:]; XF = f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/inputs/zgamma_xsec_13p6TeV.txt"
if "--xsec" in ARGS: k = ARGS.index("--xsec"); XF = ARGS[k + 1]; del ARGS[k:k + 2]                  # 2026-11-17: other photon samples (e.g. 100k)
X = dict(l.split() for l in open(XF) if l.strip())
NGEN = float(X.get("n_generated", 10000)); NPH = float(X["n_events_after_MET"])                        # defaults reproduce the 9130-photon sample
SIG = float(X["sigma_generated_pb"]) / NGEN; L_PB = 332.0e3
for run in ARGS:
    d = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{run}/chunk_*.csv"))); d = d[d.status == "ok"]
    T = lambda c: d[c].astype(str) == "True"
    d = d.assign(final_b=T("final"), plane_b=T("plane"), mult_b=T("mult")); rows = []
    for (reg, sct), g in d.groupby(["region", "sct"]):
        n = g.event.nunique(); nf = int(g.final_b.sum()); sc = NPH / n; N = L_PB * SIG * float((g.p_conv * g.final_b).sum()) * sc
        ul = L_PB * SIG * NPH * g.p_conv.mean() * 3.0 / n if nf == 0 else np.nan
        rows.append(dict(run=os.path.basename(run), region=reg, region_elements=",".join(sorted(g.region_element.unique())[:4]), sct=sct, n_photons=n,
                         mean_p_conv=g.p_conv.mean(), planes=int(g.plane_b.sum()), plane_and_mult=int((g.plane_b & g.mult_b).sum()), final=nf,
                         N_bkg_332fb=N, N_UL95_332fb_if_zero=ul, pass_prob_per_event=nf / n, pass_prob_UL95_if_zero=(3.0 / n if nf == 0 else np.nan)))
    S = pd.DataFrame(rows); os.makedirs(f"{ROOT}/tables", exist_ok=True); S.to_csv(f"{ROOT}/tables/S01_{os.path.basename(run)}.csv", index=False)
    pd.set_option("display.width", 250); print(S.to_string(index=False))
