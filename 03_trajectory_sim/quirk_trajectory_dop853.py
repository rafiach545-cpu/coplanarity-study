"""
Error-controlled DOP853 integrator for Eq. 3 (arXiv:1708.02243), numba (2026-11-22, 09/G09).

Same equations of motion as quirk_trajectory_numba (its _rhs is called unchanged). The stepper is a numba port of scipy's DOP853
(scipy.integrate._ivp.rk.DOP853: Hairer's coefficients from dop853_coefficients, stored in quirk_dop853_coefficients.npz, error norm with the 5th/3rd-order estimators,
SAFETY = 0.9, factor in [0.2, 10], initial step from select_initial_step, 7th-order dense output), so it can be checked against
scipy.solve_ivp(method="DOP853") directly.

Output for the hit code: the trajectory is written at every accepted step and, inside every step, at NCOARSE dense-output points;
every coarse sub-interval in which r(t) of either quirk crosses one of the given layer radii is filled with NFINE further dense points,
so that the linear interpolation of the existing crossing code (trajectory_to_hits.find_layer_crossing, P18 all_crossings) is exact to
(h / (NCOARSE * NFINE))^2. Points are kept only where needed (crossing brackets, step ends): between two kept points no layer is
crossed, so the crossing code finds the same crossings as on the full output.

Drop-in: integrate_trajectory_dop853(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2, Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv, ...)
with the signature of integrate_trajectory_numba (dt_gev_inv is not used for the step; only as a fallback first step bound is unused).
Tolerances (module variables, natural units): RTOL, ATOL_X (GeV^-1), ATOL_P (GeV); RADII_CM and T_STOP_NS are set by the caller.
"""
import math
import numpy as np
from numba import njit
import os as _os
from quirk_trajectory_numba import _rhs, TESLA_TO_GEV2
from quirk_trajectory import _validate_integration_inputs

CM = 1.973269804e-14; NS = 6.582119569e-16
# coefficients: scipy's dop853_coefficients, saved to quirk_dop853_coefficients.npz (scipy 1.18.0) so that envs without scipy (g4) use the
# same numbers; where scipy exists they are checked against it at import
_DC = np.load(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "quirk_dop853_coefficients.npz"))
try:
    from scipy.integrate._ivp import dop853_coefficients as _S
    for _k in ("A", "B", "C", "E3", "E5", "D"): assert np.array_equal(_DC[_k], getattr(_S, _k)), _k
except ImportError:
    pass
NST = int(_DC["N_STAGES"]); NEXT = int(_DC["N_STAGES_EXTENDED"]); NPOW = int(_DC["INTERPOLATOR_POWER"])
A_ = np.ascontiguousarray(_DC["A"], dtype=np.float64); B_ = np.ascontiguousarray(_DC["B"], dtype=np.float64); C_ = np.ascontiguousarray(_DC["C"], dtype=np.float64)
E3_ = np.ascontiguousarray(_DC["E3"], dtype=np.float64); E5_ = np.ascontiguousarray(_DC["E5"], dtype=np.float64); D_ = np.ascontiguousarray(_DC["D"], dtype=np.float64)

RTOL = 1e-10
ATOL_X = 1e-7 / CM          # 1 nm
ATOL_P = 1e-10              # GeV
NCOARSE = 8; NFINE = 64
RADII_CM = None             # layer radii (cm) for the crossing refinement; None: no refinement (step ends and coarse points only)
ZPLANES_CM = None           # z positions (cm) of disk planes (07 ATLAS end caps), refined like the radii
T_STOP_NS = None            # stop integration here (None: t_max)
STATS = {}


@njit(cache=True)
def _f(y, mass, q1, q2, L2, Bz, out):
    _rhs(y, mass, q1, q2, L2, Bz, out)


@njit(cache=True)
def _dense(F, y_old, x, out):
    for j in range(12): out[j] = 0.0
    for i in range(NPOW):
        f = F[NPOW - 1 - i]
        for j in range(12): out[j] += f[j]
        if i % 2 == 0:
            for j in range(12): out[j] *= x
        else:
            for j in range(12): out[j] *= (1.0 - x)
    for j in range(12): out[j] += y_old[j]


