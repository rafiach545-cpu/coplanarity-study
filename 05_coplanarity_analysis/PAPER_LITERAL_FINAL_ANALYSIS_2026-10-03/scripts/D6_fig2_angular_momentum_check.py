#!/usr/bin/env python3
"""Fig. 2 check (2026-10-09). The paper (Sec. II) says "whenever |L| = 0, the separation between the quirks is large". Our Fig. 2 event shows
|L| ~ 0 at every second closest approach. Checks, all COL2000 fiducial events (1.8 TeV, 2 keV, B = 2 T), CM frame as in F22:
 (1) torque test: in the CM frame dL/dt = d x (F1 - F2)/2 with F = +-q E_cm (paper Eq. 5), so L_pred(t) = q (integral of d dt) x E_cm.
     E_cm from the initial CM velocity: E' = gamma_cm (v_cm x B) (natural units, e = 0.30282). Compare |L_pred| with |L| from the trajectory.
 (2) at every closest approach (local minimum of d, r < 15 cm): |L| / |L|max; count approaches with |L| < 1% of |L|max.
Integration with 3000 steps per period (10x the production setting) to resolve the approaches better. Output: tables/fig2_L_check.csv"""
import os, sys, numpy as np, pandas as pd, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
HB, T = f22.HB, f22.T; E_NAT, T2G = 0.30282212, 1.9535e-16; NSTEP = 3000
def init():
    f22._init(); f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * NSTEP   # float margin: period/dt can come out at 2999.99
def run(a):
    m, z0, key = a; mq = 1800.0
    _, tr = f22.tth.simulate_quirk_hits((m["px1"], m["py1"], m["pz1"], m["E1"]), (m["px2"], m["py2"], m["pz2"], m["E2"]), mass_gev=mq, Lambda_gev=2e-6, B_tesla=2.0,
                                        charge1=float(m["charge1"]), charge2=float(m["charge2"]), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=20.0, steps_per_period=NSTEP)
    t = np.asarray(tr["t_gev_inv"]); x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("x1", "x2", "p1", "p2"))
    E1 = np.sqrt((p1 ** 2).sum(1) + mq * mq); E2 = np.sqrt((p2 ** 2).sum(1) + mq * mq); b = (p1[0] + p2[0]) / (E1[0] + E2[0])
    t1, y1, _, q1 = f22.lorentz(t, x1, E1, p1, b); t2, y2, _, q2 = f22.lorentz(t, x2, E2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max()); ts = t1[ok]
    y2i = np.column_stack([np.interp(ts, t2, y2[:, k]) for k in range(3)]); q2i = np.column_stack([np.interp(ts, t2, q2[:, k]) for k in range(3)])
    dv = y1[ok] - y2i; Lv = np.cross(dv, (q1[ok] - q2i) / 2); L = np.linalg.norm(Lv, axis=1); d = np.linalg.norm(dv, axis=1) * HB
    r = np.hypot(*((x1 + x2)[ok, :2] / 2 * HB).T)
    g = 1 / np.sqrt(1 - b @ b); Ecm = g * np.cross(b, [0, 0, 2.0 * T2G]); q = float(m["charge1"]) * E_NAT     # E field in the CM frame; force on quirk 1 = +q E
    I = np.concatenate([[np.zeros(3)], np.cumsum(0.5 * (dv[1:] + dv[:-1]) * np.diff(ts)[:, None], axis=0)])     # integral of d dt (trapezoid)
    Lp = q * np.cross(I, Ecm); sel = r < 15
    rel = np.abs(np.linalg.norm(Lp[sel], axis=1) - L[sel]).max() / L[sel].max()
    mn = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1; mn = mn[(r[mn] > 0.05) & (r[mn] < 15)]
    return dict(key=key, Lmax=L[sel].max(), torque_max_rel_dev=rel, n_approach=len(mn), n_low_L=int((L[mn] < 0.01 * L[sel].max()).sum()),
                min_L_at_approach=float(L[mn].min()) if len(mn) else np.nan, median_L_ratio_at_approach=float(np.median(L[mn] / L[sel].max())) if len(mn) else np.nan)
if __name__ == "__main__":
    pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); sp = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1'")
    M = pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv")
    keys = pe[(pe["sample"] == "COL2000") & (pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV") & (pe.fid.astype(str) == "True")].key
    jobs = [(M.iloc[int(k)].to_dict(), float(sp[(sp["sample"] == "COL2000") & (sp.key == k)].z0_cm.iloc[0]), int(k)) for k in keys]
    with mp.Pool(10, initializer=init) as pool: res = list(pool.imap_unordered(run, jobs))
    d = pd.DataFrame(res).sort_values("key"); d.to_csv(f"{T}/fig2_L_check.csv", index=False)
    pd.set_option("display.width", 200); print(d.to_string(float_format=lambda v: f"{v:.3g}"))
    print("events:", len(d), "| torque test max relative deviation: median %.3g, max %.3g" % (d.torque_max_rel_dev.median(), d.torque_max_rel_dev.max()),
          "| closest approaches:", int(d.n_approach.sum()), "of which |L| < 1% of |L|max:", int(d.n_low_L.sum()), "| events with at least one:", int((d.n_low_L > 0).sum()))
