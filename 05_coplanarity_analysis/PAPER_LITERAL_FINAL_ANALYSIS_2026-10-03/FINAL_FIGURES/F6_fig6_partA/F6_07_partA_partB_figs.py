#!/usr/bin/env python3
"""Figure 6 split for the Part A / Part B report (2026-10-21). No new computation: the plotting code of F6_03_contours.py (its figure section, unchanged) is
run on the stored grid fig6/F6_N_grid.csv and reach table fig6/F6_reach.csv.
  F6_fig6_partA: the paper's literal method only - signal SCT z = 1.16 mm, ε_trig = matched count, no K-factor, no N_Q factor; colored with the both-charged
                 factor f_ch. No LO-ratio line in the reach box, no "without f_ch" contour.
  F6_fig6_partB_noSCT: deviation "no SCT z smearing" (otherwise the same settings), with the colored contour without f_ch as in F6_fig6.
F6_fig6 itself is not changed."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
src = open(f"{HERE}/F6_03_contours.py").read()
fig_part = src[src.index("# ---------------------------------------------------------------- figure"):src.index("_C = C.set_index")]   # imports, Yd, contours(), panel()
ns = dict(__name__="f6_07", __file__=f"{HERE}/F6_03_contours.py")
exec("import os, sys, re, json, numpy as np, pandas as pd\nfrom scipy import stats\n", ns)
ns.update(HERE=HERE, ROOT=f"{HERE}/..", OUT=f"{HERE}/../fig6")
G = pd.read_csv(f"{HERE}/../fig6/F6_N_grid.csv"); ns["G"] = G; ns["LAMS"] = tuple(sorted(G.lambda_keV.unique()))
exec(fig_part, ns)
ns["RSE"] = None                                                              # -> lo_alt() returns None: no LO-ratio line in the reach boxes
_contours = ns["contours"]
fu, plt = ns["fu"], ns["plt"]
from matplotlib.lines import Line2D

def make(name, sct, with_nofch, title, caption):
    ns["contours"] = (lambda ax, g, col, a, b, lw, label: None if (label != "this work" and not with_nofch) else _contours(ax, g, col, a, b, lw, label))
    def plot(_):
        fig, axs = plt.subplots(1, 2, figsize=(13, 5.9))
        for ax, ch in zip(axs, ("colored", "EW")): ns["panel"](ax, ch, sct)
        h = [Line2D([], [], color=fu.INK, ls="--", lw=1.6, label="paper: exclusion (3 events)"), Line2D([], [], color=fu.INK, ls="-", lw=1.6, label="paper: discovery (5 events)"),
             Line2D([], [], color=fu.SERIES[0], ls="--", lw=2.4, label="this work: exclusion (3 events)"), Line2D([], [], color=fu.SERIES[0], ls="-", lw=2.4, label="this work: discovery (5 events)")]
        if with_nofch:
            h += [Line2D([], [], color=fu.SERIES[1], ls="--", lw=1.3, label="colored, without the both-charged factor: exclusion"),
                  Line2D([], [], color=fu.SERIES[1], ls="-", lw=1.3, label="colored, without the both-charged factor: discovery")]
        h += [Line2D([], [], color="#7fbf7f", lw=1.2, label="HSCP 12.9 / 300 fb⁻¹ (from the paper)"), Line2D([], [], color="#b5b5b5", lw=1.2, label="monojet 12.9 / 300 fb⁻¹ (from the paper)"),
              Line2D([], [], color="#9cb9d1", ls=":", lw=1.2, label="d$_{cm}$ (from the paper)"),
              Line2D([], [], marker="o", ls="", color=fu.INK2, ms=4, label="grid point with ≥ 1 event in the signal region"),
              Line2D([], [], marker="x", ls="", color=fu.MUTED, ms=6, label="0 events passed: N < 3 at 95% CL"),
              Line2D([], [], marker="x", ls="", color=fu.SERIES[7], ms=6, label="0 events passed: not resolved (95% UL on N ≥ 3)"),
              Line2D([], [], marker="o", ls="", color=fu.MUTED, mfc="none", ms=4, label="not propagated: N < 3 even with ε$_{fid}$ = ε$_{reco}$ = 1")]
        fig.legend(handles=h, loc="lower center", ncol=3, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.13))
        fig.suptitle(title, fontsize=10.5); fig.tight_layout(); return fig
    fu.figure(name, G[G.sct == sct].copy(), plot, caption, [f"{HERE}/../fig6/F6_N_grid.csv", f"{HERE}/../fig6/F6_reach.csv", f"{HERE}/../tables/paper_fig6_vector.json"],
              f"grid points with SCT z = {sct}", os.path.abspath(__file__))

make("F6_fig6_partA", "Z1160", False,
     "Figure 6, paper's literal method: 3 (exclusion) and 5 (discovery) signal events at 300 fb⁻¹, no background\n"
     "signal SCT z = 1.16 mm; ε_trig = matched count with p_T(QQ̄) > 200 GeV; LO σ (0 + 1 jet, MLM-matched); no K-factor, no N_Q factor",
     "Figure 6 with the paper's literal method only: N = L σ ε_trig [f_ch] ε_fid ε_reco at L = 300 fb⁻¹, signal SCT z = 1.16 mm, ε_trig = N(p_T(QQ̄) > 200 GeV) / N(matched), "
     "LO σ of the MLM-matched 0 + 1 jet sample, no K-factor, no N_Q factor; colored includes the both-charged factor f_ch. Same grid and reach as F6_fig6 (left column).")
make("F6_fig6_partB_noSCT", "Z0", True,
     "Figure 6, deviation tested: no SCT z smearing (everything else as the paper's method)\n"
     "3 (exclusion) and 5 (discovery) signal events at 300 fb⁻¹, no background",
     "Figure 6 with signal SCT z smearing switched off (deviation tested in Part B); otherwise as F6_fig6_partA. Thin orange: colored without the both-charged factor. "
     "Same grid and reach as F6_fig6 (right column).")
print("written F6_fig6_partA, F6_fig6_partB_noSCT")
