#!/usr/bin/env python3
"""Signal with EVERY layer crossing as a hit (paper Sec. III A: "The intersections of the trajectories with a simplified model
of the ATLAS inner detector are calculated"), instead of only the first outward crossing per quirk per layer.
- Same trigger events, stored vertices and stored SCT random draws for the first crossings (P4 path).
- Extra crossings (t < 25 ns, inside the acceptance) get SCT draws from SeedSequence([18, sample#, key]).
- Fiducial definition unchanged (first crossings of all 16 quirk-layer pairs inside the acceptance, max t < 25 ns).
- Geometry B (Ref. [27] lengths); SCT z in {Z0, Z580, Z1160}; beam spot = common shift, fit from the true vertex.
Validation: mode FIRST must reproduce tables/acceptance_longitudinal_per_event.csv (B, CV) for every event.
Output: tables/all_crossings_per_event.csv"""
import os, sys, math, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p4", f"{HERE}/P4_literal_signal.py"); p4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p4)
NS = 6.582119569e-16; CM = 1.973269804e-14; SID = {s: i for i, s in enumerate(p4.SAMPLES)}
def all_crossings(traj):
    t = np.asarray(traj["t_gev_inv"]) * NS; out = []
    for qi, x in enumerate((traj["x1"], traj["x2"]), 1):
        x = np.asarray(x) * CM; r = np.hypot(x[:, 0], x[:, 1])
        for L, lay in enumerate(p4.tth.LAYERS, 1):
            R = lay["r_cm"]; d = np.sign(r - R); idx = np.where(d[1:] != d[:-1])[0]
            for k, i in enumerate(idx):
                f = (R - r[i]) / (r[i + 1] - r[i]); p = x[i] + f * (x[i + 1] - x[i]); tt = t[i] + f * (t[i + 1] - t[i])
                out.append(dict(quirk=qi, layer=L, order=k, x=p[0], y=p[1], z_lab=p[2], t_ns=tt, r=R))
    return out
def reco(hits_cr, z0, g, sct, key, sample, first_only):
    tth, cf = p4.tth, p4.cf; rng = np.random.default_rng(np.random.SeedSequence([18, SID[sample], int(key)])); raw = []
    for c in hits_cr:
        if first_only and c["order"] > 0: continue
        if c["t_ns"] >= 25.0 or abs(c["z_lab"]) >= p4.HALF[c["layer"]]: continue
        lay = tth.LAYERS[c["layer"] - 1]; rphi = lay["r_cm"] * math.atan2(c["y"], c["x"])
        if lay["is_pixel"]: rh, zh, ir, iz = tth.quantize_pixel(rphi, c["z_lab"], lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[(c["quirk"], c["layer"])] if (c["order"] == 0 and (c["quirk"], c["layer"]) in g) else rng.standard_normal(2)
            rh, zh, ir, iz = rphi + 34e-4 * g1, c["z_lab"] + p4.SZ[sct] * g2, None, None
        ph = rh / lay["r_cm"]
        raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=c["quirk"], t_ns=c["t_ns"], x=lay["r_cm"] * math.cos(ph), y=lay["r_cm"] * math.sin(ph), z=zh,
                        is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    merged = tth.merge_neighboring_pixel_hits(raw); idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}
    hbl = {k: [] for k in range(1, 9)}
    for h in merged: hbl[idx[h["layer"]]].append(tuple(cf.vertex_relative_hits([(h["x"], h["y"], h["z"])], np.array([0.0, 0.0, z0]))[0]))
    cands = cf.seeding_and_iterative_fit(hbl); surv = [c for c in cands if c["fit"]["delta_w"] < 1.0]; sel = min(surv, key=lambda c: c["fit"]["delta_s"]) if surv else None
    mult = cf.check_hit_multiplicity(sel["layers"]) if sel else False; ds = sel["fit"]["delta_s"] if sel else np.nan; dw = sel["fit"]["delta_w"] if sel else np.nan
    from collections import Counter
    return dict(plane=sel is not None, mult=bool(mult), ds=ds, dw=dw, final=bool(sel is not None and mult and ds < 0.01), n_hits_input=sum(len(v) for v in hbl.values()),
                max_hits_per_layer=max(len(v) for v in hbl.values()), sel_layers=str(dict(Counter(sel["layers"]))) if sel else "")
