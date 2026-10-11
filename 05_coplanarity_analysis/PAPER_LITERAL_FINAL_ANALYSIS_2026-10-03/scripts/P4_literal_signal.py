#!/usr/bin/env python3
"""
Phases 4-7: literal signal analysis on the FOUR FROZEN samples (EW1000, EW2000, COL1000, COL2000),
each reported separately.

Inputs (read-only): frozen trigger lists / momenta and stored per-event project results (loaded by the
forensic pipeline's load_sample), truth crossings at z0=0 (forensics tables, used ONLY to replay the
project random stream), the project propagator (unmodified).

Steps
 1. Recover each event's exact vertex z0 from the project random stream:
      EW2000/COL2000: default_rng(stored seed); EW1000/COL1000: sequential default_rng(4242).
 2. Re-propagate EVERY trigger event with that z0 passed explicitly (bit-identical initial state).
 3. Re-derive the project's SCT random draws from the exact crossings (assert same draw count as step 1).
 4. VALIDATION: project configuration (eta-cone, SCT 34/1160 um, literal algorithm) must reproduce the
    stored fiducial / plane / multiplicity / final decisions.
 5. LITERAL configuration: finite barrel (ref [27]), no eta cut, pixel-centre quantisation, SCT
    34 um (R-phi) and 1160 um (z) Gaussian, Eq. 10-11 Delta_w, literal Sec. III C algorithm, full Sec. IV SR.
 6. Systematic variants on the same hits: geometry {B, A} x SCT z {1160, 580, 34, 0 um} x Delta_w cut
    convention {W1: sqrt(l2)<1, W2: 0.5*sqrt(l2)<1}.
Every SCT hit accepted in geometry B is also accepted by the project's eta-cone (|z|<74.9 cm at r>=29.9 cm
implies |eta|<1.65), so all B-geometry SCT hits use the project's own draws; any exception is counted.
"""
import importlib.util, json, math, os, sys, multiprocessing as mp
from collections import Counter
import numpy as np, pandas as pd

