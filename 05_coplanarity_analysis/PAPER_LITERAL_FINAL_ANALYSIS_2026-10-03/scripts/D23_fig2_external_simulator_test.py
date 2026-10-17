#!/usr/bin/env python3
"""Fig. 2 test with the external pair simulator supplied by the user on 2026-10-12 (simulate_quirk_pair_tracks: mm, ns, GeV, T; RK4;
constant string force T s with T = Lambda^2 / hbar c; Lorentz term 0.3 q beta x B; quirks start 2 mm apart along the transverse direction
perpendicular to the pair momentum, with relative momentum along the same direction).
Its right-hand side is reproduced here with three switches so that each difference to the paper can be tested on its own:
  c_fix   : Lorentz term 0.3 q beta x B multiplied by c = 0.29979 m/ns (the supplied form lacks it: force 3.34x too large)
  sep0_mm : initial separation (supplied: 2 mm; paper: production at one point)
  axis    : direction of the relative momentum: 'perp' (supplied: transverse, perpendicular to the pair momentum = parallel to E_cm) or 'z' (beam)
Event: Fig. 2 kinematics (m = 1800 GeV, Lambda = 2 keV, B = 2 T, internal speed v* = 0.556, CM transverse speed 0.0975, charges +-1).
L and d in the initial CM frame at equal CM time (as Fig. 2 / F22). Output: tables/D23_fig2_external_simulator_test.txt"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB_MM, C = 1.973269804e-13, 299.792458; T_ = f22.T
MQ, LAM_EV, VS, BT, BF = 1800.0, 2000.0, 0.556, 0.0975, 2.0
gs = 1 / np.sqrt(1 - VS ** 2); PS = MQ * gs * VS; ES = MQ * gs; GC = 1 / np.sqrt(1 - BT ** 2)
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)

def simulate(c_fix, sep0_mm, axis, tmax_ns=1.85, n_steps=40000, charge=1.0):
    Tgm = (LAM_EV * 1e-9) ** 2 / HB_MM; Bv = np.array([0, 0, BF]); kL = 0.3 * (0.299792458 if c_fix else 1.0)
    pc = np.array([GC * BT * 2 * ES, 0, 0])                       # pair momentum along x (CM transverse speed 0.0975)
    n = np.array([0, 1.0, 0]) if axis == "perp" else np.array([0, 0, 1.0])
    p1, p2 = pc / 2 + PS * n, pc / 2 - PS * n                       # internal momentum p* along n (n perpendicular to the boost: unchanged by it)
    r1, r2 = 0.5 * sep0_mm * np.array([0, 1.0, 0]), -0.5 * sep0_mm * np.array([0, 1.0, 0])
    def v(p): return C * p / np.sqrt(MQ * MQ + p @ p)
    def rhs(s):
        a1, q1, a2, q2 = s[0:3], s[3:6], s[6:9], s[9:12]; v1, v2 = v(q1), v(q2); dl = a2 - a1; h = dl / (np.linalg.norm(dl) + 1e-12)
        F1 = kL * charge * np.cross(v1 / C, Bv) + Tgm * C * h; F2 = kL * (-charge) * np.cross(v2 / C, Bv) - Tgm * C * h
        return np.concatenate([v1, F1, v2, F2])
    dt = tmax_ns / (n_steps - 1); s = np.concatenate([r1, p1, r2, p2]); S = np.empty((n_steps, 12))
    for i in range(n_steps):
        S[i] = s; k1 = rhs(s); k2 = rhs(s + 0.5 * dt * k1); k3 = rhs(s + 0.5 * dt * k2); k4 = rhs(s + dt * k3); s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    t = np.arange(n_steps) * dt
    # to natural units: x [GeV^-1] = x_mm / hbar c ; t [GeV^-1] = c t / hbar c
    return t * C / HB_MM, S[:, 0:3] / HB_MM, S[:, 3:6], S[:, 6:9] / HB_MM, S[:, 9:12]

def fig2(t, x1, p1, x2, p2):
    HB = f22.HB; e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
    t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    I = lambda a: np.column_stack([np.interp(t1[ok], t2, a[:, k]) for k in range(3)]); dv = y1[ok] - I(y2)
    L = np.linalg.norm(np.cross(dv, (k1[ok] - I(k2)) / 2), axis=1) / 1e12; d = np.linalg.norm(dv, axis=1) * HB
    g = 1 / np.sqrt(1 - b @ b); tl = g * (t1[ok] + ((y1[ok] + I(y2)) / 2) @ b); xc = (x1 + x2) / 2
    r = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1])) * HB; s = r <= 5.0
    r, L, d = r[s], L[s], d[s]; mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1
    return r, L, d, mn
P("paper: d max 3.56 cm, spacing 1.155 cm, |L| at closest approaches 0.645 / 0.194 / 0.514 / 0.287 (1e12 hbar)")
curves = {}
for lab, kw in (("as supplied (no c in Lorentz, 2 mm start, axis perp)", dict(c_fix=False, sep0_mm=2.0, axis="perp")),
                ("c fixed, 2 mm start, axis perp", dict(c_fix=True, sep0_mm=2.0, axis="perp")),
                ("c fixed, start at one point, axis perp", dict(c_fix=True, sep0_mm=0.0, axis="perp")),
                ("c fixed, start at one point, axis z", dict(c_fix=True, sep0_mm=0.0, axis="z")),
                ("no c, start at one point, axis z", dict(c_fix=False, sep0_mm=0.0, axis="z")),
                ("c fixed, 2 mm start, axis z", dict(c_fix=True, sep0_mm=2.0, axis="z"))):
    r, L, d, mn = fig2(*simulate(**kw)); curves[lab] = (r, L, d)
    P(f"{lab:52s}: d max {d.max():.2f} cm, spacing {np.diff(r[mn]).mean() if len(mn) > 1 else np.nan:.3f} cm, |L| max {L.max():.3f}, "
      f"|L| at closest approaches " + " / ".join(f"{L[i]:.3f}" for i in mn[:4]))
np.savez(f"{T_}/D23_fig2_external_simulator_curves.npz", **{k.replace(' ', '_').replace(',', ''): np.array(v) for k, v in curves.items()})
open(f"{T_}/D23_fig2_external_simulator_test.txt", "w").write("\n".join(out) + "\n")
