#!/usr/bin/env python3
"""Fig. 2 (2026-10-12), follow-up of D20 C1: is the 16% string torque (D25) physical or from applying Eq. 3 in the lab frame?
The constructed event is integrated directly in its CM frame: quirks start at the origin with p* = +-p* z, external fields E* = gamma v_cm x B,
B* = gamma B (v_cm = 0.0975 x, B = 2 T z), Lorentz force q (E* + v x B*). In this frame equal-time separation = CM-frame separation, so the
straight string is applied where the paper states it ("in the center of mass frame"). Compared with the lab-frame integration
(production method, then transformed to the CM frame), each with and without the v_par v_perp term of Eq. 3.
Output: tables/D21_fig2_cm_frame_integration.txt"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB, T, MQ, LAM, VS, BT = f22.HB, f22.T, 1800.0, 2e-6, 0.556, 0.0975
E_NAT, BZ = 0.30282212, 2.0 * 1.9535e-16; Q1, Q2 = 2 / 3, -2 / 3
gs = 1 / np.sqrt(1 - VS ** 2); PS = MQ * gs * VS; PERIOD = 2 * (2 * VS * gs * MQ / LAM ** 2); GCM = 1 / np.sqrt(1 - BT ** 2)
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
def rhs(s, E, B, vpv):
    x1, p1, x2, p2 = s[0:3], s[3:6], s[6:9], s[9:12]
    v1, v2 = p1 / np.sqrt(p1 @ p1 + MQ * MQ), p2 / np.sqrt(p2 @ p2 + MQ * MQ); d = x1 - x2; dist = np.linalg.norm(d)
    n = d / dist if dist > 1e-9 else (v1 - v2) / max(np.linalg.norm(v1 - v2), 1e-12)
    def sf(v, n):
        vpar = v @ n; vperp = v - vpar * n; st = np.sqrt(max(1 - vperp @ vperp, 1e-12))
        return -LAM ** 2 * (st * n + (vpar / st * vperp if vpv else 0))
    return np.concatenate([v1, sf(v1, n) + Q1 * E_NAT * (E + np.cross(v1, B)), v2, sf(v2, -n) + Q2 * E_NAT * (E + np.cross(v2, B))])
def run(P1, P2, E, B, vpv, tmax, spp=3000):
    dt = PERIOD / spp; n = int(tmax / dt) + 1; s = np.concatenate([np.zeros(3), P1, np.zeros(3), P2]); S = np.empty((n + 1, 12)); S[0] = s
    for i in range(n):
        k1 = rhs(s, E, B, vpv); k2 = rhs(s + 0.5 * dt * k1, E, B, vpv); k3 = rhs(s + 0.5 * dt * k2, E, B, vpv); k4 = rhs(s + dt * k3, E, B, vpv)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); S[i + 1] = s
    return np.arange(n + 1) * dt, S
def at_approaches(d, L, n=4):
    mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1
    return " / ".join(f"{L[i] / 1e12:.4f}" for i in mn[:n])
TM = 4.3 * PERIOD
Bvec = np.array([0, 0, BZ]); Ecm = GCM * np.cross([BT, 0, 0], Bvec); Bcm = GCM * Bvec
for vpv in (True, False):
    lab = "Eq. 3 full" if vpv else "Eq. 3 without v_par v_perp"
    # (a) directly in the CM frame
    t, S = run(np.array([0, 0, PS]), np.array([0, 0, -PS]), Ecm, Bcm, vpv, TM)
    d = np.linalg.norm(S[:, 0:3] - S[:, 6:9], axis=1); L = np.linalg.norm(np.cross(S[:, 0:3] - S[:, 6:9], (S[:, 3:6] - S[:, 9:12]) / 2), axis=1)
    P(f"{lab:28s} | integrated in the CM frame (E*, B*)     : |L| at closest approaches {at_approaches(d, L)}")
    # (b) in the lab frame, transformed to the CM frame (production method)
    g = GCM; E0 = MQ * gs
    P1 = np.array([g * BT * E0, 0, PS]); P2 = np.array([g * BT * E0, 0, -PS])
    t, S = run(P1, P2, np.zeros(3), Bvec, vpv, TM * g)
    x1, p1, x2, p2 = S[:, 0:3], S[:, 3:6], S[:, 6:9], S[:, 9:12]; e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ)
    b = np.array([BT, 0, 0]); t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    I = lambda a: np.column_stack([np.interp(t1[ok], t2, a[:, k]) for k in range(3)]); dv = y1[ok] - I(y2)
    L = np.linalg.norm(np.cross(dv, (k1[ok] - I(k2)) / 2), axis=1); d = np.linalg.norm(dv, axis=1)
    P(f"{lab:28s} | integrated in the lab frame, then to CM : |L| at closest approaches {at_approaches(d, L)}")
P("EM torque alone per half-oscillation (D25): 0.556; paper: 0.645 / 0.194 / 0.514 / 0.287")
open(f"{T}/D21_fig2_cm_frame_integration.txt", "w").write("\n".join(out) + "\n")
