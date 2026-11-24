#!/usr/bin/env python3
"""09 / G14 (2026-11-24): the C++ DOP853 for Eq. 3 (hep_tools/QuirkPheno_fix/quirkcore/src/QuirkEq3Dop853.cc, step 1 of G4_EQ3_DESIGN.md)
against the numba DOP853 (03_trajectory_sim/quirk_trajectory_dop853._integrate) on the G09 validation cases, at rtol 1e-10 and 1e-11:
  (A) helix: Lambda = 0, B = 2 T, 20 EW pairs, crossing refinement on the 8 radii;
  (B) exact 1D string: B = 0, back-to-back along x, Lambda = 1 and 4 keV, refinement on L1-L4; and the no-radii run with ncoarse 256;
  (C) B = 0 conservation: 20 pairs, Lambda = 0.1, 1, 4 keV, t <= 1 ns, no radii, ncoarse 8;
  (D) the 4 G08 events: Lambda = 4 keV, B = 2 T, t <= 5 ns, no radii, ncoarse 64.
The inputs are exactly those G09 passes to _integrate (recorded by wrapping it; G09_dop853_validation.py itself is not run, it would rewrite
its table). Per call: same number of output points, same accepted / rejected steps and function evaluations, and the largest difference over
all points of t (relative), positions (|dx| in cm and relative to the largest |x|) and momenta (relative to the largest |p|). Pass: every
relative difference <= 1e-10 and identical step counts. Output: out_G01/G14_cpp_vs_numba.csv. Usage (env f6fast or g4):
G14_cpp_dop853_vs_numba.py [--cli PATH]"""
import os, sys, struct, argparse, subprocess, tempfile, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [f"{BASE}/03_trajectory_sim", f"{BASE}/04_detector_sim"]
import quirk_trajectory_dop853 as Q                                   # noqa: E402
from atlas_geometry import LAYERS                                     # noqa: E402
CLI = os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix", "quirkcore", "test", "eq3_dop853_cli")
CM, NS = Q.CM, Q.NS; M = 800.0; RAD = [l["r_cm"] for l in LAYERS]
CALLS = []; _orig = Q._integrate


def _rec(*a):
    out = _orig(*a); CALLS.append((a, out)); return out


Q._integrate = _rec


def setrt(rt):
    Q.RTOL = rt; Q.ATOL_X = 1e-7 / CM * rt / 1e-10; Q.ATOL_P = 1e-10 * rt / 1e-10


def run(p1, p2, lam, B, tmax, c1=1.0, c2=-1.0, radii=None, ncoarse=8):    # as G09 run()
    Q.RADII_CM = radii; Q.NCOARSE = ncoarse
    Q.integrate_trajectory_dop853(np.zeros(3), np.array(p1, float), np.zeros(3), np.array(p2, float), M, c1, c2, lam, B, tmax)


