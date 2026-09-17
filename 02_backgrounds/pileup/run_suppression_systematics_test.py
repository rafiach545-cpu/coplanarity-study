"""
Bounded Fig 1(b) suppression-systematics sensitivity test (2026-09-17).
NOT the large-statistics run. Uses the SAME cached ancestry pool and
UNCHANGED reconstruction/coplanarity pipeline; only the tracking-efficiency
CURVE VARIANT differs (central / lower / upper total-systematic envelope,
digitized in fig1b_digitized_with_bands_v2.csv). Paired comparison: the
SAME per-event SeedSequence([seed, mu, event_i]) is used across all three
variants, so rng_pileup/rng_suppression draws are IDENTICAL -- only the
efficiency LOOKUP value differs, isolating the curve's effect.

Reuses coplanarity_fit.py's unchanged seeding_and_iterative_fit,
select_reconstructed_plane, check_hit_multiplicity, apply_signal_region_cuts
-- no cut, threshold, or detector value is touched anywhere in this file.
"""
import sys
import time
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from coplanarity_fit import (seeding_and_iterative_fit, vertex_relative_hits,
                              select_reconstructed_plane, check_hit_multiplicity,
                              apply_signal_region_cuts)
from run_pileup_fake_background import n_layers_with_hits, LAYER_NAME_TO_IDX, PRIMARY_VERTEX_CM
from pileup_hits_suppressed import build_ancestry_pool_index, sample_pileup_hits_suppressed
from tracking_efficiency import BASELINE_SELECTION

ANCESTRY_POOL_PATH = "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv"
SEED = 90210777  # SAME seed as the main sweep, for a genuinely paired comparison


def run_one(mu, event_i, pool_index, variant):
    ss = np.random.SeedSequence([SEED, int(mu), event_i])
    child_pileup, child_suppression = ss.spawn(2)
    rng_pileup = np.random.default_rng(child_pileup)
    rng_suppression = np.random.default_rng(child_suppression)

    pu_hits, pu_stats = sample_pileup_hits_suppressed(
        pool_index, mu, rng_pileup, rng_suppression, B_tesla=2.0,
        selection=BASELINE_SELECTION, efficiency_variant=variant)

    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in pu_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], PRIMARY_VERTEX_CM)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))

    candidates = seeding_and_iterative_fit(hits_by_layer)
    best_n_layers = max((n_layers_with_hits(c["layers"]) for c in candidates), default=0)
    winner = select_reconstructed_plane(candidates)
    ds = winner["fit"]["delta_s"] if winner is not None else np.nan
    dw = winner["fit"]["delta_w"] if winner is not None else np.nan
    hit_mult_pass = check_hit_multiplicity(winner["layers"]) if winner is not None else False
    final_pass = apply_signal_region_cuts(candidates) is not None

    return {
        "mu": mu, "variant": variant, "event_i": event_i,
        "n_pu_interactions": pu_stats["n_pu_interactions"],
        "n_pu_hits_before_suppression": pu_stats["n_pu_hits_premerge_before_suppression"],
        "n_pu_hits_after_suppression": pu_stats["n_pu_hits_premerge_after_suppression"],
        "n_tracks_primary_removed": pu_stats["n_tracks_primary_removed"],
        "n_tracks_primary_kept": pu_stats["n_tracks_primary_kept"],
        "n_candidates": len(candidates),
        "best_n_layers": best_n_layers,
        "has_winner": winner is not None,
        "delta_s": ds, "delta_w": dw,
        "hit_multiplicity_pass": hit_mult_pass,
        "final_sec_iv_pass": final_pass,
    }


if __name__ == "__main__":
    mus = [10.0, 50.0]
    n_events = 75
    variants = ["central", "lower", "upper"]

    pool_index = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))
    rows = []
    t0 = time.time()
    for mu in mus:
        for variant in variants:
            vt0 = time.time()
            for event_i in range(n_events):
                rows.append(run_one(mu, event_i, pool_index, variant))
            print(f"mu={mu} variant={variant}: {n_events} events in {time.time()-vt0:.1f}s", flush=True)
    print(f"TOTAL wall time: {time.time()-t0:.1f}s")

    df = pd.DataFrame(rows)
    out_path = "/home/rafia/coplanarity_study/05_coplanarity_analysis/suppression_systematics_test_2026-09-17.csv"
    df.to_csv(out_path, index=False)
    print("saved", out_path)
