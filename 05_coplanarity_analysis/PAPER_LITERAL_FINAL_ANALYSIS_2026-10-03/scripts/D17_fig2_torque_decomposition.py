#!/usr/bin/env python3
"""Fig. 2 torque decomposition (2026-10-12), follow-up of D16 item 4:
  dL(trajectory) = int tau_EM dt + int tau_string dt + (frame term) + numerical residual, per half-oscillation.
Forces are taken from the integrator's own right-hand side (quirk_trajectory_optimized_v2._rhs) at every stored step:
string only (B = 0) and electromagnetic only (Lambda = 0), so no force is re-derived.
(A) Lab frame, equal lab time (the integrator's own time slices, no interpolation):
    L = sum_i (x_i - X) x p_i about the centre of energy X; dL/dt = sum_i (x_i - X) x F_i - (dX/dt) x P   (exact identity, v_i x p_i = 0).
(B) Initial CM frame, equal CM time (as Fig. 2): each lab force is transformed to the CM frame,
    F* = [F + ((g-1)(F.b^) - g |b| (F.v)) b^] / (g (1 - b.v)),   (from dp*/dt and dt*/dt)
    interpolated to quirk 1's CM times, and tau* = sum_i (y_i - X*) x F*_i;  dL*/dt* = sum tau* - (dX*/dt*) x P*.
Events: constructed (D8 kinematics, axis z, charges +-2/3) and simulated COL2000 key 8. Output: tables/D17_fig2_torque_decomposition.txt"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
import quirk_trajectory_optimized_v2 as v2
HB, T, MQ = f22.HB, f22.T, 1800.0; f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
E_NAT, BZ, LAM = 0.30282212, 2.0 * 1.9535e-16, 2e-6
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
def boost_x(E, p, b):
    g = 1 / np.sqrt(1 - b * b); return g * (E + b * p[0]), np.array([g * (p[0] + b * E), p[1], p[2]])
gs = 1 / np.sqrt(1 - 0.556 ** 2); ps = MQ * gs * 0.556; Es = MQ * gs; n = np.array([0, 0, 1.0])
E1, P1 = boost_x(Es, ps * n, 0.0975); E2, P2 = boost_x(Es, -ps * n, 0.0975)
m8 = pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv").iloc[8]
EVENTS = {"constructed (axis z, +-2/3)": ((*P1, E1), (*P2, E2), 2 / 3, -2 / 3),
          "simulated COL2000 key 8": ((m8.px1, m8.py1, m8.pz1, m8.E1), (m8.px2, m8.py2, m8.pz2, m8.E2), float(m8.charge1), float(m8.charge2))}
cum = lambda f, t: np.concatenate([np.zeros((1, 3)), np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(t)[:, None], axis=0)])
def forces(x1, p1, x2, p2, c1, c2):
    S1, S2, M1, M2 = (np.zeros_like(x1) for _ in range(4))
    for k in range(len(x1)):
        a = (*x1[k], *p1[k], *x2[k], *p2[k], MQ)
        r = v2._rhs(*a, c1 * E_NAT, c2 * E_NAT, LAM ** 2, 0.0); S1[k], S2[k] = r[3:6], r[9:12]      # string only
        r = v2._rhs(*a, c1 * E_NAT, c2 * E_NAT, 0.0, BZ); M1[k], M2[k] = r[3:6], r[9:12]            # electromagnetic only
    return S1, S2, M1, M2
def table(label, t, d_cm, r_cm, Lv, parts, nh):
    dm = np.where((d_cm[1:-1] < d_cm[:-2]) & (d_cm[1:-1] <= d_cm[2:]))[0] + 1; edges = np.concatenate([[0], dm])
    C = {k: cum(v, t) for k, v in parts.items()}
    P(f"  {label}: per half-oscillation, projection on the L axis, 1e12 hbar")
    P("   arch  r_end   dL(traj)   EM        string    frame term   sum      residual   string/EM")
    for a in range(len(edges) - 1):
        i, j = edges[a], edges[a + 1]
        if r_cm[j] > 5.0: break
        dL = (Lv[j] - Lv[i]) @ nh / 1e12; v = {k: (C[k][j] - C[k][i]) @ nh / 1e12 for k in C}; s = sum(v.values())
        P(f"   {a + 1:3d}  {r_cm[j]:6.3f}  {dL:+8.4f}  {v['EM']:+8.4f}  {v['string']:+8.4f}  {v['frame']:+9.5f}  {s:+8.4f}  {dL - s:+9.5f}  {v['string'] / v['EM']:+7.4f}")
for name, (Q1, Q2, c1, c2) in EVENTS.items():
    _, tr = f22.tth.simulate_quirk_hits(Q1, Q2, mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0),
                                        z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=3000)
    t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ)
    xc = (x1 + x2) / 2; rl = np.hypot(xc[:, 0], xc[:, 1]) * HB; keep = rl <= 5.6
    t, x1, x2, p1, p2, e1, e2, rl = t[keep], x1[keep], x2[keep], p1[keep], p2[keep], e1[keep], e2[keep], rl[keep]
    S1, S2, M1, M2 = forces(x1, p1, x2, p2, c1, c2)
    P(f"\n== {name}: {len(t)} steps")
    # (A) lab frame, equal lab time
    X = (e1[:, None] * x1 + e2[:, None] * x2) / (e1 + e2)[:, None]; Pt = p1 + p2; Lv = np.cross(x1 - X, p1) + np.cross(x2 - X, p2)
    Xd = np.gradient(X, t, axis=0)
    parts = dict(EM=np.cross(x1 - X, M1) + np.cross(x2 - X, M2), string=np.cross(x1 - X, S1) + np.cross(x2 - X, S2), frame=-np.cross(Xd, Pt))
    nh = Lv[np.argmax(np.linalg.norm(Lv, axis=1))]; nh = nh / np.linalg.norm(nh)
    table("(A) lab frame, equal lab time, L about the centre of energy", t, np.linalg.norm(x1 - x2, axis=1) * HB, rl, Lv, parts, nh)
    # (B) initial CM frame, equal CM time
    b = (p1[0] + p2[0]) / (e1[0] + e2[0]); bb = np.linalg.norm(b); bh = b / bb; g = 1 / np.sqrt(1 - bb * bb)
    def tf(F, p, e):
        v = p / e[:, None]; return (F + (((g - 1) * (F @ bh) - g * bb * (F * v).sum(1)))[:, None] * bh) / (g * (1 - v @ b))[:, None]
    t1, y1, F1e, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, F2e, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    ts = t1[ok]; I = lambda a: np.column_stack([np.interp(ts, t2, a[:, k]) for k in range(3)])
    ya, yb, ka, kb = y1[ok], I(y2), k1[ok], I(k2); Ea, Eb = F1e[ok], np.interp(ts, t2, F2e)
    Sa, Sb, Ma, Mb = tf(S1, p1, e1)[ok], I(tf(S2, p2, e2)), tf(M1, p1, e1)[ok], I(tf(M2, p2, e2))
    Xs = (Ea[:, None] * ya + Eb[:, None] * yb) / (Ea + Eb)[:, None]; Ps = ka + kb; Ls = np.cross(ya - Xs, ka) + np.cross(yb - Xs, kb)
    Ecm = g * np.cross(b, [0, 0, BZ]); Bcm = g * np.array([0, 0, BZ]) - g * g / (g + 1) * b * (b @ [0, 0, BZ])
    Mchk = np.abs(Ma - c1 * E_NAT * (Ecm + np.cross(ka / Ea[:, None], Bcm))).max() / np.abs(Ma).max()
    parts = dict(EM=np.cross(ya - Xs, Ma) + np.cross(yb - Xs, Mb), string=np.cross(ya - Xs, Sa) + np.cross(yb - Xs, Sb), frame=-np.cross(np.gradient(Xs, ts, axis=0), Ps))
    tl = g * (ts + ((ya + yb) / 2) @ b); rcm = np.hypot(np.interp(tl, t, xc[keep][:, 0]), np.interp(tl, t, xc[keep][:, 1])) * HB
    nh = Ls[np.argmax(np.linalg.norm(Ls, axis=1))]; nh = nh / np.linalg.norm(nh)
    P(f"  check: transformed integrator EM force vs q(E* + v* x B*) on quirk 1: max relative difference {Mchk:.2e}")
    table("(B) initial CM frame, equal CM time, L about the centre of energy (Fig. 2 definition)", ts, np.linalg.norm(ya - yb, axis=1) * HB, rcm, Ls, parts, nh)
    # where does the CM-frame string torque come from: angle between the transformed string force and the CM separation
    da = (ya - yb) / np.linalg.norm(ya - yb, axis=1)[:, None]; sa = Sa / np.linalg.norm(Sa, axis=1)[:, None]; big = np.linalg.norm(ya - yb, axis=1) * HB > 0.3
    P(f"  CM-frame string force on quirk 1: angle to the CM separation line, median {np.degrees(np.median(np.arccos(np.clip(np.abs((sa * da).sum(1)), 0, 1))[big])):.3g} deg,"
      f" max {np.degrees(np.max(np.arccos(np.clip(np.abs((sa * da).sum(1)), 0, 1))[big])):.3g} deg (d > 0.3 cm)")
open(f"{T}/D17_fig2_torque_decomposition.txt", "w").write("\n".join(out) + "\n")
