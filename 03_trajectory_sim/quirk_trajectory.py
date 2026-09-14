"""
Classical trajectory integration for a quirk/anti-quirk pair.

Implements Eq. 3 of Knapen, Lou, Papucci, Setford, "Tracking down Quirks at the
Large Hadron Collider," arXiv:1708.02243v2:

    d/dt (m*gamma*v) = -Lambda^2 * ( sqrt(1-v_perp^2)/v_par * v_par_vec
                                      + v_par/sqrt(1-v_perp^2) * v_perp_vec )
                        + F_ext

for each quirk, where v_par_vec/v_perp_vec are the components of that quirk's
velocity parallel/perpendicular to the line joining the two quirks (the
string direction), v_par = |v_par_vec|, v_perp = |v_perp_vec|, and F_ext is
the Lorentz force from a uniform magnetic field B = 2 T along z (paper's
choice). Natural units (c = 1); momentum/energy in GeV, length in GeV^-1
converted to cm via hbar*c, time in GeV^-1 converted to seconds/ns as needed.

This module ONLY integrates the classical two-body trajectory. It does not
touch the detector or the plane-finding algorithm (Stages 2 and 5).
"""

import numpy as np

# ---- unit conversions (natural units GeV, c=hbar=1, converted to SI/cgs) ----
HBARC_GEV_CM = 1.973269804e-14   # hbar*c in GeV*cm  -> 1 GeV^-1 = this many cm
HBARC_GEV_S = 6.582119569e-25    # hbar in GeV*s     -> 1 GeV^-1 = this many s
C_LIGHT_CM_S = 2.99792458e10     # speed of light, cm/s


def gev_to_cm(x_gev_inv):
    return x_gev_inv * HBARC_GEV_CM


def cm_to_gev_inv(x_cm):
    return x_cm / HBARC_GEV_CM


def gev_to_s(t_gev_inv):
    return t_gev_inv * HBARC_GEV_S


def s_to_gev_inv(t_s):
    return t_s / HBARC_GEV_S


class QuirkPairState:
    """
    State of the quirk/anti-quirk system in the lab frame.

    Positions in GeV^-1 (natural units), momenta in GeV, time in GeV^-1.
    x1, x2: (3,) arrays, position of quirk 1 and quirk 2.
    p1, p2: (3,) arrays, relativistic 3-momentum of quirk 1 and quirk 2.
    """
    __slots__ = ("x1", "p1", "x2", "p2")

    def __init__(self, x1, p1, x2, p2):
        self.x1 = np.array(x1, dtype=float)
        self.p1 = np.array(p1, dtype=float)
        self.x2 = np.array(x2, dtype=float)
        self.p2 = np.array(p2, dtype=float)

    def as_vector(self):
        return np.concatenate([self.x1, self.p1, self.x2, self.p2])

    @staticmethod
    def from_vector(y):
        return QuirkPairState(y[0:3], y[3:6], y[6:9], y[9:12])


def velocity_from_momentum(p, mass):
    """v = p / E,  E = sqrt(|p|^2 + m^2).  Natural units, c=1."""
    E = np.sqrt(np.dot(p, p) + mass ** 2)
    return p / E, E


