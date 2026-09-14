"""
Validate quirk_trajectory.py against Eq. 4 of arXiv:1708.02243v2 -- the exact
closed-form solution for two quirks produced back-to-back with initial speed
v, no external force (B=0), straight-string approximation:

    d_cm(t) = (mQ/Lambda^2) * [ gamma - sqrt(1 + (Lambda^2 t / mQ - v*gamma)^2) ]

for 0 <= t <= 2*v*gamma*mQ/Lambda^2, gamma = 1/sqrt(1-v^2).

This is a hard numerical check: our general RK4 integrator (which supports
arbitrary geometry + B field) must reproduce this exact 1D analytic result
in the B=0, back-to-back special case, to within RK4 discretization error.
"""

import numpy as np
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
from quirk_trajectory import integrate_trajectory, gev_to_cm


def eq4_analytic(t, mQ, Lambda, v):
    gamma = 1.0 / np.sqrt(1.0 - v ** 2)
    Lambda2 = Lambda ** 2
    bracket = 1.0 + (Lambda2 * t / mQ - v * gamma) ** 2
    return (mQ / Lambda2) * (gamma - np.sqrt(bracket))


def run_check(mQ_gev, Lambda_gev, v, label):
    gamma = 1.0 / np.sqrt(1.0 - v ** 2)
    p_mag = gamma * mQ_gev * v

    # Back-to-back along x, produced at the origin (both quirks start at x=0;
    # Eq. 4's d_cm is measured from this common production point).
    x1_0 = np.array([0.0, 0.0, 0.0])
    x2_0 = np.array([0.0, 0.0, 0.0])
    p1_0 = np.array([+p_mag, 0.0, 0.0])
    p2_0 = np.array([-p_mag, 0.0, 0.0])

    period = 2.0 * v * gamma * mQ_gev / (Lambda_gev ** 2)
    t_max = period  # one full period, matches Eq. 4's stated validity range
    dt = period / 20000.0

    traj = integrate_trajectory(
        x1_0, p1_0, x2_0, p2_0,
        mass=mQ_gev, charge1=0.0, charge2=0.0,  # no Lorentz force for this check
        Lambda_GeV=Lambda_gev, B_tesla=0.0,
        t_max_gev_inv=t_max, dt_gev_inv=dt,
    )

    # Eq. 4's d_cm(t) is the distance from the CM to ONE quirk (subscript
    # "cm" = as measured from the CM frame's origin), not the full pair
    # separation. With this symmetric back-to-back setup the CM stays fixed
    # at the origin, so the apples-to-apples comparison is |x1(t)| vs d_cm(t).
    d_numeric = np.linalg.norm(traj["x1"], axis=1)
    d_analytic = eq4_analytic(traj["t_gev_inv"], mQ_gev, Lambda_gev, v)

    # Compare away from the very endpoints where both should -> 0 and
    # floating point / regularization effects are largest.
    mask = (traj["t_gev_inv"] > 0.02 * period) & (traj["t_gev_inv"] < 0.98 * period)
    rel_err = np.abs(d_numeric[mask] - d_analytic[mask]) / np.maximum(d_analytic[mask], 1e-30)
    max_rel_err = np.max(rel_err)
    max_d_cm = gev_to_cm(np.max(d_analytic))

    print(f"--- {label}: mQ={mQ_gev} GeV, Lambda={Lambda_gev*1e6:.1f} eV (as GeV: {Lambda_gev:.3e}), v={v} ---")
    print(f"  period (natural units) = {period:.6e} GeV^-1")
    print(f"  max separation (analytic) = {max_d_cm:.4f} cm")
    print(f"  max relative error (numeric vs Eq.4 analytic), middle 96% of period: {max_rel_err:.3e}")
    ok = max_rel_err < 1e-3
    print(f"  PASS (rel err < 1e-3): {ok}")
    return ok


if __name__ == "__main__":
    # Lambda in GeV: 2 keV = 2e-6 GeV (matches Fig 2/3 benchmark: mQ=1.8 TeV,
    # Lambda=2 keV). Use a representative CM velocity v=0.6.
    ok1 = run_check(mQ_gev=1800.0, Lambda_gev=2e-6, v=0.6, label="mQ=1.8 TeV benchmark")
    ok2 = run_check(mQ_gev=800.0, Lambda_gev=4e-6, v=0.4, label="mQ=800 GeV benchmark")
    ok3 = run_check(mQ_gev=1800.0, Lambda_gev=2e-6, v=0.95, label="mQ=1.8 TeV, highly relativistic")

    print()
    print("ALL PASS:", ok1 and ok2 and ok3)
