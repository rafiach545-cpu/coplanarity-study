"""
v4: additive full-diagnostics rerun of the converted-photon-only pipeline.

Does NOT modify convert_and_analyze.py (v3, authoritative) in any way --
this is a SEPARATE script that reimplements analyze_one_event's exact same
physics call sequence (same simulate_quirk_hits call, same RNG draws, same
seeding_and_iterative_fit, same select_reconstructed_plane/
apply_signal_region_cuts) and additionally extracts diagnostics from objects
v3 already computes but discards (merged hits' quirk_index/source_quirk_
indices/t_ns; the Sec IIIC winner's raw per-hit layers list for
check_hit_multiplicity). No new physics, no new cut, no changed RNG draw
order -- verified by a bit-for-bit regression test against v3 before any
full run (see test_v4_regression.py).

New columns over v3: hit_multiplicity_pass, winner_layer_hit_counts,
n_electron_hits_premerge, n_positron_hits_premerge, n_mixed_hits_premerge,
n_hits_premerge, n_hits_postmerge, t_ns_min, t_ns_max, t_ns_mean.
"""
import json
import os
import sys
import time
from collections import Counter
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
from trajectory_to_hits import simulate_quirk_hits
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, check_hit_multiplicity,
                              vertex_relative_hits)
from atlas_geometry import BEAMPIPE_RADIUS_CM, BEAMSPOT_SIGMA_Z_CM
from convert_and_analyze import (find_conversion_point, ELECTRON_MASS_GEV,
                                   CONVERSION_PROBABILITY, PER_EVENT_XSEC_PB,
                                   LAYER_NAME_TO_IDX)

BASE = "/home/rafia/coplanarity_study"
PC_DIR = f"{BASE}/02_backgrounds/photon_conversion"


def analyze_one_event_v4(row, rng, max_layer_r_cm=60.0):
    """IDENTICAL call sequence/RNG draws to convert_and_analyze.analyze_one_event
    -- only the returned diagnostics differ (additive extraction from hits/
    candidates that v3 already computes)."""
    px, py, pz, E = row["px"], row["py"], row["pz"], row["E"]
    z0_cm = rng.normal(0.0, BEAMSPOT_SIGMA_Z_CM)

    conv_point = find_conversion_point(px, py, pz, E, z0_cm, BEAMPIPE_RADIUS_CM)
    if conv_point is None:
        return {"status": "no_conversion_point", "passes": False}

    p_e_minus = np.array([px, py, pz]) / 2.0
    p_e_plus = np.array([px, py, pz]) / 2.0
    E_e = E / 2.0

    hits, traj = simulate_quirk_hits(
        (p_e_minus[0], p_e_minus[1], p_e_minus[2], E_e),
        (p_e_plus[0], p_e_plus[1], p_e_plus[2], E_e),
        mass_gev=ELECTRON_MASS_GEV, Lambda_gev=0.0, B_tesla=2.0,
        charge1=-1.0, charge2=1.0, rng=rng,
        x0_override_cm=conv_point, max_layer_r_cm=max_layer_r_cm,
    )

    n_hits = len(hits)
    vertex_cm = traj["vertex_cm"]
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))

    candidates = seeding_and_iterative_fit(hits_by_layer)
    sec3c_winner = select_reconstructed_plane(candidates)
    winner = apply_signal_region_cuts(candidates)

    # --- additive diagnostics only, no new RNG draws, no new physics ---
    n_electron = sum(1 for h in hits if h.get("quirk_index") == 0)
    n_positron = sum(1 for h in hits if h.get("quirk_index") == 1)
    n_mixed = sum(1 for h in hits if h.get("quirk_index") is None)
    t_vals = [h["t_ns"] for h in hits if "t_ns" in h]

    hit_mult_pass = False
    winner_layer_counts = {}
    if sec3c_winner is not None:
        hit_mult_pass = check_hit_multiplicity(sec3c_winner["layers"])
        winner_layer_counts = dict(Counter(sec3c_winner["layers"]))

    return {
        "status": "ok", "n_hits": n_hits, "n_candidates": len(candidates),
        "passes": winner is not None,
        "ds": winner["fit"]["delta_s"] if winner else np.nan,
        "dw": winner["fit"]["delta_w"] if winner else np.nan,
        "sec3c_plane_found": sec3c_winner is not None,
        "sec3c_ds": sec3c_winner["fit"]["delta_s"] if sec3c_winner else np.nan,
        "sec3c_dw": sec3c_winner["fit"]["delta_w"] if sec3c_winner else np.nan,
        "sec3c_n_layers": len(set(sec3c_winner["layers"])) if sec3c_winner else np.nan,
        "conv_r_cm": np.hypot(conv_point[0], conv_point[1]),
        # --- new v4 fields ---
        "hit_multiplicity_pass": hit_mult_pass,
        "winner_layer_hit_counts": json.dumps(winner_layer_counts),
        "n_electron_hits_premerge": n_electron,
        "n_positron_hits_premerge": n_positron,
        "n_mixed_hits_premerge": n_mixed,
        "n_hits_premerge": traj.get("n_hits_premerge"),
        "n_hits_postmerge": traj.get("n_hits_postmerge"),
        "t_ns_min": float(np.min(t_vals)) if t_vals else np.nan,
        "t_ns_max": float(np.max(t_vals)) if t_vals else np.nan,
        "t_ns_mean": float(np.mean(t_vals)) if t_vals else np.nan,
    }


