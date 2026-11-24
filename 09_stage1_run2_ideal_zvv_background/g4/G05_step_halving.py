#!/usr/bin/env python3
"""09 / Geant4 step G05 (2026-11-22): how the Geant4 (QuirkPheno) free-particle error scales when the step is halved.
Same 20 EW pairs as G01-G03 (m = 800 GeV, B = 2 T, start at the origin), string switched off (Lambda = 1e-3 eV).
The step is forced by empty G4_Galactic shells every s cm in radius (s = 8, 4, 2, 1, 0.5, 0.25, 0.125), plus the plain vacuum card.
Every Geant4 step is written (/qsim/out/stepPrescale 1). Two measures, both against the closed-form helix:
  (1) r*dphi at each layer crossing (hit midpoint, as G01-G03);
  (2) per step, the change of the transverse distance from the exact circle, split into
      'drift' steps (longer than 0.01 mm: the straight segments between field kicks) and
      'boundary' steps (<= 0.01 mm: the 1 um sensitive layers and the zero-length relocation steps at shell boundaries).
Variants (--variant): orig = QuirkPheno d91cb27 as built; the others use the patched copy (QUIRKPHENO_FIX, default hep_tools/QuirkPheno_fix):
  fix_default (patch built, nothing switched on: must equal orig), dI (DeltaIntersection 1 nm), so2 (second-order field placement), so2_dI (both).
Run in env g4 with Geant4 data variables set (conda activate g4). Output: out_G01/G05_<variant>_*.csv."""
import os, sys, subprocess, argparse, numpy as np, pandas as pd, uproot
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [f"{BASE}/04_detector_sim"]
from atlas_geometry import LAYERS                                     # noqa: E402
QP = os.environ.get("QUIRKPHENO_BUILD", os.path.join(os.environ.get("QUIRKPHENO", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno")), "build"))
QPFIX = os.environ.get("QUIRKPHENO_FIX", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix")) + "/build"
VARIANTS = {"orig": (QP, []), "fix_default": (QPFIX, []), "dI": (QPFIX, ["/qsim/field/deltaIntersection 1e-6 mm"]),
            "so2": (QPFIX, ["/quirk/secondOrderField true"]), "so2_dI": (QPFIX, ["/quirk/secondOrderField true", "/qsim/field/deltaIntersection 1e-6 mm"]),
            "so2_dI_dC": (QPFIX, ["/quirk/secondOrderField true", "/qsim/field/deltaIntersection 1e-6 mm", "/qsim/field/deltaChord 0.001 mm"])}
VAR = "orig"
OUT = f"{HERE}/out_G01/G05"; os.makedirs(OUT, exist_ok=True)
RAD = [l["r_cm"] for l in LAYERS]; MQ = 800.0; B = 2.0; LAM = 1e-3
SPACINGS = [None, 8.0, 4.0, 2.0, 1.0, 0.5, 0.25, 0.125]


def card(s):
    name = "vacuum" if s is None else f"s{s:g}".replace(".", "p")
    path = f"{OUT}/{name}.card"
    L = [f"# G05 step-halving card, shells every {s} cm" if s else "# G05: plain vacuum card (= ideal8_vacuum)", "world 100 400 G4_Galactic", "checkOverlaps 0"]
    edges = sorted(set(RAD) | set(np.round(np.arange(0.5, 95.0, s), 6) if s else set()))
    lay = {r: i for i, r in enumerate(RAD, 1)}
    prev = None
    for e in edges:
        if prev is not None and s:
            L.append(f"tube S{prev:.4f} G4_Galactic {prev} {e} -300 300 det=EMPTY")
        if e in lay:
            L.append(f"tube L{lay[e]} G4_Galactic {e} +um:1 -300 300 det=X layer={lay[e]} sens"); prev = e + 1e-4
        else:
            prev = e
    L.append(f"field {B} 0 100 0 400"); open(path, "w").write("\n".join(L) + "\n"); return name, path


def run_one(a):
    name, path, k, r, var = a
    build, extra = VARIANTS[var]
    tag = f"{OUT}/{name}_e{k:02d}" if var == "orig" else f"{OUT}/{var}/{name}_e{k:02d}"; os.makedirs(os.path.dirname(tag), exist_ok=True)
    if not os.path.exists(tag + ".root"):
        M = extra + [f"/quirk/mass {MQ} GeV", f"/quirk/lambda {LAM} eV", f"/qsim/card {path}", "/qsim/gen/mode gun", "/qsim/killSecondaries true",
             "/qsim/out/towers false", "/qsim/out/stepPrescale 1", f"/qsim/gun/p1 {r['px2']} {r['py2']} {r['pz2']} GeV",
             f"/qsim/gun/p2 {r['px1']} {r['py1']} {r['pz1']} GeV", "/qsim/gun/vertex 0 0 0 mm", "/run/initialize", "/run/beamOn 1"]
        open(tag + ".mac", "w").write("\n".join(M) + "\n")
        env = dict(os.environ, LD_LIBRARY_PATH=f"{build}/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
        with open(tag + ".log", "w") as lg:
            subprocess.run([f"{build}/quirksim/quirksim", "-m", tag + ".mac", "-t", "1", "-s", "7", "-o", tag + ".root"], env=env, stdout=lg, stderr=subprocess.STDOUT, check=True)
    f = uproot.open(tag + ".root"); S = f["steps"].arrays(library="pd"); T = f["events"].arrays(library="np")
    hits, steps = [], []
    for q, (p, c) in {0: ((r["px2"], r["py2"], r["pz2"]), -1.0), 1: ((r["px1"], r["py1"], r["pz1"]), +1.0)}.items():
        p = np.array(p); pt = np.hypot(p[0], p[1]); kap = -c * 0.299792458 * B / pt / 1000.0; ph0 = np.arctan2(p[1], p[0])   # 1/mm
        cx, cy = -np.sin(ph0) / kap, np.cos(ph0) / kap
        s = S[S.q == q].sort_values("step"); X = s[["x", "y", "z"]].to_numpy()
        seg = np.r_[np.linalg.norm(X[0]), np.linalg.norm(np.diff(X, axis=0), axis=1)]
        dev = (np.hypot(X[:, 0] - cx, X[:, 1] - cy) - 1 / abs(kap)) * 1000.0 * np.sign(1)     # um, + = outside the exact circle
        ddev = np.diff(np.r_[0.0, dev]); r_ = np.hypot(X[:, 0], X[:, 1]); m = r_ <= 515.0
        steps.append(dict(card=name, ev=k, quirk=q, pt=pt, n_steps=int(m.sum()), n_drift=int((m & (seg > 0.01)).sum()),
                          median_drift_mm=float(np.median(seg[m & (seg > 0.01)])), ddev_drift_um=float(ddev[m & (seg > 0.01)].sum()),
                          ddev_boundary_um=float(ddev[m & (seg <= 0.01)].sum())))
        for j in np.nonzero(T["h_q"][0] == q)[0]:
            l = int(T["h_layer"][0][j]); x = 0.5 * np.array([T["h_x0"][0][j] + T["h_x1"][0][j], T["h_y0"][0][j] + T["h_y1"][0][j], T["h_z0"][0][j] + T["h_z1"][0][j]])
            R = RAD[l - 1] * 10.0
            # exact helix crossing of radius R: angle on the circle from the chord length |x| = R
            phi_ex = []
            for sgn in (+1,):
                ds = 2.0 / kap * np.arcsin(np.clip(R * kap / 2.0, -1, 1))             # transverse arc length to radius R (first crossing)
                phi_ex = np.arctan2(-(np.cos(ph0 + kap * ds) - np.cos(ph0)) / kap, (np.sin(ph0 + kap * ds) - np.sin(ph0)) / kap)
            z_ex = p[2] / pt * ds
            eta = -np.log(np.tan(0.5 * np.arctan2(R, z_ex)))
            hits.append(dict(card=name, ev=k, quirk=q, layer=l, eta=eta, rdphi_um=1e3 * R * np.angle(np.exp(1j * (np.arctan2(x[1], x[0]) - phi_ex))),
                             dz_um=1e3 * (x[2] - z_ex)))
    return hits, steps


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--variant", default="orig", choices=list(VARIANTS)); VAR = a.parse_args().variant
    ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(20)
    jobs = []
    for s in SPACINGS:
        name, path = card(s); jobs += [(name, path, k, r._asdict(), VAR) for k, r in enumerate(ev.itertuples())]
    with Pool(8) as P: res = P.map(run_one, jobs)
    H = pd.DataFrame([h for a, _ in res for h in a]); H = H[H.eta.abs() < 1.8]; St = pd.DataFrame([x for _, b in res for x in b])
    H.to_csv(f"{OUT}/../G05_{VAR}_hits.csv", index=False); St.to_csv(f"{OUT}/../G05_{VAR}_steps.csv", index=False)
    print(f"variant {VAR}: {VARIANTS[VAR]}")
    print("card      | L8 |r dphi| median  max  signed mean (um) | L5 median | drift steps to r=51.5cm (median) | median drift step (mm) | circle-dev sum: drift / boundary (um, median)")
    for name in [card(s)[0] for s in SPACINGS]:
        h8 = H[(H.card == name) & (H.layer == 8)]; h5 = H[(H.card == name) & (H.layer == 5)]; st = St[St.card == name]
        print(f"{name:9s} | {h8.rdphi_um.abs().median():8.2f} {h8.rdphi_um.abs().max():7.2f} {h8.rdphi_um.mean():8.2f} | {h5.rdphi_um.abs().median():7.2f} |"
              f" {st.n_drift.median():6.0f} | {st.median_drift_mm.median():8.2f} | {st.ddev_drift_um.median():8.2f} / {st.ddev_boundary_um.median():8.2f}")
    print("G05_EXIT=0")
