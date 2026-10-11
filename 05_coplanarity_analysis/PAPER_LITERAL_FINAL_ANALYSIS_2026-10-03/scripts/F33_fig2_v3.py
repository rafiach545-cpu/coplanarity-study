#!/usr/bin/env python3
"""Fig. 2 (v3): |L| and quirk separation d vs r (transverse radius of the CM), colored 1.8 TeV, Lambda = 2 keV, B = 2 T, initial-CM-frame trajectories compared at equal CM-frame times (as F22; total pair momentum in that frame stays below 1e-3 of p_rel),
integrated with 3000 steps per period (10x the production setting) so that the closest approaches are resolved.
Panels: (a) the paper's event from its vector source figure; (b) COL2000 key 35, the fiducial event with the median |L|max (fixed rule);
(c) COL2000 key 8, the charged triggered colored event (1000- and 2000-event samples) whose predicted d max and spacing of closest approaches are
nearest the paper's event (3.56 cm, 1.155 cm), chosen from kinematics only. Output: FINAL_FIGURES/F33_fig2_v3"""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu, F22_dynamics_v2 as f22
T = f22.T; HB = f22.HB; MQ = 1800.0; f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
M = pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv")
SP = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1' and sample == 'COL2000'")
def curve(key):
    m = M.iloc[key]; z0 = float(SP[SP.key == key].z0_cm.iloc[0])
    _, tr = f22.tth.simulate_quirk_hits((m.px1, m.py1, m.pz1, m.E1), (m.px2, m.py2, m.pz2, m.E2), mass_gev=MQ, Lambda_gev=2e-6, B_tesla=2.0, charge1=float(m.charge1),
                                        charge2=float(m.charge2), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=6.0, steps_per_period=3000)
    t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    E1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); E2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (E1[0] + E2[0])
    t1, y1, _, q1 = f22.lorentz(t, x1, E1, p1, b); t2, y2, _, q2 = f22.lorentz(t, x2, E2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    y2i = np.column_stack([np.interp(t1[ok], t2, y2[:, k]) for k in range(3)]); q2i = np.column_stack([np.interp(t1[ok], t2, q2[:, k]) for k in range(3)])
    dv = y1[ok] - y2i; L = np.linalg.norm(np.cross(dv, (q1[ok] - q2i) / 2), axis=1); d = np.linalg.norm(dv, axis=1) * HB
    g = 1 / np.sqrt(1 - b @ b); tl = g * (t1[ok] + ((y1[ok] + y2i) / 2) @ b); xc = (x1 + x2) / 2     # lab time of the CM point at this CM-frame time (D12)
    r = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1])) * HB                    # lab transverse radius of the CM at that time
    s = r <= 5.0; return pd.DataFrame(dict(event=f"COL2000 key {key}", r_cm=r[s], L_hbar=L[s], d_cm=d[s]))
V = json.load(open(f"{T}/paper_fig23_vector.json"))["fig2"]["curves"]
src = pd.concat([pd.DataFrame(dict(event="paper", r_cm=V["L_1e12_hbar"]["x"], L_hbar=np.array(V["L_1e12_hbar"]["y"]) * 1e12)),
                 pd.DataFrame(dict(event="paper", r_cm=V["d_cm"]["x"], d_cm=V["d_cm"]["y"])), curve(35), curve(8)], ignore_index=True)
TIT = {"paper": "paper, Fig. 2 (representative event)", "COL2000 key 35": "this work: key 35 (median |L|max)", "COL2000 key 8": "this work: key 8 (kinematics nearest the paper's event)"}
def plot(x):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(14, 3.9), sharey=True)
    for ax, ev in zip(axs, ["paper", "COL2000 key 35", "COL2000 key 8"]):
        e = x[x.event == ev]; Lc = e.dropna(subset=["L_hbar"]).sort_values("r_cm"); dc = e.dropna(subset=["d_cm"]).sort_values("r_cm")
        ax.plot(Lc.r_cm, Lc.L_hbar / 1e12, color=fu.SERIES[0], lw=1.8, label="|L|"); ax.set_ylim(0, 1.0); ax.set_xlim(0, 5); ax.set_xlabel("r (cm)"); ax.set_title(TIT[ev], fontsize=8.5)
        bx = ax.twinx(); bx.plot(dc.r_cm, dc.d_cm, color=fu.SERIES[2], lw=1.5, ls="--", label="d"); bx.set_ylim(0, 6); bx.set_ylabel("d (cm)")
        ax.legend(loc="upper left", fontsize=7); bx.legend(loc="upper right", fontsize=7)
    axs[0].set_ylabel("|L| (×10¹² ħ)"); fig.suptitle("m_Q = 1.8 TeV, Λ = 2 keV, B = 2 T", fontsize=10); fig.tight_layout(); return fig
fu.figure("F33_fig2_v3", src, plot, "Fig. 2 on the paper's axes (d axis extended to 6 cm). |L| (solid) and quirk separation d (dashed) in the initial centre-of-mass frame at equal CM-frame times vs the "
          "transverse radius r of the centre of mass, integrated with 3000 steps per period. (a) paper's event from its vector figure; (b) key 35, median |L|max of the fiducial events; "
          "(c) key 8, the event whose d max and spacing of closest approaches are nearest the paper's event (chosen from kinematics only).",
          [f"{T}/paper_fig23_vector.json"], "fixed rules (median |L|max; nearest kinematics)", os.path.abspath(__file__))
for ev, e in src.groupby("event"):
    print(ev, "|L|max %.3g" % e.L_hbar.max(), "d max %.3g" % e.d_cm.max())
