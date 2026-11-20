#!/usr/bin/env python3
"""09 step B05 (2026-11-19): the Stage 1 EW signal (m_Q = 800 GeV, Lambda = 4 keV) as a FULL event, Stage 1 · Run 2 · Ideal.
Input: the Pythia8 file of the Stage 1 signal sample, /home/rafia/hep_tools/quirk_ew_800gev_4kev/Events/run_01/tag_1_pythia8_events.hepmc.gz
(511 events; its status-1 quirks are exactly the momenta of 01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv used in Stage 1).
Per event, one z0 ~ N(0, 4.5 cm), then
  - quirk hits: 04_detector_sim/trajectory_to_hits.simulate_quirk_hits (arXiv:1708.02243 Eq. 3, numba RK4 as in the Stage 1 grid; validated in
    g4/G02-G04), raw hits (pixel quantised, SCT smeared), PDG -9000011 = charge +1 (Stage 1 PDG_TO_CHARGE);
  - every other status-1 charged particle (underlying event, ISR jets): pileup_hits.pileup_particle_hits from its own vertex, as in B03;
  - one pixel merging of all hits (overlay_and_merge(quirk, others)), hits relative to the true PV, then three inputs:
      'qrk' = the quirk hits only (the Stage 1 signal treatment, a reproduction check), 'all' = every hit, 'orp' = after track_cleaning.
Truth flags: Stage 1 fiducial (16 quirk hits before merging, all within 25 ns), quirk hits removed by the cleaning, quirk hits in the
selected plane. Output data/B05_signal_m800_L4keV.csv. Usage (env hep): B05_signal_full_event.py [--workers 8] [--nmax N]"""
import os, sys, time, argparse, numpy as np, pandas as pd
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import paths09 as PATHS                                                                                    # noqa: E402
BASE = PATHS.BASE
sys.path[:0] = [HERE, f"{BASE}/02_backgrounds/pileup", f"{BASE}/05_coplanarity_analysis", f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim"]
import hepmc_events as H                                                                                  # noqa: E402
import track_cleaning as TC                                                                               # noqa: E402
import trajectory_to_hits as tth                                                                          # noqa: E402
from quirk_trajectory_numba import integrate_trajectory_numba                                             # noqa: E402
tth.integrate_trajectory = integrate_trajectory_numba
from pileup_hits import pileup_particle_hits, overlay_and_merge                                          # noqa: E402
from coplanarity_fit import (seeding_and_iterative_fit, select_reconstructed_plane, apply_signal_region_cuts,  # noqa: E402
                             vertex_relative_hits, check_hit_multiplicity)
from atlas_geometry import BEAMSPOT_SIGMA_Z_CM                                                            # noqa: E402

HEPMC = PATHS.B05_HEPMC
MQ, LAMBDA_GEV, SEED = 800.0, 4e-6, 20261120
Q_CHARGE = {-9000011: +1.0, 9000011: -1.0}
LAYER_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4, 'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}


def key(x):
    return tuple(np.round(np.asarray(x, float), 7))


def reconstruct(hbl, isq, tag):
    """isq: {hit key: True if the hit has a quirk contribution}."""
    cands = seeding_and_iterative_fit(hbl)
    sel = select_reconstructed_plane(cands) if cands else None
    win = apply_signal_region_cuts(cands) if cands else None
    row = {f"{tag}_n_hits": sum(len(v) for v in hbl.values()), f"{tag}_n_cand": len(cands), f"{tag}_has_plane": sel is not None,
           f"{tag}_sr_pass": win is not None}
    for nm, c in (("sel", sel), ("win", win)):
        if c is None: continue
        nq = sum(1 for x in c["hits"] if isq.get(key(x), False))
        row.update({f"{tag}_{nm}_ds_cm": c["fit"]["delta_s"], f"{tag}_{nm}_dw_cm": c["fit"]["delta_w"], f"{tag}_{nm}_n_hits": len(c["hits"]),
                    f"{tag}_{nm}_n_quirk_hits": nq, f"{tag}_{nm}_mult_ok": check_hit_multiplicity(c["layers"])})
    return row


def analyse(ev):
    t0 = time.time(); rng = np.random.default_rng(np.random.SeedSequence([SEED, ev["event"]]))
    z0 = rng.normal(0.0, BEAMSPOT_SIGMA_Z_CM); pv = np.array([0.0, 0.0, z0])
    (pa, *qa), (pb, *qb) = ev["quirks"]
    row = dict(event=ev["event"], z0_cm=z0, n_charged=len(ev["q"]), trig=bool(np.hypot(qa[0] + qb[0], qa[1] + qb[1]) > 200.0))   # Stage 1 trigger proxy pT(QQbar) > 200 GeV
    try:
        _, tr = tth.simulate_quirk_hits(qa[:4], qb[:4], mass_gev=MQ, Lambda_gev=LAMBDA_GEV, B_tesla=2.0, charge1=Q_CHARGE[pa], charge2=Q_CHARGE[pb],
                                        rng=rng, z0_cm=z0, max_layer_r_cm=60.0)
    except RuntimeError:
        row.update(integration_fail=True, t_s=time.time() - t0); return row
    raw_q = tr["raw_hits"]
    row.update(integration_fail=False, n_quirk_raw=len(raw_q), fiducial=(len(raw_q) == 16) and tr["max_hit_t_ns_premerge"] < 25.0)
    raw_o = []
    for j in range(len(ev["q"])):
        v = np.array([ev["vx"][j], ev["vy"][j], ev["vz"][j] + z0])
        raw_o += pileup_particle_hits(ev["px"][j], ev["py"][j], ev["pz"][j], ev["m"][j], ev["q"][j], v, f"p{j}", rng, B_tesla=2.0)
    hbl = {k: [] for k in range(1, 9)}; hbl_q = {k: [] for k in range(1, 9)}; isq = {}
    for h in overlay_and_merge(raw_q, raw_o)[0]:
        x = vertex_relative_hits([(h["x"], h["y"], h["z"])], pv)[0]; L = LAYER_IDX[h["layer"]]
        src = h.get("source_quirk_indices") or [h.get("quirk_index")]; q = any(isinstance(s, (int, np.integer)) for s in src)
        hbl[L].append(x); isq[key(x)] = q
        if q: hbl_q[L].append(x)
    hq = {k: [] for k in range(1, 9)}; isq_q = {}                     # quirk-only input, merged alone as in Stage 1
    for h in overlay_and_merge(raw_q, [])[0]:
        x = vertex_relative_hits([(h["x"], h["y"], h["z"])], pv)[0]; hq[LAYER_IDX[h["layer"]]].append(x); isq_q[key(x)] = True
    row.update(n_quirk_hits=sum(len(v) for v in hbl_q.values()), **reconstruct(hq, isq_q, "qrk"), **reconstruct(hbl, isq, "all"))
    removed, tracks = TC.find_tracks(hbl)
    hbl_o = {k: [x for n, x in enumerate(hbl[k]) if (k, n) not in removed] for k in range(1, 9)}
    row.update(trk_n_tracks=len(tracks), trk_n_removed=len(removed),
               quirk_hits_removed=sum(1 for (k, n) in removed if isq[key(hbl[k][n])]), **reconstruct(hbl_o, isq, "orp"), t_s=time.time() - t0)
    return row


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--workers", type=int, default=3)   # 8 workers ran out of the 7 GB RAM (long trajectories)
    a.add_argument("--nmax", type=int, default=None); A = a.parse_args()
    t0 = time.time(); R = []
    with Pool(A.workers) as P:
        for i, r in enumerate(P.imap(analyse, H.iter_events(HEPMC, A.nmax), chunksize=2)):
            R.append(r)
            if (i + 1) % 100 == 0: print(f"B05: {i + 1} events, {time.time() - t0:.0f} s", flush=True)
    E = pd.DataFrame(R); E.to_csv(f"{HERE}/data/B05_signal_m800_L4keV{'' if A.nmax is None else f'_n{A.nmax}'}.csv", index=False)
    E = E[E.trig]; ok = E[~E.integration_fail.astype(bool)]; f = ok[ok.fiducial.astype(bool)]
    print(f"B05: {len(E)} triggered events (pT(QQbar) > 200 GeV), integration failures {int(E.integration_fail.sum())}, Stage 1 fiducial {len(f)}")
    for t in ("qrk", "all", "orp"):
        print(f"  [{t}] SR pass: all events {int(ok[f'{t}_sr_pass'].sum())}, fiducial {int(f[f'{t}_sr_pass'].sum())} (eps_reco {f[f'{t}_sr_pass'].mean():.3f})")
    print(f"  cleaning: quirk hits removed {int(ok.quirk_hits_removed.sum())} of {int(ok.n_quirk_hits.sum())} "
          f"({ok.quirk_hits_removed.sum() / max(ok.n_quirk_hits.sum(), 1):.4f}); events with >= 1 quirk hit removed {int((ok.quirk_hits_removed > 0).sum())}; "
          f"mean time {E.t_s.mean():.1f} s/event; wall {time.time() - t0:.0f} s")
    print("B05_EXIT=0")