def run(n_events, out_path, checkpoint_every=200, overwrite=False):
    ckpt_path = out_path + ".checkpoint"
    done_path = out_path + ".DONE"
    if os.path.exists(done_path) and not overwrite:
        print(f"SKIP: {out_path} already complete.")
        return out_path

    photons = pd.read_csv(f"{PC_DIR}/zgamma_photons.csv")
    start_i = 0
    if os.path.exists(ckpt_path) and os.path.exists(out_path):
        with open(ckpt_path) as f:
            start_i = int(f.read().strip())
        print(f"RESUMING {out_path} from event {start_i}/{n_events}")
    else:
        if os.path.exists(out_path):
            os.remove(out_path)

    rng = np.random.default_rng(99)  # IDENTICAL seed to v3
    if start_i > 0:
        # advance rng deterministically by replaying discarded events'
        # exact same call sequence (rng is a single shared stream in the
        # original script, not per-event SeedSequence -- so resume must
        # replay, not skip)
        for i in range(start_i):
            analyze_one_event_v4(photons.iloc[i], rng)

    t0 = time.time()
    write_header = (start_i == 0)
    buf = []
    for i in range(start_i, n_events):
        res = analyze_one_event_v4(photons.iloc[i], rng)
        res["event"] = i
        res["weight_pb"] = PER_EVENT_XSEC_PB * CONVERSION_PROBABILITY
        buf.append(res)
        if len(buf) >= checkpoint_every or i == n_events - 1:
            df = pd.DataFrame(buf)
            df.to_csv(out_path, mode="a" if not write_header else "w",
                      header=write_header, index=False)
            write_header = False
            buf = []
            with open(ckpt_path, "w") as f:
                f.write(str(i + 1))
            print(f"{i+1}/{n_events} done, {time.time()-t0:.0f}s elapsed", flush=True)

    dt = time.time() - t0
    with open(done_path, "w") as f:
        f.write(f"completed {n_events} events in {dt:.1f}s at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"[{out_path}] DONE, wall time {dt:.1f}s")
    return out_path


if __name__ == "__main__":
    n_events = int(sys.argv[1]) if len(sys.argv) > 1 else 9139
    out_path = sys.argv[2] if len(sys.argv) > 2 else f"{PC_DIR}/conversion_scan_results_v4_FULL_DIAGNOSTICS.csv"
    run(n_events, out_path)
