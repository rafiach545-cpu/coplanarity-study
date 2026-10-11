#!/usr/bin/env python3
"""Audit follow-up: for events with multiple crossings of a layer (t < 25 ns), how far are the extra crossings from the
first one (|dz|, |r dphi|)? Compares with pixel size (50 x 400 um), SCT pitch (80 um), and the plane windows. Writes
tables/audit_crossing_separation.csv (one row per extra crossing)."""
import os, sys, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p4", f"{HERE}/P4_literal_signal.py"); p4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p4)
NS = 6.582119569e-16; CM = 1.973269804e-14
def job(a):
    s, key, p1, p2, c1, c2, z0 = a; mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]
    _, traj = p4.tth.simulate_quirk_hits(p1, p2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    t = np.asarray(traj["t_gev_inv"]) * NS; rows = []
    for qi, x in enumerate((traj["x1"], traj["x2"]), 1):
        x = np.asarray(x) * CM; r = np.hypot(x[:, 0], x[:, 1])
        for L, lay in enumerate(p4.tth.LAYERS, 1):
            R = lay["r_cm"]; d = np.sign(r - R); idx = np.where((d[1:] != d[:-1]) & (t[1:] < 25.0))[0]
            if len(idx) < 2: continue
            pts = []
            for i in idx:
                f = (R - r[i]) / (r[i + 1] - r[i]); pts.append(x[i] + f * (x[i + 1] - x[i]))
            p0 = pts[0]
            for k, p in enumerate(pts[1:], 2):
                dphi = np.angle(np.exp(1j * (np.arctan2(p[1], p[0]) - np.arctan2(p0[1], p0[0]))))
                rows.append(dict(sample=s, key=key, quirk=qi, layer=L, crossing=k, n_cross=len(idx), dz_cm=abs(p[2] - p0[2]), rdphi_cm=abs(R * dphi)))
    return rows
if __name__ == "__main__":
    a = pd.read_csv(f"{T}/audit_multiple_crossings.csv"); a = a[a.n_layer_quirk_with_multiple_crossings > 0]
    sp = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1'")
    jobs = []
    for s in ("EW2000", "COL2000"):
        m = p4.momenta(s)
        for key in a[a["sample"] == s].key:
            z0 = sp[(sp["sample"] == s) & (sp.key == key)].z0_cm.iloc[0]; r = m.iloc[int(key)]
            jobs.append((s, int(key), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2), float(z0)))
    with mp.Pool(10, initializer=p4._init) as pool: out = [r for rr in pool.imap_unordered(job, jobs, chunksize=2) for r in rr]
    d = pd.DataFrame(out); d.to_csv(f"{T}/audit_crossing_separation.csv", index=False)
    for s, g in d.groupby("sample"):
        print(s, "extra crossings", len(g), "| n_cross distribution", g.n_cross.value_counts().sort_index().to_dict())
        print("   |dz| cm quantiles 10/50/90/max:", np.round(g.dz_cm.quantile([.1, .5, .9]).values, 4), round(g.dz_cm.max(), 4), "| r*dphi cm:", np.round(g.rdphi_cm.quantile([.1, .5, .9]).values, 4), round(g.rdphi_cm.max(), 4))
        print("   fraction with |dz| > 400 um or r*dphi > 50 um (i.e. not the same pixel):", round(((g.dz_cm > 0.04) | (g.rdphi_cm > 0.005)).mean(), 3), "| layers involved:", g.layer.value_counts().sort_index().to_dict())
