#!/usr/bin/env python3
"""07 figures (ROOT), step 1 of 2: plot-ready CSVs in data/ from the 07 result tables (ATLAS Run 2 ID geometry, large samples, 13.6 TeV) and, for
comparison, Stage 2 (06_publication/S2_..., Knapen barrel geometry, 2000 generated events per mass point). No new physics numbers: every value is read
from the result tables or the G01 / input files; contour lines use the method of 06_publication/FIGURES_ROOT_2026-11-04/prepare_data.py (zgrid and
lines copied unchanged; checked by tests/T10_contour_method.py against its contours.csv).
Run with /home/rafia/venvs/f6fast/bin/python after reach/R01_reach_07.py. Writes data/*.csv and data/sources.json (sha256 of every input)."""
import os, json, glob, hashlib, numpy as np, pandas as pd
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
import contourpy
HERE = os.path.dirname(os.path.abspath(__file__)); D = f"{HERE}/data"; os.makedirs(D, exist_ok=True); ROOT = os.path.abspath(f"{HERE}/..")
BASE = os.path.abspath(f"{ROOT}/.."); S2 = f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop"; T = f"{ROOT}/tables"
SRC = {}
def rd(path, **kw):
    SRC[os.path.relpath(os.path.abspath(path), BASE)] = hashlib.sha256(open(path, "rb").read()).hexdigest(); return pd.read_csv(path, **kw)
TR = lambda s: s.astype(str) == "True"
def wilson(k, n, cl=0.6827):
    if n == 0: return np.nan, np.nan
    lo, hi = stats.binomtest(int(k), int(n)).proportion_ci(cl, "wilson"); return lo, hi

# ---- D1: cross sections, trigger efficiency, charge fraction: 07 large samples and Stage 2
rows = []
for sample, f in (("07_10k", f"{ROOT}/signal/inputs_large/counts.csv"), ("stage2_2k", f"{S2}/inputs/counts.csv")):
    for r in rd(f).itertuples():
        lo, hi = wilson(r.n_trigger, r.n_matched); flo, fhi = wilson(r.n_trigger_both_charged, r.n_trigger)
        rows.append(dict(sample=sample, channel=r.channel, mass_gev=r.mass_gev, n_generated=r.n_generated, sigma_fb=r.sigma_matched_fb, sigma_err_fb=r.sigma_matched_err_fb,
                         n_matched=r.n_matched, n_trigger=r.n_trigger, eps_trig=r.n_trigger / r.n_matched, eps_trig_lo=lo, eps_trig_hi=hi,
                         n_both_charged=r.n_trigger_both_charged, f_ch=r.n_trigger_both_charged / r.n_trigger, f_ch_lo=flo, f_ch_hi=fhi))
pd.DataFrame(rows).to_csv(f"{D}/xsec_and_trigger.csv", index=False)

# ---- D2: quirk velocity beta = |p| / E of the propagated events (triggered; colored: both charged), both quirks, 07 large samples
brow, hrow = [], []; EDGES = np.linspace(0, 1, 51)
for r in rd(f"{ROOT}/signal/inputs_large/counts.csv").itertuples():
    tag = f"{r.channel}_{r.mass_gev}gev"; ev = rd(f"{ROOT}/signal/inputs_large/{tag}_events.csv"); sel = TR(ev.trigger_proxy_pass)
    if r.channel == "colored": sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
    e = ev[sel]; b = np.r_[np.sqrt(e.px1 ** 2 + e.py1 ** 2 + e.pz1 ** 2) / e.E1, np.sqrt(e.px2 ** 2 + e.py2 ** 2 + e.pz2 ** 2) / e.E2]
    bt = np.r_[np.hypot(e.px1, e.py1) / e.E1, np.hypot(e.px2, e.py2) / e.E2]; bg = b / np.sqrt(1 - b ** 2)
    q = np.percentile(b, [16, 50, 84]); qt = np.percentile(bt, [16, 50, 84])
    brow.append(dict(channel=r.channel, mass_gev=r.mass_gev, n_events=int(sel.sum()), n_quirks=len(b), beta_mean=b.mean(), beta_p16=q[0], beta_median=q[1], beta_p84=q[2],
                     betaT_p16=qt[0], betaT_median=qt[1], betaT_p84=qt[2], betagamma_median=np.median(bg), frac_beta_lt_0p3=float((b < 0.3).mean()), frac_beta_gt_0p8=float((b > 0.8).mean())))
    h, _ = np.histogram(b, EDGES)
    for i in range(len(h)): hrow.append(dict(channel=r.channel, mass_gev=r.mass_gev, lo=EDGES[i], hi=EDGES[i + 1], n=int(h[i]), frac=h[i] / len(b)))
