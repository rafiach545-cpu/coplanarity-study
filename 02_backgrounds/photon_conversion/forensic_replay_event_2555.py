"""
Forensic deterministic replay of EVENT 2555 ONLY (2026-09-21).

The compact overlay summary CSV (conversion_with_pileup_mu50_v1.csv) does
not store per-hit/per-candidate provenance, sampled pool-event IDs, or
which specific hits the selected plane used -- this replay recovers that
information for event 2555 alone via deterministic replay, using the
EXACT same seeds/code path as the authoritative run.

Because rng_photon is a SINGLE SEQUENTIALLY-ADVANCING stream (identical
construction to v2/v3/v4, by design -- see analyze_converted_photon_with_
pileup_v1.py's module docstring), reaching event 2555's correct rng_photon
state REQUIRES replaying the same draws for events 0..2554 first (a
consequence of the sequential-stream design, not a full rerun of the
overlay pipeline -- only the cheap photon-conversion propagation is
replayed for the discarded prefix, not pile-up/suppression/merge/
reconstruction, which are all skipped for events 0..2554).

Captures, for BOTH mu=0 (conversion-only) and mu=50 (full overlay) states:
raw conversion hits (with origin), raw pile-up hits (with ancestry
label/origin event+particle), merged hits (with provenance), all raw
candidates (not just the winner), the selected plane's exact hit
membership, and every independent cut flag.
"""
import json
import sys
import time
from collections import Counter
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/photon_conversion")
from trajectory_to_hits import simulate_quirk_hits
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, check_hit_multiplicity,
                              vertex_relative_hits)
from atlas_geometry import BEAMPIPE_RADIUS_CM, BEAMSPOT_SIGMA_Z_CM
from convert_and_analyze import find_conversion_point, ELECTRON_MASS_GEV, LAYER_NAME_TO_IDX
from pileup_hits import overlay_and_merge
from pileup_hits_suppressed import build_ancestry_pool_index, sample_pileup_hits_suppressed
from tracking_efficiency import BASELINE_SELECTION

BASE = "/home/rafia/coplanarity_study"
PC_DIR = f"{BASE}/02_backgrounds/photon_conversion"
ANCESTRY_POOL_PATH = f"{BASE}/02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv"
OUT_DIR = f"{BASE}/05_coplanarity_analysis/event_2555_forensic_v1"
MASTER_SEED = 99
PILEUP_SEED = 90210777
TARGET_EVENT = 2555

