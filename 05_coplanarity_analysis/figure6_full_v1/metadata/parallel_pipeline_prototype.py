"""
Prototype/validation: parallelize the downstream (trajectory -> detector ->
reconstruction) pipeline across independent events using multiprocessing.
No change to any physics, algorithm, or cut logic -- analyze_event() is
called unmodified in each worker. The only change is WHICH RNG SEED each
event draws (independent per-event substreams via SeedSequence.spawn,
required for safe parallel Monte Carlo -- the serial pipeline instead
advanced one shared rng object sequentially across events for a point).

This script only validates correctness/determinism/speedup on a handful of
real pilot events. It does not touch the three-point pilot's own committed
outputs.
"""
import sys
import time
import multiprocessing as mp
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")

PILOT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_three_point_pilot_v1"
LAMBDA_GEV = 2e-6
LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}


def _worker_init():
    global trajectory_to_hits, seeding_and_iterative_fit, apply_signal_region_cuts
    global select_reconstructed_plane, check_hit_multiplicity, vertex_relative_hits
    import trajectory_to_hits as tth
    from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
    tth.integrate_trajectory = integrate_trajectory_fast_v2
    trajectory_to_hits = tth
    from coplanarity_fit import (seeding_and_iterative_fit as sif, apply_signal_region_cuts as asrc,
                                  select_reconstructed_plane as srp, check_hit_multiplicity as chm,
                                  vertex_relative_hits as vrh)
    seeding_and_iterative_fit, apply_signal_region_cuts = sif, asrc
    select_reconstructed_plane, check_hit_multiplicity, vertex_relative_hits = srp, chm, vrh


def analyze_event(row_dict, mq_gev, charge1, charge2, seed):
    rng = np.random.default_rng(seed)
    p1 = (row_dict["px1"], row_dict["py1"], row_dict["pz1"], row_dict["E1"])
    p2 = (row_dict["px2"], row_dict["py2"], row_dict["pz2"], row_dict["E2"])
    t0 = time.perf_counter()
    hits, traj = trajectory_to_hits.simulate_quirk_hits(
        p1, p2, mass_gev=mq_gev, Lambda_gev=LAMBDA_GEV, B_tesla=2.0,
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
        "n_hits_postmerge": len(merged),
        "sec3c_plane_found": sec3c_winner is not None,
        "sec3c_ds_cm": float(sec3c_winner["fit"]["delta_s"]) if sec3c_winner else None,
        "final_sec_iv_pass": secIV_winner is not None,
        "wall_time_s": wall, "seed": seed,
    }


def _worker(args):
    row_dict, mq_gev, charge1, charge2, seed = args
    return analyze_event(row_dict, mq_gev, charge1, charge2, seed)


def build_jobs():
    jobs = []
    seed_seq = np.random.SeedSequence(4242)
    for point_name, benchmark, mq in [("EW_200GeV", "EW", 200.0),
                                       ("colored_1500GeV", "colored", 1500.0),
                                       ("colored_2400GeV", "colored", 2400.0)]:
        trig = pd.read_csv(f"{PILOT}/{point_name}/event_tables/trigger_passing_events.csv")
        child_seeds = seed_seq.spawn(len(trig))
        for i, row in trig.iterrows():
            if benchmark == "colored":
                charge1, charge2 = float(row["charge1"]), float(row["charge2"])
            else:
                PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
                charge1 = PDG_TO_CHARGE[int(row["pdg1"])]
                charge2 = PDG_TO_CHARGE[int(row["pdg2"])]
            seed = int(child_seeds[i].generate_state(1)[0])
            jobs.append((row.to_dict(), mq, charge1, charge2, seed, f"{point_name}_row{i}"))
    return jobs


if __name__ == "__main__":
    jobs = build_jobs()
    print(f"Total jobs (all 10 pilot trigger-passing events): {len(jobs)}")

    # --- Serial baseline ---
    _worker_init()
    t0 = time.perf_counter()
    serial_results = {key: analyze_event(rd, mq, c1, c2, seed)
                       for (rd, mq, c1, c2, seed, key) in jobs}
    serial_wall = time.perf_counter() - t0
    print(f"Serial total wall: {serial_wall:.2f}s")

    # --- Parallel (3 worker processes, leaving 1 core free) ---
    job_args = [(rd, mq, c1, c2, seed) for (rd, mq, c1, c2, seed, key) in jobs]
    keys = [key for (*_, key) in jobs]
    t0 = time.perf_counter()
    with mp.Pool(processes=3, initializer=_worker_init) as pool:
        parallel_out = pool.map(_worker, job_args)
    parallel_wall = time.perf_counter() - t0
    parallel_results = dict(zip(keys, parallel_out))
    print(f"Parallel (3 workers) total wall: {parallel_wall:.2f}s")
    print(f"Speedup: {serial_wall / parallel_wall:.2f}x")

    # --- Rerun parallel a second time: determinism check ---
    t0 = time.perf_counter()
    with mp.Pool(processes=3, initializer=_worker_init) as pool:
        parallel_out2 = pool.map(_worker, job_args)
    parallel_results2 = dict(zip(keys, parallel_out2))

    # --- Validation ---
    all_match_serial = True
    all_match_rerun = True
    for key in keys:
        s, p1_, p2_ = serial_results[key], parallel_results[key], parallel_results2[key]
        if (s["n_hits_postmerge"], s["sec3c_plane_found"], s["sec3c_ds_cm"], s["final_sec_iv_pass"]) != \
           (p1_["n_hits_postmerge"], p1_["sec3c_plane_found"], p1_["sec3c_ds_cm"], p1_["final_sec_iv_pass"]):
            all_match_serial = False
            print(f"MISMATCH (serial vs parallel) at {key}: {s} vs {p1_}")
        if (p1_["n_hits_postmerge"], p1_["sec3c_plane_found"], p1_["sec3c_ds_cm"], p1_["final_sec_iv_pass"]) != \
           (p2_["n_hits_postmerge"], p2_["sec3c_plane_found"], p2_["sec3c_ds_cm"], p2_["final_sec_iv_pass"]):
            all_match_rerun = False
            print(f"MISMATCH (parallel run1 vs run2 -- nondeterminism) at {key}: {p1_} vs {p2_}")

    print(f"\nALL EVENTS MATCH SERIAL (same seed -> same physics): {all_match_serial}")
    print(f"PARALLEL RERUN IS DETERMINISTIC (bit-identical across two parallel runs): {all_match_rerun}")

    result = {
        "serial_wall_s": serial_wall, "parallel_wall_s": parallel_wall,
        "speedup": serial_wall / parallel_wall,
        "all_match_serial": all_match_serial, "all_match_rerun": all_match_rerun,
        "n_events": len(jobs),
    }
    import json
    with open("/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_full_v1/metadata/PARALLEL_VALIDATION.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
