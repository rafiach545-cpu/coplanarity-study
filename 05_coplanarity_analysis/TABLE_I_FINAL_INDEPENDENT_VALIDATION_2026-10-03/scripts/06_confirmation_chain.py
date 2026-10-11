#!/usr/bin/env python3
"""
LOCKED confirmation analysis (see notes/LOCKED_CONFIGURATION.md; this file's SHA-256 is recorded there
BEFORE the confirmation samples were generated).

Input: driver-v3 shower output (events.csv: matched events, final-state pair pT, final-state quirk /
R-hadron momenta and PDG codes) of the fresh confirmation samples CONF_EW and CONF_COL.

Chain, identical for EW and colored:
  trigger      : final-state pair pT > 200 GeV (strict); denominator = matched events
  charge       : colored only, both R-hadrons with non-zero electric charge (Pythia RHadrons table)
  propagation  : project propagator (unmodified), B = 2 T, vertex z0 ~ N(0, 4.5 cm)
  geometry     : B (primary) finite barrel |z| < 33.015/40.05/74.9 cm ; A (systematic) |eta_lab|<1.8
  fiducial     : all 16 first crossings accepted, max t < 25 ns
  pixel        : centre of the hit pixel (quantisation), neighbouring-pixel merging (project code)
  SCT          : sigma_Rphi = 34 um; z envelope Z0 (none), Z34 (34 um), Z580 (580 um), Z1160 (1160 um)
  algorithm    : literal Sec. III C (project coplanarity_fit, unmodified)
  Delta_w cuts : W1 (primary) sqrt(lambda_2) < 1 cm as in Eqs. 10-11 ; W2 (systematic) paper-quoted
                 convention 0.5*sqrt(lambda_2) < 1 cm, i.e. sqrt(lambda_2) < 2 cm (seed + final selection)
  eps_reco     : full Sec. IV signal region / (trigger AND fiducial)
Random numbers per event: SeedSequence(81001 EW / 82001 COL).spawn(N_trigger)[i] -> z0 then 16 standard
normals for the 8 SCT crossings (common random numbers across all SCT models).
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
SZ = {"Z0": 0.0, "Z34": 34e-4, "Z580": 580e-4, "Z1160": 1160e-4}
PAPER = {"EW": dict(trigger=0.10, fiducial=0.28, reconstruction=0.72), "COL": dict(trigger=0.24, fiducial=0.28, reconstruction=0.35)}
SEEDBASE = {"EW": 81001, "COL": 82001}


def _init():
    global tth, cf
    import trajectory_to_hits as _t, coplanarity_fit as _c
    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    _t.integrate_trajectory = integrate_trajectory_fast_v2
    tth, cf = _t, _c


def select(cands, wmax):
    s = [c for c in cands if c["fit"]["delta_w"] < wmax]
    return min(s, key=lambda c: c["fit"]["delta_s"]) if s else None


def seeding(hbl, wmax):
    # literal algorithm; only the Delta_w thresholds (seed and final) depend on the W convention
    return cf.seeding_and_iterative_fit(hbl, dw_seed_max_cm=wmax)


def reco(cr, g, z0, geom, sct, wconv):
    acc = []
    for c in cr:
        q, L, x, y, z, t = c
        lay = tth.LAYERS[L - 1]
        ok = (abs(-math.log(math.tan(math.atan2(lay["r_cm"], z) / 2))) < 1.8) if geom == "A" else (abs(z) < HALF[L])
        if ok:
            acc.append(c)
    if not (len(acc) == 16 and max(c[5] for c in cr) < 25.0):
        return dict(fid=False)
    raw = []
    for q, L, x, y, z, t in acc:
        lay = tth.LAYERS[L - 1]; rphi = lay["r_cm"] * math.atan2(y, x)
        if lay["is_pixel"]:
            rh, zh, ir, iz = tth.quantize_pixel(rphi, z, lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[q - 1, L - 5]
            rh, zh, ir, iz = rphi + 34e-4 * g1, z + SZ[sct] * g2, None, None
        ph = rh / lay["r_cm"]
        raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=q, t_ns=t, x=lay["r_cm"] * math.cos(ph),
                        y=lay["r_cm"] * math.sin(ph), z=zh, is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    merged = tth.merge_neighboring_pixel_hits(raw)
    idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}
    hbl = {k: [] for k in range(1, 9)}
    for h in merged:
        hbl[idx[h["layer"]]].append((h["x"], h["y"], h["z"] - z0))
    wmax = 1.0 if wconv == "W1" else 2.0
    cands = seeding(hbl, wmax)
    sel = select(cands, wmax)
    mult = cf.check_hit_multiplicity(sel["layers"]) if sel else False
    ds = sel["fit"]["delta_s"] if sel else np.nan
    dw = sel["fit"]["delta_w"] if sel else np.nan
    return dict(fid=True, plane=sel is not None, mult=bool(mult), ds=ds, dw=dw,
                dw_pass=bool(sel is not None and dw < wmax), ds_pass=bool(sel is not None and ds < 0.01),
                final=bool(sel is not None and mult and ds < 0.01))


def work(a):
    bench, i, p1, p2, c1, c2, seed = a
    rng = np.random.default_rng(seed)
    z0 = rng.normal(0.0, 4.5); g = rng.standard_normal(16).reshape(2, 4, 2)
    mq, lam = PAR[bench]
    meta = dict(bench=bench, i=i, z0=z0)
    try:
        _, traj = tth.simulate_quirk_hits(p1, p2, mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=c1, charge2=c2,
                                          rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    except Exception as e:
        return [dict(meta, technical=type(e).__name__, geom=gm, sct=s, wconv=w, fid=False)
                for gm in "BA" for s in SZ for w in ("W1", "W2")]
    x = (traj["x1"] * 1.973269804e-14, traj["x2"] * 1.973269804e-14)
    cr = []
    for qi in (0, 1):
        for L, lay in enumerate(tth.LAYERS, 1):
            r = tth.find_layer_crossing(x[qi], traj["t_gev_inv"], lay["r_cm"])
            cr.append(None if r is None else (qi + 1, L, r[0][0], r[0][1], r[0][2], r[1]))
    if any(c is None for c in cr):
        return [dict(meta, technical=None, geom=gm, sct=s, wconv=w, fid=False) for gm in "BA" for s in SZ for w in ("W1", "W2")]
    return [dict(meta, technical=None, geom=gm, sct=s, wconv=w, **reco(cr, g, z0, gm, s, w))
            for gm in "BA" for s in SZ for w in ("W1", "W2")]


def wil(k, n, z=1.959964):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return c - h, c + h


DRY = os.environ.get("DRYRUN") == "1"   # code check only: first 20 trigger events of the earlier G0 samples


def main():
    global T
    if DRY:
        T = f"{T}/dryrun"; os.makedirs(T, exist_ok=True)
    from extract_quirk_momenta import _make_rhadron_charge_lookup
    chg = _make_rhadron_charge_lookup()
    q = {9000011: -1.0, -9000011: 1.0}
    J, counts = [], {}
    for B in ("EW", "COL"):
        tag, lhe = (f"G0_{B}", f"G0_newseed_{B}") if DRY else (f"CONF_{B}", f"CONF_{B}")
        e = pd.read_csv(f"{W}/runs/V3OBS/{tag}/events.csv")
        assert (e.n_final_quirks == 2).all()
        lhe_n = sum(1 for l in open(f"{W}/inputs/{lhe}.lhe") if l.lstrip().startswith("<event"))
        t = e[e.pair_pt_final > 200].reset_index(drop=True)
        if B == "COL":
            t["c1"], t["c2"] = t.pdg1.map(chg), t.pdg2.map(chg)
            t = t[(t.c1.abs() > 0) & (t.c2.abs() > 0)].reset_index(drop=True)
        else:
            t["c1"], t["c2"] = t.pdg1.map(q), t.pdg2.map(q)
        counts[B] = dict(generated=lhe_n, matched=len(e), trigger=int((e.pair_pt_final > 200).sum()), trigger_charged=len(t))
        if DRY:
            t = t.iloc[:20]
        ss = np.random.SeedSequence(SEEDBASE[B]).spawn(len(t))
        for i, r in t.iterrows():
            J.append((B, i, (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.c1), float(r.c2), int(ss[i].generate_state(1)[0])))
    rows = []
    with mp.Pool(10, initializer=_init) as pool:
        for r in pool.imap_unordered(work, J, chunksize=2):
            rows += r
    d = pd.DataFrame(rows); d.to_csv(f"{T}/confirmation_per_event.csv", index=False)
    out, cut = [], []
    for (B, gm, s, w), x in d.groupby(["bench", "geom", "sct", "wconv"]):
        c = counts[B]; f = x[x.fid == True]
        effs = [("trigger", c["trigger"], c["matched"]), ("fiducial", len(f), len(x)), ("reconstruction", int(f.final.sum()), len(f))]
        for qn, k, n in effs:
            lo, hi = wil(k, n); pv = PAPER[B][qn]
            cp = (stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0, stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0)
            out.append(dict(benchmark=B, geometry=gm, sct_z=s, dw_convention=w, quantity=qn, N_pass=k, N_total=n, eff=k / n,
                            wilson95_lo=lo, wilson95_hi=hi, cp95_lo=cp[0], cp95_hi=cp[1], paper=pv,
                            paper_inside_wilson95=bool(lo <= pv <= hi), p_exact=stats.binomtest(k, n, pv).pvalue))
        stages = [("generated", c["generated"]), ("showered", c["generated"]), ("matched", c["matched"]), ("trigger", c["trigger"])]
        if B == "COL":
            stages.append(("trigger AND both charged", c["trigger_charged"]))
        stages += [("fiducial", len(f)), ("plane found", int(f.plane.sum())), ("hit multiplicity", int((f.plane & f.mult).sum())),
                   ("Delta_w cut", int((f.plane & f.mult & f.dw_pass).sum())), ("Delta_s < 0.01 cm", int((f.plane & f.mult & f.dw_pass & f.ds_pass).sum())),
                   ("final SR", int(f.final.sum()))]
        for j, (nm, v) in enumerate(stages):
            cut.append(dict(benchmark=B, geometry=gm, sct_z=s, dw_convention=w, step=j, stage=nm, events=v))
    o = pd.DataFrame(out); o.to_csv(f"{T}/confirmation_efficiencies.csv", index=False)
    pd.DataFrame(cut).to_csv(f"{T}/confirmation_cutflows.csv", index=False)
    json.dump(dict(counts=counts, technical_exceptions=d[d.technical.notna()].groupby("bench").i.nunique().to_dict()),
              open(f"{T}/confirmation_counts.json", "w"), indent=1)
    pd.set_option("display.width", 250)
    print(json.dumps(counts))
    print(o[(o.dw_convention == "W1")].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
