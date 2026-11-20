#!/usr/bin/env python3
"""09 step B03 (2026-11-19): detector hits and coplanarity reconstruction for full Z(nunu)+jet events, Stage 1 · Run 2 · Ideal.
Detector and reconstruction are the frozen Stage 1 ones, called unchanged:
  - geometry/response: 04_detector_sim/atlas_geometry.LAYERS (8-layer barrel of arXiv:1708.02243 Sec. III A: pixel quantised to the pitch,
    SCT Gaussian 34 um r-phi / 1160 um z), |eta_hit| < 1.8, 25 ns time-of-flight cut per hit, no material, uniform Bz = 2 T;
  - every status-1 charged particle of the event (hepmc_events.py) is propagated as an exact helix from its OWN production vertex by
    02_backgrounds/pileup/pileup_hits.pileup_particle_hits (the function already used for pile-up particles); the hard vertex is
    (0, 0, z0) with z0 ~ N(0, 4.5 cm), and every production vertex is shifted by the same z0;
  - pixel merging over all hits of the event: pileup_hits.overlay_and_merge(raw_hits, []) (the signal path with mu = 0);
  - hits relative to the true primary vertex (paper Sec. III C), 05_coplanarity_analysis/coplanarity_fit.seeding_and_iterative_fit,
    select_reconstructed_plane and apply_signal_region_cuts (Delta_w < 1 cm, smallest Delta_s, multiplicity, Delta_s < 100 um).
Two inputs per event (same hits, same seeds): 'all' = every hit; 'orp' = hits left after ordinary-track cleaning (track_cleaning.py, no
truth). Truth is used only for the cleaning validation columns (trk_*).
RNG: default_rng(SeedSequence([SEED, chunk, event])) per event (z0, SCT smearing).
Outputs (per chunk): data/B03_events_c<cc>.csv (one row per event; all_* and orp_* columns) and data/B03_candidates_c<cc>.csv (per event and
input, up to 30 candidates with Delta_w < 5 cm, smallest Delta_s first, for the later cut scan), with the truth particles of each plane.
Usage: B03_hits_and_planes.py <chunk> [--workers 8] [--nmax N] [--sample zvv|wlnu]   (outputs of --sample wlnu carry the prefix wlnu_)"""
import os, sys, time, argparse, numpy as np, pandas as pd
from collections import Counter, defaultdict
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import paths09 as PATHS                                                         # noqa: E402
BASE = PATHS.BASE
sys.path[:0] = [HERE, f"{BASE}/02_backgrounds/pileup", f"{BASE}/05_coplanarity_analysis", f"{BASE}/04_detector_sim"]
import hepmc_events as H                                                                       # noqa: E402
import track_cleaning as TC                                                                    # noqa: E402
from pileup_hits import pileup_particle_hits, overlay_and_merge                               # noqa: E402
from coplanarity_fit import (seeding_and_iterative_fit, select_reconstructed_plane, apply_signal_region_cuts,  # noqa: E402
                             vertex_relative_hits, check_hit_multiplicity)
from atlas_geometry import BEAMSPOT_SIGMA_Z_CM                                                 # noqa: E402

SEED = 20261119
LAYER_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4, 'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}
MAX_CAND, DW_KEEP_CM = 30, 5.0


def key(x):
    return tuple(np.round(np.asarray(x, float), 7))


def layer_counts(layers):
    c = Counter(layers); return sum(1 for l in range(1, 9) if c.get(l, 0) >= 1), sum(1 for l in range(1, 9) if c.get(l, 0) >= 2)


def reconstruct(hbl, owner, ev, tag, chunk):
    cands = seeding_and_iterative_fit(hbl)
    sel = select_reconstructed_plane(cands) if cands else None
    win = apply_signal_region_cuts(cands) if cands else None

    def info(c):
        parts = sorted({p for x in c["hits"] for p in owner.get(key(x), [])}); n1, n2 = layer_counts(c["layers"])
        return dict(ds_cm=c["fit"]["delta_s"], dw_cm=c["fit"]["delta_w"], n_plane_hits=len(c["hits"]), n_layers_1=n1, n_layers_2=n2,
                    mult_ok=check_hit_multiplicity(c["layers"]), n_particles=len(parts),
                    pdgs=";".join(str(int(ev["pdg"][p])) for p in parts),
                    max_r_vtx_cm=max((float(np.hypot(ev["vx"][p], ev["vy"][p])) for p in parts), default=np.nan),
                    min_pt=min((float(np.hypot(ev["px"][p], ev["py"][p])) for p in parts), default=np.nan))
    row = {f"{tag}_n_hits": sum(len(v) for v in hbl.values()), f"{tag}_n_cand": len(cands), f"{tag}_has_plane": sel is not None,
           f"{tag}_sr_pass": win is not None}
    row.update({f"{tag}_sel_{k}": v for k, v in (info(sel) if sel else {}).items()})
    keep = sorted([c for c in cands if c["fit"]["delta_w"] < DW_KEEP_CM], key=lambda c: c["fit"]["delta_s"])[:MAX_CAND]
    return row, [dict(chunk=chunk, event=ev["event"], input=tag, rank=i, **info(c)) for i, c in enumerate(keep)]


