"""
Stage 2: convert a quirk-pair classical trajectory (Stage 1 output) into
detector hits on the 8-layer ATLAS Run-2 barrel (Stage 2 geometry).

Pipeline per event:
  1. Integrate the quirk pair trajectory (quirk_trajectory.py), starting
     both quirks at the primary vertex (z0 drawn once per event from the
     45mm beamspot, per paper's beamspot-smearing prescription).
  2. For each quirk and each of the 8 layers, find where its trajectory
     crosses that layer's cylindrical radius (linear interpolation between
     the two straddling timesteps).
  3. Apply per-layer resolution:
       - Pixel layers (L1-L4): hit position quantized to the pixel pitch
         grid in (r-phi, z) -- "use the pixel size as the effective
         resolution" (paper Sec III A).
       - SCT layers (L5-L8): Gaussian-smear (r-phi, z) with sigma = 2x the
         intrinsic accuracy (paper's conservative doubling).
  4. Merge hits landing in neighboring pixel cells (adjacent index in both
     r-phi and z pixel-index space) into a single hit at the mean position.
  5. Restrict to |eta| < 1.8 (paper's barrel fiducial range).
"""

import numpy as np
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
from quirk_trajectory import integrate_trajectory, gev_to_cm, gev_to_s
from atlas_geometry import LAYERS, FIDUCIAL_ETA_MAX, BEAMSPOT_SIGMA_Z_CM, eta_from_theta

C_LIGHT_CM_PER_NS = 29.9792458  # speed of light, cm/ns

# Minimum RK4 steps per internal oscillation period below which the
# integrated trajectory is considered under-resolved. Justified by
# validate_dt_convergence.py (03_trajectory_sim, mQ=1.8TeV/Lambda=2keV/v=0.6
# benchmark, measured 2026-09-14): relative error vs the exact Eq. 4 solution
# is already < 1e-4 down to the smallest scanned value (30 steps/period,
# 3.3e-8 rel err) and stays below 1e-4 across the entire scanned range up to
# 3000 steps/period -- RK4's 4th-order convergence (verified: ~16x error
# reduction per dt halving, exactly the theoretical rate) means this
# integrator is far more accurate than the coplanarity cuts (cm-scale) need.
# 300 is therefore a conservative (~10x) safety margin above the measured
# floor, not a marginal value -- chosen so this check essentially never
# fires for a well-resolved event, while still catching genuine gross
# under-resolution (the kind that caused the "33x too short" bug).
MIN_STEPS_PER_PERIOD = 300


def _on_shell_energy(p_xyz, mass):
    return np.sqrt(np.dot(p_xyz, p_xyz) + mass ** 2)


def check_onshell_energy(p_xyz, E_supplied, mass, label="", rel_tol=1e-6):
    """
    E=sqrt(p^2+m^2) is the on-shell relation the integrator's dynamics
    actually use internally (quirk_trajectory.velocity_from_momentum always
    recomputes E from p and mass, never uses a separately supplied E). The
    CM-frame boost used to size the integration period/timestep in this
    module, however, historically used the SUPPLIED 4-vector energy
    directly. If that supplied E is not on-shell (upstream rounding, or a
    genuinely different mass convention), the period/geometry sizing would
    be based on a different energy than what the dynamics actually use.
    Returns the on-shell energy and prints a warning (does not raise) if the
    supplied E disagrees by more than rel_tol.
    """
    E_onshell = _on_shell_energy(np.asarray(p_xyz, dtype=float), mass)
    if E_supplied is not None and E_onshell > 0:
        rel_diff = abs(E_supplied - E_onshell) / E_onshell
        if rel_diff > rel_tol:
            print(f"WARNING [check_onshell_energy{(' ' + label) if label else ''}]: "
                  f"supplied E={E_supplied:.6f} GeV vs on-shell E={E_onshell:.6f} GeV "
                  f"(rel diff {rel_diff:.2e} > tol {rel_tol:.0e}). Using on-shell E "
                  "for period/geometry sizing so it is consistent with what the "
                  "integrator's dynamics actually use.")
    return E_onshell


