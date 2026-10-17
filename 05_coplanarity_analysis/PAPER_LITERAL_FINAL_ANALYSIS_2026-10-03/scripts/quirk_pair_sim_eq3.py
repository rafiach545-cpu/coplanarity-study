#!/usr/bin/env python3
"""Quirk pair simulator in physical units (mm, ns, GeV, T), same interface as the supplied simulate_quirk_pair_tracks (2026-10-12),
with the equations of arXiv:1708.02243:

  Eq. 3 (straight string, Nambu-Goto with massive ends), for each quirk, s = unit vector from the partner to the quirk, v_par = v.s (signed),
      d(m gamma v)/dt = -T [ sqrt(1 - v_perp^2) s + v_par / sqrt(1 - v_perp^2) v_perp ] + F_ext,    T = Lambda^2 (string tension)
  F_ext = Lorentz force q v x B, B = (0, 0, B) uniform.

Units: T in GeV/mm = Lambda^2 / (hbar c);  dp/dt [GeV/ns] = F [GeV/mm] * c [mm/ns];
       Lorentz: dp/dt [GeV/ns] = 0.299792458 [GeV / (T m)] * q * (v [m/ns]) x B [T]   (p = 0.3 q B R).
Differences to the supplied version: (1) Lorentz term multiplied by c in m/ns (the supplied 0.3 q beta x B is 3.34x too large);
(2) full Eq. 3 instead of a constant force T s; (3) quirks produced at one point (sep0_mm = 0 by default);
(4) back-to-back momenta built in the pair CM frame along any direction rel_dir and boosted to the lab (the supplied p_com/2 +- p_rel is a
CM configuration only when p_rel is perpendicular to p_com); (5) separate charges; (6) at zero separation the string direction is taken from the
relative velocity. Integrator: classical RK4 with fixed step, as in the supplied code. string_tension stays Lambda in eV."""
import numpy as np

C_MM_NS = 299.792458
HBARC_GEV_MM = 1.973269804e-13


def _boost(E, p, beta_vec):
    """Lorentz boost of (E, p) by velocity beta_vec (from the pair CM frame to the lab)."""
    b = np.linalg.norm(beta_vec)
    if b == 0.0:
        return E, p.copy()
    g = 1.0 / np.sqrt(1.0 - b * b); bh = beta_vec / b; pl = p @ bh
    return g * (E + b * pl), p + ((g - 1.0) * pl + g * b * E) * bh


