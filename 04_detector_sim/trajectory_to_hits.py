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
from atlas_geometry import LAYERS, FIDUCIAL_ETA_MAX, BEAMSPOT_SIGMA_Z_CM

C_LIGHT_CM_PER_NS = 29.9792458  # speed of light, cm/ns


def find_layer_crossing(x_traj_cm, t_gev_inv, layer_r_cm):
    """
    x_traj_cm: (N,3) array, trajectory positions in cm.
    Returns (hit_xyz_cm, hit_t_ns) at the first crossing of radius
    layer_r_cm, or None if the trajectory never reaches that radius.
    """
    r = np.hypot(x_traj_cm[:, 0], x_traj_cm[:, 1])
    above = r >= layer_r_cm
    if not np.any(above):
        return None
    idx = np.argmax(above)  # first index where r >= layer_r_cm
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
    pitch_rphi_cm = pitch_rphi_um * 1e-4
    pitch_z_cm = pitch_z_um * 1e-4
    idx_rphi = np.round(rphi_cm / pitch_rphi_cm)
    idx_z = np.round(z_cm / pitch_z_cm)
    return idx_rphi * pitch_rphi_cm, idx_z * pitch_z_cm, int(idx_rphi), int(idx_z)


def simulate_quirk_hits(p1_gev, p2_gev, mass_gev, Lambda_gev, B_tesla,
                         charge1, charge2, rng, z0_cm=None,
                         n_periods_to_integrate=40, steps_per_period=1500,
                         max_layer_r_cm=None, x0_override_cm=None,
                         n_steps_no_string=5000):
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
    Returns list of hit dicts: {layer, x,y,z (cm), quirk_index}
    """
    if x0_override_cm is not None:
        x0_natural_vec = np.array(x0_override_cm) / 1.973269804e-14
        x1_0 = x0_natural_vec.copy()
        x2_0 = x0_natural_vec.copy()
    else:
        if z0_cm is None:
            z0_cm = rng.normal(0.0, BEAMSPOT_SIGMA_Z_CM)
        z0_natural = z0_cm / 1.973269804e-14
        x1_0 = np.array([0.0, 0.0, z0_natural])
        x2_0 = np.array([0.0, 0.0, z0_natural])

    p1 = np.array(p1_gev[:3])
    p2 = np.array(p2_gev[:3])
    E1, E2 = p1_gev[3], p2_gev[3]

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
        # layer), never just a fixed number of oscillation periods. To keep
        # runtime bounded for events needing many periods, dt is relaxed
        # (coarsened) rather than the number of steps growing without
        # bound -- capped at MAX_STEPS total steps.
        MAX_STEPS = 120000
        dt = period_est / steps_per_period
        t_max = n_periods_to_integrate * period_est
        if max_layer_r_cm is not None:
            beta_cm_for_geom = np.linalg.norm(p1 + p2) / (E1 + E2) if (E1 + E2) > 0 else 1.0
            beta_cm_for_geom = max(beta_cm_for_geom, 1e-6)
            t_needed_geom = (max_layer_r_cm * 3.0) / 1.973269804e-14 / beta_cm_for_geom
            t_max = max(t_max, t_needed_geom)
            n_steps_needed = t_max / dt
            if n_steps_needed > MAX_STEPS:
                dt = t_max / MAX_STEPS  # coarsen dt to stay within budget
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
        speed_est = np.linalg.norm(p1) / E1 if E1 > 0 else 1.0
        speed_est = max(speed_est, 1e-6)
        t_max = (max_layer_r_cm * 3.0) / 1.973269804e-14 / speed_est
        dt = t_max / n_steps_no_string

    traj = integrate_trajectory(
        x1_0, p1, x2_0, p2, mass=mass_gev, charge1=charge1, charge2=charge2,
        Lambda_GeV=Lambda_gev, B_tesla=B_tesla,
        t_max_gev_inv=t_max, dt_gev_inv=dt,
    )

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
            eta = -np.log(np.tan(0.5 * np.arctan2(r, z))) if z != 0 or r != 0 else 0.0
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
    return merged_hits, traj


def merge_neighboring_pixel_hits(hits, adjacency=1):
    """
    Merge hits in the SAME layer whose pixel indices are within `adjacency`
    of each other (both r-phi and z index space) into a single hit at the
    mean position -- models ATLAS pixel hit-merging (paper Sec III A).
    Only applies to pixel-layer hits; SCT hits are passed through unchanged.
    """
    from collections import defaultdict
    by_layer = defaultdict(list)
    for h in hits:
        by_layer[h["layer"]].append(h)

    merged = []
    for layer_name, layer_hits in by_layer.items():
        if not layer_hits[0]["is_pixel"]:
            merged.extend(layer_hits)
            continue
        used = [False] * len(layer_hits)
        for i, h in enumerate(layer_hits):
            if used[i]:
                continue
            cluster = [h]
            used[i] = True
            for j in range(i + 1, len(layer_hits)):
                if used[j]:
                    continue
                h2 = layer_hits[j]
                if (abs(h["idx_rphi"] - h2["idx_rphi"]) <= adjacency and
                        abs(h["idx_z"] - h2["idx_z"]) <= adjacency):
                    cluster.append(h2)
                    used[j] = True
            if len(cluster) == 1:
                merged.append(h)
            else:
                mx = np.mean([c["x"] for c in cluster])
                my = np.mean([c["y"] for c in cluster])
                mz = np.mean([c["z"] for c in cluster])
                merged.append({**h, "x": mx, "y": my, "z": mz,
                               "merged_count": len(cluster)})
    return merged
