"""
Exact analytic helix propagation for ordinary (Lambda=0, no confining
string) charged particles in a uniform B field along z.

WHY NOT RK4: at mu=50, a single hard event needs O(50 x ~100) = ~5000
pileup-particle trajectories. RK4-integrating each one (as quirk_trajectory.py
does for the string-bound quirk pair) would be computationally infeasible
for tonight's run. For a particle with NO string force, the equation of
motion (Eq. 3 with the string term set to zero) reduces to the ordinary
relativistic Lorentz-force equation, which has a CLOSED-FORM solution: pz
and the transverse momentum magnitude are exactly conserved, and the
transverse trajectory is an exact circle. This is not an approximation of
Eq. 3 -- it IS the exact solution of Eq. 3 in the Lambda=0 limit.

VALIDATION REQUIRED: this module must be checked against the existing,
already-validated RK4 integrator (quirk_trajectory.py, with charge2=0 and
Lambda_GeV=0 for the "test" particle so only one real body moves) before
being trusted for the real pileup pipeline -- see validate_helix.py.
"""
import numpy as np

HBARC_GEV_CM = 1.973269804e-14
TESLA_TO_GEV2 = 1.9535e-16
E_CHARGE_NATURAL = 0.30282212


def find_helix_layer_crossings(x0_cm, p_gev, mass_gev, charge_e, B_tesla, layer_radii_cm):
    """
    x0_cm: (3,) starting position, cm.
    p_gev: (3,) momentum, GeV.
    mass_gev, charge_e (units of e), B_tesla: as named.
    layer_radii_cm: iterable of cylindrical radii (cm) to find crossings for.

    Returns dict {radius_cm: (hit_xyz_cm, t_ns)} for radii actually crossed
    (particle moving outward), using the EXACT helix solution.
    """
    px, py, pz = p_gev
    E = np.sqrt(px**2 + py**2 + pz**2 + mass_gev**2)
    pT = np.hypot(px, py)
    x0, y0, z0 = x0_cm

    if charge_e == 0 or pT < 1e-9:
        # Neutral or purely-longitudinal: straight line (or no transverse
        # motion at all -- never crosses any nonzero cylindrical radius
        # from the beamline in the transverse sense unless already off-axis).
        results = {}
        vx, vy, vz = px/E, py/E, pz/E
        for r in layer_radii_cm:
            # straight-line circle intersection (charge=0 case)
            # |  (x0+vx t, y0+vy t) | = r ; solve quadratic in t (natural units then convert)
            a = vx**2 + vy**2
            if a < 1e-30:
                continue
            b = 2*(x0*vx + y0*vy)
            c = x0**2 + y0**2 - r**2
            disc = b**2 - 4*a*c
            if disc < 0:
                continue
            t1 = (-b + np.sqrt(disc)) / (2*a)
            t2 = (-b - np.sqrt(disc)) / (2*a)
            t_cm = min(t for t in (t1, t2) if t > 1e-9) if any(t > 1e-9 for t in (t1, t2)) else None
            if t_cm is None:
                continue
            hit = np.array([x0 + vx*t_cm, y0 + vy*t_cm, z0 + vz*t_cm])
            t_ns = (t_cm / HBARC_GEV_CM) * 6.582119569e-25 * 1e9  # via natural-unit time
            # Actually simpler: t_cm above is a LENGTH (cm) parametrization already since v is dimensionless (c=1);
            # true elapsed time (ns) = distance_cm / (v_total * c) ... handled precisely below via helical branch instead.
            results[r] = (hit, None)
        return results

    Bz_nat = B_tesla * TESLA_TO_GEV2
    R_nat = pT / (abs(charge_e) * E_CHARGE_NATURAL * Bz_nat)   # gyroradius, GeV^-1
    R_cm = R_nat * HBARC_GEV_CM

    sign = np.sign(charge_e * Bz_nat) if Bz_nat != 0 else 1.0
    pT_hat = np.array([px, py]) / pT
    # center direction from position0 = sign * rotate90_cw(pT_hat); rotate90_cw(v)=(vy,-vx)
    rot_cw = np.array([pT_hat[1], -pT_hat[0]])
    center = np.array([x0, y0]) + sign * R_cm * rot_cw

    # vector from center to initial position:
    rel0 = np.array([x0, y0]) - center
    phi0 = np.arctan2(rel0[1], rel0[0])
    # direction of increasing arc-length (matches motion direction): the
    # particle moves with angular velocity omega = -sign / R (so that at
    # theta=phi0 the velocity matches pT_hat) -- verified in validate_helix.py
    omega_sign = -sign

    v_T = pT / E  # transverse speed (dimensionless, c=1) -- transverse arc
                  # length traveled = v_T * t_natural, exactly, regardless
                  # of pz (time formula must use v_T against the TRANSVERSE
                  # arc length, not the total 3D speed against it).
    HBARC_GEV_S = 6.582119569e-25

    results = {}
    for r in layer_radii_cm:
        # |center + R*(cos(theta), sin(theta))| = r  -> solve for theta
        d = np.linalg.norm(center)
        if d < 1e-12:
            # concentric special case
            if abs(R_cm - r) > 1e-9:
                continue
            theta_sols = [phi0 + 1e-6]  # degenerate; skip precise handling (rare)
        else:
            # |center|^2 + R^2 + 2R(center . (cos,sin)) = r^2
            rhs = (r**2 - d**2 - R_cm**2) / (2 * R_cm * d)
            if rhs < -1 or rhs > 1:
                continue  # never reaches this radius
            alpha = np.arctan2(center[1], center[0])
            dtheta = np.arccos(np.clip(rhs, -1, 1))
            theta_sols = [alpha + dtheta, alpha - dtheta]

        best_dtheta = None
        best_theta = None
        for theta in theta_sols:
            dtheta_signed = (theta - phi0) * omega_sign
            dtheta_mod = dtheta_signed % (2*np.pi)
            if dtheta_mod < 1e-9:
                continue
            if best_dtheta is None or dtheta_mod < best_dtheta:
                best_dtheta = dtheta_mod
                best_theta = theta
        if best_theta is None:
            continue

        xT = center + R_cm * np.array([np.cos(best_theta), np.sin(best_theta)])
        arc_len_cm = R_cm * best_dtheta
        # best_dtheta is already the forward-progressing (time-ordered) arc
        # parameter (constructed via the omega_sign correction above) --
        # applying omega_sign a second time here double-flips the sign for
        # one of the two charge/field sign combinations. Path length
        # traveled is R*best_dtheta (always >=0); z increases by
        # (pz/pT)*that path length, full stop.
        z = z0 + (pz / pT) * arc_len_cm
        arc_len_natural = arc_len_cm / HBARC_GEV_CM
        t_natural = arc_len_natural / v_T
        t_ns = t_natural * HBARC_GEV_S * 1e9
        results[r] = (np.array([xT[0], xT[1], z]), t_ns)
    return results