pd.DataFrame(brow).to_csv(f"{D}/beta_summary.csv", index=False); pd.DataFrame(hrow).to_csv(f"{D}/beta_hist.csv", index=False)

# ---- D3: efficiencies vs Lambda (07: station fiducial rule and the barrel rule on the same trajectories; Stage 2 for comparison)
G = rd(f"{T}/R01_N_grid_300fb.csv"); G2 = rd(f"{S2}/S2_N_grid_300fb.csv"); erow = []
for g, src in ((G, "07_10k"), (G2, "stage2_2k")):
    for r in g[g.status == "computed"].itertuples():
        n = int(r.n_prop); f_lo, f_hi = wilson(r.n_fid, n); k_lo, k_hi = wilson(r.k, n)
        d = dict(sample=src, channel=r.channel, mass_gev=r.mass_gev, lambda_keV=r.lambda_keV, sct=r.sct, n_prop=n, n_fid=int(r.n_fid), eps_fid=r.n_fid / n, eps_fid_lo=f_lo,
                 eps_fid_hi=f_hi, k=int(r.k), kn=r.k / n, kn_lo=k_lo, kn_hi=k_hi, eps_reco=r.eps_reco, N_300fb=r.N_with_f)
        if src == "07_10k":
            s_lo, s_hi = wilson(r.n_fid_stage2, n)
            d.update(n_fid_stage2=int(r.n_fid_stage2), eps_fid_stage2=r.n_fid_stage2 / n, eps_fid_stage2_lo=s_lo, eps_fid_stage2_hi=s_hi, k_endcap=int(r.k_endcap),
                     frac_endcap=r.k_endcap / r.k if r.k else np.nan)
        erow.append(d)
pd.DataFrame(erow).to_csv(f"{D}/efficiency_vs_lambda.csv", index=False)

# ---- D4: contour lines (method of 06 prepare_data.py, unchanged) and grid points
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
def scaled(G, L):
    g = G.copy(); g[["N_with_f", "N_with_f_lo", "N_with_f_hi"]] *= L / 300.0; return g
BK = rd(f"{T}/R01_background.csv")
SCEN = [("07_332fb", scaled(G, 332.0), {}, ("Z0", "A580", "Z1160")), ("stage2_332fb", scaled(G2, 332.0), {}, ("Z0", "Z1160"))]
for mu in (0, 20, 50, 60):
    th = {r.sct: (r.s_excl_332fb, r.s_disc_332fb) for r in BK[BK.mu == mu].itertuples()}
    SCEN.append((f"07_332fb_mu{mu}", scaled(G, 332.0), th, tuple(th)))
crow, grow = [], []
for name, g0, th, scts in SCEN:
    for ch in ("colored", "EW"):
        for sct in scts:
            g = g0[(g0.channel == ch) & (g0.sct == sct)]; thr = th.get(sct, (3.0, 5.0))
            for cn, t in (("exclusion", thr[0]), ("discovery", thr[1])):
                for band, col in (("central", "N_with_f"), ("lo", "N_with_f_lo"), ("hi", "N_with_f_hi")):
                    for s, seg in enumerate(lines(g, col, t)):
                        for x, yv in seg: crow.append(dict(scenario=name, channel=ch, sct=sct, contour=cn, threshold=round(t, 3), band=band, segment=s, mass_gev=x, lambda_eV=10 ** yv))
            if name in ("07_332fb", "stage2_332fb"):
                for r in g.itertuples():
                    if r.status_with_f == "computed": grow.append(dict(scenario=name, channel=ch, sct=sct, mass_gev=r.mass_gev, lambda_eV=r.lambda_keV * 1e3, k=int(r.k), n_prop=int(r.n_prop), N=r.N_with_f))
pd.DataFrame(crow).to_csv(f"{D}/contours.csv", index=False); pd.DataFrame(grow).to_csv(f"{D}/grid_points.csv", index=False)

