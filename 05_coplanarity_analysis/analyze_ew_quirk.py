"""
Run the EW quirk (mQ=800 GeV, Lambda=4 keV) sample through EXACTLY the same
detector-response (trajectory_to_hits.py) and coplanarity (coplanarity_fit.py)
pipeline used for the colored quirk. No cuts or reconstruction logic changed.

Cross-section (0.0002337 pb, matched, from MadGraph/Pythia8 -- THIS run's own
result, NOT a value the paper quotes) is reported separately and NEVER
folded into any efficiency number here.

Cutflow stages tracked:
  1. N_matched        -- events surviving MLM matching (511, from MadGraph)
  2. N_trigger        -- pT(pair) > 200 GeV, from truth-level 4-momenta
                         (exact GIVEN the extracted momenta/pdg assignment
                         are themselves correct -- see extract_ew_quirk_
                         momenta.py's own verification of that).
  3. N_truth_fiducial -- both quirks cross all 8 layers within |eta|<1.8
                         AND the last crossing occurs within 25 ns (paper
                         Sec IV, immediately after Eq. 12: "The fiducial
                         efficiency ... We also include a 25 ns timing cut,
                         which causes a slight drop in eps_fid for heavier
                         quirks"). Eligibility for a hit is decided on the
                         TRUE crossing's eta, before any smearing is
                         applied, and timing is read from the PRE-merge
                         truth crossings (traj["max_hit_t_ns_premerge"]),
                         not from merged/post-detector-response hits -- so
                         this is a genuine truth-level fiducial count.
  4. N_seed_found     -- >=1 seeding_and_iterative_fit candidate
  5. N_signal_region  -- passes apply_signal_region_cuts (Delta_s<0.01cm,
                         Delta_w<1.0cm, per-layer hit-multiplicity cut)
"""

import numpy as np
import pandas as pd
import sys, time
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
from trajectory_to_hits import simulate_quirk_hits
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, check_hit_multiplicity, fit_plane)

MQ_GEV = 800.0
LAMBDA_GEV = 4e-6  # 4000 eV, paper's EW benchmark for Fig. 5
TIMING_CUT_NS = 25.0  # paper Sec IV, post-Eq.12: "25 ns timing cut" in eps_fid

# Charge (in units of e) per PDG code, from THIS sample's own UFO model
# param_card.dat: "BLOCK QNUMBERS 9000011 # qe- / 1 -3 # 3 times electric
# charge" -> 9000011 ("qe-") has charge -1, so its antiparticle -9000011
# ("qe+") has charge +1. An earlier version of this file hardcoded
# CHARGE1,CHARGE2 = -1.0,+1.0 unconditionally for (particle1,particle2) --
# but every row's (pdg1,pdg2) is (-9000011,+9000011) (verified: 511/511),
# i.e. particle 1 is qe+ (should be +1) and particle 2 is qe- (should be
# -1) -- EXACTLY BACKWARDS from what was hardcoded. This bent every EW
# quirk's trajectory in the wrong direction under the Lorentz force for the
# entire lifetime of this pipeline. Fixed by deriving charge from the
# actual per-row PDG rather than assuming a fixed column order.
PDG_TO_CHARGE = {9000011: -1.0, -9000011: +1.0}
XSEC_MATCHED_PB = 0.0002337  # kept SEPARATE from all efficiency numbers below

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}


