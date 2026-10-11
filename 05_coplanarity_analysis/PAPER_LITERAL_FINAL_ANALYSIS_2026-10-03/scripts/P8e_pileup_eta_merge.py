#!/usr/bin/env python3
"""
P8e (copy of P8_literal_pileup.py, 2026-10-03): modes ETA_MERGE = paper-stated |eta|<1.8 acceptance (geometry A), SCT 34/1160 um,
WITH neighbouring-pixel merging (the paper merges); ETA_NOMERGE = same without merging, used only as a check that
must reproduce the stored project sweep. Same events (same seeds) as every other pile-up run; no new generation.

Original docstring:
Phase 8: pile-up-only background, mu = 50 (paper Sec. III D), literal detector.

Per event i (i = 0..N-1), the frozen sweep's seed convention is kept:
  SeedSequence([90210777, 50, i]).spawn(2) -> (rng_pileup, rng_suppression)
  pile-up: Poisson(50) interactions drawn with replacement from minbias_pool_20000_ANCESTRY_v1.csv, each with
  its own z0 ~ N(0, 45 mm); exact helix propagation; ATLAS tracking-efficiency track suppression (frozen code).
Modes
  VALIDATE : frozen code path untouched (eta-cone, no merging) -> must reproduce the stored sweep rows
             (05_coplanarity_analysis/sweep_mu_2026-09-16/pileup_mu50_n5000_sec3c_fullcutflow_v1.csv).
  LITERAL  : literal_detector.install("B", "Z1160") (finite barrel, SCT 34/1160 um) AND neighbouring-pixel merging
             (paper Sec. III A merging of neighbouring pixel hits; absent from the frozen pile-up-only driver).
Recorded per event: hits per layer, candidate count, best layer coverage (4/8, 8/8), Sec. III C plane, Delta_s,
Delta_w, hit multiplicity, Delta_s < 0.01, final Sec. IV, and the paper's relaxed control
("plane with at least one hit in each layer", i.e. 8/8).
Output: one CSV per 100-event chunk in ../logs/P8_chunks_<mode>/ (append-only; existing chunks are skipped).
"""
import os, sys, json, time, multiprocessing as mp
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import literal_detector as ld                                   # noqa: E402  (sets sys.path)
from coplanarity_fit import (seeding_and_iterative_fit, select_reconstructed_plane, check_hit_multiplicity,  # noqa: E402
                             vertex_relative_hits)
from trajectory_to_hits import merge_neighboring_pixel_hits      # noqa: E402
from run_pileup_fake_background import n_layers_with_hits, LAYER_NAME_TO_IDX, PRIMARY_VERTEX_CM  # noqa: E402
from pileup_hits_suppressed import build_ancestry_pool_index      # noqa: E402
import pileup_hits_suppressed as phs                              # noqa: E402
from run_pileup_fake_background_suppressed import ANCESTRY_POOL_PATH  # noqa: E402
from tracking_efficiency import BASELINE_SELECTION                # noqa: E402
SEED, MU, CHUNK = 90210777, 50, 100
POOL = None


def _init(mode):
    global POOL
    if mode in ("ETA_MERGE", "ETA_NOMERGE"):
        ld.install("A", "Z1160")
    else:
        raise SystemExit("P8e modes: ETA_MERGE, ETA_NOMERGE")
    POOL = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))


def one_event(i, mode):
    ss = np.random.SeedSequence([SEED, int(MU), i]); c1, c2 = ss.spawn(2)
    hits, st = phs.sample_pileup_hits_suppressed(POOL, MU, np.random.default_rng(c1), np.random.default_rng(c2),
                                                 B_tesla=2.0, selection=BASELINE_SELECTION)
    if mode == "ETA_MERGE":
        hits = merge_neighboring_pixel_hits(hits)
    hbl = {k: [] for k in range(1, 9)}
    for h in hits:
        hbl[LAYER_NAME_TO_IDX[h["layer"]]].append(tuple(vertex_relative_hits([(h["x"], h["y"], h["z"])], PRIMARY_VERTEX_CM)[0]))
    cands = seeding_and_iterative_fit(hbl)
    best = max((n_layers_with_hits(c["layers"]) for c in cands), default=0)
    w = select_reconstructed_plane(cands)
    mult = check_hit_multiplicity(w["layers"]) if w else False
    ds = w["fit"]["delta_s"] if w else np.nan; dw = w["fit"]["delta_w"] if w else np.nan
    return dict(event_i=i, n_pu_interactions=st["n_pu_interactions"], n_hits=len(hits),
                **{f"n_hits_L{k}": len(v) for k, v in hbl.items()},
                n_candidates_raw=len(cands), best_layers=best, has_4_of_8_plane=best >= 4, has_8_of_8_plane=best >= 8,
                sec3c_plane_found=w is not None, sec3c_ds=ds, sec3c_dw=dw,
                sec3c_n_hits=len(w["layers"]) if w else np.nan, sec3c_n_layers=len(set(w["layers"])) if w else np.nan,
                hit_multiplicity_pass=bool(mult), delta_w_pass=bool(w is not None and dw < 1.0),
                delta_s_pass_0p01=bool(w is not None and ds < 0.01),
                final_sec_iv_pass=bool(w is not None and mult and ds < 0.01))


def chunk_job(a):
    mode, start, stop = a
    return start, [one_event(i, mode) for i in range(start, stop)]


def main():
    mode, n = sys.argv[1], int(sys.argv[2])
    outd = f"{HERE}/../logs/P8_chunks_{mode}"; os.makedirs(outd, exist_ok=True)
    todo = [(mode, s, min(s + CHUNK, n)) for s in range(0, n, CHUNK) if not os.path.exists(f"{outd}/chunk_{s:06d}.csv")]
    print(f"{mode}: {len(todo)} chunks to run", flush=True)
    t0 = time.time()
    with mp.Pool(10, initializer=_init, initargs=(mode,)) as pool:
        for k, (start, rows) in enumerate(pool.imap_unordered(chunk_job, todo), 1):
            tmp = f"{outd}/chunk_{start:06d}.csv.tmp"
            pd.DataFrame(rows).to_csv(tmp, index=False); os.replace(tmp, f"{outd}/chunk_{start:06d}.csv")
            print(f"  chunk {start} done ({k}/{len(todo)}), {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
