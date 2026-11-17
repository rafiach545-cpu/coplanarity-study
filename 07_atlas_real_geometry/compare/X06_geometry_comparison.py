#!/usr/bin/env python3
"""07 X06 (2026-11-17): exact element-by-element comparison of the two detector geometries used for the quirk signal:
  Stage 1 (Ideal)  = sim/detsim07.build("stage2"): the 8 barrel layers of Stages 0-1 (structure from Knapen et al. R10; radii from ATLAS documentation);
  Stage 2 (ATLAS)  = sim/detsim07.build("atlas"):  the same 8 barrel layers + 2 x 3 pixel disks + 2 x 22 SCT end-cap rings (geometry CSV, R1-R3).
Every number is read from the code objects that the simulation uses (not retyped). Writes
  tables/X06_geometry_elements.csv : one row per element and geometry (kind, r or z, extent, pitch / resolution, x/X0, eta coverage at z0 = 0 and z0 = +-1 sigma_z);
  tables/X06_eta_station_coverage.csv : for a straight line from (0, 0, z0) at |eta| = 0.00 ... 3.00, the number of pixel and SCT elements crossed in each geometry,
    and whether the fiducial geometry requirement holds (Ideal: all 8 barrel layers; ATLAS: >= 4 pixel and >= 4 SCT measurements (8 stations, D1) and |eta| < 2.5).
Straight lines only: the quirks bend and oscillate, so the real acceptance is measured in X04 (selected events)."""
import os, sys, math, numpy as np, pandas as pd
R = os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/.."); sys.path.insert(0, f"{R}/sim")
import detsim07 as D
SZ = float(D.BEAMSPOT_SIGMA_Z_CM); rows = []
def cover(e, z0):
    if e["kind"] == "barrel":
        r = e["r_cm"]; return (0.0, math.asinh((e["half_cm"] - z0) / r))            # +eta side; the -eta side is z0 -> -z0
    z = abs(e["z_cm"]); dz = z - z0 if e["z_cm"] > 0 else z + z0
    return (math.asinh(dz / e["rmax_cm"]), math.asinh(dz / e["rmin_cm"]))
for geo, label in (("stage2", "Stage 1 · Ideal"), ("atlas", "Stage 2 · ATLAS")):
    for e in D.build(geo):
        if e["kind"] == "disk" and e["z_cm"] < 0: continue                               # the C side mirrors the A side
        d = dict(geometry=label, element=e["name"].replace("_A", ""), kind=e["kind"], detector="pixel" if e["is_pixel"] else "SCT",
                 r_cm=e.get("r_cm"), half_length_cm=e.get("half_cm"), z_cm=abs(e["z_cm"]) if e["kind"] == "disk" else None,
                 rmin_cm=e.get("rmin_cm"), rmax_cm=e.get("rmax_cm"), sides="A + C" if e["kind"] == "disk" else "-",
                 pitch_rphi_um=e.get("pitch_rphi_um"), pitch_long_um=e.get("pitch_long_um"), res_rphi_um=e.get("res_rphi_um"), x_over_X0=e["x0"])
        for tag, z0 in (("z0=0", 0.0), ("z0=+1sigma", SZ), ("z0=-1sigma", -SZ)):
            lo, hi = cover(e, z0); d[f"eta_min_{tag}"] = round(lo, 3); d[f"eta_max_{tag}"] = round(hi, 3)
        rows.append(d)
E = pd.DataFrame(rows); E.to_csv(f"{R}/tables/X06_geometry_elements.csv", index=False)
def count(els, eta, z0):
    th = 2 * math.atan(math.exp(-eta)); u = (math.sin(th), 0.0, math.cos(th)); n = {"pixel": 0, "SCT": 0}; nb = 0
    for e in els:
        if e["kind"] == "barrel":
            s = e["r_cm"] / u[0] if u[0] > 1e-12 else math.inf; ok = abs(z0 + s * u[2]) < e["half_cm"]; nb += ok
        else:
            if e["z_cm"] < 0 or u[2] <= 0: continue
            s = (e["z_cm"] - z0) / u[2]; r = s * u[0]; ok = s > 0 and e["rmin_cm"] <= r <= e["rmax_cm"]
        if ok: n["pixel" if e["is_pixel"] else "SCT"] += 1
    return n, nb
ELI, ELA = D.build("stage2"), D.build("atlas"); cv = []
for tag, z0 in (("z0=0", 0.0), ("z0=+1sigma", SZ), ("z0=-1sigma", -SZ)):
    for eta in np.round(np.arange(0, 3.0001, 0.01), 2):
        ni, nbi = count(ELI, eta, z0); na, _ = count(ELA, eta, z0)
        cv.append(dict(z0=tag, eta=eta, ideal_pixel=ni["pixel"], ideal_sct=ni["SCT"], ideal_fid_geometry=nbi == 8,
                       atlas_pixel=na["pixel"], atlas_sct=na["SCT"], atlas_fid_geometry=na["pixel"] >= 4 and na["SCT"] >= 4 and eta < 2.5))
C = pd.DataFrame(cv); C.to_csv(f"{R}/tables/X06_eta_station_coverage.csv", index=False)
pd.set_option("display.width", 250); print(f"beam spot sigma_z = {SZ} cm"); print(E.to_string(index=False))
for tag, x in C.groupby("z0"):
    def ranges(col):
        v = x[col].values; e = x.eta.values; out = []; st = None
        for i, f in enumerate(v):
            if f and st is None: st = e[i]
            if (not f or i == len(v) - 1) and st is not None: out.append((st, e[i] if f else e[i - 1])); st = None
        return out
    print(tag, "ideal fid geometry:", ranges("ideal_fid_geometry"), "| ATLAS:", ranges("atlas_fid_geometry"))
