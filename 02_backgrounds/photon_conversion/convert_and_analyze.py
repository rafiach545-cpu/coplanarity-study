"""
Stage 6b: convert each Z+gamma+jet background photon into an e+/e- pair at
the beampipe, propagate both through the same detector simulation and
coplanarity algorithm used for the quirk signal, and report the weighted
yield surviving the signal-region cuts.

Conversion procedure (paper Sec III D + user's professor's guidance):
  - Every surviving photon is converted (not a random 1% subset) -- the
    ~1% physical conversion probability is instead applied as an event
    WEIGHT at the end, which is far more statistically efficient than
    randomly rejecting ~99% of events.
  - Equal energy sharing between e+ and e- (paper's own conservative
    choice -- softer electrons bend more and fit a plane worse, so this is
    the harder-to-reject case).
  - The photon is uncharged and travels in a straight line from the
    primary vertex (itself drawn from the 45mm beamspot, same as signal)
    until it reaches the beampipe radius (2.35 cm) -- THAT point, not the
    primary vertex, is where the e+/e- pair's own trajectories begin. This
    matters because the coplanarity algorithm assumes the primary vertex
    is at the origin (paper Sec III C); a conversion point offset by
    ~2.35 cm is a real, physical effect on the fit geometry.
  - The resulting e+/e- pair has NO confining string between them (they
    are ordinary charged leptons, not a quirk pair) -- propagated with
    Lambda=0 (pure Lorentz-force curvature only) through the same 2T field
    and 8-layer detector.

v2 (2026-09-15, Stage 2 audit): hits are now measured relative to the TRUE
vertex (here, the conversion point) before the plane fit, via
coplanarity_fit.vertex_relative_hits -- matching the fix already applied to
the signal pipeline (commit af0fca7). An earlier version fed raw global
coordinates into the fit here while the signal scripts already didn't,
which was an unintended inconsistency between how signal and background
were reconstructed.
"""

import numpy as np
import pandas as pd
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
from trajectory_to_hits import simulate_quirk_hits
from coplanarity_fit import (seeding_and_iterative_fit, apply_signal_region_cuts,
                              select_reconstructed_plane, vertex_relative_hits)
from atlas_geometry import BEAMPIPE_RADIUS_CM, BEAMSPOT_SIGMA_Z_CM

ELECTRON_MASS_GEV = 0.000511
CONVERSION_PROBABILITY = 0.01  # event weight, per professor's guidance;
                                 # consistent with the paper's own implied
                                 # ~1% (10 fb / 1 pb fiducial cross sections)

# The HepMC 'weight' field MadGraph/Pythia8 writes for this unweighted LO
# sample is IDENTICAL for every one of the originally generated events, and
# equal to the TOTAL sample cross-section (0.2310512 pb over 10000 events),
# not a per-event contribution. An earlier version of this script summed
# that raw field directly over passing events, which silently overcounts by
# a factor of N_TOTAL_GENERATED (treating each sampled event as if it alone
# carried the full cross-section). The correct per-event cross-section
# weight is total_xsec / N_TOTAL_GENERATED.
N_TOTAL_GENERATED = 10000
TOTAL_XSEC_PB = 0.2310512
PER_EVENT_XSEC_PB = TOTAL_XSEC_PB / N_TOTAL_GENERATED

LAYER_NAME_TO_IDX = {'L1_IBL': 1, 'L2_PixelB0': 2, 'L3_PixelB1': 3, 'L4_PixelB2': 4,
                      'L5_SCT_B3': 5, 'L6_SCT_B4': 6, 'L7_SCT_B5': 7, 'L8_SCT_B6': 8}


def find_conversion_point(px, py, pz, E, z0_cm, beampipe_r_cm):
    """
    Photon travels in a straight line from (0,0,z0) in direction (px,py,pz)/|p|.
    Returns the 3D conversion point (cm) where the TRANSVERSE distance from
    the photon's own straight path reaches beampipe_r_cm, or None if the
    photon is too forward/central (negligible transverse momentum) to ever
    cross the barrel beampipe radius in a meaningful sense.
    """
    p_mag = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
    nx, ny, nz = px / p_mag, py / p_mag, pz / p_mag
    n_transverse = np.hypot(nx, ny)
    if n_transverse < 1e-6:
        return None  # travels along the beam axis, never reaches barrel radius
    t_conv = beampipe_r_cm / n_transverse
    return np.array([nx * t_conv, ny * t_conv, z0_cm + nz * t_conv])