def analyze_one(row, rng):
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])

    charge1 = PDG_TO_CHARGE[int(row["pdg1"])]
    charge2 = PDG_TO_CHARGE[int(row["pdg2"])]

    hits, traj = simulate_quirk_hits(
        p1, p2, mass_gev=MQ_GEV, Lambda_gev=LAMBDA_GEV, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0,
    )
    n_premerge = traj["n_hits_premerge"]   # truth-level fiducial hit count
    n_postmerge = traj["n_hits_postmerge"]  # detector-level, post-merge
    max_t_ns = traj["max_hit_t_ns_premerge"]  # truth-level, pre-merge (see module docstring)

    geometric_fiducial = (n_premerge == 16)
    timing_ok = (not np.isnan(max_t_ns)) and (max_t_ns < TIMING_CUT_NS)
    truth_fiducial = geometric_fiducial and timing_ok

    result = {
        "n_hits_premerge": n_premerge, "n_hits_postmerge": n_postmerge,
        "geometric_fiducial": geometric_fiducial, "timing_ok": timing_ok,
        "truth_fiducial": truth_fiducial, "max_hit_t_ns": max_t_ns,
        "n_candidates": 0, "seed_found": False,
        "passes_signal_region": False, "ds": np.nan, "dw": np.nan,
        "best_candidate_passes_hit_multiplicity": None,
        "n_layers_hit": len(set(h["layer"] for h in hits)),
    }

    if not truth_fiducial:
        return result  # matches paper's fid/reco factorization: reco only
                        # evaluated conditional on fiducial passing

    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in hits:
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((h["x"], h["y"], h["z"]))

    candidates = seeding_and_iterative_fit(hits_by_layer)
    result["n_candidates"] = len(candidates)
    result["seed_found"] = len(candidates) > 0

    winner = apply_signal_region_cuts(candidates)
    if winner is not None:
        result["passes_signal_region"] = True
        result["ds"] = winner["fit"]["delta_s"]
        result["dw"] = winner["fit"]["delta_w"]
        result["best_candidate_passes_hit_multiplicity"] = True
    else:
        # Sec III C's own reconstructed plane (Delta_w<1cm, smallest Delta_s)
        # even when it fails the Sec IV cuts, for the distribution plots
        # (Fig.5 shows this quantity for ALL events "before the final
        # selection cut" -- NOT an unfiltered global-min-Delta_s candidate,
        # which need not be the plane the paper's algorithm ever selects).
        #
        # NOTE: this candidate is NOT guaranteed to satisfy the per-layer
        # hit-multiplicity cut (Sec IV cut 2) -- Fig. 5's own text only says
        # the plot is "before the final selection cut" on Delta_s/Delta_w
        # (cut 3) specifically; it does not settle whether the plotted
        # signal curve also requires full hit multiplicity (cut 2). Rather
        # than assume either reading, the multiplicity check is recorded
        # separately here so it can be examined/filtered on independently
        # instead of being silently folded into ds/dw.
        best = select_reconstructed_plane(candidates)
        if best is not None:
            result["ds"] = best["fit"]["delta_s"]
            result["dw"] = best["fit"]["delta_w"]
            result["best_candidate_passes_hit_multiplicity"] = check_hit_multiplicity(best["layers"])

    return result


