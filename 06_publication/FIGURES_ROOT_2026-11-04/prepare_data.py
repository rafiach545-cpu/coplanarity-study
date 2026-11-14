#!/usr/bin/env python3
"""Paper figures (ROOT), step 1 of 2: plot-ready CSVs in data/ from the result CSVs of stage 1 (13 TeV) and stage 2 (13.6 TeV). No new physics numbers:
every value is read from the stage CSVs or from the background chunk files; contour lines use the same method as S2_05_reach.py (log10 N on the
(m_Q, log10 Lambda) grid, points with k = 0 left out, linear RegularGridInterpolator on 400 x 400, contour at N = threshold; contourpy, as matplotlib).
Run with /home/rafia/venvs/f6fast/bin/python. Writes data/*.csv and data/sources.json (sha256 of every input)."""
import os, glob, json, hashlib, numpy as np, pandas as pd
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
import contourpy
HERE = os.path.dirname(os.path.abspath(__file__)); D = f"{HERE}/data"; os.makedirs(D, exist_ok=True)
PUB = f"{HERE}/.."; S1 = f"{PUB}/S1_13TeV_139fb_knapen_noPU_cop"; S2 = f"{PUB}/S2_13p6TeV_run3_knapen_noPU_cop"; REP = f"{PUB}/../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03"
SRC = {}
def rd(path, **kw):
    SRC[os.path.relpath(os.path.abspath(path), os.path.abspath(f"{PUB}/.."))] = hashlib.sha256(open(path, "rb").read()).hexdigest(); return pd.read_csv(path, **kw)
TR = lambda s: s.astype(str) == "True"
def wilson(k, n, cl=0.6827):
    lo, hi = stats.binomtest(int(k), int(n)).proportion_ci(cl, "wilson"); return lo, hi

# ---- D1: cross sections and generation-level factors
rows = []
for E, f in (("13", f"{REP}/fig6/inputs/counts.csv"), ("13.6", f"{S2}/inputs/counts.csv")):
    for r in rd(f).itertuples():
        lo, hi = wilson(r.n_trigger, r.n_matched); flo, fhi = wilson(r.n_trigger_both_charged, r.n_trigger)
        rows.append(dict(sqrt_s_TeV=E, channel=r.channel, mass_gev=r.mass_gev, sigma_fb=r.sigma_matched_fb, sigma_err_fb=r.sigma_matched_err_fb, n_matched=r.n_matched,
                         n_trigger=r.n_trigger, eps_trig=r.n_trigger / r.n_matched, eps_trig_lo=lo, eps_trig_hi=hi, n_both_charged=r.n_trigger_both_charged,
                         f_ch=r.n_trigger_both_charged / r.n_trigger, f_ch_lo=flo, f_ch_hi=fhi))
pd.DataFrame(rows).to_csv(f"{D}/xsec_and_trigger.csv", index=False)

# ---- D2: contour lines and grid points
def zgrid(g, col):
    ms = sorted(g.mass_gev.unique()); lams = sorted(g.lambda_keV.unique()); z = np.full((len(ms), len(lams)), np.nan)
    for i, m in enumerate(ms):
        for j, lam in enumerate(lams):
            r = g[(g.mass_gev == m) & np.isclose(g.lambda_keV, lam)]
            if len(r) and (r.iloc[0].status_with_f == "bound" or (r.iloc[0].status_with_f == "computed" and r.iloc[0].k > 0)):
                v = r.iloc[0][col] if r.iloc[0].status_with_f == "computed" else r.iloc[0].N_with_f
                z[i, j] = np.log10(v) if v > 0 else np.nan
    return np.array(ms, float), np.log10(np.array(lams) * 1e3), z
def lines(g, col, thr):
    ms, y, z = zgrid(g, col); f = RegularGridInterpolator((ms, y), z, bounds_error=False, fill_value=np.nan)
    mm, yy = np.meshgrid(np.linspace(ms[0], ms[-1], 400), np.linspace(y[0], y[-1], 400), indexing="ij"); zz = f(np.c_[mm.ravel(), yy.ravel()]).reshape(mm.shape)
    return contourpy.contour_generator(mm, yy, np.ma.masked_invalid(zz), name="serial", line_type="Separate").lines(np.log10(thr))
