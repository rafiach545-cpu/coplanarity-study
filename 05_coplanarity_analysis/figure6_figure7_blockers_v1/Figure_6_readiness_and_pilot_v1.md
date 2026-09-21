# Figure 6 readiness and bounded pilot (v1) — 2026-09-21

## Paper methodology reread (Fig.6 caption, page 8-9, direct extraction this task)

*"Contours of having 3 (5) events in the mQ vs Lambda plane for an
integrated luminosity of ∫Ldt = 300 fb⁻¹, overlaid with (projected) HSCP
and monojet limits [36]... The 3 events bound corresponds to 2-σ exclusion
given no background. Discovery is defined by 5 events..."* Also from the
body text (page 8): *"we show the expected 95% exclusion for an
integrated luminosity of 300 fb⁻¹, assuming negligible irreducible
backgrounds."*

## Required inputs — verification status

| Input | Status |
|---|---|
| mass grid m_Q | Only 2 points simulated (800GeV, 1800GeV); paper's own Fig.6 panels span ~0-1000GeV (EW) and ~0-2700GeV (colored) continuously — a real grid (proposed: 6-7 points/axis) does not exist |
| Λ grid | Only 2 points simulated (2keV, 4keV); paper's Table I samples ~5 Λ values per mass point; Fig.6's own Λ axis spans 1-30keV log-scale |
| Colored production σ(mQ) | 1 point measured this project (0.0003144 pb at 1800GeV) — recovered from the Fig.5 weight audit, previously mislabeled MISSING in this matrix (fixed this task) |
| EW production σ(mQ) | 1 point measured this project (0.0002337 pb at 800GeV) |
| ε_trig(mQ,Λ), ε_fid(mQ,Λ), ε_reco(mQ,Λ) | Only 2 (mQ,Λ) points each; no functional form or grid |
| Integrated luminosity | 300fb⁻¹ stated exactly; no luminosity-dependent yield calculation implemented anywhere in this project |
| Background assumption | Paper assumes negligible; this project's own 0/5000 (pileup) and 1/9139 (converted-γ+PU) results are consistent with that assumption but were never required as a Fig.6 input |
| Discovery/significance criterion | 3-event (2σ exclusion, no background) / 5-event (discovery) — explicit, simple Poisson-counting criteria, no likelihood-fit machinery needed |

## Why 2 points cannot support a contour (unchanged from prior verification)

A contour in the continuous (mQ, Λ) plane requires σ(mQ)×ε(mQ,Λ) as a
smooth function over both axes. Two isolated (mQ,Λ) points fix nothing
about curvature in either dimension — interpolating a smooth contour
through them would be fabrication.

## Bounded pilot steps performed this task (steps 1-4, 7 of Phase 7)

1. **Grid coverage check**: the existing 91-point proposal (7 colored ×
   7 Λ + 6 EW × 7 Λ) from `Figure_6_future_work_grid_proposal_v1.md`
   spans mQ=600-2400GeV (colored) / 200-1200GeV (EW) and Λ=1-10keV —
   confirmed this covers the paper's own Fig.6 axis ranges (colored panel
   ~0-2700GeV/1-30keV, EW panel ~0-1000GeV/1-30keV), with the proposal's
   upper Λ bound (10keV) somewhat short of the paper's 30keV — noted as a
   gap in the existing proposal, not corrected here (no grid was run).
2. **Generator cards and interpolation requirements**: **NOT VERIFIED.**
   No MadGraph run_card, banner, or generation-time log is preserved
   anywhere in this repository for EITHER existing benchmark point
   (confirmed via repo-wide `find`, this task, Phase 6). The exact
   generation settings (PDF set, merging scale, shower tune) used to
   produce the 2 existing benchmark samples are not independently
   recoverable — this is the same gap identified in the EW discrepancy
   audit (Phase 5). Any new grid point generated without first
   reconstructing/verifying these settings against the existing 2 points
   risks internal inconsistency (a grid point generated with different
   implicit settings than the other 90 would not be a self-consistent
   scan).
3. **Cross-section calculation method**: verified as "count matched
   events / integrated luminosity implied by the run," i.e. this
   project's own MadGraph output normalization — the SAME method already
   used for the 2 existing points (0.0003144pb colored, 0.0002337pb EW).
   No independent theoretical cross-section calculation (e.g. an
   analytic QCD/EW production formula) exists in this project.
4. **Events required per point**: re-confirmed from the existing
   proposal, ≥2000 events/point for statistical parity with this
   project's other established samples.
7. **Checkpoint/resume**: **PROVEN**, re-verified this task — 11
   `.checkpoint` files exist across the pileup sweep and photon-conversion
   overlay runs (`05_coplanarity_analysis/sweep_mu_2026-09-16/*.checkpoint`,
   `02_backgrounds/photon_conversion/*.checkpoint`), confirming this
   project's checkpoint/resume infrastructure is already exercised and
   working for large runs; the same pattern would be reused for a Fig.6
   grid scan.

## Steps 5-6: benchmarking

**Step 5 (benchmark one existing grid point): DONE**, from stored data
(no rerun) — the colored benchmark point's full physics-pipeline runtime
(trajectory + detector + reconstruction, for its 27 trigger-passing
events) is 818s, i.e. 30.3s/event (from `docs/colored_quirk_v3_run.log`,
re-verified this task). This is the per-event cost for ONE stage of a
future grid point; it does NOT include the MadGraph/Pythia8 generation
time for that point, which (per step 2) is unrecoverable from stored
history for either existing benchmark.

**Step 6 (benchmark one NEW pilot point): NOT PERFORMED.** Per this
task's own explicit condition — "Benchmark one new pilot point only if
generation settings are fully verified" — and since step 2 found
generation settings are NOT verified/recoverable, this step is correctly
skipped rather than launched blind.

## Step 8: total CPU time and storage estimate (carried from the existing proposal, re-confirmed)

- 91 grid points × ≥2000 events/point ≈ 182,000+ total events
- Physics-pipeline-only cost at the measured 30.3s/event (colored) rate:
  182,000 × 30.3s ≈ 1,532,000s ≈ **425 hours** — this ALONE far exceeds
  any single-session safe-run budget, before even counting MadGraph
  generation time (unknown, likely comparable or larger).
- This is consistent with the prior task's own order-of-magnitude
  estimate ("~10-20x the largest completed run to date").

## Verdict

**FIGURE 6 NOT YET COMPLETE — VERIFIED GRID PLAN READY.**

The grid plan itself (91 points, axis coverage, events/point,
checkpoint infrastructure) is verified and ready. It is NOT launched
because: (a) generator settings for even the 2 existing benchmark points
are not independently verifiable from stored history, making any new
grid point's internal consistency with the existing ones unprovable
without first reconstructing that provenance; (b) the estimated
physics-pipeline-only cost (≈425 hours) vastly exceeds any single safe
session; (c) MadGraph generation time is a separate, unbounded, unknown
cost on top of that. No new simulation was launched. No contour was
interpolated from the 2 existing points.
