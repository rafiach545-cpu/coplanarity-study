"""
Standalone Bethe-Bloch mean-energy-loss validation module (v1).

Scope, per PAPER_TO_CODE_SPEC.md: this validates the STANDARD Bethe-Bloch
mean-dE/dx FORMULA (PDG Review of Particle Physics, the paper's own cited
ref [35] for its dE/dx treatment) against well-known reference values in
silicon. It does NOT attempt the paper's specific Landau-Vavilov
most-probable-value (MPV) treatment (a materially more involved
calculation requiring the full Landau distribution, not just the Bethe-
Bloch mean) and it is NOT integrated into this project's quirk trajectory
propagator or detector simulation, since the material thickness / path-
length inputs needed for that integration are not specified anywhere in
the paper or in this project's existing detector geometry (see spec doc).

This is a bounded feasibility/validation step only, not a Figure 7
reproduction.
"""
import numpy as np

# Physical constants
M_E_MEV = 0.51099895  # electron mass, MeV
K_MEV_CM2_PER_MOL = 0.307075  # 4*pi*N_A*r_e^2*m_e*c^2, MeV cm^2/mol

# Silicon material constants (PDG)
SI_Z = 14.0
SI_A = 28.0855  # g/mol
SI_I_EV = 173.0  # mean excitation energy, eV (PDG value for silicon)


def beta_gamma_to_beta_gamma2(betagamma):
    betagamma = np.asarray(betagamma, dtype=float)
    gamma2 = 1.0 + betagamma**2
    beta2 = betagamma**2 / gamma2
    return beta2, gamma2


def t_max_mev(betagamma, mass_mev, charge_mass_ratio_correction=True):
    """Maximum kinetic energy transferable to a free electron in a single
    collision, for an incident particle of mass mass_mev. For mass_mev >>
    m_e (true for any quirk, mQ ~ 800-1800 GeV vs m_e ~ 0.5 MeV), this
    reduces to T_max ~ 2*m_e*c^2*(beta*gamma)^2 to extremely high accuracy;
    the full PDG formula is used here regardless for correctness at
    smaller mass_mev (e.g. the MIP validation case, mass_mev=105.66 MeV
    muon)."""
    beta2, gamma2 = beta_gamma_to_beta_gamma2(betagamma)
    gamma = np.sqrt(gamma2)
    if charge_mass_ratio_correction:
        num = 2 * M_E_MEV * betagamma**2
        den = 1 + 2 * gamma * M_E_MEV / mass_mev + (M_E_MEV / mass_mev) ** 2
        return num / den
    else:
        return 2 * M_E_MEV * betagamma**2


def bethe_bloch_mean_dedx(betagamma, mass_mev, charge_e, Z=SI_Z, A=SI_A, I_eV=SI_I_EV,
                           density_effect=False):
    """Mean mass stopping power -dE/dx in MeV*cm^2/g, standard PDG Bethe-
    Bloch formula (no density-effect correction unless density_effect=True
    is explicitly requested -- see limiting-behavior test / documented
    limitation below for why this matters at high betagamma)."""
    beta2, gamma2 = beta_gamma_to_beta_gamma2(betagamma)
    I_mev = I_eV * 1e-6
    Tmax = t_max_mev(betagamma, mass_mev)
    z2 = charge_e ** 2

    delta = np.zeros_like(np.asarray(betagamma, dtype=float))
    if density_effect:
        # Sternheimer-style density effect is deliberately NOT implemented
        # here (silicon-specific Sternheimer parameters are an additional
        # material input not validated in this bounded module) -- caller
        # must not request it; this branch exists only to make the
        # limitation explicit and fail loudly rather than silently return
        # a wrong number.
        raise NotImplementedError(
            "Density-effect correction requires silicon-specific Sternheimer "
            "parameters not validated in this bounded module -- see "
            "PAPER_TO_CODE_SPEC.md 'What CAN and CANNOT be built'. Left "
            "unimplemented deliberately rather than guessing parameters."
        )

    prefactor = K_MEV_CM2_PER_MOL * z2 * (Z / A) / beta2
    log_term = 0.5 * np.log(2 * M_E_MEV * beta2 * gamma2 * Tmax / (I_mev ** 2))
    bracket = log_term - beta2 - delta / 2.0
    return prefactor * bracket


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    betagamma = np.logspace(-1, 4, 500)
    # MIP reference case: muon in silicon (mass=105.66 MeV, charge=1)
    dedx_mip = bethe_bloch_mean_dedx(betagamma, mass_mev=105.658, charge_e=1.0)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(betagamma, dedx_mip, label="muon in Si, Bethe-Bloch mean (this module)")
    ax.axhline(1.664, color="gray", linestyle="--", label="PDG MIP reference (1.664 MeV cm^2/g)")
    ax.set_xscale("log")
    ax.set_xlabel(r"$\beta\gamma$")
    ax.set_ylabel(r"$-dE/dx$ (MeV cm$^2$/g)")
    ax.set_title("Bethe-Bloch mean dE/dx validation -- muon in silicon\n"
                 "(standalone formula check, NOT a Figure 7 reproduction)")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("/home/rafia/coplanarity_study/05_coplanarity_analysis/figure7_dedx_feasibility_v1/bethe_bloch_validation_curve.png", dpi=150)
    print("Saved bethe_bloch_validation_curve.png")

    imin = np.argmin(dedx_mip)
    print(f"Minimum dE/dx = {dedx_mip[imin]:.4f} MeV cm^2/g at betagamma={betagamma[imin]:.3f}")
    print("PDG reference: minimum ionizing dE/dx in silicon = 1.664 MeV cm^2/g at betagamma~3-3.5")