G1 = rd(f"{S1}/S1_N_grid_139fb.csv"); G13 = rd(f"{REP}/fig6/F6_N_grid.csv"); G2 = rd(f"{S2}/S2_N_grid_300fb.csv"); BK = rd(f"{S2}/S2_background_13p6TeV.csv")
def scaled(G, L):
    g = G.copy(); g[["N_with_f", "N_with_f_lo", "N_with_f_hi"]] *= L / 300.0; return g
SCEN = [("13TeV_139fb", G1, {}), ("13TeV_300fb", G13, {}), ("13p6TeV_300fb", G2, {}), ("13p6TeV_332fb", scaled(G2, 332.0), {}), ("13p6TeV_355fb", scaled(G2, 355.0), {})]
for mu in (0, 20, 50, 60):
    th = {}
    for r in BK[(BK.process == "conversion + pile-up") & (BK.mu == mu)].itertuples(): th[r.sct] = (r.s_excl_332fb, r.s_disc_332fb)
    SCEN.append((f"13p6TeV_332fb_mu{mu}", scaled(G2, 332.0), th))
crow, grow = [], []
for name, G, th in SCEN:
    for ch in ("colored", "EW"):
        for sct in ("Z1160", "Z0"):
            g = G[(G.channel == ch) & (G.sct == sct)]
            thr = th.get(sct, (3.0, 5.0))
            for cn, t in (("exclusion", thr[0]), ("discovery", thr[1])):
                for band, col in (("central", "N_with_f"), ("lo", "N_with_f_lo"), ("hi", "N_with_f_hi")):
                    for s, seg in enumerate(lines(g, col, t)):
                        for x, yv in seg: crow.append(dict(scenario=name, channel=ch, sct=sct, contour=cn, threshold=round(t, 3), band=band, segment=s, mass_gev=x, lambda_eV=10 ** yv))
            if name in ("13TeV_139fb", "13p6TeV_332fb"):
                for r in g.itertuples():
                    if r.status_with_f == "computed": grow.append(dict(scenario=name, channel=ch, sct=sct, mass_gev=r.mass_gev, lambda_eV=r.lambda_keV * 1e3, k=int(r.k), n_prop=int(r.n_prop), N=r.N_with_f))
pd.DataFrame(crow).to_csv(f"{D}/contours.csv", index=False); pd.DataFrame(grow).to_csv(f"{D}/grid_points.csv", index=False)

# ---- D3: maximum reach, all scenarios
rr = []
for r in rd(f"{S1}/S1_reach_139fb.csv").itertuples(): rr.append(dict(scenario="13TeV_139fb", channel=r.channel, sct=r.sct, contour=r.contour, m_max=r.m_max_GeV, lo=r.m_max_lo, hi=r.m_max_hi))
for r in rd(f"{REP}/fig6/F6_reach.csv").query("variant == 'charge factor included'").itertuples(): rr.append(dict(scenario="13TeV_300fb", channel=r.channel, sct=r.sct, contour=r.contour, m_max=r.m_max_GeV, lo=r.m_max_lo, hi=r.m_max_hi))
for r in rd(f"{S2}/S2_reach.csv").itertuples(): rr.append(dict(scenario=f"13p6TeV_{r.lumi_fb:g}fb", channel=r.channel, sct=r.sct, contour=r.contour, m_max=r.m_max_GeV, lo=r.m_max_lo, hi=r.m_max_hi))
for r in rd(f"{S2}/S2_reach_with_background.csv").itertuples():
    if r.lumi_fb == 332: rr.append(dict(scenario=f"13p6TeV_332fb_mu{r.mu}", channel=r.channel, sct=r.sct, contour=r.contour, m_max=r.m_max_GeV, lo=r.m_max_lo, hi=r.m_max_hi))
for r in rd(f"{S2}/S2_compare_reach.csv").itertuples():
    if r.lumi_fb == 332: rr.append(dict(scenario="13p6TeV_332fb_pooled_eff", channel=r.channel, sct=r.sct, contour=r.contour, m_max=r.pooled_eff_13p6sigma, lo=np.nan, hi=np.nan))