def find_layer_crossing(x_traj_cm, t_gev_inv, layer_r_cm):
    """
    x_traj_cm: (N,3) array, trajectory positions in cm.
    Returns (hit_xyz_cm, hit_t_ns) at the first crossing of radius
    layer_r_cm, or None if the trajectory never reaches that radius.

    ONLY THE FIRST outward crossing is retained, even though the quirks'
    oscillatory radial motion means r(t) is not monotonic and could in
    principle cross a given layer's radius more than once (out, back in,
    out again). The paper does not call for multiple crossings per layer
    (Sec III C's seeding/iterative-fit cuts operate on one hit per particle
    per layer), so this matches the paper's own treatment.

    `argmax(above)` on a boolean array returns the FIRST True index, i.e.
    the first idx with r[idx] >= layer_r_cm while r[idx-1] < layer_r_cm
    (guaranteed since all earlier entries are False) -- this is already
    exactly the genuine below-to-above crossing condition
    `r[i] < r_layer <= r[i+1]`, just indexed as (idx-1, idx) below.
    """
    r = np.hypot(x_traj_cm[:, 0], x_traj_cm[:, 1])
    above = r >= layer_r_cm
    if not np.any(above):
        return None
    idx = np.argmax(above)  # first genuine below-to-above crossing (see docstring)
    if idx == 0:
        return None  # started beyond this radius (shouldn't happen at r~0 start)
    r0, r1 = r[idx - 1], r[idx]
    if r1 == r0:
        frac = 0.0
    else:
        frac = (layer_r_cm - r0) / (r1 - r0)
    hit_xyz = x_traj_cm[idx - 1] + frac * (x_traj_cm[idx] - x_traj_cm[idx - 1])
    t0_gev_inv = t_gev_inv[idx - 1] + frac * (t_gev_inv[idx] - t_gev_inv[idx - 1])
    t_ns = gev_to_s(t0_gev_inv) * 1e9
    return hit_xyz, t_ns


def quantize_pixel(rphi_cm, z_cm, pitch_rphi_um, pitch_z_um):
    """
    MODELLING CHOICE (Sec III A says only "use the pixel size ... as the
    effective resolution," which is genuinely ambiguous between two
    different responses): this function QUANTIZES the true hit position to
    the nearest pixel-grid center (a true digital-pixel readout model, RMS
    rounding error = pitch/sqrt(12)), NOT a Gaussian smear with sigma=pitch
    (which would be a different response function with a different, larger
    tail). Kept as the baseline per instruction; documented here so this
    choice is not silently conflated with a Gaussian-resolution treatment
    (which is what the SCT branch below actually uses, at sigma = 2x
    intrinsic accuracy, per the paper's own explicit prescription for SCT).
    """
    pitch_rphi_cm = pitch_rphi_um * 1e-4
    pitch_z_cm = pitch_z_um * 1e-4
    idx_rphi = np.round(rphi_cm / pitch_rphi_cm)
    idx_z = np.round(z_cm / pitch_z_cm)
    return idx_rphi * pitch_rphi_cm, idx_z * pitch_z_cm, int(idx_rphi), int(idx_z)


