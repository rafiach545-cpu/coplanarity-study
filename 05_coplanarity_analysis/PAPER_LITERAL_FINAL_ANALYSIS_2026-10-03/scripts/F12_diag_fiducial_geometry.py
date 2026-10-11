#!/usr/bin/env python3
"""DIAGNOSTIC F12 (U4): fiducial efficiency, literal finite barrel (geometry B, ref. [27]) vs project eta-cone |eta|<1.8
(geometry A, systematic), each sample separately, Wilson 95%, vs paper 0.28."""
import os, sys, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"
s = pd.read_csv(f"{T}/signal_efficiency_statistics.csv")
src = s[(s.quantity == "fiducial") & (s.dw_convention == "W1") & (s.sct_z == "Z1160")][["sample", "config", "geometry", "N_pass", "N_total", "eff", "wilson95_lo", "wilson95_hi", "paper", "p_exact_vs_paper_quoted"]]
SAMPLES = ["COL1000", "COL2000", "EW1000", "EW2000"]
def plot(d):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for j, (g, lab) in enumerate([("B", "finite barrel, ref. [27] (LITERAL)"), ("A", "η-cone |η|<1.8 (project; systematic)")]):
        x = d[d.geometry == g].set_index("sample").loc[SAMPLES].reset_index(); xs = np.arange(4) + (j - 0.5) * 0.22
        ax.errorbar(xs, x.eff, yerr=[x.eff - x.wilson95_lo, x.wilson95_hi - x.eff], fmt=fu.MARKERS[j], color=fu.SERIES[j], ms=7, label=lab)
        for xx, r in zip(xs, x.itertuples()): ax.annotate(f"{r.N_pass}/{r.N_total}", (xx, r.wilson95_hi), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=6.5, color=fu.INK2)
    ax.axhline(0.28, color=fu.INK, ls="--", lw=1.2, label="paper Table I 0.28")
    ax.set_xticks(range(4), SAMPLES); ax.set_ylabel("ε_fid (Wilson 95%)"); ax.set_ylim(0, 0.7); ax.legend(fontsize=7, loc="upper left"); fig.tight_layout(); return fig
fu.figure("F12_diag_fiducial_geometry", src, plot,
          "DIAGNOSTIC (UNRESOLVED_DIFFERENCES.md U4): fiducial efficiency with the literal finite-barrel acceptance from ref. [27] vs the project's "
          "η-cone |η| < 1.8 reading of the paper's '|η| ≲ 1.8' remark, each sample separately (Wilson 95%). The literal geometry reproduces the "
          "paper's 0.28 in all four samples; the η-cone overshoots for EW.", [f"{T}/signal_efficiency_statistics.csv"], "fiducial, SCT Z1160, W1", os.path.abspath(__file__))
print(src.to_string())
