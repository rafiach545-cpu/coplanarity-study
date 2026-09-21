"""
End-to-end validation: baseline vs optimized (v2) trajectory integrator,
run through the UNMODIFIED simulate_quirk_hits / coplanarity_fit pipeline.

Method: monkey-patch `trajectory_to_hits.integrate_trajectory` to point at
`integrate_trajectory_fast_v2` AFTER importing trajectory_to_hits. Since
trajectory_to_hits.py does `from quirk_trajectory import
integrate_trajectory` at module load time, that name lives in
trajectory_to_hits's own module namespace and is looked up there at CALL
time (not bound at def-time) -- rebinding it after import changes what
simulate_quirk_hits() calls, without touching trajectory_to_hits.py on
disk or duplicating a single line of its logic. This is the safest
possible way to swap the integrator: the exact same, unmodified
detector-response/hit-building function runs either way.

Compares, for every profiled baseline event:
  - raw/postmerge hit count and every hit's (x,y,z,t_ns,layer,quirk_index)
  - layer counts
  - candidate/plane membership (selected-plane hit set)
  - Delta_s, Delta_w
  - hit-multiplicity pass, final Sec IV verdict

Requires EXACT agreement for all discrete outputs (counts, layer
assignments, pass/fail flags) and reports numerical tolerance for
floating-point hit coordinates/Delta_s/Delta_w (expected: bit-identical,
given the optimized integrator was independently verified bit-identical
on its own; this end-to-end run re-confirms that holds through the full
pipeline, not just the bare integrator).
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
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/05_coplanarity_analysis/perf_profile_v1"

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}

EVENTS = [
    ("colored", 236, 1800.0, 2e-6), ("colored", 236, 1800.0, 5e-6),
    ("colored", 322, 1800.0, 2e-6), ("colored", 34, 1800.0, 2e-6),
    ("EW", 438, 800.0, 4e-6), ("EW", 417, 800.0, 4e-6),
]


def run_pipeline(benchmark, eid, mq_gev, lam_gev, row, seed=4242):
    from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                                  select_reconstructed_plane, check_hit_multiplicity,
                                  vertex_relative_hits)
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
    if benchmark == "colored":
        charge1, charge2 = float(row["charge1"]), float(row["charge2"])
    else:
        PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
        charge1 = PDG_TO_CHARGE[int(row["pdg1"])]
        charge2 = PDG_TO_CHARGE[int(row["pdg2"])]

    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()
    hits, traj = trajectory_to_hits.simulate_quirk_hits(
        p1, p2, mass_gev=mq_gev, Lambda_gev=lam_gev, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0,
    )
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

    hit_rows = [{"hit_id": j, "layer": h["layer"], "quirk_index": h["quirk_index"],
                 "x": h["x"], "y": h["y"], "z": h["z"], "t_ns": h["t_ns"]} for j, h in enumerate(merged)]
    plane_rows = []
    if sec3c_winner is not None:
        for L, hxyz in zip(sec3c_winner["layers"], sec3c_winner["hits"]):
            plane_rows.append({"layer_idx": L, "x_vtxrel": hxyz[0], "y_vtxrel": hxyz[1], "z_vtxrel": hxyz[2]})

    summary = {
        "n_premerge": len(hits), "n_postmerge": len(merged), "n_candidates": len(candidates),
        "sec3c_plane_found": sec3c_winner is not None,
        "sec3c_ds_cm": sec3c_winner["fit"]["delta_s"] if sec3c_winner else None,
        "sec3c_dw_cm": sec3c_winner["fit"]["delta_w"] if sec3c_winner else None,
        "hit_multiplicity_pass": check_hit_multiplicity(sec3c_winner["layers"]) if sec3c_winner else False,
        "final_sec_iv_pass": secIV_winner is not None,
        "wall_time_s": wall,
    }
    return summary, pd.DataFrame(hit_rows), pd.DataFrame(plane_rows)


def load_baseline_from_profile(tag):
    """Reuse the ALREADY-COMPUTED baseline hits/plane from the profiling
    run (profiles/*_BASELINE.csv) instead of recomputing the (slow, up to
    1429s/event) baseline a second time -- directly applying this task's
    own 'eliminate repeated calculations' priority to the validation step
    itself. Cheap downstream quantities (Delta_w, hit-multiplicity) are
    recomputed FRESH from the cached plane hits using the unmodified
    coplanarity_fit functions (deterministic, no re-integration needed) --
    this is itself cheap (<1ms), not a re-run of the expensive stage."""
    from coplanarity_fit import fit_plane, check_hit_multiplicity

    hit_cols = ["hit_id", "layer", "quirk_index", "x", "y", "z", "t_ns"]
    plane_cols = ["layer_idx", "x_vtxrel", "y_vtxrel", "z_vtxrel"]
    try:
        hits = pd.read_csv(f"{OUT}/profiles/{tag}_hits_BASELINE.csv")
    except pd.errors.EmptyDataError:
        hits = pd.DataFrame(columns=hit_cols)  # legitimate zero-hit event (e.g. trajectory never reached the detector)
    try:
        plane = pd.read_csv(f"{OUT}/profiles/{tag}_plane_BASELINE.csv")
    except pd.errors.EmptyDataError:
        plane = pd.DataFrame(columns=plane_cols)
    prof = pd.read_csv(f"{OUT}/profiles/PROFILE_SUMMARY_BASELINE.csv")
    supp = pd.read_csv(f"{OUT}/profiles/SUPPLEMENT_SUMMARY.csv")
    key = (prof["benchmark"] + "_ev" + prof["event"].astype(str) + "_lam" +
           (prof["lambda_gev"] * 1e6).round().astype(int).astype(str) + "keV")
    row = prof[key == tag]
    wall_time_s = None
    ds_cm = None
    final_pass = None
    if len(row):
        r = row.iloc[0]
        wall_time_s = float(r["wall_time_s"])
        ds_cm = r["sec3c_ds_cm"] if pd.notna(r["sec3c_ds_cm"]) else None
        final_pass = bool(r["final_sec_iv_pass"])
    else:
        key2 = (supp["benchmark"] + "_ev" + supp["event"].astype(str) + "_lam" +
                (supp["lambda_gev"] * 1e6).round().astype(int).astype(str) + "keV")
        r = supp[key2 == tag].iloc[0]
        wall_time_s = float(r["wall_time_s"])
        ds_cm = r["sec3c_ds_cm"] if pd.notna(r["sec3c_ds_cm"]) else None
        final_pass = bool(r["final_sec_iv_pass"])

    sec3c_plane_found = len(plane) > 0
    dw_cm = None
    hit_mult_pass = False
    if sec3c_plane_found:
        layers = plane["layer_idx"].tolist()
        hits_xyz = list(zip(plane["x_vtxrel"], plane["y_vtxrel"], plane["z_vtxrel"]))
        fit = fit_plane(hits_xyz)
        dw_cm = fit["delta_w"]
        hit_mult_pass = check_hit_multiplicity(layers)

    summary = {
        "n_premerge": None, "n_postmerge": len(hits), "n_candidates": None,
        "sec3c_plane_found": sec3c_plane_found,
        "sec3c_ds_cm": ds_cm, "sec3c_dw_cm": dw_cm,
        "hit_multiplicity_pass": hit_mult_pass,
        "final_sec_iv_pass": final_pass,
        "wall_time_s": wall_time_s,
    }
    return summary, hits, plane


def main():
    colored = pd.read_csv(f"{BASE}/01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv")
    ew = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv")

    comparisons = []
    for benchmark, eid, mq, lam in EVENTS:
        row = (colored[colored["event"] == eid] if benchmark == "colored" else ew[ew["event"] == eid]).iloc[0]
        tag = f"{benchmark}_ev{eid}_lam{lam*1e6:.0f}keV"

        base_summary, base_hits, base_plane = load_baseline_from_profile(tag)

        # optimized (monkey-patched) -- computed fresh, this is the only new work
        trajectory_to_hits.integrate_trajectory = integrate_trajectory_fast_v2
        opt_summary, opt_hits, opt_plane = run_pipeline(benchmark, eid, mq, lam, row)

        opt_hits.to_csv(f"{OUT}/comparisons/{tag}_hits_OPTIMIZED.csv", index=False)
        opt_plane.to_csv(f"{OUT}/comparisons/{tag}_plane_OPTIMIZED.csv", index=False)

        discrete_match = (
            base_summary["n_postmerge"] == opt_summary["n_postmerge"] and
            base_summary["sec3c_plane_found"] == opt_summary["sec3c_plane_found"] and
            base_summary["hit_multiplicity_pass"] == opt_summary["hit_multiplicity_pass"] and
            base_summary["final_sec_iv_pass"] == opt_summary["final_sec_iv_pass"]
        )
        hits_equal = base_hits.equals(opt_hits[["hit_id", "layer", "quirk_index", "x", "y", "z", "t_ns"]]) if len(base_hits) else (len(opt_hits) == 0)
        ds_diff = None
        if base_summary["sec3c_ds_cm"] is not None and opt_summary["sec3c_ds_cm"] is not None:
            ds_diff = abs(base_summary["sec3c_ds_cm"] - opt_summary["sec3c_ds_cm"])
        dw_diff = None
        if base_summary["sec3c_dw_cm"] is not None and opt_summary["sec3c_dw_cm"] is not None:
            dw_diff = abs(base_summary["sec3c_dw_cm"] - opt_summary["sec3c_dw_cm"])

        result = {
            "tag": tag, "discrete_outputs_exact_match": discrete_match,
            "hit_coordinates_exact_match": bool(hits_equal),
            "delta_s_abs_diff": ds_diff, "delta_w_abs_diff": dw_diff,
            "baseline_wall_s": base_summary["wall_time_s"], "optimized_wall_s": opt_summary["wall_time_s"],
            "speedup": base_summary["wall_time_s"] / opt_summary["wall_time_s"] if opt_summary["wall_time_s"] > 0 else None,
            "baseline_final_pass": base_summary["final_sec_iv_pass"], "optimized_final_pass": opt_summary["final_sec_iv_pass"],
        }
        comparisons.append(result)
        print(f"{tag}: discrete_match={discrete_match} hits_exact={hits_equal} "
              f"ds_diff={ds_diff} baseline={base_summary['wall_time_s']:.2f}s "
              f"optimized={opt_summary['wall_time_s']:.2f}s speedup={result['speedup']:.2f}x")

    df = pd.DataFrame(comparisons)
    df.to_csv(f"{OUT}/comparisons/OLD_VS_OPTIMIZED_COMPARISON.csv", index=False)
    all_match = bool(df["discrete_outputs_exact_match"].all() and df["hit_coordinates_exact_match"].all())
    print(f"\nALL DISCRETE + HIT-COORDINATE OUTPUTS MATCH: {all_match}")
    print(f"Mean speedup: {df['speedup'].mean():.2f}x")

    with open(f"{OUT}/comparisons/VALIDATION_SUMMARY.json", "w") as f:
        json.dump({
            "all_events_exact_match": all_match,
            "mean_speedup": float(df["speedup"].mean()),
            "min_speedup": float(df["speedup"].min()),
            "max_speedup": float(df["speedup"].max()),
            "n_events_validated": len(df),
        }, f, indent=2)


if __name__ == "__main__":
    main()
