"""
Unit, dimensional, and limiting-behavior tests for the standalone
Bethe-Bloch validation module (05_coplanarity_analysis/
figure7_dedx_feasibility_v1/bethe_bloch_validation.py). This validates the
FORMULA only -- it is not a Figure 7 reproduction test (Figure 7 itself
remains BLOCKED, see PAPER_TO_CODE_SPEC.md).
"""
import sys
import numpy as np

sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure7_dedx_feasibility_v1")
from bethe_bloch_validation import bethe_bloch_mean_dedx, t_max_mev, beta_gamma_to_beta_gamma2

PASS = []
FAIL = []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
        print(f"PASS: {name}")
    else:
        FAIL.append(name)
        print(f"FAIL: {name}  {detail}")


# --- Test 1: minimum-ionizing dE/dx in silicon matches PDG reference ---
betagamma = np.logspace(-1, 4, 2000)
dedx = bethe_bloch_mean_dedx(betagamma, mass_mev=105.658, charge_e=1.0)
i_min = np.argmin(dedx)
min_val = dedx[i_min]
min_bg = betagamma[i_min]
PDG_MIP_REF = 1.664
check("MIP dE/dx within 5% of PDG reference (1.664 MeV cm^2/g)",
      abs(min_val - PDG_MIP_REF) / PDG_MIP_REF < 0.05,
      f"got {min_val:.4f}")
check("MIP minimum occurs at betagamma in [2.5, 4.5] (PDG: ~3-3.5)",
      2.5 < min_bg < 4.5, f"got betagamma={min_bg:.3f}")

# --- Test 2: dimensional/positivity check ---
check("dE/dx is strictly positive everywhere on the tested range",
      np.all(dedx > 0))
check("dE/dx is finite everywhere on the tested range",
      np.all(np.isfinite(dedx)))

# --- Test 3: 1/beta^2 divergence at low betagamma (limiting behavior) ---
bg_low = np.array([0.05, 0.1])
dedx_low = bethe_bloch_mean_dedx(bg_low, mass_mev=105.658, charge_e=1.0)
check("dE/dx increases as betagamma decreases in the low-beta regime (1/beta^2 divergence)",
      dedx_low[0] > dedx_low[1] > min_val,
      f"got dedx(0.05)={dedx_low[0]:.3f}, dedx(0.1)={dedx_low[1]:.3f}, min={min_val:.3f}")

# --- Test 4: relativistic rise at high betagamma (documented: no density-effect saturation) ---
bg_high = np.array([100.0, 1000.0, 10000.0])
dedx_high = bethe_bloch_mean_dedx(bg_high, mass_mev=105.658, charge_e=1.0)
check("dE/dx rises monotonically at high betagamma (relativistic rise, no density-effect cutoff -- documented limitation)",
      dedx_high[0] < dedx_high[1] < dedx_high[2])

# --- Test 5: charge scaling (dE/dx ~ z^2) ---
dedx_z1 = bethe_bloch_mean_dedx(np.array([3.0]), mass_mev=800000.0, charge_e=1.0)[0]
dedx_z2 = bethe_bloch_mean_dedx(np.array([3.0]), mass_mev=800000.0, charge_e=2.0)[0]
check("dE/dx scales as charge^2 (z=2 gives 4x z=1)",
      abs(dedx_z2 / dedx_z1 - 4.0) < 1e-9,
      f"got ratio={dedx_z2/dedx_z1:.6f}")

# --- Test 6: T_max reduces correctly for heavy incident particle (quirk-mass regime) ---
# For M >> m_e, T_max ~ 2*m_e*(betagamma)^2 (MeV) to very high precision
bg_test = np.array([3.0])
Tmax_quirk = t_max_mev(bg_test, mass_mev=1.8e6)  # 1.8 TeV quirk
Tmax_approx = 2 * 0.51099895 * bg_test**2
# Expected correction size is O(2*gamma*m_e/M) ~ 1.8e-6 for a 1.8 TeV quirk
# at betagamma=3 -- tolerance set to 1e-5 to comfortably contain that, not to
# paper over a real discrepancy.
check("T_max for a quirk-mass (1.8 TeV) particle matches the M>>m_e approximation to 1e-5",
      abs(Tmax_quirk[0] - Tmax_approx[0]) / Tmax_approx[0] < 1e-5,
      f"got Tmax={Tmax_quirk[0]:.6e}, approx={Tmax_approx[0]:.6e}")

# --- Test 7: density-effect branch fails loudly rather than silently guessing ---
try:
    bethe_bloch_mean_dedx(np.array([100.0]), mass_mev=105.658, charge_e=1.0, density_effect=True)
    check("density_effect=True raises NotImplementedError (no silent guessing)", False)
except NotImplementedError:
    check("density_effect=True raises NotImplementedError (no silent guessing)", True)

# --- Test 8: beta_gamma_to_beta_gamma2 sanity ---
beta2, gamma2 = beta_gamma_to_beta_gamma2(np.array([1.0]))
check("betagamma=1 gives beta^2=0.5, gamma^2=2 (standard relativistic identity)",
      abs(beta2[0] - 0.5) < 1e-9 and abs(gamma2[0] - 2.0) < 1e-9,
      f"got beta2={beta2[0]}, gamma2={gamma2[0]}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} tests passed")
if FAIL:
    print("FAILURES:", FAIL)
    sys.exit(1)
sys.exit(0)
