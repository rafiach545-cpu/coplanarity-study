#!/usr/bin/env python3
"""Fig. 2 cross-check with PreFASERQuirkSim (github.com/eliwelch17/PreFASERQuirkSim; C++ port of the Mathematica code of arXiv:2404.13814),
2026-10-12. The package's own CalculateForces / CalculateCt and its main-loop step (quirk_run.cxx l.424-523: string direction with the CM-frame
simultaneity correction, separate lab times t1/t2 per quirk, p += F dt, trapezoidal r) were run by a small driver (scratchpad, not in the repo)
with: uniform B = 2 T along z instead of the LHC field maps, no material, production at the origin, stop at CM radius 5.2 cm; step t1q/divStep
with divStep 10000 (package default) and 40000. Events: constructed Fig. 2 kinematics with charges +-1 (the package takes integer charges) and
COL2000 key 8 (+-1). Trajectory files: argv[1] directory with traj_<event>_<divStep>.txt (um, ns, GeV).
L, d in the initial CM frame at equal CM time (as Fig. 2 / F22), compared with the production integrator.
Output: tables/D25_fig2_prefaser_check.txt"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB, T, MQ = f22.HB, f22.T, 1800.0; CCM = 29.9792458
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
def analyse(t1, x1, p1, t2, x2, p2):
    e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
    s1, y1, _, k1 = f22.lorentz(t1, x1, e1, p1, b); s2, y2, _, k2 = f22.lorentz(t2, x2, e2, p2, b); ok = (s1 >= s2.min()) & (s1 <= s2.max())
    I = lambda a: np.column_stack([np.interp(s1[ok], s2, a[:, k]) for k in range(3)]); dv = y1[ok] - I(y2)
    L = np.linalg.norm(np.cross(dv, (k1[ok] - I(k2)) / 2), axis=1) / 1e12; d = np.linalg.norm(dv, axis=1) * HB
    g = 1 / np.sqrt(1 - b @ b); tl = g * (s1[ok] + ((y1[ok] + I(y2)) / 2) @ b)
    xc = (x1 + np.column_stack([np.interp(t1, t2, x2[:, k]) for k in range(3)])) / 2
    r = np.hypot(np.interp(tl, t1, xc[:, 0]), np.interp(tl, t1, xc[:, 1])) * HB; s = r <= 5.0; r, L, d = r[s], L[s], d[s]
    mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1
    return f"d max {d.max():.3f} cm, spacing {np.diff(r[mn]).mean():.3f} cm, |L| at closest approaches " + " / ".join(f"{L[i]:.4f}" for i in mn[:4])
D = sys.argv[1]
MQ_, VS, BT = 1800.0, 0.556, 0.0975; gs = 1 / np.sqrt(1 - VS ** 2); PS = MQ * gs * VS; ES = MQ * gs; GC = 1 / np.sqrt(1 - BT ** 2)
m8 = pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv").iloc[8]
EV = {"constructed": (np.array([GC * BT * ES, 0, PS]), np.array([GC * BT * ES, 0, -PS]), (1.0, -1.0)),
      "key8": (np.array([m8.px1, m8.py1, m8.pz1]), np.array([m8.px2, m8.py2, m8.pz2]), (float(m8.charge1), float(m8.charge2)))}
f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
for name, (a, b, (q1, q2)) in EV.items():
    _, tr = f22.tth.simulate_quirk_hits((*a, np.sqrt(a @ a + MQ * MQ)), (*b, np.sqrt(b @ b + MQ * MQ)), mass_gev=MQ, Lambda_gev=2e-6, B_tesla=2.0, charge1=q1, charge2=q2,
                                        rng=np.random.default_rng(0), z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=3000)
    t, x1, p1, x2, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "p1", "x2", "p2"))
    P(f"{name:12s} production integrator (RK4, 3000/period)  : {analyse(t, x1, p1, t, x2, p2)}")
    for div in (10000, 40000):
        A = np.loadtxt(f"{D}/traj_{name}_{div}.txt")
        tt1, tt2 = A[:, 0] * CCM / HB, A[:, 7] * CCM / HB                  # ns -> GeV^-1
        X1, X2 = A[:, 1:4] * 1e-4 / HB, A[:, 8:11] * 1e-4 / HB              # um -> GeV^-1
        P(f"{name:12s} PreFASERQuirkSim step, divStep {div:6d}     : {analyse(tt1, X1, A[:, 4:7], tt2, X2, A[:, 11:14])}")
P("paper: d max 3.556 cm, spacing 1.153 cm, |L| at closest approaches 0.645 / 0.194 / 0.514 / 0.287 (charges not stated)")
open(f"{T}/D25_fig2_prefaser_check.txt", "w").write("\n".join(out) + "\n")
