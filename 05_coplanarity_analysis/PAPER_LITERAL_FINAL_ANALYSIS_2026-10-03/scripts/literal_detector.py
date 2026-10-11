#!/usr/bin/env python3
"""
Literal detector response shared by all literal background analyses (Phases 8-10).

Only ONE thing differs from the frozen project hit response: the acceptance.
  frozen project : per-hit |eta_lab| < 1.8 (infinite cylinders)
  literal        : finite barrel cylinders from ref [27] -- pixel |z| < 40.05 cm, SCT |z| < 74.9 cm,
                   IBL |z| < 33.015 cm (IBL length INFERRED, arXiv:1803.00844); no eta cut.
Everything else is the frozen project response, unchanged and imported:
  pixel-centre quantisation (trajectory_to_hits.quantize_pixel), SCT Gaussian sigma = 2 x intrinsic accuracy
  of ref [27] (34 um R-phi; z sigma configurable, literal 1160 um), neighbouring-pixel merging
  (trajectory_to_hits.merge_neighboring_pixel_hits), helix propagation of ordinary charged particles
  (helix_propagation.find_helix_layer_crossings), 25 ns per-hit time-of-flight cut for pile-up particles.
`literal_pileup_particle_hits` is a line-for-line copy of pileup_hits.pileup_particle_hits with the acceptance
line replaced and the SCT z sigma parameterised; it is bound into pileup_hits_suppressed at runtime
(`install`) so the frozen sampling + track-suppression code runs unchanged.
"""
import sys
import numpy as np

BASE = "/home/rafia/coplanarity_study"
for p in ("04_detector_sim", "05_coplanarity_analysis", "02_backgrounds/pileup", "02_backgrounds/photon_conversion", "03_trajectory_sim"):
    sys.path.insert(0, f"{BASE}/{p}")
import atlas_geometry as ag                    # noqa: E402
import trajectory_to_hits as tth               # noqa: E402
import pileup_hits as ph                       # noqa: E402
import pileup_hits_suppressed as phs           # noqa: E402
from helix_propagation import find_helix_layer_crossings   # noqa: E402

HALF_CM = {"L1_IBL": 33.015, "L2_PixelB0": 40.05, "L3_PixelB1": 40.05, "L4_PixelB2": 40.05,
           "L5_SCT_B3": 74.9, "L6_SCT_B4": 74.9, "L7_SCT_B5": 74.9, "L8_SCT_B6": 74.9}
SCT_Z_SIGMA_CM = {"Z1160": 0.1160, "Z580": 0.0580, "Z34": 0.0034, "Z0": 0.0}
CONFIG = {"geometry": "B", "sct": "Z1160"}


def accepted(layer_name, r_cm, z_cm, geometry):
    if geometry == "B":
        return abs(z_cm) < HALF_CM[layer_name]
    return abs(ag.eta_from_theta(np.arctan2(r_cm, z_cm))) <= ag.FIDUCIAL_ETA_MAX


def literal_pileup_particle_hits(px, py, pz, m, charge_e, vertex_cm, particle_tag, rng, B_tesla=2.0):
    p_gev = np.array([px, py, pz])
    x0_cm = np.asarray(vertex_cm, dtype=float)
    crossings = find_helix_layer_crossings(x0_cm, p_gev, m, charge_e, B_tesla, ph.LAYER_RADII_CM)
    hits = []
    for layer in ag.LAYERS:
        result = crossings.get(layer["r_cm"])
        if result is None:
            continue
        xyz, t_ns = result
        if t_ns is None or t_ns > ph.PILEUP_HIT_TIMING_CUT_NS:
            continue
        x, y, z = xyz
        r = np.hypot(x, y)
        if not accepted(layer["name"], r, z, CONFIG["geometry"]):      # <-- the only changed line
            continue
        phi = np.arctan2(y, x)
        rphi = layer["r_cm"] * phi
        if layer["is_pixel"]:
            rphi_hit, z_hit, idx_rphi, idx_z = tth.quantize_pixel(rphi, z, layer["eff_res_rphi_um"], layer["eff_res_z_um"])
        else:
            sigma_rphi_cm = layer["eff_res_rphi_um"] * 1e-4
            sigma_z_cm = SCT_Z_SIGMA_CM[CONFIG["sct"]]
            rphi_hit = rphi + rng.normal(0.0, sigma_rphi_cm)
            z_hit = z + rng.normal(0.0, 1.0) * sigma_z_cm      # same draw count/order as the frozen code
            idx_rphi = idx_z = None
        phi_hit = rphi_hit / layer["r_cm"]
        hits.append({"layer": layer["name"], "layer_r_cm": layer["r_cm"], "quirk_index": particle_tag, "t_ns": t_ns,
                     "x": layer["r_cm"] * np.cos(phi_hit), "y": layer["r_cm"] * np.sin(phi_hit), "z": z_hit,
                     "is_pixel": layer["is_pixel"], "idx_rphi": idx_rphi, "idx_z": idx_z})
    return hits


def install(geometry="B", sct="Z1160"):
    """Bind the literal particle-hit function into the frozen sampling module (runtime only)."""
    CONFIG["geometry"], CONFIG["sct"] = geometry, sct
    phs.pileup_particle_hits = literal_pileup_particle_hits


def charged_track_hits_from_traj(traj, z_offset_cm=0.0):
    """First outward crossing of every layer for the two bodies of a simulate_quirk_hits trajectory."""
    x = (traj["x1"] * 1.973269804e-14, traj["x2"] * 1.973269804e-14)
    out = []
    for qi in (0, 1):
        for layer in ag.LAYERS:
            r = tth.find_layer_crossing(x[qi], traj["t_gev_inv"], layer["r_cm"])
            if r is not None:
                (xx, yy, zz), t = r
                out.append((qi, layer, xx, yy, zz + z_offset_cm, t))
    return out


def respond(crossings, rng, tag_fn=lambda qi: qi):
    """Literal hit response for a list of (body, layer, x, y, z, t) crossings."""
    raw = []
    for qi, layer, x, y, z, t in crossings:
        if not accepted(layer["name"], np.hypot(x, y), z, CONFIG["geometry"]):
            continue
        rphi = layer["r_cm"] * np.arctan2(y, x)
        if layer["is_pixel"]:
            rh, zh, ir, iz = tth.quantize_pixel(rphi, z, layer["eff_res_rphi_um"], layer["eff_res_z_um"])
        else:
            rh = rphi + rng.normal(0.0, layer["eff_res_rphi_um"] * 1e-4)
            zh = z + rng.normal(0.0, 1.0) * SCT_Z_SIGMA_CM[CONFIG["sct"]]
            ir = iz = None
        ph_ = rh / layer["r_cm"]
        raw.append({"layer": layer["name"], "layer_r_cm": layer["r_cm"], "quirk_index": tag_fn(qi), "t_ns": t,
                    "x": layer["r_cm"] * np.cos(ph_), "y": layer["r_cm"] * np.sin(ph_), "z": zh,
                    "is_pixel": layer["is_pixel"], "idx_rphi": ir, "idx_z": iz})
    return raw
