#!/usr/bin/env python3
"""09 / G13 (2026-11-24): Athena string-model systematic on the 13.6 TeV full-event signal, with the B08 pipeline unchanged.
For each triggered event of 09/B08_signal_cleaning_scan.py (same HepMC, same z0 and underlying-event hits, same quirk-smearing streams, same
merging, the same reco for qrk / all / c100 / cinf / iso / iso20) the quirk trajectory comes from one of two models:
  --model eq3    : Eq. 3, the production DOP853 (QUIRK_INTEGRATOR=dop853, rtol 1e-10), stopped at 25.05 ns;
  --model athena : Geant4 QuirkPheno_fix (Athena string vectors; secondOrderField, DeltaIntersection 1 nm, maxBoost 0.01; G05/G11),
                   g4/ideal8_vacuum.card (no material, Bz = 2 T), /qsim/maxTime 25.05 ns, gun at the event vertex (0, 0, z0).
Nothing in B08 / B05 / trajectory_to_hits is edited. Two module functions are replaced at run time:
  quirk_trajectory_dop853.integrate_trajectory_dop853 -> for athena: run Geant4 for these initial conditions and return a 2-point marker
     trajectory; for eq3: the real DOP853 with T_STOP_NS = 25.05;
  trajectory_to_hits.find_layer_crossing -> for athena: the Geant4 crossing of this (quirk, layer) (entry point of the first visit of the 1 um
     layer and its time), so simulate_quirk_hits' own eta cut, pixel quantisation, SCT smearing (rng order) and raw-hit list are used unchanged.
Why 25.05 ns for both: Geant4 is stopped there (cost); the fiducial definition needs all 16 first crossings before 25 ns, so fid AND SR is
unaffected; only the SR of non-fiducial events can differ from the unstopped production run. Compare fid AND SR only.
Check: --model eq3 must reproduce the production D CSV (data/B08_13p6TeV_dop853_EW_<m>gev.csv) for fid AND SR event by event.
Output: <out>/G13_<model>_EW_<m>gev_L<lams>[_n<N>].csv (B08 columns + model). Usage (env g4):
  G13_athena_b08_scan.py <mass> --model athena|eq3 --lambdas 4,7,10 [--workers N] [--nmax N] [--out DIR]"""
