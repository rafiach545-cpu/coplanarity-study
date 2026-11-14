#!/usr/bin/env python3
"""Stage 2, step 9: 13.6 TeV background cut-flows (S2_08_background.py) and the reach with background.
Counting as S1_background_run2_summary.py (same columns, same selections). Converted photons: sigma_gamma(13.6 TeV) after post-shower MET > 200 GeV
(inputs/zgamma_xsec_13p6TeV.txt) x 1% conversion. k = 0: 95% upper limit 1 - 0.05^(1/n).
Signal thresholds with background b at luminosity L: exclusion = 95% CLs signal with n_obs = round(b) (as stage 1; 2.996 at b -> 0);
discovery = max(5, s with Asimov Z = 5) for the central b (k = 0: b = 0, i.e. the paper's 5 events; the upper limit is used for exclusion only, as stage 1). Reach: F6_04 algorithm on S2_N_grid_300fb.csv (scaled to L), as S2_05_reach.py.
Output: S2_background_13p6TeV.csv, S2_reach_with_background.csv (printed)."""
import os, glob, numpy as np, pandas as pd
from scipy import stats, optimize
HERE = os.path.dirname(os.path.abspath(__file__)); LOG = f"{HERE}/logs/bkg_13p6TeV"; TR = lambda s: s.astype(str) == "True"
X = dict(l.split() for l in open(f"{HERE}/inputs/zgamma_xsec_13p6TeV.txt")); SG = float(X["sigma_after_MET_pb"]) * 1e3 * 0.01   # fb, x 1% conversion
LUMIS = (300.0, 332.0, 355.0); MUS = (0, 20, 50, 60)
def ov(d):
    o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{d}/chunk_*.csv")); o = o[o.config == "LITERAL"]; n = int(X["n_events_after_MET"])
    if o.event.nunique() != n: return None
    return dict(n=n, plane=int(TR(o.plane).sum()), mult=int((TR(o.plane) & TR(o.mult)).sum()), sr=int((TR(o.plane) & TR(o.mult) & TR(o.final)).sum()))
def pu(d):
    p = pd.concat(pd.read_csv(f) for f in glob.glob(f"{d}/chunk_*.csv"))
    if p.event_i.nunique() != 5000: return None
    sel = TR(p.sec3c_plane_found) & (p.sec3c_dw < 1)
    return dict(n=5000, plane=int(TR(p.sec3c_plane_found).sum()), mult=int((sel & (p.sec3c_n_layers >= 8)).sum()), sr=int(TR(p.final_sec_iv_pass).sum()))
def s95(b):
    n = int(round(b)); return optimize.brentq(lambda s: stats.poisson.cdf(n, s + b) / stats.poisson.cdf(n, b) - 0.05, 1e-3, 300)
def s5(b):
    za = lambda s: np.sqrt(2 * ((s + b) * np.log(1 + s / b) - s)) - 5
    return max(5.0, optimize.brentq(za, 1e-3, 1e3)) if b > 0 else 5.0
rows = []
for lab, sct, f, run in (("conversion + pile-up", "Z1160", ov, "P10"), ("conversion + pile-up", "Z0", ov, "P17b"), ("pile-up only", "Z1160", pu, "P8")):
    for mu in MUS:
        d = f"{LOG}/{run}_mu{mu}"
        if not glob.glob(f"{d}/chunk_*.csv"): continue
        c = f(d)
        if c is None: print(f"skipped (incomplete): {d}"); continue
        r = dict(process=lab, sct=sct, mu=mu, **c)
        if lab.startswith("conversion"):
            for L in LUMIS:
                b = L * SG * c["sr"] / c["n"] if c["sr"] else L * SG * (1 - 0.05 ** (1 / c["n"]))
                r[f"N_bkg_{L:g}fb"] = L * SG * c["sr"] / c["n"]; r[f"b_used_{L:g}fb"] = b; r[f"s_excl_{L:g}fb"] = s95(b); r[f"s_disc_{L:g}fb"] = s5(L * SG * c["sr"] / c["n"])
        else:
            r["prob_per_event"] = c["sr"] / c["n"]; r["prob_UL95"] = 1 - 0.05 ** (1 / c["n"]) if c["sr"] == 0 else stats.binomtest(c["sr"], c["n"]).proportion_ci(0.95, "wilson")[1]
        rows.append(r)
B = pd.DataFrame(rows); B.to_csv(f"{HERE}/S2_background_13p6TeV.csv", index=False); pd.set_option("display.width", 250)
print(f"sigma_gamma x 1% = {SG:.4f} fb"); print(B.round(4).to_string(index=False))

G = pd.read_csv(f"{HERE}/S2_N_grid_300fb.csv")
def reach(g, col, thr):                                                      # F6_04_summary.py, unchanged (as S2_05_reach.py)
    best = (np.nan, np.nan)
    for lam, x in g.groupby("lambda_keV"):
        x = x.sort_values("mass_gev"); ok = (x[f"status_{'with_f' if 'with_f' in col else 'without_f'}"] == "bound") | ((x.status_with_f == "computed") & (x.k > 0))
        m, v = x.mass_gev.values, np.where(ok, x[col].values, np.nan)
        for i in range(len(m) - 1):
            a, b = v[i], v[i + 1]
            if np.isfinite(a) and np.isfinite(b) and a >= thr > b:
                mm = m[i] + (np.log10(thr) - np.log10(a)) / (np.log10(b) - np.log10(a)) * (m[i + 1] - m[i])
                if not np.isfinite(best[0]) or mm > best[0]: best = (mm, lam)
    return best
out = []
for r in B[B.process.str.startswith("conversion")].itertuples():
    for ch in ("colored", "EW"):
        g0 = G[(G.channel == ch) & (G.sct == r.sct)]
        for L in LUMIS:
            g = g0.copy(); g[["N_with_f", "N_with_f_lo", "N_with_f_hi"]] *= L / 300.0
            for nm, thr in (("exclusion", getattr(r, f"s_excl_{L:g}fb")), ("discovery", getattr(r, f"s_disc_{L:g}fb"))):
                c, lo, hi = (reach(g, f"N_with_f{s}", thr) for s in ("", "_lo", "_hi"))
                rd = lambda v: round(v) if np.isfinite(v) else np.nan
                out.append(dict(channel=ch, sct=r.sct, mu=r.mu, lumi_fb=L, contour=nm, N_bkg=round(getattr(r, f"N_bkg_{L:g}fb"), 3), s_required=round(thr, 2),
                                m_max_GeV=rd(c[0]), at_lambda_keV=c[1], m_max_lo=rd(lo[0]), m_max_hi=rd(hi[0])))
R = pd.DataFrame(out).sort_values(["channel", "sct", "lumi_fb", "contour", "mu"]); R.to_csv(f"{HERE}/S2_reach_with_background.csv", index=False)
print(R[R.lumi_fb == 300].to_string(index=False))
