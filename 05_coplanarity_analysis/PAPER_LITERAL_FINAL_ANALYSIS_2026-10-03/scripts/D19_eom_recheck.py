#!/usr/bin/env python3
"""Recheck of the equations used in the simulation against the paper (2026-10-12).
Integrator: quirk_trajectory_optimized_v2 (RK4; right-hand side _rhs), as used for Fig. 2 and Table I.
1. Paper Eq. 3 written literally, -Lambda^2 ( sqrt(1-vperp^2)/vpar * vpar_vec + vpar/sqrt(1-vperp^2) * vperp_vec ), with vpar = v.s (s = unit vector
   from the partner to the quirk), compared with _rhs at random states (B = 0).
2. Lorentz force q v x B (B along +z) and the unit constants (e = sqrt(4 pi alpha), 1 T in GeV^2) from first principles.
3. Single charged particle (Lambda = 0, partner neutral): gyroradius vs p_T / (0.29979 B) m.
4. Paper Eq. 4: head-on pair, B = 0, v = 0.556: half separation d(t)/2 vs d_cm(t) = m/L^2 [gamma - sqrt(1 + (L^2 t/m - v gamma)^2)] over the first period.
5. Same pair boosted (v_cm = 0.3 transverse): CM-frame d*(t*)/2 vs Eq. 4 (Eq. 3 applied in the lab frame reproduces the CM motion).
6. Energy: E1 + E2 + Lambda^2 d constant for the head-on pair (B = 0).
7. Step size: Fig. 2 constructed event, |L| at closest approaches with 3000 vs 6000 steps per period.
Output: tables/D19_eom_recheck.txt"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
import quirk_trajectory_optimized_v2 as v2
HB, T, MQ, LAM = f22.HB, f22.T, 1800.0, 2e-6
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
rng = np.random.default_rng(1)

# 1. Eq. 3 literal vs _rhs
worst = 0.0
for _ in range(2000):
    x1, x2 = rng.normal(size=3) * 1e13, rng.normal(size=3) * 1e13
    v1, v2_ = [rng.normal(size=3) for _ in range(2)]; v1 *= rng.uniform(0, 0.95) / np.linalg.norm(v1); v2_ *= rng.uniform(0, 0.95) / np.linalg.norm(v2_)
    p1, p2 = MQ * v1 / np.sqrt(1 - v1 @ v1), MQ * v2_ / np.sqrt(1 - v2_ @ v2_)
    r = v2._rhs(*x1, *p1, *x2, *p2, MQ, 0.2, -0.2, LAM ** 2, 0.0)
    for (x, xo, v, F) in ((x1, x2, v1, np.array(r[3:6])), (x2, x1, v2_, np.array(r[9:12]))):
        s = (x - xo) / np.linalg.norm(x - xo); vpar = v @ s; vpar_vec = vpar * s; vperp = v - vpar_vec; vp2 = vperp @ vperp
        Fp = -LAM ** 2 * (np.sqrt(1 - vp2) / vpar * vpar_vec + vpar / np.sqrt(1 - vp2) * vperp)
        worst = max(worst, np.linalg.norm(F - Fp) / LAM ** 2)
P(f"1. Eq. 3 (paper, literal) vs _rhs, 2000 random states: max |F_code - F_paper| / Lambda^2 = {worst:.1e}")
x1, x2 = np.zeros(3), np.array([0, 0, -1e13]); p = np.array([0, 0, 100.0])
r = v2._rhs(*x1, *p, *x2, *(-p), MQ, 0, 0, LAM ** 2, 0.0)
P(f"   direction: quirk 1 above quirk 2 (z), string force on quirk 1 z-component {r[5] / LAM ** 2:+.6f} Lambda^2 (towards the partner: negative)")

# 2. Lorentz force and constants
r = v2._rhs(0, 0, 0, 100.0, 0, 0, 1e13, 0, 0, 0, 0, 0, MQ, 0.3, 0.0, 0.0, 1.0)
P(f"2. Lorentz: q = 0.3, v along +x, B = +z: F = ({r[3]:+.3e}, {r[4]:+.3e}, {r[5]:+.3e}); q v x B = (0, -q v B, 0) -> expected y < 0")
alpha = 1 / 137.035999; e_nat = np.sqrt(4 * np.pi * alpha)
eB_1T = 0.299792458 * 1.973269804e-16          # e * (1 T) * c in GeV/m, times hbar c in GeV m  -> GeV^2
P(f"   e = sqrt(4 pi alpha) = {e_nat:.6f} (code 0.30282212); 1 T = {eB_1T / e_nat:.5e} GeV^2 (code 1.9535e-16)")

# 3. gyroradius
pT = 50.0; tmax = 2 * np.pi * (np.hypot(pT, MQ) / (e_nat * 2.0 * 1.9535e-16)) * 1.0
res = v2.integrate_trajectory_fast_v2(np.zeros(3), np.array([pT, 0, 0]), np.array([0, 0, 1e20]), np.zeros(3), MQ, 1.0, 0.0, 0.0, 2.0, tmax / 4, tmax / 4 / 20000)
xy = res["x1"][:, :2] * HB / 100; c = np.array([0, -pT / (0.299792458 * 2.0)])
P(f"3. gyroradius, p_T = 50 GeV, B = 2 T, q = +1: simulated distance from expected centre {np.abs(np.linalg.norm(xy - c, axis=1) - pT / (0.299792458 * 2.0)).max():.2e} m"
  f" (expected R = {pT / (0.299792458 * 2.0):.4f} m, centre at -y for q > 0)")

# 4-6. Eq. 4 and energy
VS = 0.556; gs = 1 / np.sqrt(1 - VS ** 2); ps = MQ * gs * VS; Tper = 2 * VS * gs * MQ / LAM ** 2
def eq4(t):
    t = np.mod(t, Tper); return MQ / LAM ** 2 * (gs - np.sqrt(1 + (LAM ** 2 * t / MQ - VS * gs) ** 2))
for bcm in (0.0, 0.3):
    g = 1 / np.sqrt(1 - bcm ** 2); E = MQ * gs
    p1 = np.array([g * bcm * E, 0, ps]); p2 = np.array([g * bcm * E, 0, -ps])
    dt = Tper / 3000; res = v2.integrate_trajectory_fast_v2(np.zeros(3), p1, np.zeros(3), p2, MQ, 0.0, 0.0, LAM, 0.0, 2.2 * Tper * g, dt)
    t, X1, X2, Q1, Q2 = (np.asarray(res[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    e1 = np.sqrt((Q1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((Q2 ** 2).sum(1) + MQ * MQ)
    if bcm > 0:
        b = np.array([bcm, 0, 0]); t1, y1, _, _ = f22.lorentz(t, X1, e1, Q1, b); t2, y2, _, _ = f22.lorentz(t, X2, e2, Q2, b)
        ok = t1 <= t2.max(); ts = t1[ok]; dd = np.linalg.norm(y1[ok] - np.column_stack([np.interp(ts, t2, y2[:, k]) for k in range(3)]), axis=1)
    else:
        ts = t; dd = np.linalg.norm(X1 - X2, axis=1)
    sel = ts <= 2 * Tper
    dev = np.abs(dd[sel] / 2 - eq4(ts[sel])).max() / (MQ / LAM ** 2 * (gs - 1))
    P(f"{'4' if bcm == 0 else '5'}. Eq. 4, v = 0.556, B = 0, v_cm = {bcm}: max |d/2 - d_cm(t)| over two periods = {dev:.1e} of the amplitude"
      f" (amplitude {MQ / LAM ** 2 * (gs - 1) * HB:.4f} cm)")
    if bcm == 0:
        Et = e1 + e2 + LAM ** 2 * dd
        P(f"6. energy E1 + E2 + Lambda^2 d (B = 0, head-on): max relative change {np.abs(Et - Et[0]).max() / Et[0]:.1e}")

# 7. step size, Fig. 2 constructed event
def boost_x(E, p, b):
    g = 1 / np.sqrt(1 - b * b); return g * (E + b * p[0]), np.array([g * (p[0] + b * E), p[1], p[2]])
E1, P1 = boost_x(MQ * gs, np.array([0, 0, ps]), 0.0975); E2, P2 = boost_x(MQ * gs, np.array([0, 0, -ps]), 0.0975); f22._init()
for n in (3000, 6000):
    f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * n
    _, tr = f22.tth.simulate_quirk_hits((*P1, E1), (*P2, E2), mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0, charge1=2 / 3, charge2=-2 / 3, rng=np.random.default_rng(0),
                                        z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=n)
    t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
    t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    I = lambda a: np.column_stack([np.interp(t1[ok], t2, a[:, k]) for k in range(3)])
    dv = y1[ok] - I(y2); L = np.linalg.norm(np.cross(dv, (k1[ok] - I(k2)) / 2), axis=1) / 1e12; d = np.linalg.norm(dv, axis=1)
    mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1
    P(f"7. Fig. 2 constructed event, {n} steps/period: |L| at closest approaches 1-4 = " + " / ".join(f"{L[i]:.4f}" for i in mn[:4]))
open(f"{T}/D19_eom_recheck.txt", "w").write("\n".join(out) + "\n")