def string_force(v, n_hat, Lambda2):
    """
    Nambu-Goto confining-string force on ONE quirk (Eq. 3 RHS, string term
    only), given that quirk's velocity v and the unit vector n_hat pointing
    AWAY from the other quirk, i.e. outward along this quirk's own
    displacement from its partner (the "parallel" direction) -- so that
    -Lambda^2 * n_hat pulls this quirk back toward its partner (attractive).

    v_par_vec = (v . n_hat) n_hat
    v_perp_vec = v - v_par_vec
    F_string = -Lambda^2 * ( sqrt(1 - |v_perp|^2)/|v_par| * v_par_vec
                              + |v_par|/sqrt(1 - |v_perp|^2) * v_perp_vec )

    Both terms are well-defined in the |v_par| -> 0 limit in the sense that
    the force stays finite and directed along -n_hat (pure perpendicular
    motion pulls straight back along the string); we regularize the 1/v_par
    division with a small floor to avoid division-by-zero blowups from
    floating point, matching the paper's stated numerical treatment for
    near-threshold configurations (Sec. II, "close to threshold quirks").
    """
    v_par_scalar = np.dot(v, n_hat)
    v_par_vec = v_par_scalar * n_hat
    v_perp_vec = v - v_par_vec

    v_perp2 = np.dot(v_perp_vec, v_perp_vec)
    sqrt_term = np.sqrt(max(1.0 - v_perp2, 1e-12))

    # term1 = sqrt(1-v_perp^2)/v_par * v_par_vec.  v_par_vec = v_par_scalar *
    # n_hat, so this ratio is EXACTLY sqrt(1-v_perp^2) * n_hat regardless of
    # the sign or magnitude of v_par_scalar (the v_par cancels algebraically
    # against itself) -- the string always pulls along the fixed direction
    # n_hat with this magnitude, never flipping sign based on which way the
    # quirk happens to be moving. Computing it via an explicit
    # magnitude-only division (as an earlier version of this code did)
    # wrongly introduces a sign(v_par) factor and makes the force alternate
    # attractive/repulsive -- confirmed as a real bug via the Eq. 4 check.
    term1 = sqrt_term * n_hat

    # term2 = v_par/sqrt(1-v_perp^2) * v_perp_vec ; v_par here is the signed
    # scalar (this term vanishes when v_perp_vec = 0, so its sign convention
    # only matters for genuinely non-radial motion).
    term2 = (v_par_scalar / sqrt_term) * v_perp_vec

    return -Lambda2 * (term1 + term2)


def lorentz_force(charge, v, B_vec):
    """F = q (v x B), natural units (E-field assumed zero in lab frame)."""
    return charge * np.cross(v, B_vec)


def equations_of_motion(t, y, mass, charge1, charge2, Lambda2, B_vec):
    """
    dy/dt for the 12-component state vector [x1, p1, x2, p2].
    charge1, charge2: electric charges of quirk 1 and quirk 2 (in units of e,
    with e absorbed into the Lorentz-force normalization by the caller).
    """
    state = QuirkPairState.from_vector(y)

    v1, _E1 = velocity_from_momentum(state.p1, mass)
    v2, _E2 = velocity_from_momentum(state.p2, mass)

    sep = state.x1 - state.x2  # points from quirk 2 to quirk 1
    dist = np.linalg.norm(sep)
    if dist < 1e-9:
        # Degenerate case (e.g. t=0, both quirks produced at the same point):
        # use each quirk's own velocity direction as its "outward" (away-
        # from-partner) direction, since that is the direction separation is
        # about to develop in for that quirk.
        v1_norm = np.linalg.norm(v1)
        n_hat_1 = v1 / v1_norm if v1_norm > 1e-12 else np.array([1.0, 0.0, 0.0])
        n_hat_2 = -n_hat_1
    else:
        n_hat_1 = sep / dist   # points away from quirk 2, i.e. outward for quirk 1
        n_hat_2 = -n_hat_1     # points away from quirk 1, i.e. outward for quirk 2

    # n_hat_i points AWAY from the other quirk (outward, along this quirk's
    # own displacement from its partner), so that -Lambda^2 * n_hat_i pulls
    # this quirk back toward its partner -- i.e. always attractive.
    F1 = string_force(v1, n_hat_1, Lambda2) + lorentz_force(charge1, v1, B_vec)
    F2 = string_force(v2, n_hat_2, Lambda2) + lorentz_force(charge2, v2, B_vec)

    dx1 = v1
    dp1 = F1
    dx2 = v2
    dp2 = F2

    return np.concatenate([dx1, dp1, dx2, dp2])


