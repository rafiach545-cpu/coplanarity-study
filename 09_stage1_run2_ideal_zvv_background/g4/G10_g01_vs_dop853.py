#!/usr/bin/env python3
"""09 / Geant4 step G10 (2026-11-24): G01 redone with DOP853 as the Eq. 3 reference instead of the fixed-step RK4.
Question: how much of the G01 'Geant4 vs old' difference (mm-cm at 4 and 25 keV) was the RK4 integration error, and how much is left
between Geant4 (Athena string model) and converged Eq. 3?

Same inputs as G01 (G01_compare_integrator.py, unchanged): the first N pairs of 01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv,
m_Q = 800 GeV, both quirks from (0, 0, 0), Bz = 2 T, g4/ideal8_vacuum.card (no material), Lambda = 1 eV (free particles), 100 eV, 4 keV, 25 keV.
Four trajectories per (event, Lambda):
  g4_orig : QuirkPheno d91cb27 as built, its defaults (as G01);
  g4_fix  : QuirkPheno_fix with secondOrderField and DeltaIntersection 1 nm (G05), maxBoost 0.01 (Athena default; G08);
  rk4     : simulate_quirk_hits with the numba RK4 (as G01 and the old production);
  dop853  : simulate_quirk_hits with QUIRK_INTEGRATOR=dop853 (the production DOP853, rtol 1e-10, crossing refinement on the 8 radii).
Hits: true first crossing of every layer by every quirk (Geant4: midpoint of the first visit of the 1 um layer; old code: find_layer_crossing).
Every difference x_a - x_b is split along the event's plane: n1 = normal of fit_plane (05 coplanarity_fit) through the dop853 crossings of
that event (the direction Delta_s measures), out-of-plane = (x_a - x_b).n1, in-plane = the rest; plus r*dphi and dz as in G01.
Usage (env g4): G10_g01_vs_dop853.py [--nev 20] [--workers 6]. Output out_G01/G10/: hits.csv, pairs.csv, summary.csv, G10.log."""
import os, sys, subprocess, argparse, numpy as np, pandas as pd
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim", f"{BASE}/05_coplanarity_analysis"]
import trajectory_to_hits as tth                                           # noqa: E402
from quirk_trajectory_numba import integrate_trajectory_numba_xonly         # noqa: E402
from atlas_geometry import LAYERS                                          # noqa: E402
from coplanarity_fit import fit_plane                                      # noqa: E402
import uproot                                                              # noqa: E402
tth.integrate_trajectory = integrate_trajectory_numba_xonly                # rk4 = the production numba RK4 (positions-only copy, bitwise identical positions; 25 keV needs ~1 GB)

