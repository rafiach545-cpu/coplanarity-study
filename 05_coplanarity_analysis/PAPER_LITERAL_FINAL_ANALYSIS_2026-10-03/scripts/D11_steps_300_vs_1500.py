#!/usr/bin/env python3
"""Step-size check on real events (2026-10-11): production 300 steps per period vs 1500 (the function's requested default before coarsening),
identical initial conditions, vertex and SCT draws. All fiducial COL2000 and EW2000 events. Per event: maximum change of the first-crossing
hit position (r-phi, z) and time over the 16 quirk-layer crossings, and the reconstruction outcome (first crossing; SCT z none and 1.16 mm).
Also one real event (COL2000 key 35, 300 steps, full length to r = 60 cm) with the baseline vs the fast integrator. Output: tables/D11_steps_check.csv"""
import os, sys, math, time, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
def job(a):
    s, key, P1, P2, c1, c2, z0, g = a; mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]; res = {}
    for n in (300, 1500):
        if n == 300:   # exactly the production call
            p4.tth.MIN_STEPS_PER_PERIOD = 300
            _, tr = p4.tth.simulate_quirk_hits(P1, P2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
        else:          # the floor check compares floats for equality; retry with the floor a hair lower (effective steps per period stay ~n)
            for f in (0.999, 0.9989, 0.9991, 0.99895, 0.99905):
                p4.tth.MIN_STEPS_PER_PERIOD = f * n
                try:
                    _, tr = p4.tth.simulate_quirk_hits(P1, P2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0,
                                                       max_layer_r_cm=60.0, steps_per_period=n); break
                except RuntimeError: continue
        cr = p18.all_crossings(tr); first = {(c["quirk"], c["layer"]): c for c in cr if c["order"] == 0}
        reco = {z: p18.reco(cr, z0, g, z, key, s, True) for z in ("Z0", "Z1160")}; res[n] = (first, reco)
    f3, f15 = res[300][0], res[1500][0]; common = set(f3) & set(f15)
    drphi = max((abs(f3[k]["r"] * (math.atan2(f3[k]["y"], f3[k]["x"]) - math.atan2(f15[k]["y"], f15[k]["x"]))) for k in common), default=np.nan)
    dz = max((abs(f3[k]["z_lab"] - f15[k]["z_lab"]) for k in common), default=np.nan); dt = max((abs(f3[k]["t_ns"] - f15[k]["t_ns"]) for k in common), default=np.nan)
    row = dict(sample=s, key=key, n_cross_300=len(f3), n_cross_1500=len(f15), max_drphi_um=drphi * 1e4, max_dz_um=dz * 1e4, max_dt_ps=dt * 1e3)
    for z in ("Z0", "Z1160"):
        a3, a15 = res[300][1][z], res[1500][1][z]
        row.update({f"{z}_final_300": a3["final"], f"{z}_final_1500": a15["final"], f"{z}_plane_same": a3["plane"] == a15["plane"],
                    f"{z}_ds_300_um": a3["ds"] * 1e4, f"{z}_ds_1500_um": a15["ds"] * 1e4})
    return row
if __name__ == "__main__":
    ref = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); ref = ref[(ref.geom == "B") & (ref.bs == "CV") & (ref.sct == "Z0")]
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv"); jobs = []
    for s in ("COL2000", "EW2000"):
        ev = p4.fp.load_sample(s).sort_values("key"); cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv"); m = p4.momenta(s)
        for e in ev.itertuples():
            rr = ref[(ref["sample"] == s) & (ref.key == e.key)]
            if rr.empty or rr.fid.astype(str).iloc[0] != "True": continue
            c = cr0[cr0.key == e.key].sort_values(["quirk", "layer"]); exk = ex[(ex["sample"] == s) & (ex.key == e.key)].sort_values(["quirk", "layer"])
            z0, g = p4.fp.stream_draws(np.random.default_rng(int(e.seed)), c, exk.copy()); r = m.iloc[int(e.key)]
            jobs.append((s, int(e.key), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2), z0, g))
    with mp.Pool(10, initializer=p4._init) as pool: d = pd.DataFrame(pool.map(job, jobs))
    d.to_csv(f"{T}/D11_steps_check.csv", index=False); pd.set_option("display.width", 220)
    for s, x in d.groupby("sample"):
        print(f"== {s}: {len(x)} fiducial events | crossings found 300 vs 1500 equal in {int((x.n_cross_300 == x.n_cross_1500).sum())}")
        print(f"   max hit shift over events: r-phi {x.max_drphi_um.max():.3g} um (median {x.max_drphi_um.median():.3g}), z {x.max_dz_um.max():.3g} um (median {x.max_dz_um.median():.3g}), time {x.max_dt_ps.max():.3g} ps")
        for z in ("Z0", "Z1160"):
            ch = (x[f"{z}_final_300"] != x[f"{z}_final_1500"]).sum(); dd = (x[f"{z}_ds_300_um"] - x[f"{z}_ds_1500_um"]).abs()
            print(f"   SCT z {z}: signal region 300 = {int(x[f'{z}_final_300'].sum())}, 1500 = {int(x[f'{z}_final_1500'].sum())}; events changing = {int(ch)}; plane decision changed = {int((~x[f'{z}_plane_same']).sum())}; max |delta ds| {dd.max():.3g} um")
    # baseline vs fast integrator on one real event at production settings
    sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim"); import quirk_trajectory as base, quirk_trajectory_optimized_v2 as v2
    import trajectory_to_hits as tth; tth.MIN_STEPS_PER_PERIOD = 300; j = [a for a in jobs if a[0] == "COL2000" and a[1] == 35][0]; out = {}
    for name, fn in (("baseline", base.integrate_trajectory), ("v2", v2.integrate_trajectory_fast_v2)):
        tth.integrate_trajectory = fn; t0 = time.perf_counter()
        _, tr = tth.simulate_quirk_hits(j[2], j[3], mass_gev=1800.0, Lambda_gev=2e-6, B_tesla=2.0, charge1=j[4], charge2=j[5], rng=np.random.default_rng(0), z0_cm=j[6], max_layer_r_cm=60.0)
        out[name] = (tr, time.perf_counter() - t0)
    a, b = out["baseline"][0], out["v2"][0]
    print("== real event COL2000 key 35, 300 steps/period, full length: " + ", ".join(f"{k} identical={np.array_equal(a[k], b[k])}" for k in ("t_gev_inv", "x1", "p1", "x2", "p2"))
          + f" | runtime baseline {out['baseline'][1]:.1f} s, v2 {out['v2'][1]:.1f} s")
