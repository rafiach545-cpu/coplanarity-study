#!/usr/bin/env python3
"""Checks of the D27 B quantum toy model (2026-10-14), for the f = 0.0879 run (classical |L| peak 30 hbar), where the overlap at meeting 4 was 0.57.
1. Numerical convergence: grid 1024^2 with dx = 0.094 (D27: 768^2, 0.125) and dt = 0.0025 (D27: 0.005); field-free run on the same grid.
2. Classical ensemble: 4000 trajectories sampled from the Wigner function of the same initial packet (|psi|^2 ~ exp(-r^2): position sigma = 1/sqrt 2
   per coordinate; momentum sigma = 1/sqrt 2 around (0, p0)); fraction inside r < 1 and <L> at the meetings, with and without the field.
   Equal quantum and classical-ensemble numbers -> the incomplete return is phase-space spreading of the initial packet (classical), not quantum.
Output: tables/D28_quantum_toy_checks.txt"""
import os, numpy as np
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables"); out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.append(s)
p0, F0 = 8.0, 0.0879; MEET = [16.0 * j for j in range(1, 5)]

def quantum(f, n, Lb, dt, tmax=66.0):
    x = (np.arange(n) - n // 2) * (2 * Lb / n); dx = x[1] - x[0]; X, Z = np.meshgrid(x, x, indexing="ij")
    k = 2 * np.pi * np.fft.fftfreq(n, dx); KX, KZ = np.meshgrid(k, k, indexing="ij"); R = np.hypot(X, Z)
    absorb = np.where(R > Lb - 4, np.exp(-((R - (Lb - 4)) / 2) ** 2), 1.0)
    expV = np.exp(-0.5j * (R - f * X) * dt); expK = np.exp(-0.5j * (KX ** 2 + KZ ** 2) * dt)
    psi = np.exp(-(X ** 2 + Z ** 2) / 2.0 + 1j * p0 * Z).astype(complex); psi /= np.sqrt((np.abs(psi) ** 2).sum() * dx * dx)
    inner = R < 1.0; rec = []; every = int(round(0.05 / dt))
    for i in range(int(tmax / dt) + 1):
        if i % every == 0:
            ph = np.fft.fft2(psi); Lop = -1j * (Z * np.fft.ifft2(1j * KX * ph) - X * np.fft.ifft2(1j * KZ * ph))
            Lm = (np.conj(psi) * Lop).sum().real * dx * dx
            rec.append((i * dt, (np.abs(psi[inner]) ** 2).sum() * dx * dx, Lm))
        psi = expV * np.fft.ifft2(expK * np.fft.fft2(expV * psi)) * absorb
    return np.array(rec)

def classical_ensemble(f, N=4000, h=2e-3, tmax=66.0, seed=1):
    g = np.random.default_rng(seed); s = 1 / np.sqrt(2)
    S = np.column_stack([g.normal(0, s, N), g.normal(0, s, N), g.normal(0, s, N), g.normal(p0, s, N)])   # x, z, px, pz
    def rhs(S):
        r = np.hypot(S[:, 0], S[:, 1]) + 1e-12
        return np.column_stack([S[:, 2], S[:, 3], -S[:, 0] / r + f, -S[:, 1] / r])
    rec = []
    for i in range(int(tmax / h) + 1):
        if i % 25 == 0:
            r = np.hypot(S[:, 0], S[:, 1]); L = S[:, 1] * S[:, 2] - S[:, 0] * S[:, 3]
            rec.append((i * h, np.mean(r < 1.0), L.mean()))
        k1 = rhs(S); k2 = rhs(S + h / 2 * k1); k3 = rhs(S + h / 2 * k2); k4 = rhs(S + h * k3); S = S + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return np.array(rec)

def table(name, A, A0):
    P(f"-- {name}")
    for j, t in enumerate(MEET, 1):
        w = (A[:, 0] > t - 2.5) & (A[:, 0] < t + 2.5); i = np.argmax(np.where(w, A[:, 1], -1)); w0 = (A0[:, 0] > t - 2.5) & (A0[:, 0] < t + 2.5)
        i0 = np.argmax(np.where(w0, A0[:, 1], -1))
        P(f"   meeting {j}: P(r<1) {A[i, 1]:.4f} / field-free {A0[i0, 1]:.4f} = ratio {A[i, 1] / A0[i0, 1]:.3f} | <L> = {A[i, 2]:+6.2f}  (t = {A[i, 0]:.2f})")

C, C0 = classical_ensemble(F0), classical_ensemble(0.0); table("classical ensemble (4000 trajectories, Wigner sampling of the initial packet), f = 0.0879", C, C0)
Q, Q0 = quantum(F0, 1024, 48.0, 0.0025), quantum(0.0, 1024, 48.0, 0.0025); table("quantum, grid 1024^2 (dx 0.094), dt 0.0025, f = 0.0879", Q, Q0)
P("D27 (768^2, dx 0.125, dt 0.005): ratio 0.001 / 0.889 / 0.019 / 0.573, <L> 28.6 / 3.2 / 27.2 / 10.7; single classical trajectory L 28.8 / 1.7 / 30.1 / 6.2")
open(f"{T}/D28_quantum_toy_checks.txt", "w").write("\n".join(out) + "\n")
