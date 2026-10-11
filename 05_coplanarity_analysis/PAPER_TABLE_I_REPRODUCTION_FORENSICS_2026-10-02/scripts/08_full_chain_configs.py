#!/usr/bin/env python3
"""
Full chain (trigger -> fiducial -> reconstruction) for coherent configurations, applied
identically to EW and colored:
    geometry  G in {A: |eta_lab|<1.8 cone (project), B: finite ATLAS barrel half-lengths}
    resolution R in {R0 (project), R2 (SCT R-phi only), R3 (SCT 34 um isotropic)}
    algorithm A0 (literal paper algorithm = project coplanarity_fit, unmodified)
Samples:
    existing  EW1000, EW2000, COL1000, COL2000 (frozen events; truth crossings already propagated)
    INDEPENDENT validation  G0_EW, G0_COL: new MG5 seeds 9101/9201 (never used to choose anything),
        showered with the frozen Pythia settings; colored events require both R-hadrons |q|=1
        (project convention, charge from Pythia's RHadrons table via extract_quirk_momenta).
Random numbers (fresh convention, identical for every configuration of an event):
    rng = default_rng(event_seed); z0 = rng.normal(0, 4.5 cm); then 2 standard normals for EVERY
    SCT crossing (quirk 1..2, layer 5..8) whether or not the hit is accepted; pixel Gaussian not used.
Hit acceptance per geometry: A -> |eta_lab|<1.8 ; B -> |z_lab| < half-length(layer).
Fiducial: all 16 crossings accepted and max t < 25 ns. Reco on trigger AND fiducial events.
"""
import math, os, sys, json, multiprocessing as mp
import numpy as np, pandas as pd
from scipy import stats

