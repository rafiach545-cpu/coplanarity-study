#!/usr/bin/env python3
"""Reconstruction efficiency with every layer crossing (< 25 ns) used as a hit, for each SCT z setting and both readings of the
paper's multiplicity cut ("All but one layer must contain 2 hits"): at least 2 and exactly 2. Source: tables/v7_primary_table_I.csv."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; V = pd.read_csv(f"{T}/v7_primary_table_I.csv"); src = V[V.quantity == "reconstruction"].copy()
def plot(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True); SC = ["Z0", "Z580", "Z1160"]; LB = ["none", "580 µm", "1.16 mm"]
    for j, s in enumerate(["COL1000", "COL2000", "EW1000", "EW2000"]):
        ax = axes[j]
        for m, (mu, off, col, mk) in enumerate([("at least 2 (primary)", -0.1, fu.SERIES[0], "o"), ("exactly 2 (sensitivity)", 0.1, fu.SERIES[1], "s")]):
            g = d[(d["sample"] == s) & (d.multiplicity == mu)].set_index("sct").loc[SC]; x = np.arange(3) + off
            ax.errorbar(x, g.frac, yerr=[g.frac - g.wilson95_lo, g.wilson95_hi - g.frac], fmt=mk, ms=7, color=col, capsize=3, lw=1.5, label=mu.replace(" (primary)", "").replace(" (sensitivity)", "") + " hits per layer")
            for xi, (k, n) in zip(x, zip(g.k, g.n)): ax.annotate(f"{k}/{n}", (xi, -0.07), ha="center", fontsize=6.5, color=fu.INK2)
        ax.axhline(d[d["sample"] == s].paper_value.iloc[0], color=fu.INK, ls="--", lw=1.2, label="paper")
        ax.set_xticks(range(3)); ax.set_xticklabels(LB, fontsize=8); ax.set_xlabel("SCT z smearing (signal)", fontsize=8); ax.set_title(s, fontsize=9); ax.set_ylim(-0.12, 1.02)
        if j == 0: ax.set_ylabel("ε_reco (Wilson 95%)", fontsize=8); ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout(); return fig
fu.figure("F27_reco_all_crossings", src, plot, "ε_reco with every layer crossing within 25 ns used as a hit. Circles: ≥ 2 hits in 7 layers; squares: exactly 2. "
          "Bars = Wilson 95%; dashed = paper (colored 0.35, EW 0.72); numbers = k/n.", [f"{T}/v7_primary_table_I.csv"], "all fiducial events", os.path.abspath(__file__))
