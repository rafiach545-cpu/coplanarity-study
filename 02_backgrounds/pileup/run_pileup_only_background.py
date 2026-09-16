"""
Part D correction (re-audit, 2026-09-16): the paper's own pile-up
BACKGROUND-RATE metric (Sec IV, verbatim): "Given the O(1000) unassociated
pile-up hits per layer in the tracker, a subset of these hits do
accidentally land on a plane. Through our reconstruction algorithm, only
~1e-3 of all background events contain a plane with at least one hit in 4
out of 8 layers. The number rapidly drops to 6e-5, for events with a plane
that contains at least one hit in each layer."

This describes running the plane-finding algorithm on PILE-UP-ONLY "events"
(no hard-scatter object at all) and asking how often a FAKE candidate plane
forms by accident -- NOT overlaying pile-up onto a real signal event.
run_pileup_overlay.py's signal+pileup test (does a real EW-quirk event's
own reconstruction survive contamination) answers a different, also useful
question, but must never be reported as this background rate. This module
implements the paper's own metric directly.

PRIMARY VERTEX for a pile-up-only "event" (item 4 of the re-audit): the
paper's algorithm description (Sec III C) states "We will assume that the
primary vertex is identified correctly, and is located at the origin" as a
general operating assumption for the reconstruction step -- it does not
separately address the case of an event with no real hard interaction to
identify. NOT SPECIFIED BY THE PAPER for this edge case. This module takes
the most direct literal reading of that same sentence and fits every
pile-up-only "event" relative to the GLOBAL ORIGIN (0,0,0), i.e. applies NO
vertex shift at all -- the natural degenerate case of "the identified
vertex is the origin" when there is no true hard vertex to look up.
Documented as an assumption, not presented as a paper requirement.
"""
import sys
import time
import numpy as np
import pandas as pd
from collections import Counter
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from coplanarity_fit import seeding_and_iterative_fit, vertex_relative_hits
from pileup_hits import build_pool_index, sample_pileup_hits

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}
POOL_PATH = "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_FINAL.csv"
PRIMARY_VERTEX_CM = np.array([0.0, 0.0, 0.0])  # see module docstring


def n_layers_with_hits(layers, n_layers_total=8):
    counts = Counter(layers)
    return sum(1 for l in range(1, n_layers_total + 1) if counts.get(l, 0) >= 1)


def run_one_background_event(mu, rng, pool_index, B_tesla=2.0):
    pu_hits, pu_stats = sample_pileup_hits(pool_index, mu, rng, B_tesla=B_tesla)

    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in pu_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], PRIMARY_VERTEX_CM)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    per_layer_counts = {k: len(v) for k, v in hits_by_layer.items()}

    candidates = seeding_and_iterative_fit(hits_by_layer)
    best_n_layers = max((n_layers_with_hits(c["layers"]) for c in candidates), default=0)

    return {
        "n_pu_interactions": pu_stats["n_pu_interactions"],
        "n_pu_particles_propagated": pu_stats["n_pu_particles_propagated"],
        "n_pu_hits_premerge": pu_stats["n_pu_hits_premerge"],
        "per_layer_hit_counts": per_layer_counts,
        "n_candidates": len(candidates),
        "best_candidate_n_layers_with_hit": best_n_layers,
        "has_4_of_8_plane": best_n_layers >= 4,
        "has_8_of_8_plane": best_n_layers >= 8,
    }


def run_background_study(mu, n_bg_events, seed=90210001, label=None):
    pool_index = build_pool_index(pd.read_csv(POOL_PATH))
    rows = []
    t0 = time.time()
    for i in range(n_bg_events):
        rng = np.random.default_rng(seed + i)
        rows.append(run_one_background_event(mu, rng, pool_index))
    dt = time.time() - t0

    df = pd.DataFrame(rows)
    tag = label if label is not None else f"mu{mu}"
    out_path = f"/home/rafia/coplanarity_study/05_coplanarity_analysis/pileup_only_background_{tag}.csv"
    df.to_csv(out_path, index=False)

    n = len(df)
    rate_4of8 = df["has_4_of_8_plane"].mean() if n else float("nan")
    rate_8of8 = df["has_8_of_8_plane"].mean() if n else float("nan")
    print(f"[mu={mu}, n_bg_events={n}] wall time {dt:.1f}s ({dt/max(n,1):.3f} s/event) -> {out_path}")
    print(f"rate(>=1 plane, >=4/8 layers) = {rate_4of8:.4g} (paper: ~1e-3)")
    print(f"rate(>=1 plane, 8/8 layers)   = {rate_8of8:.4g} (paper: ~6e-5)")
    return df, out_path


if __name__ == "__main__":
    mu = float(sys.argv[1])
    n_bg_events = int(sys.argv[2])
    label = sys.argv[3] if len(sys.argv) > 3 else None
    run_background_study(mu, n_bg_events, label=label)
