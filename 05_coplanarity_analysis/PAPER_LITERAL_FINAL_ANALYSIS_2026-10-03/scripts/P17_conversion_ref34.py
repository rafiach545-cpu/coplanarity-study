#!/usr/bin/env python3
"""Converted photons with the detector model of the simulation the paper cites for this background (arXiv:1612.00850 App. A,
paper ref. [34]): exact helix between layers; at every layer crossing (after the hit) deterministic bremsstrahlung
E -> E exp(-t_eff) (all brem energy into one tangential photon, direction unchanged) and Bethe-Bloch most-probable ionisation
loss (approximated as 0.28 MeV per mm of silicon-equivalent material; negligible for GeV electrons); NO multiple scattering
(not in [34]); 25 ns time-of-flight stop. Radiation lengths per layer: tables/material_X0_per_layer_ref27.csv (derived from the
reference [34] cites, Andreazza:2009zz = ATL-COM-PHYS-2008-105 = ATL-PHYS-PUB-2009-002 = paper ref. [27], Fig. 3).
t_eff = t / |cos(incidence)|. Same photons and per-event seeds as P9/P9d. Fit from the primary vertex.
Configs: geometry B (Ref. [27] lengths, primary as of 2026-10-05) and A, SCT z 0 and 1160 um; material on/off (off = validation).
Output: tables/conversion_ref34_per_event.csv, tables/conversion_ref34_summary.csv"""
import os, sys, math, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("p16", f"{HERE}/P16_conversion_material.py"); p16 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p16)
p9 = p16.p9; ME = p9.ELECTRON_MASS_GEV; CL = p16.CLIGHT_CM_NS
MAT = pd.read_csv(f"{T}/material_X0_per_layer_ref27.csv")
X0 = {}
for r in MAT.itertuples():
    for nm in (r.layer_names if isinstance(r.layer_names, str) else "").split(): X0[nm] = float(r.per_layer_X0_normal_incidence)
SI_X0_MM, DEDX_MP_GEV_PER_MM = 93.7, 0.28e-3
CONFIGS = [(g, s, m) for g in ("B", "A") for s in ("Z0", "Z1160") for m in (False, True)]

def track34(cp, p, q, material):
    out, x, p, tns = [], np.array(cp, float), np.array(p, float), 0.0
    for L in p9.ag.LAYERS:
        r = p16.next_crossing(x, p, q, L["r_cm"])
        if r is None: break
        x, p_new, path = r; pm = math.sqrt(p_new @ p_new); E = math.sqrt(pm * pm + ME * ME); tns += path / (CL * pm / E)
        if tns > 25.0: break
        out.append((L, x[0], x[1], x[2], tns)); p = p_new
        if material:
            rhat = np.array([x[0], x[1], 0.0]) / math.hypot(x[0], x[1]); cosi = max(abs(p @ rhat) / pm, 1e-3); te = X0[L["name"]] / cosi
            Ek = E * math.exp(-te) - DEDX_MP_GEV_PER_MM * te * SI_X0_MM          # bremsstrahlung, then most-probable ionisation
            if Ek - ME < 0.1 * ME: break                                          # [34]: stop below 10% of the mass in kinetic energy
            p = p * math.sqrt(max(Ek * Ek - ME * ME, 0.0)) / pm
    return out

def event(i):
    r = p9.PH.iloc[i]; rng = np.random.default_rng(np.random.SeedSequence([99, 1708, i])); z0 = rng.normal(0.0, 4.5); g = rng.standard_normal(16).reshape(2, 4, 2)
    cp = p9.find_conversion_point(r.px, r.py, r.pz, r.E, z0, p9.ag.BEAMPIPE_RADIUS_CM); rows = []
    for geom, sct, mat in CONFIGS:
        name = f"{geom}_{sct}_{'ref34' if mat else 'nomat'}"
        if cp is None: rows.append(dict(event=i, config=name, status="no_conversion_point")); continue
        p = np.array([r.px, r.py, r.pz]) / 2.0
        cross = [(body,) + c for body, q in ((0, -1.0), (1, 1.0)) for c in track34(cp, p, q, mat)]
        raw = []
        for body, L, x, y, z, tt in cross:
            if not p9.ld.accepted(L["name"], math.hypot(x, y), z, geom): continue
            rphi = L["r_cm"] * math.atan2(y, x)
            if L["is_pixel"]: rh, zh, ir, iz = p9.quantize_pixel(rphi, z, L["eff_res_rphi_um"], L["eff_res_z_um"])
            else:
                g1, g2 = g[body, p9.IDX[L["name"]] - 5]; rh, zh, ir, iz = rphi + 34e-4 * g1, z + p9.ld.SCT_Z_SIGMA_CM[sct] * g2, None, None
            ph = rh / L["r_cm"]
            raw.append({"layer": L["name"], "layer_r_cm": L["r_cm"], "quirk_index": body, "t_ns": tt, "x": L["r_cm"] * math.cos(ph), "y": L["r_cm"] * math.sin(ph),
                        "z": zh, "is_pixel": L["is_pixel"], "idx_rphi": ir, "idx_z": iz})
        res = p9.analyse(p9.merge_neighboring_pixel_hits(raw), (0.0, 0.0, z0))
        rows.append(dict(event=i, config=name, geom=geom, sct=sct, material=mat, status="ok", n_raw_hits=len(raw), **res))
    return rows

if __name__ == "__main__":
    p9._init()
    with mp.Pool(10, initializer=p9._init) as pool: out = [r for rr in pool.imap_unordered(event, range(len(p9.PH)), chunksize=40) for r in rr]
    d = pd.DataFrame(out).sort_values(["config", "event"])
    ref = pd.read_csv(f"{T}/conversion_acceptance_A_per_event.csv"); old = pd.concat(pd.read_csv(f) for f in __import__("glob").glob(f"{HERE}/../logs/P9_chunks_LITERAL/chunk_*.csv"))
    checks = [("A_Z0_nomat", ref[ref.config == "A_Z0_PV"]), ("A_Z1160_nomat", ref[ref.config == "A_Z1160_PV"]), ("B_Z0_nomat", old[old.config == "SYS_Z0"]), ("B_Z1160_nomat", old[old.config == "LITERAL"])]
    for cfg, b in checks:
        a = d[d.config == cfg].set_index("event"); b = b.set_index("event").loc[a.index]
        for c in ("plane", "mult", "final"): assert (a[c].astype(str) == b[c].astype(str)).all(), (cfg, c)
        print(f"validation {cfg}: plane/mult/final identical to the earlier run")
    d.to_csv(f"{T}/conversion_ref34_per_event.csv", index=False)
    TR = lambda s: s.astype(str) == "True"; sm = []
    for c, g in d[d.status == "ok"].groupby("config", sort=False):
        pl = g[TR(g.plane)]; pm = g[TR(g.plane) & TR(g.mult)]
        sm.append(dict(config=c, n=len(g), planes=len(pl), ds_median_planes_um=pl.ds.median() * 1e4, mult_pass=len(pm), mult_frac=len(pm) / len(g),
                       ds_median_mult_um=pm.ds.median() * 1e4 if len(pm) else np.nan, frac_mult_below_cut=(pm.ds < 0.01).mean() if len(pm) else np.nan, final=int(TR(g.final).sum())))
    S = pd.DataFrame(sm); S.to_csv(f"{T}/conversion_ref34_summary.csv", index=False); print(S.round(4).to_string())
