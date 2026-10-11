#!/usr/bin/env python3
"""Fig. 2 review checks (2026-10-11). (A) key -> event mapping in F33 (M.iloc[key]) and z0 lookup; (B) median-|L|max and nearest-kinematics selections
recomputed and saved; (C) r consistency: r from lab positions at the lab step vs r of the lab CM position at the lab time that corresponds to the
same CM-frame time used for d and L; (D) convergence at 1500 / 3000 / 6000 steps per period (d max, closest-approach positions and spacing, |L|max,
|L| at closest approaches, curve difference). Outputs: tables/D12_*.csv"""
import os, sys, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import F22_dynamics_v2 as f22
T, HB, MQ = f22.T, f22.HB, 1800.0; f22._init()
spec = importlib.util.spec_from_file_location("p4", f"{HERE}/P4_literal_signal.py"); p4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p4)
M = pd.read_csv(f"{f22.BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv")
SP = pd.read_csv(f"{T}/signal_per_event_all_configs.csv").query("geom == 'B' and sct == 'Z1160' and wconv == 'W1' and sample == 'COL2000'")
LS = p4.fp.load_sample("COL2000").set_index("key")
# (A)
print("(A) columns of M contain 'key':", "key" in M.columns, "| load_sample key = row index of trigger_passing_events.csv:",
      bool((LS.event_id.values == M.hepmc_event_idx.values[LS.index.values]).all()))
for k in (35, 8):
    n = int((SP.key == k).sum()); print(f"    key {k}: M row hepmc_event_idx {int(M.iloc[k].hepmc_event_idx)} = load_sample event_id {int(LS.loc[k].event_id)}; z0 rows in SP: {n} (unique: {n == 1}); "
                                        f"z0 = {float(SP[SP.key == k].z0_cm.iloc[0]):.4f} cm")
# (B)
sm = pd.read_csv(f"{T}/dynamics_v2_summary.csv"); c = sm[(sm["sample"] == "COL2000") & (sm.label == "2keV")].sort_values("Lmax").reset_index(drop=True)
print(f"(B) median |L|max among {len(c)} fiducial COL2000 events: key {int(c.iloc[len(c)//2].key)} (Lmax {c.iloc[len(c)//2].Lmax:.3g})")
rows = []
for smp in ("COL2000", "COL1000"):
    m = p4.momenta(smp)
    for k, r in m.iterrows():
        if abs(r.charge1) < 0.5 or abs(r.charge2) < 0.5: continue
        P = np.array([r.px1 + r.px2, r.py1 + r.py2, r.pz1 + r.pz2]); E = r.E1 + r.E2; b = P / E; g = 1 / np.sqrt(1 - b @ b); Mi = np.sqrt(E ** 2 - P @ P)
        gs = Mi / (2 * MQ); vs = np.sqrt(1 - 1 / gs ** 2); Tp = 2 * vs * gs * MQ / 2e-6 ** 2 * HB
        rows.append(dict(sample=smp, key=k, dmax_cm=2 * (gs - 1) * MQ / 2e-6 ** 2 * HB, spacing_cm=g * np.hypot(b[0], b[1]) * Tp))