def cpp(a):
    y0, t_end, mass, q1, q2, L2, Bz, rtol, atol, R2n, Zn, ncoarse, nfine, max_out = a[:14]
    v = [*y0, t_end, mass, q1, q2, L2, Bz, rtol, *atol, len(R2n), *R2n, len(Zn), *Zn, ncoarse, nfine, max_out]
    with tempfile.TemporaryDirectory() as d:
        open(f"{d}/in.bin", "wb").write(struct.pack(f"{len(v)}d", *map(float, v)))
        subprocess.run([CLI, f"{d}/in.bin", f"{d}/out.bin"], check=True)
        b = np.fromfile(f"{d}/out.bin", dtype=np.float64)
    st, na, nr, nf, n = (int(x) for x in b[:5]); T = b[5:5 + n]; Y = b[5 + n:5 + n + 12 * n].reshape(n, 12)
    return T, Y, st, na, nr, nf


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--cli", default=CLI); A = ap.parse_args(); CLI = A.cli
    ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(20)
    rows = []
    for rt in (1e-10, 1e-11):
        setrt(rt)
        cases = []
        for k, r in ev.iterrows():                                        # (A)
            p1, p2 = (r.px1, r.py1, r.pz1), (r.px2, r.py2, r.pz2)
            bt = min(np.hypot(*p1[:2]) / np.sqrt(np.dot(p1, p1) + M * M), np.hypot(*p2[:2]) / np.sqrt(np.dot(p2, p2) + M * M))
            cases.append((f"A helix ev{k}", lambda p1=p1, p2=p2, bt=bt: run(p1, p2, 0.0, 2.0, 60.0 * 3 / CM / bt, radii=RAD)))
        for lam_ev in (1000.0, 4000.0):                                   # (B)
            lam = lam_ev * 1e-9; s = lam ** 2 / CM; E0 = M + 20.0 * s; p0 = np.sqrt(E0 ** 2 - M ** 2); tmax = 1.5 * p0 / lam ** 2
            cases.append((f"B 1D L={lam_ev:g} eV radii", lambda p0=p0, lam=lam, tmax=tmax: run((p0, 0, 0), (-p0, 0, 0), lam, 0.0, tmax, radii=RAD[:4])))
            cases.append((f"B 1D L={lam_ev:g} eV ncoarse256", lambda p0=p0, lam=lam, tmax=tmax: run((p0, 0, 0), (-p0, 0, 0), lam, 0.0, tmax, radii=None, ncoarse=256)))
        for lam_ev in (100.0, 1000.0, 4000.0):                            # (C)
            for k, r in ev.iterrows():
                cases.append((f"C B=0 L={lam_ev:g} eV ev{k}", lambda r=r, lam_ev=lam_ev: run((r.px1, r.py1, r.pz1), (r.px2, r.py2, r.pz2), lam_ev * 1e-9, 0.0, 1.0 / NS, radii=None, ncoarse=8)))
        for k in range(4):                                                # (D)
            r = ev.iloc[k]
            cases.append((f"D G08 ev{k}", lambda r=r: run((r.px1, r.py1, r.pz1), (r.px2, r.py2, r.pz2), 4e-6, 2.0, 5.0 / NS, radii=None, ncoarse=64)))
        for name, fn in cases:
            CALLS.clear(); fn(); (a, (Tn, Yn, stn, nan, nrn, nfn)), = CALLS
            Tc, Yc, stc, nac, nrc, nfc = cpp(a)
            same_n = len(Tn) == len(Tc); row = dict(rtol=rt, case=name, n_numba=len(Tn), n_cpp=len(Tc), status=(stn, stc), steps_numba=(nan, nrn, nfn), steps_cpp=(nac, nrc, nfc),
                                                     same_counts=same_n and (nan, nrn, nfn) == (nac, nrc, nfc) and stn == stc)
            if same_n:
                X = np.r_[Yn[:, 0:3], Yn[:, 6:9]]; P = np.r_[Yn[:, 3:6], Yn[:, 9:12]]
                dX = np.r_[Yc[:, 0:3] - Yn[:, 0:3], Yc[:, 6:9] - Yn[:, 6:9]]; dP = np.r_[Yc[:, 3:6] - Yn[:, 3:6], Yc[:, 9:12] - Yn[:, 9:12]]
                row.update(dt_rel=float(np.max(np.abs(Tc - Tn)) / max(np.max(np.abs(Tn)), 1e-300)), dx_cm=float(np.max(np.abs(dX)) * CM),
                           dx_rel=float(np.max(np.abs(dX)) / max(np.max(np.abs(X)), 1e-300)), dp_rel=float(np.max(np.abs(dP)) / max(np.max(np.abs(P)), 1e-300)),
                           bitwise=bool(np.array_equal(Tc, Tn) and np.array_equal(Yc, Yn)))
            row["pass"] = bool(row["same_counts"] and same_n and max(row["dt_rel"], row["dx_rel"], row["dp_rel"]) <= 1e-10)
            rows.append(row)
    T = pd.DataFrame(rows); T.to_csv(f"{HERE}/out_G01/G14_cpp_vs_numba.csv", index=False)
    T["group"] = T.case.str.split(" ").str[0]
    S = T.groupby(["rtol", "group"]).agg(cases=("case", "size"), passed=("pass", "sum"), bitwise=("bitwise", "sum"), same_counts=("same_counts", "sum"),
                                          max_dt_rel=("dt_rel", "max"), max_dx_cm=("dx_cm", "max"), max_dx_rel=("dx_rel", "max"), max_dp_rel=("dp_rel", "max")).reset_index()
    pd.set_option("display.width", 200); print(S.to_string(index=False, float_format=lambda v: f"{v:.3g}"))
    print(f"ALL PASS: {bool(T['pass'].all())} ({int(T['pass'].sum())}/{len(T)}); bitwise identical: {int(T.bitwise.sum())}/{len(T)}")
    print("G14_EXIT=0" if T["pass"].all() else "G14_EXIT=1")
