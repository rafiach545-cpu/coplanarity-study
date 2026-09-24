"""
Larger-scale (n=500/800 requested LHE events, not just the 100-event pilot)
throughput test: extract real trigger-passing events for EW_200GeV and
colored_2400GeV, then measure serial-vs-parallel downstream wall time on a
statistically meaningful, non-degenerate sample.
"""
import sys
import time
import json
import gzip
import multiprocessing as mp
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis/madgraph_pilot_v1")
sys.path.insert(0, "/home/rafia/coplanarity_study/01_signal_generation")
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")

from extract_pilot_data import parse_hepmc
from extract_quirk_momenta import _make_rhadron_charge_lookup

RUNS = {
    "EW_200GeV": {
        "hepmc": "/home/rafia/hep_tools/throughput_test_runs/quirk_ew_200gev_throughput_v1/Events/run_throughput/tag_1_pythia8_events.hepmc.gz",
        "quirk_pdg": 9000011, "mass_gev": 200.0, "mass_tol": 5.0, "require_pdg": True,
        "benchmark": "EW", "mq": 200.0,
    },
    "colored_2400GeV": {
        "hepmc": "/home/rafia/hep_tools/throughput_test_runs/quirk_colored_2400gev_throughput_v1/Events/run_throughput/tag_1_pythia8_events.hepmc.gz",
        "quirk_pdg": 1000006, "mass_gev": 2400.0, "mass_tol": 30.0, "require_pdg": False,
        "benchmark": "colored", "mq": 2400.0,
    },
}

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


def analyze_event(row, mq_gev, charge1, charge2, seed):
    rng = np.random.default_rng(seed)
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
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
    row_dict, mq, c1, c2, seed = args
    return analyze_event(row_dict, mq, c1, c2, seed)


def build_jobs():
    jobs = []
    counts = {}
    charge_of = _make_rhadron_charge_lookup()
    for point_name, cfg in RUNS.items():
        df = parse_hepmc(cfg["hepmc"], cfg["quirk_pdg"], cfg["mass_gev"], cfg["mass_tol"], cfg["require_pdg"])
        df = df[df["n_quirks_found"] == 2].reset_index(drop=True)
        n_matched = len(df)
        if cfg["benchmark"] == "colored":
            q1c = df["pdg1"].map(lambda p: charge_of(p))
            q2c = df["pdg2"].map(lambda p: charge_of(p))
            df["charge1"], df["charge2"] = q1c, q2c
            df = df[(df["charge1"].abs() == 1) & (df["charge2"].abs() == 1)].reset_index(drop=True)
        else:
            PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
            df["charge1"] = df["pdg1"].map(PDG_TO_CHARGE)
            df["charge2"] = df["pdg2"].map(PDG_TO_CHARGE)
        n_charge_filtered = len(df)
        trig = df[df["trigger_proxy_pass"]].reset_index(drop=True)
        n_trig = len(trig)
        counts[point_name] = {"n_matched": n_matched, "n_charge_filtered": n_charge_filtered, "n_trigger": n_trig}
        seed_seq = np.random.SeedSequence(4400 if point_name == "EW_200GeV" else 4401)
        child_seeds = seed_seq.spawn(len(trig))
        for i, row in trig.iterrows():
            seed = int(child_seeds[i].generate_state(1)[0])
            jobs.append((row.to_dict(), cfg["mq"], float(row["charge1"]), float(row["charge2"]), seed,
                         f"{point_name}_row{i}"))
    return jobs, counts


if __name__ == "__main__":
    jobs, counts = build_jobs()
    print("Sample counts:", json.dumps(counts, indent=2))
    print(f"Total downstream jobs (trigger-passing events): {len(jobs)}")

    job_args = [(rd, mq, c1, c2, seed) for (rd, mq, c1, c2, seed, key) in jobs]
    keys = [key for (*_, key) in jobs]

    _worker_init()
    t0 = time.perf_counter()
    serial_results = {key: analyze_event(rd, mq, c1, c2, seed)
                       for (rd, mq, c1, c2, seed, key), (rd, mq, c1, c2, seed) in zip(jobs, job_args)}
    serial_wall = time.perf_counter() - t0
    print(f"Serial total wall: {serial_wall:.2f}s")

    t0 = time.perf_counter()
    with mp.Pool(processes=3, initializer=_worker_init) as pool:
        parallel_out = pool.map(_worker, job_args)
    parallel_wall = time.perf_counter() - t0
    parallel_results = dict(zip(keys, parallel_out))
    print(f"Parallel (3 workers) total wall: {parallel_wall:.2f}s")
    print(f"Speedup: {serial_wall / parallel_wall:.2f}x")

    t0 = time.perf_counter()
    with mp.Pool(processes=3, initializer=_worker_init) as pool:
        parallel_out2 = pool.map(_worker, job_args)
    parallel_wall2 = time.perf_counter() - t0
    parallel_results2 = dict(zip(keys, parallel_out2))

    all_match_serial, all_match_rerun = True, True
    for key in keys:
        s, p1_, p2_ = serial_results[key], parallel_results[key], parallel_results2[key]
        f = lambda d: (d["n_hits_postmerge"], d["sec3c_plane_found"], d["sec3c_ds_cm"], d["final_sec_iv_pass"])
        if f(s) != f(p1_):
            all_match_serial = False
            print(f"MISMATCH serial-vs-parallel at {key}")
        if f(p1_) != f(p2_):
            all_match_rerun = False
            print(f"MISMATCH parallel-rerun at {key}")

    result = {
        "n_events": len(jobs), "counts": counts,
        "serial_wall_s": serial_wall, "parallel_wall_s": parallel_wall,
        "parallel_wall_s_rerun": parallel_wall2,
        "speedup": serial_wall / parallel_wall,
        "all_match_serial": all_match_serial, "all_match_rerun": all_match_rerun,
        "mean_s_per_event_serial": serial_wall / len(jobs) if jobs else None,
        "mean_s_per_event_parallel": parallel_wall / len(jobs) if jobs else None,
    }
    with open("/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_full_v1/metadata/THROUGHPUT_TEST_RESULT.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
