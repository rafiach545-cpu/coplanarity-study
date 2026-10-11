#!/usr/bin/env python3
"""Audit: do quirks cross a barrel layer more than once within 25 ns? The analysis keeps only the FIRST outward crossing
per quirk per layer (trajectory_to_hits.find_layer_crossing); a real detector would record every crossing.
Re-propagates every trigger event of EW2000 and COL2000 with the stored vertex (same code path as P4) and counts all
crossings (sign changes of r - R_layer) with t < 25 ns. Output: tables/audit_multiple_crossings.csv"""
import os, sys, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p4", f"{HERE}/P4_literal_signal.py"); p4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p4)
GEV_INV_TO_NS = 6.582119569e-16
def job(a):
    s, key, eid, p1, p2, c1, c2, z0 = a
    mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]
    _, traj = p4.tth.simulate_quirk_hits(p1, p2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    t_ns = np.asarray(traj["t_gev_inv"]) * GEV_INV_TO_NS; ok = t_ns < 25.0; out = dict(sample=s, key=key, event_id=eid)
    multi = 0
    for qi, x in enumerate((traj["x1"], traj["x2"]), 1):
        r = np.hypot(x[:, 0], x[:, 1]) * 1.973269804e-14
        for L, lay in enumerate(p4.tth.LAYERS, 1):
            d = np.sign(r[ok] - lay["r_cm"]); n = int(np.sum(d[1:] != d[:-1]))
            out[f"q{qi}_L{L}"] = n; multi += int(n > 1)
    out["n_layer_quirk_with_multiple_crossings"] = multi; return out
if __name__ == "__main__":
    pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); fid = pe[(pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV")][["sample", "key", "fid", "final"]]
    jobs = []
    for s in ("EW2000", "COL2000"):
        ev = p4.fp.load_sample(s).set_index("key"); m = p4.momenta(s); sub = pe[(pe["sample"] == s) & (pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV")]
        for key in sub.key:
            z0 = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("sample == @s and key == @key and geom == 'B' and sct == 'Z1160' and wconv == 'W1'").z0_cm
            if len(z0) == 0 or np.isnan(z0.iloc[0]): continue
            r = m.iloc[int(key)]
            jobs.append((s, int(key), int(ev.loc[key].event_id), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2), float(z0.iloc[0])))
    print("events", len(jobs), flush=True)
    with mp.Pool(10, initializer=p4._init) as pool: out = list(pool.imap_unordered(job, jobs, chunksize=2))
    d = pd.DataFrame(out).merge(fid, on=["sample", "key"]); d.to_csv(f"{T}/audit_multiple_crossings.csv", index=False)
    TR = lambda x: x.astype(str) == "True"
    for s, g in d.groupby("sample"):
        f = g[TR(g.fid)]; print(s, "trigger events", len(g), "with any multiple crossing:", int((g.n_layer_quirk_with_multiple_crossings > 0).sum()),
                                "| fiducial", len(f), "with multiple:", int((f.n_layer_quirk_with_multiple_crossings > 0).sum()), "| final", int(TR(f.final).sum()), "with multiple:", int((TR(f.final) & (f.n_layer_quirk_with_multiple_crossings > 0)).sum()))
