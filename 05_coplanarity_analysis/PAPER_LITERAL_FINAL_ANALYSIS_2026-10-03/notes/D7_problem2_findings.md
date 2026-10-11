# D17 Problem 2: alternating |L| at successive closest approaches (COL2000 key 35) — investigation, 2026-10-09
Script: scripts/D7_problem2_L_alternation.py. Outputs (new): tables/D7_closest_approaches.csv, tables/D7_torque_test.csv, tables/D7_turning_points.csv,
tables/D7_spacing_candidates.csv. No existing table, report, log or commit was changed.

## Measurements
- CM-frame L vector at the large-|L| approaches (r = 0.89, 2.68, 4.47 cm) is the same vector each time: (5.19e11, 5.6e10, -6.04e11) hbar, |L| = 7.98e11,
  identical at 3000 / 6000 / 12000 steps per period. At the small-|L| approaches (r = 1.79, 3.58 cm) L points the opposite way and its size falls with
  resolution: 8.7e8 -> 2.1e8 -> 1.1e8 and 1.4e9 -> 3.2e8 -> 1.6e8 hbar.
- |p_rel*| = 1249 GeV at every approach; the angle between d* and p_rel* is < 5 deg except one sampling-limited point. d_min and p_perp at the
  approaches change with the step size (sampling-limited) and are not used for conclusions.
- Lab-frame torque test from the implemented right-hand side: integral of dL/dt between consecutive approaches reproduces the change of
  L_lab = (x1-x2)x(p1-p2)/2 to 2e-5 - 3e-4 (relative). Per half-oscillation the Lorentz torque contributes 7.08e11 hbar, aligned with dL
  (cos 0.81-0.99); the kinematic and string terms are each ~9e14 but cancel to below 1e12.
- Second event with spacing nearest the paper's 1.155 cm: key 10 (predicted 1.18 cm, d max 5.58 cm): same alternation, |L| = 2.0e12 vs 1.4e9 / 1.7e9.
- Turning points (d max): |L| = 3.27-3.28e11 (key 35) and 3.18-3.20e11 (key 10), never near zero.
- Paper event, recoverable from its Fig. 2 only: d max 3.56 cm (gamma* = 1.2005, v* = 0.553 if d is the separation), spacing 1.155 cm
  (beta*gamma_CM = 0.098), |L| maxima 6.7 / 2.0 / 5.3 / 2.9 e11 near the d minima, cusp-like |L| minima at r = 1.91 / 2.67 / 4.10 cm with d = 3.2 / 3.1 / 3.5 cm.
  Momentum directions, charges, vertex and the frame of L are not given.

## Hypotheses (kept separate; none is established as the cause)
| Hypothesis | Evidence for | Evidence against | Status |
|---|---|---|---|
| H1 initial-condition difference | paper event has other kinematics (beta*gamma 0.098 vs 0.073; d max 3.56 vs 3.86 cm); its orientation is unknown | all 22 colored events alternate (D6: 132/276 approaches, 22/22 events); key 10 with paper-like spacing alternates too | not supported by the tests; not excluded (paper inputs unavailable) |
| H2 numerical integration error | small-|L| values are not converged | large-|L| values and L vectors converged at 3000/6000/12000; finer steps make the small values smaller, not larger | does not produce the pattern; only inflates the small values |
| H3 torque / dynamics implementation | — | lab torque integral from the implemented equations matches dL to <= 3e-4; CM torque of Eq. 5 matches |L(t)| to ~11% (D6); Eq. 4 amplitude exact (D1) | implementation is consistent with its own equations and with Eq. 4/5; agreement with the paper's own code cannot be tested |
| H4 reading of the paper's curve | the paper's minima are cusps at large d, i.e. the plotted quantity passes through zero there | axis assignment follows the paper's legend; lab-frame alternatives (relative L ~2.7e14 artefact peaks; L about the vertex ~7e16) do not have the paper's scale; CM |L| does (8.0 vs 6.7 e11) | the tested alternative readings do not reproduce the paper; untested definitions (a component, per-quirk L) remain possible |
