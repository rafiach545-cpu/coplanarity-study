"""
Run the colored quirk (mQ=1800 GeV, Lambda=2 keV) sample through the FULLY
CORRECTED pipeline: charge-filtered extraction (commit ef9fe0a), transverse-
beta geometric timing + validated step-budget floor (commit e12f3a7), 25ns
fiducial timing cut (commit 4501105, mirrored here), and the vertex-relative
coplanarity correction (commit af0fca7). This is the FIRST working analysis
driver for the colored-quirk benchmark -- no such script previously existed;
the only prior colored-quirk output
(colored_quirk_1800gev_2kev_cutflow_v2_FIXED.csv) is an orphaned artifact
from before ALL of these fixes and is OBSOLETE.

Benchmark (Sec. II, Table I, Fig. 5): (3,1)_2/3, mQ=1800 GeV, Lambda=2 keV,
QCD production (p p > t1 t1~ (+j), verified directly from proc_card_mg5.dat).

Per-event electric charge comes directly from the CSV's charge1/charge2
columns (already computed via Pythia8's own particle database at extraction
time, commit ef9fe0a) -- NOT a hardcoded assumption. R-hadron charges can be
+-1 or +-2 depending on which light quark combined with the quirk; both
signs and magnitudes are used as given, per event.

Cutflow stages tracked (mirrors analyze_ew_quirk.py exactly):
  1. N_matched        -- charge-filtered pairs (125, from extract_quirk_momenta.py)
  2. N_trigger        -- pT(pair) > 200 GeV (truth-level)
  3. N_truth_fiducial -- both quirks cross all 8 layers within |eta|<1.8
                         AND the last crossing occurs within 25 ns (Sec IV,
                         post-Eq.12), timing read from PRE-merge truth
                         crossings (traj["max_hit_t_ns_premerge"]).
  4. N_seed_found     -- >=1 seeding_and_iterative_fit candidate
  5. N_signal_region  -- passes apply_signal_region_cuts on the SINGLE plane
                         selected by Sec III C's own event-selection rule,
                         hits measured relative to the TRUE vertex.
"""

import numpy as np
import pandas as pd
import sys, time
from collections import Counter
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
from trajectory_to_hits import simulate_quirk_hits
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, check_hit_multiplicity,
                              vertex_relative_hits)

MQ_GEV = 1800.0
LAMBDA_GEV = 2e-6  # 2000 eV, paper's colored-quirk benchmark for Fig. 5 / Table I
TIMING_CUT_NS = 25.0  # paper Sec IV, post-Eq.12
XSEC_MATCHED_PB = None  # NOT separately measured for this sample in this project;
                          # left unset rather than guessed. See run log.

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}


def analyze_one(row, rng):
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
    charge1 = float(row["charge1"])
    charge2 = float(row["charge2"])

    hits, traj = simulate_quirk_hits(
        p1, p2, mass_gev=MQ_GEV, Lambda_gev=LAMBDA_GEV, B_tesla=2.0,
        charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0,
    )
    n_premerge = traj["n_hits_premerge"]
    n_postmerge = traj["n_hits_postmerge"]
    max_t_ns = traj["max_hit_t_ns_premerge"]

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
        "best_candidate_n_layers_with_hit": None,
        "best_candidate_n_layers_with_2plus": None,
        "best_candidate_layer_hit_counts": None,
    }

    if not truth_fiducial:
        return result

    vertex_cm = traj["vertex_cm"]
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))

    candidates = seeding_and_iterative_fit(hits_by_layer)
    result["n_candidates"] = len(candidates)
    result["seed_found"] = len(candidates) > 0

    def record_layer_diagnostics(cand):
        counts = Counter(cand["layers"])
        result["best_candidate_n_layers_with_hit"] = sum(1 for l in range(1, 9) if counts.get(l, 0) >= 1)
        result["best_candidate_n_layers_with_2plus"] = sum(1 for l in range(1, 9) if counts.get(l, 0) >= 2)
        result["best_candidate_layer_hit_counts"] = str({l: counts.get(l, 0) for l in range(1, 9)})

    winner = apply_signal_region_cuts(candidates)
    if winner is not None:
        result["passes_signal_region"] = True
        result["ds"] = winner["fit"]["delta_s"]
        result["dw"] = winner["fit"]["delta_w"]
        result["best_candidate_passes_hit_multiplicity"] = True
        record_layer_diagnostics(winner)
    else:
        best = select_reconstructed_plane(candidates)
        if best is not None:
            result["ds"] = best["fit"]["delta_s"]
            result["dw"] = best["fit"]["delta_w"]
            result["best_candidate_passes_hit_multiplicity"] = check_hit_multiplicity(best["layers"])
            record_layer_diagnostics(best)

    return result