def rk4_step(f, t, y, dt, *args):
    k1 = f(t, y, *args)
    k2 = f(t + 0.5 * dt, y + 0.5 * dt * k1, *args)
    k3 = f(t + 0.5 * dt, y + 0.5 * dt * k2, *args)
    k4 = f(t + dt, y + dt * k3, *args)
    return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate_trajectory(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2,
                          Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv,
                          e_charge_natural=0.30282212):
    """
    Integrate the quirk-pair trajectory with fixed-step RK4.

    Lambda_GeV: string tension parameter Lambda (GeV), so Lambda^2 has units
    GeV^2 (force = dp/dt in natural units, GeV^2, consistent).
    B_tesla: magnetic field strength in Tesla, converted to natural units.
    e_charge_natural: sqrt(4 pi alpha_EM) ~ 0.3028, the natural-units electric
    charge; charge1/charge2 are then in units of e (e.g. 2/3, -1, +1).

    Returns dict of time series (all in natural units unless *_cm / *_ns).
    """
    # 1 Tesla in natural (GeV^2) units. Standard HEP conversion: 1 T = 195.35
    # eV^2 = 1.9535e-16 GeV^2. Independently re-derived and verified from the
    # electron cyclotron frequency omega=eB/m (see docs/DEVIATIONS_LOG.md --
    # an earlier version of this constant was wrong by a factor of ~1e4,
    # caught only by this cross-check, not by the B=0 Eq.4 validation).
    TESLA_TO_GEV2 = 1.9535e-16
    B_vec = np.array([0.0, 0.0, B_tesla * TESLA_TO_GEV2])

    Lambda2 = Lambda_GeV ** 2

    y = np.concatenate([x1_0, p1_0, x2_0, p2_0])
    n_steps = int(t_max_gev_inv / dt_gev_inv)

    ts = np.zeros(n_steps + 1)
    xs1 = np.zeros((n_steps + 1, 3))
    xs2 = np.zeros((n_steps + 1, 3))
    ps1 = np.zeros((n_steps + 1, 3))
    ps2 = np.zeros((n_steps + 1, 3))

    ts[0] = 0.0
    xs1[0], ps1[0], xs2[0], ps2[0] = x1_0, p1_0, x2_0, p2_0

    t = 0.0
    for i in range(1, n_steps + 1):
        y = rk4_step(equations_of_motion, t, y, dt_gev_inv,
                     mass, charge1 * e_charge_natural, charge2 * e_charge_natural,
                     Lambda2, B_vec)
        t += dt_gev_inv
        state = QuirkPairState.from_vector(y)
        ts[i] = t
        xs1[i], ps1[i] = state.x1, state.p1
        xs2[i], ps2[i] = state.x2, state.p2

    return {
        "t_gev_inv": ts,
        "x1": xs1, "p1": ps1,
        "x2": xs2, "p2": ps2,
    }


def angular_momentum_and_separation(traj, mass):
    """
    Per-timestep internal angular momentum L (about the CM) and separation d,
    in the CM frame's spatial sense but computed directly from lab-frame
    positions/momenta for simplicity (matches Fig. 2 style diagnostic).

    Returns (r_cm_array_in_cm, L_array_in_hbar_units, d_array_in_cm).
    """
    x1, p1, x2, p2 = traj["x1"], traj["p1"], traj["x2"], traj["p2"]
    n = len(x1)

    L = np.zeros(n)
    d = np.zeros(n)
    r_cm = np.zeros(n)

    for i in range(n):
        xcm = 0.5 * (x1[i] + x2[i])
        rel_x = x1[i] - x2[i]
        rel_p = 0.5 * (p1[i] - p2[i])
        Lvec = np.cross(rel_x, rel_p)
        L[i] = np.linalg.norm(Lvec)  # in natural units (dimensionless, hbar=1)
        d[i] = np.linalg.norm(rel_x)
        r_cm[i] = np.linalg.norm(xcm)

    return gev_to_cm(r_cm), L, gev_to_cm(d)
