"""
CONVERTED-PHOTON + PILE-UP OVERLAY (v1) -- the paper-required background.

Sec IIID: "The e+e- pair is then passed through the same detector
simulation as described for the pile-up background. We subsequently
overlay pile-up hits and pass the resulting set of hits through our
reconstruction algorithm." (DIRECT PAPER REQUIREMENT)

Event construction, exactly as required (no double merge):
  raw conversion e+/e- hits (traj["raw_hits"], pre-existing additive field)
  + raw retained pile-up hits (sample_pileup_hits_suppressed's suppressed
    "unassociated_hits" output, itself pre-merge)
  -> pileup_hits.overlay_and_merge() -- ONE combined merge pass (validated,
     unchanged code, already used by analyze_ew_signal_with_pileup.py)
  -> vertex-relative transform (conversion point as vertex)
  -> seeding_and_iterative_fit / select_reconstructed_plane /
     apply_signal_region_cuts (unchanged Sec IIIC/Sec IV code)

RNG STREAMS (Phase 4): THREE independent generator objects per run:
  - rng_photon: a SINGLE, sequentially-advancing stream
    (np.random.default_rng(99)), IDENTICAL construction to v2/v3/v4 --
    this is what makes the mu=0 regression bit-identical to v4 (mu=0 never
    draws from rng_pileup/rng_suppression beyond one deterministic
    Poisson(0)=0 call, which never touches rng_photon).
  - rng_pileup, rng_suppression: per-event SeedSequence([seed, event_i])
    children, matching the established pileup-driver convention
    (run_sec3c_fullcutflow_sweep.py, analyze_ew_signal_with_pileup.py).
Changing mu cannot perturb rng_photon's draws (different generator object,
never shared); this is what guarantees mu=0 reproduces v4 exactly.
"""
import json
import os
import sys
import time
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
from convert_and_analyze import (find_conversion_point, ELECTRON_MASS_GEV,
                                   CONVERSION_PROBABILITY, PER_EVENT_XSEC_PB,
                                   LAYER_NAME_TO_IDX)
from pileup_hits import overlay_and_merge
from pileup_hits_suppressed import build_ancestry_pool_index, sample_pileup_hits_suppressed
from tracking_efficiency import BASELINE_SELECTION
from provenance import build_provenance

BASE = "/home/rafia/coplanarity_study"
PC_DIR = f"{BASE}/02_backgrounds/photon_conversion"
ANCESTRY_POOL_PATH = f"{BASE}/02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv"
DETECTOR_MODEL_VERSION = "atlas_geometry.py Sec-IIIA-barrel-8-layer (no ref[34] endcap/TRT/ECAL/Bethe-Bloch)"
MASTER_SEED = 99  # photon stream, IDENTICAL to v2/v3/v4's rng=default_rng(99)
PILEUP_SEED = 90210777  # pileup/suppression streams, IDENTICAL convention to the pileup sweep drivers


def analyze_one_event_overlay(row, event_i, mu, rng_photon, pool_index,
                                selection=BASELINE_SELECTION, max_layer_r_cm=60.0):
    px, py, pz, E = row["px"], row["py"], row["pz"], row["E"]
    z0_cm = rng_photon.normal(0.0, BEAMSPOT_SIGMA_Z_CM)
    conv_point = find_conversion_point(px, py, pz, E, z0_cm, BEAMPIPE_RADIUS_CM)
    if conv_point is None:
        return {"status": "no_conversion_point", "passes": False}

    p_e_minus = np.array([px, py, pz]) / 2.0
    p_e_plus = np.array([px, py, pz]) / 2.0
    E_e = E / 2.0

    _merged_ignored, traj = simulate_quirk_hits(
        (p_e_minus[0], p_e_minus[1], p_e_minus[2], E_e),
        (p_e_plus[0], p_e_plus[1], p_e_plus[2], E_e),
        mass_gev=ELECTRON_MASS_GEV, Lambda_gev=0.0, B_tesla=2.0,
        charge1=-1.0, charge2=1.0, rng=rng_photon,
        x0_override_cm=conv_point, max_layer_r_cm=max_layer_r_cm,
    )
    raw_conv_hits = traj["raw_hits"]
    vertex_cm = traj["vertex_cm"]

    # independent pile-up/suppression streams, per-event, NEVER touching rng_photon
    ss = np.random.SeedSequence([PILEUP_SEED, event_i])
    child_pileup, child_suppression = ss.spawn(2)
    rng_pileup = np.random.default_rng(child_pileup)
    rng_suppression = np.random.default_rng(child_suppression)
    raw_pileup_hits, pu_stats = sample_pileup_hits_suppressed(
        pool_index, mu, rng_pileup, rng_suppression, B_tesla=2.0, selection=selection)

    merged, mstats = overlay_and_merge(raw_conv_hits, raw_pileup_hits)

    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in merged:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))

    candidates = seeding_and_iterative_fit(hits_by_layer)
    sec3c_winner = select_reconstructed_plane(candidates)
    sec_iv_winner = apply_signal_region_cuts(candidates)

    hit_mult_pass = False
    n_layers = np.nan
    ds = np.nan
    dw = np.nan
    if sec3c_winner is not None:
        hit_mult_pass = check_hit_multiplicity(sec3c_winner["layers"])
        n_layers = len(set(sec3c_winner["layers"]))
        ds = sec3c_winner["fit"]["delta_s"]
        dw = sec3c_winner["fit"]["delta_w"]

    return {
        "status": "ok", "event": event_i, "mu": mu,
        "n_raw_conv_hits": len(raw_conv_hits),
        "n_pu_interactions": pu_stats["n_pu_interactions"],
        "n_pu_particles_propagated": pu_stats["n_pu_particles_propagated"],
        "n_raw_pileup_hits_before_suppression": pu_stats["n_pu_hits_premerge_before_suppression"],
        "n_raw_pileup_hits_after_suppression": pu_stats["n_pu_hits_premerge_after_suppression"],
        "n_tracks_primary": pu_stats["n_tracks_primary"],
        "n_tracks_primary_removed": pu_stats["n_tracks_primary_removed"],
        "n_tracks_primary_kept": pu_stats["n_tracks_primary_kept"],
        "n_tracks_secondary": pu_stats["n_tracks_secondary"],
        "n_tracks_ambiguous": pu_stats["n_tracks_ambiguous"],
        "n_hits_combined_premerge": mstats["n_hits_premerge_combined"],
        "n_hits_combined_postmerge": mstats["n_hits_postmerge_combined"],
        "n_merged_hard_pileup_mixed": mstats["n_merged_hard_pileup_mixed"],
        "n_hits": len(merged),
        "n_candidates": len(candidates),
        "sec3c_plane_found": sec3c_winner is not None,
        "sec3c_ds": ds, "sec3c_dw": dw, "sec3c_n_layers": n_layers,
        "hit_multiplicity_pass": hit_mult_pass,
        "delta_s_pass_0p01": (ds < 0.01) if sec3c_winner is not None else False,
        "final_sec_iv_pass": sec_iv_winner is not None,
        "conv_r_cm": np.hypot(conv_point[0], conv_point[1]),
    }


