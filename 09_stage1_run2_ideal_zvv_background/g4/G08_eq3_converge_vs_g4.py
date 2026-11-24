#!/usr/bin/env python3
"""09 / step G08 (2026-11-22): does Eq. 3 converge to Geant4 (Athena) or to a ~100 um residual?  4 EW pairs (events 0-3 of
ew_quirk_pair_momenta_800gev_4kev.csv), m = 800 GeV, Lambda = 4 keV, B = 2 T, both quirks from the origin, t <= 5 ns.
Mode 'eq3' (env f6fast, scipy): Eq. 3 positions on a 4000-point time grid from
   RK4 (quirk_trajectory_numba._rhs, streamed in segments) at dt, dt/4, dt/16, dt/64 with dt = Q/T/2000 (G06 convention), and
   DOP853 (scipy solve_ivp) at rtol = 1e-12 and 1e-13 (independent, error-controlled reference).
Mode 'g4' (env g4, uproot): Geant4 with the patched QuirkPheno_fix (second-order field, DeltaIntersection 1 nm), maxBoost 0.01 and 0.001,
   interpolated on the same grid, then the table of max |x_a - x_b| over the grid and both quirks (um).
Output: out_G01/G08/eq3_e<k>.npz, out_G01/G08_table.csv."""
import os, sys, subprocess, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
OUT = f"{HERE}/out_G01/G08"; os.makedirs(OUT, exist_ok=True)
HB, HN = 1.973269804e-14, 6.582119569e-16; TNS = 5.0; LAM = 4000.0; B = 2.0; M = 800.0; NEV = 4
GRID = np.linspace(0.0, TNS * 0.999, 4000)                     # ns
QF = os.environ.get("QUIRKPHENO_FIX", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix")) + "/build"
ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(NEV)


def eq3(k):
    sys.path[:0] = [f"{BASE}/03_trajectory_sim", HERE]
    from quirk_trajectory_numba import _rhs, TESLA_TO_GEV2
    from G07_dt_impact import _seg
    from scipy.integrate import solve_ivp
    r = ev.iloc[k]; p1 = np.array([r.px1, r.py1, r.pz1]); p2 = np.array([r.px2, r.py2, r.pz2]); L = LAM * 1e-9
    q1, q2, Bz = 0.30282212, -0.30282212, B * TESLA_TO_GEV2; tmax = TNS / HN; tg = GRID / HN
    E = np.sqrt(p1 @ p1 + M * M) + np.sqrt(p2 @ p2 + M * M) - 2 * M; dt0 = min(tmax / 2e5, E / L ** 2 / 2000)
    res = {}
    for f in (1, 4, 16, 64):
        s = np.r_[0, 0, 0, p1, 0, 0, 0, p2].astype(float); t = 0.0; X = np.zeros((len(tg), 6)); j = 0
        while t < tmax and j < len(tg):
            ts, XX, t = _seg(s, t, M, q1, q2, L * L, Bz, dt0 / f, 2_000_000, tmax)
            m = (tg >= ts[0]) & (tg <= ts[-1])
            for c in range(6): X[m, c] = np.interp(tg[m], ts, XX[:, c])
            j = np.nonzero(m)[0].max() + 1 if m.any() else j
        res[f"rk4_dt{f}"] = X * HB
    out = np.zeros(12)
    def rhs(t, y): _rhs(y, M, q1, q2, L * L, Bz, out); return out.copy()
    atol = np.r_[[1e-7 / HB] * 3, [1e-10] * 3, [1e-7 / HB] * 3, [1e-10] * 3]   # 1 nm, 1e-10 GeV
    for rt in (1e-12, 1e-13):
        S = solve_ivp(rhs, (0, tmax), np.r_[0, 0, 0, p1, 0, 0, 0, p2].astype(float), method="DOP853", rtol=rt, atol=atol, t_eval=tg)
        res[f"dop853_rtol{rt:g}"] = np.c_[S.y[0:3].T, S.y[6:9].T] * HB; res[f"dop853_rtol{rt:g}_nfev"] = np.array([S.nfev])
    np.savez(f"{OUT}/eq3_e{k}.npz", **res); print(k, "eq3 done", {kk: v.shape for kk, v in res.items()}, flush=True)


def g4(k, mb):
    import uproot
    r = ev.iloc[k]; tag = f"{OUT}/g4_mb{mb}_e{k}"
    if not os.path.exists(tag + ".npy"):
        Mc = ["/quirk/secondOrderField true", "/qsim/field/deltaIntersection 1e-6 mm", f"/quirk/maxBoost {mb}", f"/quirk/mass {M} GeV", f"/quirk/lambda {LAM} eV",
              f"/qsim/card {HERE}/ideal8_vacuum.card", "/qsim/gen/mode gun", "/qsim/killSecondaries true", "/qsim/out/towers false", "/qsim/out/stepPrescale 1",
              f"/qsim/maxTime {TNS} ns", f"/qsim/gun/p1 {r.px2} {r.py2} {r.pz2} GeV", f"/qsim/gun/p2 {r.px1} {r.py1} {r.pz1} GeV", "/qsim/gun/vertex 0 0 0 mm",
              "/run/initialize", "/run/beamOn 1"]
        open(tag + ".mac", "w").write("\n".join(Mc) + "\n")
        env = dict(os.environ, LD_LIBRARY_PATH=f"{QF}/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
        subprocess.run([f"{QF}/quirksim/quirksim", "-m", tag + ".mac", "-t", "1", "-s", "7", "-o", tag + ".root"], env=env, stdout=open(tag + ".log", "w"), stderr=subprocess.STDOUT, check=True)
        S = uproot.open(tag + ".root")["steps"].arrays(library="pd"); X = np.zeros((len(GRID), 6))
        for q, c0 in ((1, 0), (0, 3)):                              # Geant4 quirk 1 = CSV particle 1 (x1), quirk 0 = particle 2 (x2)
            s = S[S.q == q].sort_values("step"); t = np.r_[0.0, s.t.to_numpy()]; xx = np.vstack([np.zeros(3), s[["x", "y", "z"]].to_numpy() * 0.1])
            for c in range(3): X[:, c0 + c] = np.interp(GRID, t, xx[:, c])
        np.save(tag + ".npy", X); os.remove(tag + ".root")
    return np.load(tag + ".npy")


if __name__ == "__main__":
    if sys.argv[1] == "eq3":
        for k in range(NEV): eq3(k)
    else:
        rows = []
        for k in range(NEV):
            E = dict(np.load(f"{OUT}/eq3_e{k}.npz")); G = {f"g4_mb{mb}": g4(k, mb) for mb in (0.01, 0.001)}
            A = {**{kk: v for kk, v in E.items() if not kk.endswith("nfev")}, **G}
            d = lambda a, b: float(np.max(np.linalg.norm((A[a] - A[b]).reshape(-1, 2, 3), axis=2)) * 1e4)
            ref = "dop853_rtol1e-13"
            row = dict(ev=k, dop_rtol12_vs_13=d("dop853_rtol1e-12", ref), g4_mb01_vs_001=d("g4_mb0.01", "g4_mb0.001"),
                       nfev_dop13=int(E["dop853_rtol1e-13_nfev"][0]))
            for f in (1, 4, 16, 64): row[f"rk4_dt{f}_vs_dop"] = d(f"rk4_dt{f}", ref)
            row["g4_vs_dop"] = d("g4_mb0.001", ref)
            for f in (1, 4, 16, 64): row[f"g4_vs_rk4_dt{f}"] = d("g4_mb0.001", f"rk4_dt{f}")
            rows.append(row)
        D = pd.DataFrame(rows); D.to_csv(f"{OUT}/../G08_table.csv", index=False)
        pd.set_option("display.width", 250); print(D.round(2).to_string(index=False)); print("G08_EXIT=0")