if __name__ == "__main__":
    df = pd.read_csv(
        "/home/rafia/coplanarity_study/01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv")
    n_matched = len(df)
    trig = df[df["pT_pair"] > 200].reset_index(drop=True)
    n_trigger = len(trig)

    print(f"N_matched (charge-filtered pairs, from extract_quirk_momenta.py): {n_matched}")
    print(f"N_trigger (pT_pair > 200 GeV, truth, exact): {n_trigger}")
    print("Matched cross-section: NOT separately measured for this sample in this project "
          "(kept unset rather than guessed).")
    print()

    rng = np.random.default_rng(4242)
    results = []
    t0 = time.time()
    for i in range(n_trigger):
        row = trig.iloc[i]
        res = analyze_one(row, rng)
        res["event"] = int(row["event"])
        results.append(res)
        print(f"{i}/{n_trigger} done (event {res['event']}), {time.time()-t0:.0f}s elapsed", flush=True)

    rdf = pd.DataFrame(results)
    out_csv = ("/home/rafia/coplanarity_study/05_coplanarity_analysis/"
               "colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv")
    rdf.to_csv(out_csv, index=False)

    n_geom_fid = int(rdf["geometric_fiducial"].sum())
    n_truth_fid = int(rdf["truth_fiducial"].sum())
    n_seed = int(rdf["seed_found"].sum())
    n_pass = int(rdf["passes_signal_region"].sum())

    print()
    print("=== CUTFLOW ===")
    print(f"N_matched         : {n_matched}")
    print(f"N_trigger         : {n_trigger}  (eff vs matched: {n_trigger/n_matched:.4f})")
    print(f"N_geometric_fiducial (16/16, before timing): {n_geom_fid}  (eff vs trigger: {n_geom_fid/n_trigger:.4f})")
    print(f"N_truth_fiducial  : {n_truth_fid}  (16/16 AND max_t<{TIMING_CUT_NS}ns)  (eff vs trigger: {n_truth_fid/n_trigger:.4f})")
    print(f"N_seed_found      : {n_seed}" + (f"  (eff vs fiducial: {n_seed/n_truth_fid:.4f})" if n_truth_fid else ""))
    print(f"N_signal_region   : {n_pass}" + (f"  (eff vs fiducial: {n_pass/n_truth_fid:.4f})" if n_truth_fid else ""))
    print()
    print(f"epsilon_trig  = N_trigger/N_matched        = {n_trigger/n_matched:.4f}")
    print(f"epsilon_fid   = N_truth_fiducial/N_trigger = {n_truth_fid/n_trigger:.4f}" if n_trigger else "n/a")
    print(f"epsilon_reco  = N_signal_region/N_truth_fiducial = "
          f"{(n_pass/n_truth_fid if n_truth_fid else float('nan')):.4f}")
    print()
    print("Paper Table I (mQ=1800 GeV, QCD, Lambda=2 keV): eps_trig=0.24, eps_fid=0.28, eps_reco=0.35")
    print(f"\nSaved full per-event cutflow to: {out_csv}")