@njit(cache=True)
def _rr(y, R2n, Zn):
    """signs of r - R (R2n: squared radii) and of z - z_d (Zn: disk planes) for both quirks"""
    r1 = y[0] * y[0] + y[1] * y[1]; r2 = y[6] * y[6] + y[7] * y[7]; nr = len(R2n); nz = len(Zn)
    s = np.empty(2 * (nr + nz), dtype=np.int8)
    for k in range(nr):
        s[k] = 1 if r1 > R2n[k] else (-1 if r1 < R2n[k] else 0)
        s[nr + k] = 1 if r2 > R2n[k] else (-1 if r2 < R2n[k] else 0)
    for k in range(nz):
        s[2 * nr + k] = 1 if y[2] > Zn[k] else (-1 if y[2] < Zn[k] else 0)
        s[2 * nr + nz + k] = 1 if y[8] > Zn[k] else (-1 if y[8] < Zn[k] else 0)
    return s


@njit(cache=True)
def _integrate(y0, t_end, mass, q1, q2, L2, Bz, rtol, atol, R2n, Zn, ncoarse, nfine, max_out, A, B, C, E3, E5, D):
    n = 12
    T = np.empty(max_out); Y = np.empty((max_out, 12)); m = 0
    y = y0.copy(); t = 0.0
    K = np.zeros((NEXT, n)); f = np.empty(n); tmp = np.empty(n); fnew = np.empty(n)
    _f(y, mass, q1, q2, L2, Bz, f)
    # initial step (scipy select_initial_step, order = error_estimator_order = 7)
    sc = np.empty(n)
    for j in range(n): sc[j] = atol[j] + abs(y[j]) * rtol
    d0 = 0.0; d1 = 0.0
    for j in range(n): d0 += (y[j] / sc[j]) ** 2; d1 += (f[j] / sc[j]) ** 2
    d0 = math.sqrt(d0 / n); d1 = math.sqrt(d1 / n)
    h0 = 1e-6 if (d0 < 1e-5 or d1 < 1e-5) else 0.01 * d0 / d1
    h0 = min(h0, t_end)
    for j in range(n): tmp[j] = y[j] + h0 * f[j]
    _f(tmp, mass, q1, q2, L2, Bz, fnew)
    d2 = 0.0
    for j in range(n): d2 += ((fnew[j] - f[j]) / sc[j]) ** 2
    d2 = math.sqrt(d2 / n) / h0
    h1 = max(1e-6, h0 * 1e-3) if (d1 <= 1e-15 and d2 <= 1e-15) else (0.01 / max(d1, d2)) ** (1.0 / 8.0)
    h_abs = min(100 * h0, h1, t_end)
    T[0] = t; Y[0, :] = y[:]; m = 1
    nacc = 0; nrej = 0; nfev = 2
    F = np.zeros((NPOW, n)); ynew = np.empty(n); yd = np.empty(n); yd2 = np.empty(n)
    while t < t_end:
        min_step = 10 * abs(np.nextafter(t, np.inf) - t)
        if h_abs < min_step: h_abs = min_step
        rejected = False
        while True:
            if h_abs < min_step: return T[:m], Y[:m], -1, nacc, nrej, nfev
            t_new = t + h_abs
            if t_new > t_end: t_new = t_end
            h = t_new - t; h_abs = abs(h)
            # rk_step
            for j in range(n): K[0, j] = f[j]
            for s in range(1, NST):
                for j in range(n):
                    acc = 0.0
                    for i in range(s): acc += K[i, j] * A[s, i]
                    tmp[j] = y[j] + acc * h
                _f(tmp, mass, q1, q2, L2, Bz, K[s]); nfev += 1
            for j in range(n):
                acc = 0.0
                for i in range(NST): acc += K[i, j] * B[i]
                ynew[j] = y[j] + h * acc
            _f(ynew, mass, q1, q2, L2, Bz, fnew); nfev += 1
            for j in range(n): K[NST, j] = fnew[j]
            # error norm (scipy DOP853._estimate_error_norm)
            e5 = 0.0; e3 = 0.0
            for j in range(n):
                scj = atol[j] + max(abs(y[j]), abs(ynew[j])) * rtol
                a5 = 0.0; a3 = 0.0
                for i in range(NST + 1): a5 += K[i, j] * E5[i]; a3 += K[i, j] * E3[i]
                e5 += (a5 / scj) ** 2; e3 += (a3 / scj) ** 2
            if e5 == 0.0 and e3 == 0.0: err = 0.0
            else: err = abs(h) * e5 / math.sqrt((e5 + 0.01 * e3) * n)
            if err < 1:
                factor = 10.0 if err == 0 else min(10.0, 0.9 * err ** (-1.0 / 8.0))
                if rejected: factor = min(1.0, factor)
                h_abs *= factor; break
            h_abs *= max(0.2, 0.9 * err ** (-1.0 / 8.0)); rejected = True; nrej += 1
        nacc += 1
        # dense output (scipy DOP853._dense_output_impl)
        for s in range(NST + 1, NEXT):
            for j in range(n):
                acc = 0.0
                for i in range(s): acc += K[i, j] * A[s, i]
                tmp[j] = y[j] + acc * h
            _f(tmp, mass, q1, q2, L2, Bz, K[s]); nfev += 1
        for j in range(n):
            dy = ynew[j] - y[j]; F[0, j] = dy; F[1, j] = h * K[0, j] - dy; F[2, j] = 2 * dy - h * (fnew[j] + K[0, j])
            for r in range(NPOW - 3):
                acc = 0.0
                for i in range(NEXT): acc += D[r, i] * K[i, j]
                F[3 + r, j] = h * acc
        # output: coarse points, refined where a radius is crossed
        if len(R2n) + len(Zn) > 0:
            sprev = _rr(y, R2n, Zn); xprev = 0.0
            for c in range(1, ncoarse + 1):
                xc = c / ncoarse
                if c == ncoarse:
                    for j in range(n): yd[j] = ynew[j]
                else: _dense(F, y, xc, yd)
                sc_ = _rr(yd, R2n, Zn); cross = False
                for k in range(len(sc_)):
                    if sc_[k] != sprev[k]: cross = True
                if cross:
                    for q in range(0, nfine + 1):                 # q = 0: the start of the sub-interval, so the bracket is short
                        xq = xprev + (xc - xprev) * q / nfine
                        if q == 0 and xprev == 0.0: continue         # the step start is already written
                        _dense(F, y, xq, yd2)
                        tq = t + xq * h
                        if m >= max_out: return T[:m], Y[:m], -2, nacc, nrej, nfev
                        if T[m - 1] == tq: continue
                        T[m] = tq; Y[m, :] = yd2[:]; m += 1
                sprev = sc_; xprev = xc
        else:                                                    # no radii (validation): every coarse dense point is written
            for c in range(1, ncoarse):
                _dense(F, y, c / ncoarse, yd)
                if m >= max_out: return T[:m], Y[:m], -2, nacc, nrej, nfev
                T[m] = t + c / ncoarse * h; Y[m, :] = yd[:]; m += 1
        if m >= max_out: return T[:m], Y[:m], -2, nacc, nrej, nfev
        if T[m - 1] != t_new:
            T[m] = t_new; Y[m, :] = ynew[:]; m += 1
        else:                                                    # the last fine point is the step end: use the step's own value
            Y[m - 1, :] = ynew[:]
        for j in range(n): y[j] = ynew[j]; f[j] = fnew[j]
        t = t_new
    return T[:m], Y[:m], 0, nacc, nrej, nfev


