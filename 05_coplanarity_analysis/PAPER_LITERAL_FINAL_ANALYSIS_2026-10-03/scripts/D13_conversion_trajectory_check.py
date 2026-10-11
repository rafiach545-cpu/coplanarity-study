#!/usr/bin/env python3
# NOTE 2026-10-11: second body = same momentum, charge 0 (a near-zero momentum made simulate_quirk_hits size t_max from speed 1e-6 and under-resolve both RK4 runs; first run invalid; its output was deleted 2026-10-11).
"""No-string (Lambda = 0) e+e- trajectories from photon conversions (2026-10-11), with the real photon momenta (zgamma_photons.csv, equal energy sharing).
Layer crossing points (x, y, z) of each lepton for the 8 layers from four propagators:
  H  analytic helix, helix_propagation.find_helix_layer_crossings   (used by P9, P10, P10e/f)
  N  analytic helix by root finding, P16 next_crossing (no material) (used by P17/P17b/P17c, the report's [34] background)
  R5 RK4 with Lambda = 0, 5000 steps for the whole track (trajectory_to_hits.simulate_quirk_hits, legacy convert_and_analyze v1 path)
  RF RK4 with Lambda = 0, 200 000 steps (reference)
Also the gyroradius R = pT / (0.3 B) of each lepton. Sample: first 300 photons with a conversion point. Output: tables/D13_conversion_trajectories.csv"""
import os, sys, math, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import literal_detector as ld, atlas_geometry as ag
from helix_propagation import find_helix_layer_crossings
import trajectory_to_hits as tth
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim"); import quirk_trajectory_optimized_v2 as v2
tth.integrate_trajectory = v2.integrate_trajectory_fast_v2
_s = importlib.util.spec_from_file_location("p16", f"{HERE}/P16_conversion_material.py"); p16 = importlib.util.module_from_spec(_s); _s.loader.exec_module(p16)
from convert_and_analyze import find_conversion_point, ELECTRON_MASS_GEV as ME
PH = pd.read_csv("/home/rafia/coplanarity_study/02_backgrounds/photon_conversion/zgamma_photons.csv"); R_ = [L["r_cm"] for L in ag.LAYERS]; HB = 1.973269804e-14
def rk4(cp, p, q, nsteps):
    E = math.sqrt(p @ p + ME * ME)
    _, tr = tth.simulate_quirk_hits((*p, E), (*p, E), mass_gev=ME, Lambda_gev=0.0, B_tesla=2.0, charge1=q, charge2=0.0, rng=np.random.default_rng(0),
                                    x0_override_cm=cp, max_layer_r_cm=60.0, n_steps_no_string=nsteps)
    x = np.asarray(tr["x1"]) * HB; out = {}
    for L in ag.LAYERS:
        c = tth.find_layer_crossing(x, tr["t_gev_inv"], L["r_cm"])
        if c is not None: out[L["r_cm"]] = np.asarray(c[0])
    return out
def photon(i):
    tth.integrate_trajectory = v2.integrate_trajectory_fast_v2
    r = PH.iloc[i]; rng = np.random.default_rng(np.random.SeedSequence([99, 1708, i])); z0 = rng.normal(0.0, 4.5)
    cp = find_conversion_point(r.px, r.py, r.pz, r.E, z0, ag.BEAMPIPE_RADIUS_CM); rows = []
    if cp is None: return dict(photon=i, rows=rows)
    for q in (-1.0, 1.0):
        p = np.array([r.px, r.py, r.pz]) / 2.0; pT = math.hypot(p[0], p[1])
        H = {k: np.asarray(v[0]) for k, v in find_helix_layer_crossings(np.asarray(cp, float), p, ME, q, 2.0, R_).items()}
        N = {}; x = np.asarray(cp, float); pp = p.copy()
        for L in ag.LAYERS:
            c = p16.next_crossing(x, pp, q, L["r_cm"])
            if c is None: break
            x, pp, _ = c; N[L["r_cm"]] = x.copy()
        R5 = rk4(cp, p, q, 5000); RF = rk4(cp, p, q, 200000)
        for Rl in R_:
            ref = RF.get(Rl)
            if ref is None: continue
            row = dict(photon=i, charge=q, pT_GeV=pT, gyroradius_cm=pT / (0.299792458 * 2.0) * 100, layer_r_cm=Rl)
            for nm, D in (("H", H), ("N", N), ("R5", R5)):
                row[f"{nm}_found"] = Rl in D; row[f"{nm}_dist_um"] = float(np.linalg.norm(D[Rl] - ref) * 1e4) if Rl in D else float("nan")
            rows.append(row)
    return dict(photon=i, rows=rows)
if __name__ == "__main__":
    import json, multiprocessing as mp; LOG = f"{HERE}/../logs/D13_photons.jsonl"; done = set()   # append-only checkpoint per photon
    if os.path.exists(LOG): done = {json.loads(l)["photon"] for l in open(LOG)}
    todo = [i for i in range(300) if i not in done]; print("photons to run", len(todo), flush=True)
    with mp.Pool(10) as pool, open(LOG, "a") as fh:
        for k, rr in enumerate(pool.imap_unordered(photon, todo), 1):
            fh.write(json.dumps(rr) + "\n"); fh.flush()
            if k % 20 == 0: print(f"{k}/{len(todo)}", flush=True)
    rows = [x for l in open(LOG) for x in json.loads(l)["rows"]]
    d = pd.DataFrame(rows); d.to_csv(f"{HERE}/../tables/D13_conversion_trajectories.csv", index=False)
    lep = d.drop_duplicates(["photon", "charge"])
    print(f"photons {d.photon.nunique()}, leptons {len(lep)}: lepton pT median {lep.pT_GeV.median():.2f} GeV [16-84%: {lep.pT_GeV.quantile(.16):.2f}-{lep.pT_GeV.quantile(.84):.2f}], min {lep.pT_GeV.min():.3f}")
    print(f"gyroradius median {lep.gyroradius_cm.median()/100:.1f} m [16-84%: {lep.gyroradius_cm.quantile(.16)/100:.2f}-{lep.gyroradius_cm.quantile(.84)/100:.1f} m], min {lep.gyroradius_cm.min():.1f} cm; leptons with R < 1 m: {int((lep.gyroradius_cm < 100).sum())}")
    for nm, lab in (("H", "analytic helix (P9/P10)"), ("N", "root-finding helix (P17, report)"), ("R5", "RK4 5000 steps (legacy v1)")):
        x = d[f"{nm}_dist_um"]; print(f"{lab:34s}: crossings found {int(d[f'{nm}_found'].sum())}/{len(d)}; distance to reference: median {x.median():.3g} um, 99% {x.quantile(.99):.3g} um, max {x.max():.3g} um")
    low = d[d.gyroradius_cm < 100]
    if len(low): print(f"leptons with R < 1 m: R5 max distance {low.R5_dist_um.max():.3g} um, N max {low.N_dist_um.max():.3g} um")
