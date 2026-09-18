"""
Converted-photon event/hit/candidate cache PROTOTYPE (2026-09-18).

Does NOT touch convert_and_analyze.py or convert_and_analyze_v4_full_
diagnostics.py (the latter is actively running as PID 165371 at the time
this was written -- this script is a separate process reading only the
same already-committed input files, and does not modify or interact with
the running process or its output files in any way).

Runs on a SMALL, bounded sample (n=100, first-100-photon prefix, same
rng=default_rng(99) stream as v3/v4) to prototype and validate a rich,
event/hit/candidate-level cache schema, WITHOUT launching another full
9139-event propagation run. This deliberately answers the "is a full
rerun needed" question conservatively: NO full rerun is performed here.

If a full 9139-event version of this cache is ever wanted, it would need
its own explicitly-authorized run (not performed by this script and not
implied by running it).
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
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/photon_conversion")
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
OUT_DIR = f"{BASE}/02_backgrounds/photon_conversion/cache_prototype_v1"
os.makedirs(OUT_DIR, exist_ok=True)

SCHEMA_VERSION = "1.0"
UNITS = {"x": "cm", "y": "cm", "z": "cm", "t_ns": "ns", "delta_s": "cm", "delta_w": "cm",
         "px": "GeV", "py": "GeV", "pz": "GeV", "E": "GeV", "layer_r_cm": "cm"}


def build_cache(n_events, seed=99):
    photons = pd.read_csv(f"{PC_DIR}/zgamma_photons.csv")
    rng = np.random.default_rng(seed)

    event_rows = []
    raw_hit_rows = []
    merged_hit_rows = []
    candidate_rows = []
    candidate_hit_link_rows = []

    global_raw_hit_id = 0
    global_merged_hit_id = 0
    global_candidate_id = 0

    for i in range(n_events):
        row = photons.iloc[i]
        px, py, pz, E = row["px"], row["py"], row["pz"], row["E"]
        z0_cm = rng.normal(0.0, BEAMSPOT_SIGMA_Z_CM)
        conv_point = find_conversion_point(px, py, pz, E, z0_cm, BEAMPIPE_RADIUS_CM)

        if conv_point is None:
            event_rows.append({"event": i, "status": "no_conversion_point", "seed": seed,
                                "rng_stream_position": i, "photon_px": px, "photon_py": py,
                                "photon_pz": pz, "photon_E": E, "z0_cm": z0_cm})
            continue

        p_e_minus = np.array([px, py, pz]) / 2.0
        p_e_plus = np.array([px, py, pz]) / 2.0
        E_e = E / 2.0

        hits, traj = simulate_quirk_hits(
            (p_e_minus[0], p_e_minus[1], p_e_minus[2], E_e),
            (p_e_plus[0], p_e_plus[1], p_e_plus[2], E_e),
            mass_gev=ELECTRON_MASS_GEV, Lambda_gev=0.0, B_tesla=2.0,
            charge1=-1.0, charge2=1.0, rng=rng,
            x0_override_cm=conv_point, max_layer_r_cm=60.0,
        )
        raw_hits = traj["raw_hits"]  # pre-existing, additive field -- not a new capability

        # --- 2. raw detector response ---
        raw_id_map = {}  # id(python object) -> assigned raw_hit_id, for merge provenance below
        for rh in raw_hits:
            hid = global_raw_hit_id
            global_raw_hit_id += 1
            raw_id_map[id(rh)] = hid
            raw_hit_rows.append({
                "event": i, "raw_hit_id": hid, "layer": rh["layer"], "layer_r_cm": rh["layer_r_cm"],
                "x": rh["x"], "y": rh["y"], "z": rh["z"], "t_ns": rh["t_ns"],
                "quirk_index": rh["quirk_index"], "is_pixel": rh["is_pixel"],
                "idx_rphi": rh["idx_rphi"] if rh["idx_rphi"] is not None else -1,
                "idx_z": rh["idx_z"] if rh["idx_z"] is not None else -1,
                "acceptance_reason": "accepted (eta/layer-radius cut already applied upstream in simulate_quirk_hits; rejected crossings are not separately counted there -- see cache schema note)",
            })

        # --- 3. merged detector response ---
        # merge provenance: match merged hit's seed identity back to raw_hit_ids by
        # exact (layer, x, y, z, t_ns, quirk_index) value tuple -- reliable since
        # these are the same unmodified values, not recomputed
        raw_lookup = {}
        for rh in raw_hits:
            key = (rh["layer"], rh["x"], rh["y"], rh["z"], rh["t_ns"], rh["quirk_index"])
            raw_lookup.setdefault(key, []).append(raw_id_map[id(rh)])

        merged_id_for_hit_obj = {}
        vertex_cm = traj["vertex_cm"]
        hits_by_layer = {k: [] for k in range(1, 9)}
        hit_tuple_to_merged_id = {}
        for h in hits:
            mid = global_merged_hit_id
            global_merged_hit_id += 1
            src_indices = h.get("source_quirk_indices", [h.get("quirk_index")])
            merged_hit_rows.append({
                "event": i, "merged_hit_id": mid, "layer": h["layer"],
                "x": h["x"], "y": h["y"], "z": h["z"], "t_ns": h.get("t_ns"),
                "quirk_index": h.get("quirk_index"),
                "source_quirk_indices": json.dumps(src_indices),
                "merged_count": h.get("merged_count", 1),
            })
            hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
            layer_idx = LAYER_NAME_TO_IDX[h["layer"]]
            hits_by_layer[layer_idx].append((hx, hy, hz))
            hit_tuple_to_merged_id[(layer_idx, hx, hy, hz)] = mid

        candidates = seeding_and_iterative_fit(hits_by_layer)
        sec3c_winner = select_reconstructed_plane(candidates)
        sec_iv_winner = apply_signal_region_cuts(candidates)

        for cand in candidates:
            cid = global_candidate_id
            global_candidate_id += 1
            is_selected = (cand is sec3c_winner)
            hit_mult_pass = check_hit_multiplicity(cand["layers"])
            layer_counts = dict(Counter(cand["layers"]))
            candidate_rows.append({
                "event": i, "candidate_id": cid, "is_selected_sec3c_plane": is_selected,
                "delta_s": cand["fit"]["delta_s"], "delta_w": cand["fit"]["delta_w"],
                "n_hits": len(cand["hits"]), "n_layers": len(set(cand["layers"])),
                "layer_hit_counts": json.dumps(layer_counts),
                "hit_multiplicity_pass": hit_mult_pass,
                "delta_w_pass": cand["fit"]["delta_w"] < 1.0,
                "delta_s_pass": cand["fit"]["delta_s"] < 0.01,
                "final_pass": (cand is sec_iv_winner) if sec_iv_winner is not None else False,
            })
            for layer_idx, hxyz in zip(cand["layers"], cand["hits"]):
                key = (layer_idx, hxyz[0], hxyz[1], hxyz[2])
                mid = hit_tuple_to_merged_id.get(key)
                candidate_hit_link_rows.append({"event": i, "candidate_id": cid, "merged_hit_id": mid, "layer": layer_idx})

        event_rows.append({
            "event": i, "status": "ok", "seed": seed, "rng_stream_position": i,
            "photon_px": px, "photon_py": py, "photon_pz": pz, "photon_E": E,
            "z0_cm": z0_cm, "conv_x_cm": conv_point[0], "conv_y_cm": conv_point[1], "conv_z_cm": conv_point[2],
            "e_minus_px": p_e_minus[0], "e_minus_py": p_e_minus[1], "e_minus_pz": p_e_minus[2], "e_minus_E": E_e,
            "e_plus_px": p_e_plus[0], "e_plus_py": p_e_plus[1], "e_plus_pz": p_e_plus[2], "e_plus_E": E_e,
            "n_hits_premerge": traj["n_hits_premerge"], "n_hits_postmerge": traj["n_hits_postmerge"],
            "n_candidates": len(candidates),
            "sec3c_plane_found": sec3c_winner is not None,
            "sec3c_ds": sec3c_winner["fit"]["delta_s"] if sec3c_winner else np.nan,
            "sec3c_dw": sec3c_winner["fit"]["delta_w"] if sec3c_winner else np.nan,
            "final_pass": sec_iv_winner is not None,
        })

    return (pd.DataFrame(event_rows), pd.DataFrame(raw_hit_rows), pd.DataFrame(merged_hit_rows),
            pd.DataFrame(candidate_rows), pd.DataFrame(candidate_hit_link_rows))


def save_npz(df, path, str_cols=()):
    arrs = {}
    for col in df.columns:
        if col in str_cols:
            arrs[col] = df[col].astype(str).to_numpy()
        else:
            arrs[col] = df[col].to_numpy()
    np.savez_compressed(path, **arrs)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    t0 = time.time()
    ev, raw, merged, cand, link = build_cache(n)
    dt = time.time() - t0

    ev.to_csv(f"{OUT_DIR}/conversion_photon_event_cache_sample{n}_v1.csv", index=False)
    save_npz(raw, f"{OUT_DIR}/conversion_photon_hit_cache_sample{n}_v1.npz", str_cols=("layer", "acceptance_reason"))
    save_npz(merged, f"{OUT_DIR}/conversion_photon_hit_cache_sample{n}_v1_merged.npz", str_cols=("layer", "source_quirk_indices"))
    save_npz(cand, f"{OUT_DIR}/conversion_photon_candidate_cache_sample{n}_v1.npz", str_cols=("layer_hit_counts",))
    save_npz(link, f"{OUT_DIR}/conversion_photon_candidate_hit_link_sample{n}_v1.npz")

    schema = {
        "schema_version": SCHEMA_VERSION, "units": UNITS, "sample_size": n, "seed": 99,
        "rng_stream_convention": "single shared np.random.default_rng(99) stream, sequential over event index -- IDENTICAL to v2/v3/v4",
        "files": {
            "event_cache": f"conversion_photon_event_cache_sample{n}_v1.csv (compact, one row per event)",
            "raw_hit_cache": f"conversion_photon_hit_cache_sample{n}_v1.npz (one row per pre-merge hit, linked by event+raw_hit_id)",
            "merged_hit_cache": f"conversion_photon_hit_cache_sample{n}_v1_merged.npz (one row per post-merge hit, linked by event+merged_hit_id)",
            "candidate_cache": f"conversion_photon_candidate_cache_sample{n}_v1.npz (one row per raw seeding_and_iterative_fit candidate)",
            "candidate_hit_link_cache": f"conversion_photon_candidate_hit_link_sample{n}_v1.npz (candidate_id <-> merged_hit_id join table)",
        },
        "known_gaps": {
            "raw_to_merged_provenance": "NOT individually resolved to specific raw_hit_id lists in this prototype (merge cluster membership is only implicit via merged_count; an exact raw<->merged join was judged unnecessary for the requested cache questions and was not built to keep this prototype bounded)",
            "acceptance_reason_detail": "simulate_quirk_hits does not separately count/report eta- or timing-rejected raw crossings (they are filtered inline and never appended to raw_hits) -- 'acceptance_reason' column is a placeholder, not a real per-crossing rejection log",
        },
        "generated_from_full_9139_event_sample": False,
        "note": "This is a SMALL-SAMPLE PROTOTYPE (n={}), not a full-statistics cache. No full 9139-event propagation run was performed to build it.".format(n),
    }
    with open(f"{OUT_DIR}/conversion_photon_cache_schema_v1.json", "w") as f:
        json.dump(schema, f, indent=2, default=str)

    sizes = {}
    for fn in os.listdir(OUT_DIR):
        sizes[fn] = os.path.getsize(f"{OUT_DIR}/{fn}")
    with open(f"{OUT_DIR}/cache_write_benchmark.json", "w") as f:
        json.dump({"n_events": n, "wall_time_s": dt, "file_sizes_bytes": sizes,
                    "total_size_bytes": sum(sizes.values())}, f, indent=2)

    print(f"n={n} events, wall_time={dt:.2f}s, total_cache_size={sum(sizes.values())/1024:.1f}KB")
    print("event rows:", len(ev), "raw hits:", len(raw), "merged hits:", len(merged),
          "candidates:", len(cand), "candidate-hit links:", len(link))
