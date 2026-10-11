#!/usr/bin/env python3
"""
Truth (unsmeared) layer crossings for every TRIGGER-passing event of the four samples.

EW1000, EW2000, COL2000: taken from the previous audit's validated replay
  (../EW_PAPER_REPRODUCTION_AUDIT_2026-10-02/tables/*_layer_crossings_vertex_relative.csv;
   baseline fiducial flags reproduced 89/89, 186/186, 68/68).
COL1000: propagated here with the identical method (project propagator, unmodified,
  vertex at z0=0; the EOM is exactly z-translation invariant).

Output: tables/truth_crossings_<sample>.csv with columns
  sample,key(row_index),quirk,layer,crossed,x,y,z_rel,t_ns,r,is_pixel
"""
import os
import sys
import shutil
import multiprocessing as mp
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f"{HERE}/../tables"
PREV = f"{BASE}/05_coplanarity_analysis/EW_PAPER_REPRODUCTION_AUDIT_2026-10-02/tables"
sys.path.insert(0, f"{BASE}/04_detector_sim")
sys.path.insert(0, f"{BASE}/03_trajectory_sim")


def _init():
    global tth
    import trajectory_to_hits as _t
    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    _t.integrate_trajectory = integrate_trajectory_fast_v2
    tth = _t


def prop(args):
    key, p1, p2, c1, c2 = args
    try:
        _, traj = tth.simulate_quirk_hits(p1, p2, mass_gev=1800.0, Lambda_gev=2e-6, B_tesla=2.0,
                                          charge1=c1, charge2=c2, rng=np.random.default_rng(0),
                                          z0_cm=0.0, max_layer_r_cm=60.0)
    except Exception as e:
        return key, None, f"{type(e).__name__}: {e}"
    x1 = traj["x1"] * 1.973269804e-14
    x2 = traj["x2"] * 1.973269804e-14
    rows = []
    for qi, xt in ((1, x1), (2, x2)):
        for L, lay in enumerate(tth.LAYERS, 1):
            r = tth.find_layer_crossing(xt, traj["t_gev_inv"], lay["r_cm"])
            if r is None:
                rows.append(dict(key=key, quirk=qi, layer=L, crossed=False))
            else:
                (x, y, z), t = r
                rows.append(dict(key=key, quirk=qi, layer=L, crossed=True, x=x, y=y, z_rel=z, t_ns=t,
                                 r=lay["r_cm"], is_pixel=lay["is_pixel"]))
    return key, rows, None


def main():
    for s in ("EW1000", "EW2000", "COL2000"):
        d = pd.read_csv(f"{PREV}/{s}_layer_crossings_vertex_relative.csv")
        d.insert(0, "sample", s)
        d.to_csv(f"{OUT}/truth_crossings_{s}.csv", index=False)
        print(s, "copied", d.key.nunique(), "events")
    src = pd.read_csv(f"{BASE}/01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv")
    trig = src[src.pT_pair > 200].reset_index(drop=True)
    jobs = [(i, (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2))
            for i, r in enumerate(trig.itertuples())]
    rows, errs = [], []
    with mp.Pool(10, initializer=_init) as pool:
        for key, rr, err in pool.imap_unordered(prop, jobs):
            if err:
                errs.append((key, err))
                rows += [dict(key=key, quirk=q, layer=L, crossed=False, technical_error=err)
                         for q in (1, 2) for L in range(1, 9)]
            else:
                rows += rr
    d = pd.DataFrame(rows).sort_values(["key", "quirk", "layer"])
    d.insert(0, "sample", "COL1000")
    d.to_csv(f"{OUT}/truth_crossings_COL1000.csv", index=False)
    print("COL1000 propagated", d.key.nunique(), "events; technical errors:", errs)


if __name__ == "__main__":
    main()
