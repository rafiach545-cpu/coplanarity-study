#!/usr/bin/env python3
"""
Correction audit (2026-10-03, user request): acceptance and longitudinal treatments, on the EXISTING exact crossings
(no new events, no re-propagation, frozen files read-only).

Acceptance       A = paper-stated effective |eta| < 1.8 per hit, barrel only, no finite-z boundary (PRIMARY)
                 B = finite barrel lengths of Ref. [27] (INFERRED sensitivity)
SCT z smearing   Z1160 = 2 x 580 um (paper rule 'twice the intrinsic accuracy' applied to the z accuracy of Ref. [27]; INFERRED)
                 Z580  = 1 x Ref. [27] z accuracy (sensitivity) ;  Z0 = no SCT z smearing (UNDOCUMENTED alternative)
                 SCT R-phi = 34 um always (paper rule x Ref. [27] 17 um R-phi).
Beam spot 45 mm  CV = one common z shift per event (stored z0), fit relative to the true vertex (current implementation)
                 CO = one common z shift per event, fit relative to the origin ('primary vertex ... located at the origin' read literally)
                 PH = independent N(0, 45 mm) z shift of every hit (crossing), no common shift; acceptance, pixel quantisation and
                      merging applied to the smeared positions; fit relative to the origin.  Seed: SeedSequence([45, sample#, key]).
Self-check: (A, Z1160, CV) and (B, Z1160, CV) must reproduce tables/signal_per_event_all_configs.csv exactly (asserted).
Output: tables/acceptance_longitudinal_per_event.csv, tables/acceptance_longitudinal_matrix.csv
"""
import importlib.util, os, sys, math, json, multiprocessing as mp
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p4", f"{HERE}/P4_literal_signal.py"); p4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p4)
sys.path.insert(0, HERE); from stats_utils import row
SAMPLES = p4.SAMPLES; SID = {s: i for i, s in enumerate(SAMPLES)}
PAPER = {"EW": {"trigger": .10, "fiducial": .28, "reco": .72}, "COL": {"trigger": .24, "fiducial": .28, "reco": .35}}


def recon(cr, z0, g, geom, sct, bs, sample, key):
    tth, cf = p4.tth, p4.cf
    if not all(c["crossed"] for c in cr):
        return dict(fid=False, why="missing crossing")
    cr = [dict(c) for c in cr]
    if bs == "PH":
        rng = np.random.default_rng(np.random.SeedSequence([45, SID[sample], int(key)]))
        for c in cr:
            c["z_lab"] = c["z_lab"] - z0 + rng.normal(0.0, 4.5)
    acc = [c for c in cr if (abs(c["z_lab"]) < p4.HALF[c["layer"]] if geom == "B" else abs(p4.eta_lab(c["r"], c["z_lab"])) < 1.8)]
    tmax = max(c["t_ns"] for c in cr)
    if len(acc) < 16 or tmax >= 25.0:
        return dict(fid=False, why=("acceptance" if len(acc) < 16 else "timing"))
    raw, fb = [], np.random.default_rng(900000 + key)
    for c in acc:
        lay = tth.LAYERS[c["layer"] - 1]; rphi = lay["r_cm"] * math.atan2(c["y"], c["x"])
        if lay["is_pixel"]:
            rh, zh, ir, iz = tth.quantize_pixel(rphi, c["z_lab"], lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[(c["quirk"], c["layer"])] if (c["quirk"], c["layer"]) in g else fb.standard_normal(2)
            rh, zh, ir, iz = rphi + 34e-4 * g1, c["z_lab"] + p4.SZ[sct] * g2, None, None
        ph = rh / lay["r_cm"]
        raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=c["quirk"], t_ns=c["t_ns"], x=lay["r_cm"] * math.cos(ph),
                        y=lay["r_cm"] * math.sin(ph), z=zh, is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    merged = tth.merge_neighboring_pixel_hits(raw)
    idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}
    origin = np.array([0.0, 0.0, z0 if bs == "CV" else 0.0])
    hbl = {k: [] for k in range(1, 9)}
    for h in merged:
        hbl[idx[h["layer"]]].append(tuple(cf.vertex_relative_hits([(h["x"], h["y"], h["z"])], origin)[0]))
    cands = cf.seeding_and_iterative_fit(hbl)
    surv = [c for c in cands if c["fit"]["delta_w"] < 1.0]
    sel = min(surv, key=lambda c: c["fit"]["delta_s"]) if surv else None
    mult = cf.check_hit_multiplicity(sel["layers"]) if sel else False
    ds = sel["fit"]["delta_s"] if sel else np.nan; dw = sel["fit"]["delta_w"] if sel else np.nan
    return dict(fid=True, plane=sel is not None, mult=bool(mult), ds=ds, dw=dw, final=bool(sel is not None and mult and ds < 0.01))


def job(a):
    s, key, eid, cr, z0, g, cfgs = a
    return [dict(sample=s, key=key, event_id=eid, geom=ge, sct=sc, bs=b, **recon(cr, z0, g, ge, sc, b, s, key)) for ge, sc, b in cfgs]


