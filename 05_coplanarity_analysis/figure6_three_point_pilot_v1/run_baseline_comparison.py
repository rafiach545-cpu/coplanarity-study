"""
Baseline-vs-optimized comparison: for ONE real trigger-passing event per
pilot point, run the ORIGINAL unmodified integrate_trajectory and compare
against the already-computed optimized-v2 result. Requires identical
discrete outputs and unchanged physics verdicts.
"""
import sys
import time
import json
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")

import trajectory_to_hits
import quirk_trajectory
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, check_hit_multiplicity,
                              vertex_relative_hits)

BASE = "/home/rafia/coplanarity_study"
PILOT = f"{BASE}/05_coplanarity_analysis/figure6_three_point_pilot_v1"
LAMBDA_GEV = 2e-6
LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}

TARGETS = [
    ("EW_200GeV", "EW", 200.0, 1),
    ("colored_1500GeV", "colored", 1500.0, 0),
    ("colored_2400GeV", "colored", 2400.0, 1),
]


def analyze(row, mq, charge1, charge2, rng):
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
    t0 = time.perf_counter()
    hits, traj = trajectory_to_hits.simulate_quirk_hits(
        p1, p2, mass_gev=mq, Lambda_gev=LAMBDA_GEV, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0)
    merged = trajectory_to_hits.merge_neighboring_pixel_hits(hits, adjacency=1)
    vertex_cm = traj["vertex_cm"]
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in merged:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    candidates = seeding_and_iterative_fit(hits_by_layer)
    sec3c_winner = select_reconstructed_plane(candidates)
    secIV_winner = apply_signal_region_cuts(candidates)
    wall = time.perf_counter() - t0
    return {
        "n_hits_postmerge": len(merged), "n_candidates": len(candidates),
        "sec3c_plane_found": sec3c_winner is not None,
        "sec3c_ds_cm": sec3c_winner["fit"]["delta_s"] if sec3c_winner else None,
        "sec3c_dw_cm": sec3c_winner["fit"]["delta_w"] if sec3c_winner else None,
        "hit_multiplicity_pass": check_hit_multiplicity(sec3c_winner["layers"]) if sec3c_winner else False,
        "final_sec_iv_pass": secIV_winner is not None,
        "wall_time_s": wall,
    }


results = []
for point_name, benchmark, mq, row_idx in TARGETS:
    trig = pd.read_csv(f"{PILOT}/{point_name}/event_tables/trigger_passing_events.csv")
    row = trig.iloc[row_idx]
    if benchmark == "colored":
        charge1, charge2 = float(row["charge1"]), float(row["charge2"])
    else:
        PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
        charge1 = PDG_TO_CHARGE[int(row["pdg1"])]
        charge2 = PDG_TO_CHARGE[int(row["pdg2"])]

    trajectory_to_hits.integrate_trajectory = quirk_trajectory.integrate_trajectory
    rng_base = np.random.default_rng(4242)
    baseline = analyze(row, mq, charge1, charge2, rng_base)

    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    trajectory_to_hits.integrate_trajectory = integrate_trajectory_fast_v2
    rng_opt = np.random.default_rng(4242)
    optimized = analyze(row, mq, charge1, charge2, rng_opt)

    discrete_match = (
        baseline["n_hits_postmerge"] == optimized["n_hits_postmerge"] and
        baseline["sec3c_plane_found"] == optimized["sec3c_plane_found"] and
        baseline["hit_multiplicity_pass"] == optimized["hit_multiplicity_pass"] and
        baseline["final_sec_iv_pass"] == optimized["final_sec_iv_pass"]
    )
    ds_diff = (abs(baseline["sec3c_ds_cm"] - optimized["sec3c_ds_cm"])
               if baseline["sec3c_ds_cm"] is not None and optimized["sec3c_ds_cm"] is not None else None)
    speedup = baseline["wall_time_s"] / optimized["wall_time_s"] if optimized["wall_time_s"] > 0 else None

    result = {"point": point_name, "row_index": row_idx, "discrete_match": discrete_match,
               "ds_diff": ds_diff, "baseline_wall_s": baseline["wall_time_s"],
               "optimized_wall_s": optimized["wall_time_s"], "speedup": speedup,
               "baseline_final_pass": baseline["final_sec_iv_pass"],
               "optimized_final_pass": optimized["final_sec_iv_pass"]}
    results.append(result)
    print(f"{point_name} row{row_idx}: discrete_match={discrete_match} ds_diff={ds_diff} "
          f"baseline={baseline['wall_time_s']:.2f}s optimized={optimized['wall_time_s']:.2f}s speedup={speedup:.2f}x")

df = pd.DataFrame(results)
df.to_csv(f"{PILOT}/metadata/baseline_vs_optimized_comparison.csv", index=False)
print(f"\nALL DISCRETE OUTPUTS MATCH: {bool(df['discrete_match'].all())}")
print(f"ALL PHYSICS VERDICTS (final_sec_iv_pass) UNCHANGED: {bool((df['baseline_final_pass']==df['optimized_final_pass']).all())}")
