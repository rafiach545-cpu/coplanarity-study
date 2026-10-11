#!/usr/bin/env python3
"""P24 (2026-10-11): signal Fig. 5 population as stated by the authors (D18): "Fig 5 is before applying the Delta_s and Delta_w cuts".
Plane finding of Sec. III C unchanged (including its seed cuts Delta_s < 0.05 cm, Delta_w < 1 cm and the factor-3 rule); the selected plane is the
candidate with the smallest Delta_s WITHOUT the final Delta_w < 1 cm requirement. Recorded with and without the hit-multiplicity requirement.
Same events, hits and random draws as P18 (first crossing; Ref. [27] lengths; COL2000, EW2000); SCT z = 0, 580 um, 1.16 mm.
Check: the Delta_w < 1 selection must reproduce tables/all_crossings_per_event.csv (FIRST). Output: tables/fig5_author_population.csv"""
import os, sys, math, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
def reco2(cr, z0, g, sct, key, sample):
    tth, cf = p4.tth, p4.cf; rng = np.random.default_rng(np.random.SeedSequence([18, p18.SID[sample], int(key)])); raw = []
    for c in cr:
        if c["order"] > 0 or c["t_ns"] >= 25.0 or abs(c["z_lab"]) >= p4.HALF[c["layer"]]: continue
        lay = tth.LAYERS[c["layer"] - 1]; rphi = lay["r_cm"] * math.atan2(c["y"], c["x"])
        if lay["is_pixel"]: rh, zh, ir, iz = tth.quantize_pixel(rphi, c["z_lab"], lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[(c["quirk"], c["layer"])] if (c["quirk"], c["layer"]) in g else rng.standard_normal(2)
            rh, zh, ir, iz = rphi + 34e-4 * g1, c["z_lab"] + p4.SZ[sct] * g2, None, None
        ph = rh / lay["r_cm"]; raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=c["quirk"], t_ns=c["t_ns"], x=lay["r_cm"] * math.cos(ph), y=lay["r_cm"] * math.sin(ph),
                                               z=zh, is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}; hbl = {k: [] for k in range(1, 9)}
    for h in tth.merge_neighboring_pixel_hits(raw): hbl[idx[h["layer"]]].append(tuple(cf.vertex_relative_hits([(h["x"], h["y"], h["z"])], np.array([0.0, 0.0, z0]))[0]))
    cands = cf.seeding_and_iterative_fit(hbl)
    a = min(cands, key=lambda c: c["fit"]["delta_s"]) if cands else None                                  # author's Fig. 5 population: no final Delta_w cut
    surv = [c for c in cands if c["fit"]["delta_w"] < 1.0]; b = min(surv, key=lambda c: c["fit"]["delta_s"]) if surv else None   # analysis selection (check)
    f = lambda c: (c is not None, bool(cf.check_hit_multiplicity(c["layers"])) if c else False, c["fit"]["delta_s"] if c else np.nan, c["fit"]["delta_w"] if c else np.nan)
    (pa, ma, dsa, dwa), (pb, mb, dsb, dwb) = f(a), f(b)
    return dict(n_candidates=len(cands), plane_any=pa, mult_any=ma, ds_any=dsa, dw_any=dwa, plane_dw1=pb, mult_dw1=mb, ds_dw1=dsb, dw_dw1=dwb)
def job(a):
    s, key, eid, P1, P2, c1, c2, z0, g, fid = a; mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]; out = []
    if not fid: return [dict(sample=s, key=key, event_id=eid, sct=z, fid=False) for z in ("Z0", "Z580", "Z1160")]
    _, traj = p4.tth.simulate_quirk_hits(P1, P2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    cr = p18.all_crossings(traj)
    for z in ("Z0", "Z580", "Z1160"): out.append(dict(sample=s, key=key, event_id=eid, sct=z, fid=True, **reco2(cr, z0, g, z, key, s)))
    return out
if __name__ == "__main__":
    ref = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); ref = ref[(ref.geom == "B") & (ref.bs == "CV") & (ref.sct == "Z0")]
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv"); jobs = []
    for s in ("COL2000", "EW2000"):
        ev = p4.fp.load_sample(s).sort_values("key"); cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv"); m = p4.momenta(s)
        for e in ev.itertuples():
            c = cr0[cr0.key == e.key].sort_values(["quirk", "layer"]); exk = ex[(ex["sample"] == s) & (ex.key == e.key)].sort_values(["quirk", "layer"])
            if len(c) == 0 or len(exk) == 0 or ("technical_error" in c.columns and c.technical_error.notna().any()): continue
            z0, g = p4.fp.stream_draws(np.random.default_rng(int(e.seed)), c, exk.copy()); r = m.iloc[int(e.key)]
            fid = bool(ref[(ref["sample"] == s) & (ref.key == e.key)].fid.astype(str).iloc[0] == "True")
            jobs.append((s, int(e.key), int(e.event_id), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2), z0, g, fid))
    with mp.Pool(10, initializer=p4._init) as pool: out = [x for rr in pool.imap_unordered(job, jobs) for x in rr]
    d = pd.DataFrame(out); d.to_csv(f"{T}/fig5_author_population.csv", index=False); TR = lambda x: x.astype(str) == "True"
    A = pd.read_csv(f"{T}/all_crossings_per_event.csv"); A = A[A["mode"] == "FIRST"]; bad = 0
    for (s, z), x in d[TR(d.fid)].groupby(["sample", "sct"]):
        y = A[(A["sample"] == s) & (A.sct == z)].set_index("key").loc[x.key]
        bad += int((TR(x.plane_dw1).values != TR(y.plane).values).sum() + (TR(x.mult_dw1).values != TR(y.mult).values).sum())
        bad += int((~np.isclose(x.ds_dw1.fillna(-1).values, y.ds.fillna(-1).values, rtol=1e-9)).sum())
    print("check vs all_crossings_per_event (plane, mult, ds with the Delta_w < 1 selection): mismatches =", bad)
    for (s, z), x in d[TR(d.fid)].groupby(["sample", "sct"]):
        pa = x[TR(x.plane_any)]; pm = pa[TR(pa.mult_any)]
        print(f"{s} {z:6s} fid {len(x)} | no final cuts: planes {len(pa)}, ds median {pa.ds_any.median()*1e4:.0f} um, dw median {pa.dw_any.median():.3f} cm, dw>1: {int((pa.dw_any>=1).sum())}"
              f" | + hit cut: {len(pm)}, ds median {pm.ds_any.median()*1e4:.0f} um, dw median {pm.dw_any.median():.3f} cm")
