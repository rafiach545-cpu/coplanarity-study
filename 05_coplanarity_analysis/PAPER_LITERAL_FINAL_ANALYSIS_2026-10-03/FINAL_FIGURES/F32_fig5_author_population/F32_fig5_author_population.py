#!/usr/bin/env python3
"""Fig. 5 signal panels with the authors' population (D18: before the Delta_s and Delta_w cuts): plane found by Sec. III C, smallest Delta_s,
no final Delta_w or Delta_s cut, no hit-multiplicity cut. COL2000 / EW2000, first crossing; SCT z none, 580 um (Ref. [27]), 1.16 mm (2 x 580 um).
Paper histograms from its vector source figure (tables/paper_fig5_vector.json). Unit area on the paper's 0.1-dex bins."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; TR = lambda s: s.astype(str) == "True"
d = pd.read_csv(f"{T}/fig5_author_population.csv"); d = d[TR(d.fid) & TR(d.plane_any)][["sample", "key", "sct", "ds_any", "dw_any"]]
V = json.load(open(f"{T}/paper_fig5_vector.json")); rows = [d.assign(kind="this work")]
for s, lab in (("COL2000", "Colored Quirk"), ("EW2000", "EW Quirk")):
    for v, k in (("ds", "delta_s_cm"), ("dw", "delta_w_cm")):
        h = V[k]["histograms"][lab]; t = sum(b["height"] for b in h)
        rows.append(pd.DataFrame(dict(sample=s, kind="paper", var=v, lo=[b["lo"] for b in h], hi=[b["hi"] for b in h], frac=[b["height"] / t for b in h])))
src = pd.concat(rows, ignore_index=True)
EDG = {"ds": 10 ** np.arange(-4, -0.99, 0.1), "dw": 10 ** np.arange(-3, 0.51, 0.1)}; COL = {"Z0": fu.SERIES[1], "Z580": fu.SERIES[0], "Z1160": fu.SERIES[2]}
LAB = {"Z0": "no SCT z smearing", "Z580": "SCT z 580 µm", "Z1160": "SCT z 1.16 mm"}
def plot(x):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(11, 6.2))
    for j, (s, t) in enumerate((("COL2000", "colored 1.8 TeV, 2 keV"), ("EW2000", "EW 800 GeV, 4 keV"))):
        for i, (v, col) in enumerate((("ds", "ds_any"), ("dw", "dw_any"))):
            ax = axs[i, j]; e = EDG[v]
            for z in ("Z0", "Z580", "Z1160"):
                y = x[(x["sample"] == s) & (x.kind == "this work") & (x.sct == z)][col]
                hh = np.histogram(np.clip(y, e[0] * 1.0001, e[-1] * 0.9999), bins=e)[0].astype(float)
                ax.stairs(hh / max(hh.sum(), 1), e, color=COL[z], lw=2, label=f"{LAB[z]} (N = {len(y)}, median {y.median()*(1e4 if v=='ds' else 1):.0f} µm)" if v == "ds" else f"{LAB[z]} (median {y.median():.3f} cm)")
            p = x[(x["sample"] == s) & (x.kind == "paper") & (x["var"] == v)]; ax.stairs(p.frac.values, np.r_[p.lo.values, p.hi.values[-1]], color=fu.INK, lw=1.4, ls=":", label="paper Fig. 5")
            ax.axvline(0.01 if v == "ds" else 1.0, color=fu.MUTED, lw=1); ax.set_xscale("log"); ax.set_xlabel("Δs (cm)" if v == "ds" else "Δw (cm)"); ax.set_ylabel("fraction per bin")
            ax.set_title(t, fontsize=9); ax.legend(fontsize=6.8, loc="upper left")
    fig.tight_layout(); return fig
fu.figure("F32_fig5_author_population", src, plot, "Signal Δs (top) and Δw (bottom) with the authors' Fig. 5 population: plane found, before the Δs and Δw cuts, no hit-multiplicity cut. "
          "Three SCT z settings; dotted: the paper's Fig. 5 from its vector source figure. Vertical lines: the signal-region cuts.",
          [f"{T}/fig5_author_population.csv", f"{T}/paper_fig5_vector.json"], "plane found, no final cuts", os.path.abspath(__file__))
