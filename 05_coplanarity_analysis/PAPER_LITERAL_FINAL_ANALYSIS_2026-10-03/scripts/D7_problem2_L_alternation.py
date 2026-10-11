#!/usr/bin/env python3
"""D17 Problem 2 investigation (2026-10-09): alternating |L| at successive closest approaches, COL2000 key 35 (and a second event).
New outputs only: tables/D7_*.csv. No existing table, report or log is modified.
(1) per closest approach: separation vector d*, relative momentum p_rel* = (p1* - p2*)/2, angle, |p_rel*|, p_perp, L* vector (exact CM frame as F22).
(2) torque test in the LAB frame at equal lab time, from the implemented right-hand side (_rhs of quirk_trajectory_optimized_v2):
    L_lab = (x1 - x2) x (p1 - p2)/2 ;  dL_lab/dt = (v1 - v2) x (p1 - p2)/2 + (x1 - x2) x (F1 - F2)/2, with F split into string (Bz = 0) and Lorentz parts.
    The integral of the right-hand side between consecutive closest approaches is compared with the change of L_lab.
(3) step convergence: 3000 / 6000 / 12000 steps per period, identical initial conditions.
(5) second colored event: the fiducial event whose predicted spacing of closest approaches is nearest 1.155 cm."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim"); import quirk_trajectory_optimized_v2 as qt
HB, T = f22.HB, f22.T; MQ, LAM, E_NAT, BZ = 1800.0, 2e-6, 0.30282212, 2.0 * qt.TESLA_TO_GEV2
f22._init()
M = pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv")
SP = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1' and sample == 'COL2000'")
def simulate(key, nstep, rmax=6.0):
    f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * nstep; m = M.iloc[key]; z0 = float(SP[SP.key == key].z0_cm.iloc[0])
    _, tr = f22.tth.simulate_quirk_hits((m.px1, m.py1, m.pz1, m.E1), (m.px2, m.py2, m.pz2, m.E2), mass_gev=MQ, Lambda_gev=LAM, B_tesla=2.0, charge1=float(m.charge1),
                                        charge2=float(m.charge2), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=rmax, steps_per_period=nstep)
    return m, {k: np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2")}
def cm_quantities(tr):
    t, x1, x2, p1, p2 = (tr[k] for k in ("t_gev_inv", "x1", "x2", "p1", "p2"))
    E1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); E2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (E1[0] + E2[0])
    t1, y1, _, q1 = f22.lorentz(t, x1, E1, p1, b); t2, y2, _, q2 = f22.lorentz(t, x2, E2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    y2i = np.column_stack([np.interp(t1[ok], t2, y2[:, k]) for k in range(3)]); q2i = np.column_stack([np.interp(t1[ok], t2, q2[:, k]) for k in range(3)])
    dv = y1[ok] - y2i; pr = (q1[ok] - q2i) / 2; Lv = np.cross(dv, pr); r = np.hypot(*((x1 + x2)[ok, :2] / 2 * HB).T)
    return dict(dv=dv, pr=pr, Lv=Lv, d=np.linalg.norm(dv, axis=1) * HB, r=r, b=b)
def extrema(y, r, kind, rlo=0.02, rhi=5.0):
    i = np.where((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:]))[0] + 1 if kind == "min" else np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1
    return i[(r[i] > rlo) & (r[i] < rhi)]
def approach_table(key, nstep, c):
    rows = []
    for j, i in enumerate(extrema(c["d"], c["r"], "min")):
        dv, pr, L = c["dv"][i], c["pr"][i], c["Lv"][i]; nh = dv / np.linalg.norm(dv)
        rows.append(dict(key=key, steps_per_period=nstep, approach=j + 1, r_cm=c["r"][i], d_cm=c["d"][i], d_x=dv[0] * HB, d_y=dv[1] * HB, d_z=dv[2] * HB,
                         prel_x=pr[0], prel_y=pr[1], prel_z=pr[2], prel_GeV=np.linalg.norm(pr), angle_d_prel_deg=np.degrees(np.arccos(np.clip(abs(nh @ pr) / np.linalg.norm(pr), 0, 1))),
                         pperp_GeV=np.linalg.norm(pr - (pr @ nh) * nh), L_x=L[0], L_y=L[1], L_z=L[2], L_hbar=np.linalg.norm(L)))
    return rows
def torque_test(key, tr, m):
    t, x1, x2, p1, p2 = (tr[k] for k in ("t_gev_inv", "x1", "x2", "p1", "p2")); q1, q2 = float(m.charge1) * E_NAT, float(m.charge2) * E_NAT
    n = len(t); kin = np.zeros((n, 3)); stg = np.zeros((n, 3)); lor = np.zeros((n, 3))
    for k in range(n):
        s = (*x1[k], *p1[k], *x2[k], *p2[k])
        a = qt._rhs(*s, MQ, q1, q2, LAM ** 2, BZ); a0 = qt._rhs(*s, MQ, q1, q2, LAM ** 2, 0.0)
        v1, F1, v2, F2 = np.array(a[0:3]), np.array(a[3:6]), np.array(a[6:9]), np.array(a[9:12]); F1s, F2s = np.array(a0[3:6]), np.array(a0[9:12])
        dx, dp = x1[k] - x2[k], (p1[k] - p2[k]) / 2
        kin[k] = np.cross(v1 - v2, dp); stg[k] = np.cross(dx, (F1s - F2s) / 2); lor[k] = np.cross(dx, ((F1 - F1s) - (F2 - F2s)) / 2)
    L = np.cross(x1 - x2, (p1 - p2) / 2); d = np.linalg.norm(x1 - x2, axis=1) * HB; r = np.hypot(*((x1 + x2)[:, :2] / 2 * HB).T)
    cum = lambda y: np.concatenate([[np.zeros(3)], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(t)[:, None], axis=0)])
    Ck, Cs, Cl = cum(kin), cum(stg), cum(lor); mn = extrema(d, r, "min"); pts = np.r_[0, mn]; rows = []
    for a_, b_ in zip(pts[:-1], pts[1:]):
        dL = L[b_] - L[a_]; parts = {nm: c[b_] - c[a_] for nm, c in (("kinematic", Ck), ("string", Cs), ("lorentz", Cl))}; pred = sum(parts.values())
        rows.append(dict(key=key, r_from=r[a_], r_to=r[b_], dL_obs=np.linalg.norm(dL), dL_pred=np.linalg.norm(pred), residual_rel=np.linalg.norm(dL - pred) / max(np.linalg.norm(dL), 1e-30),
                         L_lab_at_end=np.linalg.norm(L[b_]), **{f"{nm}_part": np.linalg.norm(v) for nm, v in parts.items()},
                         lorentz_dot_dL=float(parts["lorentz"] @ dL / max(np.linalg.norm(parts["lorentz"]) * np.linalg.norm(dL), 1e-30))))
    return rows
if __name__ == "__main__":
    A, TQ = [], []
    for nstep in (3000, 6000, 12000):
        m, tr = simulate(35, nstep); A += approach_table(35, nstep, cm_quantities(tr))
        if nstep == 3000: TQ += torque_test(35, tr, m)
    # second event: predicted spacing nearest 1.155 cm among the fiducial colored events
    pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); keys = pe[(pe["sample"] == "COL2000") & (pe.geom == "B") & (pe.sct == "Z0") & (pe.bs == "CV") & (pe.fid.astype(str) == "True")].key.values
    r_ = M.iloc[keys]; P = r_[["quirk_pair_px", "quirk_pair_py", "quirk_pair_pz"]].values; E = r_.quirk_pair_E.values; b = P / E[:, None]; g = 1 / np.sqrt(1 - (b ** 2).sum(1))
    gs = r_.quirk_pair_mass_gev.values / (2 * MQ); vs = np.sqrt(1 - 1 / gs ** 2); spac = g * np.hypot(b[:, 0], b[:, 1]) * 2 * vs * gs * MQ / LAM ** 2 * HB; dmax = 2 * (gs - 1) * MQ / LAM ** 2 * HB
    cand = pd.DataFrame(dict(key=keys, spacing_cm=spac, dmax_cm=dmax)).sort_values("spacing_cm"); cand.to_csv(f"{T}/D7_spacing_candidates.csv", index=False)
    k2 = int(cand.iloc[(cand.spacing_cm - 1.155).abs().argmin()].key)
    m, tr = simulate(k2, 3000); c = cm_quantities(tr); A += approach_table(k2, 3000, c); TQ += torque_test(k2, tr, m)
    TP = [dict(key=k2, kind="turning point (d max)", r_cm=c["r"][i], d_cm=c["d"][i], L_hbar=np.linalg.norm(c["Lv"][i])) for i in extrema(c["d"], c["r"], "max")]
    m35, tr35 = simulate(35, 3000); c35 = cm_quantities(tr35)
    TP += [dict(key=35, kind="turning point (d max)", r_cm=c35["r"][i], d_cm=c35["d"][i], L_hbar=np.linalg.norm(c35["Lv"][i])) for i in extrema(c35["d"], c35["r"], "max")]
    pd.DataFrame(A).to_csv(f"{T}/D7_closest_approaches.csv", index=False); pd.DataFrame(TQ).to_csv(f"{T}/D7_torque_test.csv", index=False); pd.DataFrame(TP).to_csv(f"{T}/D7_turning_points.csv", index=False)
    pd.set_option("display.width", 250)
    print("second event:", k2, cand[cand.key == k2].to_string(index=False))
    print(pd.DataFrame(A)[["key", "steps_per_period", "approach", "r_cm", "d_cm", "prel_GeV", "angle_d_prel_deg", "pperp_GeV", "L_x", "L_y", "L_z", "L_hbar"]].to_string(float_format=lambda v: f"{v:.4g}"))
    print(pd.DataFrame(TQ).to_string(float_format=lambda v: f"{v:.3g}"))
    print(pd.DataFrame(TP).to_string(float_format=lambda v: f"{v:.4g}"))