K = pd.DataFrame(rows); K["distance"] = np.hypot((K.dmax_cm - 3.56) / 3.56, (K.spacing_cm - 1.155) / 1.155); K = K.sort_values("distance"); K.to_csv(f"{T}/D12_nearest_kinematics.csv", index=False)
print(f"    nearest kinematics among {len(K)} charged triggered colored events: {K.iloc[0].to_dict()}")
# (C) + (D)
def run(key, nstep):
    f22.tth.MIN_STEPS_PER_PERIOD = 0.999 * nstep; m = M.iloc[key]; z0 = float(SP[SP.key == key].z0_cm.iloc[0])
    _, tr = f22.tth.simulate_quirk_hits((m.px1, m.py1, m.pz1, m.E1), (m.px2, m.py2, m.pz2, m.E2), mass_gev=MQ, Lambda_gev=2e-6, B_tesla=2.0, charge1=float(m.charge1),
                                        charge2=float(m.charge2), rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=6.0, steps_per_period=nstep)
    t, x1, x2, p1, p2 = (np.asarray(tr[k]) for k in ("t_gev_inv", "x1", "x2", "p1", "p2")); spp = tr["dt_diagnostics"]["steps_per_period_effective"]
    E1 = np.sqrt((p1 ** 2).sum(1) + MQ * MQ); E2 = np.sqrt((p2 ** 2).sum(1) + MQ * MQ); b = (p1[0] + p2[0]) / (E1[0] + E2[0]); g = 1 / np.sqrt(1 - b @ b)
    t1, y1, _, q1 = f22.lorentz(t, x1, E1, p1, b); t2, y2, _, q2 = f22.lorentz(t, x2, E2, p2, b); ok = (t1 >= t2.min()) & (t1 <= t2.max())
    y2i = np.column_stack([np.interp(t1[ok], t2, y2[:, k]) for k in range(3)]); q2i = np.column_stack([np.interp(t1[ok], t2, q2[:, k]) for k in range(3)])
    dv = y1[ok] - y2i; L = np.linalg.norm(np.cross(dv, (q1[ok] - q2i) / 2), axis=1); d = np.linalg.norm(dv, axis=1) * HB
    r_old = np.hypot(*((x1 + x2)[ok, :2] / 2 * HB).T)
    Xs = (y1[ok] + y2i) / 2; tl = g * (t1[ok] + Xs @ b)                         # lab time of the CM point at this CM-frame time
    xc = (x1 + x2) / 2; r_lab = np.hypot(np.interp(tl, t, xc[:, 0]), np.interp(tl, t, xc[:, 1])) * HB   # lab CM transverse radius at that lab time
    tot = np.linalg.norm(q1[ok] + q2i, axis=1) / np.linalg.norm(q1[ok] - q2i, axis=1)
    return dict(r_old=r_old, r_new=r_lab, d=d, L=L, spp=spp, ptot=tot)
def approaches(x, r):
    d = x["d"]; i = np.where((d[1:-1] < d[:-2]) & (d[1:-1] <= d[2:]))[0] + 1; return i[(r[i] > 0.05) & (r[i] < 5.0)]
C, D = [], []
for key in (35, 8):
    res = {n: run(key, n) for n in (1500, 3000, 6000)}; x = res[3000]; s = x["r_new"] <= 5
    C.append(dict(key=key, max_abs_r_shift_cm=np.abs(x["r_old"] - x["r_new"])[s].max(), median_abs_r_shift_cm=np.median(np.abs(x["r_old"] - x["r_new"])[s]),
                  median_rel_total_momentum=np.median(x["ptot"]), p95_rel_total_momentum=np.quantile(x["ptot"], .95)))
    for n, x in res.items():
        r = x["r_new"]; s = r <= 5; i = approaches(x, r)
        D.append(dict(key=key, steps_requested=n, steps_effective=x["spp"], d_max_cm=x["d"][s].max(), L_max=x["L"][s].max(), approach_r=" / ".join(f"{v:.3f}" for v in r[i]),
                      spacing_cm=np.diff(r[i]).mean(), L_at_approaches=" / ".join(f"{v:.3g}" for v in x["L"][i])))
    # curve difference 3000 vs 6000 on a common r grid
    gr = np.linspace(0.05, 4.95, 2000)
    for n in (1500, 3000):
        a, bb = res[n], res[6000]
        La = np.interp(gr, np.sort(a["r_new"]), a["L"][np.argsort(a["r_new"])]); Lb = np.interp(gr, np.sort(bb["r_new"]), bb["L"][np.argsort(bb["r_new"])])
        da = np.interp(gr, np.sort(a["r_new"]), a["d"][np.argsort(a["r_new"])]); db = np.interp(gr, np.sort(bb["r_new"]), bb["d"][np.argsort(bb["r_new"])])
        D.append(dict(key=key, steps_requested=f"{n} vs 6000", curve_max_dL_over_Lmax=np.abs(La - Lb).max() / Lb.max(), curve_max_dd_cm=np.abs(da - db).max()))
pd.DataFrame(C).to_csv(f"{T}/D12_r_consistency.csv", index=False); pd.DataFrame(D).to_csv(f"{T}/D12_convergence.csv", index=False)
pd.set_option("display.width", 250); print("(C)"); print(pd.DataFrame(C).to_string(float_format=lambda v: f"{v:.3g}")); print("(D)"); print(pd.DataFrame(D).to_string(float_format=lambda v: f"{v:.4g}"))
