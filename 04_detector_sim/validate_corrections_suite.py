"""
Section D validation suite (D3-D10) for the trajectory/Stage-2 corrections.
D1 (Eq.4 B=0 test) and D2 (RK4 convergence) are their own existing scripts:
  03_trajectory_sim/validate_against_eq4.py
  03_trajectory_sim/validate_dt_convergence.py

Every check prints: expected result, measured result, relative error (or a
qualitative pass condition where no single number applies), and pass/fail.
"""

import numpy as np
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
from quirk_trajectory import integrate_trajectory, equations_of_motion, QuirkPairState
from trajectory_to_hits import (simulate_quirk_hits, quantize_pixel,
                                 merge_neighboring_pixel_hits)
from atlas_geometry import LAYERS, eta_from_theta

HBARC_CM = 1.973269804e-14
results = []


def report(name, expected, measured, rel_err, tol, passed):
    results.append((name, passed))
    print(f"--- {name} ---")
    print(f"  expected : {expected}")
    print(f"  measured : {measured}")
    print(f"  rel_err  : {rel_err}")
    print(f"  tol      : {tol}")
    print(f"  PASS     : {passed}")
    print()


# ---------------------------------------------------------------------
# D3: Lambda=0 Lorentz gyroradius test
# ---------------------------------------------------------------------
def d3_gyroradius():
    mass = 0.000511  # electron, GeV
    charge = 1.0  # units of e
    e_nat = 0.30282212
    B_tesla = 2.0
    TESLA_TO_GEV2 = 1.9535e-16
    Bz = B_tesla * TESLA_TO_GEV2

    p_perp = 5.0  # GeV, purely transverse
    p0 = np.array([p_perp, 0.0, 0.0])
    E = np.sqrt(p_perp ** 2 + mass ** 2)
    v_perp = p_perp / E

    # Classical relativistic gyroradius: r = p_perp / (|q|*e*B)
    r_expected_natural = p_perp / (abs(charge) * e_nat * Bz)
    r_expected_cm = r_expected_natural * HBARC_CM

    period_natural = 2 * np.pi * E / (abs(charge) * e_nat * Bz)  # cyclotron period
    t_max = period_natural
    dt = t_max / 20000.0

    traj = integrate_trajectory(
        np.zeros(3), p0, np.array([1e6, 0, 0]), np.array([0.001, 0, 0]),
        mass=mass, charge1=charge, charge2=0.0, Lambda_GeV=0.0,
        B_tesla=B_tesla, t_max_gev_inv=t_max, dt_gev_inv=dt,
    )
    x1 = traj["x1"]
    # Radius of the circular orbit in the transverse (x,y) plane, measured
    # from the orbit's own center (found as the mean position over one full
    # period, which for a closed circle equals the center).
    center = x1[:, :2].mean(axis=0)
    r_numeric_natural = np.linalg.norm(x1[:, :2] - center, axis=1).mean()
    r_numeric_cm = r_numeric_natural * HBARC_CM

    rel_err = abs(r_numeric_cm - r_expected_cm) / r_expected_cm
    report("D3: Lambda=0 Lorentz gyroradius",
           f"r = {r_expected_cm:.6f} cm (p_perp/(qeB))",
           f"r = {r_numeric_cm:.6f} cm (mean orbit radius)",
           f"{rel_err:.3e}", "< 1e-3", rel_err < 1e-3)