BASE = "/home/rafia/coplanarity_study"
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; LOGD = f"{HERE}/../logs"
FOR = f"{BASE}/05_coplanarity_analysis/PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02"
sys.path[:0] = [f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim", f"{BASE}/05_coplanarity_analysis"]
spec = importlib.util.spec_from_file_location("fp", f"{FOR}/scripts/02_forensic_pipeline.py")
fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
HALF = {1: 33.015, 2: 40.05, 3: 40.05, 4: 40.05, 5: 74.9, 6: 74.9, 7: 74.9, 8: 74.9}
SZ = {"Z1160": 0.1160, "Z580": 0.0580, "Z34": 0.0034, "Z0": 0.0}
PAR = {"EW": (800.0, 4e-6), "COL": (1800.0, 2e-6)}
SAMPLES = ("EW1000", "EW2000", "COL1000", "COL2000")


def momenta(s):
    if s in ("EW2000", "COL2000"):
        tag = "EW_800GeV_L4keV" if s == "EW2000" else "colored_1800GeV_L2keV"
        m = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/{tag}/trigger_passing_events.csv")
    else:
        f = "ew_quirk_pair_momenta_800gev_4kev.csv" if s == "EW1000" else "quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv"
        m = pd.read_csv(f"{BASE}/01_signal_generation/{f}"); m = m[m.pT_pair > 200].reset_index(drop=True)
        if "charge1" not in m:
            q = {9000011: -1.0, -9000011: 1.0}; m["charge1"], m["charge2"] = m.pdg1.map(q), m.pdg2.map(q)
    return m


def _init():
    global tth, cf
    import trajectory_to_hits as _t, coplanarity_fit as _c
    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    _t.integrate_trajectory = integrate_trajectory_fast_v2
    tth, cf = _t, _c


def propagate(a):
    s, key, p1, p2, c1, c2, z0 = a
    mq, lam = PAR["EW" if s.startswith("EW") else "COL"]
    try:
        _, traj = tth.simulate_quirk_hits(p1, p2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2,
                                          rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    except Exception as e:
        return s, key, None, f"{type(e).__name__}: {str(e)[:120]}"
    x = (traj["x1"] * 1.973269804e-14, traj["x2"] * 1.973269804e-14)
    rows = []
    for qi in (1, 2):
        for L, lay in enumerate(tth.LAYERS, 1):
            r = tth.find_layer_crossing(x[qi - 1], traj["t_gev_inv"], lay["r_cm"])
            if r is None:
                rows.append(dict(quirk=qi, layer=L, crossed=False))
            else:
                (xx, yy, zz), t = r
                rows.append(dict(quirk=qi, layer=L, crossed=True, x=xx, y=yy, z_lab=zz, t_ns=t, r=lay["r_cm"], is_pixel=lay["is_pixel"]))
    return s, key, rows, None


def eta_lab(r, z):
    return -math.log(math.tan(math.atan2(r, z) / 2.0))


def reconstruct(cr, z0, g, geom, sct, wconv, key, log=None):
    """cr: list of crossing dicts (16 entries). Returns decision dict."""
    if not all(c["crossed"] for c in cr):
        return dict(fid=False, why="missing crossing")
    acc = [c for c in cr if (abs(c["z_lab"]) < HALF[c["layer"]] if geom == "B" else abs(eta_lab(c["r"], c["z_lab"])) < 1.8)]
    tmax = max(c["t_ns"] for c in cr)
    if len(acc) < 16 or tmax >= 25.0:
        return dict(fid=False, why=("acceptance" if len(acc) < 16 else "timing"), n_acc=len(acc), tmax=tmax)
    raw, extra = [], 0
    fb = np.random.default_rng(900000 + key)
    for c in acc:
        lay = tth.LAYERS[c["layer"] - 1]; rphi = lay["r_cm"] * math.atan2(c["y"], c["x"])
        if lay["is_pixel"]:
            rh, zh, ir, iz = tth.quantize_pixel(rphi, c["z_lab"], lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            if (c["quirk"], c["layer"]) in g:
                g1, g2 = g[(c["quirk"], c["layer"])]
            else:
                g1, g2 = fb.standard_normal(2); extra += 1
            rh, zh, ir, iz = rphi + 34e-4 * g1, c["z_lab"] + SZ[sct] * g2, None, None
        ph = rh / lay["r_cm"]
        raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=c["quirk"], t_ns=c["t_ns"],
                        x=lay["r_cm"] * math.cos(ph), y=lay["r_cm"] * math.sin(ph), z=zh, is_pixel=lay["is_pixel"],
                        idx_rphi=ir, idx_z=iz))
    merged = tth.merge_neighboring_pixel_hits(raw)
    idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}
    hbl = {k: [] for k in range(1, 9)}
    for h in merged:
        hbl[idx[h["layer"]]].append(tuple(cf.vertex_relative_hits([(h["x"], h["y"], h["z"])], np.array([0.0, 0.0, z0]))[0]))
    wmax = 1.0 if wconv == "W1" else 2.0
    if log is not None and wconv == "W1":
        cands = fp.instrumented(hbl, "A0", log)
        ref = cf.seeding_and_iterative_fit(hbl)
        assert len(ref) == len(cands) and all(r["hits"] == c["hits"] for r, c in zip(ref, cands))
    else:
        cands = cf.seeding_and_iterative_fit(hbl, dw_seed_max_cm=wmax)
    surv = [c for c in cands if c["fit"]["delta_w"] < wmax]
    sel = min(surv, key=lambda c: c["fit"]["delta_s"]) if surv else None
    mult = cf.check_hit_multiplicity(sel["layers"]) if sel else False
    ds = sel["fit"]["delta_s"] if sel else np.nan; dw = sel["fit"]["delta_w"] if sel else np.nan
    final = bool(sel is not None and mult and ds < 0.01)
    if sel is None:
        ff = "no_seed_pair" if not (len(hbl[8]) >= 2 and len(hbl[7]) >= 2) else ("no_seed_passing_cuts" if not cands else "no_candidate_dw")
    else:
        ff = "PASS" if final else ("hit_multiplicity" if not mult else "delta_s")
    cnt = Counter(sel["layers"]) if sel else Counter()
    out = dict(fid=True, n_merged=len(merged), avail=json.dumps({k: len(v) for k, v in hbl.items()}), n_cands=len(cands),
               plane=sel is not None, mult=bool(mult), dw=dw, ds=ds, dw_pass=bool(sel is not None and dw < wmax),
               ds_pass=bool(sel is not None and ds < 0.01), final=final, first_failure=ff,
               sel_layers=json.dumps({k: cnt.get(k, 0) for k in range(1, 9)}), extra_draws=extra)
    if log is not None and wconv == "W1":
        log.update(candidates=[dict(n_hits=len(c["hits"]), layers=c["layers"], ds=c["fit"]["delta_s"], dw=c["fit"]["delta_w"],
                                    growth_log=c["steps"]) for c in cands],
                   selected=(cands.index(sel) if sel else None), result=out)
    return out