def simulate_quirk_hits(p1_gev, p2_gev, mass_gev, Lambda_gev, B_tesla,
                         charge1, charge2, rng, z0_cm=None,
                         n_periods_to_integrate=40, steps_per_period=1500,
                         max_layer_r_cm=None, x0_override_cm=None,
                         n_steps_no_string=5000, smear_primary_vertex=True):
    """
    p1_gev, p2_gev: (px,py,pz,E) lab-frame 4-momenta of the two particles.
    x0_override_cm: if given, BOTH particles start at this common 3-position
      (cm) instead of the default (0,0,z0) -- used for photon-conversion
      background, where the e+/e- pair starts at the beampipe conversion
      point, not the primary vertex.
    Lambda_gev: set to 0 for ordinary (non-quirk) charged particles with no
      confining string -- e.g. the converted e+/e- pair. The oscillation-
      period formula used to size the integration timestep is undefined
      (divides by zero) when Lambda=0, since there is no oscillation; in
      that case we instead size the timestep from the geometry (flight time
      to the outer layer) since the trajectory is then just Lorentz-force
      gyration with a gyroradius vastly larger than the detector (nearly
      straight line), not a rapid oscillation needing fine resolution.
    smear_primary_vertex: if True (paper's official baseline -- Sec III A's
      45mm beamspot smearing), draw z0 from BEAMSPOT_SIGMA_Z_CM (or use the
      caller-supplied z0_cm) as before. If False, force z0=0 exactly
      (equivalent to passing z0_cm=0.0, provided as an explicit, self-
      documenting flag for validation/debugging so a caller does not have to
      remember that z0_cm=0.0 is the way to disable smearing). Only affects
      the signal-vertex path; x0_override_cm (pile-up/conversion vertex) is
      untouched by this flag, since that is a separate, already-explicit
      vertex choice.
    Returns list of hit dicts: {layer, x,y,z (cm), quirk_index}, and a traj
      dict that additionally carries dt-coarsening diagnostics (see below).
    """
    if x0_override_cm is not None:
        x0_natural_vec = np.array(x0_override_cm) / 1.973269804e-14
        x1_0 = x0_natural_vec.copy()
        x2_0 = x0_natural_vec.copy()
        vertex_cm = np.array(x0_override_cm, dtype=float)
    else:
        if not smear_primary_vertex:
            z0_cm = 0.0
        elif z0_cm is None:
            z0_cm = rng.normal(0.0, BEAMSPOT_SIGMA_Z_CM)
        z0_natural = z0_cm / 1.973269804e-14
        x1_0 = np.array([0.0, 0.0, z0_natural])
        x2_0 = np.array([0.0, 0.0, z0_natural])
        vertex_cm = np.array([0.0, 0.0, z0_cm])

    p1 = np.array(p1_gev[:3])
    p2 = np.array(p2_gev[:3])
    # Use ON-SHELL energies (E=sqrt(p^2+m^2)) for all period/geometry sizing
    # below, not the raw supplied 4-vector energies -- this is exactly what
    # the integrator's own dynamics use internally (quirk_trajectory always
    # recomputes E from p and mass), so sizing dt/t_max from anything else
    # risks a subtle mismatch if the supplied E isn't exactly on-shell.
    # check_onshell_energy prints a warning (does not raise) if the supplied
    # E disagrees meaningfully with the on-shell value.
    E1 = check_onshell_energy(p1, p1_gev[3], mass_gev, label="quirk/particle 1")
    E2 = check_onshell_energy(p2, p2_gev[3], mass_gev, label="quirk/particle 2")

    dt_diagnostics = {}

    if Lambda_gev is not None and Lambda_gev > 0:
        # Eq. 4's oscillation period is derived in the PAIR's CM frame --
        # using quirk 1's lab-frame velocity here (an earlier version of
        # this code did) is only correct for a non-boosted pair. Every real
        # MadGraph event has a boosted, asymmetric pair, so that gave a
        # wrong period estimate (hence wrong integration dt) for every real
        # event, even though the integrator itself was already validated
        # correctly against Eq.4 in the symmetric (non-boosted) test case,
        # where lab frame == CM frame by construction. Properly boost
        # quirk 1's momentum into the pair's own CM frame first.
        P_total = np.array([p1[0] + p2[0], p1[1] + p2[1], p1[2] + p2[2]])
        E_total = E1 + E2
        beta_cm_vec = P_total / E_total
        beta_cm2 = np.dot(beta_cm_vec, beta_cm_vec)
        gamma_cm = 1.0 / np.sqrt(max(1.0 - beta_cm2, 1e-15))

        if beta_cm2 > 1e-20:
            beta_hat = beta_cm_vec / np.sqrt(beta_cm2)
            p1_par = np.dot(p1, beta_hat)
            p1_perp = p1 - p1_par * beta_hat
            beta_cm_mag = np.sqrt(beta_cm2)
            p1_par_cm = gamma_cm * (p1_par - beta_cm_mag * E1)
            E1_cm = gamma_cm * (E1 - beta_cm_mag * p1_par)
            p1_cm_3vec = p1_perp + p1_par_cm * beta_hat
        else:
            E1_cm = E1
            p1_cm_3vec = p1

        v_int = np.linalg.norm(p1_cm_3vec) / E1_cm  # true CM-frame internal speed
        gamma_est = E1_cm / mass_gev                 # true CM-frame gamma
        period_est = 2.0 * v_int * gamma_est * mass_gev / (Lambda_gev ** 2)

        # BUG (found 2026-09-14, EW quirk mQ=800GeV/Lambda=4keV benchmark):
        # t_max = n_periods_to_integrate * period_est is NOT a valid upper
        # bound in general -- it has nothing to do with how long the CM
        # actually needs to travel to the outer detector layer. For events
        # with low CM boost (beta_cm small) and/or short oscillation period
        # (light mass, large Lambda), 40 periods' worth of time can be a
        # tiny fraction of the flight time needed, silently truncating the
        # trajectory before it reaches most layers (confirmed: for one EW
        # quirk event, 40*period = 1.4e15 vs the ~4.7e16 actually needed --
        # 33x too short). This affected EVERY EW quirk event (0/89 reached
        # full fiducial coverage) and could have silently truncated some
        # low-boost colored-quirk events too, even though the colored quirk
        # benchmark's higher mass/lower Lambda happened to avoid triggering
        # it badly in the runs done so far.
        #
        # Fix: when max_layer_r_cm is given, t_max must cover the ACTUAL
        # geometric requirement (CM flight time to well past the outer
        # layer), never just a fixed number of oscillation periods.
        #
        # Coarsening strategy (revised 2026-09-15, after the MAX_STEPS=120000
        # total-step cap was found to fail 77/89 = 86.5% of real EW-quirk
        # trigger-passing events below MIN_STEPS_PER_PERIOD): a total-step
        # CEILING is the wrong mechanism -- it caps something with no direct
        # physical meaning (how many steps fit in an arbitrary budget)
        # instead of the thing that is actually validated
        # (validate_dt_convergence.py: steps/period, not total steps). When
        # coarsening is needed, dt is now set to hit
        # TARGET_STEPS_PER_PERIOD_WHEN_COARSENING directly -- by
        # construction this can never fall below the validated floor,
        # because it explicitly targets it rather than whatever falls out of
        # an unrelated total-step cap. TARGET is set equal to
        # MIN_STEPS_PER_PERIOD itself (300) since validate_dt_convergence.py
        # already found rel err < 1e-4 down to 30 steps/period for the
        # generic benchmark checked there -- 300 already carries a ~10x
        # margin above that measured knee, so no further multiplier is
        # added on top (that would only inflate runtime for no accuracy
        # benefit at this resolution).
        #
        # ABSOLUTE_MAX_STEPS remains ONLY as a defensive ceiling against a
        # genuinely pathological input (e.g. a corrupt/absurd momentum),
        # not as the normal operating mechanism -- set well above the
        # largest requirement actually measured across the real EW sample
        # (worst case ~2.2e6 steps at the 300-steps/period floor, per
        # diagnose_step_budget.py) so it does not engage for any real event.
        TARGET_STEPS_PER_PERIOD_WHEN_COARSENING = MIN_STEPS_PER_PERIOD
        ABSOLUTE_MAX_STEPS = 20_000_000
        dt_original = period_est / steps_per_period
        dt = dt_original
        t_max = n_periods_to_integrate * period_est
        if max_layer_r_cm is not None:
            # BUG (found on paper re-audit, 2026-09-14): tracker layers are
            # defined by CYLINDRICAL radius r=sqrt(x^2+y^2), i.e. a purely
            # TRANSVERSE geometric requirement. Using the FULL 3D speed
            # |p1+p2|/E (as an earlier version of this code did) UNDER-
            # estimates the time needed to reach a given transverse radius
            # whenever the pair has nonzero longitudinal (pz) momentum
            # (beta_3D >= beta_T always) -- i.e. the exact same silent-
            # truncation failure mode as the already-fixed "33x too short"
            # bug above, but triggered by boost-along-z instead of low
            # overall boost. Use the TRANSVERSE beta only.
            Px_total, Py_total = p1[0] + p2[0], p1[1] + p2[1]
            E_total_geom = E1 + E2
            beta_cm_T = np.hypot(Px_total, Py_total) / E_total_geom if E_total_geom > 0 else 1.0
            beta_cm_T = max(beta_cm_T, 1e-6)
            t_needed_geom = (max_layer_r_cm * 3.0) / 1.973269804e-14 / beta_cm_T
            t_max = max(t_max, t_needed_geom)
            n_steps_needed = t_max / dt

            requested_steps_per_period = steps_per_period
            if n_steps_needed > (t_max / (period_est / TARGET_STEPS_PER_PERIOD_WHEN_COARSENING)):
                dt = period_est / TARGET_STEPS_PER_PERIOD_WHEN_COARSENING

            effective_steps_per_period = period_est / dt
            dt_was_coarsened = dt != dt_original
            dt_diagnostics = {
                "dt_original_gev_inv": dt_original,
                "dt_used_gev_inv": dt,
                "steps_per_period_requested": requested_steps_per_period,
                "steps_per_period_effective": effective_steps_per_period,
                "dt_was_coarsened": dt_was_coarsened,
            }
            n_steps_final = t_max / dt
            if effective_steps_per_period < MIN_STEPS_PER_PERIOD or n_steps_final > ABSOLUTE_MAX_STEPS:
                raise RuntimeError(
                    "simulate_quirk_hits: cannot reach MIN_STEPS_PER_PERIOD="
                    f"{MIN_STEPS_PER_PERIOD} within ABSOLUTE_MAX_STEPS="
                    f"{ABSOLUTE_MAX_STEPS} total steps (would need "
                    f"{n_steps_final:.3e} steps for "
                    f"{effective_steps_per_period:.1f} steps/period). This is "
                    "the defensive ceiling for a genuinely pathological "
                    "input, not the normal operating path -- check "
                    f"mass={mass_gev} GeV, Lambda={Lambda_gev} GeV, and the "
                    "supplied momenta for a real error before raising "
                    "ABSOLUTE_MAX_STEPS further "
                    f"(period_est={period_est:.3e}, t_max={t_max:.3e} GeV^-1).")
    else:
        # No confining string (e.g. converted e+/e- pair): there is no
        # oscillation period to base dt on -- the period formula would
        # divide by zero at Lambda=0. The only relevant timescale is the
        # Lorentz-force gyration, whose radius (~km scale for GeV-scale
        # leptons in a 2T field) is vastly larger than the ~50cm detector,
        # so the trajectory is nearly straight; size dt from the geometry
        # (flight time to the outer layer) with generous fixed resolution.
        if max_layer_r_cm is None:
            raise ValueError("max_layer_r_cm is required when Lambda_gev=0 "
                              "(no oscillation period to size dt from otherwise).")
        # Same transverse-vs-3D distinction as above, applied per-particle,
        # since there is no shared CM concept needed here -- each particle's
        # own transverse speed governs how fast IT reaches a given
        # cylindrical radius. Use the SLOWER (minimum) of the two particles'
        # transverse speeds to size a shared integration window that is
        # adequate for both.
        beta1_T = np.hypot(p1[0], p1[1]) / E1 if E1 > 0 else 1.0
        beta2_T = np.hypot(p2[0], p2[1]) / E2 if E2 > 0 else 1.0
        speed_est = max(min(beta1_T, beta2_T), 1e-6)
        t_max = (max_layer_r_cm * 3.0) / 1.973269804e-14 / speed_est
        dt = t_max / n_steps_no_string
        dt_diagnostics = {
            "dt_original_gev_inv": dt, "dt_used_gev_inv": dt,
            "steps_per_period_requested": None, "steps_per_period_effective": None,
            "dt_was_coarsened": False,
        }

    traj = integrate_trajectory(
        x1_0, p1, x2_0, p2, mass=mass_gev, charge1=charge1, charge2=charge2,
        Lambda_GeV=Lambda_gev, B_tesla=B_tesla,
        t_max_gev_inv=t_max, dt_gev_inv=dt,
    )
    traj["dt_diagnostics"] = dt_diagnostics
    # True primary-vertex position (cm), exposed so callers of the
    # coplanarity fit can measure hits relative to it (paper Sec III C:
    # "We will assume that the primary vertex is identified correctly, and
    # is located at the origin" -- the FIT's coordinate origin must be the
    # true vertex, not the fixed lab-frame origin used for detector
    # response/eta above, which stays unchanged here). This does NOT alter
    # any detector-response, eta, or trajectory-integration behavior above
    # -- it only exposes the already-known vertex position for downstream
    # use.
    traj["vertex_cm"] = vertex_cm

    x1_cm = traj["x1"] * 1.973269804e-14
    x2_cm = traj["x2"] * 1.973269804e-14
    t_gev_inv = traj["t_gev_inv"]

    raw_hits = []
    for quirk_idx, x_traj in [(1, x1_cm), (2, x2_cm)]:
        for layer in LAYERS:
            result = find_layer_crossing(x_traj, t_gev_inv, layer["r_cm"])
            if result is None:
                continue
            xyz, t_ns = result
            x, y, z = xyz
            r = np.hypot(x, y)
            # eta measured from the NOMINAL detector origin (0,0,0), NOT from
            # the per-event production/conversion vertex. Considered and
            # REJECTED switching to a vertex-relative definition (Sec III A:
            # "we only included the barrel... which effectively restricts the
            # fiducial range to |eta|<1.8" describes the barrel's fixed
            # geometric/hardware extent in the LAB frame; a vertex-relative
            # eta would silently cancel the very beamspot/conversion-point
            # smearing effect the paper wants included). This applies
            # identically to both the primary-vertex signal case and the
            # x0_override_cm (photon-conversion) case -- see DEVIATIONS_LOG.md.
            eta = eta_from_theta(np.arctan2(r, z)) if (z != 0 or r != 0) else 0.0
            if abs(eta) > FIDUCIAL_ETA_MAX:
                continue
            phi = np.arctan2(y, x)
            rphi = layer["r_cm"] * phi

            if layer["is_pixel"]:
                rphi_hit, z_hit, idx_rphi, idx_z = quantize_pixel(
                    rphi, z, layer["eff_res_rphi_um"], layer["eff_res_z_um"])
            else:
                sigma_rphi_cm = layer["eff_res_rphi_um"] * 1e-4
                sigma_z_cm = layer["eff_res_z_um"] * 1e-4
                rphi_hit = rphi + rng.normal(0.0, sigma_rphi_cm)
                z_hit = z + rng.normal(0.0, sigma_z_cm)
                idx_rphi = idx_z = None

            phi_hit = rphi_hit / layer["r_cm"]
            x_hit = layer["r_cm"] * np.cos(phi_hit)
            y_hit = layer["r_cm"] * np.sin(phi_hit)

            raw_hits.append({
                "layer": layer["name"], "layer_r_cm": layer["r_cm"],
                "quirk_index": quirk_idx, "t_ns": t_ns,
                "x": x_hit, "y": y_hit, "z": z_hit,
                "is_pixel": layer["is_pixel"],
                "idx_rphi": idx_rphi, "idx_z": idx_z,
            })

    # Merge neighboring-pixel hits (paper Sec III A) -- this belongs to the
    # detector simulation itself, not something callers should have to
    # remember to invoke separately (an earlier version of the analysis
    # pipeline forgot to call this at all).
    merged_hits = merge_neighboring_pixel_hits(raw_hits)
    # Non-invasive diagnostics only (does not change hits used downstream,
    # does not touch any cut or reconstruction logic): pre-merge hit count,
    # for cutflow/"before vs after merging" reporting.
    traj["n_hits_premerge"] = len(raw_hits)
    traj["n_hits_postmerge"] = len(merged_hits)
    # TRUTH-level crossing timing, from the pre-merge raw hits -- needed for
    # the paper's Sec IV, post-Eq.12 "25 ns timing cut" (part of the
    # fiducial-efficiency definition). Deliberately NOT read from
    # merged_hits: merge_neighboring_pixel_hits's merged entries inherit
    # t_ns from an arbitrary cluster member (the "seed"), not a genuine
    # max/representative time across the cluster, so post-merge timing is
    # not a faithful truth-crossing-time proxy.
    traj["max_hit_t_ns_premerge"] = (max(h["t_ns"] for h in raw_hits)
                                       if raw_hits else float("nan"))
    # Expose the RAW (pre-merge) hit list too -- purely additive (new dict
    # key on the already-returned traj dict; does not change the function's
    # signature, the primary `merged_hits` return value, or any existing
    # caller's behavior). Needed so a caller that wants to combine these
    # hits with ANOTHER hit source (e.g. pile-up) before merging can do
    # raw+raw -> one combined merge, instead of merged+raw -> merge again,
    # which is NOT generally equivalent: merging hard hits alone first can
    # shift a hit's effective position (a merged cluster's centroid), which
    # can then change whether a nearby third-party hit (e.g. a pile-up hit)
    # falls within one-pixel adjacency of it. (Found during the pile-up
    # overlay re-audit -- 2026-09-16.)
    traj["raw_hits"] = raw_hits
    return merged_hits, traj


