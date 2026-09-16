"""
Validates helix_propagation.py's exact analytic helix solution against the
already-validated RK4 integrator (quirk_trajectory.py), as required by
helix_propagation.py's own module docstring before it may be trusted for the
real pile-up pipeline.

Method: set Lambda_GeV=0 in quirk_trajectory.integrate_trajectory, which
makes string_force() return exactly zero (Lambda2=0) -- this fully decouples
the two "quirks" in the pair, so particle 1's motion reduces to the plain
relativistic Lorentz-force equation, i.e. exactly the physical system
find_helix_layer_crossings() solves in closed form. Particle 2's state is
irrelevant (arbitrary, never influences particle 1 when Lambda=0) and is
discarded.

For each test case: run RK4 with a small fixed step, linearly interpolate
the RK4 trajectory to each target layer radius, and compare position/time
against the exact helix result. RK4 step count/step size are chosen so the
particle's arc length to the outermost layer is resolved by ~5000 steps
(curvature radius here is O(meters) >> detector radii of O(10s of cm), so
the trajectory is very nearly straight over this range and fixed-step RK4
converges easily).

Tolerance: 1e-3 cm / 1e-3 ns (both far above the actual sub-um/sub-ps level
agreement observed -- see printed diffs).
"""
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
import numpy as np
from quirk_trajectory import integrate_trajectory, HBARC_GEV_CM
from helix_propagation import find_helix_layer_crossings

LAYER_RADII_CM = [3.325, 5.05, 8.85, 12.25, 29.9, 37.1, 44.3, 51.4]
HBARC_GEV_S = 6.582119569e-25
POS_TOL_CM = 1e-3
T_TOL_NS = 1e-3


def run_case(mass, p_gev, x0_cm, charge_e, B_tesla, label):
    x0_cm = np.asarray(x0_cm, dtype=float)
    p_gev = np.asarray(p_gev, dtype=float)
    x0_gevinv = x0_cm / HBARC_GEV_CM
    p2_dummy = np.array([1.0, 0.0, 0.0])  # irrelevant: Lambda=0 decouples the pair

    E = np.sqrt(p_gev @ p_gev + mass**2)
    v = np.linalg.norm(p_gev) / E
    r_max_cm = 65.0
    t_max = (r_max_cm / HBARC_GEV_CM) / v * 1.4
    dt = t_max / 5000.0

    traj = integrate_trajectory(x0_gevinv, p_gev, x0_gevinv + 1e-3, p2_dummy,
                                 mass, charge_e, 0.0, 0.0, B_tesla, t_max, dt)
    x1_cm = traj["x1"] * HBARC_GEV_CM
    r_from_beam = np.hypot(x1_cm[:, 0], x1_cm[:, 1])

    helix_result = find_helix_layer_crossings(x0_cm, p_gev, mass, charge_e, B_tesla, LAYER_RADII_CM)

    max_pos_diff = 0.0
    max_t_diff = 0.0
    n_compared = 0
    for r_target in LAYER_RADII_CM:
        ge = r_from_beam >= r_target
        if not np.any(ge):
            continue
        idx = np.argmax(ge)
        if idx == 0:
            continue
        r0, r1 = r_from_beam[idx - 1], r_from_beam[idx]
        frac = (r_target - r0) / (r1 - r0)
        xyz_interp = x1_cm[idx - 1] + frac * (x1_cm[idx] - x1_cm[idx - 1])
        t0, t1 = traj["t_gev_inv"][idx - 1], traj["t_gev_inv"][idx]
        t_interp_ns = (t0 + frac * (t1 - t0)) * HBARC_GEV_S * 1e9

        helix_xyz, helix_t_ns = helix_result.get(r_target, (None, None))
        if helix_xyz is None:
            print(f"  [{label}] r={r_target}: helix reports NO CROSSING but RK4 crossed -- MISMATCH")
            return False
        diff = np.linalg.norm(xyz_interp - helix_xyz)
        tdiff = abs(t_interp_ns - helix_t_ns)
        max_pos_diff = max(max_pos_diff, diff)
        max_t_diff = max(max_t_diff, tdiff)
        n_compared += 1

    ok = max_pos_diff < POS_TOL_CM and max_t_diff < T_TOL_NS and n_compared >= 6
    status = "PASS" if ok else "FAIL"
    print(f"  [{label}] layers_compared={n_compared}/8, max_pos_diff={max_pos_diff:.3e} cm, "
          f"max_t_diff={max_t_diff:.3e} ns -> {status}")
    return ok


if __name__ == "__main__":
    cases = [
        (0.13957, [2.0, 1.5, 3.0], [0.0, 0.0, 0.0], 1.0, 2.0, "pion+, origin vertex"),
        (0.13957, [2.0, 1.5, 3.0], [0.0, 0.0, 0.0], -1.0, 2.0, "pion-, origin vertex"),
        (0.13957, [1.5, -2.0, 4.0], [0.0, 0.0, 4.5], 1.0, 2.0, "pion+, z-shifted (beamspot) vertex"),
        (0.000511, [0.8, 0.3, 1.0], [0.1, -0.2, -2.0], -1.0, 2.0, "electron, off-axis xy+z vertex"),
    ]
    results = [run_case(*c) for c in cases]
    print(f"\n{sum(results)}/{len(results)} cases PASS")
    sys.exit(0 if all(results) else 1)
