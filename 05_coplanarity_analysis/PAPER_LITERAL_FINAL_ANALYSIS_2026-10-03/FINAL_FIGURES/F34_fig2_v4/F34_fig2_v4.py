#!/usr/bin/env python3
"""Fig. 2 (v4): paper's event | constructed event with the paper's kinematics | simulated event (COL2000 key 8).
Constructed event (scripts/D8_fig2_toy_event.py): v* = 0.556, CM transverse speed 0.0975 (read from the paper's Fig. 2: d max 3.6 cm, spacing 1.16 cm),
quirk charges +-2/3, oscillation axis along the beam (along the boost gives the same curve), 1800 GeV, 2 keV, B = 2 T, 3000 steps per period.
Simulated event: COL2000 key 8 (final-state R-hadrons, charges +-1), from F33. |L| from initial-CM-frame trajectories at equal CM-frame times (centre-of-energy formula agrees to <= 5%); r = lab transverse radius of the CM at the matching lab time."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; F = f"{HERE}/../FINAL_FIGURES"
toy = pd.read_csv(f"{T}/D8_fig2_toy_curves.csv"); toy = toy[(toy["axis"] == "z (beam)") & np.isclose(toy.charge, 2 / 3)]
f33 = pd.read_csv(f"{F}/F33_fig2_v3/F33_fig2_v3_source.csv")
src = pd.concat([f33[f33.event == "paper"], toy.rename(columns={"L_cm_hbar": "L_hbar"}).assign(event="constructed")[["event", "r_cm", "L_hbar", "d_cm"]],
                 f33[f33.event == "COL2000 key 8"]], ignore_index=True)
TIT = {"paper": "PAPER\nFig. 2 of arXiv:1708.02243", "constructed": "CONSTRUCTED (not a reproduction)\nkinematics read from the paper: v* = 0.556, β_cm = 0.0975, charges ±2/3",
       "COL2000 key 8": "SIMULATED\nCOL2000 key 8: kinematics nearest the paper's, charges ±1"}
def plot(x):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.3), sharey=True)
    for ax, ev in zip(axs, ["paper", "constructed", "COL2000 key 8"]):
        e = x[x.event == ev]; Lc = e.dropna(subset=["L_hbar"]).sort_values("r_cm"); dc = e.dropna(subset=["d_cm"]).sort_values("r_cm")
        ax.plot(Lc.r_cm, Lc.L_hbar / 1e12, color=fu.SERIES[0], lw=1.8, label="|L|"); ax.set_ylim(0, 1.0); ax.set_xlim(0, 5); ax.set_xlabel("r (cm)"); ax.set_title(TIT[ev], fontsize=8.5)
        bx = ax.twinx(); bx.plot(dc.r_cm, dc.d_cm, color=fu.SERIES[2], lw=1.5, ls="--", label="d"); bx.set_ylim(0, 5); bx.set_ylabel("d (cm)")
        ax.legend(loc="upper left", fontsize=7); bx.legend(loc="upper right", fontsize=7)
    axs[0].set_ylabel("|L| (×10¹² ħ)"); fig.suptitle("m_Q = 1.8 TeV, Λ = 2 keV, B = 2 T", fontsize=10); fig.tight_layout(); return fig
fu.figure("F34_fig2_v4", src, plot, "Fig. 2 on the paper's axes (r 0–5 cm, |L| 0–1×10¹² ħ, d 0–5 cm, all linear). |L| and d from initial-CM-frame trajectories at equal CM-frame times; r = lab transverse radius of the CM; 2997 steps per period (curves agree with 5994 to 0.2% of |L|max). Middle: an event constructed with the kinematics read from the paper's "
          "figure (v* = 0.556, β_cm = 0.0975, charges ±2/3; charge and oscillation direction cannot be separated): the separation d and the first |L| peak (0.64 vs 0.65×10¹² ħ) "
          "match the paper; the later peaks do not (0 / 0.64 / 0 vs 0.19 / 0.52 / 0.29×10¹² ħ), and |L| reaches zero at closest approach instead of at large d. "
          "Right: simulated event with the nearest kinematics (d max 4.19 cm, spacing 1.05 cm): |L| at closest approaches 0.86 / ~0 / 0.86 / ~0 ×10¹² ħ, the same pattern.",
          [f"{T}/D8_fig2_toy_curves.csv", f"{F}/F33_fig2_v3/F33_fig2_v3_source.csv"], "constructed + nearest-kinematics event", os.path.abspath(__file__))
