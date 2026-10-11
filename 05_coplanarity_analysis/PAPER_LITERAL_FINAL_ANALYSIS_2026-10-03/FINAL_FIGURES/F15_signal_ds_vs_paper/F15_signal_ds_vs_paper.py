#!/usr/bin/env python3
"""F15: signal Delta_s (plane + hit multiplicity, i.e. 'before the final cut') for EW2000 and COL2000, literal geometry,
with the literal SCT z smearing (1160 um) and with no z smearing (calibrated diagnostic), vs the paper's digitised Fig. 5.
Unit-area histograms on the paper's own 10-per-decade log bins; the vertical line is the 0.01 cm cut."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; FIG5 = f"{HERE}/../../PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/paper_fig5_extracted.json"
TR = lambda s: s.astype(str) == "True"
pe = pd.read_csv(f"{T}/signal_per_event_all_configs.csv")
rows = []
for smp, lab in [("EW2000", "EW Quirk"), ("COL2000", "Colored Quirk")]:
    for sct, name in [("Z1160", "literal (SCT z 1.16 mm)"), ("Z0", "no SCT z smearing (calibrated)")]:
        x = pe[(pe["sample"] == smp) & (pe.geom == "B") & (pe.sct == sct) & (pe.wconv == "W1") & TR(pe.fid) & TR(pe.plane) & TR(pe.mult)]
        rows += [dict(sample=smp, series=name, ds_cm=v, bin_lo=np.nan, bin_hi=np.nan, frac=np.nan) for v in x.ds]
    h = json.load(open(FIG5))["delta_s_cm"]["histograms"][lab]; tot = sum(t["height"] for t in h)
    rows += [dict(sample=smp, series="paper Fig. 5 (digitised)", ds_cm=np.nan, bin_lo=t["lo"], bin_hi=t["hi"], frac=t["height"] / tot) for t in h]
src = pd.DataFrame(rows); E = 10 ** np.arange(-4, -0.99, 0.1)

def plot(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.4), sharey=True)
    for ax, smp, title in zip(axes, ["EW2000", "COL2000"], ["EW 800 GeV, Λ = 4 keV (EW2000)", "colored 1800 GeV, Λ = 2 keV (COL2000)"]):
        g = d[d["sample"] == smp]
        p = g[g.series.str.startswith("paper")]
        ax.stairs(p.frac.values, np.r_[p.bin_lo.values, p.bin_hi.values[-1]], color=fu.INK, lw=1.6, ls=":", label="paper Fig. 5")
        for j, (nm, col, ls) in enumerate([("literal (SCT z 1.16 mm)", fu.SERIES[1], "-"), ("no SCT z smearing (calibrated)", fu.SERIES[0], "--")]):
            v = g[g.series == nm].ds_cm.dropna(); hh = np.histogram(v, bins=E)[0].astype(float)
            ax.stairs(hh / max(hh.sum(), 1), E, color=col, lw=2, ls=ls, label=f"{nm}, N = {len(v)}, median {np.median(v)*1e4:.0f} µm")
        ax.axvline(0.01, color=fu.MUTED, lw=1); ax.text(0.0105, ax.get_ylim()[1] * 0.02 if False else 0.0, "", fontsize=7)
        ax.set_xscale("log"); ax.set_xlabel("Δs (cm)  — signal-region cut at 0.01 cm"); ax.set_title(title, fontsize=9); ax.legend(fontsize=6.8, loc="upper left")
    axes[0].set_ylabel("fraction of events per bin"); fig.tight_layout(); return fig

fu.figure("F15_signal_ds_vs_paper", src, plot,
          "Signal Δs before the final cut (plane + hit multiplicity), literal geometry, unit area on the paper's log bins. With the SCT z smearing "
          "the text implies (1.16 mm) our Δs sits well right of the paper's Fig. 5 (EW median 110 µm vs ~28 µm); without it, it moves close to the paper (44 µm) but not exactly onto it.",
          [f"{T}/signal_per_event_all_configs.csv", FIG5], "EW2000 and COL2000, geometry B, plane & mult", os.path.abspath(__file__))
for (s, n), g in src.dropna(subset=["ds_cm"]).groupby(["sample", "series"]): print(s, n, len(g), round(g.ds_cm.median() * 1e4), "um")
