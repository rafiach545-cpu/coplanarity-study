#!/usr/bin/env python3
"""07 test T01 (2026-11-15): coverage of the Run 2 silicon geometry (geometry/atlas_run2_geometry.py) for straight tracks.
Checks against published statements (references/REFERENCES.md):
  (a) R3 Sec. 4.3.2: the SCT modules 'provide almost hermetic coverage with at least four precision space-point measurements over the
      fiducial coverage of the inner detector' -> SCT elements crossed >= 4 for |eta| < 2.5 (from z0 = 0; full phi coverage assumed)
  (b) R1 Sec. 2.1: the ID reconstructs tracks within |eta| < 2.5 -> pixel elements (IBL + barrel + disks) crossed >= 3 for |eta| < 2.5
  (c) module counts: SCT end-cap modules summed over rings and both sides = 1976 (R3 Table 4.6 caption); barrel 2112 (R3 Table 4.5)
  (d) trajectory_crossings agrees with straight_crossings on densely sampled straight lines
Also written: tables/T01_coverage_vs_eta.csv (hits per subdetector vs eta for z0 = 0 and +-45 mm, the 1-sigma beam spot of Stages 1-2).
Note: this checks the CSV + crossing code, not the physics; module gaps and tilts are not in the model yet."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."
sys.path.insert(0, f"{ROOT}/geometry"); import atlas_run2_geometry as G
os.makedirs(f"{ROOT}/tables", exist_ok=True)
rows = []
for z0 in (0.0, 45.0, -45.0):
    for eta in np.round(np.arange(0.0, 2.71, 0.05), 2):
        c = G.straight_crossings(eta, z0)
        n = lambda det, kind=None: sum(1 for e, *_ in c if e["det"] == det and (kind is None or e["kind"] == kind))
        rows.append(dict(z0_mm=z0, eta=eta, pix_barrel=n("pixel", "barrel"), pix_disk=n("pixel", "disk"), sct_barrel=n("sct", "barrel"),
                         sct_disk=n("sct", "disk"), pix=n("pixel"), sct=n("sct"), all8_barrel=n("pixel", "barrel") + n("sct", "barrel") == 8))
T = pd.DataFrame(rows); T.to_csv(f"{ROOT}/tables/T01_coverage_vs_eta.csv", index=False)
c0 = T[(T.z0_mm == 0) & (T.eta < 2.5)]
ok_a = bool((c0.sct >= 4).all()); ok_b = bool((c0.pix >= 3).all())
g = pd.read_csv(G.CSV); ring = g[g.region == "endcap_ring"]
n_ec = int(2 * ring.n_units.str.extract(r"(\d+)")[0].astype(int).sum())
n_br = int(g[(g.element == "sct") & (g.region == "barrel")].n_units.str.extract(r"(\d+)")[0].astype(int).sum())
ok_c = n_ec == 1976 and n_br == 2112
dev = []
for eta in (0.3, 1.2, 1.9, 2.4):
    th = 2 * np.arctan(np.exp(-eta)); s = np.linspace(0, 3500, 400001)
    x, y, z = s * np.sin(th), 0 * s, 10.0 + s * np.cos(th)
    a = sorted((e["name"], round(zz, 3)) for e, xx, yy, zz in G.straight_crossings(eta, 10.0))
    b = sorted((e["name"], round(zz, 3)) for e, xx, yy, zz, tt in G.trajectory_crossings(x, y, z, s / 299.792458))
    dev.append(a == b)
ok_d = all(dev)
print(T[T.z0_mm == 0].iloc[::5].to_string(index=False))
print(f"(a) SCT >= 4 for |eta| < 2.5, z0 = 0: {ok_a}  (min {int(c0.sct.min())} at eta {c0.eta[c0.sct.idxmin()]})")
print(f"(b) pixel >= 3 for |eta| < 2.5, z0 = 0: {ok_b}  (min {int(c0.pix.min())} at eta {c0.eta[c0.pix.idxmin()]})")
print(f"(c) SCT modules: end-cap {n_ec} (expect 1976), barrel {n_br} (expect 2112): {ok_c}")
print(f"(d) trajectory_crossings == straight_crossings: {ok_d}")
for z0 in (0.0, 45.0):
    t = T[T.z0_mm == z0]; print(f"z0 = {z0:+.0f} mm: all 8 barrel layers crossed for eta <= {t[t.all8_barrel].eta.max():.2f}")
print("T01_PASS" if ok_a and ok_b and ok_c and ok_d else "T01_FAIL")
