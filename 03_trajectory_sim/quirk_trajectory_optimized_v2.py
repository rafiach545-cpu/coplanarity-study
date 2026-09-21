"""
Optimized RK4 trajectory integrator (v2) -- pure-Python-float variant.

v1 (quirk_trajectory_optimized_v1.py) eliminated object-construction and
function-call overhead but still used numpy arrays/scalar indexing for the
per-step 3-vector math. For arrays this small (3-12 elements), numpy's
per-call dispatch overhead exceeds the cost of the actual arithmetic --
plain Python floats (which are the same IEEE-754 double precision as
numpy float64, so identical arithmetic results) avoid that dispatch
entirely. This version unpacks the 12-dim state into 12 individual Python
floats for the RK4 stepping loop and does all per-step arithmetic in pure
Python, only touching numpy for the input/output array packaging at the
loop boundary.

Same physics, same algorithm, same order of floating-point operations as
the baseline -- validated to reproduce it bit-for-bit (see
tests/test_optimized_trajectory_agreement.py).
"""
import sys
import math
import numpy as np

sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
from quirk_trajectory import _validate_integration_inputs

TESLA_TO_GEV2 = 1.9535e-16


def _rhs(x1x, x1y, x1z, p1x, p1y, p1z, x2x, x2y, x2z, p2x, p2y, p2z,
         mass, q1, q2, Lambda2, Bz):
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

    def string_force(vx, vy, vz, nx, ny, nz):
        vpar = vx*nx + vy*ny + vz*nz
        vparx, vpary, vparz = vpar*nx, vpar*ny, vpar*nz
        vperpx, vperpy, vperpz = vx - vparx, vy - vpary, vz - vparz
        vperp2 = vperpx*vperpx + vperpy*vperpy + vperpz*vperpz
        st = math.sqrt(max(1.0 - vperp2, 1e-12))
        t1x, t1y, t1z = st*nx, st*ny, st*nz
        coef = vpar / st
        t2x, t2y, t2z = coef*vperpx, coef*vperpy, coef*vperpz
        return -Lambda2*(t1x+t2x), -Lambda2*(t1y+t2y), -Lambda2*(t1z+t2z)

    F1x, F1y, F1z = string_force(v1x, v1y, v1z, n1x, n1y, n1z)
    F1x += q1 * Bz * v1y
    F1y += -q1 * Bz * v1x

    F2x, F2y, F2z = string_force(v2x, v2y, v2z, n2x, n2y, n2z)
    F2x += q2 * Bz * v2y
    F2y += -q2 * Bz * v2x

    return v1x, v1y, v1z, F1x, F1y, F1z, v2x, v2y, v2z, F2x, F2y, F2z


def integrate_trajectory_fast_v2(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2,
                                  Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv,
                                  e_charge_natural=0.30282212):
    """Drop-in-compatible with quirk_trajectory.integrate_trajectory."""
    _validate_integration_inputs(x1_0, p1_0, x2_0, p2_0, mass, Lambda_GeV,
                                  t_max_gev_inv, dt_gev_inv)

    Bz = B_tesla * TESLA_TO_GEV2
    Lambda2 = Lambda_GeV ** 2
    q1 = charge1 * e_charge_natural
    q2 = charge2 * e_charge_natural

    n_steps = int(math.ceil(t_max_gev_inv / dt_gev_inv))

    ts = np.zeros(n_steps + 1)
    xs1 = np.zeros((n_steps + 1, 3))
    xs2 = np.zeros((n_steps + 1, 3))
    ps1 = np.zeros((n_steps + 1, 3))
    ps2 = np.zeros((n_steps + 1, 3))

    ts[0] = 0.0
    xs1[0], ps1[0], xs2[0], ps2[0] = x1_0, p1_0, x2_0, p2_0

    state = (float(x1_0[0]), float(x1_0[1]), float(x1_0[2]),
             float(p1_0[0]), float(p1_0[1]), float(p1_0[2]),
             float(x2_0[0]), float(x2_0[1]), float(x2_0[2]),
             float(p2_0[0]), float(p2_0[1]), float(p2_0[2]))

    t = 0.0
    for i in range(1, n_steps + 1):
        step = dt_gev_inv if i < n_steps else (t_max_gev_inv - t)
        k1 = _rhs(*state, mass, q1, q2, Lambda2, Bz)
        s2 = tuple(state[j] + 0.5*step*k1[j] for j in range(12))
        k2 = _rhs(*s2, mass, q1, q2, Lambda2, Bz)
        s3 = tuple(state[j] + 0.5*step*k2[j] for j in range(12))
        k3 = _rhs(*s3, mass, q1, q2, Lambda2, Bz)
        s4 = tuple(state[j] + step*k3[j] for j in range(12))
        k4 = _rhs(*s4, mass, q1, q2, Lambda2, Bz)
        state = tuple(state[j] + (step/6.0)*(k1[j] + 2*k2[j] + 2*k3[j] + k4[j]) for j in range(12))
        t += step
        if not all(math.isfinite(v) for v in state):
            raise RuntimeError(
                f"integrate_trajectory_fast_v2: non-finite state at step {i}/{n_steps} "
                f"(t={t:.3e} GeV^-1, dt={step:.3e} GeV^-1) -- integration diverged.")
        ts[i] = t
        xs1[i] = state[0:3]; ps1[i] = state[3:6]; xs2[i] = state[6:9]; ps2[i] = state[9:12]

    return {
        "t_gev_inv": ts,
        "x1": xs1, "p1": ps1,
        "x2": xs2, "p2": ps2,
    }
