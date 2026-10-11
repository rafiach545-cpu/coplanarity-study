#!/usr/bin/env python3
"""Baseline integrator (03_trajectory_sim/quirk_trajectory.integrate_trajectory) vs the fast one used everywhere in the analysis
(quirk_trajectory_optimized_v2.integrate_trajectory_fast_v2): identical initial conditions, parameters and time step.
Event: the constructed Fig. 2 event (v* = 0.556, beta = 0.0975 along x, axis z, charges +-2/3), 1800 GeV, 2 keV, B = 2 T, 3000 steps per period, r <= 6 cm.
Compares t, x1, p1, x2, p2 element by element, the CM-frame L(t) and d(t), and the runtime (3 runs each)."""
import os, sys, time, importlib, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
sys.path[:0] = ["/home/rafia/coplanarity_study/03_trajectory_sim", "/home/rafia/coplanarity_study/04_detector_sim"]
import quirk_trajectory as base, quirk_trajectory_optimized_v2 as v2, trajectory_to_hits as tth
HB, MQ, VS, BETA = f22.HB, 1800.0, 0.556, 0.0975
tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
def bx(E, p, b): g = 1 / np.sqrt(1 - b * b); return g * (E + b * p[0]), np.array([g * (p[0] + b * E), p[1], p[2]])
gs = 1 / np.sqrt(1 - VS ** 2); n = np.array([0, 0, 1.0]); E1, P1 = bx(MQ * gs, MQ * gs * VS * n, BETA); E2, P2 = bx(MQ * gs, -MQ * gs * VS * n, BETA)
def run(fn):
    tth.integrate_trajectory = fn; t0 = time.perf_counter()
    _, tr = tth.simulate_quirk_hits((*P1, E1), (*P2, E2), mass_gev=MQ, Lambda_gev=2e-6, B_tesla=2.0, charge1=2 / 3, charge2=-2 / 3, rng=np.random.default_rng(0),
                                    z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=3000)
    return tr, time.perf_counter() - t0
def LCM(tr):
    t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
    t1, y1, _, q1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, q2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    y2i = np.column_stack([np.interp(t1[ok], t2, y2[:, k]) for k in range(3)]); q2i = np.column_stack([np.interp(t1[ok], t2, q2[:, k]) for k in range(3)])
    dv = y1[ok] - y2i; return np.linalg.norm(np.cross(dv, (q1[ok] - q2i) / 2), axis=1), np.linalg.norm(dv, axis=1) * HB
times = {"baseline": [], "v2": []}; out = {}
for rep in range(3):
    for name, fn in (("baseline", base.integrate_trajectory), ("v2", v2.integrate_trajectory_fast_v2)):
        tr, dt = run(fn); times[name].append(dt); out[name] = tr
a, b = out["baseline"], out["v2"]
print("steps:", len(a["t_gev_inv"]), "(baseline)", len(b["t_gev_inv"]), "(v2)")
for k in ("t_gev_inv", "x1", "p1", "x2", "p2"):
    A, B = np.asarray(a[k]), np.asarray(b[k]); same = A.shape == B.shape and np.array_equal(A, B)
    if A.shape == B.shape:
        ad = np.abs(A - B).max(); rd = (np.abs(A - B) / np.maximum(np.abs(A), 1e-300)).max(); nz = int((A != B).sum())
    else: ad = rd = nz = float("nan")
    print(f"  {k:9s}: bit-for-bit identical = {same}; elements differing = {nz}; max |diff| = {ad:.3e}; max rel diff = {rd:.3e}")
La, da = LCM(a); Lb, db = LCM(b)
print(f"  L(t) CM frame: identical = {np.array_equal(La, Lb)}; max |diff| = {np.abs(La - Lb).max():.3e} hbar (|L|max {La.max():.3e}); d(t) identical = {np.array_equal(da, db)}")
for k in times: print(f"  runtime {k}: " + ", ".join(f"{x:.2f} s" for x in times[k]) + f"  (median {np.median(times[k]):.2f} s)")
print(f"  speed-up: {np.median(times['baseline']) / np.median(times['v2']):.1f}x")
