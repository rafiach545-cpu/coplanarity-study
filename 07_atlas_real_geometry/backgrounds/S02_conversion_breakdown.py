#!/usr/bin/env python3
"""07 background step S02 (2026-11-16): C01 results with statistical errors and split into barrel-like / end-cap parts.
Same normalisation as S01 (N = L * sigma_per_photon * p_conv * final * N_photons / n; 100k runs: the Z01 cross-section file); stat error = L * sigma_per_photon * sqrt(sum (p_conv * final)^2) * 9130 / n.
'barrel-like' = all 8 winner stations are barrel layers (the only kind Stage 2 can make); 'with end-cap' = at least one station is a disk element.
Also: eta of the conversion point seen from the PV, eta = asinh((z_conv - z0) / r_conv).
Usage: S02_conversion_breakdown.py <run folder> ...  -> prints a table and writes tables/S02_conversion_breakdown.csv"""
import os, sys, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."
def xsec(f):                                                                   # (sigma per generated event, photons after MET), as S01 --xsec
    X = dict(l.split()[:2] for l in open(f) if len(l.split()) >= 2); return float(X["sigma_generated_pb"]) / float(X.get("n_generated", 10000)), float(X["n_events_after_MET"])
# 2026-11-18: runs with "100k" in the name use the 100k Z01 sample (90 980 photons); the others the 9130-photon sample (unchanged numbers)
XS = {"9130": xsec("/home/rafia/coplanarity_study/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/inputs/zgamma_xsec_13p6TeV.txt"),
      "100k": xsec(f"{HERE}/inputs_zgamma_large/zgamma_xsec_large.txt")}
L_PB = 332.0e3; rows = []
for run in sys.argv[1:]:
    d = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{run}/chunk_*.csv"))); d = d[d.status == "ok"]
    d = d.assign(fin=d.final.astype(str) == "True", endcap=d.winner_stations.astype(str).str.contains("SCTD|PixD", regex=True),
                 eta=np.arcsinh((d.conv_z_cm - d.z0_cm) / d.conv_r_cm))
    for (reg, sct), g in d.groupby(["region", "sct"]):
        SIG, NPH = XS["100k" if "100k" in os.path.basename(run) else "9130"]; sc = L_PB * SIG * NPH / g.event.nunique(); w = g.p_conv * g.fin
        for part, m in (("all", np.ones(len(g), bool)), ("barrel-like", ~g.endcap), ("with end-cap", g.endcap)):
            rows.append(dict(run=os.path.basename(run), region=reg, sct=sct, part=part, final=int((g.fin & m).sum()),
                             final_abs_eta_lt_1=int((g.fin & m & (g.eta.abs() < 1)).sum()),
                             N_332fb=sc * float(w[m].sum()), N_stat=sc * float(np.sqrt((w[m] ** 2).sum()))))
S = pd.DataFrame(rows); S.to_csv(f"{ROOT}/tables/S02_conversion_breakdown.csv", index=False)
pd.set_option("display.width", 250); print(S[S.sct == "Z0"].to_string(index=False))
T = S[(S.part == "all")].groupby(["run", "sct"]).apply(lambda g: pd.Series(dict(N_total=g.N_332fb.sum(), N_stat=np.sqrt((g.N_stat ** 2).sum()))))
print(T.to_string())
