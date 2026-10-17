#!/usr/bin/env python3
"""Convergence control for D30 (2026-10-14): truth plane thickness of 5 EW2000 fiducial events (keys 2, 4, 29, 46, 57) versus step size:
our integrator (lab-time string) at 1500 / 3000 / 6000 steps per period; PreFASER step (CM-time string) at divStep 3000 / 30000.
If each code converges to its own value, the difference is the string-direction convention; if they approach each other, it is numerical.
Output: tables/D31_thickness_convergence.csv"""
import os, sys, subprocess, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
DRV = sys.argv[1]
def thick(X):
    X = np.asarray(X); return np.sqrt(max(np.linalg.eigvalsh(X.T @ X / (len(X) - 1))[0], 0)) * 1e4
def ours(P1, P2, c1, c2, m, lam, n):
    p4._init()
    for fac in (0.999, 0.9989, 0.9991, 0.99895, 0.99905):
        p4.tth.MIN_STEPS_PER_PERIOD = fac * n
        try:
            _, tr = p4.tth.simulate_quirk_hits((*P1, np.sqrt(P1 @ P1 + m * m)), (*P2, np.sqrt(P2 @ P2 + m * m)), mass_gev=m, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2,
                                               rng=np.random.default_rng(0), z0_cm=0.0, max_layer_r_cm=60.0, steps_per_period=n)
            return thick([(c["x"], c["y"], c["z_lab"]) for c in p18.all_crossings(tr) if c["order"] == 0])
        except RuntimeError: continue
    return np.nan
def theirs(P1, P2, c1, c2, m, lam, div):
    o = subprocess.run([DRV, str(m), str(lam * 1e9), "2.0", *map(str, P1), *map(str, P2), "560000", str(div), str(int(c1)), str(int(c2))], capture_output=True, text=True).stdout
    return thick([[float(v) * 1e-4 for v in l.split()[2:5]] for l in o.splitlines()])
def job(a):
    key, P1, P2, c1, c2, m, lam = a
    return dict(key=key, **{f"lab_{n}": ours(P1, P2, c1, c2, m, lam, n) for n in (1500, 3000, 6000)}, **{f"cm_div{d}": theirs(P1, P2, c1, c2, m, lam, d) for d in (3000, 30000)})
if __name__ == "__main__":
    m, lam = p4.PAR["EW"]; M = p4.momenta("EW2000"); jobs = []
    for k in (2, 4, 29, 46, 57):
        r = M.iloc[k]; jobs.append((k, np.array([r.px1, r.py1, r.pz1]), np.array([r.px2, r.py2, r.pz2]), float(r.charge1), float(r.charge2), m, lam))
    with mp.Pool(3) as pool: d = pd.DataFrame(list(pool.imap_unordered(job, jobs))).sort_values("key")
    d.to_csv(f"{T}/D31_thickness_convergence.csv", index=False); print("truth thickness (um):"); print(d.round(2).to_string(index=False))
