#!/usr/bin/env python3
"""Fig. 3 with the paper's own definition: rotation of "the plane spanned by the quirks' velocity vectors" (paper Sec. II).
n(t) = v1 x v2 (lab, equal lab time); points with |v1 x v2| < 5% of its maximum dropped; reference = first remaining point with r > 0.05 cm;
Delta_phi(r) = angle between n(r) and the reference; r = transverse radius of the lab centre of mass. Benchmarks as in the paper's Fig. 3:
colored 1.8 TeV and EW 800 GeV, both Lambda = 2 keV, B = 2 T; all COL2000 / EW2000 fiducial events (Ref. [27] lengths).
Per event: median Delta_phi in 0.1 cm bins of r up to 15 cm. Output: tables/fig3_velocity_plane_curves.csv"""
import os, sys, numpy as np, pandas as pd, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
T = f22.T; HB = f22.HB; EDG = np.arange(0, 15.01, 0.1)
def run(a):
    m, mq, lam, z0, tag = a
    _, tr = f22.tth.simulate_quirk_hits((m["px1"], m["py1"], m["pz1"], m["E1"]), (m["px2"], m["py2"], m["pz2"], m["E2"]), mass_gev=mq, Lambda_gev=lam, B_tesla=2.0,
                                        charge1=float(m["charge1"]), charge2=float(m["charge2"]), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("x1", "x2", "p1", "p2")); E1 = np.sqrt((p1 ** 2).sum(1) + mq * mq); E2 = np.sqrt((p2 ** 2).sum(1) + mq * mq)
    n = np.cross(p1 / E1[:, None], p2 / E2[:, None]); nn = np.linalg.norm(n, axis=1); good = nn > 0.05 * nn.max(); n = n / np.maximum(nn, 1e-300)[:, None]
    cm = (x1 + x2) / 2 * HB; r = np.hypot(cm[:, 0], cm[:, 1]); j = np.where(good & (r > 0.05))[0][0]
    a_ = np.where(good, np.arccos(np.clip(np.abs(n @ n[j]), 0, 1)), np.nan)
    b = np.digitize(r, EDG) - 1; rows = []
    for k in range(len(EDG) - 1):
        s = (b == k) & np.isfinite(a_)
        if s.any(): rows.append((tag, 0.5 * (EDG[k] + EDG[k + 1]), float(np.median(a_[s]))))
    return rows
if __name__ == "__main__":
    pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); sp = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1'")
    MOM = {s: pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/{t}/trigger_passing_events.csv") for s, t in (("EW2000", "EW_800GeV_L4keV"), ("COL2000", "colored_1800GeV_L2keV"))}
    jobs = []
    for s, mq in (("COL2000", 1800.0), ("EW2000", 800.0)):
        fid = pe[(pe["sample"] == s) & (pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV") & (pe.fid.astype(str) == "True")].sort_values("key")
        for key in fid.key:
            z0 = float(sp[(sp["sample"] == s) & (sp.key == key)].z0_cm.iloc[0]); jobs.append((MOM[s].iloc[int(key)].to_dict(), mq, 2e-6, z0, f"{s}|{int(key)}"))
    with mp.Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4, initializer=f22._init) as pool: res = [r for rr in pool.imap_unordered(run, jobs) for r in rr]
    d = pd.DataFrame(res, columns=["tag", "r_cm", "dphi_rad"]); d[["sample", "key"]] = d.tag.str.split("|", expand=True); d = d.drop(columns="tag")
    d.to_csv(f"{T}/fig3_velocity_plane_curves.csv", index=False)
    e = d[d.r_cm > 14.5].groupby(["sample", "key"]).dphi_rad.median()
    for s, g in e.groupby(level=0): print(s, "N", len(g), "Delta_phi(15 cm) median %.3g, 16-84%% %.3g-%.3g" % (g.median(), g.quantile(.16), g.quantile(.84)), "| paper", {"COL2000": 0.0906e-3, "EW2000": 0.3545e-3}[s], "percentile", round(100 * (g < {"COL2000": 0.0906e-3, "EW2000": 0.3545e-3}[s]).mean()))
