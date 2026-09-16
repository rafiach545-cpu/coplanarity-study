"""
Phase 5: ancestry- and tracking-efficiency-corrected pile-up hit sampling.
Wires together Phase 1 (ancestry_classifier), Phase 2 (the ancestry-labeled
pool), Phase 3 (tracking_efficiency), and Phase 4 (track_suppression) into a
drop-in ALTERNATIVE to pileup_hits.sample_pileup_hits() -- kept in a
SEPARATE module/function so the existing, already-validated direct-count
path (pileup_hits.py, run_pileup_fake_background.py,
run_pileup_background_all8layer_diagnostic.py) is completely unchanged and
untouched.

RNG STREAMS: THREE independent streams are used per call, spawned from one
SeedSequence: multiplicity/vertex/SCT-smearing (as before, unchanged
convention), and a NEW, separate suppression-decision stream (Phase 4's
requirement). Turning suppression on/off can never perturb the other draws.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from pileup_hits import pileup_particle_hits, BEAMSPOT_SIGMA_Z_CM
from ancestry_classifier import classify_particle
from track_suppression import suppress_tracks
from tracking_efficiency import BASELINE_SELECTION


def build_ancestry_pool_index(ancestry_pool_df):
    """
    Like pileup_hits.build_pool_index, but also carries the ancestry_label
    column (Phase 1/2) per particle, keyed by event.
    """
    index = {}
    for ev_id, g in ancestry_pool_df.groupby("event", sort=False):
        index[ev_id] = (
            g["px"].to_numpy(), g["py"].to_numpy(), g["pz"].to_numpy(),
            g["m"].to_numpy(), g["charge"].to_numpy(),
            g["ancestry_label"].to_numpy(),
        )
    return index


def sample_pileup_hits_suppressed(ancestry_pool_index, mu, rng_pileup, rng_suppression,
                                    B_tesla=2.0, selection=BASELINE_SELECTION):
    """
    Same sampling procedure as pileup_hits.sample_pileup_hits() (Poisson(mu)
    interactions, with replacement, independent per-interaction 45mm-Gaussian
    z0 vertex -- UNCHANGED), but additionally:
      1. groups all raw hits by their originating truth particle,
      2. looks up each particle's Phase-1 ancestry label and truth pT,
      3. applies Phase 4's track-level Bernoulli suppression (using
         rng_suppression, independent of rng_pileup) to get the final
         "unassociated" hit pool.

    Returns (unassociated_hits, stats) -- stats includes both the original
    sampling diagnostics AND the suppression breakdown from
    track_suppression.suppress_tracks().
    """
    n_pu = rng_pileup.poisson(mu)
    pool_event_ids = np.fromiter(ancestry_pool_index.keys(), dtype=np.int64)

    raw_hits_by_particle = {}
    particle_kinematics = {}
    particle_labels = {}
    sampled_event_ids = []
    n_particles_total = 0

    if n_pu > 0 and len(pool_event_ids) > 0:
        chosen = rng_pileup.choice(pool_event_ids, size=n_pu, replace=True)
        sampled_event_ids = [int(e) for e in chosen]
        for pu_idx, ev_id in enumerate(chosen):
            z0_cm = rng_pileup.normal(0.0, BEAMSPOT_SIGMA_Z_CM)
            vertex_cm = np.array([0.0, 0.0, z0_cm])
            px_arr, py_arr, pz_arr, m_arr, q_arr, label_arr = ancestry_pool_index[ev_id]
            n_particles_total += len(px_arr)
            for j in range(len(px_arr)):
                tag = f"pu{pu_idx}_ev{ev_id}_p{j}"
                hits = pileup_particle_hits(
                    px_arr[j], py_arr[j], pz_arr[j], m_arr[j], q_arr[j],
                    vertex_cm, tag, rng_pileup, B_tesla=B_tesla,
                )
                if hits:  # only tracks with >=1 surviving hit matter downstream
                    raw_hits_by_particle[tag] = hits
                    particle_kinematics[tag] = float(np.hypot(px_arr[j], py_arr[j]))
                    particle_labels[tag] = str(label_arr[j])

    unassociated_hits, suppression_stats = suppress_tracks(
        raw_hits_by_particle, particle_kinematics, particle_labels,
        rng_suppression, selection=selection,
    )

    stats = {
        "n_pu_interactions": int(n_pu),
        "sampled_pool_event_ids": sampled_event_ids,
        "n_pu_particles_propagated": n_particles_total,
        "n_pu_hits_premerge_before_suppression": sum(len(h) for h in raw_hits_by_particle.values()),
        "n_pu_hits_premerge_after_suppression": len(unassociated_hits),
        "selection": selection,
        **suppression_stats,
    }
    return unassociated_hits, stats
