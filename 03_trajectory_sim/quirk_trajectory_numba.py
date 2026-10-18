"""
RK4 trajectory integrator, numba-compiled copy of quirk_trajectory_optimized_v2 (2026-10-17).

Same physics, same algorithm and the same order of floating-point operations as integrate_trajectory_fast_v2 (no fastmath, no reassociation);
only the loop is compiled. Drop-in compatible (same signature and return dict). Validated against v2 by
05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts/F6_06_validate_numba.py before any use.
"""
import sys
import math
import numpy as np
from numba import njit

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))   # this file's directory (2026-10-17)
from quirk_trajectory import _validate_integration_inputs

TESLA_TO_GEV2 = 1.9535e-16


@njit(cache=True)
def _string_force(vx, vy, vz, nx, ny, nz, Lambda2):
    vpar = vx*nx + vy*ny + vz*nz
    vparx, vpary, vparz = vpar*nx, vpar*ny, vpar*nz
    vperpx, vperpy, vperpz = vx - vparx, vy - vpary, vz - vparz
    vperp2 = vperpx*vperpx + vperpy*vperpy + vperpz*vperpz
    st = math.sqrt(max(1.0 - vperp2, 1e-12))
    t1x, t1y, t1z = st*nx, st*ny, st*nz
    coef = vpar / st
    t2x, t2y, t2z = coef*vperpx, coef*vperpy, coef*vperpz
    return -Lambda2*(t1x+t2x), -Lambda2*(t1y+t2y), -Lambda2*(t1z+t2z)


@njit(cache=True)
def _rhs(s, mass, q1, q2, Lambda2, Bz, out):
    x1x, x1y, x1z, p1x, p1y, p1z, x2x, x2y, x2z, p2x, p2y, p2z = s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10], s[11]
    m2 = mass * mass
    E1 = math.sqrt(p1x*p1x + p1y*p1y + p1z*p1z + m2)
    E2 = math.sqrt(p2x*p2x + p2y*p2y + p2z*p2z + m2)
    v1x, v1y, v1z = p1x/E1, p1y/E1, p1z/E1
    v2x, v2y, v2z = p2x/E2, p2y/E2, p2z/E2
    sepx, sepy, sepz = x1x - x2x, x1y - x2y, x1z - x2z
    dist = math.sqrt(sepx*sepx + sepy*sepy + sepz*sepz)
    if dist < 1e-9:
        vrx, vry, vrz = v1x - v2x, v1y - v2y, v1z - v2z
        vrn = math.sqrt(vrx*vrx + vry*vry + vrz*vrz)
        if vrn > 1e-12:
            n1x, n1y, n1z = vrx/vrn, vry/vrn, vrz/vrn
        else:
            n1x, n1y, n1z = 1.0, 0.0, 0.0
    else:
        n1x, n1y, n1z = sepx/dist, sepy/dist, sepz/dist
    n2x, n2y, n2z = -n1x, -n1y, -n1z
    F1x, F1y, F1z = _string_force(v1x, v1y, v1z, n1x, n1y, n1z, Lambda2)
    F1x += q1 * Bz * v1y
    F1y += -q1 * Bz * v1x
    F2x, F2y, F2z = _string_force(v2x, v2y, v2z, n2x, n2y, n2z, Lambda2)
    F2x += q2 * Bz * v2y
    F2y += -q2 * Bz * v2x
    out[0], out[1], out[2], out[3], out[4], out[5] = v1x, v1y, v1z, F1x, F1y, F1z
    out[6], out[7], out[8], out[9], out[10], out[11] = v2x, v2y, v2z, F2x, F2y, F2z


@njit(cache=True)
def _integrate(state0, mass, q1, q2, Lambda2, Bz, t_max, dt, n_steps):
    ts = np.zeros(n_steps + 1)
    S = np.zeros((n_steps + 1, 12))
    S[0] = state0
    state = state0.copy()
    k1 = np.empty(12); k2 = np.empty(12); k3 = np.empty(12); k4 = np.empty(12); tmp = np.empty(12)
    t = 0.0
    for i in range(1, n_steps + 1):
        step = dt if i < n_steps else (t_max - t)
        _rhs(state, mass, q1, q2, Lambda2, Bz, k1)
        for j in range(12): tmp[j] = state[j] + 0.5*step*k1[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k2)
        for j in range(12): tmp[j] = state[j] + 0.5*step*k2[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k3)
        for j in range(12): tmp[j] = state[j] + step*k3[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k4)
        for j in range(12): state[j] = state[j] + (step/6.0)*(k1[j] + 2*k2[j] + 2*k3[j] + k4[j])
        t += step
        for j in range(12):
            if not math.isfinite(state[j]):
                return ts, S, i, t, step
        ts[i] = t
        S[i] = state
    return ts, S, -1, t, dt