def analyse(job):
    chunk, ev = job; t0 = time.time()
    rng = np.random.default_rng(np.random.SeedSequence([SEED, chunk, ev["event"]]))
    z0 = rng.normal(0.0, BEAMSPOT_SIGMA_Z_CM); pv = np.array([0.0, 0.0, z0]); raw = []
    for j in range(len(ev["q"])):
        v = np.array([ev["vx"][j], ev["vy"][j], ev["vz"][j] + z0])
        raw += pileup_particle_hits(ev["px"][j], ev["py"][j], ev["pz"][j], ev["m"][j], ev["q"][j], v, f"p{j}", rng, B_tesla=2.0)
    merged, _ = overlay_and_merge(raw, [])
    hbl = {k: [] for k in range(1, 9)}; owner = {}
    for h in merged:
        x = vertex_relative_hits([(h["x"], h["y"], h["z"])], pv)[0]; hbl[LAYER_IDX[h["layer"]]].append(x)
        src = h.get("source_quirk_indices") or [h.get("quirk_index")]; owner[key(x)] = [int(str(s)[1:]) for s in src if s is not None]
    row = dict(chunk=chunk, event=ev["event"], weight=ev["weight"], met=ev["met"], z0_cm=z0, n_charged=len(ev["q"]), n_raw_hits=len(raw),
               **{f"n_L{k}": len(hbl[k]) for k in range(1, 9)})
    r_all, c_all = reconstruct(hbl, owner, ev, "all", chunk)
    t1 = time.time(); removed, tracks = TC.find_tracks(hbl); t_trk = time.time() - t1
    hbl_o = {k: [x for n, x in enumerate(hbl[k]) if (k, n) not in removed] for k in range(1, 9)}
    r_orp, c_orp = reconstruct(hbl_o, owner, ev, "orp", chunk)
    # cleaning validation (truth only here): prompt particles with hits on >= 6 layers, and whether all their hits were removed
    by_p = defaultdict(list)
    for k in range(1, 9):
        for n, x in enumerate(hbl[k]):
            for p in owner.get(key(x), []): by_p[p].append((k, n))
    rv = np.hypot(ev["vx"], ev["vy"])
    prompt = [p for p, hs in by_p.items() if rv[p] < 0.1 and len({k for k, _ in hs}) >= 6]
    found = [p for p in prompt if all(h in removed for h in by_p[p])]
    disp_removed = sum(1 for p, hs in by_p.items() if rv[p] >= 0.1 for h in hs if h in removed)
    row.update(trk_n_tracks=len(tracks), trk_n_removed=len(removed), trk_n_prompt=len(prompt), trk_n_prompt_found=len(found),
               trk_n_displaced_hits_removed=disp_removed, t_track_s=t_trk, **r_all, **r_orp, t_s=time.time() - t0)
    return row, c_all + c_orp


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("chunk", type=int); a.add_argument("--workers", type=int, default=8)
    a.add_argument("--nmax", type=int, default=None); a.add_argument("--sample", default="zvv", choices=sorted(PATHS.SAMPLES)); A = a.parse_args()
    SP = PATHS.SAMPLES[A.sample]; pre = SP["prefix"]
    C = pd.read_csv(f"{HERE}/data/{SP['chunks']}").set_index("chunk"); hep = PATHS.hepmc_of(A.sample, A.chunk, C.loc[A.chunk, "hepmc"]); t0 = time.time()
    jobs = ((A.chunk, e) for e in H.iter_events(hep, A.nmax)); R, CR = [], []
    with Pool(A.workers) as P:
        for i, (r, cr) in enumerate(P.imap(analyse, jobs, chunksize=4)):
            R.append(r); CR += cr
            if (i + 1) % 1000 == 0: print(f"B03 chunk {A.chunk}: {i + 1} events, {time.time() - t0:.0f} s", flush=True)
    E = pd.DataFrame(R); E.to_csv(f"{HERE}/data/{pre}B03_events_c{A.chunk:02d}.csv", index=False)
    pd.DataFrame(CR).to_csv(f"{HERE}/data/{pre}B03_candidates_c{A.chunk:02d}.csv", index=False)
    m = E.met > 200
    for t in ("all", "orp"):
        print(f"B03 chunk {A.chunk} [{t}]: {len(E)} events ({int(m.sum())} MET > 200), mean hits {E[f'{t}_n_hits'].mean():.0f}, with a selected plane "
              f"{int(E[f'{t}_has_plane'].sum())}, SR pass {int(E[f'{t}_sr_pass'].sum())} (MET > 200: {int((E[f'{t}_sr_pass'] & m).sum())})")
    print(f"B03 chunk {A.chunk} cleaning: prompt particles (>= 6 layers) {int(E.trk_n_prompt.sum())}, fully removed "
          f"{int(E.trk_n_prompt_found.sum())} ({E.trk_n_prompt_found.sum() / max(E.trk_n_prompt.sum(), 1):.3f}); hits removed {int(E.trk_n_removed.sum())}, "
          f"of which displaced-particle hits {int(E.trk_n_displaced_hits_removed.sum())}; time per event mean {E.t_s.mean():.2f} s "
          f"(tracking {E.t_track_s.mean():.2f} s), max {E.t_s.max():.1f} s; wall {time.time() - t0:.0f} s")
    print("B03_EXIT=0")