def recon_job(a):
    s, key, event_id, cr, z0, g, configs, want_log = a
    res = []
    for geom, sct, w in configs:
        log = {} if (want_log and (geom, sct, w) == ("B", "Z1160", "W1")) else None
        r = reconstruct(cr, z0, g, geom, sct, w, key, log)
        res.append(dict(sample=s, key=key, event_id=event_id, geom=geom, sct=sct, wconv=w, z0_cm=z0, **r))
        if log is not None:
            res[-1]["_log"] = json.dumps(dict(sample=s, key=key, event_id=event_id, z0_cm=z0, seeds=log.get("seeds"),
                                              n_pairs_L8=log.get("n_pairs_L8"), n_pairs_L7=log.get("n_pairs_L7"),
                                              candidates=log.get("candidates"), selected=log.get("selected")), default=float)
    return res


def main():
    jobs, meta = [], {}
    for s in SAMPLES:
        ev = fp.load_sample(s).sort_values("key"); m = momenta(s)
        cr0 = pd.read_csv(f"{FOR}/tables/truth_crossings_{s}.csv")
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
        for e in ev.itertuples():
            c = cr0[cr0.key == e.key].sort_values(["quirk", "layer"])
            tech_stored = bool(e.technical)
            if len(c) == 0 or ("technical_error" in c.columns and c.technical_error.notna().any()):
                meta[(s, int(e.key))] = dict(event_id=int(e.event_id), z0=None, stored=e, tech=True); continue
            rng = seq if seq is not None else np.random.default_rng(int(e.seed))
            z0, g = fp.stream_draws(rng, c)
            meta[(s, int(e.key))] = dict(event_id=int(e.event_id), z0=z0, ndraw=len(g), stored=e, tech=tech_stored)
            r = m.iloc[int(e.key)]
            jobs.append((s, int(e.key), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2), z0))
    print("propagating", len(jobs), "trigger events", flush=True)
    crossings = {}
    with mp.Pool(10, initializer=_init) as pool:
        for s, key, rows, err in pool.imap_unordered(propagate, jobs, chunksize=2):
            crossings[(s, key)] = (rows, err)
    flat = [dict(sample=s, key=k, **r) for (s, k), (rows, err) in crossings.items() if rows for r in rows]
    pd.DataFrame(flat).sort_values(["sample", "key", "quirk", "layer"]).to_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv", index=False)
    # re-derive draws from the exact crossings (sequential streams replayed in order)
    configs = [(g_, s_, w_) for g_ in ("B", "A") for s_ in ("Z1160", "Z580", "Z34", "Z0") for w_ in ("W1", "W2")]
    rjobs, draw_mismatch = [], 0
    for s in SAMPLES:
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
        for (ss, key), md in sorted(((k, v) for k, v in meta.items() if k[0] == s), key=lambda t: t[0][1]):
            rows, err = crossings.get((s, key), (None, "not propagated"))
            if md["z0"] is None:
                continue
            rng = seq if seq is not None else np.random.default_rng(int(md["stored"].seed))
            ex = pd.DataFrame(rows) if rows else None
            if ex is not None:
                ex = ex.rename(columns={"z_lab": "z_lab"}); ex["key"] = key
            z0b, g = fp.stream_draws(rng, pd.read_csv(f"{FOR}/tables/truth_crossings_{s}.csv").query("key == @key").sort_values(["quirk", "layer"]), ex)
            assert abs(z0b - md["z0"]) < 1e-12
            draw_mismatch += int(len(g) != md["ndraw"])
            md["err"] = err
            if rows is None:
                continue
            rjobs.append((s, key, md["event_id"], rows, md["z0"], g, configs, True))
    print("draw-count mismatches between z0=0 replay and exact crossings:", draw_mismatch, flush=True)
    out, logs = [], open(f"{LOGD}/P4_literal_forensic_events.jsonl", "a")
    with mp.Pool(10, initializer=_init) as pool:
        for res in pool.imap_unordered(recon_job, rjobs, chunksize=2):
            for r in res:
                if "_log" in r:
                    logs.write(r.pop("_log") + "\n")
                out.append(r)
    logs.close()
    # technical exceptions (stored or propagation failure): non-fiducial in every configuration
    for (s, key), md in meta.items():
        if md["z0"] is None or crossings.get((s, key), (None,))[0] is None:
            for g_, s_, w_ in configs:
                out.append(dict(sample=s, key=key, event_id=md["event_id"], geom=g_, sct=s_, wconv=w_, fid=False,
                                why="technical_exception", technical=True))
    d = pd.DataFrame(out)
    d.to_csv(f"{T}/signal_per_event_all_configs.csv", index=False)
    # validation vs stored project decisions (project config = A, Z1160, W1)
    v = d[(d.geom == "A") & (d.sct == "Z1160") & (d.wconv == "W1")]
    rep = []
    for (s, key), md in meta.items():
        st = md["stored"]; r = v[(v["sample"] == s) & (v.key == key)].iloc[0]
        rep.append(dict(sample=s, key=key, event_id=md["event_id"], stored_fid=bool(st.stored_fid), replay_fid=bool(r.fid),
                        stored_plane=bool(st.stored_plane) if st.stored_fid else None, replay_plane=bool(r.get("plane")) if r.fid else None,
                        stored_final=bool(st.stored_final) if st.stored_fid else None, replay_final=bool(r.get("final")) if r.fid else None,
                        stored_ds=st.stored_ds, replay_ds=r.get("ds"), stored_tech=bool(md["tech"]), prop_error=md.get("err")))
    rp = pd.DataFrame(rep); rp.to_csv(f"{T}/signal_replay_vs_stored.csv", index=False)
    for s in SAMPLES:
        x = rp[rp["sample"] == s]; f = x[x.stored_fid]
        print(s, "trigger events", len(x), "| fid match", int((x.stored_fid == x.replay_fid).sum()),
              "| plane match", int((f.stored_plane == f.replay_plane).sum()), "/", len(f),
              "| final match", int((f.stored_final == f.replay_final).sum()), "/", len(f),
              "| ds exact(1e-9)", int(((f.stored_ds - f.replay_ds).abs() < 1e-9).sum() + (f.stored_ds.isna() & f.replay_ds.isna()).sum()),
              "| extra SCT draws", int(d[(d["sample"] == s)].extra_draws.fillna(0).sum()))


if __name__ == "__main__":
    main()
