#!/usr/bin/env python3
"""Fig. 2: systematic scan of the possibilities behind the three open questions (2026-10-12).
Target (paper, D24): |L| at closest approaches 0.645 / 0.194 / 0.514 / 0.287 (1e12 hbar); signed change per half-oscillation +0.645 / -0.839 / +0.708 / -0.801.
Base event: constructed (D8): v* = 0.556 along z, v_cm = 0.0975 along x, m = 1800 GeV, Lambda = 2 keV, B = 2 T along z, charges +-2/3.
A. Definition of L (Q1), on the base trajectory: CM frame equal CM time (base); lab equal lab time about the midpoint / centre of energy / production point;
   non-relativistic momenta m v; total L of quirks + string (= integral of the EM torque, since the string forces are internal); r of quirk 1 instead of the CM.
B. Charges and initial momenta (Q2): 60 random configurations: isotropic oscillation axis, transverse CM direction random, longitudinal CM speed
   0-0.5, charges from {+-2/3, +-1, (+1, 0), (+1, -1/3)}; v* and transverse CM speed fixed to the paper's event.
C. Equation of motion (Q3), own RK4 with switchable terms (validated against the production integrator in variant C0):
   C0 Eq. 3 + Lorentz; C1 without the v_par v_perp term; C2 constant string force -T s; C3 non-relativistic m dv/dt = F;
   C4 Eq. 3 + Lorentz with forward Euler (3000 / 300 steps per period); C5 RK4 300 steps per period; C6 Lorentz force with lab velocity but B scaled by gamma_cm.
   Material: not simulated; the paper's half-oscillations already differ at r < 2.35 cm (inside the beam pipe, no material).
Metric: |L| at closest approaches 1-4 and the ratio |L(2nd)| / |L(1st)| (paper 0.30). Output: tables/D20_fig2_possibilities.txt"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB, T, MQ, LAM, VS, BT = f22.HB, f22.T, 1800.0, 2e-6, 0.556, 0.0975
E_NAT, BZ = 0.30282212, 2.0 * 1.9535e-16
gs = 1 / np.sqrt(1 - VS ** 2); PS = MQ * gs * VS; ES = MQ * gs; PERIOD = 2 * (2 * VS * gs * MQ / LAM ** 2)
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
PAPER = "0.645 / 0.194 / 0.514 / 0.287 (ratio 0.30)"

def boost(E, p, b):
    b = np.asarray(b, float); bb = np.linalg.norm(b)
    if bb == 0: return E, p
    g = 1 / np.sqrt(1 - bb * bb); bh = b / bb; pl = p @ bh
    return g * (E + bb * pl), p + ((g - 1) * pl + g * bb * E) * bh

# ---------- own integrator with switchable terms ----------
def rhs(s, q1, q2, mode):
    x1, p1, x2, p2 = s[0:3], s[3:6], s[6:9], s[9:12]
    if mode == "nonrel": v1, v2 = p1 / MQ, p2 / MQ
    else: v1, v2 = p1 / np.sqrt(p1 @ p1 + MQ * MQ), p2 / np.sqrt(p2 @ p2 + MQ * MQ)
    d = x1 - x2; dist = np.linalg.norm(d)
    n = d / dist if dist > 1e-9 else (v1 - v2) / max(np.linalg.norm(v1 - v2), 1e-12)
    def sf(v, n):
        vpar = v @ n; vperp = v - vpar * n; st = np.sqrt(max(1 - vperp @ vperp, 1e-12))
        if mode == "no_vpar_vperp": return -LAM ** 2 * st * n
        if mode == "const": return -LAM ** 2 * n
        return -LAM ** 2 * (st * n + vpar / st * vperp)
    Bz = BZ * (MODE_G if mode == "B_gamma" else 1.0)
    F1 = sf(v1, n) + q1 * E_NAT * np.array([Bz * v1[1], -Bz * v1[0], 0.0]); F2 = sf(v2, -n) + q2 * E_NAT * np.array([Bz * v2[1], -Bz * v2[0], 0.0])
    return np.concatenate([v1, F1, v2, F2])
MODE_G = 1.0
def integrate(P1, P2, q1, q2, mode="eq3", scheme="rk4", spp=3000, rmax=5.3, vT=BT):
    dt = PERIOD / spp; tmax = rmax / HB / max(vT, 1e-3) * 1.02; n = int(tmax / dt) + 1
    s = np.concatenate([np.zeros(3), P1, np.zeros(3), P2]); S = np.empty((n + 1, 12)); S[0] = s
    for i in range(n):
        if scheme == "euler": s = s + dt * rhs(s, q1, q2, mode)
        else:
            k1 = rhs(s, q1, q2, mode); k2 = rhs(s + 0.5 * dt * k1, q1, q2, mode); k3 = rhs(s + 0.5 * dt * k2, q1, q2, mode); k4 = rhs(s + dt * k3, q1, q2, mode)
            s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        S[i + 1] = s
    return np.arange(n + 1) * dt, S[:, 0:3], S[:, 3:6], S[:, 6:9], S[:, 9:12]

def production(P1, P2, q1, q2):
    f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * 3000
    _, tr = f22.tth.simulate_quirk_hits((*P1, np.sqrt(P1 @ P1 + MQ * MQ)), (*P2, np.sqrt(P2 @ P2 + MQ * MQ)), mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0,
                                        charge1=q1, charge2=q2, rng=np.random.default_rng(0), z0_cm=0.0, max_layer_r_cm=6.0, steps_per_period=3000)
    return tuple(np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "p1", "x2", "p2"))

def L_cm(t, x1, p1, x2, p2, nonrel=False):
    e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (e1[0] + e2[0])
    t1, y1, _, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, _, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    I = lambda a: np.column_stack([np.interp(t1[ok], t2, a[:, k]) for k in range(3)])
    dv = y1[ok] - I(y2); kr = (k1[ok] - I(k2)) / 2
    if nonrel:   # m v instead of the relativistic momentum
        Ea, Eb = np.sqrt((k1[ok] ** 2).sum(1) + MQ * MQ), np.sqrt((I(k2) ** 2).sum(1) + MQ * MQ); kr = MQ * (k1[ok] / Ea[:, None] - I(k2) / Eb[:, None]) / 2
    L = np.linalg.norm(np.cross(dv, kr), axis=1); d = np.linalg.norm(dv, axis=1) * HB
    g = 1 / np.sqrt(1 - b @ b); tl = g * (t1[ok] + ((y1[ok] + I(y2)) / 2) @ b); xc = (x1 + x2) / 2
    r = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1])) * HB
    return r, L / 1e12, d
def approaches(r, L, d, n=4):
    s = r <= 5.2; r, L, d = r[s], L[s], d[s]
    mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1; mn = mn[r[mn] > 0.05][:n]
    v = [L[i] for i in mn]; return v, (v[1] / v[0] if len(v) > 1 and v[0] > 0 else np.nan)
fmt = lambda v: " / ".join(f"{x:.3f}" for x in v)

n0 = np.array([0, 0, 1.0]); E1, P1 = boost(ES, PS * n0, [BT, 0, 0]); E2, P2 = boost(ES, -PS * n0, [BT, 0, 0])
P(f"paper target: |L| at closest approaches {PAPER}")

# ---------- A. definitions of L on the base trajectory ----------
t, x1, p1, x2, p2 = production(P1, P2, 2 / 3, -2 / 3)
P("\n== A. Definition of L (Q1), base trajectory")
r, L, d = L_cm(t, x1, p1, x2, p2); v, q = approaches(r, L, d); P(f"A0 CM frame, equal CM time, about the CM (base)        : {fmt(v)}  ratio {q:.3f}")
r_, L_, d_ = L_cm(t, x1, p1, x2, p2, nonrel=True); v, q = approaches(r_, L_, d_); P(f"A1 same, non-relativistic momenta m v                  : {fmt(v)}  ratio {q:.3f}")
e1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); e2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); rl = np.hypot(*((x1 + x2)[:, :2] / 2 * HB).T); dl = np.linalg.norm(x1 - x2, axis=1) * HB
XE = (e1[:, None] * x1 + e2[:, None] * x2) / (e1 + e2)[:, None]
for lab, Lv in (("A2 lab, equal lab time, about the midpoint            ", np.cross(x1 - x2, (p1 - p2) / 2)),
                ("A3 lab, equal lab time, about the centre of energy    ", np.cross(x1 - XE, p1) + np.cross(x2 - XE, p2)),
                ("A4 lab, about the production point (interaction pt.)  ", np.cross(x1, p1) + np.cross(x2, p2))):
    v, q = approaches(rl, np.linalg.norm(Lv, axis=1) / 1e12, dl); P(f"{lab}: {fmt(v)}  ratio {q:.3f}")
r1 = np.hypot(x1[:, 0], x1[:, 1]) * HB; v, q = approaches(r1, np.linalg.norm(np.cross(x1 - x2, (p1 - p2) / 2), axis=1) / 1e12, dl)
P(f"A5 lab midpoint L, plotted vs r of quirk 1             : {fmt(v)}  ratio {q:.3f}")
# total L (quirks + string): changes only by the EM torque (string forces are internal) -> integral of the CM-frame EM torque (D25 method)
b = (p1[0] + p2[0]) / (e1[0] + e2[0]); g = 1 / np.sqrt(1 - b @ b)
t1, y1, F1, k1 = f22.lorentz(t, x1, e1, p1, b); t2, y2, F2, k2 = f22.lorentz(t, x2, e2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
ts = t1[ok]; I = lambda a: np.column_stack([np.interp(ts, t2, a[:, k]) for k in range(3)]); ya, yb = y1[ok], I(y2)
Ea, Eb = F1[ok], np.interp(ts, t2, F2); va, vb = k1[ok] / Ea[:, None], I(k2) / Eb[:, None]; X = (Ea[:, None] * ya + Eb[:, None] * yb) / (Ea + Eb)[:, None]
Ecm = g * np.cross(b, [0, 0, BZ]); Bcm = g * np.array([0, 0, BZ])
tau = np.cross(ya - X, 2 / 3 * E_NAT * (Ecm + np.cross(va, Bcm))) + np.cross(yb - X, -2 / 3 * E_NAT * (Ecm + np.cross(vb, Bcm)))
Ltot = np.concatenate([np.zeros((1, 3)), np.cumsum(0.5 * (tau[1:] + tau[:-1]) * np.diff(ts)[:, None], axis=0)])
v, q = approaches(r, np.linalg.norm(Ltot, axis=1) / 1e12, d); P(f"A6 total L of quirks + string (integral of EM torque)  : {fmt(v)}  ratio {q:.3f}")

# ---------- B. charges and initial momenta ----------
P("\n== B. Charges and initial momenta (Q2): 60 random configurations, production integrator")
rng = np.random.default_rng(7); CH = [(2 / 3, -2 / 3), (1, -1), (1, 0), (1, -1 / 3)]; ratios = []
for k in range(60):
    ax = rng.normal(size=3); ax /= np.linalg.norm(ax); ph = rng.uniform(0, 2 * np.pi); bz = rng.uniform(0, 0.5)
    bvec = np.array([BT * np.cos(ph), BT * np.sin(ph), bz]); q1, q2 = CH[k % 4]
    if np.linalg.norm(bvec) >= 1: continue
    E1r, P1r = boost(ES, PS * ax, bvec); E2r, P2r = boost(ES, -PS * ax, bvec)
    tt, a1, b1, a2, b2 = production(P1r, P2r, q1, q2); rr, LL, dd = L_cm(tt, a1, b1, a2, b2)
    v, q = approaches(rr, LL, dd); ratios.append(q)
    if k < 8 or q > 0.05: P(f"   #{k:2d} axis {np.round(ax, 2)}, v_cm {np.round(bvec, 3)}, charges ({q1:+.2f},{q2:+.2f}): {fmt(v)}  ratio {q:.3f}")
ratios = np.array(ratios); P(f"   {len(ratios)} configurations: ratio |L(2nd)|/|L(1st)| median {np.nanmedian(ratios):.4f}, max {np.nanmax(ratios):.4f} (paper 0.30)")

# ---------- C. equation of motion ----------
P("\n== C. Equation of motion (Q3), own RK4 with switchable terms")
for lab, kw in (("C0 Eq. 3 + Lorentz (own RK4, check vs A0)         ", dict()),
                ("C1 without the v_par v_perp string term          ", dict(mode="no_vpar_vperp")),
                ("C2 constant string force -T s                    ", dict(mode="const")),
                ("C3 non-relativistic  m dv/dt = F                 ", dict(mode="nonrel")),
                ("C4 Eq. 3 + Lorentz, forward Euler, 3000 steps     ", dict(scheme="euler")),
                ("C4b forward Euler, 300 steps                      ", dict(scheme="euler", spp=300)),
                ("C5 RK4, 300 steps per period                      ", dict(spp=300)),
                ("C6 Lorentz force with B x gamma_cm                ", dict(mode="B_gamma"))):
    if kw.get("mode") == "B_gamma": MODE_G = 1 / np.sqrt(1 - BT ** 2)
    tt, a1, b1, a2, b2 = integrate(P1, P2, 2 / 3, -2 / 3, **kw); MODE_G = 1.0
    rr, LL, dd = L_cm(tt, a1, b1, a2, b2, nonrel=(kw.get("mode") == "nonrel"))
    v, q = approaches(rr, LL, dd); P(f"{lab}: {fmt(v)}  ratio {q:.3f}   d max {dd[rr <= 5].max():.2f} cm")
P(f"\npaper: {PAPER}")
open(f"{T}/D20_fig2_possibilities.txt", "w").write("\n".join(out) + "\n")