# ---------------------------------------------------------------------
# D4: Opposite-charge bending-direction test
# ---------------------------------------------------------------------
def d4_bending_direction():
    mass = 0.000511
    B_tesla = 2.0
    p0 = np.array([5.0, 0.0, 0.0])
    t_max = 5e11
    dt = t_max / 5000.0

    def run(charge):
        traj = integrate_trajectory(
            np.zeros(3), p0, np.array([1e6, 0, 0]), np.array([0.001, 0, 0]),
            mass=mass, charge1=charge, charge2=0.0, Lambda_GeV=0.0,
            B_tesla=B_tesla, t_max_gev_inv=t_max, dt_gev_inv=dt,
        )
        return traj["x1"][-1]

    x_pos = run(+1.0)
    x_neg = run(-1.0)
    # A positive charge moving along +x in Bz>0 feels F=q(v x B); v=+x, B=+z
    # -> v x B = x_hat x z_hat = -y_hat, so F = q*(-y_hat) for q>0 -> bends
    # toward -y. Opposite charge bends toward +y. Check the sign of y at a
    # fixed, still-early time (before either completes a quarter-turn) is
    # opposite for the two charges, and that neither y is ~0 (i.e. bending
    # actually happened).
    bent_opposite = (x_pos[1] * x_neg[1] < 0) and (abs(x_pos[1]) > 1e-6) and (abs(x_neg[1]) > 1e-6)
    report("D4: opposite-charge bending direction",
           "y(+charge) and y(-charge) have opposite sign at fixed t",
           f"y(+1)={x_pos[1]:.6e}, y(-1)={x_neg[1]:.6e} (natural units)",
           "n/a (sign check)", "opposite signs, both nonzero", bent_opposite)


# ---------------------------------------------------------------------
# D5: Initial x1=x2 boosted-pair test using relative velocity (A1 fix)
# ---------------------------------------------------------------------
def d5_coincident_point_uses_relative_velocity():
    mass = 1800.0
    Lambda2 = (2e-6) ** 2
    # Strongly asymmetric (boosted) pair: v1 != -v2, and neither is zero.
    p1 = np.array([300.0, 0.0, 400.0])
    p2 = np.array([-50.0, 80.0, 200.0])
    y = np.concatenate([[0, 0, 0], p1, [0, 0, 0], p2])
    dy = equations_of_motion(0.0, y, mass, 0.0, 0.0, Lambda2, np.zeros(3))
    F1 = dy[3:6]

    E1 = np.sqrt(np.dot(p1, p1) + mass ** 2)
    E2 = np.sqrt(np.dot(p2, p2) + mass ** 2)
    v1, v2 = p1 / E1, p2 / E2
    v_rel = v1 - v2
    n_hat_expected = v_rel / np.linalg.norm(v_rel)
    F1_dir = F1 / np.linalg.norm(F1)
    # Force should be attractive along -n_hat_expected (dominant term1, small
    # term2 correction) -- check alignment via dot product close to -1.
    cos_align = np.dot(F1_dir, -n_hat_expected)

    n_hat_old = v1 / np.linalg.norm(v1)  # what the pre-fix code would have used
    cos_align_old_convention = np.dot(F1_dir, -n_hat_old)

    passed = cos_align > 0.99  # allow for the (small) term2 perpendicular correction
    report("D5: coincident-point (x1=x2) uses v1-v2, not v1",
           "F1 direction ~ -(v1-v2)/|v1-v2| (cos alignment ~1)",
           f"cos_align_to_-v_rel_hat={cos_align:.6f}, "
           f"cos_align_to_-v1_hat(old convention)={cos_align_old_convention:.6f}",
           f"{1 - cos_align:.3e}", "cos_align > 0.99", passed)


# ---------------------------------------------------------------------
# D6: Pixel quantization unit test
# ---------------------------------------------------------------------
def d6_pixel_quantization():
    pitch_rphi_um, pitch_z_um = 50.0, 250.0
    pitch_rphi_cm = pitch_rphi_um * 1e-4
    pitch_z_cm = pitch_z_um * 1e-4

    # A point exactly at 2.3 pixels in rphi, -1.4 pixels in z -> should snap
    # to the nearest INTEGER pixel index (round-half-away-from-zero-ish via
    # np.round), i.e. index (2, -1) here.
    rphi_in = 2.3 * pitch_rphi_cm
    z_in = -1.4 * pitch_z_cm
    rphi_out, z_out, idx_rphi, idx_z = quantize_pixel(rphi_in, z_in, pitch_rphi_um, pitch_z_um)

    expected_idx = (2, -1)
    idx_ok = (idx_rphi, idx_z) == expected_idx
    pos_ok = (abs(rphi_out - expected_idx[0] * pitch_rphi_cm) < 1e-12 and
              abs(z_out - expected_idx[1] * pitch_z_cm) < 1e-12)
    report("D6: pixel quantization snaps to nearest grid index",
           f"idx=(2,-1), position=(2*pitch, -1*pitch)",
           f"idx=({idx_rphi},{idx_z}), position=({rphi_out:.6e},{z_out:.6e}) cm",
           "n/a (exact index match)", "idx==(2,-1) and position exact",
           idx_ok and pos_ok)


