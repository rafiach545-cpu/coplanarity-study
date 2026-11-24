#!/usr/bin/env python3
"""09 / Geant4 step G15 (2026-11-24): Geant4 with /quirk/model eq3 (QuirkPheno_fix: QuirkEq3Pair + QuirkEq3Stepper, the C++ DOP853 that is
bitwise equal to the numba one, G14) against the production DOP853 chain (simulate_quirk_hits, QUIRK_INTEGRATOR=dop853), no material.
Target: crossing positions << 1 um. Inputs as G01 / G10: the first N pairs of 01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv,
m_Q = 800 GeV, both quirks from (0, 0, 0), Bz = 2 T, g4/ideal8_vacuum.card, Lambda = 1 eV, 100 eV, 4 keV, 25 keV (the same Lambda on both
sides, also at 1 eV), both stopped at 25.05 ns. Geant4 variants: eq3 with slice 1, 0.1 (default) and 0.01 ns (slice independence);
deltaIntersection 1 nm. Hit = ENTRY point of the first visit of each 1 um layer (its inner surface is the layer radius; the midpoint used
by G01/G10 sits 0.5 um outside), against find_layer_crossing on the DOP853 trajectory (crossing refinement on the 8 radii).
Per (event, quirk, layer): |dx| (3D), in-plane / out-of-plane (normal of fit_plane through the DOP853 crossings), dt.
Quirk mapping as G01: Geant4 p1 = CSV particle 2 (positive PDG, charge -1, h_q 0) = trajectory x2. No random numbers are used.
Usage (env g4): G15_g4eq3_vs_dop853.py [--nev 20] [--workers 6]. Output out_G01/G15/: hits.csv, pairs.csv, summary.csv."""
import os, sys, subprocess, argparse, numpy as np, pandas as pd
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim", f"{BASE}/05_coplanarity_analysis"]
import trajectory_to_hits as tth                                           # noqa: E402
import quirk_trajectory_dop853 as Q                                         # noqa: E402
from atlas_geometry import LAYERS                                          # noqa: E402
from coplanarity_fit import fit_plane                                      # noqa: E402
import uproot                                                              # noqa: E402
QF = os.environ.get("QUIRKPHENO_FIX", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix")) + "/build"
MQ, B_T, LAMBDAS_EV, T_STOP = 800.0, 2.0, [1.0, 100.0, 4000.0, 25000.0], 25.05
G4V = {"g4eq3_s1": ["/quirk/model eq3", "/quirk/eq3Slice 1 ns"], "g4eq3": ["/quirk/model eq3", "/quirk/eq3Slice 0.1 ns"],
       "g4eq3_s001": ["/quirk/model eq3", "/quirk/eq3Slice 0.01 ns"]}
OUT = f"{HERE}/out_G01/G15"; CARD = f"{HERE}/ideal8_vacuum.card"


def g4_one(args):
    var, k, r, lam = args
    tag = f"{var}_L{lam:g}eV_e{k:03d}"; mac, root = f"{OUT}/runs/{tag}.mac", f"{OUT}/runs/{tag}.root"
    if not os.path.exists(root):
        L = G4V[var] + ["/qsim/field/deltaIntersection 1e-6 mm", f"/quirk/mass {MQ} GeV", f"/quirk/lambda {lam} eV", f"/qsim/card {CARD}",
                        "/qsim/gen/mode gun", "/qsim/killSecondaries true", "/qsim/out/towers false", "/qsim/out/printEvery 1000", f"/qsim/maxTime {T_STOP} ns",
                        f"/qsim/gun/p1 {r['px2']} {r['py2']} {r['pz2']} GeV", f"/qsim/gun/p2 {r['px1']} {r['py1']} {r['pz1']} GeV", "/qsim/gun/vertex 0 0 0 mm",
                        "/run/initialize", "/run/beamOn 1"]
        open(mac, "w").write("\n".join(L) + "\n")
        env = dict(os.environ, LD_LIBRARY_PATH=f"{QF}/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
        with open(f"{OUT}/runs/{tag}.log", "w") as lg:
            subprocess.run([f"{QF}/quirksim/quirksim", "-m", mac, "-t", "1", "-s", "7", "-o", root[:-5] + "_part.root"], env=env, stdout=lg, stderr=subprocess.STDOUT, check=True)
        os.replace(root[:-5] + "_part.root", root)
    T = uproot.open(root)["events"].arrays(library="np"); assert len(T["evt"]) == 1
    rows, seen = [], set()
    for j in np.argsort(T["h_t0"][0]):
        q, l = int(T["h_q"][0][j]), int(T["h_layer"][0][j])
        if (q, l) in seen: continue
        seen.add((q, l))
        rows.append(dict(sim=var, lam_ev=lam, ev=k, quirk=q, layer=l, x=0.1 * T["h_x0"][0][j], y=0.1 * T["h_y0"][0][j], z=0.1 * T["h_z0"][0][j], t_ns=float(T["h_t0"][0][j])))
    return rows


def dop_one(args):
    k, r, lam = args
    os.environ["QUIRK_INTEGRATOR"] = "dop853"; Q.T_STOP_NS = T_STOP
    p1 = (r["px1"], r["py1"], r["pz1"], r["E1"]); p2 = (r["px2"], r["py2"], r["pz2"], r["E2"])
    _, tr = tth.simulate_quirk_hits(p1, p2, MQ, lam * 1e-9, B_T, +1.0, -1.0, np.random.default_rng(1), z0_cm=0.0, max_layer_r_cm=60.0)
    rows = []
    for q, key in [(0, "x2"), (1, "x1")]:
        X = tr[key] * 1.973269804e-14
        for li, lay in enumerate(LAYERS, start=1):
            res = tth.find_layer_crossing(X, tr["t_gev_inv"], lay["r_cm"])
            if res is None or res[1] >= T_STOP: continue
            (x, y, z), t = res
            if abs(z) >= 300.0: continue                                  # the card's layers end at |z| = 300 cm
            rows.append(dict(sim="dop853", lam_ev=lam, ev=k, quirk=q, layer=li, x=x, y=y, z=z, t_ns=t))
    return rows


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--nev", type=int, default=20); a.add_argument("--workers", type=int, default=6); A = a.parse_args()
    os.makedirs(f"{OUT}/runs", exist_ok=True)
    ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(A.nev)
    assert (ev.pdg1 == -9000011).all() and (ev.pdg2 == 9000011).all()
    with Pool(A.workers) as P:
        R = [x for rows in P.map(g4_one, [(v, k, r._asdict(), lam) for lam in LAMBDAS_EV for v in G4V for k, r in enumerate(ev.itertuples())], chunksize=1) for x in rows]
    with Pool(2) as P:
        R += [x for rows in P.map(dop_one, [(k, r._asdict(), lam) for lam in LAMBDAS_EV for k, r in enumerate(ev.itertuples())], chunksize=1) for x in rows]
    H = pd.DataFrame(R); H.to_csv(f"{OUT}/hits.csv", index=False)
    N1 = {key: fit_plane(g[["x", "y", "z"]].to_numpy())["n1"] for key, g in H[H.sim == "dop853"].groupby(["lam_ev", "ev"]) if len(g) >= 3}
    K = ["lam_ev", "ev", "quirk", "layer"]; P_, S = [], []
    for a_, b_ in [("g4eq3", "dop853"), ("g4eq3_s1", "dop853"), ("g4eq3_s001", "dop853"), ("g4eq3_s1", "g4eq3"), ("g4eq3_s001", "g4eq3")]:
        M = H[H.sim == a_].merge(H[H.sim == b_], on=K, how="outer", suffixes=("_a", "_b"), indicator=True); b = M[M._merge == "both"].copy()
        d = b[["x_a", "y_a", "z_a"]].to_numpy() - b[["x_b", "y_b", "z_b"]].to_numpy()
        n1 = np.array([N1.get((l, e), [np.nan] * 3) for l, e in zip(b.lam_ev, b.ev)])
        b["dx_um"] = 1e4 * np.linalg.norm(d, axis=1); b["out_um"] = 1e4 * np.abs(np.einsum("ij,ij->i", d, n1))
        b["in_um"] = np.sqrt(np.maximum(b.dx_um ** 2 - b.out_um ** 2, 0)); b["dt_ps"] = 1e3 * (b.t_ns_a - b.t_ns_b); b["pair"] = f"{a_}-{b_}"; P_.append(b)
        for lam, g in M.groupby("lam_ev"):
            q = b[b.lam_ev == lam]
            S.append(dict(pair=f"{a_} vs {b_}", lam_ev=lam, both=len(q), only_a=int((g._merge == "left_only").sum()), only_b=int((g._merge == "right_only").sum()),
                          dx_med_um=q.dx_um.median(), dx_p90_um=q.dx_um.quantile(.9), dx_max_um=q.dx_um.max(), out_max_um=q.out_um.max(), in_max_um=q.in_um.max(),
                          dt_max_ps=q.dt_ps.abs().max()))
    pd.concat(P_).to_csv(f"{OUT}/pairs.csv", index=False); S = pd.DataFrame(S); S.to_csv(f"{OUT}/summary.csv", index=False)
    pd.set_option("display.width", 250); print(S.to_string(index=False, float_format=lambda v: f"{v:.3g}")); print("G15_EXIT=0")
