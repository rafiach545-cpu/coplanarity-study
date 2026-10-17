#!/usr/bin/env python3
"""Fig. 2 (2026-10-12): how small is |L| at the 'L = 0' closest approaches, in units of hbar, and what is the classical distance of
closest approach there (annihilation needs L of order hbar and a distance of order 1/m_Q). Constructed event (D8: v* = 0.556, v_cm = 0.0975 x,
charges +-2/3, 2 keV, 1800 GeV, B = 2 T), production integrator (v2 RK4) with 3000 / 10000 / 30000 / 100000 steps per period.
At each closest approach: time of minimum d from a parabola through d^2 at the three nearest stored points; signed L (projection on the L axis)
interpolated linearly to that time; classical impact parameter b = |L| / p_rel* (p_rel* = |p1* - p2*|/2) compared with 1/m_Q.
Output: tables/D22_fig2_L_residual_annihilation.txt"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB, T, MQ, LAM, VS, BT = f22.HB, f22.T, 1800.0, 2e-6, 0.556, 0.0975
gs = 1 / np.sqrt(1 - VS ** 2); PS = MQ * gs * VS; ES = MQ * gs
def boost_x(E, p, b):
    g = 1 / np.sqrt(1 - b * b); return g * (E + b * p[0]), np.array([g * (p[0] + b * E), p[1], p[2]])
E1, P1 = boost_x(ES, np.array([0, 0, PS]), BT); E2, P2 = boost_x(ES, np.array([0, 0, -PS]), BT); f22._init()
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
P(f"1/m_Q = {1 / MQ:.3e} GeV^-1 = {HB / MQ:.2e} cm; p* = {PS:.1f} GeV, so b > 1/m_Q requires |L| > {PS / MQ:.2f} hbar")
for n in (3000, 10000, 30000, 100000):
    f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * n
    _, tr = f22.tth.simulate_quirk_hits((*P1, E1), (*P2, E2), mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0, charge1=2 / 3, charge2=-2 / 3, rng=np.random.default_rng(0),
                                        z0_cm=0.0, max_layer_r_cm=3.0, steps_per_period=n)
    t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
    t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    ts = t1[ok]; I = lambda a: np.column_stack([np.interp(ts, t2, a[:, k]) for k in range(3)])
    dv = y1[ok] - I(y2); kr = (k1[ok] - I(k2)) / 2; Lv = np.cross(dv, kr); L = np.linalg.norm(Lv, axis=1)
    nh = Lv[np.argmax(L)] / L.max(); Ls = Lv @ nh; d2 = (dv ** 2).sum(1)
    mn = np.where((d2[1:-1] < d2[:-2]) & (d2[1:-1] <= d2[2:]))[0] + 1; row = []
    for i in mn[:4]:
        x0, xa, xb = ts[i - 1:i + 2]; y0, ya, yb = d2[i - 1:i + 2]
        A = ((yb - ya) / (xb - xa) - (ya - y0) / (xa - x0)) / (xb - x0); tm = (x0 + xa) / 2 - (ya - y0) / (xa - x0) / (2 * A) if A > 0 else xa
        Lm = np.interp(tm, ts, Ls); pr = np.linalg.norm(kr[i]); row.append(f"{Lm:+.3e} hbar (b = {abs(Lm) / pr * HB:.1e} cm, b*m_Q = {abs(Lm) / pr * MQ:.1e})")
    P(f"{n:6d} steps/period, signed L at closest approaches 1-4: " + " | ".join(row))
open(f"{T}/D22_fig2_L_residual_annihilation.txt", "w").write("\n".join(out) + "\n")
