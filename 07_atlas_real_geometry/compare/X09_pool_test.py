#!/usr/bin/env python3
"""07 X09 (2026-11-17): pool test, region by region and photon by photon.
Production: backgrounds/runs/C01_atlas_mu50 (laptop, pool seed 20260916, sha256 52b465f5...), sct Z0.
Test:       backgrounds/runs/C01_atlas_pooltest_seed20261117_mu50 (server, new pool seed 20261117), sct Z0.
Same 9130 photons, same per-photon seeds and conversion points; only the pool (and the machine) differ.
N = sum_i w_i * final_i, w_i = c_r * p_conv,i, c_r = L * sigma_per_photon * NPH / (photons in region r) (exactly as S01).
Paired difference D = sum_i w_i (f_test,i - f_prod,i); its error sqrt(sum_i w_i^2 (f_test,i - f_prod,i)^2) uses only the
photons whose pass/fail changed (concordant photons cancel exactly). The unpaired error sqrt(s_prod^2 + s_test^2) is printed for comparison.
Writes tables/X09_pool_test_by_region.csv."""
import os, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); T = f"{R}/tables"
BASE = os.environ.get("COPLANARITY_BASE", os.path.abspath(f"{R}/.."))
X = dict(l.split()[:2] for l in open(f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/inputs/zgamma_xsec_13p6TeV.txt") if len(l.split()) >= 2)
SIG = float(X["sigma_generated_pb"]) / float(X.get("n_generated", 10000)); NPH = float(X["n_events_after_MET"]); L_PB = 332.0e3
K = ["event", "region"]


def load(run):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{R}/backgrounds/runs/{run}/chunk_*.csv"))], ignore_index=True)
    d = d[d.sct == "Z0"].copy(); d["f"] = d.final.astype(str).str.lower().eq("true").astype(int)
    return d[K + ["region_element", "p_conv", "f"]]


P, Q = load("C01_atlas_mu50"), load("C01_atlas_pooltest_seed20261117_mu50")
M = P.merge(Q, on=K, suffixes=("_p", "_t"), how="outer", indicator=True)
assert (M._merge == "both").all(), "photon/region rows differ between the two runs"
assert np.allclose(M.p_conv_p, M.p_conv_t) and (M.region_element_p == M.region_element_t).all(), "conversion points differ"
M["p"] = M.p_conv_p; M["w"] = L_PB * SIG * NPH * M.p / M.groupby("region").event.transform("nunique")


def summ(g):
    d = g.f_t - g.f_p; Np, Nt = (g.w * g.f_p).sum(), (g.w * g.f_t).sum()
    sp, st = np.sqrt((g.w**2 * g.f_p).sum()), np.sqrt((g.w**2 * g.f_t).sum()); sd = np.sqrt((g.w**2 * d**2).sum())
    return pd.Series(dict(n_rows=len(g), pass_prod=int(g.f_p.sum()), pass_test=int(g.f_t.sum()), both=int((g.f_p & g.f_t).sum()),
                          prod_only=int(((g.f_p == 1) & (g.f_t == 0)).sum()), test_only=int(((g.f_p == 0) & (g.f_t == 1)).sum()),
                          N_prod=Np, err_prod=sp, N_test=Nt, err_test=st, D=Nt - Np, err_D_paired=sd, err_D_unpaired=np.hypot(sp, st),
                          z_paired=(Nt - Np) / sd if sd > 0 else 0.0, mean_pconv_prod_pass=g.p[g.f_p == 1].mean(), mean_pconv_test_pass=g.p[g.f_t == 1].mean()))


A = M.groupby("region").apply(summ); A.loc["total"] = summ(M); A.to_csv(f"{T}/X09_pool_test_by_region.csv")
pd.set_option("display.width", 250)
print(A.round(3).to_string())
for run, N in (("C01_atlas_mu50", A.loc["total", "N_prod"]), ("C01_atlas_pooltest_seed20261117_mu50", A.loc["total", "N_test"])):   # cross-check with S01
    s = pd.read_csv(f"{T}/S01_{run}.csv"); s = s[s.sct == "Z0"]; assert abs(s.N_bkg_332fb.sum() - N) < 1e-6 * N, (run, s.N_bkg_332fb.sum(), N)
print("X09: N totals match the S01 tables; X09_EXIT=0")
