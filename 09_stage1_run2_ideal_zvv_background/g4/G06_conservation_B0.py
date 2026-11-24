#!/usr/bin/env python3
"""09 / Geant4 step G06 (2026-11-22): energy and angular-momentum conservation at B = 0, Eq. 3 (old integrator) vs Athena (QuirkPheno), for
general angles (v not along the string). Same 20 EW pairs (m = 800 GeV), both quirks from the origin, B = 0, t <= T_NS.

Quantities at equal lab times t (Geant4 tracks the two quirks separately, so both trajectories are interpolated to one time grid):
  E_naive = gamma1 m + gamma2 m + T d                         (straight string at rest; the quantity asked for)
  E_NG    = gamma1 m + gamma2 m + T * int_0^d gamma_perp(s) ds (straight Nambu-Goto string whose points move with the linear interpolation
                                                               of the end-point velocities; gamma_perp from the velocity component normal to it)
  L_naive = x1 x p1 + x2 x p2 (about the origin);  L_NG = L_naive + T * int x(s) x gamma_perp v_perp(s) ds
T = Lambda^2 (natural units). Reported: the largest |E(t) - E(0)| over the window, in GeV and as a fraction of Q = E(0) - 2m (the energy the
string can take), and |L(t) - L(0)| relative to the largest |x1 x p1| + |x2 x p2| in the window. v_perp,max is the largest end-point speed
normal to the string (so 'v not along the string' is shown, not assumed).

Discretisation checks: old code at dt, dt/2, dt/4; Geant4 at maxBoost 0.1 (QuirkPheno default), 0.01 (Athena default) and 0.001. Geant4 uses the patched copy
(QUIRKPHENO_FIX) with DeltaIntersection = 1 nm (G05); at B = 0 the second-order field option has no effect.
Run in env g4 (conda activate g4). Output: out_G01/G06_conservation.csv."""
import os, sys, subprocess, argparse, numpy as np, pandas as pd, uproot
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [f"{BASE}/03_trajectory_sim"]
from quirk_trajectory_numba import integrate_trajectory_numba     # noqa: E402
QPFIX = os.environ.get("QUIRKPHENO_FIX", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix")) + "/build"
OUT = f"{HERE}/out_G01/G06"; os.makedirs(OUT, exist_ok=True)
HBARC_CM, HBAR_NS = 1.973269804e-14, 6.582119569e-16      # GeV cm, GeV ns
MQ = 800.0; T_NS = 1.0; NGRID = 3000; NSIG = 65


def string_terms(x1, x2, v1, v2, T):
    """Straight-string energy, momentum and angular momentum (Nambu-Goto, linear velocity interpolation). Arrays (n, 3), natural units."""
    s = np.linspace(0.0, 1.0, NSIG); w = np.full(NSIG, 1.0 / (NSIG - 1)); w[[0, -1]] *= 0.5        # trapezoid in the fraction along the string
    sep = x1 - x2; d = np.linalg.norm(sep, axis=1); n = sep / np.maximum(d, 1e-300)[:, None]
    E = np.zeros(len(d)); P = np.zeros_like(x1); L = np.zeros_like(x1)
    for sk, wk in zip(s, w):
        x = x2 + sk * sep; v = v2 + sk * (v1 - v2); vp = v - np.sum(v * n, axis=1)[:, None] * n
        g = 1.0 / np.sqrt(np.maximum(1.0 - np.sum(vp * vp, axis=1), 1e-12))
        E += wk * g * d; P += wk * (g * d)[:, None] * vp; L += wk * d[:, None] * np.cross(x, g[:, None] * vp)
    return T * E, T * P, T * L, d


def quantities(t, x1, p1, x2, p2, lam_gev):
    T = lam_gev ** 2; E1 = np.sqrt(np.sum(p1 * p1, 1) + MQ ** 2); E2 = np.sqrt(np.sum(p2 * p2, 1) + MQ ** 2)
    v1, v2 = p1 / E1[:, None], p2 / E2[:, None]
    Es, Ps, Ls, d = string_terms(x1, x2, v1, v2, T)
    n = (x1 - x2) / np.maximum(d, 1e-300)[:, None]
    vperp = np.maximum(np.linalg.norm(v1 - np.sum(v1 * n, 1)[:, None] * n, axis=1), np.linalg.norm(v2 - np.sum(v2 * n, 1)[:, None] * n, axis=1))
    Ekin = E1 + E2; Lq = np.cross(x1, p1) + np.cross(x2, p2)
    scaleL = np.max(np.linalg.norm(np.cross(x1, p1), axis=1) + np.linalg.norm(np.cross(x2, p2), axis=1))
    k = d > 0     # string direction defined
    Q = Ekin[0] + T * d[0] - 2 * MQ
    out = dict(Q_GeV=Q, vperp_max=float(vperp[k].max()), d_max_cm=float(d.max() * HBARC_CM), t_end_ns=float(t[-1] * HBAR_NS))
    for name, E in (("naive", Ekin + T * d), ("NG", Ekin + Es)):
        dE = np.abs(E - E[0]).max(); out[f"dE_{name}_GeV"] = dE; out[f"dE_{name}_over_Q"] = dE / Q
    for name, L in (("naive", Lq), ("NG", Lq + Ls)):
        out[f"dL_{name}_rel"] = np.linalg.norm(L - L[0], axis=1).max() / scaleL
    out["dP_NG_rel"] = np.linalg.norm(p1 + p2 + Ps - (p1 + p2 + Ps)[0], axis=1).max() / np.linalg.norm(p1[0] - p2[0])
    return out


def run_old(args):
    k, r, lam_ev, dt_scale = args
    lam = lam_ev * 1e-9; p1 = np.array([r["px1"], r["py1"], r["pz1"]]); p2 = np.array([r["px2"], r["py2"], r["pz2"]])
    tmax = T_NS / HBAR_NS
    E1 = np.sqrt(p1 @ p1 + MQ ** 2); E2 = np.sqrt(p2 @ p2 + MQ ** 2); Q = E1 + E2 - 2 * MQ
    dt = min(tmax / 2e5, Q / lam ** 2 / 2000.0) * dt_scale     # Q / T = largest string length: >= ~4000 steps per oscillation period
    try:
        tr = integrate_trajectory_numba(np.zeros(3), p1, np.zeros(3), p2, MQ, +1.0, -1.0, lam, 0.0, tmax, dt)
    except RuntimeError as e:
        return dict(code="Eq3_old", ev=k, lam_ev=lam_ev, setting=f"dt x{dt_scale:g}", error=str(e)[:80])
    t = tr["t_gev_inv"]; g = np.linspace(0, t[-1], NGRID); I = lambda a: np.stack([np.interp(g, t, a[:, j]) for j in range(3)], 1)
    q = quantities(g, I(tr["x1"]), I(tr["p1"]), I(tr["x2"]), I(tr["p2"]), lam)
    return dict(code="Eq3_old", ev=k, lam_ev=lam_ev, setting=f"dt x{dt_scale:g}", n_steps=len(t), **q)


def card():
    path = f"{OUT}/vacuum_B0.card"
    s = open(f"{HERE}/ideal8_vacuum.card").read().replace("field 2.0 0 100 0 400", "field 0.0 0 100 0 400"); open(path, "w").write(s); return path


def run_g4(args):
    k, r, lam_ev, maxboost = args
    tag = f"{OUT}/g4_L{lam_ev:g}_mb{maxboost:g}_e{k:02d}"
    if not os.path.exists(tag + ".root"):
        M = ["/qsim/field/deltaIntersection 1e-6 mm", f"/quirk/maxBoost {maxboost}", f"/quirk/mass {MQ} GeV", f"/quirk/lambda {lam_ev} eV",
             f"/qsim/card {card()}", "/qsim/gen/mode gun", "/qsim/killSecondaries true", "/qsim/out/towers false", "/qsim/out/stepPrescale 1",
             f"/qsim/maxTime {T_NS} ns", f"/qsim/gun/p1 {r['px2']} {r['py2']} {r['pz2']} GeV", f"/qsim/gun/p2 {r['px1']} {r['py1']} {r['pz1']} GeV",
             "/qsim/gun/vertex 0 0 0 mm", "/run/initialize", "/run/beamOn 1"]
        open(tag + ".mac", "w").write("\n".join(M) + "\n")
        env = dict(os.environ, LD_LIBRARY_PATH=f"{QPFIX}/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
        with open(tag + ".log", "w") as lg:
            subprocess.run([f"{QPFIX}/quirksim/quirksim", "-m", tag + ".mac", "-t", "1", "-s", "7", "-o", tag + ".root"], env=env, stdout=lg, stderr=subprocess.STDOUT, check=True)
    S = uproot.open(tag + ".root")["steps"].arrays(library="pd")
    # quirk 0 = positive PDG = CSV particle 2 (charge -1); quirk 1 = CSV particle 1. Geant4 units: mm, ns, MeV.
    tr = {}
    for q, key in ((1, "1"), (0, "2")):
        s = S[S.q == q].sort_values("step")
        t = np.r_[0.0, s.t.to_numpy()]
        p0 = np.array([r[f"px{key}"], r[f"py{key}"], r[f"pz{key}"]])
        x = np.vstack([np.zeros(3), s[["x", "y", "z"]].to_numpy() * 0.1 / HBARC_CM])        # mm -> GeV^-1
        p = np.vstack([s[["px", "py", "pz"]].to_numpy()[0] * 1e-3, s[["px", "py", "pz"]].to_numpy() * 1e-3])  # first point: Geant4's own start momentum
        tr[key] = (t / HBAR_NS, x, p)
    tend = min(tr["1"][0][-1], tr["2"][0][-1]); g = np.linspace(0, tend, NGRID)
    I = lambda tt, a: np.stack([np.interp(g, tt, a[:, j]) for j in range(3)], 1)
    q = quantities(g, I(tr["1"][0], tr["1"][1]), I(tr["1"][0], tr["1"][2]), I(tr["2"][0], tr["2"][1]), I(tr["2"][0], tr["2"][2]), lam_ev * 1e-9)
    return dict(code="Athena_g4", ev=k, lam_ev=lam_ev, setting=f"maxBoost {maxboost:g}", n_steps=int(len(S)), **q)


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--nev", type=int, default=20); a.add_argument("--lambdas", default="100,1000,4000"); A = a.parse_args()
    ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(A.nev)
    lams = [float(x) for x in A.lambdas.split(",")]
    jobs_old = [(k, r._asdict(), l, s) for l in lams for s in (1.0, 0.5, 0.25) for k, r in enumerate(ev.itertuples())]
    jobs_g4 = [(k, r._asdict(), l, mb) for l in lams for mb in (0.1, 0.01, 0.001) for k, r in enumerate(ev.itertuples())]
    with Pool(8) as P: R = P.map(run_old, jobs_old) + P.map(run_g4, jobs_g4)
    D = pd.DataFrame(R); D.to_csv(f"{OUT}/../G06_conservation.csv", index=False)
    cols = ["vperp_max", "dE_naive_over_Q", "dE_NG_over_Q", "dL_naive_rel", "dL_NG_rel", "dP_NG_rel"]
    print(f"B = 0, m = {MQ:g} GeV, t <= {T_NS:g} ns, 20 pairs; medians [max] over events")
    for (lam, code, st), g in D.dropna(subset=["dE_naive_GeV"]).groupby(["lam_ev", "code", "setting"]):
        print(f" L={lam:>5g} eV {code:9s} {st:13s} n={len(g):2d} " + "  ".join(f"{c} {g[c].median():.2e} [{g[c].max():.2e}]" for c in cols))
    print("G06_EXIT=0")
