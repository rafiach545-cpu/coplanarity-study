#!/usr/bin/env python3
"""09 / Geant4 step G02 (2026-11-19): single free charged particles, Geant4 and the old integrator vs the EXACT helix.
Same 20 quirk pairs as G01 (m = 800 GeV, B = 2 T, start at the origin), but with the string switched off:
  - Geant4 (quirksim, ideal8_vacuum.card): Lambda = 1e-3 eV (string force 1e-24 GeV^2, negligible), one process per event;
  - old code: simulate_quirk_hits with Lambda = 0 (its Lorentz-force-only path), numba RK4 as in the Stage 1 grid;
  - reference: 02_backgrounds/pileup/helix_propagation.find_helix_layer_crossings (closed-form helix).
Only crossings with |eta| < 1.8 (the Stage 1 fiducial cut) are compared. Output: r*dphi and dz (um) of each code minus the exact helix."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [HERE, f"{BASE}/02_backgrounds/pileup"]
import G01_compare_integrator as G                                   # noqa: E402  (same Geant4 and old-code drivers)
from helix_propagation import find_helix_layer_crossings              # noqa: E402
from atlas_geometry import LAYERS                                     # noqa: E402

LAM_G4 = 1e-3
if __name__ == "__main__":
    ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(20)
    R = G.run_g4(ev, LAM_G4) + [dict(r, lam_ev=LAM_G4) for r in G.run_old(ev, 0.0)]
    radii = [l["r_cm"] for l in LAYERS]
    for k, r in enumerate(ev.itertuples()):          # quirk 0 = CSV particle 2 (charge -1), quirk 1 = particle 1 (charge +1)
        for q, p, c in [(0, (r.px2, r.py2, r.pz2), -1.0), (1, (r.px1, r.py1, r.pz1), +1.0)]:
            X = find_helix_layer_crossings(np.zeros(3), np.array(p), G.MQ, c, 2.0, radii)
            for li, rr in enumerate(radii, start=1):
                if rr in X: (x, y, z), t = X[rr]; R.append(dict(sim="exact", lam_ev=LAM_G4, ev=k, quirk=q, layer=li, x=x, y=y, z=z, t_ns=t))
    D = pd.DataFrame(R); D["eta"] = -np.log(np.tan(0.5 * np.arctan2(np.hypot(D.x, D.y), D.z)))
    D = D[D.eta.abs() < 1.8]
    E = D[D.sim == "exact"]; out = []
    print("code minus exact helix, |eta| < 1.8 (um):  layer: n, median |r dphi|, max |r dphi|, median |dz|, max |dz|")
    for sim in ("g4", "old"):
        M = D[D.sim == sim].merge(E, on=["ev", "quirk", "layer"], suffixes=("", "_ex"))
        M["rdphi_um"] = 1e4 * np.hypot(M.x_ex, M.y_ex) * np.angle(np.exp(1j * (np.arctan2(M.y, M.x) - np.arctan2(M.y_ex, M.x_ex))))
        M["dz_um"] = 1e4 * (M.z - M.z_ex); M["sim"] = sim; out.append(M)
        print(f" {sim}: missing vs exact {len(E) - len(M)}")
        for l, g in M.groupby("layer"):
            print(f"   L{l}: {len(g):3d}  {g.rdphi_um.abs().median():7.2f} {g.rdphi_um.abs().max():7.2f}   {g.dz_um.abs().median():7.2f} {g.dz_um.abs().max():7.2f}")
    pd.concat(out).to_csv(f"{G.OUT}/G02_vs_exact.csv", index=False); print("G02_EXIT=0")
