#!/usr/bin/env python3
"""Physics test suite for the trajectory code (2026-10-12); run after any change to 03_trajectory_sim / 04_detector_sim:
    python3 scripts/T0_physics_tests.py        (about one minute; exit code 1 if a test fails)
Tests (the integrator used in production: quirk_trajectory_optimized_v2 through trajectory_to_hits):
  1 Eq. 3 of the paper, written literally, equals the integrator's string force (random states)
  2 Lorentz force direction q v x B (B along +z) and the units: gyroradius of a single charge vs p_T / (0.29979 B)
  3 Energy E1 + E2 + Lambda^2 d constant at B = 0 (head-on pair; median over steps)
  4 Eq. 4 / Eq. 1: maximum separation = 2 (gamma - 1) m / Lambda^2 at B = 0
  5 Torque balance with B = 2 T (Fig. 2 kinematics): |L| at the 2nd closest approach < 1% of the 1st (CM frame)
Tolerances are set well above the values found on 2026-10-12 (D27, D19 script) and well below a physics error."""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
import quirk_trajectory_optimized_v2 as v2
HB, MQ, LAM = f22.HB, 1800.0, 2e-6; E_NAT, T2G = 0.30282212, 1.9535e-16
res = []
def test(name, value, limit, unit=""):
    ok = value < limit; res.append(ok); print(f"{'PASS' if ok else 'FAIL'}  {name}: {value:.3g}{unit} (limit {limit:g}{unit})", flush=True)
rng = np.random.default_rng(1); worst = 0.0
for _ in range(500):
    x1, x2 = rng.normal(size=3) * 1e13, rng.normal(size=3) * 1e13; vs = []
    for _ in range(2):
        v = rng.normal(size=3); vs.append(v * rng.uniform(0, 0.95) / np.linalg.norm(v))
    p1, p2 = (MQ * v / np.sqrt(1 - v @ v) for v in vs); r = v2._rhs(*x1, *p1, *x2, *p2, MQ, 0.0, 0.0, LAM ** 2, 0.0)
    for x, xo, v, F in ((x1, x2, vs[0], np.array(r[3:6])), (x2, x1, vs[1], np.array(r[9:12]))):
        s = (x - xo) / np.linalg.norm(x - xo); vp = v @ s; vpv = vp * s; vq = v - vpv; st = np.sqrt(1 - vq @ vq)
        worst = max(worst, np.linalg.norm(F + LAM ** 2 * (st / vp * vpv + vp / st * vq)) / LAM ** 2)
test("1 Eq. 3 literal vs integrator, max |dF|/Lambda^2", worst, 1e-12)
r = v2._rhs(0, 0, 0, 100.0, 0, 0, 1e13, 0, 0, 0, 0, 0, MQ, 0.3, 0.0, 0.0, 1.0)
test("2a Lorentz direction (F_y should be < 0 for q > 0, v = +x, B = +z): F_y", r[4], 0.0)
pT = 50.0; tq = 2 * np.pi * np.hypot(pT, MQ) / (E_NAT * 2.0 * T2G) / 4
o = v2.integrate_trajectory_fast_v2(np.zeros(3), np.array([pT, 0, 0]), np.array([0, 0, 1e20]), np.zeros(3), MQ, 1.0, 0.0, 0.0, 2.0, tq, tq / 20000)
R = pT / (0.299792458 * 2.0); xy = o["x1"][:, :2] * HB / 100
test("2b gyroradius, relative deviation from p_T/(0.29979 B)", np.abs(np.linalg.norm(xy - [0, -R], axis=1) - R).max() / R, 1e-4)
VS = 0.556; gs = 1 / np.sqrt(1 - VS ** 2); PS = MQ * gs * VS; TP = 2 * VS * gs * MQ / LAM ** 2
o = v2.integrate_trajectory_fast_v2(np.zeros(3), np.array([0, 0, PS]), np.zeros(3), np.array([0, 0, -PS]), MQ, 0.0, 0.0, LAM, 0.0, 2.2 * TP, TP / 3000)
P1, P2, X1, X2 = (np.asarray(o[k]) for k in ("p1", "p2", "x1", "x2")); d = np.linalg.norm(X1 - X2, axis=1)
E = np.sqrt((P1 ** 2).sum(1) + MQ * MQ) + np.sqrt((P2 ** 2).sum(1) + MQ * MQ) + LAM ** 2 * d
test("3 energy conservation at B = 0, median relative change", np.median(np.abs(E - E[0]) / E[0]), 1e-9)
test("4 d max vs 2 (gamma-1) m / Lambda^2, relative", abs(d.max() / (2 * (gs - 1) * MQ / LAM ** 2) - 1), 1e-4)
g = 1 / np.sqrt(1 - 0.0975 ** 2); f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
Q1, Q2 = (np.array([g * 0.0975 * MQ * gs, 0, s_ * PS]) for s_ in (1, -1))
_, tr = f22.tth.simulate_quirk_hits((*Q1, np.sqrt(Q1 @ Q1 + MQ * MQ)), (*Q2, np.sqrt(Q2 @ Q2 + MQ * MQ)), mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0, charge1=2 / 3,
                                    charge2=-2 / 3, rng=np.random.default_rng(0), z0_cm=0.0, max_layer_r_cm=3.0, steps_per_period=3000)
t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
I = lambda a: np.column_stack([np.interp(t1[ok], t2, a[:, k]) for k in range(3)]); dv = y1[ok] - I(y2)
L = np.linalg.norm(np.cross(dv, (k1[ok] - I(k2)) / 2), axis=1); dd = np.linalg.norm(dv, axis=1); mn = np.where((dd[1:-1] < dd[:-2]) & (dd[1:-1] <= dd[2:]))[0] + 1
test("5 torque balance: |L(2nd approach)| / |L(1st)|", L[mn[1]] / L[mn[0]], 1e-2)
print("RESULT:", "all tests passed" if all(res) else f"{res.count(False)} test(s) failed"); sys.exit(0 if all(res) else 1)
