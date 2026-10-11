#!/usr/bin/env python3
"""EW (gamma* - 1) reweighting test (existing data only). Can ONE reweighting of the production (gamma* - 1) spectrum, gamma* = M_QQ/(2 m_Q),
fit the paper's eps_trig = 0.10 and its five eps_reco(Lambda) values together?
Inputs: EW2000 matched events (trigger: pT(QQ) > 200 GeV), EW1000+EW2000 fiducial events of the Lambda scan (tables/lambda_scan_per_event.csv).
Model: K bins of (gamma* - 1) (edges = quantiles of the matched EW2000 events), weight w_b >= 0 per bin applied at production.
  eps_trig(w) = sum w_b T_b / sum w_b M_b ;  eps_reco(L; w) = sum w_b k_b(L) / sum w_b n_b(L)  (fiducial events, same weights).
Fit: minimise chi2 = sum (pred - paper)^2 / var, var = paper(1-paper) / n_eff(w) (Kish effective size of the weighted sample).
Goodness: chi2 vs dof = 6 - (K - 1). Done for the two Lambda-scan readings. Output: tables/ew_gamma_reweight_test.csv"""
import os, importlib.util, numpy as np, pandas as pd
from scipy import optimize, stats
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p4", f"{HERE}/P4_literal_signal.py"); p4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p4)
MQ = 800.0; PAPER_TRIG = 0.10; PAPER_RECO = {1: .11, 2: .41, 3: .65, 4: .72, 5: .74}; LAMS = sorted(PAPER_RECO)
TR = lambda s: s.astype(str) == "True"
def gstar(df): return np.sqrt((df.E1 + df.E2) ** 2 - (df.px1 + df.px2) ** 2 - (df.py1 + df.py2) ** 2 - (df.pz1 + df.pz2) ** 2) / (2 * MQ) - 1
M = pd.read_csv(f"{p4.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/matched_events_full.csv")
M["g"] = gstar(M); M["trig"] = M.trigger_proxy_pass.astype(str) == "True"
assert abs(M.trig.mean() - 186 / 1045) < 1e-9, M.trig.mean()
L = pd.read_csv(f"{T}/lambda_scan_per_event.csv"); L = L[L["sample"].str.startswith("EW")]
G = {s: gstar(p4.momenta(s)) for s in ("EW1000", "EW2000")}
L["g"] = [G[s].iloc[int(k)] for s, k in zip(L["sample"], L.key)]
rows = []
for K in (3, 4, 5):
    edges = np.quantile(M.g, np.linspace(0, 1, K + 1)); edges[0], edges[-1] = -1, 99
    b = lambda g: np.clip(np.searchsorted(edges, g, side="right") - 1, 0, K - 1)
    Mb = np.bincount(b(M.g), minlength=K).astype(float); Tb = np.bincount(b(M.g[M.trig]), minlength=K).astype(float)
    for lab, mode, col in (("first crossing, no SCT z smear", "FIRST", "final"), ("all crossings, no smear, >=2", "ALL", "final")):
        x = L[(L["mode"] == mode) & (L.sct == "Z0")]; nb, kb = {}, {}
        for lk in LAMS:
            y = x[(x.lambda_keV == lk) & TR(x.fid)]; nb[lk] = np.bincount(b(y.g), minlength=K).astype(float); kb[lk] = np.bincount(b(y.g[TR(y[col])]), minlength=K).astype(float)
        def pred(w):
            out = [(w @ Tb) / (w @ Mb)] + [(w @ kb[l]) / (w @ nb[l]) for l in LAMS]
            neff = [(w @ Mb) ** 2 / ((w ** 2) @ Mb)] + [(w @ nb[l]) ** 2 / ((w ** 2) @ nb[l]) for l in LAMS]
            return np.array(out), np.array(neff)
        tgt = np.array([PAPER_TRIG] + [PAPER_RECO[l] for l in LAMS])
        def chi2(u):
            w = np.exp(u); p, n = pred(w); return float((((p - tgt) ** 2) / (tgt * (1 - tgt) / n)).sum())
        best = min((optimize.minimize(chi2, u0, method="Nelder-Mead", options=dict(maxiter=20000, xatol=1e-8, fatol=1e-10)) for u0 in
                    [np.zeros(K)] + [np.random.default_rng(s).normal(0, 2, K) for s in range(30)]), key=lambda r: r.fun)
        w = np.exp(best.x); w = w / (w @ Mb) * Mb.sum(); p, n = pred(w); p0, _ = pred(np.ones(K)); dof = 6 - (K - 1)
        rows.append(dict(bins=K, setup=lab, edges=" ".join(f"{e:.3f}" for e in edges[1:-1]), weights=" ".join(f"{v:.3g}" for v in w),
                         chi2_unweighted=chi2(np.zeros(K)), chi2_best=best.fun, dof=dof, p_best=stats.chi2.sf(best.fun, dof),
                         **{f"pred_{t}": round(v, 3) for t, v in zip(["trig"] + [f"reco_{l}keV" for l in LAMS], p)},
                         **{f"ours_{t}": round(v, 3) for t, v in zip(["trig"] + [f"reco_{l}keV" for l in LAMS], p0)}))
out = pd.DataFrame(rows); out.to_csv(f"{T}/ew_gamma_reweight_test.csv", index=False)
pd.set_option("display.width", 250); print("paper: trig 0.10, reco", PAPER_RECO); print(out.drop(columns=["edges"]).to_string(float_format=lambda v: f"{v:.3g}"))
print("per-bin trigger efficiency (K=4):"); edges = np.quantile(M.g, np.linspace(0, 1, 5))
for i in range(4):
    s = M[(M.g >= edges[i]) & (M.g <= edges[i + 1])]; print(f"  gamma*-1 {edges[i]:.3f}-{edges[i+1]:.3f}: {s.trig.sum()}/{len(s)} = {s.trig.mean():.3f}")