pd.DataFrame(rr).to_csv(f"{D}/reach_summary.csv", index=False)

# ---- D4: backgrounds vs mu (signal-region fraction per converted photon, Wilson 68%; k = 0: 95% upper limit)
br = []
def addb(E, sct, mu, n, plane, mult, sr, note=""):
    lo, hi = wilson(sr, n); br.append(dict(sqrt_s_TeV=E, sct=sct, mu=mu, n=n, plane=plane, mult=mult, sr=sr, frac=sr / n, frac_lo=lo, frac_hi=hi, frac_UL95=1 - 0.05 ** (1 / n) if sr == 0 else np.nan, note=note))
b0 = rd(f"{S1}/S1_background_139fb.csv")
for _, r in b0[b0.pileup == "none"].iterrows(): addb("13", r.sct, 0, r["sample"], np.nan, np.nan, r["pass"])
for r in rd(f"{S1}/S1_background_run2.csv").query("process == 'conversion + pile-up'").itertuples(): addb("13", r.sct, r.mu, r.n, r.plane, r.mult, r.sr)
for r in BK[BK.process == "conversion + pile-up"].itertuples(): addb("13.6", r.sct, r.mu, r.n, r.plane, r.mult, r.sr)
def count(d):
    o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{d}/chunk_*.csv")); o = o[o.config == "LITERAL"]
    for f in glob.glob(f"{d}/chunk_*.csv")[:1]: SRC[os.path.relpath(d, os.path.abspath(f"{PUB}/.."))] = f"{len(glob.glob(d + '/chunk_*.csv'))} chunk files"
    return o.event.nunique(), int(TR(o.plane).sum()), int((TR(o.plane) & TR(o.mult)).sum()), int((TR(o.plane) & TR(o.mult) & TR(o.final)).sum())
n, p, m, s = count(f"{S2}/logs/bkg_13TeV/P17b_mu50_seed20261104"); addb("13", "Z0", 50, n, p, m, s, "pile-up seed 20261104")
pd.DataFrame(br).to_csv(f"{D}/background_vs_mu.csv", index=False)
pu = []
for r in rd(f"{S1}/S1_background_run2.csv").query("process == 'pile-up only'").itertuples(): pu.append(dict(sqrt_s_TeV="13", mu=r.mu, n=r.n, plane=r.plane, mult=r.mult, sr=r.sr))
for r in BK[BK.process == "pile-up only"].itertuples(): pu.append(dict(sqrt_s_TeV="13.6", mu=r.mu, n=r.n, plane=r.plane, mult=r.mult, sr=r.sr))
pd.DataFrame(pu).to_csv(f"{D}/pileup_only.csv", index=False)
nb = BK[BK.process == "conversion + pile-up"][["sct", "mu"] + [c for c in BK.columns if c.endswith("fb")]]; nb.to_csv(f"{D}/background_13p6TeV_thresholds.csv", index=False)

# ---- D5: mixed test (sigma_z = 0, mu = 50)
mx = []
for ph, pu_, d in (("13", "13", f"{REP}/logs/P10_chunks_B_Z0_REF34"), ("13", "13 (seed 20261104)", f"{S2}/logs/bkg_13TeV/P17b_mu50_seed20261104"),
                   ("13", "13.6", f"{S2}/logs/bkg_ph13_pu13p6/P17b_mu50"), ("13.6", "13", f"{S2}/logs/bkg_ph13p6_pu13/P17b_mu50"), ("13.6", "13.6", f"{S2}/logs/bkg_13p6TeV/P17b_mu50")):
    n, p, m, s = count(d); lo, hi = wilson(s, n); mx.append(dict(photons_TeV=ph, pileup_TeV=pu_, n=n, plane=p, mult=m, sr=s, frac=s / n, frac_lo=lo, frac_hi=hi))
pd.DataFrame(mx).to_csv(f"{D}/mix_test_mu50.csv", index=False)

