#!/usr/bin/env python3
"""Step-by-step cut-flow of the plane-finding algorithm (Sec. III C) and the signal region (Sec. IV), 2026-10-12.
Same events, vertices, SCT draws and hit model as P18 (mode FIRST: first crossing per quirk and layer); COL2000 and EW2000; SCT z: none (Z0)
and 580 um (Z580, Ref. [27]). The algorithm of coplanarity_fit.seeding_and_iterative_fit is re-run with counters (code unchanged); the
final flags are checked against p18.reco for every event (mismatches printed; must be 0).
Steps (an event passes a step if at least one candidate survives it):
  0 fiducial (denominator of eps_reco)
  1 layer 8: >= 1 hit pair with dphi < 0.1, dz < 2 cm        2 layer 7: same
  3 >= 1 four-hit seed with Delta_s < 0.05 cm                  4 ... and Delta_w < 1 cm          5 ... and x.n3 > 0 for all 4 hits
  6 after the iterative fit (layers 6 -> 1), >= 1 plane with Delta_w < 1 cm  (= "plane found"; smallest Delta_s kept)
  7 hit multiplicity (7 layers with 2 hits, 1 layer with >= 1) on that plane
  8 Delta_s < 0.01 cm  (= signal region; events at step 8 / events at step 0 = eps_reco)
Conditional efficiency = step k / step k-1, Wilson 95%. The last row is the eps_reco numerator; eps_reco's denominator is the fiducial count.
Output: tables/D26_stepwise_cutflow.csv"""
import os, sys, math, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
from collections import Counter
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
SAMPLES = ("COL2000", "EW2000"); SCTS = ("Z0", "Z580")
STEPS = ["fiducial", "layer-8 seed pair", "layer-7 seed pair", "seed Delta_s < 0.05", "seed Delta_w < 1", "seed x.n3 > 0",
         "plane found (iterative fit, Delta_w < 1)", "hit multiplicity", "Delta_s < 0.01 (signal region)"]

def hits_by_layer(hits_cr, z0, g, sct, key, sample):          # identical to the first part of p18.reco (first crossings)
    tth, cf = p4.tth, p4.cf; rng = np.random.default_rng(np.random.SeedSequence([18, p18.SID[sample], int(key)])); raw = []
    for c in hits_cr:
        if c["order"] > 0: continue
        if c["t_ns"] >= p4.R["timing_ns"] or abs(c["z_lab"]) >= p4.HALF[c["layer"]]: continue
        lay = tth.LAYERS[c["layer"] - 1]; rphi = lay["r_cm"] * math.atan2(c["y"], c["x"])
        if lay["is_pixel"]: rh, zh, ir, iz = tth.quantize_pixel(rphi, c["z_lab"], lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[(c["quirk"], c["layer"])] if (c["order"] == 0 and (c["quirk"], c["layer"]) in g) else rng.standard_normal(2)
            rh, zh, ir, iz = rphi + p4.R["sct_rphi_cm"] * g1, c["z_lab"] + p4.SZ[sct] * g2, None, None
        ph = rh / lay["r_cm"]
        raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=c["quirk"], t_ns=c["t_ns"], x=lay["r_cm"] * math.cos(ph), y=lay["r_cm"] * math.sin(ph), z=zh,
                        is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    merged = tth.merge_neighboring_pixel_hits(raw); idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}; hbl = {k: [] for k in range(1, 9)}
    for h in merged: hbl[idx[h["layer"]]].append(tuple(cf.vertex_relative_hits([(h["x"], h["y"], h["z"])], np.array([0.0, 0.0, z0]))[0]))
    return hbl

def stepwise(hbl):
    """Counters around the unchanged algorithm (same order of checks as coplanarity_fit.seeding_and_iterative_fit)."""
    cf = p4.cf; passed = [True] + [False] * 8; S = p4.R["seed"]
    def dphi(a, b):
        d = abs(math.atan2(a[1], a[0]) - math.atan2(b[1], b[0])); return min(d, 2 * math.pi - d)
    pr = {L: [(a, b) for i, a in enumerate(hbl[L]) for b in hbl[L][i + 1:] if dphi(a, b) < S["dphi_seed_max"] and abs(a[2] - b[2]) < S["dz_seed_max_cm"]] for L in (8, 7)}
    passed[1], passed[2] = len(pr[8]) > 0, len(pr[8]) > 0 and len(pr[7]) > 0
    for p8 in pr[8]:
        for p7 in pr[7]:
            x = np.array(list(p8) + list(p7)); f = cf.fit_plane(x)
            if f["delta_s"] >= S["ds_seed_max_cm"]: continue
            passed[3] = True
            if f["delta_w"] >= S["dw_seed_max_cm"]: continue
            passed[4] = True
            if np.all(x @ f["n3"] > 0): passed[5] = True
    cands = cf.seeding_and_iterative_fit(hbl, **S); surv = [c for c in cands if c["fit"]["delta_w"] < p4.R["final_dw_cm"]]
    sel = min(surv, key=lambda c: c["fit"]["delta_s"]) if surv else None
    passed[6] = sel is not None
    passed[7] = passed[6] and bool(p18.mult_ok(sel["layers"]))
    passed[8] = passed[7] and sel["fit"]["delta_s"] < p4.R["signal_ds_cm"]
    for k in range(1, 9): passed[k] = passed[k] and passed[k - 1]
    return passed