def simulate_quirk_pair_tracks(
    event_id,
    n_steps=70000,
    t_max=80.0,
    b_field=2.0,
    charge=1.0,
    quirk_mass=500.0,
    pair_pt=50.0,
    pair_pz=10.0,
    opening_angle=1.3,
    phi0=0.0,
    x0=0.0,
    y0=0.0,
    z0=0.0,
    string_tension=900.0,
    oscillation_jitter=0.0,
    velocity_scale=1.0,
    p_star=None,
    rel_dir=None,
    charge2=None,
    sep0_mm=0.0,
):
    """
    Units: position mm, time ns, mass GeV, momentum GeV, B in T, string_tension = Lambda in eV.
    Pair kinematics: total momentum (pair_pt cos phi0, pair_pt sin phi0, pair_pz). Internal momentum p_star (GeV, CM frame); if None it is taken
    from opening_angle as in the supplied code (p_rel = 0.5 pair_pt tan(opening_angle / 2)). rel_dir = direction of quirk 1 in the CM frame
    (default: transverse, perpendicular to the pair momentum, as in the supplied code). charge2 defaults to -charge.
    oscillation_jitter and velocity_scale are kept for interface compatibility and are not used.
    """
    n_steps = int(max(200, n_steps)); t_max = float(max(1e-6, t_max)); dt = t_max / float(n_steps - 1)
    m = float(max(1e-9, quirk_mass)); q1 = float(charge); q2 = -q1 if charge2 is None else float(charge2)
    lam = float(max(0.0, string_tension)) * 1e-9; T_gev_mm = lam * lam / HBARC_GEV_MM
    B = np.array([0.0, 0.0, float(b_field)]); kL = 0.299792458e-3          # GeV / (T mm): p = 0.3 q B R with R in m -> per mm

    P = np.array([pair_pt * np.cos(phi0), pair_pt * np.sin(phi0), pair_pz], float)
    if p_star is None:
        p_star = 0.5 * pair_pt * np.tan(0.5 * float(np.clip(opening_angle, 1e-6, np.pi - 1e-6)))
    n = np.array([-np.sin(phi0), np.cos(phi0), 0.0]) if rel_dir is None else np.asarray(rel_dir, float)
    n = n / np.linalg.norm(n)
    Es = np.sqrt(m * m + p_star ** 2); Mpair = 2.0 * Es; Epair = np.sqrt(Mpair ** 2 + P @ P); beta = P / Epair
    _, p1 = _boost(Es, p_star * n, beta); _, p2 = _boost(Es, -p_star * n, beta)
    r0 = np.array([x0, y0, z0], float); off = 0.5 * float(sep0_mm) * n
    r1, r2 = r0 + off, r0 - off

    def vel(p):                                     # mm/ns
        return C_MM_NS * p / np.sqrt(m * m + p @ p)

    def string_force(v_b, s):                       # Eq. 3, v_b = v/c, s from partner to this quirk; GeV/mm
        vpar = v_b @ s; vperp = v_b - vpar * s; st = np.sqrt(max(1.0 - vperp @ vperp, 1e-12))
        return -T_gev_mm * (st * s + (vpar / st) * vperp)

    def rhs(state):
        a1, k1, a2, k2 = state[0:3], state[3:6], state[6:9], state[9:12]
        v1, v2 = vel(k1), vel(k2); b1, b2 = v1 / C_MM_NS, v2 / C_MM_NS
        dl = a1 - a2; dist = np.linalg.norm(dl)
        if dist > 1e-12:
            s = dl / dist
        else:                                       # at zero separation: direction of the relative velocity
            dv = b1 - b2; s = dv / max(np.linalg.norm(dv), 1e-15)
        F1 = string_force(b1, s) * C_MM_NS + kL * q1 * np.cross(v1, B)
        F2 = string_force(b2, -s) * C_MM_NS + kL * q2 * np.cross(v2, B)
        return np.concatenate([v1, F1, v2, F2])

    state = np.concatenate([r1, p1, r2, p2]).astype(np.float64)
    xyz1 = np.zeros((n_steps, 3)); xyz2 = np.zeros((n_steps, 3)); pxyz1 = np.zeros((n_steps, 3)); pxyz2 = np.zeros((n_steps, 3))
    for i in range(n_steps):
        xyz1[i], pxyz1[i], xyz2[i], pxyz2[i] = state[0:3], state[3:6], state[6:9], state[9:12]
        if not np.all(np.isfinite(state)):
            raise RuntimeError(f"non-finite state at step {i}")
        k1 = rhs(state); k2 = rhs(state + 0.5 * dt * k1); k3 = rhs(state + 0.5 * dt * k2); k4 = rhs(state + dt * k3)
        state = state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return {"event_id": int(event_id), "xyz_q": xyz1, "xyz_aq": xyz2, "pxyz_q": pxyz1, "pxyz_aq": pxyz2,
            "q_q": np.float32(q1), "q_aq": np.float32(q2), "time": np.linspace(0.0, t_max, n_steps)}


def oscillation_period_ns(quirk_mass, p_star, string_tension_ev):
    """Full CM oscillation period (two passes through each other), Eq. 4: 2 x 2 p*/Lambda^2, in ns."""
    lam = string_tension_ev * 1e-9
    return 2.0 * 2.0 * p_star / (lam * lam) * HBARC_GEV_MM / C_MM_NS
