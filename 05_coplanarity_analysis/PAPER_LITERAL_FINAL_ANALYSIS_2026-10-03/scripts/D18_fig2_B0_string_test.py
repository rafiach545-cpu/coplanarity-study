#!/usr/bin/env python3
"""Fig. 2 string-torque test at B = 0 (2026-10-12), follow-up of D25.
Constructed event (v* = 0.556 along z, m = 1800 GeV, Lambda = 2 keV), B = 0, so there is no external torque and the CM-frame L must stay constant.
Small initial L: the quirks start at +-delta/2 along y (perpendicular to both the motion and the boost, so both start at the same CM time),
L0 = delta * p* (target 0.5e12 hbar). Runs: v_cm = 0 and v_cm = 0.0975 along x (the Fig. 2 boost), also 0.3 (scaling).
Integrator: quirk_trajectory_optimized_v2.integrate_trajectory_fast_v2 called directly, 3000 steps per CM period, ~4.3 periods.
L in the initial CM frame at equal CM time about the centre of energy (Fig. 2 definition, as D17).
Output: tables/D18_fig2_B0_string_test.txt"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
import quirk_trajectory_optimized_v2 as v2
HB, T, MQ, LAM, VS = f22.HB, f22.T, 1800.0, 2e-6, 0.556
gs = 1 / np.sqrt(1 - VS ** 2); ps = MQ * gs * VS; Es = MQ * gs
period = 2 * (2 * VS * gs * MQ / LAM ** 2)        # full CM oscillation (two half-oscillations of Eq. 4), GeV^-1
delta = 0.5e12 / ps                               # initial y offset (GeV^-1) for L0 = 0.5e12 hbar
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
P(f"p* = {ps:.2f} GeV, CM period {period * HB:.3f} cm/c, delta = {delta * HB * 1e4:.3e} um, L0 target 0.5e12 hbar")
for beta in (0.0, 0.0975, 0.3):
    g = 1 / np.sqrt(1 - beta ** 2)
    def lab(pz_sign):   # CM momentum along +-z, boost along x
        return np.array([g * beta * Es, 0.0, pz_sign * ps]), g * Es
    p1, E1 = lab(+1); p2, E2 = lab(-1)
    x1 = np.array([0.0, +delta / 2, 0.0]); x2 = np.array([0.0, -delta / 2, 0.0])
    tmax = 4.3 * period * g; dt = period / 3000 / 1.0
    res = v2.integrate_trajectory_fast_v2(x1, p1, x2, p2, MQ, 2 / 3, -2 / 3, LAM, 0.0, tmax, dt)
    t, X1, X2, P1, P2 = (np.asarray(res[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    e1 = np.sqrt((P1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((P2 ** 2).sum(1) + MQ * MQ)
    if beta > 0:
        b = np.array([beta, 0, 0])
        t1, y1, F1, k1 = f22.lorentz(t, X1, e1, P1, b); t2, y2, F2, k2 = f22.lorentz(t, X2, e2, P2, b)
    else:
        t1, y1, F1, k1, t2, y2, F2, k2 = t, X1, e1, P1, t, X2, e2, P2
    ok = (t1 >= t2.min()) & (t1 <= t2.max()); ts = t1[ok]; I = lambda a: np.column_stack([np.interp(ts, t2, a[:, k]) for k in range(3)])
    ya, yb, ka, kb = y1[ok], I(y2), k1[ok], I(k2); Ea, Eb = F1[ok], np.interp(ts, t2, F2)
    Xs = (Ea[:, None] * ya + Eb[:, None] * yb) / (Ea + Eb)[:, None]; Lv = np.cross(ya - Xs, ka) + np.cross(yb - Xs, kb)
    d = np.linalg.norm(ya - yb, axis=1) * HB; L0 = Lv[0]; n0 = L0 / np.linalg.norm(L0); Lp = Lv @ n0
    dm = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1; dM = np.where((d[1:-1] > d[:-2]) & (d[1:-1] >= d[2:]))[0] + 1
    perp = np.linalg.norm(Lv - Lp[:, None] * n0, axis=1)
    P(f"\n== v_cm = {beta}: steps {len(t)}, d max {d.max():.3f} cm, closest approaches {len(dm)}, L0 = {np.linalg.norm(L0) / 1e12:.4f} e12 hbar")
    P(f"   L along n0, relative to L0: min {Lp.min() / Lp[0]:.6f}, max {Lp.max() / Lp[0]:.6f}; component perpendicular to n0: max {perp.max() / Lp[0]:.2e} of L0")
    P("   at successive turning points (d max) and closest approaches (d min), L/L0:")
    ev = sorted([(i, "max") for i in dM] + [(i, "min") for i in dm])
    P("   " + " | ".join(f"{k} {Lp[i] / Lp[0]:.6f}" for i, k in ev))
    P(f"   d min values (um): " + " / ".join(f"{d[i] * 1e4:.3g}" for i in dm))
open(f"{T}/D18_fig2_B0_string_test.txt", "w").write("\n".join(out) + "\n")
