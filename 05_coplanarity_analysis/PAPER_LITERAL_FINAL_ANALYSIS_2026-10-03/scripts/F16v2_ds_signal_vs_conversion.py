#!/usr/bin/env python3
"""F16v2: the paper's Fig. 5 is dsigma/dlog(Delta_s) in fb/bin; its conversion histogram is the population that enters the
signal-region Delta_s cut, i.e. converted photon + pile-up after plane + hit multiplicity (paper Sec. III D: conversions are
overlaid with pile-up). Left: EW2000 signal Delta_s (plane + multiplicity), unit area (signal normalisation not compared).
Right: conversion + pile-up after plane + multiplicity, in fb/bin = sigma(paper 1 pb) x 1% x (events/9139), for SCT z 1.16 mm
(P10e) and no SCT z smearing (P10f); paper histogram as digitised (fb/bin). Bins: the paper's own (10/decade)."""
import os, sys, json, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; L = f"{HERE}/../logs"; FIG5 = f"{HERE}/../../PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/paper_fig5_extracted.json"
TR = lambda s: s.astype(str) == "True"; f5 = json.load(open(FIG5))["delta_s_cm"]["histograms"]
pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); rows = []
for z, nm in [("Z1160", "SCT z 1.16 mm"), ("Z0", "no SCT z smearing")]:
    x = pe[(pe["sample"] == "EW2000") & (pe.geom == "A") & (pe.sct == z) & (pe.bs == "CV") & TR(pe.fid) & TR(pe.plane) & TR(pe.mult)].ds
    rows += [dict(panel="signal", series=nm, ds_cm=v, weight_fb=np.nan) for v in x]
for d_, nm in [("P10_chunks_ETA", "SCT z 1.16 mm"), ("P10_chunks_ETA_Z0", "no SCT z smearing")]:
    o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{L}/{d_}/chunk_*.csv")); o = o[o.config == "LITERAL"]; assert o.event.nunique() == 9139, d_
    m = o[TR(o.plane) & TR(o.mult)]
    rows += [dict(panel="conversion", series=nm, ds_cm=v, weight_fb=1000.0 * 0.01 / 9139) for v in m.ds]
for pan, lab in [("signal", "EW Quirk"), ("conversion", "Converted gamma")]:
    h = f5[lab]; tot = sum(t["height"] for t in h)
    rows += [dict(panel=pan, series="paper Fig. 5", bin_lo=t["lo"], bin_hi=t["hi"], frac=t["height"] / tot, fb=t["height"]) for t in h]
src = pd.DataFrame(rows); E = 10 ** np.arange(-4, -0.99, 0.1)
def plot(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 3.7))
    ax = axes[0]; g = d[d.panel == "signal"]; p = g[g.series == "paper Fig. 5"]
    ax.stairs(p.frac.values, np.r_[p.bin_lo.values, p.bin_hi.values[-1]], color=fu.INK, lw=1.8, ls=":", label=f"paper Fig. 5: {100*p.frac[p.bin_hi <= 0.0100001].sum():.0f}% below cut")
    for nm, col, ls in [("SCT z 1.16 mm", fu.SERIES[1], "-"), ("no SCT z smearing", fu.SERIES[0], "--")]:
        v = g[g.series == nm].ds_cm.dropna(); hh = np.histogram(v, bins=E)[0].astype(float)
        ax.stairs(hh / max(hh.sum(), 1), E, color=col, lw=2, ls=ls, label=f"{nm}: {100*(v < 0.01).mean():.0f}% below cut (N = {len(v)})")
    ax.set_ylabel("fraction per bin"); ax.set_title("EW signal (EW2000), plane + hit multiplicity", fontsize=9)
    bx = axes[1]; g = d[d.panel == "conversion"]; p = g[g.series == "paper Fig. 5"]
    bx.stairs(np.maximum(p.fb.values, 1e-7), np.r_[p.bin_lo.values, p.bin_hi.values[-1]], color=fu.INK, lw=1.8, ls=":", label=f"paper Fig. 5: {p.fb.sum():.3f} fb, {100*p.fb[p.bin_hi <= 0.0100001].sum()/p.fb.sum():.1f}% below cut")
    for nm, col, ls in [("SCT z 1.16 mm", fu.SERIES[1], "-"), ("no SCT z smearing", fu.SERIES[0], "--")]:
        gg = g[g.series == nm]; v = gg.ds_cm.values; w = gg.weight_fb.values
        hh = np.histogram(np.clip(v, 1.0001e-4, None), bins=E, weights=w)[0]
        bx.stairs(np.maximum(hh, 1e-7), E, color=col, lw=2, ls=ls, label=f"{nm}: {w.sum():.3f} fb, {100*(v < 0.01).mean():.1f}% below cut (N = {len(v)})")
    bx.set_yscale("log"); bx.set_ylim(5e-5, 0.2); bx.set_ylabel("fb per bin (σ = 1 pb × 1%)"); bx.set_title("converted γ + pile-up, plane + hit multiplicity", fontsize=9)
    for a in axes: a.axvline(0.01, color=fu.MUTED, lw=1); a.set_xscale("log"); a.set_xlabel("Δs (cm); cut at 0.01 cm"); a.legend(fontsize=6.6, loc="upper left")
    fig.tight_layout(); return fig
fu.figure("F16v2_ds_signal_vs_conversion", src, plot,
          "Δs against the paper's Fig. 5. Left: EW signal, unit area. Right: converted photon + μ = 50 pile-up after plane and hit multiplicity (the population "
          "that enters the Δs cut), in fb per bin using the paper's σ ≈ 1 pb and 1% conversion probability, as in the paper's dσ/dlogΔs axis. "
          "SCT z smearing 1.16 mm (solid) vs none (dashed); dotted = paper.", [f"{T}/acceptance_longitudinal_per_event.csv", f"{L}/P10_chunks_ETA", f"{L}/P10_chunks_ETA_Z0", FIG5], "see caption", os.path.abspath(__file__))
for (pn, s), g in src.dropna(subset=["ds_cm"]).groupby(["panel", "series"]): print(pn, s, len(g), f"median {g.ds_cm.median()*1e4:.0f} um", f"below {(g.ds_cm < 0.01).mean():.3f}")
