#!/usr/bin/env python3
"""Figure 5-style Delta_s and Delta_w, current setup, unit area on the paper's own log bins (10 per decade), vs the paper's digitised Fig. 5.
colored / EW   : COL2000 / EW2000, Ref. [27] lengths, no SCT z smearing, plane + hit multiplicity (before the last cut)
converted gamma: conversion + mu=50 pile-up, Ref. [27] lengths, SCT z 580 um, cited material model [34], plane + hit multiplicity
pile-up        : pile-up only (existing run: Ref. [27] lengths, SCT z 1.16 mm, pixel merging), all reconstructed planes
Our Delta_w is sqrt(lambda_2) (paper Eq. 11); the paper's plotted Delta_w appears to be 0.5*sqrt(lambda_2)."""
import os, sys, glob, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; L = f"{HERE}/../logs"; FIG5 = f"{HERE}/../../PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/paper_fig5_extracted.json"
TR = lambda s: s.astype(str) == "True"; f5 = json.load(open(FIG5)); rows = []
pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv")
for pop, smp in [("colored", "COL2000"), ("EW", "EW2000")]:
    x = pe[(pe["sample"] == smp) & (pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV") & TR(pe.fid) & TR(pe.plane) & TR(pe.mult)]
    rows += [dict(population=pop, ds_cm=a, dw_cm=b) for a, b in zip(x.ds, x.dw)]
o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{L}/P10_chunks_B_Z580_REF34/chunk_*.csv")); o = o[(o.config == "LITERAL") & TR(o.plane) & TR(o.mult)]
rows += [dict(population="converted γ + pile-up", ds_cm=a, dw_cm=b) for a, b in zip(o.ds, o.dw)]
p = pd.concat(pd.read_csv(f) for f in glob.glob(f"{L}/P8_chunks_LITERAL/chunk_*.csv")); p = p[TR(p.sec3c_plane_found)]
rows += [dict(population="pile-up", ds_cm=a, dw_cm=b) for a, b in zip(p.sec3c_ds, p.sec3c_dw)]
LAB = {"colored": "Colored Quirk", "EW": "EW Quirk", "converted γ + pile-up": "Converted gamma", "pile-up": "Pileup"}
for pop, lab in LAB.items():
    for var in ("delta_s_cm", "delta_w_cm"):
        h = f5[var]["histograms"][lab]; tot = sum(t["height"] for t in h)
        rows += [dict(population=pop, paper_var=var, bin_lo=t["lo"], bin_hi=t["hi"], paper_frac=t["height"] / tot) for t in h]
src = pd.DataFrame(rows)
POPS = ["colored", "EW", "converted γ + pile-up", "pile-up"]; NOTE = {"colored": "COL2000, no SCT z smearing", "EW": "EW2000, no SCT z smearing", "converted γ + pile-up": "SCT z 580 µm, cited material model", "pile-up": "SCT z 1.16 mm (existing run), all planes"}
EDG = {"ds_cm": 10 ** np.arange(-4, -0.99, 0.1), "dw_cm": 10 ** np.arange(-3, 1.01, 0.1)}; PV = {"ds_cm": "delta_s_cm", "dw_cm": "delta_w_cm"}
def plot(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 4, figsize=(13, 5.6))
    for i, var in enumerate(["ds_cm", "dw_cm"]):
        for j, pop in enumerate(POPS):
            ax = axes[i, j]; e = EDG[var]; v = d[(d.population == pop) & d[var].notna()][var]
            hh = np.histogram(np.clip(v, e[0] * 1.0001, None), bins=e)[0].astype(float)
            ax.stairs(hh / max(hh.sum(), 1), e, color=fu.SERIES[j], lw=2, label=f"this work (N = {len(v)})")
            pp = d[(d.population == pop) & (d.paper_var == PV[var])]
            ax.stairs(pp.paper_frac.values, np.r_[pp.bin_lo.values, pp.bin_hi.values[-1]], color=fu.INK, lw=1.4, ls=":", label="paper Fig. 5")
            ax.axvline(0.01 if var == "ds_cm" else 1.0, color=fu.MUTED, lw=1); ax.set_xscale("log"); ax.tick_params(labelsize=7)
            ax.set_xlabel("Δs (cm)" if var == "ds_cm" else "Δw (cm)", fontsize=8)
            if i == 0: ax.set_title(f"{pop}\n{NOTE[pop]}", fontsize=8)
            if j == 0: ax.set_ylabel("fraction per bin", fontsize=8)
            ax.legend(fontsize=6.5, loc="upper left")
    fig.tight_layout(); return fig
fu.figure("F21_fig5_current", src, plot, "Figure 5-style Δs (top) and Δw (bottom), current setup, unit area on the paper's log bins; dotted = paper's Fig. 5 "
          "(digitised, unit area). Vertical lines = signal-region cuts. Our Δw is √λ₂ (paper Eq. 11); the paper's plotted Δw appears to be ½√λ₂.",
          [f"{T}/acceptance_longitudinal_per_event.csv", f"{L}/P10_chunks_B_Z580_REF34", f"{L}/P8_chunks_LITERAL", FIG5], "see caption", os.path.abspath(__file__))
print(src.dropna(subset=["ds_cm"]).groupby("population").size())