# ---- D6: 13 vs 13.6 TeV comparison (copied, with Wilson bands on k/n)
F = rd(f"{S2}/S2_compare_factors.csv"); kn = F[F.factor == "k/n"].copy()
for E, c in (("13", "counts13"), ("13p6", "counts13p6")):
    k = kn[c].str.split("/").str[0].astype(int); n = kn[c].str.split("/").str[1].astype(int)
    b = [wilson(a, bb) for a, bb in zip(k, n)]; kn[f"k_{E}"] = k; kn[f"n_{E}"] = n; kn[f"lo_{E}"] = [x[0] for x in b]; kn[f"hi_{E}"] = [x[1] for x in b]
kn.to_csv(f"{D}/kn_13_vs_13p6.csv", index=False)
F.to_csv(f"{D}/factors_13_vs_13p6.csv", index=False)
rd(f"{S2}/S2_compare_reach.csv").to_csv(f"{D}/reach_variants.csv", index=False); rd(f"{S2}/S2_compare_bootstrap.csv").to_csv(f"{D}/bootstrap.csv", index=False)

# ---- D8: expected signal events per mass point (no pile-up, zero background): at the best Lambda (largest N) and at Lambda = 2 keV, 13 TeV 139 fb^-1 and 13.6 TeV 332 fb^-1.
# Not propagated points ("bound", 13 TeV colored 2400 GeV): N <= L sigma eps_trig f_ch.
ev = []
for name, G in (("13TeV_139fb", G1), ("13p6TeV_332fb", scaled(G2, 332.0))):
    for (ch, sct, m), g in G.groupby(["channel", "sct", "mass_gev"]):
        g = g.sort_values("lambda_keV"); bound = (g.status_with_f == "bound").all(); b = g.loc[g.N_with_f.idxmax()]; t = g[np.isclose(g.lambda_keV, 2.0)].iloc[0]
        cell = lambda r, p: {f"{p}_N": r.N_with_f, f"{p}_lo": np.nan if bound else r.N_with_f_lo, f"{p}_hi": np.nan if bound else r.N_with_f_hi, f"{p}_k": np.nan if bound else int(r.k)}
        ev.append(dict(scenario=name, channel=ch, sct=sct, mass_gev=m, status="bound" if bound else "computed", n_prop=int(g.n_prop.iloc[0]), pre_N=g.L_sigma_eps_trig.iloc[0] * g.f_ch.iloc[0],
                       best_lambda_keV=np.nan if bound else b.lambda_keV, **cell(b, "best"), **cell(t, "lam2")))
EV = pd.DataFrame(ev); EV.loc[EV.scenario == "13p6TeV_332fb", "pre_N"] *= 332.0 / 300.0   # scaled() rescales only the N columns
EV.to_csv(f"{D}/expected_events.csv", index=False)
# ---- D9: statistical uncertainties (S2_11_uncertainties.py): budget, reach toys, 13 vs 13.6 TeV consistency
for f in ("budget", "reach", "consistency_mass", "consistency"): rd(f"{S2}/S2_unc_{f}.csv").to_csv(f"{D}/unc_{f}.csv", index=False)
# ---- D10: expected exclusion bands, n_obs ~ Poisson(b) (S2_12_expected_bands.py)
rd(f"{S2}/S2_expected_bands.csv").to_csv(f"{D}/expected_bands.csv", index=False)
# ---- D11: production channels and pair pT (S2_13_production_and_pt.py)
for f in ("production_channels", "pair_pt"): rd(f"{S2}/S2_{f}.csv").to_csv(f"{D}/{f}.csv", index=False)
# ---- D12: k and n of every 13.6 TeV grid point (S2_N_grid_300fb.csv); N also at 332 fb^-1 (N is linear in L, k and n do not depend on L)
G12 = rd(f"{S2}/S2_N_grid_300fb.csv")[["channel", "mass_gev", "lambda_keV", "sct", "status_with_f", "n_prop", "k", "N_with_f"]].rename(columns={"N_with_f": "N_300fb"})
G12["N_332fb"] = G12.N_300fb * 332.0 / 300.0; G12.to_csv(f"{D}/grid_k_13p6TeV.csv", index=False)
json.dump(SRC, open(f"{D}/sources.json", "w"), indent=1); print("prepared:", sorted(os.listdir(D)))
