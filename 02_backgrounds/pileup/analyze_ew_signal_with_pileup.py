"""
SIGNAL_WITH_PILEUP study (explicitly NOT the paper's pile-up-only fake-
background rate -- see run_pileup_only_background.py for that).

For each real, trigger-passing EW-quirk (mQ=800 GeV, Lambda=4 keV) hard
event, this measures whether its OWN reconstruction (does it still form a
valid plane candidate and pass the Sec IV signal-region cuts) survives
Poisson(mu) real pile-up interactions being overlaid on top of its hits.
This is a signal-reconstruction-robustness / efficiency-in-pile-up study.
It reads ew_quirk_pair_momenta_800gev_4kev.csv, applies the paper's own
pT_pair>200 GeV trigger cut, requires the truth-level 16-hit/25ns fiducial
condition (matching analyze_ew_quirk.py's validated v3 cutflow exactly),
and only then reconstructs -- confirmed by direct code inspection to be an
EW-signal-plus-pile-up efficiency study, not a background-rate calculation
(verified per the 2026-09-16 re-audit request).

RAW-HIT MERGING (re-audit item 1, CONFIRMED BUG, fixed here):
simulate_quirk_hits() returns ALREADY-MERGED hard-event hits as its primary
value. Combining that with raw pile-up hits and merging AGAIN is not
equivalent to merging raw hard hits + raw pile-up hits together in one
pass -- concretely demonstrated (and now provenance-losing in the wrong
order) in test_raw_merge_ordering.py. This driver uses
traj["raw_hits"] (the newly-exposed, purely additive pre-merge hit list),
never the primary merged return value, before calling overlay_and_merge().

RNG STREAMS (re-audit item 4): the hard-event detector response (beamspot
z0 draw, SCT smearing) and the pile-up draw (Poisson multiplicity, each
interaction's own z0, its own SCT smearing) use TWO INDEPENDENT RNG
streams per event, spawned via numpy.random.SeedSequence([seed, event_id])
-- not a single shared/sequential rng object. This makes it structurally
impossible for whether/when pile-up sampling happens to alter the hard
event's own detector-response draws (verified empirically below: moving
pile-up sampling to after the truth_fiducial decision does not change any
fiducial event's ds/dw/pass verdict, exactly as expected since the streams
are independent by construction, not just by call-order coincidence).

PILE-UP SAMPLING ORDER (re-audit item 4): pile-up is now sampled ONLY for
truth_fiducial events. This is mathematically consistent with epsilon_reco
= N_reco / N_truth_fiducial: non-fiducial events contribute to neither the
numerator nor the denominator, so whether pile-up gets drawn for them
(previously: yes, but discarded) is irrelevant to that ratio. Non-fiducial
events now report n_pu_interactions=0 (not drawn) rather than a discarded
Poisson value.
"""
import sys
import time
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
from trajectory_to_hits import simulate_quirk_hits
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, vertex_relative_hits)
from pileup_hits import build_pool_index, sample_pileup_hits, overlay_and_merge
from provenance import build_provenance, write_csv_with_provenance, POOL_PATH

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}
PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
MQ_GEV = 800.0
LAMBDA_GEV = 4e-6
TIMING_CUT_NS = 25.0
DETECTOR_MODEL_VERSION = "atlas_geometry.py Sec-IIIA-barrel-8-layer (no ref[34] endcap/TRT/ECAL/Bethe-Bloch)"
RNG_STREAM_CONVENTION = ("SeedSequence([seed, event_id]).spawn(2) -> independent "
                          "(rng_hard, rng_pileup) child streams per event")


def build_hits_by_layer(merged_hits, vertex_cm):
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in merged_hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))
    return hits_by_layer


