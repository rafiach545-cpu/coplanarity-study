#!/usr/bin/env python3
"""07 background step M01 (2026-11-15, decision D2): photon conversion probability from the ATLAS Run 2 material instead of the flat 1%.
Photons: the 13.6 TeV Z(nunu)+gamma+j sample of Stage 2 (06_publication/S2_.../inputs/zgamma_photons_13p6TeV.csv, 9130 photons after MET > 200 GeV).
Vertex: (0, 0, z0), z0 ~ N(0, 45 mm) (R10 beam spot), own seed SeedSequence([7, 1, event]).
Photon path: straight line (neutral, no field). Material surfaces crossed in path order, each infinitely thin (as R11 App. A):
  beam pipe (cylinder r = 23.9 mm, middle of 23.5-24.3 mm, R6; all z), IBL (33.25 mm, |z| < 330.15), pixel barrel 1-3 (|z| < 400.5),
  pixel disks (|z| = 495/580/650, 88.8 < r < 149.6), SCT barrel 1-4 (|z| < 749), SCT disks (9 per side, r from the innermost ring present to 560 mm).
  Geometry from geometry/atlas_run2_id_geometry.csv. x/X0 (normal incidence) from geometry/atlas_run2_id_material.csv via the CONFIG below.
Per surface: t = (x/X0) / |cos(alpha)| (barrel: |cos alpha| = sin(theta); disk: |cos theta|), conversion probability on that surface
  P_i = prod_{j<i} exp(-7 t_j / 9) * (1 - exp(-7 t_i / 9))   (R7 Eq. 34.32).
Regions: 'before IBL' (beam pipe: the e+e- pair can hit all 8 stations), 'IBL', 'pixel' (after IBL, inside pixel), 'SCT'.
Variants: nominal (IBL 1.88% R2, beam pipe Be wall 0.227% DERIVED), IBL 1.5% (R6), beam pipe 0.45% (Run 1 pipe, R3 Table 4.15 at eta = 0, used as
  normal-incidence value), beam pipe x2 (crude allowance for the polyimide tapes not in the DERIVED value).
Output: tables/M01_conversion_per_photon.csv, tables/M01_conversion_summary.csv, logs/M01_conversion_probability.log (stdout)."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; BASE = "/home/rafia/coplanarity_study"
PH = f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/inputs/zgamma_photons_13p6TeV.csv"
G = pd.read_csv(f"{ROOT}/geometry/atlas_run2_id_geometry.csv"); M = pd.read_csv(f"{ROOT}/geometry/atlas_run2_id_material.csv").set_index("component")
X = lambda c: float(M.loc[c, "x_over_X0_normal_incidence"])
VARIANTS = {"nominal": dict(bp=X("beam_pipe_Be_wall"), ibl=X("IBL_staves")),
            "IBL_1p5": dict(bp=X("beam_pipe_Be_wall"), ibl=X("IBL_staves_alt")),
            "BP_run1_0p45": dict(bp=X("beam_pipe_Run1_reference"), ibl=X("IBL_staves")),
            "BP_x2": dict(bp=2 * X("beam_pipe_Be_wall"), ibl=X("IBL_staves"))}
PIX_L = X("pixel_barrel_3layers_total") / 3; SCT_L = X("sct_barrel_layer"); SCT_D = X("sct_endcap_disk"); PIX_D = PIX_L   # pixel disk: INFERRED (D2)
BEAMSPOT_MM = 45.0

def surfaces(v):
    s = [("before IBL", "cyl", 23.9, np.inf, v["bp"])]
    for r in G[G.region == "barrel"].itertuples():
        s.append(("IBL" if r.name == "IBL" else ("pixel" if r.element == "pixel" else "SCT"), "cyl", r.r_mm, r.half_z_mm,
                  v["ibl"] if r.name == "IBL" else (PIX_L if r.element == "pixel" else SCT_L)))
    for r in G[(G.region == "endcap")].itertuples():
        for sd in (1, -1): s.append(("pixel", "disk", sd * r.z_mm, (r.r_min_mm, r.r_max_mm), PIX_D))
    rings = G[G.region == "endcap_ring"].copy(); rings["disk"] = rings.name.str.extract(r"SCTD(\d)")[0]
    for d, g in rings.groupby("disk"):
        for sd in (1, -1): s.append(("SCT", "disk", sd * g.z_mm.iloc[0], (g.r_min_mm.min(), g.r_max_mm.max()), SCT_D))
    return s

def per_photon(p, z0, surf):
    pt = np.hypot(p[0], p[1]); pm = np.linalg.norm(p); st, ct = pt / pm, p[2] / pm; hits = []
    for reg, kind, a, b, x0 in surf:
        if kind == "cyl":
            if st <= 0: continue
            L = a / st; z = z0 + L * ct
            if abs(z) < b: hits.append((L, reg, x0 / st))
        else:
            if ct == 0 or np.sign(a - z0) != np.sign(ct): continue
            L = (a - z0) / ct; r = L * st
            if b[0] <= r <= b[1]: hits.append((L, reg, x0 / abs(ct)))
    hits.sort(); surv = 1.0; out = {"before IBL": 0.0, "IBL": 0.0, "pixel": 0.0, "SCT": 0.0}
    for L, reg, t in hits:
        pc = surv * (1 - np.exp(-7 * t / 9)); out[reg] += pc; surv *= np.exp(-7 * t / 9)
    return out

ph = pd.read_csv(PH); rows = []
z0 = np.array([np.random.default_rng(np.random.SeedSequence([7, 1, int(e)])).normal(0, BEAMSPOT_MM) for e in ph.event])
eta = np.arcsinh(ph.pz / np.hypot(ph.px, ph.py))
for vn, v in VARIANTS.items():
    surf = surfaces(v)
    for i, r in enumerate(ph.itertuples()):
        o = per_photon(np.array([r.px, r.py, r.pz]), z0[i], surf)
        rows.append(dict(variant=vn, event=r.event, eta=eta[i], z0_mm=z0[i], E=r.E, **{f"P_{k.replace(' ', '_')}": val for k, val in o.items()}))
T = pd.DataFrame(rows); T["P_total"] = T[[c for c in T.columns if c.startswith("P_")]].sum(axis=1)
os.makedirs(f"{ROOT}/tables", exist_ok=True); T.to_csv(f"{ROOT}/tables/M01_conversion_per_photon.csv", index=False)
T["abs_eta_bin"] = pd.cut(T.eta.abs(), [0, 0.5, 1.0, 1.5, 1.8, 2.5, 99], right=False)
S = T.groupby(["variant", "abs_eta_bin"], observed=True)[["P_before_IBL", "P_IBL", "P_pixel", "P_SCT", "P_total"]].mean()
S["n_photons"] = T.groupby(["variant", "abs_eta_bin"], observed=True).size()
A = T.groupby("variant")[["P_before_IBL", "P_IBL", "P_pixel", "P_SCT", "P_total"]].mean(); A["n_photons"] = T.groupby("variant").size()
A18 = T[T.eta.abs() < 1.8].groupby("variant")[["P_before_IBL", "P_IBL", "P_total"]].mean().add_suffix("_eta<1.8")
Sum = A.join(A18); Sum["ratio_before_IBL_to_flat_1pct"] = Sum.P_before_IBL / 0.01
Sum.to_csv(f"{ROOT}/tables/M01_conversion_summary.csv")
pd.set_option("display.width", 220)
print("Mean conversion probability per photon (all 9130 photons; 'before IBL' = beam pipe):"); print(Sum.round(5).to_string())
print("\nNominal, by |eta|:"); print(S.loc["nominal"].round(5).to_string())
print("\nCheck vs R12 ('about 20% of photons at low |eta| convert in the ID', ID = up to r ~ 800 mm incl. TRT): our silicon-only total at |eta| < 0.5 =",
      round(float(S.loc[("nominal", T.abs_eta_bin.cat.categories[0]), "P_total"]), 4), "(expected below 20%: TRT, services and passive tubes not included)")
print("M01_EXIT=0")