QP = os.environ.get("QUIRKPHENO", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno")) + "/build"
QF = os.environ.get("QUIRKPHENO_FIX", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix")) + "/build"
G4V = {"g4_orig": (QP, []), "g4_fix": (QF, ["/quirk/secondOrderField true", "/qsim/field/deltaIntersection 1e-6 mm", "/quirk/maxBoost 0.01"])}
MQ, B_T, LAMBDAS_EV = 800.0, 2.0, [1.0, 100.0, 4000.0, 25000.0]
OUT = f"{HERE}/out_G01/G10"; CARD = f"{HERE}/ideal8_vacuum.card"


def g4_one(args):
    var, k, r, lam = args
    qp, extra = G4V[var]; tag = f"{var}_L{lam:g}eV_e{k:03d}"; mac, root = f"{OUT}/runs/{tag}.mac", f"{OUT}/runs/{tag}.root"
    if not os.path.exists(root):
        L = extra + [f"/quirk/mass {MQ} GeV", f"/quirk/lambda {lam} eV", f"/qsim/card {CARD}", "/qsim/gen/mode gun", "/qsim/killSecondaries true",
                     "/qsim/out/towers false", "/qsim/out/printEvery 1000", f"/qsim/gun/p1 {r['px2']} {r['py2']} {r['pz2']} GeV",
                     f"/qsim/gun/p2 {r['px1']} {r['py1']} {r['pz1']} GeV", "/qsim/gun/vertex 0 0 0 mm", "/run/initialize", "/run/beamOn 1"]
        open(mac, "w").write("\n".join(L) + "\n")
        env = dict(os.environ, LD_LIBRARY_PATH=f"{qp}/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
        with open(f"{OUT}/runs/{tag}.log", "w") as lg:
            subprocess.run([f"{qp}/quirksim/quirksim", "-m", mac, "-t", "1", "-s", "7", "-o", root[:-5] + "_part.root"], env=env, stdout=lg, stderr=subprocess.STDOUT, check=True)
        os.replace(root[:-5] + "_part.root", root)
    T = uproot.open(root)["events"].arrays(library="np"); assert len(T["evt"]) == 1
    rows, seen = [], set()
    for j in np.argsort(T["h_t0"][0]):                       # as G01: first visit of each layer by each quirk, midpoint of entry and exit
        q, l = int(T["h_q"][0][j]), int(T["h_layer"][0][j])
        if (q, l) in seen: continue
        seen.add((q, l))
        x = 0.05 * np.array([T["h_x0"][0][j] + T["h_x1"][0][j], T["h_y0"][0][j] + T["h_y1"][0][j], T["h_z0"][0][j] + T["h_z1"][0][j]])
        rows.append(dict(sim=var, lam_ev=lam, ev=k, quirk=q, layer=l, x=x[0], y=x[1], z=x[2], t_ns=0.5 * (T["h_t0"][0][j] + T["h_t1"][0][j])))
    return rows


def old_one(args):
    var, k, r, lam = args
    if var == "dop853": os.environ["QUIRK_INTEGRATOR"] = "dop853"
    else: os.environ.pop("QUIRK_INTEGRATOR", None)
    p1 = (r["px1"], r["py1"], r["pz1"], r["E1"]); p2 = (r["px2"], r["py2"], r["pz2"], r["E2"])
    try:
        _, tr = tth.simulate_quirk_hits(p1, p2, MQ, 0.0 if lam <= 1.0 else lam * 1e-9, B_T, +1.0, -1.0, np.random.default_rng(1), z0_cm=0.0, max_layer_r_cm=60.0)
    except RuntimeError as e:
        return [dict(sim=var, lam_ev=lam, ev=k, quirk=-1, layer=-1, fail=str(e)[:80])]
    rows = []
    for q, key in [(0, "x2"), (1, "x1")]:                     # quirk 0 = the +9000011 (charge -1) quirk, as G01
        X = tr[key] * 1.973269804e-14
        for li, lay in enumerate(LAYERS, start=1):
            res = tth.find_layer_crossing(X, tr["t_gev_inv"], lay["r_cm"])
            if res is None: continue
            (x, y, z), t = res
            rows.append(dict(sim=var, lam_ev=lam, ev=k, quirk=q, layer=li, x=x, y=y, z=z, t_ns=t))
    return rows


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--nev", type=int, default=20); a.add_argument("--workers", type=int, default=6); A = a.parse_args()
    os.makedirs(f"{OUT}/runs", exist_ok=True)
    ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(A.nev)
    assert (ev.pdg1 == -9000011).all() and (ev.pdg2 == 9000011).all()
    jobs = lambda vs: [(v, k, r._asdict(), lam) for lam in LAMBDAS_EV for v in vs for k, r in enumerate(ev.itertuples())]
    with Pool(A.workers) as P:
        R = [x for rows in P.map(g4_one, jobs(G4V), chunksize=1) for x in rows]; print("Geant4 done", flush=True)
    with Pool(2) as P:                                        # RK4 at 25 keV: up to 2e7 steps per trajectory (7 GB laptop)
        R += [x for rows in P.map(old_one, jobs(["rk4", "dop853"]), chunksize=1) for x in rows]
    H = pd.DataFrame(R); H.to_csv(f"{OUT}/hits.csv", index=False)
    fails = H[H.layer == -1]; H = H[H.layer != -1]
    for (v, lam), g in fails.groupby(["sim", "lam_ev"]): print(f"  {v} Lambda {lam:g} eV: {len(g)} integration failures (events dropped for that trajectory)")
    # event plane from the dop853 crossings (normal n1 through the vertex, as fit_plane / Delta_s)
    N1 = {}
    for (lam, k), g in H[H.sim == "dop853"].groupby(["lam_ev", "ev"]):
        if len(g) >= 3: N1[(lam, k)] = fit_plane(g[["x", "y", "z"]].to_numpy())["n1"]
    K = ["lam_ev", "ev", "quirk", "layer"]; P_ = []; S = []
    for a_, b_ in [("rk4", "dop853"), ("g4_orig", "dop853"), ("g4_fix", "dop853"), ("g4_orig", "rk4"), ("g4_fix", "rk4"), ("g4_orig", "g4_fix")]:
        M = H[H.sim == a_].merge(H[H.sim == b_], on=K, how="outer", suffixes=("_a", "_b"), indicator=True)
        b = M[M._merge == "both"].copy()
        d = b[["x_a", "y_a", "z_a"]].to_numpy() - b[["x_b", "y_b", "z_b"]].to_numpy()
        n1 = np.array([N1.get((l, e), [np.nan] * 3) for l, e in zip(b.lam_ev, b.ev)])
        b["out_um"] = 1e4 * np.einsum("ij,ij->i", d, n1); b["in_um"] = 1e4 * np.sqrt(np.maximum((d ** 2).sum(1) - (b.out_um / 1e4) ** 2, 0))
        r = np.hypot(b.x_b, b.y_b); b["rdphi_um"] = 1e4 * r * np.angle(np.exp(1j * (np.arctan2(b.y_a, b.x_a) - np.arctan2(b.y_b, b.x_b))))
        b["dz_um"] = 1e4 * (b.z_a - b.z_b); b["dt_ps"] = 1e3 * (b.t_ns_a - b.t_ns_b); b["pair"] = f"{a_}-{b_}"; P_.append(b)
        for lam, g in M.groupby("lam_ev"):
            q = b[b.lam_ev == lam]
            S.append(dict(pair=f"{a_} vs {b_}", lam_ev=lam, both=len(q), only_a=int((g._merge == "left_only").sum()), only_b=int((g._merge == "right_only").sum()),
                          out_med=q.out_um.abs().median(), out_p90=q.out_um.abs().quantile(.9), out_max=q.out_um.abs().max(),
                          in_med=q.in_um.median(), in_p90=q.in_um.quantile(.9), in_max=q.in_um.max(),
                          rdphi_max=q.rdphi_um.abs().max(), dz_max=q.dz_um.abs().max(), dt_max_ps=q.dt_ps.abs().max()))
    pd.concat(P_).to_csv(f"{OUT}/pairs.csv", index=False); S = pd.DataFrame(S); S.to_csv(f"{OUT}/summary.csv", index=False)
    pd.set_option("display.width", 250); print(S.round(2).to_string(index=False)); print("G10_EXIT=0")