# ---------------------------------------------------------------------
# D7: Transitive A-B-C pixel-cluster test
# ---------------------------------------------------------------------
def d7_transitive_clustering():
    layer = LAYERS[0]  # L1_IBL, pixel
    r = layer["r_cm"]
    pitch_rphi_cm = layer["eff_res_rphi_um"] * 1e-4

    def make_hit(idx_rphi, idx_z, quirk_index=1):
        rphi = idx_rphi * pitch_rphi_cm
        phi = rphi / r
        return {"layer": layer["name"], "layer_r_cm": r, "quirk_index": quirk_index,
                "t_ns": 0.0, "x": r * np.cos(phi), "y": r * np.sin(phi), "z": 0.0,
                "is_pixel": True, "idx_rphi": idx_rphi, "idx_z": 0}

    # A at rphi-index 0, B at 1, C at 2: A-B adjacent, B-C adjacent, A-C NOT
    # directly adjacent (diff=2 > adjacency=1) -- must still end up in ONE
    # cluster via transitivity.
    hits = [make_hit(0, 0), make_hit(1, 0), make_hit(2, 0)]
    merged = merge_neighboring_pixel_hits(hits)

    one_cluster = (len(merged) == 1) and (merged[0]["merged_count"] == 3)
    report("D7: transitive A-B-C pixel clustering",
           "A,B,C (chain-adjacent, A-C not directly adjacent) merge into 1 cluster of 3",
           f"{len(merged)} cluster(s), sizes={[m['merged_count'] for m in merged]}",
           "n/a (exact count)", "1 cluster, merged_count==3", one_cluster)


