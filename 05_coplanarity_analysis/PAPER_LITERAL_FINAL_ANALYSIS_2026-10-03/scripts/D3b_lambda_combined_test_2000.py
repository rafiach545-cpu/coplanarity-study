#!/usr/bin/env python3
"""D3 for the report scope: 2000-event samples only (COL2000, EW2000), the report's two SCT z settings (1.16 mm, none) and both hit readings
(first crossing; every crossing with >= 2 hits). Same statistics as D3: naive binomial G-test and a correlated chi2 with the correlation of the
eps vector from an event-level bootstrap (10 000 resamples); paper values taken as exact; dof = number of Lambda points.
Inputs: tables/lambda_scan_per_event.csv (SCT z none), tables/lambda_scan_z1160_per_event.csv (1.16 mm). Output: tables/lambda_scan_combined_test_2000.csv"""
import os, numpy as np, pandas as pd
from scipy import stats
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
PAPER = {"EW": {1: .11, 2: .41, 3: .65, 4: .72, 5: .74}, "COL": {1: .083, 2: .35, 3: .59, 5: .74, 10: .58}}
d = pd.concat([pd.read_csv(f"{T}/lambda_scan_per_event.csv"), pd.read_csv(f"{T}/lambda_scan_z1160_per_event.csv")])
d = d[d["sample"].isin(["COL2000", "EW2000"])]; d["benchmark"] = d["sample"].str[:-4]; TR = lambda s: s.astype(str) == "True"
SETUPS = [("SCT z 1.16 mm, first crossing", "FIRST", "Z1160"), ("no SCT z smearing, first crossing", "FIRST", "Z0"),
          ("SCT z 1.16 mm, every crossing (>= 2)", "ALL", "Z1160"), ("no SCT z smearing, every crossing (>= 2)", "ALL", "Z0")]
rng = np.random.default_rng(20261009); rows = []
for lab, mode, sct in SETUPS:
    tot = dict(G=0.0, C=0.0, dof=0)
    for b, P in PAPER.items():
        x = d[(d.benchmark == b) & (d["mode"] == mode) & (d.sct == sct)]; L = sorted(P)
        piv = lambda c: x.pivot_table(index="key", columns="lambda_keV", values=c, aggfunc=lambda v: TR(pd.Series(v)).iloc[0])[L].astype(bool).values
        fid = piv("fid"); pas = piv("final") & fid; n = fid.sum(0); k = pas.sum(0); e = k / n; p0 = np.array([P[l] for l in L])
        with np.errstate(divide="ignore", invalid="ignore"):
            G = 2 * np.nansum(np.where(k > 0, k * np.log(k / (n * p0)), 0) + np.where(n - k > 0, (n - k) * np.log((n - k) / (n * (1 - p0))), 0))
        N = len(fid); bs = np.empty((10000, len(L)))
        for i in range(10000):
            j = rng.integers(0, N, N); bs[i] = pas[j].sum(0) / fid[j].sum(0)
        with np.errstate(invalid="ignore"): R = np.corrcoef(bs.T)
        R = np.where(np.isfinite(R), R, 0.0); np.fill_diagonal(R, 1.0)
        s = np.sqrt(p0 * (1 - p0) / n); C = R * np.outer(s, s); dv = e - p0; chi = float(dv @ np.linalg.solve(C, dv))
        rows.append(dict(setup=lab, benchmark=b, points=len(L), k=" ".join(map(str, k)), n=" ".join(map(str, n)), G_naive=G, p_naive=stats.chi2.sf(G, len(L)), chi2_corr=chi, p_corr=stats.chi2.sf(chi, len(L))))
        tot["G"] += G; tot["C"] += chi; tot["dof"] += len(L)
    rows.append(dict(setup=lab, benchmark="EW+COL", points=tot["dof"], G_naive=tot["G"], p_naive=stats.chi2.sf(tot["G"], tot["dof"]), chi2_corr=tot["C"], p_corr=stats.chi2.sf(tot["C"], tot["dof"])))
out = pd.DataFrame(rows); out.to_csv(f"{T}/lambda_scan_combined_test_2000.csv", index=False)
pd.set_option("display.width", 220); print(out[["setup", "benchmark", "k", "n", "chi2_corr", "p_corr", "G_naive", "p_naive"]].to_string(float_format=lambda v: f"{v:.3g}"))