BASE = "/home/rafia/coplanarity_study"
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
W = "/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02"
sys.path[:0] = [f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim", f"{BASE}/05_coplanarity_analysis", f"{BASE}/01_signal_generation"]
HALF = {1: 33.015, 2: 40.05, 3: 40.05, 4: 40.05, 5: 74.9, 6: 74.9, 7: 74.9, 8: 74.9}
PAR = {"EW": (800.0, 4e-6), "COL": (1800.0, 2e-6)}
PAPER = {"EW": dict(trig=0.10, fid=0.28, reco=0.72), "COL": dict(trig=0.24, fid=0.28, reco=0.35)}


def _init():
    global tth, cf
    import trajectory_to_hits as _t, coplanarity_fit as _c
    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    _t.integrate_trajectory = integrate_trajectory_fast_v2
    tth, cf = _t, _c


def propagate(a):
    sid, key, bench, p1, p2, c1, c2, seed = a
    rng = np.random.default_rng(seed)
    z0 = rng.normal(0.0, 4.5)
    g = rng.standard_normal(16).reshape(2, 4, 2)          # [quirk, sct layer, (rphi,z)]
    mq, lam = PAR[bench]
    try:
        _, traj = tth.simulate_quirk_hits(p1, p2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2,
                                          rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    except Exception as e:
        return dict(sid=sid, key=key, bench=bench, technical=f"{type(e).__name__}"), None
    x = (traj["x1"] * 1.973269804e-14, traj["x2"] * 1.973269804e-14)
    cr = []
    for qi in (0, 1):
        for L, lay in enumerate(tth.LAYERS, 1):
            r = tth.find_layer_crossing(x[qi], traj["t_gev_inv"], lay["r_cm"])
            cr.append(None if r is None else (qi + 1, L, r[0][0], r[0][1], r[0][2], r[1]))
    return dict(sid=sid, key=key, bench=bench, technical=None, z0=z0), (cr, g)


def reco(cr, g, z0, geom, model):
    acc = []
    for c in cr:
        q, L, x, y, z, t = c
        lay = tth.LAYERS[L - 1]
        ok = (abs(-math.log(math.tan(math.atan2(lay["r_cm"], z) / 2))) < 1.8) if geom == "A" else (abs(z) < HALF[L])
        if ok:
            acc.append(c)
    fid = len(acc) == 16 and max(c[5] for c in cr if c) < 25.0 and all(c is not None for c in cr)
    if not fid:
        return dict(fid=False)
    raw = []
    for q, L, x, y, z, t in acc:
        lay = tth.LAYERS[L - 1]
        rphi = lay["r_cm"] * math.atan2(y, x)
        if lay["is_pixel"]:
            rh, zh, ir, iz = tth.quantize_pixel(rphi, z, lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[q - 1, L - 5]
            sr = lay["eff_res_rphi_um"] * 1e-4
            sz = {"R0": lay["eff_res_z_um"] * 1e-4, "R2": 0.0, "R3": sr}[model]
            rh, zh, ir, iz = rphi + sr * g1, z + sz * g2, None, None
        ph = rh / lay["r_cm"]
        raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=q, t_ns=t, x=lay["r_cm"] * math.cos(ph),
                        y=lay["r_cm"] * math.sin(ph), z=zh, is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    merged = tth.merge_neighboring_pixel_hits(raw)
    idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}
    hbl = {k: [] for k in range(1, 9)}
    for h in merged:
        hbl[idx[h["layer"]]].append(tuple(cf.vertex_relative_hits([(h["x"], h["y"], h["z"])], np.array([0, 0, z0]))[0]))
    cands = cf.seeding_and_iterative_fit(hbl)
    sel = cf.select_reconstructed_plane(cands)
    mult = cf.check_hit_multiplicity(sel["layers"]) if sel else False
    ds = sel["fit"]["delta_s"] if sel else np.nan
    return dict(fid=True, plane=sel is not None, mult=bool(mult), ds=ds, dw=sel["fit"]["delta_w"] if sel else np.nan,
                final=bool(sel is not None and mult and ds < 0.01))


def work(a):
    meta, res = propagate(a)
    out = []
    if res is None:
        for gm in "AB":
            for m in ("R0", "R2", "R3"):
                out.append({**meta, "geom": gm, "model": m, "fid": False})
        return out
    cr, g = res
    for gm in "AB":
        for m in ("R0", "R2", "R3"):
            out.append({**meta, "geom": gm, "model": m, **reco(cr, g, meta["z0"], gm, m)})
    return out


def jobs():
    J, trig = [], {}
    A5 = f"{BASE}/05_coplanarity_analysis"
    q = {9000011: -1.0, -9000011: 1.0}
    # existing samples (momenta from the project trigger lists)
    src = {"EW1000": (pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv"), "EW"),
           "COL1000": (pd.read_csv(f"{BASE}/01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv"), "COL"),
           "EW2000": (pd.read_csv(f"{A5}/quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/trigger_passing_events.csv"), "EW"),
           "COL2000": (pd.read_csv(f"{A5}/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv"), "COL")}
    for sid, (d, b) in src.items():
        ptcol = "pT_pair" if "pT_pair" in d else "quirk_pair_pt_gev"
        d = d[d[ptcol] > 200].reset_index(drop=True)
        if "charge1" not in d:
            d["charge1"], d["charge2"] = d.pdg1.map(q), d.pdg2.map(q)
        trig[sid] = len(d)
        for i, r in d.iterrows():
            J.append((sid, i, b, (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2),
                      int(np.random.SeedSequence([abs(hash(sid)) % 2**31, i]).generate_state(1)[0])))
    # independent validation samples
    from extract_quirk_momenta import _make_rhadron_charge_lookup
    chg = _make_rhadron_charge_lookup()
    info = {}
    for b, seedbase in (("EW", 71001), ("COL", 72001)):
        e = pd.read_csv(f"{W}/runs/G0_newseed/{b}/events.csv")
        n_matched = len(e)
        t = e[e.pair_pt_final > 200].reset_index(drop=True)
        if b == "COL":
            t["charge1"], t["charge2"] = t.pdg1.map(chg), t.pdg2.map(chg)
            n_both = int(((e.pdg1.map(chg).abs() == 1) & (e.pdg2.map(chg).abs() == 1)).sum())
            t = t[(t.charge1.abs() == 1) & (t.charge2.abs() == 1)].reset_index(drop=True)
        else:
            t["charge1"], t["charge2"] = t.pdg1.map(q), t.pdg2.map(q)
            n_both = n_matched
        info[f"G0_{b}"] = dict(N_matched=n_matched, N_trigger_all=int((e.pair_pt_final > 200).sum()), N_both_charged_matched=n_both,
                               N_trigger_charged=len(t))
        trig[f"G0_{b}"] = len(t)
        ss = np.random.SeedSequence(seedbase).spawn(len(t))
        for i, r in t.iterrows():
            J.append((f"G0_{b}", i, b, (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2),
                      float(r.charge1), float(r.charge2), int(ss[i].generate_state(1)[0])))
    return J, trig, info


def wil(k, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return c - h, c + h


def main():
    J, trig, info = jobs()
    print("jobs", len(J), trig, json.dumps(info), flush=True)
    rows = []
    with mp.Pool(10, initializer=_init) as pool:
        for r in pool.imap_unordered(work, J, chunksize=2):
            rows += r
    d = pd.DataFrame(rows)
    d.to_csv(f"{T}/full_chain_per_event.csv", index=False)
    sets = {"EW existing (1000+2000)": ["EW1000", "EW2000"], "COL existing (1000+2000)": ["COL1000", "COL2000"],
            "EW INDEPENDENT G0 (seed 9101)": ["G0_EW"], "COL INDEPENDENT G0 (seed 9201)": ["G0_COL"]}
    out = []
    for (gm, m), g in d.groupby(["geom", "model"]):
        for name, ss in sets.items():
            b = "EW" if name.startswith("EW") else "COL"
            x = g[g.sid.isin(ss)]
            nt = len(x); nf = int(x.fid.sum()); nr = int(x.final.fillna(False).sum()); npl = int(x.plane.fillna(False).sum())
            for q, k, n in (("fid", nf, nt), ("reco_SR", nr, nf), ("plane", npl, nf)):
                lo, hi = wil(k, n)
                pv = PAPER[b]["fid" if q == "fid" else "reco"]
                out.append(dict(geom=gm, model=m, set=name, quantity=q, k=k, n=n, eff=k / n if n else np.nan,
                                se=math.sqrt(k / n * (1 - k / n) / n) if n else np.nan, w95_lo=lo, w95_hi=hi,
                                w68_lo=wil(k, n, 1.0)[0], w68_hi=wil(k, n, 1.0)[1],
                                cp95_lo=stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0,
                                cp95_hi=stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0,
                                paper=pv if q != "plane" else np.nan,
                                p_vs_paper=stats.binomtest(k, n, pv).pvalue if n and q != "plane" else np.nan,
                                paper_in_w95=(lo <= pv <= hi) if q != "plane" else None))
    o = pd.DataFrame(out); o.to_csv(f"{T}/full_chain_summary.csv", index=False)
    json.dump(dict(trigger_counts=trig, independent_sample_info=info), open(f"{T}/full_chain_inputs.json", "w"), indent=1)
    pd.set_option("display.width", 250)
    print(o[o.quantity != "plane"][["geom", "model", "set", "quantity", "k", "n", "eff", "w95_lo", "w95_hi", "paper", "p_vs_paper", "paper_in_w95"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
