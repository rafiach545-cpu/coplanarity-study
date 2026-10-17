#!/usr/bin/env python3
"""Fig. 2 with the improved pair simulator (scripts/quirk_pair_sim_eq3.py: Eq. 3 + Lorentz force in mm / ns / GeV / T), validated against the
production integrator (quirk_trajectory_optimized_v2 via trajectory_to_hits) on the constructed Fig. 2 event (charges +-2/3, axis z) and on
COL2000 key 8 (charges +-1). 3000 steps per CM oscillation period in both. L, d in the initial CM frame at equal CM time.
Output: tables/D24_fig2_improved_simulator_test.txt, FINAL_FIGURES/F36_fig2_improved_simulator/"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22, quirk_pair_sim_eq3 as qs
HB, T, MQ, LAM = f22.HB, f22.T, 1800.0, 2e-6; HBMM, C = qs.HBARC_GEV_MM, qs.C_MM_NS
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
def cm_curves(t, x1, p1, x2, p2):
    e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
    t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    I = lambda a: np.column_stack([np.interp(t1[ok], t2, a[:, k]) for k in range(3)]); dv = y1[ok] - I(y2)
    L = np.linalg.norm(np.cross(dv, (k1[ok] - I(k2)) / 2), axis=1) / 1e12; d = np.linalg.norm(dv, axis=1) * HB
    g = 1 / np.sqrt(1 - b @ b); tl = g * (t1[ok] + ((y1[ok] + I(y2)) / 2) @ b); xc = (x1 + x2) / 2
    r = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1])) * HB; s = r <= 5.0
    return r[s], L[s], d[s]
def summary(r, L, d):
    mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1
    return f"d max {d.max():.3f} cm, spacing {np.diff(r[mn]).mean():.3f} cm, |L| at closest approaches " + " / ".join(f"{L[i]:.4f}" for i in mn[:4])
VS, BT = 0.556, 0.0975; gs = 1 / np.sqrt(1 - VS ** 2); PS = MQ * gs * VS; ES = MQ * gs; GC = 1 / np.sqrt(1 - BT ** 2)
m8 = pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv").iloc[8]
def onshell(px, py, pz): return np.array([px, py, pz]), np.sqrt(px * px + py * py + pz * pz + MQ * MQ)
k1v, k1e = onshell(m8.px1, m8.py1, m8.pz1); k2v, k2e = onshell(m8.px2, m8.py2, m8.pz2); Pk = k1v + k2v; bk = Pk / (k1e + k2e)
_, ps8 = qs._boost(k1e, k1v, -bk)                                 # quirk 1 in the pair CM frame
EVENTS = {"constructed (+-2/3, axis z)": dict(P=np.array([GC * BT * 2 * ES, 0, 0]), pstar=PS * np.array([0, 0, 1.0]), q=(2 / 3, -2 / 3)),
          "COL2000 key 8 (+-1)": dict(P=Pk, pstar=ps8, q=(float(m8.charge1), float(m8.charge2)))}
curves = {}
for name, ev in EVENTS.items():
    Pv, pst, (q1, q2) = ev["P"], ev["pstar"], ev["q"]; pmag = np.linalg.norm(pst)
    # production integrator
    Es = np.sqrt(MQ * MQ + pmag ** 2); beta = Pv / np.sqrt((2 * Es) ** 2 + Pv @ Pv)
    E1, P1 = qs._boost(Es, pst, beta); E2, P2 = qs._boost(Es, -pst, beta); f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
    _, tr = f22.tth.simulate_quirk_hits((*P1, E1), (*P2, E2), mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0, charge1=q1, charge2=q2, rng=np.random.default_rng(0),
                                        z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=3000)
    a = cm_curves(*(np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "p1", "x2", "p2"))); P(f"{name:28s} production integrator : {summary(*a)}")
    # improved simulator (mm, ns)
    per = qs.oscillation_period_ns(MQ, pmag, 2000.0); bT = np.hypot(beta[0], beta[1]); tmax = 52.0 / (bT * C) * 1.05
    nst = int(tmax / per * 3000) + 2; phi0 = np.arctan2(Pv[1], Pv[0])
    res = qs.simulate_quirk_pair_tracks(0, n_steps=nst, t_max=tmax, b_field=2.0, charge=q1, charge2=q2, quirk_mass=MQ, pair_pt=np.hypot(Pv[0], Pv[1]),
                                        pair_pz=Pv[2], phi0=phi0, string_tension=2000.0, p_star=pmag, rel_dir=pst / pmag)
    t = res["time"] * C / HBMM
    b_ = cm_curves(t, res["xyz_q"] / HBMM, res["pxyz_q"], res["xyz_aq"] / HBMM, res["pxyz_aq"]); P(f"{name:28s} improved simulator    : {summary(*b_)}")
    curves[name] = (a, b_)
P("paper: d max 3.556 cm, spacing 1.153 cm, |L| at closest approaches 0.645 / 0.194 / 0.514 / 0.287")
open(f"{T}/D24_fig2_improved_simulator_test.txt", "w").write("\n".join(out) + "\n")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, fig_utils as fu
p = pd.read_csv(f"{T}/fig2_r_d_L_paper.csv"); pl, pd_ = p.dropna(subset=["L_1e12_hbar"]).sort_values("r_cm"), p.dropna(subset=["d_cm"]).sort_values("r_cm")
ra, La, da = curves["constructed (+-2/3, axis z)"][1]; o = np.argsort(ra)
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(9, 5.2), sharex=True); fig.patch.set_facecolor("white")
for j, (t_, rl, L, rd, d) in enumerate((("PAPER (Fig. 2)\n", pl.r_cm, pl.L_1e12_hbar, pd_.r_cm, pd_.d_cm),
                                         ("IMPROVED SIMULATOR (Eq. 3 + Lorentz)\npaper's kinematics, charges ±2/3", ra[o], La[o], ra[o], da[o]))):
    ax[0, j].plot(rl, L, color=fu.SERIES[0], lw=1.8); ax[1, j].plot(rd, d, color=fu.SERIES[1], lw=1.6); ax[0, j].set_title(t_, fontsize=8.5, loc="left", weight="bold")
    ax[0, j].set_ylim(0, 1); ax[1, j].set_ylim(0, 4.2); ax[1, j].set_xlim(0, 5); ax[1, j].set_xlabel("r (cm)")
    for a_ in ax[:, j]: a_.grid(axis="y", color="#d5dbde", lw=0.4)
ax[0, 0].set_ylabel("|L| (10¹² ħ)"); ax[1, 0].set_ylabel("d (cm)"); fig.tight_layout()
os.makedirs(f"{HERE}/../FINAL_FIGURES/F36_fig2_improved_simulator", exist_ok=True); fig.savefig(f"{HERE}/../FINAL_FIGURES/F36_fig2_improved_simulator/F36_fig2_improved_simulator.png", dpi=150)