def integrate_trajectory_numba(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2,
                               Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv,
                               e_charge_natural=0.30282212):
    """Drop-in-compatible with quirk_trajectory.integrate_trajectory and integrate_trajectory_fast_v2."""
    _validate_integration_inputs(x1_0, p1_0, x2_0, p2_0, mass, Lambda_GeV, t_max_gev_inv, dt_gev_inv)
    Bz = B_tesla * TESLA_TO_GEV2
    Lambda2 = Lambda_GeV ** 2
    q1 = charge1 * e_charge_natural
    q2 = charge2 * e_charge_natural
    n_steps = int(math.ceil(t_max_gev_inv / dt_gev_inv))
    s0 = np.array([float(x1_0[0]), float(x1_0[1]), float(x1_0[2]), float(p1_0[0]), float(p1_0[1]), float(p1_0[2]),
                   float(x2_0[0]), float(x2_0[1]), float(x2_0[2]), float(p2_0[0]), float(p2_0[1]), float(p2_0[2])])
    ts, S, bad, t, step = _integrate(s0, float(mass), float(q1), float(q2), float(Lambda2), float(Bz), float(t_max_gev_inv), float(dt_gev_inv), n_steps)
    if bad >= 0:
        raise RuntimeError(f"integrate_trajectory_fast_v2: non-finite state at step {bad}/{n_steps} "
                           f"(t={t:.3e} GeV^-1, dt={step:.3e} GeV^-1) -- integration diverged.")
    # views into one (n, 12) array: same values as v2's separate arrays, half the memory (long high-Lambda trajectories reach ~2e7 steps)
    return {"t_gev_inv": ts, "x1": S[:, 0:3], "p1": S[:, 3:6], "x2": S[:, 6:9], "p2": S[:, 9:12]}


# ---------------------------------------------------------------- positions-only variant (2026-10-18)
# Same stepping as _integrate (identical state evolution); stores only t and the two positions, not the momenta, which the hit/crossing code never
# reads. Memory: 7 doubles per step instead of 13 (about 1.1 GB instead of 2.1 GB at 20 million steps). p1/p2 are returned as empty (0, 3) arrays so
# that any code which did read them would fail loudly instead of silently using wrong values.
@njit(cache=True)
def _integrate_x(state0, mass, q1, q2, Lambda2, Bz, t_max, dt, n_steps):
    ts = np.zeros(n_steps + 1)
    X = np.zeros((n_steps + 1, 6))
    X[0, 0:3] = state0[0:3]; X[0, 3:6] = state0[6:9]
    state = state0.copy()
    k1 = np.empty(12); k2 = np.empty(12); k3 = np.empty(12); k4 = np.empty(12); tmp = np.empty(12)
    t = 0.0
    for i in range(1, n_steps + 1):
        step = dt if i < n_steps else (t_max - t)
        _rhs(state, mass, q1, q2, Lambda2, Bz, k1)
        for j in range(12): tmp[j] = state[j] + 0.5*step*k1[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k2)
        for j in range(12): tmp[j] = state[j] + 0.5*step*k2[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k3)
        for j in range(12): tmp[j] = state[j] + step*k3[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k4)
        for j in range(12): state[j] = state[j] + (step/6.0)*(k1[j] + 2*k2[j] + 2*k3[j] + k4[j])
        t += step
        for j in range(12):
            if not math.isfinite(state[j]):
                return ts, X, i, t, step
        ts[i] = t
        X[i, 0] = state[0]; X[i, 1] = state[1]; X[i, 2] = state[2]; X[i, 3] = state[6]; X[i, 4] = state[7]; X[i, 5] = state[8]
    return ts, X, -1, t, dt


def integrate_trajectory_numba_xonly(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2,
                                     Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv,
                                     e_charge_natural=0.30282212):
    """As integrate_trajectory_numba, but returns only t, x1, x2 (p1, p2 empty). For the hit/crossing pipeline, which never reads the momenta."""
    _validate_integration_inputs(x1_0, p1_0, x2_0, p2_0, mass, Lambda_GeV, t_max_gev_inv, dt_gev_inv)
    Bz = B_tesla * TESLA_TO_GEV2
    Lambda2 = Lambda_GeV ** 2
    q1 = charge1 * e_charge_natural
    q2 = charge2 * e_charge_natural
    n_steps = int(math.ceil(t_max_gev_inv / dt_gev_inv))
    s0 = np.array([float(x1_0[0]), float(x1_0[1]), float(x1_0[2]), float(p1_0[0]), float(p1_0[1]), float(p1_0[2]),
                   float(x2_0[0]), float(x2_0[1]), float(x2_0[2]), float(p2_0[0]), float(p2_0[1]), float(p2_0[2])])
    ts, X, bad, t, step = _integrate_x(s0, float(mass), float(q1), float(q2), float(Lambda2), float(Bz), float(t_max_gev_inv), float(dt_gev_inv), n_steps)
    if bad >= 0:
        raise RuntimeError(f"integrate_trajectory_fast_v2: non-finite state at step {bad}/{n_steps} "
                           f"(t={t:.3e} GeV^-1, dt={step:.3e} GeV^-1) -- integration diverged.")
    return {"t_gev_inv": ts, "x1": X[:, 0:3], "p1": np.empty((0, 3)), "x2": X[:, 3:6], "p2": np.empty((0, 3))}
