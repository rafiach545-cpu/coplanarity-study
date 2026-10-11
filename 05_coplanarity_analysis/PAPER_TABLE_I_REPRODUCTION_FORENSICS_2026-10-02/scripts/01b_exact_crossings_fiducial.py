#!/usr/bin/env python3
"""
Exact truth crossings for every FIDUCIAL event, propagated with the project's own
vertex z0 passed explicitly (simulate_quirk_hits(z0_cm=z0)), so the trajectory is
bit-identical to the project's run. (Propagating at z0=0 and shifting is exact in
physics but not bit-exact numerically; pixel quantisation amplifies 1e-7 cm differences.)

z0 per event: EW2000/COL2000 from default_rng(stored seed); EW1000/COL1000 from the
sequential default_rng(4242) stream replayed over all trigger events (validated
previously: fiducial flags reproduced 89/89).
Output: tables/exact_crossings_fiducial_<sample>.csv (z_lab and z_rel = z_lab - z0).
"""
import os
import sys
import math
import multiprocessing as mp
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
HERE = os.path.dirname(os.path.abspath(__file__))
OUTT = f"{HERE}/../tables"
sys.path.insert(0, f"{BASE}/04_detector_sim")
sys.path.insert(0, f"{BASE}/03_trajectory_sim")
sys.path.insert(0, HERE)
PAR = {"EW1000": (800.0, 4e-6), "EW2000": (800.0, 4e-6), "COL1000": (1800.0, 2e-6), "COL2000": (1800.0, 2e-6)}


def _init():
    global tth
    import trajectory_to_hits as _t
    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    _t.integrate_trajectory = integrate_trajectory_fast_v2
    tth = _t


def prop(a):
    s, key, p1, p2, c1, c2, z0 = a
    mq, lam = PAR[s]
    _, traj = tth.simulate_quirk_hits(p1, p2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2,
                                      rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    x1 = traj["x1"] * 1.973269804e-14
    x2 = traj["x2"] * 1.973269804e-14
    out = []
    for qi, xt in ((1, x1), (2, x2)):
        for L, lay in enumerate(tth.LAYERS, 1):
            r = tth.find_layer_crossing(xt, traj["t_gev_inv"], lay["r_cm"])
            (x, y, z), t = r
            out.append(dict(sample=s, key=key, quirk=qi, layer=L, crossed=True, x=x, y=y, z_lab=z,
                            z_rel=z - z0, t_ns=t, r=lay["r_cm"], is_pixel=lay["is_pixel"], z0_cm=z0))
    return out


def main():
    import importlib.util
    spec = importlib.util.spec_from_file_location("fp", f"{HERE}/02_forensic_pipeline.py")
    fp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fp)
    jobs = []
    for s in ("EW1000", "EW2000", "COL1000", "COL2000"):
        ev = fp.load_sample(s).sort_values("key")
        cr_all = pd.read_csv(f"{OUTT}/truth_crossings_{s}.csv")
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
        if s in ("EW2000", "COL2000"):
            tag = "EW_800GeV_L4keV" if s == "EW2000" else "colored_1800GeV_L2keV"
            mom = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/{tag}/trigger_passing_events.csv")
        else:
            f = "ew_quirk_pair_momenta_800gev_4kev.csv" if s == "EW1000" else "quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv"
            mom = pd.read_csv(f"{BASE}/01_signal_generation/{f}")
            mom = mom[mom.pT_pair > 200].reset_index(drop=True)
            if "charge1" not in mom:
                q = {9000011: -1.0, -9000011: 1.0}
                mom["charge1"], mom["charge2"] = mom.pdg1.map(q), mom.pdg2.map(q)
        for e in ev.itertuples():
            cr = cr_all[cr_all.key == e.key].sort_values(["quirk", "layer"])
            if e.technical or len(cr) == 0 or ("technical_error" in cr.columns and cr.technical_error.notna().any()):
                continue
            rng = seq if seq is not None else np.random.default_rng(int(e.seed))
            z0, _ = fp.stream_draws(rng, cr)
            if e.stored_fid:
                m = mom.iloc[int(e.key)]
                jobs.append((s, int(e.key), (m.px1, m.py1, m.pz1, m.E1), (m.px2, m.py2, m.pz2, m.E2),
                             float(m.charge1), float(m.charge2), float(z0)))
    print("fiducial events to propagate:", len(jobs), flush=True)
    rows = []
    with mp.Pool(10, initializer=_init) as pool:
        for r in pool.imap_unordered(prop, jobs):
            rows += r
    d = pd.DataFrame(rows)
    for s, g in d.groupby("sample"):
        g.sort_values(["key", "quirk", "layer"]).to_csv(f"{OUTT}/exact_crossings_fiducial_{s}.csv", index=False)
        print(s, g.key.nunique())


if __name__ == "__main__":
    main()
