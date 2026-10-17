#!/usr/bin/env python3
"""Fig. 2: four checks (2026-10-12), requested after the D23 scan.
1. Paper curves (tables/fig2_r_d_L_paper.csv; L and d sampled at different r): minima of d and of |L| located by parabolic interpolation on each
   curve's own points; |L| interpolated at the d minima.
2. Constructed event (D8 kinematics, axis z, charges +-2/3) and simulated COL2000 key 8: initial CM momenta balance, |v*|, CM velocity, charges, B direction
   (sign of the implemented force q v x B checked against the right-hand side of quirk_trajectory_optimized_v2).
3. Signed L: vector L(t) in the CM frame, its projection on the direction at the first |L| peak, and the angle of L to that direction.
4. Torque: exact CM-frame torque tau = sum_i r_i x q_i (E* + v_i* x B*), r_i from the CM point, E* = gamma v_cm x B, B* = gamma B - gamma^2/(gamma+1) v_cm (v_cm.B);
   integral of tau dt* per half-oscillation (between successive d minima) compared with the change of L over the same interval, and with the paper's
   estimate q d x E_cm. Output: tables/D16_fig2_four_checks.txt (printed)."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB, T, MQ = f22.HB, f22.T, 1800.0; f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
E_NAT, T2GEV2 = 0.30282212, 1.9535e-16; BZ = 2.0 * T2GEV2
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)

def minima_parabolic(x, y):
    i = np.where((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:]))[0] + 1; res = []
    for k in i:
        x0, x1, x2 = x[k - 1:k + 2]; y0, y1, y2 = y[k - 1:k + 2]
        den = (x0 - x1) * (x0 - x2) * (x1 - x2); A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
        B = (x2 ** 2 * (y0 - y1) + x1 ** 2 * (y2 - y0) + x0 ** 2 * (y1 - y2)) / den; C = y1 - A * x1 ** 2 - B * x1
        xv = -B / (2 * A) if A > 0 else x1; res.append((xv, A * xv ** 2 + B * xv + C if A > 0 else y1))
    return res

# ---- 1. paper curves
p = pd.read_csv(f"{T}/fig2_r_d_L_paper.csv"); pd_ = p.dropna(subset=["d_cm"]).sort_values("r_cm"); pl = p.dropna(subset=["L_1e12_hbar"]).sort_values("r_cm")
dmin = [m for m in minima_parabolic(pd_.r_cm.values, pd_.d_cm.values)]; lmin = minima_parabolic(pl.r_cm.values, pl.L_1e12_hbar.values)
P("== 1. paper curves (parabolic minima on each curve's own points)")
P("   d minima (r cm, d cm):", " / ".join(f"({r:.3f}, {v:.3f})" for r, v in dmin))
P("   |L| at the d minima (linear interpolation of the L curve):", " / ".join(f"{np.interp(r, pl.r_cm, pl.L_1e12_hbar):.3f}" for r, _ in dmin))
P("   |L| minima (r cm, |L| 1e12 hbar):", " / ".join(f"({r:.3f}, {v:.3f})" for r, v in lmin))
P("   d at the |L| minima:", " / ".join(f"{np.interp(r, pd_.r_cm, pd_.d_cm):.2f}" for r, _ in lmin))
P("   sampling: d points", len(pd_), "L points", len(pl), "median spacing in r", f"{np.median(np.diff(pd_.r_cm)):.4f} / {np.median(np.diff(pl.r_cm)):.4f} cm")

# ---- 2-4. trajectories
def boost_x(E, p, b):
    g = 1 / np.sqrt(1 - b * b); return g * (E + b * p[0]), np.array([g * (p[0] + b * E), p[1], p[2]])
gs = 1 / np.sqrt(1 - 0.556 ** 2); ps = MQ * gs * 0.556; Es = MQ * gs; n = np.array([0, 0, 1.0])
E1, P1 = boost_x(Es, ps * n, 0.0975); E2, P2 = boost_x(Es, -ps * n, 0.0975)
M = pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv"); m8 = M.iloc[8]
EVENTS = {"constructed (axis z, +-2/3)": ((*P1, E1), (*P2, E2), 2 / 3, -2 / 3),
          "simulated COL2000 key 8": ((m8.px1, m8.py1, m8.pz1, m8.E1), (m8.px2, m8.py2, m8.pz2, m8.E2), float(m8.charge1), float(m8.charge2))}

# sign of the implemented magnetic force (right-hand side of the integrator) vs q v x B with B = +z
import quirk_trajectory_optimized_v2 as v2
r_ = v2._rhs(0, 0, 0, 100.0, 0, 0, 1, 0, 0, 0, 0, 0, MQ, 0.3, 0.0, 0.0, BZ)
P("== 2. implemented magnetic force for q = 0.3, p = +x, B along +z: F =", np.round(np.array(r_[3:6]) / (0.3 * BZ * 100 / np.hypot(100, MQ)), 6), "(q v x B = -y: expect [0, -1, 0])")

for name, (Q1, Q2, c1, c2) in EVENTS.items():
    _, tr = f22.tth.simulate_quirk_hits(Q1, Q2, mass_gev=MQ, Lambda_gev=2e-6, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0),
                                        z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=3000)
    t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0]); bb = np.linalg.norm(b); g = 1 / np.sqrt(1 - bb * bb)
    t1, y1, F1, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, F2, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    ts = t1[ok]; I = lambda a: np.column_stack([np.interp(ts, t2, a[:, k]) for k in range(3)])
    ya, yb, ka, kb = y1[ok], I(y2), k1[ok], I(k2); Ea, Eb = F1[ok], np.interp(ts, t2, F2)
    dv = ya - yb; Lv = np.cross(dv, (ka - kb) / 2); L = np.linalg.norm(Lv, axis=1); d = np.linalg.norm(dv, axis=1) * HB
    P(f"\n== {name}")
    P("2. initial CM frame: |p1*+p2*|/|p1*| =", f"{np.linalg.norm(ka[0] + kb[0]) / np.linalg.norm(ka[0]):.2e}", "| |v1*|, |v2*| =", f"{np.linalg.norm(ka[0]) / Ea[0]:.4f}, {np.linalg.norm(kb[0]) / Eb[0]:.4f}",
      "| v_cm =", np.round(b, 5), f"|v_cm,T| = {np.hypot(b[0], b[1]):.4f}", "| charges", c1, c2, "| B = +z, 2 T",
      f"| d max {d.max():.3f} cm, energy-conservation prediction {2 * (Ea[0] / MQ - 1) * MQ / 4e-12 * HB:.3f} cm")
    # 3. signed L
    i0 = int(np.argmax(L)); nh = Lv[i0] / L[i0]; Ls = Lv @ nh; ang = np.degrees(np.arccos(np.clip(np.abs(Ls) / np.maximum(L, 1e-300), -1, 1)))
    big = L > 0.05 * L.max()
    P("3. signed L along its direction at the |L| peak: n =", np.round(nh, 4), f"| angle of L to +-n where |L| > 5% of max: max {ang[big].max():.3g} deg",
      f"| min signed L/|L|max {Ls.min() / L.max():+.4f}, max {Ls.max() / L.max():+.4f}")
    # 4. torque in the CM frame
    vc = b; Ecm = g * np.cross(vc, [0, 0, BZ]); Bcm = g * np.array([0, 0, BZ]) - g * g / (g + 1) * vc * (vc @ [0, 0, BZ])
    va, vb = ka / Ea[:, None], kb / Eb[:, None]; X = (ya * Ea[:, None] + yb * Eb[:, None]) / (Ea + Eb)[:, None]
    Fa = c1 * E_NAT * (Ecm + np.cross(va, Bcm)); Fb = c2 * E_NAT * (Ecm + np.cross(vb, Bcm))
    tau = np.cross(ya - X, Fa) + np.cross(yb - X, Fb); tau_paper = 0.5 * (c1 - c2) * E_NAT * np.cross(dv, Ecm)
    Lc = np.cross(ya - X, ka) + np.cross(yb - X, kb)   # L about the centre of energy (equal masses: equals d x (p1-p2)/2 when p1* = -p2*)
    cum = lambda f: np.concatenate([np.zeros((1, 3)), np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(ts)[:, None], axis=0)])
    Ttau, Tpap = cum(tau), cum(tau_paper)
    dm = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1; edges = np.concatenate([[0], dm, [len(ts) - 1]])
    xc = (x1 + x2) / 2; tl = g * (ts + ((ya + yb) / 2) @ b); r = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1])) * HB
    P("4. per half-oscillation (between successive d minima), projections on n in 1e12 hbar:")
    P("   arch  r_end(cm)   dL(trajectory)   int tau dt (exact CM)   int q d x E_cm (paper Eq. 5 form)   L at arch end")
    for a in range(len(edges) - 1):
        i, j = edges[a], edges[a + 1]
        if r[i] > 5.0: break
        P(f"   {a + 1:3d}   {r[j]:7.3f}   {((Lc[j] - Lc[i]) @ nh) / 1e12:+12.4f}   {((Ttau[j] - Ttau[i]) @ nh) / 1e12:+18.4f}   {((Tpap[j] - Tpap[i]) @ nh) / 1e12:+24.4f}"
          f"   {L[j] / 1e12:12.4f}")
    rel = np.abs((Lc - Lc[0]) - Ttau).max() / L.max()
    P(f"   max |L(t) - L(0) - int tau dt| / |L|max over the whole trajectory = {rel:.2e}")
open(f"{T}/D16_fig2_four_checks.txt", "w").write("\n".join(out) + "\n")
