#!/usr/bin/env python3
"""09 step B08 (2026-11-20): cleaning loss of the signal over (m_Q, Lambda), full events, with the cleaning variants c100 / cinf / iso / iso20 (B07.removal_sets).
Signal samples: the 10k-generated EW quirk samples of 07 (/home/rafia/hep_tools/07_large_runs/EW_<m>gev_c00..c04, MG5 + Pythia8, 0+1 jet MLM,
13.6 TeV; at 13 TeV only the 2k Stage 1 grid samples exist). The cleaning loss is a property of the detector, Lambda and the quirk kinematics;
the 13.6 vs 13 TeV difference is small but is stated wherever these numbers are used.
Per triggered event (pT(QQbar) > 200 GeV, the Stage 1 trigger proxy) and per Lambda, as B05:
  quirk hits from simulate_quirk_hits (Eq. 3, numba RK4), underlying-event hits as B03, one pixel merging, hits relative to the PV;
  inputs 'qrk' (quirk hits only, Stage 1), 'all', and the cleaned inputs c100 / cinf / iso / iso20 (2026-11-20: c20, c50 dropped after B07).
RNG per (mass, chunk, event): z0 and the underlying-event hits are the same for every Lambda (own stream); quirk smearing has its own stream per Lambda.
Output data/B08_EW_<m>gev.csv. Usage (env g4): B08_signal_cleaning_scan.py <mass> [--lambdas 0.1,1,4,10,25] [--workers 3] [--nmax N]"""
import os, sys, time, argparse, glob, numpy as np, pandas as pd
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import B05_signal_full_event as S                                                  # noqa: E402  (numba integrator patched in there)
from B07_cleaning_pt_threshold_bkg import VARIANTS, removal_sets                  # noqa: E402  (c100, cinf, iso, iso20)
from quirk_trajectory_numba import integrate_trajectory_numba_xonly                # noqa: E402
S.tth.integrate_trajectory = integrate_trajectory_numba_xonly   # positions only (as F6_02_grid.py XONLY=1): about half the memory; 25 keV
                                                                # trajectories reach 2e7 steps and 4 workers with momenta crashed WSL twice (2026-11-20)
RUNS = S.PATHS.SIGNAL_10K_RUNS; SEED = 20261121


def analyse(job):
    mass, chunk, ev, lams = job; t0 = time.time()
    (pa, *qa), (pb, *qb) = ev["quirks"]
    rng_ue = np.random.default_rng(np.random.SeedSequence([SEED, int(mass), chunk, ev["event"], 0]))
    z0 = rng_ue.normal(0.0, S.BEAMSPOT_SIGMA_Z_CM); pv = np.array([0.0, 0.0, z0]); raw_o = []
    for j in range(len(ev["q"])):
        v = np.array([ev["vx"][j], ev["vy"][j], ev["vz"][j] + z0])
        raw_o += S.pileup_particle_hits(ev["px"][j], ev["py"][j], ev["pz"][j], ev["m"][j], ev["q"][j], v, f"p{j}", rng_ue, B_tesla=2.0)
    rows = []
    for il, lam in enumerate(lams):
        row = dict(mass_gev=mass, chunk=chunk, event=ev["event"], lambda_keV=lam, z0_cm=z0)
        rng_q = np.random.default_rng(np.random.SeedSequence([SEED, int(mass), chunk, ev["event"], 1 + il])); t1 = time.time()
        try:
            _, tr = S.tth.simulate_quirk_hits(qa[:4], qb[:4], mass_gev=mass, Lambda_gev=lam * 1e-6, B_tesla=2.0, charge1=S.Q_CHARGE[pa],
                                              charge2=S.Q_CHARGE[pb], rng=rng_q, z0_cm=z0, max_layer_r_cm=60.0)
        except RuntimeError:
            rows.append(dict(row, integration_fail=True, t_s=time.time() - t1)); continue
        raw_q = tr["raw_hits"]; del tr
        row.update(integration_fail=False, fiducial=False, n_quirk_raw=len(raw_q))
        row["fiducial"] = len(raw_q) == 16 and max(h["t_ns"] for h in raw_q) < 25.0
        hbl = {k: [] for k in range(1, 9)}; isq = {}
        for h in S.overlay_and_merge(raw_q, raw_o)[0]:
            x = S.vertex_relative_hits([(h["x"], h["y"], h["z"])], pv)[0]
            src = h.get("source_quirk_indices") or [h.get("quirk_index")]
            hbl[S.LAYER_IDX[h["layer"]]].append(x); isq[S.key(x)] = any(isinstance(s, (int, np.integer)) for s in src)
        hq = {k: [] for k in range(1, 9)}; isq_q = {}
        for h in S.overlay_and_merge(raw_q, [])[0]:
            x = S.vertex_relative_hits([(h["x"], h["y"], h["z"])], pv)[0]; hq[S.LAYER_IDX[h["layer"]]].append(x); isq_q[S.key(x)] = True
        row.update(n_quirk_hits=sum(v for v in isq.values()), **S.reconstruct(hq, isq_q, "qrk"), **S.reconstruct(hbl, isq, "all"))
        _, tracks = S.TC.find_tracks(hbl)
        for v, rem in removal_sets(hbl, tracks).items():
            row[f"{v}_quirk_hits_removed"] = sum(1 for (k, n) in rem if isq[S.key(hbl[k][n])])
            row.update(S.reconstruct({k: [x for n, x in enumerate(hbl[k]) if (k, n) not in rem] for k in range(1, 9)}, isq, v))
        rows.append(dict(row, t_s=time.time() - t1))
    return rows