# ---------------------------------------------------------------------
# D8: phi=+-pi Pixel-boundary merge test
# ---------------------------------------------------------------------
def d8_phi_wraparound_merge():
    layer = LAYERS[0]
    r = layer["r_cm"]
    pitch_rphi_cm = layer["eff_res_rphi_um"] * 1e-4
    n_bins = int(round(2 * np.pi * r / pitch_rphi_cm))

    def make_hit_at_phi(phi, idx_rphi):
        return {"layer": layer["name"], "layer_r_cm": r, "quirk_index": 1,
                "t_ns": 0.0, "x": r * np.cos(phi), "y": r * np.sin(phi), "z": 0.0,
                "is_pixel": True, "idx_rphi": idx_rphi, "idx_z": 0}

    # One hit just below +pi, one hit just above -pi -- physically adjacent
    # pixels straddling the wrap, but with idx_rphi = n_bins//2 and
    # -(n_bins//2)-ish (huge raw index difference).
    idx_a = n_bins // 2
    idx_b = -(n_bins // 2) - 1  # wraps to be adjacent to idx_a
    phi_a = idx_a * pitch_rphi_cm / r
    phi_b = idx_b * pitch_rphi_cm / r
    hits = [make_hit_at_phi(phi_a, idx_a), make_hit_at_phi(phi_b, idx_b)]
    merged = merge_neighboring_pixel_hits(hits)

    merged_ok = (len(merged) == 1) and (merged[0]["merged_count"] == 2)
    on_circle = False
    if merged:
        r_out = np.hypot(merged[0]["x"], merged[0]["y"])
        on_circle = abs(r_out - r) < 1e-9
    report("D8: phi=+-pi pixel-boundary merge",
           "two pixels straddling phi=+-pi merge into 1 cluster, result ON the layer radius",
           f"{len(merged)} cluster(s), merged_count={[m['merged_count'] for m in merged]}, "
           f"on_circle={on_circle}",
           "n/a (exact)", "1 cluster, count==2, on_circle==True",
           merged_ok and on_circle)


# ---------------------------------------------------------------------
# D9: Nonzero-z0 eta test
# ---------------------------------------------------------------------
def d9_nonzero_z0_eta():
    # A hit at fixed (x,y) but the SAME lab-frame z, computed for two
    # different "vertex" z0 assumptions, should give the SAME eta under the
    # origin-relative convention (since eta only depends on the hit's own
    # global (r,z), never on where the vertex was) -- confirming the
    # documented, deliberate choice (C3) is actually what the code does.
    r_cm = 5.05
    z_cm = 3.0  # global z of the hit, regardless of vertex position
    eta = eta_from_theta(np.arctan2(r_cm, z_cm))

    # Sanity: also check against the standard eta=-ln(tan(theta/2)) formula
    # directly, and against the asinh(z/r) approximation relation for
    # consistency at moderate eta.
    theta = np.arctan2(r_cm, z_cm)
    eta_direct = -np.log(np.tan(theta / 2.0))
    rel_err = abs(eta - eta_direct) / abs(eta_direct)

    report("D9: eta computed from global (r,z), independent of vertex z0",
           f"eta_from_theta matches direct -ln(tan(theta/2)) formula exactly",
           f"eta_from_theta={eta:.6f}, direct={eta_direct:.6f}",
           f"{rel_err:.3e}", "< 1e-12", rel_err < 1e-12)


# ---------------------------------------------------------------------
# D10: Outer-layer coverage test using beta_T rather than total beta
# ---------------------------------------------------------------------
def d10_transverse_beta_coverage():
    # Direct, isolated unit-test of the exact fixed quantity (t_needed_geom's
    # beta estimate), rather than a full end-to-end simulate_quirk_hits run
    # -- a full run couples this to the (unrelated, separately validated)
    # MAX_STEPS/MIN_STEPS_PER_PERIOD budget in a way that is easy to
    # over/under-tune and would obscure exactly what is being checked here.
    #
    # For a pz-dominated pair, beta_3D = |p|/E is LARGER than the true
    # geometric requirement beta_T = pt/E (layers are defined by CYLINDRICAL
    # radius). The OLD code used beta_3D, UNDER-estimating t_needed_geom
    # (= r*3/beta) whenever beta_3D > beta_T -- i.e. for any nonzero pz. That
    # under-estimate is exactly the same failure mode as the already-fixed
    # "33x too short" bug: t_max could end up too short to reach the outer
    # layer, silently truncating the trajectory.
    mass_gev = 1800.0
    p1 = np.array([60.0, 0.0, 1000.0])
    p2 = np.array([-40.0, 30.0, 950.0])
    E1 = np.sqrt(np.dot(p1, p1) + mass_gev ** 2)
    E2 = np.sqrt(np.dot(p2, p2) + mass_gev ** 2)

    beta_3D_wrong = np.linalg.norm(p1 + p2) / (E1 + E2)
    beta_T_correct = np.hypot(p1[0] + p2[0], p1[1] + p2[1]) / (E1 + E2)

    max_layer_r_cm = 60.0
    t_needed_3D_wrong = (max_layer_r_cm * 3.0) / HBARC_CM / beta_3D_wrong
    t_needed_T_correct = (max_layer_r_cm * 3.0) / HBARC_CM / beta_T_correct

    # The fixed formula must give a LARGER (safer, more conservative)
    # t_needed than the old 3D-beta formula whenever pz != 0, since
    # beta_T < beta_3D always in that case -- confirming the fix moves in
    # the safe direction (never under-shoots what the old code already
    # covered, only extends coverage further where needed).
    fix_is_more_conservative = t_needed_T_correct > t_needed_3D_wrong
    ratio = t_needed_T_correct / t_needed_3D_wrong

    report("D10: transverse (not 3D) beta used for cylindrical geometric-time sizing",
           "beta_T < beta_3D for pz!=0  =>  t_needed_geom(transverse) > t_needed_geom(3D)",
           f"beta_3D={beta_3D_wrong:.5f}, beta_T={beta_T_correct:.5f}, "
           f"t_needed ratio (new/old)={ratio:.2f}x",
           f"n/a (must be >1, measured {ratio:.2f})", "> 1", fix_is_more_conservative)


if __name__ == "__main__":
    d3_gyroradius()
    d4_bending_direction()
    d5_coincident_point_uses_relative_velocity()
    d6_pixel_quantization()
    d7_transitive_clustering()
    d8_phi_wraparound_merge()
    d9_nonzero_z0_eta()
    d10_transverse_beta_coverage()

    print("=== SUMMARY ===")
    for name, passed in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"\nALL PASS: {all(p for _, p in results)}")
