#!/usr/bin/env python3
"""Full-length step convergence on real events (2026-10-11): 300 (production), 1500, 3000, 6000 steps per period, identical initial conditions,
vertex and SCT draws; all fiducial COL2000 and EW2000 events. Per event and setting: first-crossing hit positions of the 16 quirk-layer pairs
(shift relative to 6000; r-phi difference wrapped in phi), crossing times, and the reconstruction (first crossing; SCT z none and 1.16 mm).
Output: tables/D14_step_convergence.csv
2026-10-12: a setting refused by the 20M-step ceiling of simulate_quirk_hits (low beta_T events; the earlier version stopped with
"no step setting accepted") is recorded as not run; hit shifts are then measured against the highest setting that ran (column ref_steps).
Workers from NWORKERS (default 3; 10 workers with ~2 GB trajectories exhausted the 7 GB machine)."""
import os, sys, math, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
NS = (300, 1500, 3000, 6000)
def sim(n, P1, P2, mq, lam, c1, c2, z0):
    if n == 300:
        p4.tth.MIN_STEPS_PER_PERIOD = 300
        return p4.tth.simulate_quirk_hits(P1, P2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)[1]
    for f in (0.999, 0.9989, 0.9991, 0.99895, 0.99905):
        p4.tth.MIN_STEPS_PER_PERIOD = f * n
        try: return p4.tth.simulate_quirk_hits(P1, P2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0,
                                              max_layer_r_cm=60.0, steps_per_period=n)[1]
        except RuntimeError: continue
    return None   # every MIN factor refused: the 20M-step ceiling of simulate_quirk_hits (low beta_T events at high steps); recorded as not run
def job(a):
    s, key, P1, P2, c1, c2, z0, g = a; mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]; F, R = {}, {}
    for n in NS:
        tr = sim(n, P1, P2, mq, lam, c1, c2, z0)
        if tr is None: continue
        cr = p18.all_crossings(tr)
        F[n] = {(c["quirk"], c["layer"]): c for c in cr if c["order"] == 0}; R[n] = {z: p18.reco(cr, z0, g, z, key, s, True) for z in ("Z0", "Z1160")}
    ref = max(F); rows = []   # reference = highest step setting that ran (6000 unless refused by the step ceiling)
    for n in NS:
        if n not in F:
            rows.append(dict(sample=s, key=key, steps=n, ref_steps=ref, not_run="exceeds 20M-step ceiling")); continue
        common = set(F[n]) & set(F[ref]); sh = []; dts = []
        for k in common:
            a_, b_ = F[n][k], F[ref][k]; dphi = (math.atan2(a_["y"], a_["x"]) - math.atan2(b_["y"], b_["x"]) + math.pi) % (2 * math.pi) - math.pi
            sh.append(math.hypot(a_["r"] * dphi, a_["z_lab"] - b_["z_lab"])); dts.append(abs(a_["t_ns"] - b_["t_ns"]))
        rows.append(dict(sample=s, key=key, steps=n, ref_steps=ref, not_run="", n_cross=len(F[n]), max_shift_um=max(sh) * 1e4, median_shift_um=float(np.median(sh)) * 1e4, max_dt_ps=max(dts) * 1e3,
                         **{f"{z}_{q}": R[n][z][q] for z in ("Z0", "Z1160") for q in ("plane", "mult", "final", "ds")}))
    return rows
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
    import json; LOG = f"{HERE}/../logs/D14_events.jsonl"; done = set()   # append-only checkpoint, one line per finished event; rerun resumes
    if os.path.exists(LOG): done = {(json.loads(l)[0]["sample"], json.loads(l)[0]["key"]) for l in open(LOG)}
    todo = [j for j in jobs if (j[0], j[1]) not in done]; print("events", len(jobs), "done", len(done), "to run", len(todo), flush=True)
    with mp.Pool(int(os.environ.get("NWORKERS", 3)), initializer=p4._init) as pool, open(LOG, "a") as fh:
        for k, rr in enumerate(pool.imap_unordered(job, todo), 1):
            fh.write(json.dumps(rr, default=lambda v: v.item() if hasattr(v, "item") else str(v)) + "\n"); fh.flush(); print(f"{k}/{len(todo)}", flush=True)
    d = pd.DataFrame([x for l in open(LOG) for x in json.loads(l)])
    if "not_run" not in d: d["not_run"] = ""
    d["not_run"] = d["not_run"].fillna(""); d["ref_steps"] = d.get("ref_steps", pd.Series(6000, index=d.index)).fillna(6000).astype(int)
    print("not run (step ceiling):", d[d.not_run != ""][["sample", "key", "steps"]].to_dict("records"))
    d = d[d.not_run == ""]
    d.to_csv(f"{T}/D14_step_convergence.csv", index=False); TR = lambda x: x.astype(str) == "True"
    for (s, n), x in d.groupby(["sample", "steps"]):
        x = x[x.key.isin(d[(d["sample"] == s) & (d.steps == 6000)].key)]   # SR comparison only for events with a 6000-step run
        ref6 = d[(d["sample"] == s) & (d.steps == 6000)].set_index("key").loc[x.key]
        ch = {z: int((TR(x[f"{z}_final"]).values != TR(ref6[f"{z}_final"]).values).sum()) for z in ("Z0", "Z1160")}
        print(f"{s} {n:5d} steps/period: hit shift vs 6000 median {x.median_shift_um.median():8.1f} um, worst event {x.max_shift_um.max():9.1f} um, max dt {x.max_dt_ps.max():6.2f} ps | "
              f"SR (none) {int(TR(x.Z0_final).sum())}/{len(x)} [changed vs 6000: {ch['Z0']}] | SR (1.16 mm) {int(TR(x.Z1160_final).sum())}/{len(x)} [changed: {ch['Z1160']}]")
