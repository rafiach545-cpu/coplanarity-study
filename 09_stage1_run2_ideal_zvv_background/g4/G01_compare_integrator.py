#!/usr/bin/env python3
"""09 / Geant4 step G01 (2026-11-19): Geant4 (QuirkPheno quirksim, Geant4 11.4.1) vs the old Stage 1 integrator, ideal 8-layer detector, no material.
Same quirk pairs in both:
  - kinematics: the first N events of 01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv (the Stage 1 EW signal, m_Q = 800 GeV);
  - both quirks start at (0, 0, 0); uniform Bz = 2 T. In the CSV particle 1 is PDG -9000011 (charge +1 e, Stage 1 PDG_TO_CHARGE) and particle 2 is
    +9000011 (charge -1 e). quirksim's gun p1 is the positive PDG code with charge -1 e (its default), so Geant4 p1 = CSV particle 2, p2 = particle 1;
    quirk index 0 = the +9000011 (charge -1) quirk in both outputs;
  - Lambda: 1 eV in Geant4 vs 0 in the old code (free charged particles: a helix check), then 0.1, 4 and 25 keV (string force F = Lambda^2).
Geant4: g4/ideal8_vacuum.card (1 um G4_Galactic layers), one quirksim process per event, secondaries killed. The hit is the midpoint of the entry and exit
points of the first visit of each layer by each quirk.
Old: 04_detector_sim/trajectory_to_hits.simulate_quirk_hits (RK4 of arXiv:1708.02243 Eq. 3, unchanged; the integrator is the numba copy
03_trajectory_sim/quirk_trajectory_numba, as in the Stage 1 grid production), then its find_layer_crossing on the true
trajectory (first crossing of each layer radius, before any pixel quantisation or SCT smearing).
Compared per (event, quirk, layer): r*dphi, dz (um), dt (ps), and whether the layer is reached in both.
Usage (env g4): G01_compare_integrator.py [--nev 20]"""
import os, sys, subprocess, argparse, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim"]
import trajectory_to_hits as tth                                           # noqa: E402
from trajectory_to_hits import simulate_quirk_hits, find_layer_crossing   # noqa: E402
from quirk_trajectory_numba import integrate_trajectory_numba               # noqa: E402
tth.integrate_trajectory = integrate_trajectory_numba   # validated drop-in copy (F6_06_validate_numba.py), as in the Stage 1 grid (F6_02_grid.py FAST=1)
from atlas_geometry import LAYERS                                          # noqa: E402
import uproot                                                              # noqa: E402