def job(a):
    s, key, eid, P1, P2, c1, c2, z0, g, fid = a; mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]
    _, traj = p4.tth.simulate_quirk_hits(P1, P2, mass_gev=mq, Lambda_gev=lam, B_tesla=p4.R["B_tesla"], charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=p4.R["max_layer_r_cm"])
    cr = p18.all_crossings(traj); out = []
    for sct in SCTS:
        st = stepwise(hits_by_layer(cr, z0, g, sct, key, s)); ref = p18.reco(cr, z0, g, sct, key, s, True)
        out.append(dict(sample=s, key=key, sct=sct, **{f"s{k}": st[k] for k in range(9)}, ref_plane=ref["plane"], ref_mult=ref["mult"], ref_final=ref["final"]))
    return out

if __name__ == "__main__":
    ref = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); ref = ref[(ref.geom == "B") & (ref.bs == "CV")]
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv"); jobs = []
    for s in SAMPLES:                                             # job construction as in P18 (2000-event samples: per-event seeds)
        ev = p4.fp.load_sample(s).sort_values("key"); cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv"); m = p4.momenta(s)
        for e in ev.itertuples():
            c = cr0[cr0.key == e.key].sort_values(["quirk", "layer"])
            if len(c) == 0 or ("technical_error" in c.columns and c.technical_error.notna().any()): continue
            exk = ex[(ex["sample"] == s) & (ex.key == e.key)].sort_values(["quirk", "layer"])
            if len(exk) == 0: continue
            rr = ref[(ref["sample"] == s) & (ref.key == e.key) & (ref.sct == "Z0")]
            if rr.empty or rr.fid.astype(str).iloc[0] != "True": continue
            z0, g = p4.fp.stream_draws(np.random.default_rng(int(e.seed)), c, exk.copy()); r = m.iloc[int(e.key)]
            jobs.append((s, int(e.key), int(e.event_id), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2), z0, g, True))
    print("fiducial events", len(jobs), flush=True)
    with mp.Pool(int(os.environ.get("NWORKERS", 3)), initializer=p4._init) as pool: out = [r for rr in pool.imap_unordered(job, jobs) for r in rr]
    d = pd.DataFrame(out)
    mism = int(((d.s6 != d.ref_plane) | (d.s7 != d.ref_mult) | (d.s8 != d.ref_final)).sum()); print("mismatches vs p18.reco (plane/mult/final):", mism)
    rows = []
    for (s, sct), x in d.groupby(["sample", "sct"]):
        n = [int(x[f"s{k}"].sum()) for k in range(9)]
        for k in range(9):
            lo, hi = (stats.binomtest(n[k], n[k - 1]).proportion_ci(0.95, "wilson") if k and n[k - 1] else (np.nan, np.nan))
            rows.append(dict(sample=s, sct=sct, step=k, stage=STEPS[k], events=n[k], lost_here=(n[k - 1] - n[k]) if k else 0,
                             conditional_eff=(n[k] / n[k - 1]) if k and n[k - 1] else np.nan, wilson_lo=lo, wilson_hi=hi,
                             lost_keys=" ".join(str(v) for v in sorted(x[x[f"s{k - 1}"] & ~x[f"s{k}"]].key)) if k else ""))
    c = pd.DataFrame(rows); c.to_csv(f"{T}/D26_stepwise_cutflow.csv", index=False)
    p4.CFG.validate_signal_inputs(); p4.CFG.assert_used("signal"); p4.CFG.write_provenance(f"{T}/D26_stepwise_cutflow.csv", dict(mismatches_vs_p18_reco=mism))
    pd.set_option("display.width", 220)
    for (s, sct), x in c.groupby(["sample", "sct"]):
        print(f"\n== {s}, SCT z {sct}  (eps_reco = last row / fiducial = {x.events.iloc[-1]}/{x.events.iloc[0]})")
        print(x[["step", "stage", "events", "lost_here", "conditional_eff", "wilson_lo", "wilson_hi"]].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