def integrate_trajectory_dop853(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2, Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv=None,
                                e_charge_natural=0.30282212, rtol=None, max_out=20_000_000):
    """Drop-in for integrate_trajectory_numba: returns t, x1, p1, x2, p2 at the written points."""
    _validate_integration_inputs(x1_0, p1_0, x2_0, p2_0, mass, Lambda_GeV, t_max_gev_inv, dt_gev_inv if dt_gev_inv else t_max_gev_inv / 10)
    rt = RTOL if rtol is None else rtol
    y0 = np.array([*map(float, x1_0), *map(float, p1_0), *map(float, x2_0), *map(float, p2_0)])
    atol = np.array([ATOL_X] * 3 + [ATOL_P] * 3 + [ATOL_X] * 3 + [ATOL_P] * 3)
    t_end = t_max_gev_inv if T_STOP_NS is None else min(t_max_gev_inv, T_STOP_NS / NS)
    R2n = np.array([(r / CM) ** 2 for r in (RADII_CM or [])], dtype=np.float64)
    Zn = np.array([z / CM for z in (ZPLANES_CM or [])], dtype=np.float64)
    T, Y, status, nacc, nrej, nfev = _integrate(y0, float(t_end), float(mass), charge1 * e_charge_natural, charge2 * e_charge_natural, Lambda_GeV ** 2,
                                                B_tesla * TESLA_TO_GEV2, float(rt), atol, R2n, Zn, NCOARSE, NFINE, max_out, A_, B_, C_, E3_, E5_, D_)
    if status == -1: raise RuntimeError("DOP853: step size too small")
    if status == -2: raise RuntimeError(f"DOP853: more than {max_out} output points")
    if not np.all(np.isfinite(Y)): raise RuntimeError("DOP853: non-finite state")
    STATS.update(n_accepted=nacc, n_rejected=nrej, nfev=nfev, n_out=len(T))
    return {"t_gev_inv": T, "x1": Y[:, 0:3], "p1": Y[:, 3:6], "x2": Y[:, 6:9], "p2": Y[:, 9:12]}
