# 09 / g4 — Geant4 validation of the quirk transport (Stage 1 · Run 2 · Ideal, no material)

Started 2026-11-19. The setup:

- Geant4 11.4.1, conda env `g4` (see `/home/rafia/hep_tools/g4_setup/`).
- QuirkPheno quirksim, commit d91cb27, Apache-2.0. Its quirkcore is derived from the public ATLAS athena Quirks code.
- 20 Stage 1 EW signal pairs, m<sub>Q</sub> = 800 GeV (`01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv`). Both quirks start at the origin.

The old code is `04_detector_sim/trajectory_to_hits.simulate_quirk_hits`, the RK4 integration of arXiv:1708.02243 Eq. 3, unchanged. It uses the numba copy, as in the Stage 1 grid. Hits are the true crossing points, before quantisation or smearing. Only hits with |η| < 1.8 are compared.

| Script | Test |
|---|---|
| `ideal8_vacuum.card` | 8 layers at the Stage 1 radii: 1 µm G4_Galactic cylinders that only record the crossing. Uniform 2 T |
| `G01_compare_integrator.py` | Geant4 vs the old code at Λ = 1 eV, 0.1 keV, 4 keV and 25 keV |
| `G02_free_particle_vs_exact_helix.py` | Free particles (Geant4 Λ = 10⁻³ eV, old code Λ = 0) vs the closed-form helix |
| `G03_step_and_B0_tests.py` | (a) the same, with empty vacuum shells every 0.5 cm to cut the steps; (b) B = 0, string only |

## Results so far (2026-11-19)

1. **Free particles vs the exact helix.**
   - The old code agrees to < 0.01 µm on all layers.
   - Geant4 is off by 0.4–4 µm on the pixel layers and 10–45 µm on the SCT layers in r-φ. In z it is off by ≤ 2.5 µm.
   - The Geant4 error does not converge with step length. At L8 the median error is 7 µm with 5 cm shells, 1.7 µm with 2 cm, 15 µm with 0.5 cm (opposite sign) and 171 µm with 0.1 cm.
   - So the error grows with the number of geometry-limited steps. QuirkHyperbolaStep moves along the string segment and applies B as one kick per step; the per-step error is still to be located.
2. **B = 0.** Both codes keep every hit in the exact plane spanned by p₁, p₂ and the vertex: Geant4 ≤ 1.5 µm, old code < 0.01 µm. Within the plane they differ:
   - Λ = 0.1 keV: about 1 µm in r-φ and about 6 µm in z (median);
   - Λ = 4 keV: hundreds of µm.

   Both codes are planar, so this is a difference in the motion within the plane: the two string models (Eq. 3 vs the Athena string vectors) and their initial conditions.
3. **With B = 2 T and Λ = 4 keV,** the codes differ by mm to cm. In 130 of 304 cases a layer is reached in the old code and not in Geant4.
4. **Old-code integration failures** (the step ceiling, events skipped in the comparison): 1 of 20 at 4 keV and 16 of 20 at 25 keV.

Not yet done: locating the Geant4 per-step error, and an independent in-plane reference for Λ > 0 (conserved quantities at B = 0).

## G04: string force vs the exact 1D solution (2026-11-19)

The test (`G04_string_force_exact_1d.py`):
- B = 0, back-to-back quirks of m = 800 GeV, tilted by 1 mrad. An exactly collinear start stalls the Geant4 transport, which then writes 1.4 GB of steps in 20 ns.
- With v ∥ string, Eq. 3 and a straight Nambu–Goto string both give a constant force Λ². The motion is then exactly hyperbolic.
- E₀ − m is chosen so that the exact turning point is at 20 cm.

| Λ | L1–L4 crossing times vs exact | Turning point: exact / Geant4 / old |
|---|---|---|
| 1 keV | both within 0.005 ps | 20.0000 / 19.9961 / 20.0000 cm |
| 4 keV | both within 0.005 ps | 20.0000 / 19.9998 / 20.0000 cm |

**Conclusion for the ideal baseline (no material).** The old integrator passes all three exact references: the closed-form helix (< 0.01 µm), the exact plane at B = 0 (< 0.01 µm) and the exact 1D string solution. It remains the transport for Stage 1 · Run 2 · Ideal, and B05 uses it.

Geant4/QuirkPheno is kept for the material step. Its per-step error on geometry-limited steps (G02/G03) must be solved before it is used there.

The 4 keV differences in G01 (B = 2 T, general angles) come from the part that is not exactly solvable: v<sub>⊥</sub> ≠ 0, where Eq. 3 and the Athena string-vector model differ, plus that Geant4 step error. They are not from the string-force normalisation.
