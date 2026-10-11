#!/usr/bin/env python3
"""F16: does one SCT z setting reproduce the paper's Fig. 5 for both signal and conversions?
Left: EW2000 signal Delta_s (fiducial, plane + hit multiplicity). Right: converted-photon Delta_s (all reconstructed planes; with
SCT z 1.16 mm no conversion passes the hit-multiplicity cut, so 'all planes' is the only populated set). |eta|<1.8, common beam-spot
shift, fit from the vertex. Paper: digitised Fig. 5, unit area. Bins: the paper's own (10 per decade); values below 1e-4 cm drawn in the first bin."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; FIG5 = f"{HERE}/../../PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/paper_fig5_extracted.json"
TR = lambda s: s.astype(str) == "True"; f5 = json.load(open(FIG5))["delta_s_cm"]["histograms"]
pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); cv = pd.read_csv(f"{T}/conversion_acceptance_A_per_event.csv")
rows = []
for z, nm in [("Z1160", "SCT z 1.16 mm"), ("Z0", "no SCT z smearing")]:
    x = pe[(pe["sample"] == "EW2000") & (pe.geom == "A") & (pe.sct == z) & (pe.bs == "CV") & TR(pe.fid) & TR(pe.plane) & TR(pe.mult)].ds
    rows += [dict(panel="signal", series=nm, ds_cm=v) for v in x]
    y = cv[(cv.config == f"A_{z}_PV") & TR(cv.plane)].ds
    rows += [dict(panel="conversion", series=nm, ds_cm=v) for v in y]
for pan, lab in [("signal", "EW Quirk"), ("conversion", "Converted gamma")]:
    h = f5[lab]; tot = sum(t["height"] for t in h)
    rows += [dict(panel=pan, series="paper Fig. 5", bin_lo=t["lo"], bin_hi=t["hi"], frac=t["height"] / tot) for t in h]
src = pd.DataFrame(rows); E = 10 ** np.arange(-4, -0.99, 0.1)
def plot(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.6))
    for ax, pan, title in zip(axes, ["signal", "conversion"], ["EW signal (EW2000), plane + hit multiplicity", "converted photons, all reconstructed planes"]):
        g = d[d.panel == pan]; p = g[g.series == "paper Fig. 5"]
        pb = (p.frac[p.bin_hi <= 0.0100001]).sum()
        ax.stairs(p.frac.values, np.r_[p.bin_lo.values, p.bin_hi.values[-1]], color=fu.INK, lw=1.8, ls=":", label=f"paper Fig. 5: {100*pb:.0f}% below cut")
        for nm, col, ls in [("SCT z 1.16 mm", fu.SERIES[1], "-"), ("no SCT z smearing", fu.SERIES[0], "--")]:
            v = g[g.series == nm].ds_cm.dropna(); hh = np.histogram(np.clip(v, 1.0001e-4, None), bins=E)[0].astype(float)
            ax.stairs(hh / max(hh.sum(), 1), E, color=col, lw=2, ls=ls, label=f"{nm}: {100*(v < 0.01).mean():.0f}% below cut (N = {len(v)})")
        ax.axvline(0.01, color=fu.MUTED, lw=1); ax.set_xscale("log"); ax.set_xlabel("Δs (cm); cut at 0.01 cm"); ax.set_title(title, fontsize=9); ax.legend(fontsize=7, loc="upper left" if pan == "signal" else "upper center")
    axes[0].set_ylabel("fraction per bin"); fig.tight_layout(); return fig
fu.figure("F16_ds_signal_vs_conversion", src, plot,
          "Δs against the paper's Fig. 5 for the EW signal (left) and converted photons (right), with SCT z smearing of 1.16 mm and without. The signal "
          "agrees better without smearing; the conversions agree better with 1.16 mm. No single setting reproduces both panels of the paper's Fig. 5. "
          "Converted photons: all reconstructed planes (with 1.16 mm none passes the hit-multiplicity cut). Values below 10⁻⁴ cm are drawn in the first bin.",
          [f"{T}/acceptance_longitudinal_per_event.csv", f"{T}/conversion_acceptance_A_per_event.csv", FIG5], "EW2000 signal; 9139 conversions; acceptance A", os.path.abspath(__file__))
