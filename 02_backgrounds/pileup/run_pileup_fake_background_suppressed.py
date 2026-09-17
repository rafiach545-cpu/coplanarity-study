"""
Phase 5: PILEUP_FAKE_BACKGROUND driver with tracking-efficiency suppression
applied (Phases 1-4), kept STRICTLY SEPARATE from run_pileup_fake_
background.py's direct-count outputs (different module, different output
filenames, different pool file -- never overwrites any prior authoritative
output).

Reuses the UNCHANGED Sec III C / Sec IV reconstruction chain
(seeding_and_iterative_fit, select_reconstructed_plane, check_hit_
multiplicity, apply_signal_region_cuts) -- only the INPUT hit set differs
(post-suppression "unassociated" hits instead of all raw pile-up hits).
"""
import sys
import time
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from coplanarity_fit import (seeding_and_iterative_fit, vertex_relative_hits,
                              select_reconstructed_plane, check_hit_multiplicity)
from run_pileup_fake_background import (n_layers_with_hits, LAYER_NAME_TO_IDX,
                                          PRIMARY_VERTEX_CM, wilson_interval)
from pileup_hits_suppressed import build_ancestry_pool_index, sample_pileup_hits_suppressed
from tracking_efficiency import BASELINE_SELECTION
from provenance import build_provenance, write_csv_with_provenance

ANCESTRY_POOL_PATH = "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv"
DETECTOR_MODEL_VERSION = "atlas_geometry.py Sec-IIIA-barrel-8-layer (no ref[34] endcap/TRT/ECAL/Bethe-Bloch)"


def run_one_background_event_suppressed(mu, rng_pileup, rng_suppression, pool_index,
                                          selection=BASELINE_SELECTION, B_tesla=2.0):
    pu_hits, pu_stats = sample_pileup_hits_suppressed(
        pool_index, mu, rng_pileup, rng_suppression, B_tesla=B_tesla, selection=selection)

    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in pu_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], PRIMARY_VERTEX_CM)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    per_layer_counts = {k: len(v) for k, v in hits_by_layer.items()}

    candidates = seeding_and_iterative_fit(hits_by_layer)
    best_n_layers = max((n_layers_with_hits(c["layers"]) for c in candidates), default=0)

    result = {
        "n_pu_interactions": pu_stats["n_pu_interactions"],
        "n_pu_particles_propagated": pu_stats["n_pu_particles_propagated"],
        "n_pu_hits_before_suppression": pu_stats["n_pu_hits_premerge_before_suppression"],
        "n_pu_hits_after_suppression": pu_stats["n_pu_hits_premerge_after_suppression"],
        "n_tracks_primary": pu_stats["n_tracks_primary"],
        "n_tracks_primary_removed": pu_stats["n_tracks_primary_removed"],
        "n_tracks_primary_kept": pu_stats["n_tracks_primary_kept"],
        "n_tracks_secondary": pu_stats["n_tracks_secondary"],
        "n_tracks_ambiguous": pu_stats["n_tracks_ambiguous"],
        "per_layer_hit_counts": per_layer_counts,
        "n_candidates": len(candidates),
        "best_candidate_n_layers_with_hit": best_n_layers,
        "has_4_of_8_plane": best_n_layers >= 4,
        "has_8_of_8_plane": best_n_layers >= 8,
    }
    return result


def run_one_background_event_full_cutflow(mu, rng_pileup, rng_suppression, pool_index,
                                             selection=BASELINE_SELECTION, B_tesla=2.0):
    """
    ADDITIVE, non-invasive twin of run_one_background_event_suppressed(): the
    exact same detector response / suppression / ancestry / vertex-relative
    hit chain (sample_pileup_hits_suppressed, seeding_and_iterative_fit) is
    reused verbatim -- only the OUTPUT diagnostics differ, adding the Sec IIIC
    Event-Selection winner (select_reconstructed_plane) and Sec IV hit-
    multiplicity check (check_hit_multiplicity), neither of which consumes
    any RNG draw. This function does not replace or alter
    run_one_background_event_suppressed, which remains used elsewhere
    unchanged.
    """
    pu_hits, pu_stats = sample_pileup_hits_suppressed(
        pool_index, mu, rng_pileup, rng_suppression, B_tesla=B_tesla, selection=selection)

    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in pu_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], PRIMARY_VERTEX_CM)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))

    candidates = seeding_and_iterative_fit(hits_by_layer)
    best_n_layers = max((n_layers_with_hits(c["layers"]) for c in candidates), default=0)

    winner = select_reconstructed_plane(candidates)  # Sec IIIC Event Selection (Delta_w<1cm, smallest Delta_s)
    sec3c_plane_found = winner is not None
    if sec3c_plane_found:
        sec3c_ds = winner["fit"]["delta_s"]
        sec3c_dw = winner["fit"]["delta_w"]
        sec3c_n_hits = len(winner["layers"])
        sec3c_n_layers = len(set(winner["layers"]))
        hit_mult_pass = check_hit_multiplicity(winner["layers"])
        delta_s_pass_0p01 = sec3c_ds < 0.01
    else:
        sec3c_ds = np.nan
        sec3c_dw = np.nan
        sec3c_n_hits = np.nan
        sec3c_n_layers = np.nan
        hit_mult_pass = False
        delta_s_pass_0p01 = False

    final_sec_iv_pass = sec3c_plane_found and hit_mult_pass and delta_s_pass_0p01

    return {
        "n_candidates_raw": len(candidates),
        "sec3c_plane_found": sec3c_plane_found,
        "sec3c_ds": sec3c_ds,
        "sec3c_dw": sec3c_dw,
        "sec3c_n_hits": sec3c_n_hits,
        "sec3c_n_layers": sec3c_n_layers,
        "hit_multiplicity_pass": hit_mult_pass,
        "delta_s_pass_0p01": delta_s_pass_0p01,
        "final_sec_iv_pass": final_sec_iv_pass,
        "has_4_of_8_plane": best_n_layers >= 4,
        "has_8_of_8_plane": best_n_layers >= 8,
    }


