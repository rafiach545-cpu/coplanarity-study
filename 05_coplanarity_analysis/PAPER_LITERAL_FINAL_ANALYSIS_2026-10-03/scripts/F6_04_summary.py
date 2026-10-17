#!/usr/bin/env python3
"""Figure 6 summary (2026-10-17): (1) maximum mass reach of the 3- and 5-event contours (central, and with N at the Wilson 68% bounds of k/n), per
variant, vs the paper's curves; (2) bound on the effect of integration failures: failed (event, Lambda) whose event is fiducial at another Lambda of the
same band are counted as passing (upper bound on k). Reach: log10 N interpolated linearly in m between computed grid masses at each grid Lambda
(only between points with k > 0 or bound points, as in the figure). Output: fig6/F6_reach.csv, fig6/F6_failure_bound.csv (printed)."""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; G = pd.read_csv(f"{ROOT}/fig6/F6_N_grid.csv")
V = json.load(open(f"{ROOT}/tables/paper_fig6_vector.json"))
def reach(g, col, thr):
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
rows = []
for ch in ("colored", "EW"):
    for sct in ("Z1160", "Z0"):
        g = G[(G.channel == ch) & (G.sct == sct)]
        for var in (("with_f", "without_f") if ch == "colored" else ("with_f",)):
            for thr, nm in ((3, "exclusion"), (5, "discovery")):
                c = reach(g, f"N_{var}", thr); lo = reach(g, f"N_{var}_lo", thr); hi = reach(g, f"N_{var}_hi", thr)
                pc = V[ch]["curves"][nm]; i = int(np.argmax(pc["m_GeV"]))
                rows.append(dict(channel=ch, sct=sct, variant="charge factor included" if var == "with_f" else "without charge factor", contour=nm,
                                 m_max_GeV=round(c[0]), at_lambda_keV=c[1], m_max_lo=round(lo[0]) if np.isfinite(lo[0]) else np.nan,
                                 m_max_hi=round(hi[0]) if np.isfinite(hi[0]) else np.nan, paper_m_max_GeV=round(pc["m_GeV"][i]), paper_at_lambda_keV=round(pc["lambda_eV"][i] / 1e3, 2)))
R = pd.DataFrame(rows); R.to_csv(f"{ROOT}/fig6/F6_reach.csv", index=False); pd.set_option("display.width", 220); print(R.to_string(index=False))
# ---- failure bound
TR = lambda s: s.astype(str) == "True"; out = []
for r in G[(G.status_with_f == "computed")].drop_duplicates(["channel", "mass_gev"]).itertuples():
    tag = f"{r.channel}_{r.mass_gev}gev"
    for band in ("low", "mid"):
        d = pd.DataFrame([x for l in open(f"{ROOT}/logs/F6_{tag}{'' if band == 'mid' else '_low'}_events.jsonl") if l.strip() for x in json.loads(l)])
        fidany = d.groupby("event").fid.apply(lambda s: TR(s).any())
        for lam, x in d.groupby("lambda_keV"):
            f = x[(x.error.astype(str) != "") & x.event.map(fidany)]
            if len(f):
                k = {s: int(G[(G.channel == r.channel) & (G.mass_gev == r.mass_gev) & np.isclose(G.lambda_keV, float(lam)) & (G.sct == s)].k.iloc[0]) for s in ("Z0", "Z1160")}
                out.append(dict(channel=r.channel, mass_gev=r.mass_gev, lambda_keV=lam, failed_fiducial_elsewhere=len(f), n=int(r.n_prop), k_Z0=k["Z0"], k_Z1160=k["Z1160"],
                                max_rel_increase_Z0=round(len(f) / k["Z0"], 2) if k["Z0"] else np.inf, max_rel_increase_Z1160=round(len(f) / k["Z1160"], 2) if k["Z1160"] else np.inf))
F = pd.DataFrame(out); F.to_csv(f"{ROOT}/fig6/F6_failure_bound.csv", index=False); print(); print(F.to_string(index=False))
