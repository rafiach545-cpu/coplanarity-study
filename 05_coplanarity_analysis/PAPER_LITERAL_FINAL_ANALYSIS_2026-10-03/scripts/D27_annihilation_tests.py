#!/usr/bin/env python3
"""Annihilation at the L ~ 0 meetings (D29): two separate tests (2026-10-13).

A. Worst-case semi-classical estimate (S-wave at every second meeting), per fiducial event of COL2000 / EW2000 and for every Table I Lambda.
   |psi(0)|^2 = mu F / (2 pi) for any S state of V = F r (mu = m/2, F = Lambda^2); Gamma = (sigma v) |psi(0)|^2;
   one full oscillation (two meetings) in the CM frame lasts T = 4 m gamma* v* / Lambda^2, so P_osc = Gamma T = c_sigma alpha^2 gamma* v*, with
   sigma v = c_sigma pi alpha^2 / m^2. c_sigma = 1 (upper value used in the request) and the dark-gluon channel of arXiv:2404.13814 Eq. 4.11 with
   N_IC = 2 (fermions: c_sigma = (N_IC^2 - 1) / (4 N_C N_IC) = 1/8 for colored (N_C = 3), 3/8 for colour-neutral (N_C = 1)); alpha = 0.02 and 0.05.
   Full oscillations inside the tracker: N = t_exit / (gamma_cm T), t_exit = min(25 ns, 51.4 cm / (beta_T c)) (CM reaching the outer SCT layer).
   Survival = (1 - P_osc)^N. Kinematics from the production samples (2 keV / 4 keV); for the other Lambda N scales as Lambda^2.
   Non-relativistic formula (v* ~ 0.5-0.6), order of magnitude.

B. Quantum toy model of the relative coordinate (2D, hbar = mu = F = 1): H = p^2/2 + |r| - f x (string + uniform CM electric force f = qE*
   perpendicular to the initial motion). Initial Gaussian packet at the origin (width 1) with momentum p0 = 8 along z (amplitude p0^2/2 = 32).
   Split-operator FFT on a 768^2 grid (dx = 0.125), dt = 0.005, four meetings (t = 0 ... 64). Measured: probability inside r < 1
   at each return to the origin, relative to the field-free run (f = 0); quantum <L> and its spread; classical L(t) of the same model (RK4).
   f chosen so that the classical |L| peak is ~10 and ~30 hbar (f = 10, 30 / (2 p0^3 / 3)).
Output: tables/D27_annihilation_A.csv, tables/D27_annihilation_B.txt"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
HB_CM, HB_NS = 1.973269804e-14, 6.582119569e-16; C_CM_NS = 29.9792458
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)

# ------------------------------------------------------------------ A
acc = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); acc = acc[(acc.geom == "B") & (acc.bs == "CV") & (acc.sct == "Z0")]
BASE = "/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events"
SAMP = {"COL2000": ("colored_1800GeV_L2keV", 1800.0, 2000.0, [1000, 2000, 3000, 5000, 10000], 1 / 8),
        "EW2000": ("EW_800GeV_L4keV", 800.0, 4000.0, [1000, 2000, 3000, 4000, 5000], 3 / 8)}
rows = []
for s, (tag, m, lam_prod, lams, c_dark) in SAMP.items():
    M = pd.read_csv(f"{BASE}/{tag}/trigger_passing_events.csv"); fid = acc[(acc["sample"] == s) & (acc.fid.astype(str) == "True")].key.astype(int)
    for k in fid:
        r = M.iloc[k]; p1 = np.array([r.px1, r.py1, r.pz1]); p2 = np.array([r.px2, r.py2, r.pz2])
        E1, E2 = np.sqrt(p1 @ p1 + m * m), np.sqrt(p2 @ p2 + m * m); P_ = p1 + p2; E = E1 + E2; Mi = np.sqrt(E * E - P_ @ P_)
        gs = Mi / (2 * m); vs = np.sqrt(1 - 1 / gs ** 2); b = P_ / E; bT = np.hypot(b[0], b[1]); gcm = E / Mi
        t_exit = min(25.0, 51.4 / (bT * C_CM_NS))
        for lam in lams:
            Tosc_ns = gcm * 4 * m * gs * vs / (lam * 1e-9) ** 2 * HB_NS          # lab time of one full oscillation (two meetings)
            N = t_exit / Tosc_ns
            for alpha in (0.02, 0.05):
                for cs_name, cs in (("c_sigma=1", 1.0), ("dark gluons N_IC=2", c_dark)):
                    Posc = cs * alpha ** 2 * gs * vs
                    rows.append(dict(sample=s, key=k, lambda_ev=lam, production_lambda=lam == lam_prod, gamma_v=gs * vs, N_osc=N,
                                     alpha=alpha, sigma_v=cs_name, P_osc=Posc, survival=(1 - Posc) ** N))
A = pd.DataFrame(rows); A.to_csv(f"{T}/D27_annihilation_A.csv", index=False)
P("== A. worst case (S-wave at every second meeting), mean over fiducial events: survival probability inside the tracker")
g = A.groupby(["sample", "lambda_ev", "sigma_v", "alpha"]).agg(N_osc_median=("N_osc", "median"), gamma_v_median=("gamma_v", "median"), survival_mean=("survival", "mean"),
                                                                  survival_min=("survival", "min")).reset_index()
P(g.to_string(index=False, float_format=lambda v: f"{v:.4g}"))

# ------------------------------------------------------------------ B
P("\n== B. quantum toy model (2D relative coordinate, hbar = mu = F = 1, p0 = 8)")
n, Lb = 768, 48.0; x = (np.arange(n) - n // 2) * (2 * Lb / n); dx = x[1] - x[0]; X, Z = np.meshgrid(x, x, indexing="ij")
k = 2 * np.pi * np.fft.fftfreq(n, dx); KX, KZ = np.meshgrid(k, k, indexing="ij"); p0, dt = 8.0, 0.005
R = np.hypot(X, Z); absorb = np.where(R > Lb - 4, np.exp(-((R - (Lb - 4)) / 2) ** 2), 1.0)
def quantum(f, tmax=64.0):
    V = R - f * X; expV = np.exp(-0.5j * V * dt); expK = np.exp(-0.5j * (KX ** 2 + KZ ** 2) * dt)
    psi = np.exp(-(X ** 2 + Z ** 2) / 2.0 + 1j * p0 * Z).astype(complex); psi /= np.sqrt((np.abs(psi) ** 2).sum() * dx * dx)
    nst = int(tmax / dt); rec = []; inner = R < 1.0
    for i in range(nst + 1):
        if i % 10 == 0:
            d = np.abs(psi) ** 2; pin = d[inner].sum() * dx * dx
            ph = np.fft.fft2(psi); dpx = np.fft.ifft2(1j * KX * ph); dpz = np.fft.ifft2(1j * KZ * ph)
            Lop = -1j * (Z * dpx - X * dpz)                                  # L_y = z p_x - x p_z
            Lm = (np.conj(psi) * Lop).sum().real * dx * dx; L2 = (np.abs(Lop) ** 2).sum() * dx * dx
            rec.append((i * dt, pin, Lm, np.sqrt(max(L2 - Lm ** 2, 0)), d.sum() * dx * dx))
        if i == nst: break
        psi = expV * np.fft.ifft2(expK * np.fft.fft2(expV * psi)) * absorb
    return np.array(rec)
def classical(f, tmax=64.0, h=1e-3):
    s = np.array([0.0, 0.0, 0.0, p0]); res = []
    def rhs(s):
        r = np.hypot(s[0], s[1]) + 1e-12; return np.array([s[2], s[3], -s[0] / r + f, -s[1] / r])
    for i in range(int(tmax / h) + 1):
        if i % 10 == 0: res.append((i * h, s[1] * s[2] - s[0] * s[3]))
        k1 = rhs(s); k2 = rhs(s + h / 2 * k1); k3 = rhs(s + h / 2 * k2); k4 = rhs(s + h * k3); s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return np.array(res)
Q0 = quantum(0.0)
tm = [16.0 * j for j in range(1, 5)]                                          # classical meeting times (2 p0 / F per half-oscillation)
def at_meeting(Q, t):
    w = (Q[:, 0] > t - 2) & (Q[:, 0] < t + 2); i = np.argmax(np.where(w, Q[:, 1], -1)); return Q[i]
for Lpk in (10.0, 30.0):
    f = Lpk / (2 * p0 ** 3 / 3); Q = quantum(f); C = classical(f)
    P(f"-- f = {f:.4f} (classical |L| peak target {Lpk:.0f} hbar)")
    for j, t in enumerate(tm, 1):
        a, a0 = at_meeting(Q, t), at_meeting(Q0, t); Lc = np.interp(a[0], C[:, 0], C[:, 1])
        P(f"   meeting {j} (t = {a[0]:5.2f}): P(r < 1) = {a[1]:.4f}, field-free {a0[1]:.4f}, ratio {a[1] / a0[1]:.3f} | quantum <L> = {a[2]:+7.2f} +- {a[3]:5.2f}"
          f" | classical L = {Lc:+7.2f} | norm {a[4]:.3f}")
    iq = np.argmax(np.abs(Q[:, 2])); ic = np.argmax(np.abs(C[:, 1]))
    P(f"   peak |<L>|: quantum {abs(Q[iq, 2]):.2f} at t = {Q[iq, 0]:.1f}; classical {abs(C[ic, 1]):.2f} at t = {C[ic, 0]:.1f}")
open(f"{T}/D27_annihilation_B.txt", "w").write("\n".join(out) + "\n")
