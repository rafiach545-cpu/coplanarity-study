#!/usr/bin/env python3
"""09 / Geant4 step G04 (2026-11-19): the string force against an exact solution. Back-to-back quirks along x, B = 0.
With the velocities along the string (v_perp = 0), arXiv:1708.02243 Eq. 3 reduces to a constant force of magnitude Lambda^2 towards the partner,
and so does a straight Nambu-Goto string with massive ends. Each quirk then has hyperbolic motion (exact, independent of the integrator):
  E(x) = E0 - Lambda^2 x,  p(x) = sqrt(E(x)^2 - m^2),  t(x) = (p0 - p(x)) / Lambda^2   (natural units, hbar c = 1.973e-14 GeV cm),
  turning point x_max = (E0 - m) / Lambda^2 (the d_max = 2 (E* - m) / Lambda^2 of the pair), as in arXiv:2611.10273 Sec. I.
E0 - m is chosen so that x_max = 20 cm: the quirks cross L1-L4 (r = 3.3-12.3 cm) on the way out and turn before L5.
Compared: the crossing times of L1-L4 (first crossing, quirk 0) and the turning point max |x| within 1.5 x the exact turning time, Geant4 (ideal8_dense_B0.card) and the old code."""
import os, sys, subprocess, numpy as np, pandas as pd, uproot
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [HERE, f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim"]
import G01_compare_integrator as G                                     # noqa: E402  (numba integrator patched in)
from trajectory_to_hits import simulate_quirk_hits, find_layer_crossing  # noqa: E402
from atlas_geometry import LAYERS                                       # noqa: E402
HBARC, M, XMAX = 1.973269804e-14, 800.0, 20.0
C_NS = 29.9792458                                                       # cm / ns
TILT = 1e-3   # rad: both momenta tilted by 1 mrad towards +y (an exactly collinear start stalls the Geant4 transport); O(TILT^2) effect
RAD = [l["r_cm"] for l in LAYERS][:4]


def T_STOP_NS(lam, E0):            # 1.5 x the exact time to the turning point (before the quirks come back to the vertex)
    return 1.5 * np.sqrt(E0 ** 2 - M ** 2) / (lam ** 2 / HBARC) / C_NS


def exact(lam_gev, E0):
    s = lam_gev ** 2 / HBARC; p0 = np.sqrt(E0 ** 2 - M ** 2)            # force in GeV / cm
    t = {}
    for i, r in enumerate(RAD, 1):
        E = E0 - s * r; p = np.sqrt(E ** 2 - M ** 2); t[i] = (p0 - p) / s / C_NS   # (GeV / (GeV/cm)) = cm -> ns
    return t, (E0 - M) / s


if __name__ == "__main__":
    rows = []
    for lam_ev in (1000.0, 4000.0):
        lam = lam_ev * 1e-9; E0 = M + XMAX * lam ** 2 / HBARC; p0 = np.sqrt(E0 ** 2 - M ** 2)
        t_ex, xmax = exact(lam, E0)
        P1 = (p0 * np.cos(TILT), p0 * np.sin(TILT)); P2 = (-p0 * np.cos(TILT), p0 * np.sin(TILT))
        # Geant4: one event, steps written, quirk 0 (gun p1) along +x
        tag = f"G04_L{lam_ev:g}"; mac = f"{G.OUT}/{tag}.mac"; root = f"{G.OUT}/{tag}.root"
        open(mac, "w").write("\n".join([f"/quirk/mass {M} GeV", f"/quirk/lambda {lam_ev} eV", f"/qsim/card {HERE}/ideal8_dense_B0.card",
                                        "/qsim/gen/mode gun", "/qsim/killSecondaries true", "/qsim/out/towers false", "/qsim/out/stepPrescale 1",
                                        f"/qsim/maxTime {T_STOP_NS(lam, E0):.3f} ns", f"/qsim/gun/p1 {P1[0]} {P1[1]} 0 GeV", f"/qsim/gun/p2 {P2[0]} {P2[1]} 0 GeV",
                                        "/qsim/gun/vertex 0 0 0 mm", "/run/initialize", "/run/beamOn 1"]) + "\n")
        env = dict(os.environ, LD_LIBRARY_PATH=f"{G.QP}/build/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
        subprocess.run([f"{G.QP}/build/quirksim/quirksim", "-m", mac, "-t", "1", "-o", root], env=env, stdout=open(f"{G.OUT}/{tag}.log", "w"),
                       stderr=subprocess.STDOUT, check=True)
        F = uproot.open(root); T = F["events"].arrays(library="np"); S = F["steps"].arrays(library="pd")
        hq, hl, ht = T["h_q"][0], T["h_layer"][0], 0.5 * (T["h_t0"][0] + T["h_t1"][0])
        t_g4 = {l: float(ht[(hq == 0) & (hl == l)].min()) for l in range(1, 5) if ((hq == 0) & (hl == l)).any()}
        S0 = S[S.q == 0]; rmax_g4 = float(S0.x.abs().max() / 10)                # turning point along the string (x), cm
        # old code, B = 0
        _, tr = simulate_quirk_hits((P1[0], P1[1], 0, E0), (P2[0], P2[1], 0, E0), M, lam, 0.0, -1.0, +1.0, np.random.default_rng(1), z0_cm=0.0, max_layer_r_cm=60.0)
        X = tr["x1"] * HBARC; t_old = {}
        for l, r in enumerate(RAD, 1):
            res = find_layer_crossing(X, tr["t_gev_inv"], r)
            if res is not None: t_old[l] = res[1]
        tn = tr["t_gev_inv"] * 6.582119569e-25 * 1e9; rmax_old = float(np.abs(X[tn < T_STOP_NS(lam, E0), 0]).max())   # same window as Geant4
        print(f"Lambda {lam_ev:g} eV, E0 - m = {E0 - M:.4f} GeV: turning radius exact {xmax:.4f} cm | Geant4 {rmax_g4:.4f} | old {rmax_old:.4f}")
        for l in range(1, 5):
            g, o = t_g4.get(l, np.nan), t_old.get(l, np.nan)
            print(f"   L{l} r = {RAD[l - 1]:6.3f} cm: t exact {t_ex[l]:.5f} ns | Geant4 {g:.5f} ({1e3 * (g - t_ex[l]):+.2f} ps) | old {o:.5f} ({1e3 * (o - t_ex[l]):+.2f} ps)")
            rows.append(dict(lam_ev=lam_ev, layer=l, t_exact_ns=t_ex[l], t_g4_ns=g, t_old_ns=o))
        rows.append(dict(lam_ev=lam_ev, layer=0, t_exact_ns=xmax, t_g4_ns=rmax_g4, t_old_ns=rmax_old))   # layer 0 row = turning radius (cm)
    pd.DataFrame(rows).to_csv(f"{G.OUT}/G04_exact_1d.csv", index=False); print("G04_EXIT=0")