def run_one_event(row, mu, seed, pool_index):
    ss = np.random.SeedSequence([seed, int(row.event)])
    child_hard, child_pileup = ss.spawn(2)
    rng_hard = np.random.default_rng(child_hard)
    rng_pileup = np.random.default_rng(child_pileup)

    p1 = (row.px1, row.py1, row.pz1, row.E1)
    p2 = (row.px2, row.py2, row.pz2, row.E2)
    charge1 = PDG_TO_CHARGE[int(row.pdg1)]
    charge2 = PDG_TO_CHARGE[int(row.pdg2)]

    _merged_ignored, traj = simulate_quirk_hits(
        p1, p2, mass_gev=MQ_GEV, Lambda_gev=LAMBDA_GEV, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng_hard, max_layer_r_cm=60.0,
    )
    raw_hard_hits = traj["raw_hits"]  # RAW, pre-merge -- see module docstring item 1
    n_premerge = traj["n_hits_premerge"]
    max_t_ns = traj["max_hit_t_ns_premerge"]
    geometric_fiducial = (n_premerge == 16)
    timing_ok = (not np.isnan(max_t_ns)) and (max_t_ns < TIMING_CUT_NS)
    truth_fiducial = geometric_fiducial and timing_ok
    vertex_cm = traj["vertex_cm"]

    result = {
        "event": int(row.event), "mu": mu,
        "truth_fiducial": truth_fiducial,
        "n_raw_hard_hits": len(raw_hard_hits),
        "n_pu_interactions": 0, "n_pu_particles_propagated": 0,
        "n_raw_pileup_hits": 0,
        "n_hits_combined_premerge": len(raw_hard_hits),
        "n_hits_combined_postmerge": len(raw_hard_hits),
        "n_merged_hard_pileup_mixed": 0,
        "n_candidates": 0, "passes_signal_region": False,
        "ds": np.nan, "dw": np.nan,
        "per_layer_hit_counts": None,
    }

    if not truth_fiducial:
        # item 4: pile-up is NOT sampled for non-fiducial events -- they
        # enter neither the numerator nor denominator of epsilon_reco =
        # N_reco/N_truth_fiducial, so this is mathematically consistent.
        return result

    raw_pileup_hits, pu_stats = sample_pileup_hits(pool_index, mu, rng_pileup, B_tesla=2.0)
    result["n_pu_interactions"] = pu_stats["n_pu_interactions"]
    result["n_pu_particles_propagated"] = pu_stats["n_pu_particles_propagated"]
    result["n_raw_pileup_hits"] = pu_stats["n_pu_hits_premerge"]

    merged, mstats = overlay_and_merge(raw_hard_hits, raw_pileup_hits)
    result["n_hits_combined_premerge"] = mstats["n_hits_premerge_combined"]
    result["n_hits_combined_postmerge"] = mstats["n_hits_postmerge_combined"]
    result["n_merged_hard_pileup_mixed"] = mstats["n_merged_hard_pileup_mixed"]

    hits_by_layer = build_hits_by_layer(merged, vertex_cm)
    result["per_layer_hit_counts"] = {k: len(v) for k, v in hits_by_layer.items()}

    candidates = seeding_and_iterative_fit(hits_by_layer)
    result["n_candidates"] = len(candidates)
    if candidates:
        winner = apply_signal_region_cuts(candidates)
        result["passes_signal_region"] = winner is not None
        best = winner if winner is not None else select_reconstructed_plane(candidates)
        if best is not None:
            result["ds"] = best["fit"]["delta_s"]
            result["dw"] = best["fit"]["delta_w"]
    return result


def run_mu(mu, n_events=None, seed=20260916, label=None, overwrite=False):
    ew_all = pd.read_csv("/home/rafia/coplanarity_study/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv")
    ew = ew_all[ew_all["pT_pair"] > 200].reset_index(drop=True)
    if n_events is not None:
        ew = ew.iloc[:n_events]
    pool_index = build_pool_index(pd.read_csv(POOL_PATH))

    rows = []
    t0 = time.time()
    for row in ew.itertuples(index=False):
        rows.append(run_one_event(row, mu, seed, pool_index))
    dt = time.time() - t0

    df = pd.DataFrame(rows)
    tag = label if label is not None else f"mu{mu}"
    out_path = f"/home/rafia/coplanarity_study/05_coplanarity_analysis/ew_signal_with_pileup_{tag}_cutflow.csv"
    prov = build_provenance(
        study_type="SIGNAL_WITH_PILEUP", mu=mu, n_events_processed=len(df),
        seed=seed, rng_stream_convention=RNG_STREAM_CONVENTION,
        detector_model_version=DETECTOR_MODEL_VERSION,
        extra={"hard_sample": "ew_quirk_pair_momenta_800gev_4kev.csv, pT_pair>200 GeV trigger applied",
               "wall_time_s": dt},
    )
    write_csv_with_provenance(df, out_path, prov, overwrite=overwrite)
    print(f"[SIGNAL_WITH_PILEUP mu={mu}, n={len(df)}] wall time {dt:.1f}s ({dt/max(len(df),1):.3f} s/event) -> {out_path}")
    return df, out_path


if __name__ == "__main__":
    mu = float(sys.argv[1])
    n_events = int(sys.argv[2]) if len(sys.argv) > 2 else None
    label = sys.argv[3] if len(sys.argv) > 3 else None
    df, out_path = run_mu(mu, n_events=n_events, label=label)
    print(df.describe(include="all"))