RESULT_COLUMNS = [
    "status", "event", "mu", "n_raw_conv_hits", "n_pu_interactions",
    "n_pu_particles_propagated", "n_raw_pileup_hits_before_suppression",
    "n_raw_pileup_hits_after_suppression", "n_tracks_primary",
    "n_tracks_primary_removed", "n_tracks_primary_kept", "n_tracks_secondary",
    "n_tracks_ambiguous", "n_hits_combined_premerge", "n_hits_combined_postmerge",
    "n_merged_hard_pileup_mixed", "n_hits", "n_candidates", "sec3c_plane_found",
    "sec3c_ds", "sec3c_dw", "sec3c_n_layers", "hit_multiplicity_pass",
    "delta_s_pass_0p01", "final_sec_iv_pass", "conv_r_cm", "weight_pb",
]


def run(n_events, mu, out_path, checkpoint_every=100, overwrite=False):
    ckpt_path = out_path + ".checkpoint"
    done_path = out_path + ".DONE"
    if os.path.exists(done_path) and not overwrite:
        print(f"SKIP: {out_path} already complete.")
        return out_path

    photons = pd.read_csv(f"{PC_DIR}/zgamma_photons.csv")
    pool_index = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))

    start_i = 0
    if os.path.exists(ckpt_path) and os.path.exists(out_path):
        with open(ckpt_path) as f:
            start_i = int(f.read().strip())
        print(f"RESUMING {out_path} from event {start_i}/{n_events}")
    else:
        if os.path.exists(out_path):
            os.remove(out_path)

    rng_photon = np.random.default_rng(MASTER_SEED)
    if start_i > 0:
        # rng_photon is a single sequential stream (matches v2/v3/v4) -- resume
        # must replay the discarded prefix to stay bit-identical
        for i in range(start_i):
            analyze_one_event_overlay(photons.iloc[i], i, mu, rng_photon, pool_index)

    t0 = time.time()
    write_header = (start_i == 0)
    buf = []
    for i in range(start_i, n_events):
        res = analyze_one_event_overlay(photons.iloc[i], i, mu, rng_photon, pool_index)
        res["weight_pb"] = PER_EVENT_XSEC_PB * CONVERSION_PROBABILITY
        buf.append(res)
        if len(buf) >= checkpoint_every or i == n_events - 1:
            df = pd.DataFrame(buf, columns=RESULT_COLUMNS)
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

    prov = build_provenance(
        study_type="PILEUP_FAKE_BACKGROUND", mu=mu, n_events_processed=n_events,
        seed=PILEUP_SEED,
        rng_stream_convention="rng_photon=single sequential default_rng(99) (IDENTICAL to v2/v3/v4); "
                               "rng_pileup/rng_suppression=SeedSequence([90210777,event_i]).spawn(2), independent per event",
        detector_model_version=DETECTOR_MODEL_VERSION, pool_path=ANCESTRY_POOL_PATH,
        extra={"tracking_efficiency_selection": selection if (selection := BASELINE_SELECTION) else None,
               "checkpoint_every": checkpoint_every, "wall_time_s": dt,
               "master_photon_seed": MASTER_SEED,
               "note": "converted-photon + pile-up overlay, one combined raw+raw merge (overlay_and_merge)"},
    )
    with open(out_path + ".provenance.json", "w") as f:
        json.dump(prov, f, indent=2, default=str)

    print(f"[{out_path}] DONE, wall time {dt:.1f}s")
    return out_path


if __name__ == "__main__":
    n_events = int(sys.argv[1]) if len(sys.argv) > 1 else 9139
    mu = float(sys.argv[2]) if len(sys.argv) > 2 else 50.0
    out_path = sys.argv[3] if len(sys.argv) > 3 else f"{PC_DIR}/conversion_with_pileup_mu{int(mu)}_v1.csv"
    run(n_events, mu, out_path)
