#!/usr/bin/env python3
"""Combined test of the paper's Table I eps_reco(Lambda) column against the Lambda scan (tables/lambda_scan_per_event.csv), real n.
The 5 Lambda points of one benchmark use the SAME fiducial events, so they are correlated. Two statistics, paper values taken as exact:
  G (naive): binomial likelihood-ratio  2 sum[k ln(k/(n p0)) + (n-k) ln((n-k)/(n(1-p0)))], chi2 with dof = number of points (assumes independence).
  chi2_corr: d^T C^-1 d with d = eps - p0, C_ij = R_ij sqrt(p0_i(1-p0_i)/n_i * p0_j(1-p0_j)/n_j), R = correlation of the eps vector from an
             event-level bootstrap (10 000 resamples, 1000+2000 samples pooled per benchmark). dof = number of points.
A point with k = 0 (no bootstrap spread) is treated as uncorrelated with the others.
Benchmarks are independent samples, so the combined statistic is the sum (dof 10). Output: tables/lambda_scan_combined_test.csv"""
import os, numpy as np, pandas as pd
from scipy import stats
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
PAPER = {"EW": {1: .11, 2: .41, 3: .65, 4: .72, 5: .74}, "COL": {1: .083, 2: .35, 3: .59, 5: .74, 10: .58}}
SETUPS = [("first crossing, no SCT z smear", "FIRST", "Z0", "final"), ("all crossings, no smear, >=2", "ALL", "Z0", "final"),
          ("all crossings, no smear, exactly 2", "ALL", "Z0", "final_exact2"), ("all crossings, SCT z 580, >=2", "ALL", "Z580", "final")]
d = pd.read_csv(f"{T}/lambda_scan_per_event.csv"); d["benchmark"] = d["sample"].str[:-4]; TR = lambda s: s.astype(str) == "True"
rng = np.random.default_rng(20261007); rows = []
for lab, mode, sct, col in SETUPS:
    tot = dict(G=0.0, C=0.0, dof=0)
    for b, P in PAPER.items():
        x = d[(d.benchmark == b) & (d["mode"] == mode) & (d.sct == sct)]; L = sorted(P)
        fid = x.pivot_table(index=["sample", "key"], columns="lambda_keV", values="fid", aggfunc=lambda v: TR(pd.Series(v)).iloc[0])[L].astype(bool).values
        pas = x.pivot_table(index=["sample", "key"], columns="lambda_keV", values=col, aggfunc=lambda v: TR(pd.Series(v)).iloc[0])[L].astype(bool).values & fid
        n = fid.sum(0); k = pas.sum(0); e = k / n; p0 = np.array([P[l] for l in L])
        with np.errstate(divide="ignore", invalid="ignore"):
            G = 2 * np.nansum(np.where(k > 0, k * np.log(k / (n * p0)), 0) + np.where(n - k > 0, (n - k) * np.log((n - k) / (n * (1 - p0))), 0))
        N = len(fid); bs = np.empty((10000, len(L)))
        for i in range(10000):
            j = rng.integers(0, N, N); bs[i] = pas[j].sum(0) / fid[j].sum(0)
        R = np.corrcoef(bs.T); R = np.where(np.isfinite(R), R, 0.0); np.fill_diagonal(R, 1.0); s = np.sqrt(p0 * (1 - p0) / n); C = R * np.outer(s, s); dv = e - p0; chi = float(dv @ np.linalg.solve(C, dv))
        rows.append(dict(setup=lab, benchmark=b, points=len(L), n=" ".join(map(str, n)), k=" ".join(map(str, k)), G_naive=G, p_naive=stats.chi2.sf(G, len(L)),
                         chi2_corr=chi, p_corr=stats.chi2.sf(chi, len(L)), mean_offdiag_corr=float(R[np.triu_indices(len(L), 1)].mean())))
        tot["G"] += G; tot["C"] += chi; tot["dof"] += len(L)
    rows.append(dict(setup=lab, benchmark="EW+COL", points=tot["dof"], G_naive=tot["G"], p_naive=stats.chi2.sf(tot["G"], tot["dof"]), chi2_corr=tot["C"], p_corr=stats.chi2.sf(tot["C"], tot["dof"])))
out = pd.DataFrame(rows); out.to_csv(f"{T}/lambda_scan_combined_test.csv", index=False)
pd.set_option("display.width", 250); print(out[["setup", "benchmark", "points", "k", "n", "G_naive", "p_naive", "chi2_corr", "p_corr", "mean_offdiag_corr"]].to_string(float_format=lambda v: f"{v:.3g}"))
