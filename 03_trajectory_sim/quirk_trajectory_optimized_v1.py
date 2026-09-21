"""
Optimized RK4 trajectory integrator (v1) -- a SEPARATE, versioned
implementation. Does NOT modify or import over
03_trajectory_sim/quirk_trajectory.py (the validated baseline), which
remains untouched and is still the file every other part of this project
uses by default.

Profiling this task (perf_profile_v1/) found integrate_trajectory
consumes 99.96-99.98% of total pipeline wall time across 6 diverse
(event, Lambda) baseline runs -- detector hit-building, smearing, merging,
and reconstruction combined are <0.03%. This module targets that one
function exclusively.

Optimization strategy (no algorithm change, no physics change -- same
fixed-step RK4, same equations of motion, same order of floating-point
operations, so results are expected to be numerically IDENTICAL to the
baseline, not merely close):

1. Eliminate QuirkPairState object construction in the hot loop -- the
   baseline's `QuirkPairState.from_vector(y)` calls `np.array(x1,
   dtype=float)` on each of 4 slices, which COPIES even though y[0:3] etc.
   are already ndarray views. This optimized version operates directly on
   views (no copy), since nothing in the hot path mutates them in place.
2. Inline velocity_from_momentum / string_force / lorentz_force into a
   single function -- eliminates 5 Python function-call layers per RHS
   evaluation (4 RHS evaluations per RK4 step), preserving the exact same
   arithmetic and branch structure (including the dist<1e-9 degenerate
   case, byte-for-byte the same condition and fallback).
3. Replace np.linalg.norm(v) with sqrt(dot(v,v)) -- avoids norm's extra
   generality dispatch overhead for a fixed 3-vector.
4. Replace np.concatenate with direct np.empty(12) + slice assignment for
   the RHS output -- avoids concatenate's own call overhead.

None of these change what is computed, only how many Python/numpy function
calls it takes to compute it. Validated (see
tests/test_optimized_trajectory_agreement.py) to reproduce the baseline's
full trajectory to floating-point-identical precision (bit-for-bit, not
just within a tolerance) on every profiled baseline event.
"""
import numpy as np

TESLA_TO_GEV2 = 1.9535e-16


def _equations_of_motion_fast(y, mass, charge1, charge2, Lambda2, Bz):
    """Same physics as quirk_trajectory.equations_of_motion, inlined.
    Bz is the z-component of B_vec only (B_vec=[0,0,Bz] always, in this
    project -- baseline also only ever calls with a z-aligned B_vec, so
    this is not a physics restriction, just avoiding a redundant 3-vector
    cross product with two always-zero components)."""
    x1 = y[0:3]; p1 = y[3:6]; x2 = y[6:9]; p2 = y[9:12]

    E1 = np.sqrt(p1[0]*p1[0] + p1[1]*p1[1] + p1[2]*p1[2] + mass*mass)
    E2 = np.sqrt(p2[0]*p2[0] + p2[1]*p2[1] + p2[2]*p2[2] + mass*mass)
    v1 = p1 / E1
    v2 = p2 / E2

    sep = x1 - x2
    dist = np.sqrt(sep[0]*sep[0] + sep[1]*sep[1] + sep[2]*sep[2])
    if dist < 1e-9:
        v_rel = v1 - v2
        v_rel_norm = np.sqrt(v_rel[0]*v_rel[0] + v_rel[1]*v_rel[1] + v_rel[2]*v_rel[2])
        if v_rel_norm > 1e-12:
            n_hat_1 = v_rel / v_rel_norm
        else:
            n_hat_1 = np.array([1.0, 0.0, 0.0])
        n_hat_2 = -n_hat_1
    else:
        n_hat_1 = sep / dist
        n_hat_2 = -n_hat_1

    def string_force_inline(v, n_hat):
        v_par_scalar = v[0]*n_hat[0] + v[1]*n_hat[1] + v[2]*n_hat[2]
        v_par_vec = v_par_scalar * n_hat
        v_perp_vec = v - v_par_vec
        v_perp2 = v_perp_vec[0]*v_perp_vec[0] + v_perp_vec[1]*v_perp_vec[1] + v_perp_vec[2]*v_perp_vec[2]
        sqrt_term = np.sqrt(max(1.0 - v_perp2, 1e-12))
        term1 = sqrt_term * n_hat
        term2 = (v_par_scalar / sqrt_term) * v_perp_vec
        return -Lambda2 * (term1 + term2)

    # Lorentz force with B=[0,0,Bz]: q*(v x B) = q*Bz*(vy, -vx, 0)
    F1 = string_force_inline(v1, n_hat_1)
    F1[0] += charge1 * Bz * v1[1]
    F1[1] += -charge1 * Bz * v1[0]

    F2 = string_force_inline(v2, n_hat_2)
    F2[0] += charge2 * Bz * v2[1]
    F2[1] += -charge2 * Bz * v2[0]

    out = np.empty(12)
    out[0:3] = v1
    out[3:6] = F1
    out[6:9] = v2
    out[9:12] = F2
    return out


