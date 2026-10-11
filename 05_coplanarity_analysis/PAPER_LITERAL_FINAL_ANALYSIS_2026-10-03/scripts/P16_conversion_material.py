#!/usr/bin/env python3
"""Test (review point 1): can electron material effects make converted-photon planes 'thick' when there is NO SCT z smearing?
Existing 9139 photons, same per-event seeds as P9/P9d (z0, 16 SCT normals); |eta|<1.8 acceptance; fit from the primary vertex.
e+/e- are propagated layer by layer with an exact helix between layers; at each layer crossing (after recording the hit):
  BREM : deterministic bremsstrahlung energy loss E -> E*exp(-t_eff) (photon tangential, direction unchanged), as in the
         simulation the paper cites (arXiv:1612.00850 App. A: Bethe-Bloch most-probable loss + bremsstrahlung, radiation lengths
         from Andreazza:2009zz -- values not available here). Ionisation loss (~0.3 MeV per layer) is neglected.
  MS   : Highland multiple scattering, theta0 = 13.6 MeV/(beta p) sqrt(t)(1 + 0.038 ln t), two Gaussian kicks (NOT in the cited
         simulation; tested because it is the physical effect proposed in the review). Seed SeedSequence([99,1708,i,1]).
  t_eff = t / |cos(incidence)|, with t = x/X0 per layer an ASSUMPTION: scanned over {0.01, 0.03, 0.05}.
Validation: with t = 0 the result must equal P9d (conversion_acceptance_A_per_event.csv) event by event for SCT z 0 and 1160 um.
Output: tables/conversion_material_per_event.csv, tables/conversion_material_summary.csv"""
import os, sys, math, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
from scipy.optimize import brentq
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("p9", f"{HERE}/P9_literal_conversion.py"); p9 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p9)
CLIGHT_CM_NS = 29.9792458; ME = p9.ELECTRON_MASS_GEV; BT = 2.0
CONFIGS = [("Z0", 0.0, "none"), ("Z1160", 0.0, "none")] + [("Z0", t, m) for t in (0.01, 0.03, 0.05) for m in ("brem", "brem+ms")] + [("Z1160", 0.03, "brem+ms")]

def next_crossing(x, p, q, rho):
    """Exact helix from x (cm) with momentum p (GeV), charge q, to the first outward crossing of radius rho. Returns (pos, p_new, path_cm) or None."""
    pT = math.hypot(p[0], p[1]); Rc = pT * 100.0 / (0.299792458 * BT); s = -q
    ux, uy = p[0] / pT, p[1] / pT
    def pos(a):
        sa, ca = math.sin(s * a), math.cos(s * a)
        return x[0] + Rc * (ux * sa - uy * (1 - ca)) / s, x[1] + Rc * (ux * (1 - ca) + uy * sa) / s
    f = lambda a: math.hypot(*pos(a)) - rho
    grid = np.linspace(0, 2 * math.pi, 2001)[1:]; prev = f(1e-12); a0 = 1e-12
    for a in grid:
        v = f(a)
        if prev < 0 <= v:
            a = brentq(f, a0, a, xtol=1e-15, rtol=1e-15); X, Y = pos(a)
            Z = x[2] + Rc * a * p[2] / pT; th = s * a
            return np.array([X, Y, Z]), np.array([pT * (ux * math.cos(th) - uy * math.sin(th)), pT * (ux * math.sin(th) + uy * math.cos(th)), p[2]]), Rc * a * math.sqrt(1 + (p[2] / pT) ** 2)
        prev, a0 = v, a
    return None

def track(cp, p, q, t, mode, rng):
    """Crossings [(layer dict, x, y, z, t_ns)] of the 8 layers with material effects applied after each hit."""
    out, x, p, tns = [], np.array(cp, float), np.array(p, float), 0.0
    for L in p9.ag.LAYERS:
        r = next_crossing(x, p, q, L["r_cm"])
        if r is None: break
        x, p_new, path = r; E = math.sqrt(p_new @ p_new + ME * ME); tns += path / (CLIGHT_CM_NS * math.sqrt(p_new @ p_new) / E)
        if tns > 25.0: break
        out.append((L, x[0], x[1], x[2], tns)); p = p_new
        if t > 0:
            rhat = np.array([x[0], x[1], 0.0]) / math.hypot(x[0], x[1]); cosi = abs(p @ rhat) / math.sqrt(p @ p); te = t / max(cosi, 1e-3)
            if "brem" in mode: p = p * math.exp(-te)
            if "ms" in mode:
                pm = math.sqrt(p @ p); beta = pm / math.sqrt(pm * pm + ME * ME); th0 = 0.0136 / (beta * pm) * math.sqrt(te) * (1 + 0.038 * math.log(te))
                d = p / pm; e1 = np.cross(d, [0, 0, 1.0]); e1 /= np.linalg.norm(e1); e2 = np.cross(d, e1)
                a1, a2 = rng.normal(0, th0, 2); d = d + a1 * e1 + a2 * e2; d /= np.linalg.norm(d); p = pm * d
    return out

