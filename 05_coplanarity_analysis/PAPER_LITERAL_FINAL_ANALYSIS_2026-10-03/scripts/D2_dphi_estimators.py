#!/usr/bin/env python3
"""Fig. 3 4-keV check: Delta_phi at r ~ 15 cm with three plane normals, same trajectories as F22 (fiducial COL2000 2 keV, EW2000 2 and 4 keV).
  LHAT : L-hat in the exact CM frame (F22 primary).
  VEL  : the paper's own words, "the plane spanned by the quirks' velocity vectors": n = v1_lab x v2_lab (equal lab time).
  AXCM : plane containing the lab separation and the CM velocity: n = (x1 - x2)_lab x beta_cm(t).
Points where |n| before normalisation < 5% of its maximum are dropped; reference = first point with r > 0.5 cm; Delta_phi at r>13 cm = median.
Also |L|max and Eq. 7 scaling (L ~ 1/Lambda^4). Output: tables/dphi_estimators.csv."""
import os, sys, numpy as np, pandas as pd, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB = f22.HB; T = f22.T
def ang(n, good, r):
    j = np.where(good & (r > 0.5))[0]
    if not len(j): return np.nan
    nr = n[j[0]]; a = np.where(good, np.arccos(np.clip(np.abs(n @ nr), 0, 1)), np.nan); s = (r > 13) & (r <= 15) & good
    return np.nanmedian(a[s]) if s.any() else np.nan
def run(a):
    m, mq, lam, z0, tag = a
    _, tr = f22.tth.simulate_quirk_hits((m["px1"], m["py1"], m["pz1"], m["E1"]), (m["px2"], m["py2"], m["pz2"], m["E2"]), mass_gev=mq, Lambda_gev=lam, B_tesla=2.0,
                                        charge1=float(m["charge1"]), charge2=float(m["charge2"]), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("x1", "x2", "p1", "p2")); E1 = np.sqrt((p1 ** 2).sum(1) + mq * mq); E2 = np.sqrt((p2 ** 2).sum(1) + mq * mq)
    v1, v2 = p1 / E1[:, None], p2 / E2[:, None]; bcm = (p1 + p2) / (E1 + E2)[:, None]; cm = (x1 + x2) / 2 * HB; r = np.hypot(cm[:, 0], cm[:, 1])
    out = dict(tag=tag)
    for k, nv in (("VEL", np.cross(v1, v2)), ("AXCM", np.cross(x1 - x2, bcm))):
        nn = np.linalg.norm(nv, axis=1); good = nn > 0.05 * nn.max(); out[f"dphi15_{k}"] = ang(nv / np.maximum(nn, 1e-300)[:, None], good, r)
    return out
if __name__ == "__main__":
    pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); sp = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1'")
    MOM = {s: pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/{t}/trigger_passing_events.csv") for s, t in (("EW2000", "EW_800GeV_L4keV"), ("COL2000", "colored_1800GeV_L2keV"))}
    jobs = []
    for s, mq, lams in (("COL2000", 1800.0, (2e-6,)), ("EW2000", 800.0, (2e-6, 4e-6))):
        fid = pe[(pe["sample"] == s) & (pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV") & (pe.fid.astype(str) == "True")].sort_values("key")
        for key in fid.key:
            z0 = float(sp[(sp["sample"] == s) & (sp.key == key)].z0_cm.iloc[0]); m = MOM[s].iloc[int(key)].to_dict()
            for lam in lams: jobs.append((m, mq, lam, z0, f"{s}|{int(key)}|{lam*1e6:.0f}keV"))
    with mp.Pool(10, initializer=f22._init) as pool: res = list(pool.imap_unordered(run, jobs, chunksize=1))
    df = pd.DataFrame(res); df[["sample", "key", "label"]] = df.tag.str.split("|", expand=True); df.key = df.key.astype(int)
    sm = pd.read_csv(f"{T}/dynamics_v2_summary.csv"); df = df.drop(columns="tag").merge(sm[["sample", "key", "label", "Lmax", "dphi_at_15", "dphiw_at_15"]], on=["sample", "key", "label"])
    df = df.rename(columns={"dphi_at_15": "dphi15_LHAT", "dphiw_at_15": "dphi15_WINDOW"}); df.to_csv(f"{T}/dphi_estimators.csv", index=False)
    print(df.groupby(["sample", "label"])[["Lmax", "dphi15_LHAT", "dphi15_WINDOW", "dphi15_VEL", "dphi15_AXCM"]].median().T.to_string())
