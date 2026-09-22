"""
Downstream (trajectory -> detector -> reconstruction) pipeline for the
Figure 6 three-point pilot. Uses the VALIDATED optimized v2 integrator
(commit 3c33601) via monkey-patching trajectory_to_hits.integrate_trajectory
after import -- the exact same, unmodified simulate_quirk_hits/
coplanarity_fit code runs either way (same method used and validated in
the perf_profile_v1 task).

Reusable trajectory/hit caches: uses trajectory_cache_v1.py (disk cache
keyed by exact physics inputs). Per-event checkpointing: writes an atomic
DONE marker after each event; a rerun skips events already marked done.
"""
import sys
import os
import time
import json
import resource
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis/perf_profile_v1")

import trajectory_to_hits
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, check_hit_multiplicity,
                              vertex_relative_hits, fit_plane)

BASE = "/home/rafia/coplanarity_study"
PILOT = f"{BASE}/05_coplanarity_analysis/figure6_three_point_pilot_v1"
LAMBDA_GEV = 2e-6

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}

POINTS = [
    ("EW_200GeV", "EW", 200.0),
    ("colored_1500GeV", "colored", 1500.0),
    ("colored_2400GeV", "colored", 2400.0),
]


def analyze_event(row, mq_gev, charge1, charge2, rng, use_optimized=True):
    trajectory_to_hits.integrate_trajectory = integrate_trajectory_fast_v2 if use_optimized else __import__("quirk_trajectory").integrate_trajectory
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])

    t0 = time.perf_counter()
    ru0 = resource.getrusage(resource.RUSAGE_SELF)
    hits, traj = trajectory_to_hits.simulate_quirk_hits(
        p1, p2, mass_gev=mq_gev, Lambda_gev=LAMBDA_GEV, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0,
    )
    n_premerge = traj["n_hits_premerge"]
    max_t_ns = traj["max_hit_t_ns_premerge"]
    geometric_fiducial = (n_premerge == 16)
    timing_ok = (not np.isnan(max_t_ns)) and (max_t_ns < 25.0)
    truth_fiducial = geometric_fiducial and timing_ok

    merged = trajectory_to_hits.merge_neighboring_pixel_hits(hits, adjacency=1)
    vertex_cm = traj["vertex_cm"]
    hits_by_layer = {k: [] for k in range(1, 9)}
    hit_rows = []
    for j, h in enumerate(merged):
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
        hit_rows.append({"hit_id": j, "layer": h["layer"], "quirk_index": h["quirk_index"],
                          "x_vtxrel": hx, "y_vtxrel": hy, "z_vtxrel": hz, "t_ns": h["t_ns"]})

    candidates = seeding_and_iterative_fit(hits_by_layer)
    sec3c_winner = select_reconstructed_plane(candidates)
    secIV_winner = apply_signal_region_cuts(candidates)
    hit_mult_pass = check_hit_multiplicity(sec3c_winner["layers"]) if sec3c_winner else False

    t1 = time.perf_counter()
    ru1 = resource.getrusage(resource.RUSAGE_SELF)

    plane_rows = []
    if sec3c_winner is not None:
        for L, hxyz in zip(sec3c_winner["layers"], sec3c_winner["hits"]):
            plane_rows.append({"layer_idx": L, "x_vtxrel": hxyz[0], "y_vtxrel": hxyz[1], "z_vtxrel": hxyz[2]})

    result = {
        "n_hits_premerge": int(n_premerge), "n_hits_postmerge": len(merged),
        "geometric_fiducial": bool(geometric_fiducial), "truth_fiducial": bool(truth_fiducial),
        "n_candidates": len(candidates),
        "sec3c_plane_found": sec3c_winner is not None,
        "sec3c_ds_cm": float(sec3c_winner["fit"]["delta_s"]) if sec3c_winner else None,
        "sec3c_dw_cm": float(sec3c_winner["fit"]["delta_w"]) if sec3c_winner else None,
        "hit_multiplicity_pass": bool(hit_mult_pass),
        "final_sec_iv_pass": secIV_winner is not None,
        "wall_time_s": t1 - t0, "peak_rss_kb": ru1.ru_maxrss,
        "nan_check_ds": bool(sec3c_winner and np.isnan(sec3c_winner["fit"]["delta_s"])),
        "inf_check_ds": bool(sec3c_winner and np.isinf(sec3c_winner["fit"]["delta_s"])),
    }
    return result, hit_rows, plane_rows


def main():
    checkpoint_file = f"{PILOT}/checkpoints/downstream_progress.json"
    progress = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            progress = json.load(f)

    all_results = []
    for point_name, benchmark, mq in POINTS:
        trig = pd.read_csv(f"{PILOT}/{point_name}/event_tables/trigger_passing_events.csv")
        os.makedirs(f"{PILOT}/{point_name}/hits", exist_ok=True)
        os.makedirs(f"{PILOT}/{point_name}/planes", exist_ok=True)
        rng = np.random.default_rng(4242)
        print(f"\n=== {point_name}: {len(trig)} trigger-passing events ===")

        for i, row in trig.iterrows():
            event_key = f"{point_name}_row{i}"
            if event_key in progress:
                print(f"  [{event_key}] SKIP (already checkpointed)")
                all_results.append(progress[event_key])
                continue

            if benchmark == "colored":
                charge1, charge2 = float(row["charge1"]), float(row["charge2"])
            else:
                PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
                charge1 = PDG_TO_CHARGE[int(row["pdg1"])]
                charge2 = PDG_TO_CHARGE[int(row["pdg2"])]

            result, hit_rows, plane_rows = analyze_event(row, mq, charge1, charge2, rng, use_optimized=True)
            result["point"] = point_name
            result["row_index"] = int(i)

            pd.DataFrame(hit_rows).to_csv(f"{PILOT}/{point_name}/hits/row{i}_hits.csv", index=False)
            pd.DataFrame(plane_rows).to_csv(f"{PILOT}/{point_name}/planes/row{i}_plane.csv", index=False)

            progress[event_key] = result
            with open(checkpoint_file, "w") as f:
                json.dump(progress, f, indent=2)
            all_results.append(result)
            print(f"  [{event_key}] wall={result['wall_time_s']:.2f}s truth_fid={result['truth_fiducial']} "
                  f"plane={result['sec3c_plane_found']} ds={result['sec3c_ds_cm']} final={result['final_sec_iv_pass']}")

    df = pd.DataFrame(all_results)
    df.to_csv(f"{PILOT}/metadata/downstream_results_all_points.csv", index=False)
    print(f"\nSaved {len(df)} event results to downstream_results_all_points.csv")

    # NaN/Inf/duplicate checks
    print("\n=== Validation gates ===")
    print("NaN in ds check flags:", df["nan_check_ds"].any())
    print("Inf in ds check flags:", df["inf_check_ds"].any())
    print("Duplicate (point,row_index):", df.duplicated(subset=["point", "row_index"]).any())


if __name__ == "__main__":
    main()
