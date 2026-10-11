#!/usr/bin/env python3
"""Figure 2 / Figure 3 rebuilt with an exact centre-of-mass treatment (supersedes F01's equal-lab-time approximation).
CM frame: fixed boost beta = (p1+p2)/(E1+E2) at t = 0 (net charge 0, so the CM velocity is nearly constant). Each quirk's
worldline (t, x) and four-momentum are Lorentz-transformed; quirk 2 is interpolated to quirk 1's CM times, so every point
is at EQUAL CM TIME. Quantities (natural units; x in GeV^-1, so L = |d x p| is in units of hbar):
  d   = |x1* - x2*|  (cm),  L = |(x1* - x2*) x (p1* - p2*)/2|  (the magnitude |L|, as in the paper),
  r   = transverse radius of the lab centre of mass,
  plane normal n = L_hat (direction of the internal angular momentum = normal of the plane of relative motion);
  Delta_phi(r) = angle between n(r) and n at the first point with |L| > 20% of its maximum; points with |L| < 5% of the
  maximum (cusps where the normal is undefined) are dropped. Check: |p1* + p2*| / |p1*| printed (should be ~0)."""
import os, sys, numpy as np, pandas as pd, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
BASE = "/home/rafia/coplanarity_study"; sys.path[:0] = [f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim"]
HB = 1.973269804e-14; T = f"{HERE}/../tables"
def _init():
    global tth
    import trajectory_to_hits as _t; from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    _t.integrate_trajectory = integrate_trajectory_fast_v2; tth = _t
def lorentz(t, x, E, p, b):
    bb = np.linalg.norm(b); g = 1 / np.sqrt(1 - bb * bb); bh = b / bb
    xl = x @ bh; pl = p @ bh
    ts = g * (t - bb * xl); xs = x + ((g - 1) * xl - g * bb * t)[:, None] * bh
    Es = g * (E - bb * pl); ps = p + ((g - 1) * pl - g * bb * E)[:, None] * bh
    return ts, xs, Es, ps
def dynamics(a):
    m, mq, lam, z0, tag = a
    _, tr = tth.simulate_quirk_hits((m["px1"], m["py1"], m["pz1"], m["E1"]), (m["px2"], m["py2"], m["pz2"], m["E2"]), mass_gev=mq, Lambda_gev=lam, B_tesla=2.0,
                                    charge1=float(m["charge1"]), charge2=float(m["charge2"]), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    t = np.asarray(tr["t_gev_inv"]); x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("x1", "x2", "p1", "p2"))
    E1 = np.sqrt((p1 ** 2).sum(1) + mq * mq); E2 = np.sqrt((p2 ** 2).sum(1) + mq * mq); b = (p1[0] + p2[0]) / (E1[0] + E2[0])
    t1, y1, F1, q1 = lorentz(t, x1, E1, p1, b); t2, y2, F2, q2 = lorentz(t, x2, E2, p2, b)
    ok = (t1 >= t2.min()) & (t1 <= t2.max())
    y2i = np.column_stack([np.interp(t1[ok], t2, y2[:, k]) for k in range(3)]); q2i = np.column_stack([np.interp(t1[ok], t2, q2[:, k]) for k in range(3)])
    dv = y1[ok] - y2i; pr = (q1[ok] - q2i) / 2; Lv = np.cross(dv, pr); L = np.linalg.norm(Lv, axis=1); d = np.linalg.norm(dv, axis=1) * HB
    mom_bal = np.median(np.linalg.norm(q1[ok] + q2i, axis=1) / np.linalg.norm(q1[ok], axis=1))
    cm = (x1 + x2)[ok] / 2 * HB; r = np.hypot(cm[:, 0], cm[:, 1])
    n = Lv / np.maximum(L, 1e-300)[:, None]; good = L > 0.05 * L.max(); j0 = int(np.argmax(L > 0.2 * L.max())); nref = n[j0]
    dphi = np.where(good, np.arccos(np.clip(np.abs(n @ nref), -1, 1)), np.nan)
    # second estimator: plane of relative motion fitted to d* over a sliding window of ~one oscillation (PCA smallest axis)
    dd = np.linalg.norm(dv, axis=1); mx = np.where((dd[1:-1] > dd[:-2]) & (dd[1:-1] >= dd[2:]))[0] + 1
    half = int(np.median(np.diff(mx))) if len(mx) > 2 else 200
    sel = r <= 15.0; idx = np.where(sel)[0]; idx = idx[:: max(1, len(idx) // 5000)]
    nw = []
    for i in idx:
        w = dv[max(0, i - half): i + half + 1]; ev, evec = np.linalg.eigh(w.T @ w); nw.append(evec[:, 0])
    nw = np.array(nw); nref2 = nw[int(np.argmax(r[idx] > 0.5))] if np.any(r[idx] > 0.5) else nw[0]
    dphi_w = np.arccos(np.clip(np.abs(nw @ nref2), -1, 1))
    return tag, pd.DataFrame(dict(r_cm=r[idx], L_hbar=L[idx], d_cm=d[idx], dphi_rad=dphi[idx], dphi_window_rad=dphi_w)), mom_bal
if __name__ == "__main__":
    pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); sp = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1'")
    MOM = {s: pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/{t}/trigger_passing_events.csv") for s, t in (("EW2000", "EW_800GeV_L4keV"), ("COL2000", "colored_1800GeV_L2keV"))}
    jobs = []
    for s, mq, lam_list in (("COL2000", 1800.0, (2e-6,)), ("EW2000", 800.0, (2e-6, 4e-6))):
        fid = pe[(pe["sample"] == s) & (pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV") & (pe.fid.astype(str) == "True")].sort_values("key")
        for key in fid.key:
            z0 = float(sp[(sp["sample"] == s) & (sp.key == key)].z0_cm.iloc[0]); m = MOM[s].iloc[int(key)].to_dict()
            for lam in lam_list: jobs.append((m, mq, lam, z0, f"{s}|{int(key)}|{lam*1e6:.0f}keV"))
    print("trajectories", len(jobs), flush=True)
    with mp.Pool(10, initializer=_init) as pool: res = list(pool.imap_unordered(dynamics, jobs, chunksize=1))
    allr = []; bal = []
    for tag, df, mb in res:
        s, key, lab = tag.split("|"); df.insert(0, "label", lab); df.insert(0, "key", int(key)); df.insert(0, "sample", s); allr.append(df); bal.append(mb)
    out = pd.concat(allr); out.to_csv(f"{T}/dynamics_v2_trajectories.csv", index=False)
    print("CM momentum balance |p1*+p2*|/|p1*| median over trajectories:", float(np.median(bal)), "max:", float(np.max(bal)))
    summ = out.groupby(["sample", "key", "label"]).apply(lambda g: pd.Series(dict(Lmax=g.L_hbar.max(), dmax=g.d_cm.max(), dphi_at_15=g[g.r_cm > 13].dphi_rad.median(), dphiw_at_15=g[g.r_cm > 13].dphi_window_rad.median(), dphi_max=g.dphi_rad.max(), rmax=g.r_cm.max())))
    summ.reset_index().to_csv(f"{T}/dynamics_v2_summary.csv", index=False); print(summ.groupby(["sample", "label"]).median())
