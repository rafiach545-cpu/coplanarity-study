#!/usr/bin/env python3
"""09 / step G09 (2026-11-22): validation of the numba DOP853 integrator (03_trajectory_sim/quirk_trajectory_dop853.py) before production.
  (A) exact helix (Lambda = 0, B = 2 T, 20 EW pairs): first layer crossings vs helix_propagation.find_helix_layer_crossings (as G02);
  (B) exact 1D string (B = 0, back-to-back along x, exactly collinear, Lambda = 1 and 4 keV, turning point at 20 cm, as G04):
      L1-L4 crossing times vs t(x) = (p0 - p(x)) / Lambda^2 and the turning radius;
  (C) G06 conservation at B = 0 (20 pairs, Lambda = 0.1, 1, 4 keV, t <= 1 ns): E_NG, L_NG, P_NG drift;
  (D) the 4 G08 events (Lambda = 4 keV, B = 2 T, 5 ns): max |dx| vs scipy DOP853 (rtol 1e-13) and RK4 dt/64, and runtime.
Each at rtol = 1e-10 and 1e-11 (atol: 1 nm and 1e-10 GeV, scaled by the same factor). Run with /home/rafia/venvs/f6fast/bin/python."""
import os, sys, time, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [f"{BASE}/03_trajectory_sim", f"{BASE}/04_detector_sim", f"{BASE}/02_backgrounds/pileup", HERE]
import quirk_trajectory_dop853 as Q                                   # noqa: E402
from trajectory_to_hits import find_layer_crossing                   # noqa: E402
from helix_propagation import find_helix_layer_crossings             # noqa: E402
from atlas_geometry import LAYERS                                     # noqa: E402
import types; sys.modules.setdefault("uproot", types.ModuleType("uproot"))   # G06 imports uproot (Geant4 part only, not used here)
import G06_conservation_B0 as G6                                      # noqa: E402
CM, NS = Q.CM, Q.NS; M = 800.0; RAD = [l["r_cm"] for l in LAYERS]
ev = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv").head(20)
RT = (1e-10, 1e-11)


def setrt(rt):
    Q.RTOL = rt; Q.ATOL_X = 1e-7 / CM * rt / 1e-10; Q.ATOL_P = 1e-10 * rt / 1e-10


def run(p1, p2, lam, B, tmax, c1=1.0, c2=-1.0, radii=None, ncoarse=8):
    Q.RADII_CM = radii; Q.NCOARSE = ncoarse; t0 = time.time()
    tr = Q.integrate_trajectory_dop853(np.zeros(3), np.array(p1, float), np.zeros(3), np.array(p2, float), M, c1, c2, lam, B, tmax)
    return tr, time.time() - t0, dict(Q.STATS)