def event(i):
    r = p9.PH.iloc[i]; rng = np.random.default_rng(np.random.SeedSequence([99, 1708, i])); z0 = rng.normal(0.0, 4.5); g = rng.standard_normal(16).reshape(2, 4, 2)
    cp = p9.find_conversion_point(r.px, r.py, r.pz, r.E, z0, p9.ag.BEAMPIPE_RADIUS_CM); rows = []
    for sct, t, mode in CONFIGS:
        name = f"{sct}_t{t:g}_{mode}"
        if cp is None: rows.append(dict(event=i, config=name, status="no_conversion_point")); continue
        rms = np.random.default_rng(np.random.SeedSequence([99, 1708, i, 1])); p = np.array([r.px, r.py, r.pz]) / 2.0
        cross = [(body,) + c for body, q in ((0, -1.0), (1, 1.0)) for c in track(cp, p, q, t, mode, rms)]
        raw = []
        for body, L, x, y, z, tt in cross:
            if not p9.ld.accepted(L["name"], math.hypot(x, y), z, "A"): continue
            rphi = L["r_cm"] * math.atan2(y, x)
            if L["is_pixel"]: rh, zh, ir, iz = p9.quantize_pixel(rphi, z, L["eff_res_rphi_um"], L["eff_res_z_um"])
            else:
                g1, g2 = g[body, p9.IDX[L["name"]] - 5]; rh, zh, ir, iz = rphi + 34e-4 * g1, z + p9.ld.SCT_Z_SIGMA_CM[sct] * g2, None, None
            ph = rh / L["r_cm"]
            raw.append({"layer": L["name"], "layer_r_cm": L["r_cm"], "quirk_index": body, "t_ns": tt, "x": L["r_cm"] * math.cos(ph), "y": L["r_cm"] * math.sin(ph),
                        "z": zh, "is_pixel": L["is_pixel"], "idx_rphi": ir, "idx_z": iz})
        res = p9.analyse(p9.merge_neighboring_pixel_hits(raw), (0.0, 0.0, z0))
        rows.append(dict(event=i, config=name, sct=sct, t=t, mode=mode, status="ok", n_raw_hits=len(raw), **res))
    return rows

def init(): p9._init()
if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    init(); N = len(p9.PH) if n is None else n
    with mp.Pool(10, initializer=init) as pool: out = [r for rr in pool.imap_unordered(event, range(N), chunksize=40) for r in rr]
    d = pd.DataFrame(out).sort_values(["config", "event"])
    ref = pd.read_csv(f"{T}/conversion_acceptance_A_per_event.csv")
    for sct, cfg in (("Z0", "A_Z0_PV"), ("Z1160", "A_Z1160_PV")):
        a = d[d.config == f"{sct}_t0_none"].set_index("event"); b = ref[ref.config == cfg].set_index("event").loc[a.index]
        for c in ("plane", "mult", "final"): assert (a[c].astype(str) == b[c].astype(str)).all(), (sct, c)
        m = a.plane.astype(str) == "True"; dd = np.nanmax(np.abs(a.ds[m] - b.ds[m])) if m.any() else 0
        print(f"validation t=0 {sct}: decisions identical to P9d; max |ds diff| = {dd:.2e} cm")
    tag = "" if n is None else f"_first{n}"
    d.to_csv(f"{T}/conversion_material_per_event{tag}.csv", index=False)
    TR = lambda s: s.astype(str) == "True"; sm = []
    for c, g in d[d.status == "ok"].groupby("config", sort=False):
        pl = g[TR(g.plane)]; pm = g[TR(g.plane) & TR(g.mult)]
        sm.append(dict(config=c, n=len(g), planes=len(pl), ds_median_planes_um=pl.ds.median() * 1e4, frac_planes_below_cut=(pl.ds < 0.01).mean(),
                       mult_pass=len(pm), mult_frac=len(pm) / len(g), ds_median_mult_um=pm.ds.median() * 1e4 if len(pm) else np.nan,
                       frac_mult_below_cut=(pm.ds < 0.01).mean() if len(pm) else np.nan, final=int(TR(g.final).sum())))
    S = pd.DataFrame(sm); S.to_csv(f"{T}/conversion_material_summary{tag}.csv", index=False); print(S.round(4).to_string())
