"""
Phase 4: track-level Bernoulli removal, per explicit user decision (Task C).

MODELLING ASSUMPTION, NOT A UNIQUELY SPECIFIED PAPER PRESCRIPTION (neither
the quirk paper nor ref[33] states this mechanism -- see the Sec IV / ref[33]
audit reports). Mechanism, as decided:
  - One independent Bernoulli draw per ref[33]-PRIMARY truth particle
    (secondaries are never drawn on -- see module docstring below and the
    Task B/C audit: exclusion from ref[33]'s efficiency DENOMINATOR does
    NOT mean secondary hits vanish from the simulation; they are simply
    never subject to this removal step and their hits are always kept as
    part of the "unassociated" pool, same as an ordinary failed-track
    primary).
  - draw < ε_track(pT, selection): track "reconstructed" -> ALL of its
    correlated hits are REMOVED from the unassociated-hit pool (it was
    successfully associated to a track, so it stops being "unassociated").
  - draw >= ε_track(pT, selection): track "failed" -> ALL of its hits are
    RETAINED (this is exactly ref[33]'s own definition of the background
    source: "unassociated hits, which predominantly come from pile-up
    tracks for which the track reconstruction failed").
  - Hit-level correlation is preserved BY CONSTRUCTION: the draw is made
    once per TRACK (i.e. per truth particle), and its outcome is applied to
    every hit that particle produced -- never an independent per-hit draw
    (which would be physically wrong, since a single track's hits are not
    independent samples).
  - A COMPLETELY INDEPENDENT, DETERMINISTIC RNG stream is used for this
    decision, separate from both the pile-up-multiplicity/vertex stream and
    the SCT-smearing stream already in use elsewhere in this pipeline (see
    pileup_hits.py's rng_pileup / analyze_ew_signal_with_pileup.py's
    rng_hard/rng_pileup split) -- spawned via a third SeedSequence child, so
    turning this suppression on/off never perturbs any other draw.
"""
import numpy as np
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from tracking_efficiency import track_efficiency, BASELINE_SELECTION


def suppress_tracks(raw_hits_by_particle, particle_kinematics, particle_labels,
                     rng_suppression, selection=BASELINE_SELECTION):
    """
    raw_hits_by_particle: dict {particle_tag: [hit_dict, ...]} -- ALL raw
      (pre-merge) hits produced by that one truth particle (same particle_tag
      convention as pileup_hits.py's pileup_particle_hits: e.g. "pu3_ev central117_p42").
    particle_kinematics: dict {particle_tag: pT_gev} -- truth pT of that particle.
    particle_labels: dict {particle_tag: 'primary'|'secondary'|'ambiguous'}
      from ancestry_classifier.classify_particle.
    rng_suppression: an RNG stream INDEPENDENT of any other draw in the
      pipeline (caller's responsibility -- see module docstring).
    selection: "Loose" (baseline) or "TightPrimary" (systematic variant).

    Returns (unassociated_hits, stats):
      unassociated_hits: flat list of hit dicts that remain in the
        "unassociated" background pool after suppression.
      stats: per-particle-class hit/track counts for diagnostics.
    """
    unassociated_hits = []
    stats = {
        "n_tracks_primary": 0, "n_tracks_primary_removed": 0, "n_tracks_primary_kept": 0,
        "n_tracks_secondary": 0, "n_tracks_ambiguous": 0,
        "n_hits_removed": 0, "n_hits_kept_primary_failed": 0,
        "n_hits_kept_secondary": 0, "n_hits_kept_ambiguous": 0,
    }

    for tag, hits in raw_hits_by_particle.items():
        label = particle_labels.get(tag, "ambiguous")
        if label == "secondary":
            stats["n_tracks_secondary"] += 1
            stats["n_hits_kept_secondary"] += len(hits)
            unassociated_hits.extend(hits)
            continue
        if label == "ambiguous":
            # Conservative default for the (empirically unobserved) ambiguous
            # class: treat like secondary -- never subject to removal, since
            # ref[33]'s own denominator is restricted to PRIMARY particles
            # and an unresolved classification should not be guessed into
            # either removal or an efficiency draw it was never verified for.
            stats["n_tracks_ambiguous"] += 1
            stats["n_hits_kept_ambiguous"] += len(hits)
            unassociated_hits.extend(hits)
            continue

        # label == "primary"
        stats["n_tracks_primary"] += 1
        pt = particle_kinematics.get(tag, 0.0)
        eff = track_efficiency(pt, selection=selection)
        draw = rng_suppression.uniform(0.0, 1.0)
        if draw < eff:
            stats["n_tracks_primary_removed"] += 1
            stats["n_hits_removed"] += len(hits)
            # hits NOT added to unassociated_hits -- successfully "reconstructed"
        else:
            stats["n_tracks_primary_kept"] += 1
            stats["n_hits_kept_primary_failed"] += len(hits)
            unassociated_hits.extend(hits)

    return unassociated_hits, stats