def merge_neighboring_pixel_hits(hits, adjacency=1):
    """
    Merge hits in the SAME layer whose pixel indices are within `adjacency`
    of each other (both r-phi and z index space) into a single hit -- models
    ATLAS pixel hit-merging (paper Sec III A). Only applies to pixel-layer
    hits; SCT hits are passed through unchanged.

    Fixed (2026-09-14, paper re-audit) three real bugs in an earlier version:

    1. NON-TRANSITIVE clustering: the old code only checked adjacency of
       every other hit against the CURRENT SEED hit, not against other hits
       already placed in the growing cluster. For three pixels A-B-C at
       consecutive r-phi indices 0,1,2 (A-B adjacent, B-C adjacent, A-C NOT
       adjacent), seeding on A would merge {A,B} but leave C in its own
       cluster/pair with something else -- wrong; A,B,C are one physical
       merged cluster (adjacency is transitive: touching pixels merge into
       one blob regardless of chain length). Fixed with a graph
       connected-components pass (BFS) so an A-B-C chain always ends up in
       one cluster together.
    2. NO periodic phi=+-pi handling: r-phi pixel index is built from
       phi=atan2(y,x), which wraps at +-pi; two physically ADJACENT pixels
       straddling that wrap (index e.g. +N and -N-1 style) would have a huge
       raw index difference and never be seen as adjacent. Fixed by wrapping
       the r-phi index difference into (-n_bins/2, n_bins/2] before comparing
       to `adjacency`, where n_bins = 2*pi*r / pitch_rphi (the number of
       r-phi pixel bins that tile the full circle at this layer's radius).
    3. Cartesian mean of already-quantized (x,y) points does not sit ON the
       cylindrical layer radius (the mean of two points on a circle lies
       strictly inside it) -- inconsistent with "preserve local coordinates,
       reconstruct x,y at the fixed layer radius" applied to the pre-merge
       hits. Fixed: take a circular mean of phi (via the mean of unit
       vectors, robust across the +-pi wrap) and a plain mean of z, then
       reconstruct x,y at the EXACT layer radius, exactly as done for a
       single (unmerged) hit.

    Also: every returned hit (merged or not) now carries `merged_count`
    (>=1) and `source_quirk_indices` (sorted list of the distinct
    quirk_index values contributing to it) -- a merged cluster does not
    silently inherit only its seed hit's quirk_index, since two DIFFERENT
    quirks' hits landing in neighboring pixels is a real, physically
    meaningful possibility this information should not hide.
    """
    from collections import defaultdict

    by_layer = defaultdict(list)
    for h in hits:
        by_layer[h["layer"]].append(h)

    merged = []
    for layer_name, layer_hits in by_layer.items():
        if not layer_hits[0]["is_pixel"]:
            for h in layer_hits:
                merged.append({**h, "merged_count": h.get("merged_count", 1),
                               "source_quirk_indices": [h["quirk_index"]]})
            continue

        layer_r_cm = layer_hits[0]["layer_r_cm"]
        pitch_rphi_cm = None
        for L in LAYERS:
            if L["name"] == layer_name:
                pitch_rphi_cm = L["eff_res_rphi_um"] * 1e-4
                break
        n_bins = max(int(round(2.0 * np.pi * layer_r_cm / pitch_rphi_cm)), 1)

        def rphi_idx_diff(a, b, n_bins=n_bins):
            # Wrap the index difference into (-n_bins/2, n_bins/2] so pixels
            # straddling the phi=+-pi boundary compare as adjacent.
            d = (a - b + n_bins // 2) % n_bins - n_bins // 2
            return d

        n = len(layer_hits)
        adj = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if (abs(rphi_idx_diff(layer_hits[i]["idx_rphi"], layer_hits[j]["idx_rphi"])) <= adjacency
                        and abs(layer_hits[i]["idx_z"] - layer_hits[j]["idx_z"]) <= adjacency):
                    adj[i].append(j)
                    adj[j].append(i)

        # Connected components via BFS -- guarantees transitivity (A-B-C
        # chains merge into one cluster even though A and C are not
        # themselves directly adjacent).
        visited = [False] * n
        for i in range(n):
            if visited[i]:
                continue
            stack = [i]
            visited[i] = True
            component = []
            while stack:
                k = stack.pop()
                component.append(k)
                for nb in adj[k]:
                    if not visited[nb]:
                        visited[nb] = True
                        stack.append(nb)

            cluster = [layer_hits[k] for k in component]
            # sorted() on a raw mixed int/str set raises TypeError in Python 3
            # (e.g. quirk_index=1 for a hard-event hit vs. a pile-up
            # particle_tag string like "pu5_ev123_p7", once a merged cluster
            # mixes hard-scatter and pile-up hits -- found via the pixel-
            # merging unit tests' "mixed hard/pile-up cluster" case, which
            # crashed here; real pile-up overlay runs at any mu>0 hit this
            # whenever a pile-up hit lands next to a hard-event hit). Sort by
            # str(x) instead: still deterministic/reproducible, and this
            # field is provenance-only (never used for cut logic), so the
            # sort order itself has no physics meaning.
            source_quirk_indices = sorted(set(c["quirk_index"] for c in cluster), key=str)
            if len(cluster) == 1:
                h = cluster[0]
                merged.append({**h, "merged_count": 1,
                               "source_quirk_indices": source_quirk_indices})
                continue

            phis = np.array([np.arctan2(c["y"], c["x"]) for c in cluster])
            # Circular mean: average the unit vectors, not the angles
            # directly, so the +-pi wrap never causes a wrong-side average.
            mean_phi = np.arctan2(np.mean(np.sin(phis)), np.mean(np.cos(phis)))
            mz = np.mean([c["z"] for c in cluster])
            mx = layer_r_cm * np.cos(mean_phi)
            my = layer_r_cm * np.sin(mean_phi)

            seed = cluster[0]
            merged.append({**seed, "x": mx, "y": my, "z": mz,
                           "merged_count": len(cluster),
                           "source_quirk_indices": source_quirk_indices,
                           "quirk_index": (source_quirk_indices[0]
                                           if len(source_quirk_indices) == 1
                                           else None)})
    return merged
