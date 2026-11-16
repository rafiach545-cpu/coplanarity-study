#!/usr/bin/env python3
"""07 (2026-11-15): ATLAS Run 2 Inner Detector silicon geometry (barrel cylinders + end-cap disks/rings), read from atlas_run2_id_geometry.csv.
Every number comes from that CSV, and every CSV row names its reference (references/REFERENCES.md). Nothing is hard-coded here.

Model (step 1 of the 07 plan; deliberately simple, each simplification listed):
  - barrel layers: cylinders at the average active radius, active |z| < half_z (as Stages 1-2; tilted staves/modules NOT yet modelled)
  - end-cap layers: flat disks (pixel) or rings (SCT) at |z| = z_disk + ring_dz on both sides, active for r_min <= r <= r_max
    (SCT rings overlap in r, so one track can cross two rings of the same disk, as in ATLAS)
  - phi coverage is full (gaps between modules/sectors NOT yet modelled)
Units: mm.
API:
  ELEMENTS                      list of dicts (one per barrel layer / disk / ring), side-resolved for end-caps
  straight_crossings(eta, z0, phi=0)  crossings of a straight line from (0, 0, z0) -> list of (element, x, y, z)
  trajectory_crossings(x, y, z, t)    crossings of a sampled trajectory (arrays, mm and ns) -> list of (element, x, y, z, t), time ordered
"""
import os, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = f"{HERE}/atlas_run2_id_geometry.csv"


def load(csv=CSV):
    g = pd.read_csv(csv)
    out = []
    for r in g.itertuples():
        if r.region == "barrel":
            out.append(dict(name=r.name, kind="barrel", det=r.element, r=float(r.r_mm), half_z=float(r.half_z_mm),
                            res_rphi_um=float(r.res_rphi_um), res_long_um=float(r.res_long_um)))
        elif r.region in ("endcap", "endcap_ring"):
            dz = float(r.ring_dz_mm) if pd.notna(r.ring_dz_mm) else 0.0
            for side in (+1, -1):
                out.append(dict(name=f"{r.name}_{'A' if side > 0 else 'C'}", kind="disk", det=r.element, side=side,
                                z=side * (float(r.z_mm) + dz), r_min=float(r.r_min_mm), r_max=float(r.r_max_mm),
                                res_rphi_um=float(r.res_rphi_um), res_long_um=float(r.res_long_um)))
    return out


ELEMENTS = load()


def straight_crossings(eta, z0=0.0, phi=0.0):
    """Straight line from (0, 0, z0) with pseudorapidity eta (w.r.t. the line's own origin) and azimuth phi."""
    th = 2.0 * np.arctan(np.exp(-eta)); ux, uy, uz = np.sin(th) * np.cos(phi), np.sin(th) * np.sin(phi), np.cos(th)
    out = []
    for e in ELEMENTS:
        if e["kind"] == "barrel":
            if np.sin(th) <= 0: continue
            s = e["r"] / np.sin(th); z = z0 + s * uz
            if abs(z) < e["half_z"]: out.append((e, s * ux, s * uy, z))
        else:
            if uz == 0 or np.sign(e["z"] - z0) != np.sign(uz): continue
            s = (e["z"] - z0) / uz; r = s * np.sin(th)
            if e["r_min"] <= r <= e["r_max"]: out.append((e, s * ux, s * uy, e["z"]))
    return out


def trajectory_crossings(x, y, z, t):
    """All crossings (both directions) of the sampled trajectory with every element, linear interpolation between samples."""
    x, y, z, t = map(np.asarray, (x, y, z, t)); r = np.hypot(x, y); out = []
    for e in ELEMENTS:
        f = r - e["r"] if e["kind"] == "barrel" else z - e["z"]
        k = np.nonzero(np.sign(f[:-1]) * np.sign(f[1:]) < 0)[0]
        for i in k:
            a = f[i] / (f[i] - f[i + 1]); xc, yc, zc, tc = (v[i] + a * (v[i + 1] - v[i]) for v in (x, y, z, t))
            if e["kind"] == "barrel":
                ok = abs(zc) < e["half_z"]
            else:
                rc = np.hypot(xc, yc); ok = e["r_min"] <= rc <= e["r_max"]
            if ok: out.append((e, xc, yc, zc, tc))
    return sorted(out, key=lambda c: c[4])