def job(a):
    s, key, eid, p1, p2, c1, c2, z0, g, fid = a; mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]
    _, traj = p4.tth.simulate_quirk_hits(p1, p2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    cr = all_crossings(traj); out = []
    for mode in ("FIRST", "ALL"):
        for sct in ("Z0", "Z580", "Z1160"):
            r = reco(cr, z0, g, sct, key, s, mode == "FIRST") if fid else dict(plane=False, mult=False, ds=np.nan, dw=np.nan, final=False)
            out.append(dict(sample=s, key=key, event_id=eid, mode=mode, sct=sct, fid=fid, z0_cm=z0, **r))
    return out
if __name__ == "__main__":
    ref = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); ref = ref[(ref.geom == "B") & (ref.bs == "CV")]
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv"); jobs = []
    for s in p4.SAMPLES:
        ev = p4.fp.load_sample(s).sort_values("key"); cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv"); m = p4.momenta(s)
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None; z0s = {}
        for e in ev.itertuples():
            c = cr0[cr0.key == e.key].sort_values(["quirk", "layer"])
            if len(c) == 0 or ("technical_error" in c.columns and c.technical_error.notna().any()): continue
            rng = seq if seq is not None else np.random.default_rng(int(e.seed)); z0s[int(e.key)] = (p4.fp.stream_draws(rng, c)[0], e)
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
        for key in sorted(z0s):
            z0, e = z0s[key]; rng = seq if seq is not None else np.random.default_rng(int(e.seed))
            exk = ex[(ex["sample"] == s) & (ex.key == key)].sort_values(["quirk", "layer"])
            z0b, g = p4.fp.stream_draws(rng, cr0[cr0.key == key].sort_values(["quirk", "layer"]), exk.copy() if len(exk) else None)
            if len(exk) == 0: continue
            rr = ref[(ref["sample"] == s) & (ref.key == key) & (ref.sct == "Z0")]
            fid = bool(rr.fid.astype(str).iloc[0] == "True"); r = m.iloc[int(key)]
            jobs.append((s, int(key), int(e.event_id), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2), z0, g, fid))
    print("events", len(jobs), flush=True)
    with mp.Pool(10, initializer=p4._init) as pool: out = [r for rr in pool.imap_unordered(job, jobs, chunksize=2) for r in rr]
    d = pd.DataFrame(out); d.to_csv(f"{T}/all_crossings_per_event.csv", index=False)
    # validation: FIRST mode == stored B/CV results
    TR = lambda x: x.astype(str) == "True"; bad = 0
    for sct in ("Z0", "Z580", "Z1160"):
        a = d[(d["mode"] == "FIRST") & (d.sct == sct)].set_index(["sample", "key"]); b = ref[ref.sct == sct].set_index(["sample", "key"]).loc[a.index]
        for c in ("plane", "mult", "final"): bad += int((TR(a[c]) != TR(b[c])).sum())
    print("validation FIRST vs stored (plane/mult/final mismatches):", bad)
    for s in p4.SAMPLES:
        for mode in ("FIRST", "ALL"):
            row = []
            for sct in ("Z0", "Z580", "Z1160"):
                x = d[(d["sample"] == s) & (d["mode"] == mode) & (d.sct == sct)]; f = x[TR(x.fid)]
                row.append(f"{sct}: plane {int(TR(f.plane).sum())} mult {int(TR(f.mult).sum())} final {int(TR(f.final).sum())}/{len(f)}")
            print(s, mode, " | ".join(row))