# ---- D5: maximum reach, all scenarios (07 zero background, 07 with background, Stage 2)
rr = []
for r in rd(f"{T}/R01_reach.csv").itertuples(): rr.append(dict(scenario=f"07_{r.lumi_fb:g}fb", channel=r.channel, sct=r.sct, contour=r.contour, mu=np.nan, variant="zero background", m_max=r.m_max_GeV, lo=r.m_max_lo, hi=r.m_max_hi, at_lambda_keV=r.at_lambda_keV, s_required=r.s_required))
for r in rd(f"{T}/R01_reach_with_background.csv").itertuples(): rr.append(dict(scenario=f"07_{r.lumi_fb:g}fb_mu{r.mu}", channel=r.channel, sct=r.sct, contour=r.contour, mu=r.mu, variant=r.variant, m_max=r.m_max_GeV, lo=r.m_max_lo, hi=r.m_max_hi, at_lambda_keV=r.at_lambda_keV, s_required=r.s_required))
for r in rd(f"{S2}/S2_reach.csv").itertuples(): rr.append(dict(scenario=f"stage2_{r.lumi_fb:g}fb", channel=r.channel, sct=r.sct, contour=r.contour, mu=np.nan, variant="zero background", m_max=r.m_max_GeV, lo=r.m_max_lo, hi=r.m_max_hi, at_lambda_keV=r.at_lambda_keV, s_required=3.0 if r.contour == "exclusion" else 5.0))
for r in rd(f"{S2}/S2_reach_with_background.csv").itertuples(): rr.append(dict(scenario=f"stage2_{r.lumi_fb:g}fb_mu{r.mu}", channel=r.channel, sct=r.sct, contour=r.contour, mu=r.mu, variant="b_used = UL if 0 passed", m_max=r.m_max_GeV, lo=r.m_max_lo, hi=r.m_max_hi, at_lambda_keV=r.at_lambda_keV, s_required=r.s_required))
pd.DataFrame(rr).to_csv(f"{D}/reach_summary.csv", index=False)

# ---- D6: background vs pile-up (07 C01 per setting with the barrel-like / end-cap split of S02; Stage 2 converted photons for comparison)
S02 = rd(f"{T}/S02_conversion_breakdown.csv"); brow = []
for (run, sct, part), x in S02.groupby(["run", "sct", "part"]):
    mu = int(run.split("mu")[-1]); brow.append(dict(sample="07", sct=sct, mu=mu, part=part, final=int(x.final.sum()), N_332fb=x.N_332fb.sum(), N_stat=float(np.sqrt((x.N_stat ** 2).sum()))))
for r in BK.itertuples(): brow.append(dict(sample="07", sct=r.sct, mu=r.mu, part="UL95 if 0 passed", final=r.n_final, N_332fb=r.N_UL95_332fb_if_zero, N_stat=np.nan))
S2B = rd(f"{S2}/S2_background_13p6TeV.csv")
for r in S2B[S2B.process.str.startswith("conversion")].itertuples(): brow.append(dict(sample="stage2", sct=r.sct, mu=r.mu, part="all", final=r.sr, N_332fb=r.N_bkg_332fb, N_stat=r.N_bkg_332fb / np.sqrt(r.sr) if r.sr else np.nan))
pd.DataFrame(brow).to_csv(f"{D}/background_vs_mu.csv", index=False)
pd.DataFrame([dict(sct=r.sct, mu=r.mu, N_bkg_332fb=r.N_bkg_332fb, b_used_332fb=r.b_used_332fb, s_excl_332fb=r.s_excl_332fb, s_disc_332fb=r.s_disc_332fb) for r in BK.itertuples()]).to_csv(f"{D}/background_thresholds.csv", index=False)

# ---- D7: conversion probability from the material (M01) vs |eta|, nominal and variants
M = rd(f"{T}/M01_conversion_per_photon.csv"); EB = np.linspace(0, 2.5, 11); mrow = []
for v, x in M.groupby("variant"):
    a = x.eta.abs()
    for i in range(len(EB) - 1):
        y = x[(a >= EB[i]) & (a < EB[i + 1])]
        if len(y): mrow.append(dict(variant=v, eta_lo=EB[i], eta_hi=EB[i + 1], n=len(y), **{c: y[c].mean() for c in ("P_before_IBL", "P_IBL", "P_pixel", "P_SCT", "P_total")}))
pd.DataFrame(mrow).to_csv(f"{D}/material_conversion_vs_eta.csv", index=False)
rd(f"{T}/M01_conversion_summary.csv").to_csv(f"{D}/material_conversion_summary.csv", index=False)
json.dump(SRC, open(f"{D}/sources.json", "w"), indent=1); print("prepare_data_07: wrote", sorted(os.listdir(D)))
