"""
Bounded, read-first performance profile of the Figure 6 downstream
(trajectory -> detector -> reconstruction) pipeline.

Profiles the EXACT, UNMODIFIED baseline functions via cProfile (stdlib) --
no baseline file is touched, no logic is duplicated or reimplemented, so
the profiled code path is guaranteed identical to production. Also
measures wall time, CPU time, and peak RSS via resource.getrusage() for
each (event, Lambda) run.

16 (event, Lambda) combinations profiled:
  - colored (mQ=1800GeV): events 236, 322 (low boost, pT_pair~208-232 GeV),
    34, 169 (high boost, pT_pair~847-922 GeV); each at Lambda=2keV (paper
    benchmark) and Lambda=5keV (second value, in Table I's own colored
    Lambda list)
  - EW (mQ=800GeV): events 438, 169 (low boost, pT_pair~203 GeV), 346, 417
    (high boost, pT_pair~910-999 GeV); each at Lambda=4keV (paper
    benchmark) and Lambda=2keV (second value, in Table I's own EW Lambda
    list)

No full grid launched -- this is a bounded diagnostic only.
"""
import cProfile
import io
import pstats
import resource
import sys
import time
import json
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
from trajectory_to_hits import simulate_quirk_hits, merge_neighboring_pixel_hits
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, check_hit_multiplicity,
                              vertex_relative_hits)

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/05_coplanarity_analysis/perf_profile_v1"

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}

PROFILE_FUNCS = [
    "integrate_trajectory", "find_layer_crossing", "quantize_pixel",
    "merge_neighboring_pixel_hits", "seeding_and_iterative_fit",
    "apply_signal_region_cuts", "vertex_relative_hits", "fit_plane",
]

EVENTS = [
    # (label, benchmark, event_id, mQ_gev, lambda_gev, charge1, charge2, boost_class)
]


def load_events():
    colored = pd.read_csv(f"{BASE}/01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv")
    ew = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv")

    rows = []
    colored_ids = {236: "low", 322: "low", 34: "high", 169: "high"}
    for eid, boost in colored_ids.items():
        row = colored[colored["event"] == eid].iloc[0]
        for lam in [2e-6, 5e-6]:
            rows.append(("colored", eid, row, 1800.0, lam, boost))

    ew_ids = {438: "low", 169: "low", 346: "high", 417: "high"}
    for eid, boost in ew_ids.items():
        row = ew[ew["event"] == eid].iloc[0]
        for lam in [4e-6, 2e-6]:
            rows.append(("EW", eid, row, 800.0, lam, boost))
    return rows


def run_one(benchmark, eid, row, mq_gev, lam_gev, boost, seed=4242):
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
    if benchmark == "colored":
        charge1, charge2 = float(row["charge1"]), float(row["charge2"])
    else:
        PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}  # matches analyze_ew_quirk.py exactly
        charge1 = PDG_TO_CHARGE[int(row["pdg1"])]
        charge2 = PDG_TO_CHARGE[int(row["pdg2"])]

    rng = np.random.default_rng(seed)

    ru_start = resource.getrusage(resource.RUSAGE_SELF)
    t_wall_start = time.perf_counter()

    pr = cProfile.Profile()
    pr.enable()

    hits, traj = simulate_quirk_hits(
        p1, p2, mass_gev=mq_gev, Lambda_gev=lam_gev, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0,
    )
    n_premerge = len(hits)
    merged = merge_neighboring_pixel_hits(hits, adjacency=1)
    n_postmerge = len(merged)

    vertex_cm = traj["vertex_cm"]
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in merged:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))

    candidates = seeding_and_iterative_fit(hits_by_layer)
    sec3c_winner = select_reconstructed_plane(candidates)
    secIV_winner = apply_signal_region_cuts(candidates)

    pr.disable()
    t_wall_end = time.perf_counter()
    ru_end = resource.getrusage(resource.RUSAGE_SELF)

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    func_times = {}
    for func_key, (cc, nc, tt, ct, callers) in ps.stats.items():
        fname = func_key[2]
        if fname in PROFILE_FUNCS:
            func_times[fname] = func_times.get(fname, 0.0) + ct  # cumulative time, sum if called >once

    n_hits_premerge = traj["n_hits_premerge"]
    max_t_ns = traj["max_hit_t_ns_premerge"]
    geometric_fiducial = (n_hits_premerge == 16)
    timing_ok = (not np.isnan(max_t_ns)) and (max_t_ns < 25.0)
    truth_fiducial = geometric_fiducial and timing_ok

    result = {
        "benchmark": benchmark, "event": eid, "mQ_gev": mq_gev, "lambda_gev": lam_gev,
        "boost_class": boost, "pT_pair_gev": float(np.hypot(p1[0]+p2[0], p1[1]+p2[1])),
        "wall_time_s": t_wall_end - t_wall_start,
        "cpu_time_s": (ru_end.ru_utime - ru_start.ru_utime) + (ru_end.ru_stime - ru_start.ru_stime),
        "peak_rss_kb": ru_end.ru_maxrss,
        "n_hits_premerge": n_hits_premerge, "n_hits_postmerge": n_postmerge,
        "n_candidates": len(candidates),
        "geometric_fiducial": geometric_fiducial, "truth_fiducial": truth_fiducial,
        "sec3c_plane_found": sec3c_winner is not None,
        "sec3c_ds_cm": sec3c_winner["fit"]["delta_s"] if sec3c_winner else None,
        "sec3c_dw_cm": sec3c_winner["fit"]["delta_w"] if sec3c_winner else None,
        "hit_multiplicity_pass": check_hit_multiplicity(sec3c_winner["layers"]) if sec3c_winner else False,
        "final_sec_iv_pass": secIV_winner is not None,
    }
    for fname in PROFILE_FUNCS:
        result[f"time_{fname}_s"] = func_times.get(fname, 0.0)

    # save raw hits for comparison-phase reuse
    hit_rows = [{"hit_id": j, "layer": h["layer"], "quirk_index": h["quirk_index"],
                 "x": h["x"], "y": h["y"], "z": h["z"], "t_ns": h["t_ns"]} for j, h in enumerate(merged)]
    plane_rows = []
    if sec3c_winner is not None:
        for L, hxyz in zip(sec3c_winner["layers"], sec3c_winner["hits"]):
            plane_rows.append({"layer_idx": L, "x_vtxrel": hxyz[0], "y_vtxrel": hxyz[1], "z_vtxrel": hxyz[2]})

    return result, hit_rows, plane_rows, s.getvalue()


