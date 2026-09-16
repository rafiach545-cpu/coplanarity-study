"""
Part D: real pile-up overlay driver. For a given mu, overlays Poisson(mu)
pile-up interactions (drawn with replacement from the real 20,000-event
minimum-bias pool) onto each real EW-quirk hard event, re-runs the unchanged
Sec III C / Sec IV reconstruction on the combined hit set, and records the
full cutflow plus pile-up-specific diagnostics (multiplicity, pool reuse,
per-layer hit counts, transitions relative to the mu=0 baseline).

Hard-event sample: the real EW quirk (mQ=800 GeV, Lambda=4 keV) momenta
already used for the validated v3 signal cutflow
(ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv), re-run here from the
truth momenta so pile-up can be overlaid onto the SAME underlying hard
trajectories at each mu (only the pile-up draw and RNG stream differ).

Vertex convention (Sec III C, "primary vertex identified correctly, located
at the origin"): the plane fit uses the HARD event's own true vertex only;
pile-up hits are generated at their own (independently beamspot-smeared)
lab-frame position like any other hit, then combined and re-fit relative to
the hard vertex -- pile-up does not get its own separate fit.
"""
import sys
import time
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
from trajectory_to_hits import simulate_quirk_hits
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, vertex_relative_hits)
from pileup_hits import build_pool_index, sample_pileup_hits, overlay_and_merge

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}
PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
MQ_GEV = 800.0
LAMBDA_GEV = 4e-6
TIMING_CUT_NS = 25.0
POOL_PATH = "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_FINAL.csv"


def build_hits_by_layer(merged_hits, vertex_cm):
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in merged_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    return hits_by_layer


def run_one_event(row, mu, rng, pool_index):
    p1 = (row.px1, row.py1, row.pz1, row.E1)
    p2 = (row.px2, row.py2, row.pz2, row.E2)
    charge1 = PDG_TO_CHARGE[int(row.pdg1)]
    charge2 = PDG_TO_CHARGE[int(row.pdg2)]

    hits, traj = simulate_quirk_hits(
        p1, p2, mass_gev=MQ_GEV, Lambda_gev=LAMBDA_GEV, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0,
    )
    n_premerge = traj["n_hits_premerge"]
    max_t_ns = traj["max_hit_t_ns_premerge"]
    geometric_fiducial = (n_premerge == 16)
    timing_ok = (not np.isnan(max_t_ns)) and (max_t_ns < TIMING_CUT_NS)
    truth_fiducial = geometric_fiducial and timing_ok
    vertex_cm = traj["vertex_cm"]

    result = {
        "event": int(row.event), "mu": mu,
        "truth_fiducial": truth_fiducial,
        "n_pu_interactions": 0, "n_pu_particles_propagated": 0,
        "n_pu_hits_premerge": 0,
        "n_hits_combined_premerge": len(hits), "n_hits_combined_postmerge": len(hits),
        "n_candidates": 0, "passes_signal_region": False,
        "ds": np.nan, "dw": np.nan,
        "per_layer_hit_counts": None,
    }

    pu_hits, pu_stats = sample_pileup_hits(pool_index, mu, rng, B_tesla=2.0)
    result["n_pu_interactions"] = pu_stats["n_pu_interactions"]
    result["n_pu_particles_propagated"] = pu_stats["n_pu_particles_propagated"]
    result["n_pu_hits_premerge"] = pu_stats["n_pu_hits_premerge"]

    if not truth_fiducial:
        return result  # matches paper's fid/reco factorization

    merged, mstats = overlay_and_merge(hits, pu_hits)
    result["n_hits_combined_premerge"] = mstats["n_hits_premerge_combined"]
    result["n_hits_combined_postmerge"] = mstats["n_hits_postmerge_combined"]

    hits_by_layer = build_hits_by_layer(merged, vertex_cm)
    result["per_layer_hit_counts"] = {k: len(v) for k, v in hits_by_layer.items()}

    candidates = seeding_and_iterative_fit(hits_by_layer)
    result["n_candidates"] = len(candidates)
    if candidates:
        winner = apply_signal_region_cuts(candidates)
        result["passes_signal_region"] = winner is not None
        # Record Sec III C's own selected plane (Delta_w<1cm, smallest
        # Delta_s) even on FAILURE of the Sec IV cuts, matching the already-
        # validated analyze_ew_quirk.py convention -- needed so a mu=0
        # overlay run reproduces the v3 signal cutflow's ds/dw bit-for-bit,
        # not just its pass/fail verdict.
        best = winner if winner is not None else select_reconstructed_plane(candidates)
        if best is not None:
            result["ds"] = best["fit"]["delta_s"]
            result["dw"] = best["fit"]["delta_w"]
    return result


def run_mu(mu, n_events=None, seed=20260916, label=None):
    ew_all = pd.read_csv("/home/rafia/coplanarity_study/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv")
    # Sec IV / analyze_ew_quirk.py's own N_trigger cut (pT_pair > 200 GeV):
    # apply it FIRST, exactly as the validated v3 pipeline does, both to
    # stay physically correct (an event that never triggers is not part of
    # any efficiency denominator downstream of N_trigger) and because it is
    # the only cheap way to avoid RK4-integrating non-triggering events.
    ew = ew_all[ew_all["pT_pair"] > 200].reset_index(drop=True)
    if n_events is not None:
        ew = ew.iloc[:n_events]
    # Build the index and let the raw DataFrame go out of scope immediately
    # -- build_pool_index() copies every numeric column into pool_index, so
    # keeping `pool` alive for the rest of the run needlessly doubles peak
    # memory (~230MB pool DataFrame + ~230MB-equivalent pool_index, held
    # simultaneously for no reason -- caught during the code-safety re-audit).
    pool_index = build_pool_index(pd.read_csv(POOL_PATH))

    rows = []
    t0 = time.time()
    for i, row in enumerate(ew.itertuples(index=False)):
        rng = np.random.default_rng(seed + int(row.event))  # per-event, reproducible stream
        rows.append(run_one_event(row, mu, rng, pool_index))
    dt = time.time() - t0

    df = pd.DataFrame(rows)
    tag = label if label is not None else f"mu{mu}"
    out_path = f"/home/rafia/coplanarity_study/05_coplanarity_analysis/pileup_overlay_ew_{tag}_cutflow.csv"
    df.to_csv(out_path, index=False)
    print(f"[mu={mu}, n={len(df)}] wall time {dt:.1f}s ({dt/len(df):.3f} s/event) -> {out_path}")
    return df, out_path


if __name__ == "__main__":
    mu = float(sys.argv[1])
    n_events = int(sys.argv[2]) if len(sys.argv) > 2 else None
    label = sys.argv[3] if len(sys.argv) > 3 else None
    df, out_path = run_mu(mu, n_events=n_events, label=label)
    print(df.describe(include="all"))