def run_suppressed_background_study(mu, n_bg_events, seed=55550001, label=None,
                                      selection=BASELINE_SELECTION, overwrite=False):
    pool_index = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))
    rows = []
    t0 = time.time()
    for i in range(n_bg_events):
        ss = np.random.SeedSequence([seed, i])
        child_pileup, child_suppression = ss.spawn(2)
        rng_pileup = np.random.default_rng(child_pileup)
        rng_suppression = np.random.default_rng(child_suppression)
        rows.append(run_one_background_event_suppressed(
            mu, rng_pileup, rng_suppression, pool_index, selection=selection))
    dt = time.time() - t0

    df = pd.DataFrame(rows)
    tag = label if label is not None else f"mu{mu}_{selection}"
    out_path = (f"/home/rafia/coplanarity_study/05_coplanarity_analysis/"
                f"pileup_fake_background_suppressed_{tag}.csv")

    n = len(df)
    k_4of8 = int(df["has_4_of_8_plane"].sum())
    k_8of8 = int(df["has_8_of_8_plane"].sum())
    rate_4of8 = k_4of8 / n if n else float("nan")
    rate_8of8 = k_8of8 / n if n else float("nan")

    prov = build_provenance(
        study_type="PILEUP_FAKE_BACKGROUND", mu=mu, n_events_processed=n,
        seed=seed, rng_stream_convention="SeedSequence([seed,i]).spawn(2) -> (rng_pileup, rng_suppression) independent streams per event",
        detector_model_version=DETECTOR_MODEL_VERSION,
        pool_path=ANCESTRY_POOL_PATH,  # BUG FIX (audit, 2026-09-17): was previously defaulting to
        # provenance.POOL_PATH (the FINAL pool), which this driver does NOT sample from -- see
        # run_sweep_resumable.py's identical fix and RUN_LOG.md 2026-09-17 errata.
        extra={
            "diagnostic_only": False,
            "tracking_efficiency_selection": selection,
            "tracking_efficiency_source": "docs/reference/atl_phys_pub_2015_051/fig1b_digitized.csv (Task A digitization)",
            "suppression_mechanism": "track-level Bernoulli removal, Phase 4 (track_suppression.py) -- "
                                      "modelling assumption, not a uniquely specified paper prescription",
            "k_4of8": k_4of8, "rate_4of8": rate_4of8, "wilson_95ci_4of8": wilson_interval(k_4of8, n),
            "k_8of8": k_8of8, "rate_8of8": rate_8of8, "wilson_95ci_8of8": wilson_interval(k_8of8, n),
            "wall_time_s": dt,
        },
    )
    write_csv_with_provenance(df, out_path, prov, overwrite=overwrite)

    print(f"[SUPPRESSED mu={mu}, selection={selection}, n={n}] wall time {dt:.1f}s -> {out_path}")
    print(f"rate(>=4/8 layers) = {rate_4of8:.4g} [{k_4of8}/{n}]")
    print(f"rate(8/8 layers)   = {rate_8of8:.4g} [{k_8of8}/{n}]")
    return df, out_path


if __name__ == "__main__":
    mu = float(sys.argv[1])
    n_bg_events = int(sys.argv[2])
    selection = sys.argv[3] if len(sys.argv) > 3 else BASELINE_SELECTION
    label = sys.argv[4] if len(sys.argv) > 4 else None
    run_suppressed_background_study(mu, n_bg_events, selection=selection, label=label)