QP = os.environ.get("QUIRKPHENO", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno")); MQ = 800.0
LAMBDAS_EV = [1.0, 100.0, 4000.0, 25000.0]
OUT = f"{HERE}/out_G01"; os.makedirs(OUT, exist_ok=True)
FAILED = set()
CARD, B_T = f"{HERE}/ideal8_vacuum.card", 2.0     # G03 changes these (step-length and B = 0 tests)


def _g4_one(args):
    k, r, lam_ev = args
    tag = f"{os.path.basename(CARD)[:-5]}_B{B_T:g}_L{lam_ev:g}eV_e{k:03d}"; mac = f"{OUT}/{tag}.mac"; root = f"{OUT}/{tag}.root"
    L = [f"/quirk/mass {MQ} GeV", f"/quirk/lambda {lam_ev} eV", f"/qsim/card {CARD}", "/qsim/gen/mode gun",
         "/qsim/killSecondaries true", "/qsim/out/towers false", "/qsim/out/printEvery 1000",
         f"/qsim/gun/p1 {r['px2']} {r['py2']} {r['pz2']} GeV", f"/qsim/gun/p2 {r['px1']} {r['py1']} {r['pz1']} GeV", "/qsim/gun/vertex 0 0 0 mm",
         "/run/initialize", "/run/beamOn 1"]          # one process per event: the ROOT output keeps only the last run of a process
    open(mac, "w").write("\n".join(L) + "\n")
    env = dict(os.environ, LD_LIBRARY_PATH=f"{QP}/build/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
    with open(f"{OUT}/{tag}.log", "w") as lg:
        subprocess.run([f"{QP}/build/quirksim/quirksim", "-m", mac, "-t", "1", "-s", "7", "-o", root], env=env, stdout=lg, stderr=subprocess.STDOUT, check=True)
    T = uproot.open(root)["events"].arrays(library="np"); assert len(T["evt"]) == 1
    rows, seen = [], set()
    for j in np.argsort(T["h_t0"][0]):
        q, l = int(T["h_q"][0][j]), int(T["h_layer"][0][j])
        if (q, l) in seen: continue
        seen.add((q, l))
        x = 0.05 * np.array([T["h_x0"][0][j] + T["h_x1"][0][j], T["h_y0"][0][j] + T["h_y1"][0][j], T["h_z0"][0][j] + T["h_z1"][0][j]])  # mm -> cm, midpoint
        rows.append(dict(sim="g4", lam_ev=lam_ev, ev=k, quirk=q, layer=l, x=x[0], y=x[1], z=x[2], t_ns=0.5 * (T["h_t0"][0][j] + T["h_t1"][0][j])))
    return rows


def _set(c, b):
    global CARD, B_T; CARD, B_T = c, b


def run_g4(ev, lam_ev):
    from multiprocessing import Pool
    with Pool(8, initializer=_set, initargs=(CARD, B_T)) as P:
        return [x for rows in P.map(_g4_one, [(k, r._asdict(), lam_ev) for k, r in enumerate(ev.itertuples())]) for x in rows]


def run_old(ev, lam_ev):
    rows = []
    for k, r in enumerate(ev.itertuples()):
        p1 = (r.px1, r.py1, r.pz1, r.E1); p2 = (r.px2, r.py2, r.pz2, r.E2)
        try:
            _, tr = simulate_quirk_hits(p1, p2, MQ, 0.0 if lam_ev <= 1.0 else lam_ev * 1e-9, B_T, +1.0, -1.0, np.random.default_rng(1), z0_cm=0.0, max_layer_r_cm=60.0)
        except RuntimeError:          # step ceiling of the old code (counted as n_integration_fail in the Stage 1 grid); event skipped in both
            FAILED.add((lam_ev, k)); continue
        for q, key in [(0, "x2"), (1, "x1")]:
            X = tr[key] * 1.973269804e-14
            for li, lay in enumerate(LAYERS, start=1):
                res = find_layer_crossing(X, tr["t_gev_inv"], lay["r_cm"])
                if res is None: continue
                (x, y, z), t = res
                rows.append(dict(sim="old", lam_ev=lam_ev, ev=k, quirk=q, layer=li, x=x, y=y, z=z, t_ns=t))
    return rows


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--nev", type=int, default=20); A = a.parse_args()
    ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(A.nev)
    assert (ev.pdg1 == -9000011).all() and (ev.pdg2 == 9000011).all()
    R = []
    for lam in LAMBDAS_EV:
        R += run_g4(ev, lam) + run_old(ev, lam); print(f"Lambda {lam:g} eV done", flush=True)
    D = pd.DataFrame(R); D = D[[(l, e) not in FAILED for l, e in zip(D.lam_ev, D.ev)]]
    for lam in LAMBDAS_EV: print(f"  Lambda {lam:g} eV: old-code integration failures (events skipped) {sum(1 for l, _ in FAILED if l == lam)}")
    D.to_csv(f"{OUT}/G01_hits.csv", index=False)
    M = D[D.sim == "g4"].merge(D[D.sim == "old"], on=["lam_ev", "ev", "quirk", "layer"], how="outer", suffixes=("_g4", "_old"), indicator=True)
    r = np.hypot(M.x_old, M.y_old)
    M["rdphi_um"] = 1e4 * r * np.angle(np.exp(1j * (np.arctan2(M.y_g4, M.x_g4) - np.arctan2(M.y_old, M.x_old))))
    M["dz_um"] = 1e4 * (M.z_g4 - M.z_old); M["dt_ps"] = 1e3 * (M.t_ns_g4 - M.t_ns_old)
    M.to_csv(f"{OUT}/G01_compare.csv", index=False)
    print(f"events {A.nev}, m_Q = {MQ:g} GeV; per Lambda: (quirk, layer) pairs in both / only Geant4 / only old; |r dphi|, |dz| (um) median and max; |dt| (ps) max")
    for lam, g in M.groupby("lam_ev"):
        b = g[g._merge == "both"]
        print(f"  Lambda {lam:>7g} eV: {len(b):3d} / {int((g._merge == 'left_only').sum())} / {int((g._merge == 'right_only').sum())};  "
              f"r dphi {b.rdphi_um.abs().median():8.3f} {b.rdphi_um.abs().max():9.3f};  dz {b.dz_um.abs().median():8.3f} {b.dz_um.abs().max():9.3f};  dt {b.dt_ps.abs().max():8.3f}")
    print("G01_EXIT=0")