if __name__ == "__main__":
    df = pd.read_csv(
        "/home/rafia/coplanarity_study/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv")
    n_matched = len(df)
    trig = df[df["pT_pair"] > 200].reset_index(drop=True)
    n_trigger = len(trig)

    print(f"N_matched (MLM-matching-surviving, from MadGraph): {n_matched}")
    print(f"N_trigger (pT_pair > 200 GeV, truth, exact): {n_trigger}")
    print(f"Matched cross-section (kept separate from efficiency): {XSEC_MATCHED_PB} pb")
    print()

    rng = np.random.default_rng(4242)
    results = []
    t0 = time.time()
    for i in range(n_trigger):
        row = trig.iloc[i]
        res = analyze_one(row, rng)
        # Preserve the ORIGINAL HepMC-derived event id (the CSV's own
        # "event" column) for traceability -- an earlier version overwrote
        # this with `i`, the row position within the trigger-filtered,
        # index-reset dataframe, which is not the same number and breaks
        # cross-referencing back to the raw sample / HepMC file.
        res["event"] = int(row["event"])
        results.append(res)
        if i % 10 == 0:
            print(f"{i}/{n_trigger} done, {time.time()-t0:.0f}s elapsed", flush=True)

    rdf = pd.DataFrame(results)
    # New versioned filename -- this run includes the charge-sign fix and
    # the 25ns timing cut, both of which change results relative to the
    # previously saved ew_quirk_800gev_4kev_cutflow.csv; that file is left
    # untouched rather than overwritten.
    out_csv = ("/home/rafia/coplanarity_study/05_coplanarity_analysis/"
               "ew_quirk_800gev_4kev_cutflow_v2_CHARGE_TIMING_FIXED.csv")
    rdf.to_csv(out_csv, index=False)

    n_geom_fid = int(rdf["geometric_fiducial"].sum())
    n_truth_fid = int(rdf["truth_fiducial"].sum())
    n_seed = int(rdf["seed_found"].sum())
    n_pass = int(rdf["passes_signal_region"].sum())

    print()
    print("=== CUTFLOW ===")
    print(f"N_matched         : {n_matched}")
    print(f"N_trigger         : {n_trigger}  (eff vs matched: {n_trigger/n_matched:.4f})")
    print(f"N_geometric_fiducial (16/16 crossings, before timing cut): {n_geom_fid}  "
          f"(eff vs trigger: {n_geom_fid/n_trigger:.4f})")
    print(f"N_truth_fiducial  : {n_truth_fid}  (16/16 crossings AND max_t < {TIMING_CUT_NS} ns, "
          f"paper Sec IV post-Eq.12)  (eff vs trigger: {n_truth_fid/n_trigger:.4f})")
    print(f"N_seed_found      : {n_seed}  (eff vs fiducial: {n_seed/n_truth_fid:.4f})" if n_truth_fid else "N_seed_found: 0")
    print(f"N_signal_region   : {n_pass}  (eff vs fiducial: {n_pass/n_truth_fid:.4f})" if n_truth_fid else "N_signal_region: 0")
    print()
    print(f"epsilon_trig  = N_trigger/N_matched        = {n_trigger/n_matched:.4f}")
    print(f"epsilon_fid   = N_truth_fiducial/N_trigger = {n_truth_fid/n_trigger:.4f}")
    print(f"epsilon_reco  = N_signal_region/N_truth_fiducial = "
          f"{(n_pass/n_truth_fid if n_truth_fid else float('nan')):.4f}")
    print()

    fid = rdf[rdf["truth_fiducial"]]
    print("=== HIT COUNTS (fiducial events only) ===")
    print("n_hits_premerge (truth-level, pre-merge):")
    print(fid["n_hits_premerge"].describe())
    print("\nn_hits_postmerge (detector-level, post-merge):")
    print(fid["n_hits_postmerge"].describe())
    n_merged_away = (fid["n_hits_premerge"] != fid["n_hits_postmerge"]).sum()
    print(f"\nEvents where merging changed hit count: {n_merged_away} / {len(fid)}")

    print("\n=== n_layers_hit distribution (fiducial events) ===")
    print(fid["n_layers_hit"].value_counts().sort_index())

    print("\n=== Delta_s, Delta_w distributions (fiducial events with a candidate) ===")
    with_cand = fid[fid["n_candidates"] > 0]
    print(f"N with >=1 candidate: {len(with_cand)}")
    print(with_cand[["ds", "dw"]].describe())

    print(f"\n=== max hit timing (fiducial events -- NOW an ENFORCED cut at {TIMING_CUT_NS} ns, "
          "paper Sec IV post-Eq.12) ===")
    print(fid["max_hit_t_ns"].describe())

    print("\n=== best-candidate hit-multiplicity, for events failing signal-region cuts "
          "(Fig.5-style diagnostic; see analyze_one's docstring note) ===")
    failing_with_cand = fid[(~fid["passes_signal_region"]) & (fid["n_candidates"] > 0)]
    print(failing_with_cand["best_candidate_passes_hit_multiplicity"].value_counts(dropna=False))

    print(f"\nSaved full per-event cutflow to: {out_csv}")
