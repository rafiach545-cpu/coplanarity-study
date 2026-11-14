#!/usr/bin/env python3
"""Stage 1: background cut-flows with low (mu = 20) and Run 2 (<mu> = 33.7) pile-up (S1_pileup_run2.py) next to the reproduction's mu = 50, and the expected background at
139 fb^-1. Counting as in R_data_2026_10_15.backgrounds() (same columns, same selections). Converted photons: sigma_gamma = 0.211 pb (after MET > 200 GeV)
x 1% conversion. Pile-up only: probability per triggered event (the number of triggered events it sits on is not given by the paper).
Output: S1_background_run2.csv (printed)."""
import os, glob, numpy as np, pandas as pd
from scipy import stats, optimize
HERE = os.path.dirname(os.path.abspath(__file__)); LOG0 = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/logs"; LOG1 = f"{HERE}/logs"
TR = lambda s: s.astype(str) == "True"; L, SG = 139.0, 211.2 * 0.01
def ov(d):
    o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{d}/chunk_*.csv")); o = o[o.config == "LITERAL"]
    if o.event.nunique() != 9139: return None                                   # run still in progress: skipped
    return dict(n=9139, plane=int(TR(o.plane).sum()), mult=int((TR(o.plane) & TR(o.mult)).sum()), sr=int((TR(o.plane) & TR(o.mult) & TR(o.final)).sum()))
def pu(d):
    p = pd.concat(pd.read_csv(f) for f in glob.glob(f"{d}/chunk_*.csv"))
    if p.event_i.nunique() != 5000: return None
    sel = TR(p.sec3c_plane_found) & (p.sec3c_dw < 1)
    return dict(n=5000, plane=int(TR(p.sec3c_plane_found).sum()), mult=int((sel & (p.sec3c_n_layers >= 8)).sum()), sr=int(TR(p.final_sec_iv_pass).sum()))
def s95(b):                                                                  # 95% CLs signal, median expectation n_obs = round(b)
    n = int(round(b)); return optimize.brentq(lambda s: stats.poisson.cdf(n, s + b) / stats.poisson.cdf(n, b) - 0.05, 1e-3, 300)
rows = []
for lab, sct, f, d0, d1 in (("conversion + pile-up", "Z1160", ov, "P10_chunks_LITERAL", "P10"), ("conversion + pile-up", "Z0", ov, "P10_chunks_B_Z0_REF34", "P17b"),
                            ("pile-up only", "Z1160", pu, "P8_chunks_LITERAL", "P8")):
    for mu, d in ((50, f"{LOG0}/{d0}"), (33.7, f"{LOG1}/{d1}_mu33p7"), (20, f"{LOG1}/{d1}_mu20")):
        if not glob.glob(f"{d}/chunk_*.csv"): continue
        c = f(d)
        if c is None: print(f"skipped (incomplete): {d}"); continue
        r = dict(process=lab, sct=sct, mu=mu, **c)
        if lab.startswith("conversion"):
            r["N_bkg_139fb"] = L * SG * c["sr"] / c["n"]; r["N_bkg_UL95_139fb"] = L * SG * (1 - 0.05 ** (1 / c["n"])) if c["sr"] == 0 else np.nan
            r["s95_CLs_139fb"] = s95(r["N_bkg_UL95_139fb"] if c["sr"] == 0 else r["N_bkg_139fb"])
        else:
            lo, hi = stats.binomtest(c["sr"], c["n"]).proportion_ci(0.95, "wilson"); r["prob_per_event"] = c["sr"] / c["n"]; r["prob_UL95"] = 1 - 0.05 ** (1 / c["n"]) if c["sr"] == 0 else hi
        rows.append(r)
B = pd.DataFrame(rows); B.to_csv(f"{HERE}/S1_background_run2.csv", index=False); pd.set_option("display.width", 220); print(B.round(4).to_string(index=False))
