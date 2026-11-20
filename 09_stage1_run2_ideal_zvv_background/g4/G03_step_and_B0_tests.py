#!/usr/bin/env python3
"""09 / Geant4 step G03 (2026-11-19): two tests of the G01/G02 differences, same 20 quirk pairs (m = 800 GeV).
(a) Free particles (Lambda = 1e-3 eV) in B = 2 T with ideal8_dense.card (empty vacuum shells every 0.5 cm cut the transport steps) vs the
    exact helix. If the G02 deviations (up to 45 um) come from the one-kick-per-step B field of QuirkHyperbolaStep, they must shrink.
(b) The string alone: B = 0 (ideal8_dense_B0.card and ideal8_vacuum card with B = 0 is not needed: the dense card is the finer one),
    Lambda = 0.1 and 4 keV, Geant4 vs the old integrator (simulate_quirk_hits with B_tesla = 0). Only |eta| < 1.8 crossings."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [HERE, f"{BASE}/02_backgrounds/pileup"]
import G01_compare_integrator as G                                   # noqa: E402
from helix_propagation import find_helix_layer_crossings              # noqa: E402
from atlas_geometry import LAYERS                                     # noqa: E402
RAD = [l["r_cm"] for l in LAYERS]


def eta_cut(D):
    D = D.copy(); D["eta"] = -np.log(np.tan(0.5 * np.arctan2(np.hypot(D.x, D.y), D.z))); return D[D.eta.abs() < 1.8]


def diff(A, B, label):
    M = A.merge(B, on=["ev", "quirk", "layer"], suffixes=("", "_ref"), how="outer", indicator=True); b = M[M._merge == "both"].copy()
    b["rdphi_um"] = 1e4 * np.hypot(b.x_ref, b.y_ref) * np.angle(np.exp(1j * (np.arctan2(b.y, b.x) - np.arctan2(b.y_ref, b.x_ref))))
    b["dz_um"] = 1e4 * (b.z - b.z_ref)
    print(f" {label}: in both {len(b)}, only first {int((M._merge == 'left_only').sum())}, only reference {int((M._merge == 'right_only').sum())}")
    for l, g in b.groupby("layer"):
        print(f"   L{l}: {len(g):3d}  r dphi median {g.rdphi_um.abs().median():9.2f} max {g.rdphi_um.abs().max():9.2f}   dz median {g.dz_um.abs().median():9.2f} max {g.dz_um.abs().max():9.2f}")
    return b


if __name__ == "__main__":
    ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(20); out = []
    print("(a) free particles, B = 2 T, dense card, Geant4 minus exact helix (um)")
    G.CARD, G.B_T = f"{HERE}/ideal8_dense.card", 2.0
    A = eta_cut(pd.DataFrame(G.run_g4(ev, 1e-3))); X = []
    for k, r in enumerate(ev.itertuples()):
        for q, p, c in [(0, (r.px2, r.py2, r.pz2), -1.0), (1, (r.px1, r.py1, r.pz1), +1.0)]:
            H = find_helix_layer_crossings(np.zeros(3), np.array(p), G.MQ, c, 2.0, RAD)
            X += [dict(ev=k, quirk=q, layer=i, x=H[rr][0][0], y=H[rr][0][1], z=H[rr][0][2]) for i, rr in enumerate(RAD, 1) if rr in H]
    out.append(diff(A, eta_cut(pd.DataFrame(X)), "dense card vs exact").assign(test="a"))
    G.CARD, G.B_T = f"{HERE}/ideal8_dense_B0.card", 0.0
    for lam in (100.0, 4000.0):
        print(f"(b) B = 0, Lambda = {lam:g} eV, Geant4 (dense card) minus old integrator (um)")
        A = eta_cut(pd.DataFrame(G.run_g4(ev, lam))); O = pd.DataFrame(G.run_old(ev, lam))
        O = eta_cut(O[[(lam, e) not in G.FAILED for e in O.ev]]) if len(O) else O
        A = A[[(lam, e) not in G.FAILED for e in A.ev]]
        print(f"   old-code integration failures (events skipped): {sum(1 for l, _ in G.FAILED if l == lam)}")
        out.append(diff(A, O, f"B0 L{lam:g}").assign(test=f"b{lam:g}"))
    pd.concat(out).to_csv(f"{G.OUT}/G03_tests.csv", index=False); print("G03_EXIT=0")