def analyze_one_event(row, rng, max_layer_r_cm=60.0):
    px, py, pz, E = row["px"], row["py"], row["pz"], row["E"]
    z0_cm = rng.normal(0.0, BEAMSPOT_SIGMA_Z_CM)

    conv_point = find_conversion_point(px, py, pz, E, z0_cm, BEAMPIPE_RADIUS_CM)
    if conv_point is None:
        return {"status": "no_conversion_point", "passes": False}

    # Equal energy sharing, collinear with the parent photon (paper's
    # conservative assumption; the true QED opening angle ~m_e/E_gamma is
    # negligible at these energies).
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
    # VERTEX-RELATIVE CORRECTION (Sec III C: plane fit assumes the primary
    # vertex is at the origin) -- for this background, the relevant vertex
    # IS the conversion point (traj["vertex_cm"] == conv_point for the
    # x0_override_cm path in simulate_quirk_hits), not the hard-scatter
    # primary vertex. An earlier version of this script fed raw global hit
    # coordinates into the fit here while the signal pipeline (analyze_ew_
    # quirk.py, analyze_colored_quirk.py) already applied this correction --
    # that inconsistency is fixed here so signal and background are
    # reconstructed by the IDENTICAL algorithm, as Sec III D's own
    # description requires ("passed through the same detector simulation").
    vertex_cm = traj["vertex_cm"]
    hits_by_layer = {k: [] for k in range(1, 9)}
    for h in hits:
        hx, hy, hz = vertex_relative_hits([(h["x"], h["y"], h["z"])], vertex_cm)[0]
        hits_by_layer[LAYER_NAME_TO_IDX[h["layer"]]].append((hx, hy, hz))

    candidates = seeding_and_iterative_fit(hits_by_layer)

    # Sec III C Event Selection (Fig. 5's population), computed BEFORE and
    # INDEPENDENTLY of the stricter Sec IV cuts below. select_reconstructed_
    # plane() is a pure list operation (filter on delta_w<1cm, then min() on
    # delta_s) -- it draws no random numbers, so inserting this call cannot
    # perturb the RNG stream consumed by simulate_quirk_hits() above or any
    # downstream event's hits/results.
    sec3c_winner = select_reconstructed_plane(candidates)

    winner = apply_signal_region_cuts(candidates)

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
    }


if __name__ == "__main__":
    import time
    photons = pd.read_csv(
        "/home/rafia/coplanarity_study/02_backgrounds/photon_conversion/zgamma_photons.csv")
    print(f"Loaded {len(photons)} MET-passing, pT_gamma-passing background photons")

    n_test = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    rng = np.random.default_rng(99)
    results = []
    t0 = time.time()
    for i in range(min(n_test, len(photons))):
        row = photons.iloc[i]
        res = analyze_one_event(row, rng)
        res["event"] = i
        res["weight_pb"] = PER_EVENT_XSEC_PB * CONVERSION_PROBABILITY
        results.append(res)
        if i % 5 == 0:
            print(f"{i}/{n_test} done, {time.time()-t0:.0f}s elapsed", flush=True)

    rdf = pd.DataFrame(results)
    # v3: adds sec3c_ds/sec3c_dw/sec3c_plane_found/sec3c_n_layers columns
    # (Sec III C Event Selection, Fig. 5's population) alongside the
    # unchanged v2 columns. Same input, same seed, same event order as v2;
    # v2 file is left untouched, not overwritten.
    out_csv = ("/home/rafia/coplanarity_study/02_backgrounds/photon_conversion/"
               "conversion_scan_results_v3_SEC3C_DS_DW.csv")
    rdf.to_csv(out_csv, index=False)
    print()
    print(rdf["status"].value_counts())
    ok = rdf[rdf["status"] == "ok"]
    print(f"\nOf {len(ok)} events with a valid conversion point:")
    print(f"  n_hits distribution:\n{ok['n_hits'].describe()}")
    n_pass = int(ok["passes"].sum())
    n_tested = len(ok)
    print(f"  events passing signal region: {n_pass} / {n_tested}")

    n_sec3c = int(ok["sec3c_plane_found"].sum())
    print(f"  Sec IIIC plane-found (Fig. 5 population): {n_sec3c} / {n_tested}")
    sec3c = ok[ok["sec3c_plane_found"]]
    if n_sec3c > 0:
        for col in ("sec3c_ds", "sec3c_dw"):
            v = sec3c[col].to_numpy()
            print(f"    {col}: median={np.median(v):.5f} p16={np.percentile(v,16):.5f} "
                  f"p84={np.percentile(v,84):.5f} min={v.min():.5f} max={v.max():.5f}")
        frac_below = float((sec3c["sec3c_ds"] < 0.01).mean())
        print(f"    fraction sec3c_ds < 0.01cm: {frac_below:.4f}")

    # Cross-section for events passing the signal region, correctly
    # normalized: (fraction of the TESTED sample passing) x (fraction of
    # the full 10000-event MadGraph sample this tested sample represents,
    # i.e. how much of the true post-shower-MET-cut population, 9139/10000,
    # was actually run through the expensive detector+algorithm pipeline)
    # x (total cross-section) x (conversion probability weight).
    n_met_passing_pool = 9139  # from extract_zgamma_photons.py's true-MET cut
    eff_signal_region = n_pass / n_tested if n_tested > 0 else 0.0
    sigma_after_met = (n_met_passing_pool / N_TOTAL_GENERATED) * TOTAL_XSEC_PB
    sigma_passing_pb = eff_signal_region * sigma_after_met * CONVERSION_PROBABILITY
    print(f"\n  cross-section passing signal region: {sigma_passing_pb*1000:.6f} fb "
          f"(point estimate; 0 if n_pass=0)")

    if n_pass == 0:
        # Standard 95% CL Poisson upper limit for zero observed events in n
        # trials: ~3 events "worth" of rate, i.e. upper limit on the true
        # per-trial probability is ~3/n_tested.
        upper_limit_eff = 3.0 / n_tested if n_tested > 0 else float("nan")
        upper_limit_pb = upper_limit_eff * sigma_after_met * CONVERSION_PROBABILITY
        print(f"  0 observed in {n_tested} trials -> 95% CL upper limit on "
              f"efficiency: {upper_limit_eff:.4f}")
        print(f"  95% CL upper limit on passing cross-section: "
              f"{upper_limit_pb*1000:.6f} fb")
        print(f"  (paper's own converted-photon background, after its full "
              f"analysis chain, is likewise consistent with ~0 -- see "
              f"Sec IV: 'we suspect they can easily be removed')")

    print(f"\nSaved full per-event results to: {out_csv}")