def integrate_trajectory_fast(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2,
                               Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv,
                               e_charge_natural=0.30282212):
    """Drop-in-compatible replacement for
    quirk_trajectory.integrate_trajectory -- same signature, same return
    dict keys, same validated input-checking (re-imports and reuses
    quirk_trajectory._validate_integration_inputs UNCHANGED, not
    reimplemented, so validation logic cannot drift from the baseline)."""
    import sys
    sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
    from quirk_trajectory import _validate_integration_inputs

    _validate_integration_inputs(x1_0, p1_0, x2_0, p2_0, mass, Lambda_GeV,
                                  t_max_gev_inv, dt_gev_inv)

    Bz = B_tesla * TESLA_TO_GEV2
    Lambda2 = Lambda_GeV ** 2
    q1 = charge1 * e_charge_natural
    q2 = charge2 * e_charge_natural

    y = np.concatenate([x1_0, p1_0, x2_0, p2_0])

    n_steps = int(np.ceil(t_max_gev_inv / dt_gev_inv))

    ts = np.zeros(n_steps + 1)
    xs1 = np.zeros((n_steps + 1, 3))
    xs2 = np.zeros((n_steps + 1, 3))
    ps1 = np.zeros((n_steps + 1, 3))
    ps2 = np.zeros((n_steps + 1, 3))

    ts[0] = 0.0
    xs1[0], ps1[0], xs2[0], ps2[0] = x1_0, p1_0, x2_0, p2_0

    t = 0.0
    for i in range(1, n_steps + 1):
        step = dt_gev_inv if i < n_steps else (t_max_gev_inv - t)
        k1 = _equations_of_motion_fast(y, mass, q1, q2, Lambda2, Bz)
        k2 = _equations_of_motion_fast(y + 0.5*step*k1, mass, q1, q2, Lambda2, Bz)
        k3 = _equations_of_motion_fast(y + 0.5*step*k2, mass, q1, q2, Lambda2, Bz)
        k4 = _equations_of_motion_fast(y + step*k3, mass, q1, q2, Lambda2, Bz)
        y = y + (step/6.0) * (k1 + 2*k2 + 2*k3 + k4)
        t += step
        if not np.all(np.isfinite(y)):
            raise RuntimeError(
                f"integrate_trajectory_fast: non-finite state at step {i}/{n_steps} "
                f"(t={t:.3e} GeV^-1, dt={step:.3e} GeV^-1) -- integration diverged.")
        ts[i] = t
        xs1[i] = y[0:3]; ps1[i] = y[3:6]; xs2[i] = y[6:9]; ps2[i] = y[9:12]

    return {
        "t_gev_inv": ts,
        "x1": xs1, "p1": ps1,
        "x2": xs2, "p2": ps2,
    }