import os, sys, time, argparse, shutil, tempfile, subprocess, numpy as np, pandas as pd
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
D09 = os.environ.get("G13_D09", os.path.dirname(HERE)); sys.path.insert(0, D09)   # 2026-11-24: B08 folder overridable (server bundle v2)
import B08_signal_cleaning_scan as B8                                       # noqa: E402  (unchanged: analyse(), jobs())
import quirk_trajectory_dop853 as Q                                          # noqa: E402
import uproot                                                                # noqa: E402
TTH = B8.S.tth; CM = 1.973269804e-14; NS = 6.582119569e-16; T_STOP_NS = 25.05
QF = os.environ.get("QUIRKPHENO_FIX", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix")) + "/build"
CARD = f"{HERE}/ideal8_vacuum.card"; MODEL = None; CROSS = {}


class G4RunError(Exception):
    """Geant4 did not run. Not a RuntimeError on purpose: B08 counts RuntimeError as integration_fail, a Geant4 failure must stop the job (2026-11-24)."""
_dop_real = Q.integrate_trajectory_dop853; _flc_real = TTH.find_layer_crossing


def _g4(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2, Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv=None, **kw):
    """Run Geant4 for these initial conditions; store its first crossings in CROSS[(marker quirk, layer radius)]; return the marker trajectory."""
    assert abs(B_tesla - 2.0) < 1e-12 and charge1 * charge2 == -1 and np.allclose(x1_0, x2_0) and abs(x1_0[0]) + abs(x1_0[1]) == 0
    z0_mm = float(x1_0[2]) * CM * 10.0
    neg, pos = (p1_0, p2_0) if charge1 < 0 else (p2_0, p1_0)                 # Geant4 p1 = charge -1 (h_q 0)
    d = tempfile.mkdtemp(prefix="g13_", dir=os.environ.get("G13_TMP")); mac, root = f"{d}/r.mac", f"{d}/r.root"
    L = ["/quirk/secondOrderField true", "/qsim/field/deltaIntersection 1e-6 mm", "/quirk/maxBoost 0.01", f"/quirk/mass {mass} GeV",
         f"/quirk/lambda {Lambda_GeV * 1e9} eV", f"/qsim/card {CARD}", "/qsim/gen/mode gun", "/qsim/killSecondaries true", "/qsim/out/towers false",
         "/qsim/out/printEvery 1000", f"/qsim/maxTime {T_STOP_NS} ns", f"/qsim/gun/p1 {neg[0]} {neg[1]} {neg[2]} GeV",
         f"/qsim/gun/p2 {pos[0]} {pos[1]} {pos[2]} GeV", f"/qsim/gun/vertex 0 0 {z0_mm} mm", "/run/initialize", "/run/beamOn 1"]
    open(mac, "w").write("\n".join(L) + "\n")
    env = dict(os.environ, LD_LIBRARY_PATH=f"{QF}/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
    try:
        r = subprocess.run([f"{QF}/quirksim/quirksim", "-m", mac, "-t", "1", "-s", "7", "-o", root], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode != 0 or not os.path.exists(root):
            tail = "\n".join(r.stdout.decode(errors="replace").splitlines()[-30:])
            raise G4RunError(f"Geant4 (quirksim) exit {r.returncode}, output {'missing' if not os.path.exists(root) else 'present'}; last lines:\n{tail}")
        T = uproot.open(root)["events"].arrays(library="np")
    finally:
        shutil.rmtree(d, ignore_errors=True)                                 # only this call's own temporary folder
    marker = {0: 1 if charge1 < 0 else 2, 1: 2 if charge1 < 0 else 1}; CROSS.clear()
    for j in np.argsort(T["h_t0"][0]):
        q, l = marker[int(T["h_q"][0][j])], int(T["h_layer"][0][j]); key = (q, round(TTH.LAYERS[l - 1]["r_cm"], 6))
        if key not in CROSS: CROSS[key] = (0.1 * np.array([T["h_x0"][0][j], T["h_y0"][0][j], T["h_z0"][0][j]]), float(T["h_t0"][0][j]))
    one = np.ones((2, 3)) / CM
    return {"t_gev_inv": np.array([0.0, 1.0]), "x1": 1.0 * one, "p1": np.empty((0, 3)), "x2": 2.0 * one, "p2": np.empty((0, 3))}


def _flc(x_traj_cm, t_gev_inv, layer_r_cm):
    if MODEL != "athena": return _flc_real(x_traj_cm, t_gev_inv, layer_r_cm)
    q = int(round(float(x_traj_cm[0, 0])))                                  # marker trajectory: x1 = 1 cm, x2 = 2 cm
    c = CROSS.get((q, round(layer_r_cm, 6)))
    return None if c is None else (c[0].copy(), c[1])


def _setup(model):
    global MODEL
    MODEL = model; os.environ["QUIRK_INTEGRATOR"] = "dop853"               # simulate_quirk_hits: no RK4 step ceiling, calls Q.integrate_trajectory_dop853
    TTH.find_layer_crossing = _flc
    if model == "athena": Q.integrate_trajectory_dop853 = _g4
    else: Q.T_STOP_NS = T_STOP_NS; Q.integrate_trajectory_dop853 = _dop_real


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("mass", type=float); a.add_argument("--model", choices=["athena", "eq3"], required=True)
    a.add_argument("--lambdas", default="4,7,10"); a.add_argument("--workers", type=int, default=3); a.add_argument("--nmax", type=int)
    a.add_argument("--out", default=f"{HERE}/out_G01/G13"); A = a.parse_args(); os.makedirs(A.out, exist_ok=True)
    lams = [float(x) for x in A.lambdas.split(",")]; t0 = time.time(); R = []
    out = f"{A.out}/G13_{A.model}_EW_{int(A.mass)}gev_L{A.lambdas.replace(',', '-')}{f'_n{A.nmax}' if A.nmax else ''}.csv"
    if os.path.exists(out): sys.exit(f"output exists, not overwritten: {out}")
    with Pool(A.workers, initializer=_setup, initargs=(A.model,)) as P:
        for i, rows in enumerate(P.imap_unordered(B8.analyse, B8.jobs(A.mass, lams, A.nmax), chunksize=1)):
            R += rows
            if (i + 1) % 50 == 0:
                print(f"G13 {A.model} m={A.mass:g}: {i + 1} triggered events, {time.time() - t0:.0f} s", flush=True); pd.DataFrame(R).to_csv(out + ".partial", index=False)
    E = pd.DataFrame(R); E["model"] = A.model; E.to_csv(out, index=False)
    if os.path.exists(out + ".partial"): os.remove(out + ".partial")
    for c in ("integration_fail", "fiducial", "qrk_sr_pass", "iso20_sr_pass"):
        if c not in E.columns: E[c] = False                                  # summary only; the CSV above is unchanged
    for lam, g in E.groupby("lambda_keV"):
        f = g[g.fiducial.astype(str) == "True"]
        print(f"{A.model} m {A.mass:g} L {lam:g}: triggered {len(g)}, fail {int((g.integration_fail.astype(str) == 'True').sum())}, fid {len(f)}, "
              f"fid&SR qrk {int((f.qrk_sr_pass.astype(str) == 'True').sum())} iso20 {int((f.iso20_sr_pass.astype(str) == 'True').sum())}")
    print(f"wall {time.time() - t0:.0f} s, {len(E)} rows -> {out}"); print("G13_EXIT=0")
