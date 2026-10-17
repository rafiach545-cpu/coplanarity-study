#!/usr/bin/env python3
"""F39_fig2_combined: Fig. 2 with |L| and d on the same graph vs r (as in the paper): paper | this work, event with the paper's kinematics |
this work, one simulated event of our sample (COL2000 event no. 8). Data: tables/fig2_final/*.csv."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
D = f"{HERE}/../tables/fig2_final"; rows = []
pl = pd.read_csv(f"{D}/fig2_paper_L.csv"); pdd = pd.read_csv(f"{D}/fig2_paper_d.csv")
rows += [dict(panel="paper", curve="L", r_cm=a, y=b) for a, b in zip(pl.r_cm, pl.L_1e12_hbar)] + [dict(panel="paper", curve="d", r_cm=a, y=b) for a, b in zip(pdd.r_cm, pdd.d_cm)]
for k in ("constructed", "key8"):
    x = pd.read_csv(f"{D}/fig2_ours_{k}.csv").iloc[::3]
    rows += [dict(panel=k, curve="L", r_cm=a, y=b) for a, b in zip(x.r_cm, x.L_1e12_hbar)] + [dict(panel=k, curve="d", r_cm=a, y=b) for a, b in zip(x.r_cm, x.d_cm)]
TIT = {"paper": "Paper (arXiv:1708.02243, Fig. 2)", "constructed": "This work: event with the paper's kinematics", "key8": "This work: one event of our sample (no. 8)"}
def plot(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(14, 3.9), sharey=True)
    for ax, k in zip(axs, ("paper", "constructed", "key8")):
        x = d[d.panel == k]; L = x[x.curve == "L"].sort_values("r_cm"); dd = x[x.curve == "d"].sort_values("r_cm")
        ax.plot(L.r_cm, L.y, color=fu.SERIES[0], lw=1.8, label="|L|"); ax.set_ylim(0, 1.0); ax.set_xlim(0, 5); ax.set_xlabel("r (cm)"); ax.set_title(TIT[k], fontsize=9)
        bx = ax.twinx(); bx.plot(dd.r_cm, dd.y, color=fu.SERIES[1], lw=1.5, ls="--", label="d"); bx.set_ylim(0, 5); bx.set_ylabel("d (cm)", fontsize=8)
        ax.legend(loc="upper left", fontsize=7); bx.legend(loc="upper right", fontsize=7)
    axs[0].set_ylabel("|L| (10¹² ħ)"); fig.suptitle("m_Q = 1.8 TeV, Λ = 2 keV, B = 2 T", fontsize=9); fig.tight_layout(); return fig
fu.figure("F39_fig2_combined", pd.DataFrame(rows), plot, "Fig. 2: |L| (solid, left axis) and quirk separation d (dashed, right axis) vs the radius r of the pair's centre.",
          [D], "paper event; constructed event; COL2000 event no. 8", os.path.abspath(__file__))
