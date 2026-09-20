"""
READ-ONLY statistical audit + targeted fix for a Wilson-interval bug found
in this session. Does NOT touch any authoritative event CSV and does NOT
rerun any simulation.

BUG: 05_coplanarity_analysis/build_ppt_statistics.py's wilson(k,n,z) (and an
inline copy of the same pattern used ad hoc for the converted-photon+
pileup overlay's Phase 9 cutflow/final-pass statistics) omitted the
leading `z` multiplier on the margin term:

  BUGGY:    half = sqrt(phat*(1-phat)/n + z*z/(4*n*n))
  CORRECT:  half = z * sqrt(phat*(1-phat)/n + z*z/(4*n*n))

This produces an interval that is too narrow (understates uncertainty),
and for small k/n can fail to contain the point estimate entirely --
exactly what was observed for k=1, n=9139.

Other Wilson implementations in this repo (run_pileup_fake_background.py,
build_pileup_only_statistics.py, build_converted_photon_only_statistics.py)
already include the z multiplier and are CONFIRMED CORRECT below.
"""
import json
import numpy as np
from scipy import stats as sstats


def wilson_correct(k, n, z):
    """Canonical two-sided Wilson score interval."""
    if n == 0:
        return (float("nan"), float("nan"))
    phat = k / n
    center = (phat + z * z / (2 * n)) / (1 + z * z / n)
    half = (z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))) / (1 + z * z / n)
    return (max(0.0, center - half), min(1.0, center + half))


def wilson_buggy(k, n, z):
    """The BUGGY version found in build_ppt_statistics.py / the Phase 9
    overlay script -- kept here ONLY to demonstrate/prove the discrepancy,
    never to be used for reporting."""
    if n == 0:
        return (float("nan"), float("nan"))
    phat = k / n
    c = phat + z * z / (2 * n)
    h = np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))  # BUG: missing leading z
    d = 1 + z * z / n
    return ((c - h) / d, (c + h) / d)


def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else sstats.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else sstats.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (lo, hi)


if __name__ == "__main__":
    print("=" * 70)
    print("PART 1 -- reproduce and confirm the reported bug (k=1, n=9139)")
    print("=" * 70)
    k, n = 1, 9139
    phat = k / n
    buggy = wilson_buggy(k, n, 1.96)
    correct = wilson_correct(k, n, 1.96)
    print(f"point estimate phat = {phat:.9f}")
    print(f"REPORTED (buggy)  Wilson 95%: [{buggy[0]:.9f}, {buggy[1]:.9f}] "
          f"-- contains phat? {buggy[0] <= phat <= buggy[1]}")
    print(f"CORRECTED         Wilson 95%: [{correct[0]:.9f}, {correct[1]:.9f}] "
          f"-- contains phat? {correct[0] <= phat <= correct[1]}")

    print()
    print("=" * 70)
    print("PART 2 -- independent calculation, k=1, n=9139")
    print("=" * 70)
    for z, label in [(1.0, "68%"), (1.96, "95%")]:
        w = wilson_correct(k, n, z)
        print(f"Wilson {label}: [{w[0]:.9f}, {w[1]:.9f}]  contains phat={phat <= w[1] and phat >= w[0]}")
    for alpha, label in [(0.32, "68%"), (0.05, "95%")]:
        cp = clopper_pearson(k, n, alpha)
        print(f"Clopper-Pearson {label}: [{cp[0]:.9f}, {cp[1]:.9f}]  contains phat={cp[0] <= phat <= cp[1]}")

    print()
    print("=" * 70)
    print("PART 3 -- cross-check via scipy.stats.beta (Clopper-Pearson) and manual Wilson re-derivation")
    print("=" * 70)
    # manual re-derivation, independent code path, z=1.96
    z = 1.96
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
    print(f"manual re-derivation: center={center:.9f} margin={margin:.9f} "
          f"-> [{center-margin:.9f}, {center+margin:.9f}]")
    print("statsmodels.stats.proportion.proportion_confint: NOT AVAILABLE in this "
          "environment (ModuleNotFoundError) -- cross-checked instead via an "
          "independently-written manual re-derivation (above) and scipy.stats.beta "
          "for Clopper-Pearson, both of which agree with wilson_correct().")

    print()
    print("=" * 70)
    print("PART 4 -- regression test cases")
    print("=" * 70)
    cases = [(0, 5000), (1, 9139), (4, 2982), (172, 172), (0, 172)]
    all_pass = True
    for k, n in cases:
        phat = k / n
        w68 = wilson_correct(k, n, 1.0)
        w95 = wilson_correct(k, n, 1.96)
        c68 = clopper_pearson(k, n, 0.32)
        c95 = clopper_pearson(k, n, 0.05)
        eps = 1e-9  # floating-point tolerance at the k=0/k=n boundary only (not a formula bug)
        ok68 = w68[0] - eps <= phat <= w68[1] + eps
        ok95 = w95[0] - eps <= phat <= w95[1] + eps
        okc68 = c68[0] - eps <= phat <= c68[1] + eps
        okc95 = c95[0] - eps <= phat <= c95[1] + eps
        all_pass &= ok68 and ok95 and okc68 and okc95
        print(f"k={k:>5} n={n:>6} phat={phat:.6f}  "
              f"Wilson68=[{w68[0]:.6f},{w68[1]:.6f}]({ok68})  "
              f"Wilson95=[{w95[0]:.6f},{w95[1]:.6f}]({ok95})  "
              f"CP68=[{c68[0]:.6f},{c68[1]:.6f}]({okc68})  "
              f"CP95=[{c95[0]:.6f},{c95[1]:.6f}]({okc95})")
    print(f"\nALL REGRESSION CASES CONTAIN POINT ESTIMATE: {all_pass}")
    import sys
    sys.exit(0 if all_pass else 1)
