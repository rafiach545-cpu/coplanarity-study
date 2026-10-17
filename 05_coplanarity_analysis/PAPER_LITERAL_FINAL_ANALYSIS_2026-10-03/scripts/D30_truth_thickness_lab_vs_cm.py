#!/usr/bin/env python3
"""Truth plane thickness with the two string-direction conventions (2026-10-14), request of D-review item 3 (arXiv:2002.07503 Sec. VIII:
"choosing the correct s direction is critical in coplanar quirk search").
(a) our integrator: straight string with the separation at equal LAB time (quirk_trajectory_optimized_v2, 3000 steps per period);
(b) PreFASERQuirkSim step (driver scripts/external/D30_prefaser_driver_crossings.cxx): separation at equal CM time (2002.07503 Eq. VIII.1-4,
    1911.02223 Eq. III.6-9), dt = t1q / 3000.
Both: production at the origin, uniform B = 2 T, no material, the same momenta and charges (+-1). First outward crossing of each quirk with the
8 layer radii; plane fitted through the origin to the 16 points (smallest eigenvalue of T_ij, as Delta_s; no detector resolution).
Events: all 22 fiducial COL2000 events and the first 20 fiducial EW2000 events (by key). Driver binary: argv[1].
Output: tables/D30_truth_thickness_lab_vs_cm.csv"""
import os, sys, subprocess, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
DRV = sys.argv[1] if len(sys.argv) > 1 else "driver_cross"
def thick(X):
    X = np.asarray(X); w = np.linalg.eigvalsh(X.T @ X / (len(X) - 1)); return np.sqrt(max(w[0], 0))
def job(a):
    s, key, P1, P2, c1, c2, m, lam = a
    p4._init()
    for fac in (0.999, 0.9989, 0.9991, 0.99895, 0.99905):            # float-equality floor check, as D14
        p4.tth.MIN_STEPS_PER_PERIOD = fac * 3000
        try:
            _, tr = p4.tth.simulate_quirk_hits((*P1, np.sqrt(P1 @ P1 + m * m)), (*P2, np.sqrt(P2 @ P2 + m * m)), mass_gev=m, Lambda_gev=lam, B_tesla=2.0,
                                               charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=0.0, max_layer_r_cm=60.0, steps_per_period=3000)
            break
        except RuntimeError: tr = None
    if tr is None: return dict(sample=s, key=key, n_points=0)
    cr = [c for c in p18.all_crossings(tr) if c["order"] == 0]; A = {(c["quirk"], c["layer"]): (c["x"], c["y"], c["z_lab"]) for c in cr}
    o = subprocess.run([DRV, str(m), str(lam * 1e9), "2.0", *map(str, P1), *map(str, P2), "560000", "3000", str(int(c1)), str(int(c2))], capture_output=True, text=True).stdout
    B = {}
    for line in o.splitlines():
        q, L, x, y, z, t = line.split(); B[(int(q), int(L))] = (float(x) * 1e-4, float(y) * 1e-4, float(z) * 1e-4)
    common = sorted(set(A) & set(B))
    d = [np.linalg.norm(np.subtract(A[k], B[k])) * 1e4 for k in common]
    return dict(sample=s, key=key, n_points=len(common), ds_lab_um=thick([A[k] for k in common]) * 1e4, ds_cm_um=thick([B[k] for k in common]) * 1e4,
                max_point_shift_um=max(d), median_point_shift_um=float(np.median(d)))
if __name__ == "__main__":
    acc = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); acc = acc[(acc.geom == "B") & (acc.bs == "CV") & (acc.sct == "Z0") & (acc.fid.astype(str) == "True")]
    jobs = []
    for s, nmax in (("COL2000", 99), ("EW2000", 20)):
        m, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]; M = p4.momenta(s)
        for k in sorted(acc[acc["sample"] == s].key.astype(int))[:nmax]:
            r = M.iloc[k]; jobs.append((s, k, np.array([r.px1, r.py1, r.pz1]), np.array([r.px2, r.py2, r.pz2]), float(r.charge1), float(r.charge2), m, lam))
    with mp.Pool(int(os.environ.get("NWORKERS", 3))) as pool: rows = list(pool.imap_unordered(job, jobs))
    d = pd.DataFrame(rows).sort_values(["sample", "key"]); d.to_csv(f"{T}/D30_truth_thickness_lab_vs_cm.csv", index=False)
    for s, x in d.groupby("sample"):
        print(f"{s}: {len(x)} events | truth thickness median: lab-time string {x.ds_lab_um.median():.2f} um, CM-time string {x.ds_cm_um.median():.2f} um | "
              f"median |ratio-1| {np.median(np.abs(x.ds_cm_um / x.ds_lab_um - 1)):.3f} | crossing points: median shift {x.median_point_shift_um.median():.2f} um, max {x.max_point_shift_um.max():.1f} um")
