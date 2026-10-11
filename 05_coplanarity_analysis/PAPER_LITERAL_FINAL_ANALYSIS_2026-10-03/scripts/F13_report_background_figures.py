#!/usr/bin/env python3
"""Clean report figures for the professor PDF (data only from verified tables):
F13_pileup_rates   : pile-up per-event rates (literal, 5000 events) with Wilson 95% bars / CP95 UL, vs the paper's quoted rates.
F14_conversion_flow: converted-photon cutflows (conversion only; conversion + pile-up), literal vs frozen project vs
                     the calibrated no-z-smearing variant; zero counts drawn as CP95 one-sided upper limits."""
import os, sys, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__)

pu = pd.read_csv(f"{T}/pileup_cutflow.csv"); pu = pu[pu.config.str.startswith("LITERAL")]
lab = {"plane with >=1 hit in >=4/8 layers (paper 1e-3)": ("plane, ≥1 hit in ≥4/8 layers", 1e-3),
       "plane with >=1 hit in 8/8 layers = relaxed control (paper 6e-5)": ("plane, ≥1 hit in all 8 layers", 6e-5),
       "Sec. III C plane": ("any reconstructed plane", np.nan), "final Sec. IV": ("full signal region", np.nan)}
src1 = pu[pu.stage.isin(lab)].copy(); src1["label"] = src1.stage.map(lambda s: lab[s][0]); src1["paper"] = src1.stage.map(lambda s: lab[s][1])
src1 = src1[["label", "k", "n", "frac", "wilson95_lo", "wilson95_hi", "cp95_upper_one_sided", "paper"]]

def plot1(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    for i, r in d.reset_index(drop=True).iterrows():
        if r.k > 0:
            ax.plot([r.wilson95_lo, r.wilson95_hi], [i, i], color=fu.SERIES[0], lw=2.5, solid_capstyle="round")
            ax.plot(r.frac, i, "o", color=fu.SERIES[0], ms=8, mec=fu.SURFACE, mew=1.5, label="this work (95% CI)" if i == 0 else None)
            ax.annotate(f"{r.k}/{r.n}", (r.wilson95_hi, i), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=fu.INK2)
        else:
            ax.plot([1e-6, r.cp95_upper_one_sided], [i, i], color=fu.SERIES[0], lw=1.2, ls=":")
            ax.plot(r.cp95_upper_one_sided, i, marker="<", color=fu.SERIES[0], ms=8, label="0 events: 95% upper limit")
            ax.annotate(f"0/{r.n}", (r.cp95_upper_one_sided, i), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=fu.INK2)
        if not np.isnan(r.paper):
            ax.plot(r.paper, i, marker="D", color=fu.INK, ms=7, ls="none", label="paper" if i == 0 else None)
    ax.set_yticks(range(len(d)), d.label, fontsize=9); ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlim(2e-5, 0.1)
    ax.set_xlabel("fraction of pile-up events (μ = 50)"); h, l = ax.get_legend_handles_labels(); u = dict(zip(l, h))
    ax.legend(u.values(), u.keys(), fontsize=7.5, loc="lower right"); fig.tight_layout(); return fig

fu.figure("F13_pileup_rates", src1, plot1,
          "Pile-up only (μ = 50, 5000 events, literal detector): per-event rates with Wilson 95% intervals; when no event passes, the one-sided "
          "Clopper–Pearson 95% upper limit is drawn. Diamonds: rates quoted in the paper (Sec. IV).",
          [f"{T}/pileup_cutflow.csv"], "config LITERAL", S)

cv = pd.read_csv(f"{T}/converted_photon_cutflow.csv"); ov = pd.read_csv(f"{T}/overlay_cutflow.csv")
rows = []
def take(d, cfgprefix, name):
    g = d[d.config.str.startswith(cfgprefix) & ~d.stage.str.contains("non-sequential|generated")]
    for st, key in [("plane", "Sec. III C plane"), ("hit multiplicity", "hit multiplicity"), ("Δw < 1 cm", "dw < 1 cm"), ("Δs < 0.01 cm (signal region)", "ds < 0.01")]:
        r = g[g.stage.str.startswith(key)].iloc[0]
        rows.append(dict(series=name, stage=st, k=r.k, n=r.n, frac=r.frac, cp95_upper=r.cp95_upper_one_sided))
take(cv, "LITERAL", "conversion only — literal")
take(ov, "LITERAL", "conversion + pile-up — literal")
take(ov, "FROZEN overlay v1 (all", "conversion + pile-up — old project setup")
take(cv, "SYS_Z0", "conversion only — no SCT z smearing (calibrated)")
src2 = pd.DataFrame(rows)

def plot2(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 3.6)); st = list(dict.fromkeys(d.stage))
    for j, (s, g) in enumerate(d.groupby("series", sort=False)):
        g = g.set_index("stage").loc[st]; x = np.arange(len(st)) + (j - 1.5) * 0.06
        v = g.frac.where(g.k > 0); ax.plot(x, v, marker=fu.MARKERS[j], ls=fu.STYLES[j], color=fu.SERIES[j], label=s, ms=7)
        z = g.k == 0
        ax.plot(x[z.values], g.cp95_upper[z], marker="v", ls="none", ms=8, mfc="none", mec=fu.SERIES[j], mew=1.4)
    ax.plot([], [], marker="v", ls="none", mfc="none", mec=fu.INK2, label="0 events: 95% upper limit")
    ax.set_yscale("log"); ax.set_ylim(3e-5, 1); ax.set_xticks(range(len(st)), st, fontsize=8.5)
    ax.set_ylabel("fraction of 9139 photons"); ax.legend(fontsize=7, loc="lower left"); fig.tight_layout(); return fig

fu.figure("F14_conversion_flow", src2, plot2,
          "Converted-photon background, 9139 Z(νν)γ+jet photons: fraction surviving each signal-region cut (sequential). Literal detector for "
          "conversion only and with μ = 50 pile-up overlaid; the old project setup (one event survived); and the calibrated variant without "
          "SCT z smearing (22 events survive). Open triangles: 95% upper limit when no event survives.",
          [f"{T}/converted_photon_cutflow.csv", f"{T}/overlay_cutflow.csv"], "as listed", S)
print(src1.to_string()); print(src2.to_string())