def main():
    events = load_events()
    print(f"Profiling {len(events)} (event, Lambda) combinations...")
    results = []
    for i, (benchmark, eid, row, mq, lam, boost) in enumerate(events):
        r, hit_rows, plane_rows, full_stats = run_one(benchmark, eid, row, mq, lam, boost)
        results.append(r)
        tag = f"{benchmark}_ev{eid}_lam{lam*1e6:.0f}keV"
        pd.DataFrame(hit_rows).to_csv(f"{OUT}/profiles/{tag}_hits_BASELINE.csv", index=False)
        pd.DataFrame(plane_rows).to_csv(f"{OUT}/profiles/{tag}_plane_BASELINE.csv", index=False)
        with open(f"{OUT}/profiles/{tag}_full_cprofile.txt", "w") as f:
            f.write(full_stats)
        print(f"[{i+1}/{len(events)}] {tag}: wall={r['wall_time_s']:.3f}s "
              f"traj={r['time_integrate_trajectory_s']:.3f}s "
              f"layer_cross={r['time_find_layer_crossing_s']:.4f}s "
              f"quantize={r['time_quantize_pixel_s']:.4f}s "
              f"merge={r['time_merge_neighboring_pixel_hits_s']:.4f}s "
              f"recon={r['time_seeding_and_iterative_fit_s']:.4f}s "
              f"ds={r['sec3c_ds_cm']} final={r['final_sec_iv_pass']}")

    df = pd.DataFrame(results)
    df.to_csv(f"{OUT}/profiles/PROFILE_SUMMARY_BASELINE.csv", index=False)

    # aggregate bottleneck identification
    stage_cols = [c for c in df.columns if c.startswith("time_")]
    agg = df[stage_cols].sum().sort_values(ascending=False)
    print("\n=== Aggregate time by stage (sum over 16 runs) ===")
    print(agg)
    total_wall = df["wall_time_s"].sum()
    print(f"\nTotal wall time (16 runs): {total_wall:.2f}s")
    print(f"Mean wall time per run: {df['wall_time_s'].mean():.3f}s")
    print(f"Max peak RSS: {df['peak_rss_kb'].max()} kB")

    bottleneck = agg.index[0].replace("time_", "").replace("_s", "")
    with open(f"{OUT}/runtime/BOTTLENECK_IDENTIFICATION.json", "w") as f:
        json.dump({
            "aggregate_stage_times_s": agg.to_dict(),
            "identified_bottleneck": bottleneck,
            "bottleneck_share_of_total_pct": float(agg.iloc[0] / df["wall_time_s"].sum() * 100),
            "total_wall_time_s_16_runs": float(total_wall),
            "mean_wall_time_per_run_s": float(df["wall_time_s"].mean()),
            "max_peak_rss_kb": float(df["peak_rss_kb"].max()),
        }, f, indent=2)
    print(f"\nBOTTLENECK: {bottleneck} ({agg.iloc[0]/total_wall*100:.1f}% of total wall time)")


if __name__ == "__main__":
    main()
