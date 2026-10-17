#!/usr/bin/env python3
"""F42_fig2_log_scale: Fig. 2 with |L| on a log scale in hbar (2026-10-16), to show what "L = 0" at the even meetings means at the 1e8 hbar level.
Event with the paper's kinematics (v* = 0.556, beta_cm = 0.0975 along x, oscillation along the beam, charges +-2/3, 1800 GeV, 2 keV, B = 2 T), production
integrator (RK4) with 3000 / 10000 / 30000 / 100000 steps per period. L = d* x (p1* - p2*)/2 in the initial CM frame at equal CM time, projected on the
direction of its maximum (signed; plotted as |L|); r = lab transverse radius of the CM at the matching lab time (as scripts/D8_fig2_toy_event.py).
Paper curve: tables/fig2_final/fig2_paper_L.csv (vector extraction; its smallest values are limited by the figure). Curves: tables/fig2_final/fig2_ours_constructed_steps.csv."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22, fig_utils as fu
HB, T, MQ, LAM, VS, BT = f22.HB, f22.T, 1800.0, 2e-6, 0.556, 0.0975
gs = 1 / np.sqrt(1 - VS ** 2); PS, ES = MQ * gs * VS, MQ * gs
def boost_x(E, p, b):
    g = 1 / np.sqrt(1 - b * b); return g * (E + b * p[0]), np.array([g * (p[0] + b * E), p[1], p[2]])
E1, P1 = boost_x(ES, np.array([0, 0, PS]), BT); E2, P2 = boost_x(ES, np.array([0, 0, -PS]), BT); f22._init()
OUT = f"{T}/fig2_final/fig2_ours_constructed_steps.csv"
if not os.path.exists(OUT):
    cur = []
    for n in (3000, 10000, 30000, 100000):
        f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * n
        _, tr = f22.tth.simulate_quirk_hits((*P1, E1), (*P2, E2), mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0, charge1=2 / 3, charge2=-2 / 3, rng=np.random.default_rng(0),
                                            z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=n)
        t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
        e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
        t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
        ts = t1[ok]; I = lambda a: np.column_stack([np.interp(ts, t2, a[:, k]) for k in range(3)])
        dv = y1[ok] - I(y2); kr = (k1[ok] - I(k2)) / 2; Lv = np.cross(dv, kr); L = np.linalg.norm(Lv, axis=1); nh = Lv[np.argmax(L)] / L.max(); Ls = Lv @ nh
        gg = 1 / np.sqrt(1 - b @ b); tl = gg * (ts + ((y1[ok] + I(y2)) / 2) @ b); xc = (x1 + x2) / 2
        r = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1])) * HB; s = r <= 5.0
        cur.append(pd.DataFrame(dict(steps_per_period=n, r_cm=r[s], d_cm=np.linalg.norm(dv, axis=1)[s] * HB, L_signed_hbar=Ls[s])))
        print(n, "done", s.sum(), flush=True)
    pd.concat(cur).to_csv(OUT, index=False)
C = pd.read_csv(OUT); pL = pd.read_csv(f"{T}/fig2_final/fig2_paper_L.csv")
src = pd.concat([C.assign(curve="this work"), pL.assign(curve="paper", L_signed_hbar=pL.L_1e12_hbar * 1e12, steps_per_period=0)[["curve", "steps_per_period", "r_cm", "L_signed_hbar"]]])

def plot(d):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(14.5, 4.8), gridspec_kw=dict(width_ratios=[1.6, 1]))
    cols = {3000: fu.SERIES[0], 10000: fu.SERIES[2], 30000: fu.SERIES[3], 100000: fu.SERIES[1]}
    for k, (ax, (x0, x1)) in enumerate(zip(axs, ((0, 5), (2.15, 2.50)))):
        p = d[d.curve == "paper"]; ax.plot(p.r_cm, np.clip(p.L_signed_hbar.abs(), 1, None), color=fu.INK, lw=1.6, ls=":", label="paper (from its figure)")
        for n, c in cols.items():
            x = d[(d.curve == "this work") & (d.steps_per_period == n)]
            if k == 0 and n not in (3000, 100000): continue
            ax.plot(x.r_cm, np.clip(x.L_signed_hbar.abs(), 1, None), color=c, lw=1.5, label=f"this work, {n:,} steps / oscillation")
        ax.axhline(1e8, color=fu.SERIES[7], lw=1.2, ls="--"); ax.text(x0 + 0.02 * (x1 - x0), 1.4e8, "10⁸ ħ", color=fu.INK, fontsize=8.5)
        ax.axhline(6.4e11, color=fu.MUTED, lw=0.8, ls=":"); ax.text(x0 + 0.02 * (x1 - x0), 8.5e11, "peak 6.4×10¹¹ ħ", color=fu.INK2, fontsize=8)
        ax.set_yscale("log"); ax.set_ylim(1e5, 3e12); ax.set_xlim(x0, x1); ax.set_xlabel("r (cm)"); ax.set_ylabel("|L| (ħ), log scale")
        ax.legend(fontsize=7.5, loc="lower left", frameon=True, framealpha=0.9) if k == 0 else ax.legend(fontsize=7.5, loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False)
    axs[0].set_title("Fig. 2 on a log scale: m = 1.8 TeV, Λ = 2 keV, B = 2 T", fontsize=10, loc="left")
    axs[1].set_title("zoom on meeting 2 (r ≈ 2.33 cm), all time steps", fontsize=10, loc="left")
    fig.text(0.01, -0.02, "At the even meetings the lowest |L| changes with the step size (4×10⁸, 5×10⁷, 5×10⁶ ħ; at 10,000 steps the numerical L even crosses zero): this is the numerical limit, not a physical value.\nAnnihilation would need |L| of order 1 ħ (b ~ 1/m = 1.1×10⁻¹⁷ cm), which this classical simulation cannot resolve.", fontsize=8.5, color=fu.INK2)
    fig.tight_layout(); return fig
fu.figure("F42_fig2_log_scale", src, plot,
          "Fig. 2 with |L| in ħ on a log scale, for the event with the paper's kinematics, at four integration step sizes; dotted: the paper's curve (its smallest values are "
          "limited by the figure). Left: 3000 and 100000 steps per oscillation over 0–5 cm. Right: zoom on the second meeting with all four step sizes. At the odd meetings "
          "|L| = 6.4×10¹¹ ħ for every step size; at the even meetings |L| drops to a value that depends on the step size (the numerical limit), below 10⁹ ħ (at 10,000 steps the numerical L crosses zero). The paper's "
          "|L| at the second meeting is 2×10¹¹ ħ.", [OUT, f"{T}/fig2_final/fig2_paper_L.csv"], "event with the paper's kinematics", os.path.abspath(__file__))
for n in (3000, 10000, 30000, 100000):
    x = C[(C.steps_per_period == n) & (C.r_cm > 2.0) & (C.r_cm < 2.6)]; print(n, "min |L| near meeting 2:", f"{x.L_signed_hbar.abs().min():.2e}", "at r", round(float(x.r_cm.iloc[int(np.argmin(x.L_signed_hbar.abs().values))]), 3))