import os
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    photons = pd.read_csv(f"{PC_DIR}/zgamma_photons.csv")
    pool_index = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))
    pool_df = pd.read_csv(ANCESTRY_POOL_PATH)

    rng_photon = np.random.default_rng(MASTER_SEED)
    t0 = time.time()
    print(f"Replaying rng_photon prefix, events 0..{TARGET_EVENT-1} (discarded, photon-side only)...", flush=True)
    for i in range(TARGET_EVENT):
        row = photons.iloc[i]
        px, py, pz, E = row["px"], row["py"], row["pz"], row["E"]
        z0_cm = rng_photon.normal(0.0, BEAMSPOT_SIGMA_Z_CM)
        cp = find_conversion_point(px, py, pz, E, z0_cm, BEAMPIPE_RADIUS_CM)
        if cp is None:
            continue
        p_em = np.array([px, py, pz]) / 2.0
        p_ep = p_em.copy()
        Ee = E / 2.0
        simulate_quirk_hits((p_em[0], p_em[1], p_em[2], Ee), (p_ep[0], p_ep[1], p_ep[2], Ee),
                             mass_gev=ELECTRON_MASS_GEV, Lambda_gev=0.0, B_tesla=2.0,
                             charge1=-1.0, charge2=1.0, rng=rng_photon,
                             x0_override_cm=cp, max_layer_r_cm=60.0)
        if (i + 1) % 500 == 0:
            print(f"  prefix {i+1}/{TARGET_EVENT}, {time.time()-t0:.0f}s elapsed", flush=True)
    print(f"Prefix replay done in {time.time()-t0:.0f}s. rng_photon now at event {TARGET_EVENT} state.", flush=True)

    # --- now the REAL event 2555, fully instrumented ---
    row = photons.iloc[TARGET_EVENT]
    px, py, pz, E = row["px"], row["py"], row["pz"], row["E"]
    photon_info = {"event": TARGET_EVENT, "px": px, "py": py, "pz": pz, "E": E,
                    "pT": float(np.hypot(px, py)),
                    "eta": float(-np.log(np.tan(np.arccos(pz / np.sqrt(px**2 + py**2 + pz**2)) / 2))),
                    "phi": float(np.arctan2(py, px))}

    z0_cm = rng_photon.normal(0.0, BEAMSPOT_SIGMA_Z_CM)
    conv_point = find_conversion_point(px, py, pz, E, z0_cm, BEAMPIPE_RADIUS_CM)
    photon_info["z0_cm"] = float(z0_cm)
    photon_info["conv_point_xyz_cm"] = [float(c) for c in conv_point]

    p_e_minus = np.array([px, py, pz]) / 2.0
    p_e_plus = np.array([px, py, pz]) / 2.0
    E_e = E / 2.0
    photon_info["e_minus_p4_GeV"] = [float(p_e_minus[0]), float(p_e_minus[1]), float(p_e_minus[2]), float(E_e)]
    photon_info["e_plus_p4_GeV"] = [float(p_e_plus[0]), float(p_e_plus[1]), float(p_e_plus[2]), float(E_e)]

    _merged_ignored, traj = simulate_quirk_hits(
        (p_e_minus[0], p_e_minus[1], p_e_minus[2], E_e), (p_e_plus[0], p_e_plus[1], p_e_plus[2], E_e),
        mass_gev=ELECTRON_MASS_GEV, Lambda_gev=0.0, B_tesla=2.0, charge1=-1.0, charge2=1.0,
        rng=rng_photon, x0_override_cm=conv_point, max_layer_r_cm=60.0,
    )
    raw_conv_hits = traj["raw_hits"]
    vertex_cm = traj["vertex_cm"]

    conv_hit_rows = []
    for j, h in enumerate(raw_conv_hits):
        conv_hit_rows.append({
            "hit_id": f"conv{j}", "layer": h["layer"], "x": h["x"], "y": h["y"], "z": h["z"],
            "t_ns": h["t_ns"], "is_pixel": h["is_pixel"], "idx_rphi": h["idx_rphi"], "idx_z": h["idx_z"],
            "origin": "conversion_e-" if h["quirk_index"] == 0 else "conversion_e+",
            "quirk_index": h["quirk_index"],
        })

    # --- mu=0 state (conversion-only) ---
    hits_by_layer_mu0 = {k: [] for k in range(1, 9)}
    for h in raw_conv_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer_mu0[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    candidates_mu0 = seeding_and_iterative_fit(hits_by_layer_mu0)
    winner_mu0 = select_reconstructed_plane(candidates_mu0)
    secIV_mu0 = apply_signal_region_cuts(candidates_mu0)
    mu0_summary = {
        "n_raw_conv_hits": len(raw_conv_hits), "n_candidates": len(candidates_mu0),
        "sec3c_plane_found": winner_mu0 is not None,
        "sec3c_ds": winner_mu0["fit"]["delta_s"] if winner_mu0 else None,
        "sec3c_dw": winner_mu0["fit"]["delta_w"] if winner_mu0 else None,
        "sec3c_n_layers": len(set(winner_mu0["layers"])) if winner_mu0 else None,
        "sec3c_layer_hit_counts": dict(Counter(winner_mu0["layers"])) if winner_mu0 else None,
        "hit_multiplicity_pass": check_hit_multiplicity(winner_mu0["layers"]) if winner_mu0 else False,
        "final_sec_iv_pass": secIV_mu0 is not None,
        "per_layer_raw_hit_counts": {L: len(hits_by_layer_mu0[L]) for L in range(1, 9)},
    }

    # --- mu=50 state (full overlay) ---
    ss = np.random.SeedSequence([PILEUP_SEED, TARGET_EVENT])
    child_pileup, child_suppression = ss.spawn(2)
    rng_pileup = np.random.default_rng(child_pileup)
    rng_suppression = np.random.default_rng(child_suppression)

    # instrumented pileup sampling to recover sampled_pool_event_ids
    raw_pileup_hits, pu_stats = sample_pileup_hits_suppressed(
        pool_index, 50.0, rng_pileup, rng_suppression, B_tesla=2.0, selection=BASELINE_SELECTION)

    pileup_hit_rows = []
    for j, h in enumerate(raw_pileup_hits):
        pileup_hit_rows.append({
            "hit_id": h["quirk_index"], "layer": h["layer"], "x": h["x"], "y": h["y"], "z": h["z"],
            "t_ns": h["t_ns"], "is_pixel": h["is_pixel"], "idx_rphi": h["idx_rphi"], "idx_z": h["idx_z"],
            "origin": "pileup",
        })

    merged, mstats = overlay_and_merge(raw_conv_hits, raw_pileup_hits)
    merged_rows = []
    for j, h in enumerate(merged):
        merged_rows.append({
            "merged_hit_id": j, "layer": h["layer"], "x": h["x"], "y": h["y"], "z": h["z"],
            "merged_count": h.get("merged_count", 1),
            "source_quirk_indices": json.dumps(h.get("source_quirk_indices", [h.get("quirk_index")]), default=str),
        })

    hits_by_layer_mu50 = {k: [] for k in range(1, 9)}
    hit_tuple_to_merged = {}
    for j, h in enumerate(merged):
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        L = LAYER_NAME_TO_IDX[h["layer"]]
        hits_by_layer_mu50[L].append((hx, hy, hz))
        hit_tuple_to_merged[(L, hx, hy, hz)] = j

    candidates_mu50 = seeding_and_iterative_fit(hits_by_layer_mu50)
    winner_mu50 = select_reconstructed_plane(candidates_mu50)
    secIV_mu50 = apply_signal_region_cuts(candidates_mu50)

    selected_plane_hits = []
    if winner_mu50 is not None:
        for L, hxyz in zip(winner_mu50["layers"], winner_mu50["hits"]):
            key = (L, hxyz[0], hxyz[1], hxyz[2])
            mid = hit_tuple_to_merged.get(key)
            src = merged_rows[mid]["source_quirk_indices"] if mid is not None else None
            selected_plane_hits.append({"layer": L, "merged_hit_id": mid, "source_quirk_indices": src})

    mu50_summary = {
        "n_pu_interactions": pu_stats["n_pu_interactions"],
        "sampled_pool_event_ids": pu_stats["sampled_pool_event_ids"],
        "n_unique_pool_events_sampled": len(set(pu_stats["sampled_pool_event_ids"])),
        "n_pu_particles_propagated": pu_stats["n_pu_particles_propagated"],
        "n_tracks_primary": pu_stats["n_tracks_primary"],
        "n_tracks_primary_removed": pu_stats["n_tracks_primary_removed"],
        "n_tracks_primary_kept": pu_stats["n_tracks_primary_kept"],
        "n_tracks_secondary": pu_stats["n_tracks_secondary"],
        "n_tracks_ambiguous": pu_stats["n_tracks_ambiguous"],
        "n_raw_pileup_hits_before_suppression": pu_stats["n_pu_hits_premerge_before_suppression"],
        "n_raw_pileup_hits_after_suppression": pu_stats["n_pu_hits_premerge_after_suppression"],
        "n_raw_conv_hits": len(raw_conv_hits),
        "n_hits_combined_premerge": mstats["n_hits_premerge_combined"],
        "n_hits_combined_postmerge": mstats["n_hits_postmerge_combined"],
        "n_merged_hard_pileup_mixed": mstats["n_merged_hard_pileup_mixed"],
        "n_candidates": len(candidates_mu50),
        "sec3c_plane_found": winner_mu50 is not None,
        "sec3c_ds": winner_mu50["fit"]["delta_s"] if winner_mu50 else None,
        "sec3c_dw": winner_mu50["fit"]["delta_w"] if winner_mu50 else None,
        "sec3c_n_layers": len(set(winner_mu50["layers"])) if winner_mu50 else None,
        "sec3c_layer_hit_counts": dict(Counter(winner_mu50["layers"])) if winner_mu50 else None,
        "hit_multiplicity_pass": check_hit_multiplicity(winner_mu50["layers"]) if winner_mu50 else False,
        "final_sec_iv_pass": secIV_mu50 is not None,
        "per_layer_raw_hit_counts": {L: len(hits_by_layer_mu50[L]) for L in range(1, 9)},
        "selected_plane_hits": selected_plane_hits,
    }

    # normal vector comparison
    if winner_mu0 is not None:
        mu0_summary["normal_vector_n1"] = [float(x) for x in winner_mu0["fit"]["n1"]]
    if winner_mu50 is not None:
        mu50_summary["normal_vector_n1"] = [float(x) for x in winner_mu50["fit"]["n1"]]

    with open(f"{OUT_DIR}/event2555_photon_info.json", "w") as f:
        json.dump(photon_info, f, indent=2, default=str)
    with open(f"{OUT_DIR}/event2555_mu0_summary.json", "w") as f:
        json.dump(mu0_summary, f, indent=2, default=str)
    with open(f"{OUT_DIR}/event2555_mu50_summary.json", "w") as f:
        json.dump(mu50_summary, f, indent=2, default=str)
    pd.DataFrame(conv_hit_rows).to_csv(f"{OUT_DIR}/event2555_raw_conversion_hits.csv", index=False)
    pd.DataFrame(pileup_hit_rows).to_csv(f"{OUT_DIR}/event2555_raw_pileup_hits.csv", index=False)
    pd.DataFrame(merged_rows).to_csv(f"{OUT_DIR}/event2555_merged_hits_mu50.csv", index=False)

    print("=== mu=0 summary ===")
    print(json.dumps(mu0_summary, indent=2, default=str))
    print("=== mu=50 summary ===")
    print(json.dumps(mu50_summary, indent=2, default=str))
    print(f"\nTotal wall time: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
