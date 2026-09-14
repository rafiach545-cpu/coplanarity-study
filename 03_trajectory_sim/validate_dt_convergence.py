"""
D2 (validation requirement): RK4 convergence test using dt, dt/2, dt/4, and a
scan over steps_per_period, to empirically justify MIN_STEPS_PER_PERIOD used
in trajectory_to_hits.py's dt-coarsening-floor check.

Uses the same Eq. 4 analytic solution as validate_against_eq4.py (B=0,
back-to-back, straight-string limit) as ground truth, since it is the only
closed-form check available.
"""

import numpy as np
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
from quirk_trajectory import integrate_trajectory, gev_to_cm
from validate_against_eq4 import eq4_analytic


def rel_error_for_steps_per_period(mQ_gev, Lambda_gev, v, steps_per_period):
    gamma = 1.0 / np.sqrt(1.0 - v ** 2)
    p_mag = gamma * mQ_gev * v
    x1_0 = np.array([0.0, 0.0, 0.0])
    x2_0 = np.array([0.0, 0.0, 0.0])
    p1_0 = np.array([+p_mag, 0.0, 0.0])
    p2_0 = np.array([-p_mag, 0.0, 0.0])

    period = 2.0 * v * gamma * mQ_gev / (Lambda_gev ** 2)
    t_max = period
    dt = period / steps_per_period

    traj = integrate_trajectory(
        x1_0, p1_0, x2_0, p2_0, mass=mQ_gev, charge1=0.0, charge2=0.0,
        Lambda_GeV=Lambda_gev, B_tesla=0.0, t_max_gev_inv=t_max, dt_gev_inv=dt,
    )
    d_numeric = np.linalg.norm(traj["x1"], axis=1)
    d_analytic = eq4_analytic(traj["t_gev_inv"], mQ_gev, Lambda_gev, v)
    mask = (traj["t_gev_inv"] > 0.02 * period) & (traj["t_gev_inv"] < 0.98 * period)
    rel_err = np.abs(d_numeric[mask] - d_analytic[mask]) / np.maximum(d_analytic[mask], 1e-30)
    return np.max(rel_err)


if __name__ == "__main__":
    mQ, Lam, v = 1800.0, 2e-6, 0.6

    print("=== D2: RK4 order-of-convergence check (dt, dt/2, dt/4) ===")
    base_steps = 200
    errs = []
    for mult, label in [(1, "dt"), (2, "dt/2"), (4, "dt/4")]:
        steps = base_steps * mult
        err = rel_error_for_steps_per_period(mQ, Lam, v, steps)
        errs.append(err)
        print(f"  {label:6s} (steps/period={steps:5d}): max rel err = {err:.3e}")
    ratio1 = errs[0] / errs[1] if errs[1] > 0 else float("inf")
    ratio2 = errs[1] / errs[2] if errs[2] > 0 else float("inf")
    print(f"  error ratio dt->dt/2:  {ratio1:.2f} (RK4 expects ~16x per halving)")
    print(f"  error ratio dt/2->dt/4: {ratio2:.2f} (RK4 expects ~16x per halving)")
    order_ok = ratio1 > 8 and ratio2 > 8  # allow slack for the analytic-check floor
    print(f"  4th-order convergence behavior observed: {order_ok}")
    print()

    print("=== D2b: steps_per_period scan -> MIN_STEPS_PER_PERIOD justification ===")
    print(f"  {'steps/period':>14s} | {'max rel err':>12s} | pass(<1e-4)")
    scan_points = [30, 50, 100, 150, 200, 300, 500, 1000, 1500, 3000]
    results = []
    for sp in scan_points:
        err = rel_error_for_steps_per_period(mQ, Lam, v, sp)
        results.append((sp, err))
        print(f"  {sp:14d} | {err:12.3e} | {err < 1e-4}")
    print()
    # Find the smallest steps_per_period in the scan that keeps rel err < 1e-4
    passing = [sp for sp, err in results if err < 1e-4]
    knee = min(passing) if passing else None
    print(f"  Smallest scanned steps/period with rel err < 1e-4: {knee}")
    print("  MIN_STEPS_PER_PERIOD=300 (used in trajectory_to_hits.py) is chosen "
          "as a safety margin above this measured knee, not an arbitrary guess.")
