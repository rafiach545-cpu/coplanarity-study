#!/usr/bin/env python3
"""F13v2: pile-up per-event rates (5000 events each) for the existing |eta|<1.8 run (paper-stated acceptance; SCT 34/1160 um;
no pixel merging) and the finite-barrel run (inferred sensitivity; with merging), vs the paper's quoted rates."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"
pu = pd.read_csv(f"{T}/pileup_cutflow.csv")
lab = {"plane with >=1 hit in >=4/8 layers (paper 1e-3)": ("plane, ≥1 hit in ≥4/8 layers", 1e-3), "plane with >=1 hit in 8/8 layers = relaxed control (paper 6e-5)": ("plane, ≥1 hit in all 8 layers", 6e-5),
       "Sec. III C plane": ("any reconstructed plane", np.nan), "final Sec. IV": ("full signal region", np.nan)}
src = pu[pu.stage.isin(lab)].copy(); src["label"] = src.stage.map(lambda s: lab[s][0]); src["paper"] = src.stage.map(lambda s: lab[s][1])
src["run"] = np.where(src.config.str.startswith("FROZEN"), "|η| < 1.8 (paper-stated), no pixel merging", "finite barrel (inferred), with merging")
src = src[["run", "label", "k", "n", "frac", "wilson95_lo", "wilson95_hi", "cp95_upper_one_sided", "paper"]]
def plot(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.4, 3.5)); labels = list(dict.fromkeys(d.label))
    for j, (run, g) in enumerate(d.groupby("run", sort=False)):
        g = g.set_index("label").loc[labels].reset_index(); off = (j - 0.5) * 0.22
        for i, r in g.iterrows():
            y = i + off
            if r.k > 0:
                ax.plot([r.wilson95_lo, r.wilson95_hi], [y, y], color=fu.SERIES[j], lw=2.2); ax.plot(r.frac, y, fu.MARKERS[j], color=fu.SERIES[j], ms=7, label=run if i == 0 else None)
                ax.annotate(f"{r.k}/{r.n}", (r.wilson95_hi, y), xytext=(5, 0), textcoords="offset points", va="center", fontsize=7, color=fu.INK2)
            else:
                ax.plot([1e-6, r.cp95_upper_one_sided], [y, y], color=fu.SERIES[j], lw=1, ls=":"); ax.plot(r.cp95_upper_one_sided, y, "<", color=fu.SERIES[j], ms=7, label=run if i == 0 else None)
                ax.annotate(f"0/{r.n}", (r.cp95_upper_one_sided, y), xytext=(5, 0), textcoords="offset points", va="center", fontsize=7, color=fu.INK2)
    pp = d.drop_duplicates("label").set_index("label").loc[labels].reset_index()
    for i, r in pp.iterrows():
        if not np.isnan(r.paper): ax.plot(r.paper, i, "D", color=fu.INK, ms=7, label="paper" if i == 0 else None)
    ax.set_yticks(range(len(labels)), labels, fontsize=8.5); ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlim(2e-5, 0.1)
    ax.set_xlabel("fraction of pile-up events (μ = 50); ◁ = 95% upper limit when 0"); h, l = ax.get_legend_handles_labels(); u = dict(zip(l, h))
    ax.legend(u.values(), u.keys(), fontsize=7, loc="lower right"); fig.tight_layout(); return fig
fu.figure("F13v2_pileup_by_acceptance", src, plot,
          "Pile-up only (μ = 50), 5000 events per run: per-event rates with Wilson 95% intervals (one-sided 95% upper limit when 0) for the existing "
          "run with the paper-stated |η| < 1.8 acceptance (no pixel merging) and the finite-barrel run (inferred, with merging). Diamonds: paper.",
          [f"{T}/pileup_cutflow.csv"], "both runs", os.path.abspath(__file__))
print(src.to_string())