def jobs(mass, lams, nmax):
    n = 0
    for f in sorted(glob.glob(f"{RUNS}/EW_{int(mass)}gev_c0[0-4]/Events/*/tag_1_pythia8_events.hepmc.gz")):
        chunk = int(f.split("_c0")[1][0])
        for ev in S.H.iter_events(f):
            if len(ev["quirks"]) != 2: continue
            (_, *a), (_, *b) = ev["quirks"]
            if np.hypot(a[0] + b[0], a[1] + b[1]) <= 200.0: continue
            yield (mass, chunk, ev, lams); n += 1
            if nmax and n >= nmax: return


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("mass", type=float); a.add_argument("--lambdas", default="0.1,1,4,10,25")
    a.add_argument("--workers", type=int, default=3); a.add_argument("--nmax", type=int, default=None); A = a.parse_args()
    lams = [float(x) for x in A.lambdas.split(",")]; t0 = time.time(); R = []
    out = f"{HERE}/data/B08_EW_{int(A.mass)}gev{'' if A.nmax is None else '_test'}.csv"
    with Pool(A.workers) as P:
        for i, rows in enumerate(P.imap_unordered(analyse, jobs(A.mass, lams, A.nmax), chunksize=1)):
            R += rows
            if (i + 1) % 100 == 0:
                print(f"B08 m={A.mass:g}: {i + 1} triggered events, {time.time() - t0:.0f} s", flush=True)
                pd.DataFrame(R).to_csv(out + ".partial", index=False)          # checkpoint (a WSL restart lost a run on 2026-11-20)
    E = pd.DataFrame(R); E.to_csv(out, index=False)
    if os.path.exists(out + ".partial"): os.remove(out + ".partial")
    for lam, g in E.groupby("lambda_keV"):
        ok = g[~g.integration_fail.astype(bool)]; f = ok[ok.fiducial.astype(bool)]
        s = ", ".join(f"{t} {int(f[f'{t}_sr_pass'].sum())}" for t in ["qrk", "all"] + VARIANTS)
        print(f"m {A.mass:g} GeV, Lambda {lam:g} keV: triggered {len(g)}, integration fail {int(g.integration_fail.sum())}, fiducial {len(f)}; SR pass: {s}")
    print(f"wall {time.time() - t0:.0f} s"); print("B08_EXIT=0")
