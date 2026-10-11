#!/usr/bin/env python3
"""Eq. 1 / Eq. 4 test of the oscillation amplitude, event by event (paper Sec. I-II).
Eq. 4 (B = 0, back-to-back): one quirk's distance from the CM reaches d_cm,max = (gamma* - 1) m_Q / Lambda^2 at t = v gamma m_Q/Lambda^2,
so the quirk SEPARATION reaches 2 (gamma* - 1) m_Q/Lambda^2 (Eq. 1: d_cm ~ 2 cm (gamma-1)(m_Q/100 GeV)(keV/Lambda)^2 is the same number).
For every fiducial event (COL2000 2 keV, EW2000 2 and 4 keV): gamma* of each quirk in the pair CM frame at production, the predicted
first maximum of the separation, and the simulated first maximum of |x1* - x2*| at equal CM time, with B = 0 and with B = 2 T.
Output: tables/dcm_eq1_test.csv. Ratio sim/pred = 1 means the string force and the units follow the paper's Eq. 3-4."""
import os, sys, numpy as np, pandas as pd, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
BASE = f22.BASE; HB = f22.HB; T = f22.T
def run(a):
    m, mq, lam, z0, tag = a; out = dict(tag=tag)
    p1 = np.array([m["px1"], m["py1"], m["pz1"]]); p2 = np.array([m["px2"], m["py2"], m["pz2"]]); E1, E2 = np.hypot(np.linalg.norm(p1), mq), np.hypot(np.linalg.norm(p2), mq)
    b = (p1 + p2) / (E1 + E2); _, _, Es, ps = f22.lorentz(np.zeros(2), np.zeros((2, 3)), np.array([E1, E2]), np.vstack([p1, p2]), b)
    g1, g2 = Es / mq; out.update(gamma1=g1, gamma2=g2, v_star=np.linalg.norm(ps[0]) / Es[0], beta_cm=np.linalg.norm(b), beta_cm_T=np.hypot(b[0], b[1]),
                                 pred_sep_cm=(g1 + g2 - 2) * mq / lam ** 2 * HB,   # energy conservation: 2 m + Lambda^2 d = E1* + E2*  (equal-gamma limit = Eq. 4 x 2)
                                 pred_eq1_dcm_cm=2 * ((g1 + g2) / 2 - 1) * (mq / 100) * (1e-6 / lam) ** 2)
    for B in (0.0, 2.0):
        _, tr = f22.tth.simulate_quirk_hits((m["px1"], m["py1"], m["pz1"], m["E1"]), (m["px2"], m["py2"], m["pz2"], m["E2"]), mass_gev=mq, Lambda_gev=lam, B_tesla=B,
                                            charge1=float(m["charge1"]), charge2=float(m["charge2"]), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
        t = np.asarray(tr["t_gev_inv"]); x1, x2, q1, q2 = (np.asarray(tr[k]) for k in ("x1", "x2", "p1", "p2"))
        F1 = np.sqrt((q1 ** 2).sum(1) + mq * mq); F2 = np.sqrt((q2 ** 2).sum(1) + mq * mq)
        t1, y1, _, _ = f22.lorentz(t, x1, F1, q1, b); t2, y2, _, _ = f22.lorentz(t, x2, F2, q2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
        y2i = np.column_stack([np.interp(t1[ok], t2, y2[:, k]) for k in range(3)]); d = np.linalg.norm(y1[ok] - y2i, axis=1) * HB; ts = t1[ok]
        mx = np.where((d[1:-1] > d[:-2]) & (d[1:-1] >= d[2:]))[0] + 1; mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1
        k = f"B{int(B)}"; out[f"sim_first_max_{k}"] = d[mx[0]] if len(mx) else np.nan; out[f"sim_median_max_{k}"] = np.median(d[mx]) if len(mx) else np.nan
        out[f"sim_first_min_{k}"] = d[mn[0]] if len(mn) else np.nan
        out[f"sim_t_first_return_ns_{k}"] = ts[mn[0]] * 6.582e-16 if len(mn) else np.nan
    out["pred_t_return_ns"] = 2 * out["v_star"] * (g1 + g2) / 2 * mq / lam ** 2 * 6.582e-16
    return out
if __name__ == "__main__":
    pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); sp = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1'")
    MOM = {s: pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/{t}/trigger_passing_events.csv") for s, t in (("EW2000", "EW_800GeV_L4keV"), ("COL2000", "colored_1800GeV_L2keV"))}
    jobs = []
    for s, mq, lams in (("COL2000", 1800.0, (2e-6,)), ("EW2000", 800.0, (2e-6, 4e-6))):
        fid = pe[(pe["sample"] == s) & (pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV") & (pe.fid.astype(str) == "True")].sort_values("key")
        for key in fid.key:
            z0 = float(sp[(sp["sample"] == s) & (sp.key == key)].z0_cm.iloc[0]); m = MOM[s].iloc[int(key)].to_dict()
            for lam in lams: jobs.append((m, mq, lam, z0, f"{s}|{int(key)}|{lam*1e6:.0f}keV"))
    with mp.Pool(10, initializer=f22._init) as pool: res = list(pool.imap_unordered(run, jobs, chunksize=1))
    df = pd.DataFrame(res); df[["sample", "key", "label"]] = df.tag.str.split("|", expand=True); df.key = df.key.astype(int); df = df.drop(columns="tag").sort_values(["sample", "label", "key"])
    for B in ("B0", "B2"): df[f"ratio_{B}"] = df[f"sim_first_max_{B}"] / df.pred_sep_cm
    df.to_csv(f"{T}/dcm_eq1_test.csv", index=False)
    print(df.groupby(["sample", "label"])[["gamma1", "v_star", "pred_sep_cm", "sim_first_max_B0", "sim_first_max_B2", "ratio_B0", "ratio_B2", "sim_first_min_B2", "pred_t_return_ns", "sim_t_first_return_ns_B0"]].median().T.to_string())