out = []
for rt in RT:
    setrt(rt)
    # (A) helix
    dmax = []
    for k, r in ev.iterrows():
        p1, p2 = (r.px1, r.py1, r.pz1), (r.px2, r.py2, r.pz2)
        bt = min(np.hypot(*p1[:2]) / np.sqrt(np.dot(p1, p1) + M * M), np.hypot(*p2[:2]) / np.sqrt(np.dot(p2, p2) + M * M))
        tr, _, _ = run(p1, p2, 0.0, 2.0, 60.0 * 3 / CM / bt, radii=RAD)
        for key, p, c in (("x1", p1, 1.0), ("x2", p2, -1.0)):
            X = find_helix_layer_crossings(np.zeros(3), np.array(p), M, c, 2.0, RAD)
            for R in RAD:
                res = find_layer_crossing(tr[key] * CM, tr["t_gev_inv"], R)
                if R in X and res is not None: dmax.append(np.linalg.norm(np.array(res[0]) - np.array(X[R][0])) * 1e4)
    out.append(dict(test="A helix |dx| max (um)", rtol=rt, value=max(dmax), median=np.median(dmax), n=len(dmax)))
    # (B) exact 1D string
    for lam_ev in (1000.0, 4000.0):
        lam = lam_ev * 1e-9; s = lam ** 2 / CM; E0 = M + 20.0 * s; p0 = np.sqrt(E0 ** 2 - M ** 2)
        tmax = 1.5 * p0 / lam ** 2
        tr, _, _ = run((p0, 0, 0), (-p0, 0, 0), lam, 0.0, tmax, radii=RAD[:4])
        dts = []
        for R in RAD[:4]:
            res = find_layer_crossing(tr["x1"] * CM, tr["t_gev_inv"], R)
            p = np.sqrt((E0 - s * R) ** 2 - M ** 2)                           # exact: t = (p0 - p) / Lambda^2 (GeV^-1) -> ns
            dts.append(abs(res[1] - (p0 - p) / lam ** 2 * NS) if res else np.nan)
        tr2, _, _ = run((p0, 0, 0), (-p0, 0, 0), lam, 0.0, tmax, radii=None, ncoarse=256)
        xturn = np.abs(tr2["x1"][:, 0]).max() * CM
        out.append(dict(test=f"B 1D L={lam_ev:g} eV: max |dt| L1-L4 (ps)", rtol=rt, value=np.nanmax(dts) * 1e3, median=np.nan, n=4))
        out.append(dict(test=f"B 1D L={lam_ev:g} eV: turning radius - 20 cm (um)", rtol=rt, value=(xturn - 20.0) * 1e4, median=np.nan, n=1))
    # (C) conservation
    for lam_ev in (100.0, 1000.0, 4000.0):
        res = []
        for k, r in ev.iterrows():
            tr, _, _ = run((r.px1, r.py1, r.pz1), (r.px2, r.py2, r.pz2), lam_ev * 1e-9, 0.0, 1.0 / NS, radii=None, ncoarse=8)
            idx = np.linspace(0, len(tr["t_gev_inv"]) - 1, min(len(tr["t_gev_inv"]), 6000)).astype(int)
            res.append(G6.quantities(tr["t_gev_inv"][idx], tr["x1"][idx], tr["p1"][idx], tr["x2"][idx], tr["p2"][idx], lam_ev * 1e-9))
        D = pd.DataFrame(res)
        for c in ("dE_NG_over_Q", "dL_NG_rel", "dP_NG_rel"):
            out.append(dict(test=f"C B=0 L={lam_ev:g} eV {c}", rtol=rt, value=D[c].max(), median=D[c].median(), n=len(D)))
    # (D) the 4 G08 events
    import G08_eq3_converge_vs_g4 as G8
    for k in range(4):
        r = ev.iloc[k]; E = dict(np.load(f"{G8.OUT}/eq3_e{k}.npz"))
        tr, ts, st = run((r.px1, r.py1, r.pz1), (r.px2, r.py2, r.pz2), 4e-6, 2.0, G8.TNS / NS, radii=None, ncoarse=64)
        tg = G8.GRID / NS / 1.0; t = tr["t_gev_inv"]
        X = np.stack([np.interp(tg, t, tr[kk][:, j]) for kk in ("x1", "x2") for j in range(3)], 1) * CM
        d = lambda A: float(np.max(np.linalg.norm((X - A).reshape(-1, 2, 3), axis=2)) * 1e4)
        out.append(dict(test=f"D ev{k}: |dx| vs scipy DOP853 rtol1e-13 (um)", rtol=rt, value=d(E["dop853_rtol1e-13"]), median=np.nan, n=1))
        out.append(dict(test=f"D ev{k}: |dx| vs RK4 dt/64 (um)", rtol=rt, value=d(E["rk4_dt64"]), median=np.nan, n=1))
        out.append(dict(test=f"D ev{k}: runtime s / accepted steps / nfev", rtol=rt, value=ts, median=st["n_accepted"], n=st["nfev"]))
T = pd.DataFrame(out); T.to_csv(f"{HERE}/out_G01/G09_validation.csv", index=False)
pd.set_option("display.width", 200); print(T.pivot_table(index="test", columns="rtol", values="value", sort=False).to_string(float_format=lambda v: f"{v:.3g}"))
