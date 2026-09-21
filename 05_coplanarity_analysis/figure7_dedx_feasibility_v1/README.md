# Figure 7 dE/dx feasibility (v1) — 2026-09-21

## Verdict: FIGURE 7 BLOCKED — MATERIAL MODEL NOT SPECIFIED/IMPLEMENTED

Unchanged from the prior turn's finding, re-verified this task (see
`PAPER_TO_CODE_SPEC.md` for the full item-by-item breakdown). Neither the
paper nor this project's existing detector geometry specifies the
material thickness / path-length inputs needed to convert a dE/dx-vs-βγ
formula into actual simulated per-hit energy-loss histograms matching the
paper's real Fig.7.

## What WAS built this task (bounded, non-fabricated feasibility step)

A standalone Bethe-Bloch mean-dE/dx validation module
(`bethe_bloch_validation.py`) — validates the STANDARD formula (per the
paper's own cited ref [35], PDG) against known reference values, entirely
independent of this project's unavailable detector-material inputs.

**Results:**
- Minimum-ionizing dE/dx in silicon (muon, βγ≈3.18): **1.694 MeV·cm²/g**
  vs. the PDG reference value **1.664 MeV·cm²/g** — agreement to 1.8%,
  with the small residual difference attributed to the deliberately
  omitted density-effect (Sternheimer) correction, not a bug.
- Correct qualitative shape confirmed: 1/β² divergence at low βγ, minimum
  around βγ≈3-3.5, relativistic rise at high βγ (the rise does not
  saturate, as expected without the density-effect correction — this is
  a documented, visible limitation in the produced diagnostic curve, not
  hidden).
- 10/10 unit/dimensional/limiting-behavior tests pass
  (`tests/test_bethe_bloch_validation.py`): MIP reference match,
  positivity, finiteness, low-βγ divergence, high-βγ rise, z² charge
  scaling, T_max heavy-particle limit (quirk-mass regime, agrees with the
  M≫m_e approximation to 1e-5), and a deliberate "fail loudly, don't
  guess" check for the unimplemented density-effect branch.

## What was explicitly NOT done

- **No integration into `quirk_trajectory.py`** — the paper's own Eq.3
  propagator has no dE/dx feedback term (Fig.7 is a post-hoc diagnostic
  in the paper, not part of the equations of motion), and this project's
  detector geometry lacks the material-thickness values needed for a
  physically meaningful per-hit path-length calculation.
- **No material-budget values invented.** No silicon thickness, radiation
  length, or path-length-correction factor was guessed or assumed for
  any of this project's 8 detector layers.
- **No MPV (Landau-Vavilov most-probable-value) implementation** — the
  paper specifically uses MPV, not the Bethe-Bloch mean; MPV requires the
  full Landau distribution machinery, a materially larger undertaking
  than validating the mean formula, and was out of scope for this bounded
  feasibility step.
- **No Figure 7 histogram was produced or claimed as a reproduction.**

## Files
- `PAPER_TO_CODE_SPEC.md` — full item-by-item specification and BLOCKED verdict
- `bethe_bloch_validation.py` — standalone formula validation module
- `bethe_bloch_validation_curve.png` — diagnostic curve (muon-in-silicon MIP validation)
- `tests/test_bethe_bloch_validation.py` (repo root `tests/`) — 10/10 passing unit tests
