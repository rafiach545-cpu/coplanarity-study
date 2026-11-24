#!/usr/bin/env python3
"""09 / G16 (2026-11-24): isolate the G15 discrepancy of the Geant4 eq3 model (1.3 cm at 4 keV with slice 0.1 / 1 ns, fine at 0.01 ns).
(a) the pair solver alone: numba DOP853 (quirk_trajectory_dop853) vs the C++ solver (eq3_dop853_cli, the code inside Geant4) for G01 event 0,
    Lambda = 4 keV, B = 2 T, t <= 25.05 ns, no radii, ncoarse 64: bitwise check, max pair separation AT EQUAL TIMES, the first layer crossings;
(c) the Geant4 eq3 run of the same event (slice 0.1 ns, step tree written): distance of every Geant4 step end point and of every hit entry point
    from the reference trajectory at the same time t (x_ref(t) by interpolation of the dense C++ output, ncoarse 256) -> replay error alone;
    the hits are where G4PropagatorInField located the boundary.
(b) is printed by the Geant4 run itself (QUIRK_EQ3_DEBUG counters). Usage (env g4): G16_eq3_replay_debug.py <g4 steps root> <g4 log>"""
import os, sys, struct, subprocess, tempfile, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [f"{BASE}/03_trajectory_sim", f"{BASE}/04_detector_sim"]
import quirk_trajectory_dop853 as Q                                   # noqa: E402
from atlas_geometry import LAYERS                                     # noqa: E402
CLI = os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix", "quirkcore", "test", "eq3_dop853_cli")
CM, NS = Q.CM, Q.NS; M = 800.0; LAM = 4e-6; TSTOP = 25.05
CALLS = []; _orig = Q._integrate
Q._integrate = lambda *a: (CALLS.append(a), _orig(*a))[1]


def cpp(a, ncoarse=None):
    a = list(a)
    if ncoarse: a[11] = ncoarse
    y0, t_end, mass, q1, q2, L2, Bz, rtol, atol, R2n, Zn, nc, nf, mo = a[:14]
    v = [*y0, t_end, mass, q1, q2, L2, Bz, rtol, *atol, len(R2n), *R2n, len(Zn), *Zn, nc, nf, mo]
    with tempfile.TemporaryDirectory() as d:
        open(f"{d}/i", "wb").write(struct.pack(f"{len(v)}d", *map(float, v))); subprocess.run([CLI, f"{d}/i", f"{d}/o"], check=True)
        b = np.fromfile(f"{d}/o", dtype=np.float64)
    n = int(b[4]); return b[5:5 + n], b[5 + n:5 + 13 * n].reshape(n, 12), [int(x) for x in b[:4]]


r = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").iloc[0]
Q.RADII_CM = None; Q.NCOARSE = 64; Q.T_STOP_NS = TSTOP
tr = Q.integrate_trajectory_dop853(np.zeros(3), np.array([r.px1, r.py1, r.pz1]), np.zeros(3), np.array([r.px2, r.py2, r.pz2]), M, 1.0, -1.0, LAM, 2.0, 1e30)
a = CALLS[-1]; Tn = tr["t_gev_inv"]; Yn = np.hstack([tr["x1"], tr["p1"], tr["x2"], tr["p2"]])
Tc, Yc, st = cpp(a)
print("(a) numba vs C++ solver: points", len(Tn), len(Tc), "| bitwise identical:", bool(len(Tn) == len(Tc) and np.array_equal(Tn, Tc) and np.array_equal(Yn, Yc)),
      "| status/nacc/nrej/nfev C++", st)
sep = np.linalg.norm(Yc[:, 0:3] - Yc[:, 6:9], axis=1) * CM * 10
print(f"    max pair separation at equal times: {sep.max():.4f} mm (G4 eq3 log 21.43 mm, Athena 7.96 mm: quirksim's maxSep is NOT at equal times, Actions.cc:340)")
R = [l["r_cm"] for l in LAYERS]
for k, (nm, X) in enumerate((("x1 (charge +1, G4 h_q 1)", Yc[:, 0:3]), ("x2 (charge -1, G4 h_q 0)", Yc[:, 6:9]))):
    rr = np.hypot(X[:, 0], X[:, 1]) * CM; cr = []
    for Ri in R:
        w = np.nonzero((rr[:-1] < Ri) & (rr[1:] >= Ri))[0]
        cr.append(f"{Tc[w[0]] * NS:.4f}" if len(w) else "-")
    print(f"    first crossing time (ns) per layer, {nm}: {cr}")
# (c) replay error
if len(sys.argv) > 2:
    import uproot
    Td, Yd, _ = cpp(a, ncoarse=256); td = Td * NS
    def xref(t, slot):                                               # reference position (mm) at lab time t (ns), slot 0 = x1, 1 = x2
        return np.stack([np.interp(t, td, Yd[:, 6 * slot + j]) for j in range(3)], 1) * CM * 10
    F = uproot.open(sys.argv[1]); S = F["steps"].arrays(library="np"); E = F["events"].arrays(library="np")
    slot = {0: 1, 1: 0}                                              # G4 q 0 = positive PDG = charge -1 = x2 (slot 1)
    rows = []
    for q in (0, 1):
        m = S["q"] == q; t = S["t"][m]; X = np.stack([S["x"][m], S["y"][m], S["z"][m]], 1); k = t <= TSTOP
        d = np.linalg.norm(X[k] - xref(t[k], slot[q]), axis=1) * 1e3
        rows.append(dict(what=f"step end points q{q}", n=int(k.sum()), med_um=np.median(d), max_um=d.max()))
    hq, ht = E["h_q"][0], E["h_t0"][0]; HX = np.stack([E["h_x0"][0], E["h_y0"][0], E["h_z0"][0]], 1)
    for q in (0, 1):
        m = (hq == q) & (ht <= TSTOP)
        if m.sum():
            d = np.linalg.norm(HX[m] - xref(ht[m], slot[q]), axis=1) * 1e3
            rows.append(dict(what=f"hit entry points q{q}", n=int(m.sum()), med_um=np.median(d), max_um=d.max()))
    # step lengths of the Geant4 steps, against the oscillation
    for q in (0, 1):
        m = S["q"] == q; X = np.stack([S["x"][m], S["y"][m], S["z"][m]], 1); L = np.linalg.norm(np.diff(X, axis=0), axis=1)
        rows.append(dict(what=f"G4 chord length q{q} (mm)", n=len(L), med_um=np.median(L) * 1e3, max_um=L.max() * 1e3))
    print("(c) Geant4 eq3 points vs the reference trajectory at the same time (um; last rows: chord lengths in um)")
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:.4g}"))