def main():
    ex_all = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv")
    old = pd.read_csv(f"{T}/signal_per_event_all_configs.csv")
    cfgs = [(ge, sc, b) for ge in ("A", "B") for sc in ("Z1160", "Z580", "Z0") for b in ("CV", "CO", "PH")]
    jobs = []
    for s in SAMPLES:
        ev = p4.fp.load_sample(s).sort_values("key"); cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv")
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
        z0s = {}
        for e in ev.itertuples():          # pass 1 (mirrors P4 main): consume the stream exactly as P4 did
            c = cr0[cr0.key == e.key].sort_values(["quirk", "layer"])
            if len(c) == 0 or ("technical_error" in c.columns and c.technical_error.notna().any()):
                continue
            rng = seq if seq is not None else np.random.default_rng(int(e.seed)); z0s[int(e.key)] = (p4.fp.stream_draws(rng, c)[0], int(e.event_id), e)
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
        for key in sorted(z0s):             # pass 2 (mirrors P4 main): draws re-derived from the exact crossings
            z0, eid, e = z0s[key]
            rng = seq if seq is not None else np.random.default_rng(int(e.seed))
            ex = ex_all[(ex_all["sample"] == s) & (ex_all.key == key)].sort_values(["quirk", "layer"])
            exd = ex.copy() if len(ex) else None
            z0b, g = p4.fp.stream_draws(rng, cr0[cr0.key == key].sort_values(["quirk", "layer"]), exd)
            assert abs(z0b - z0) < 1e-12
            if len(ex) == 0:
                continue
            rows = [{k: v for k, v in r.items() if k not in ("sample", "key")} for r in ex.to_dict("records")]
            for r in rows: r["crossed"] = bool(r["crossed"])
            jobs.append((s, key, eid, rows, z0, g, cfgs))
    print("events:", len(jobs), flush=True)
    out = []
    with mp.Pool(10, initializer=p4._init) as pool:
        for res in pool.imap_unordered(job, jobs, chunksize=2):
            out += res
    d = pd.DataFrame(out)
    # technical / unpropagated events: non-fiducial, as in P4
    have = set(zip(d["sample"], d.key))
    for _, r in old[(old.geom == "A") & (old.sct == "Z1160") & (old.wconv == "W1")].iterrows():
        if (r["sample"], r.key) not in have:
            for ge, sc, b in cfgs: out.append(dict(sample=r["sample"], key=r.key, event_id=r.event_id, geom=ge, sct=sc, bs=b, fid=False, why="technical_exception"))
    d = pd.DataFrame(out); d.to_csv(f"{T}/acceptance_longitudinal_per_event.csv", index=False)
    # self-check vs P4
    for ge in ("A", "B"):
        a = d[(d.geom == ge) & (d.sct == "Z1160") & (d.bs == "CV")].set_index(["sample", "key"]).sort_index()
        b = old[(old.geom == ge) & (old.sct == "Z1160") & (old.wconv == "W1")].set_index(["sample", "key"]).sort_index()
        TR = lambda x: x.astype(str) == "True"
        for col in ("fid", "plane", "mult", "final"):
            assert (TR(a[col].reindex(b.index)) == TR(b[col])).all(), (ge, col)
        m = TR(b.fid); assert np.allclose(a.ds.reindex(b.index)[m].fillna(-1), b.ds[m].fillna(-1), atol=1e-7), ge   # CSV round-trip of crossings: <= 1.3e-8 cm
    print("self-check vs P4: identical fiducial/plane/mult/final, Delta_s within 1e-7 cm, for A and B at (Z1160, CV)", flush=True)
    # matrix
    gen = json.load(open(f"{T}/P3_raw_trigger_recount.json")); TR = lambda x: x.astype(str) == "True"
    mrows = []
    for (s, ge, sc, b), x in d.groupby(["sample", "geom", "sct", "bs"]):
        bench = "EW" if s.startswith("EW") else "COL"
        nf, ntrig_an = int(TR(x.fid).sum()), len(x)
        f = x[TR(x.fid)]; npl, nmu, nfi = int(TR(f.plane).sum()), int(TR(f.mult).sum()), int(TR(f.final).sum())
        rf = row(nf, ntrig_an, PAPER[bench]["fiducial"]); rr = row(nfi, nf, PAPER[bench]["reco"]) if nf else {}
        mrows.append(dict(sample=s, acceptance=ge, sct_z=sc, beamspot=b, trigger_analysed=ntrig_an, fiducial=nf, plane=npl, mult=nmu, final=nfi,
                          eps_fid=rf["frac"], fid_w95_lo=rf["wilson95_lo"], fid_w95_hi=rf["wilson95_hi"], p_fid=rf["p_exact_vs_paper"],
                          eps_reco=rr.get("frac"), reco_w95_lo=rr.get("wilson95_lo"), reco_w95_hi=rr.get("wilson95_hi"), p_reco=rr.get("p_exact_vs_paper")))
    M = pd.DataFrame(mrows); M.to_csv(f"{T}/acceptance_longitudinal_matrix.csv", index=False)
    print(M[["sample", "acceptance", "sct_z", "beamspot", "trigger_analysed", "fiducial", "plane", "mult", "final", "p_fid", "p_reco"]].to_string())


if __name__ == "__main__":
    main()
