# Final Paper Reproduction Report (v1) — 2026-09-21

Independent reproduction audit of arXiv:1708.02243v2, "Tracking down
Quirks at the LHC" (Knapen, Lou, Papucci, Setford). This report compiles
the complete, current state of this project as of the FINAL PAPER
COMPLETION AUDIT AND REMAINING-WORK EXECUTION task.

## 1. Executive summary

This project reproduces the paper's core coplanarity-based search
strategy for quirks: signal simulation (colored + EW benchmarks),
background modeling (pile-up, converted photons), an 8-layer barrel
detector response, and the Sec. IIIC/IV plane-finding and cut sequence.
**Figures 1-5 are reproduced approximately** (Figure 3 corrected this
task from a prior "NOT ACHIEVED" verdict that was itself a measurement
bug). **Figures 6 and 7 remain BLOCKED** — verified, bounded feasibility
work was performed on both (a grid-readiness plan for Fig.6, a standalone
Bethe-Bloch validation module for Fig.7) but neither was completed with
validated physics, and neither is claimed as reproduced. **Table I shows
close agreement for the colored benchmark and the EW reconstruction
efficiency, but a real, audited, unresolved tension in EW trigger/fiducial
efficiencies**, traced (this task) to undocumented MC generation settings
in both the paper and this project — not a code bug.

## 2. Complete paper methodology

Sec. II: quirks as vector-like fermions confined by a Nambu-Goto string
(action Eq.2), regime mQ≫Λ. Two benchmarks: EW (1,1)₁ Drell-Yan, unit
charge; colored (3,1)₂/₃ QCD, quirk-hadron charge ±1 with ~30%
probability. Equation of motion (Eq.3) = string tension force + external
Lorentz force. Exact B=0 solution (Eq.4). Internal angular momentum
(Eq.5-7) suppresses annihilation. Plane rotation from external torque
(Eq.8-9), always small (paper: "typically not larger than 10⁻³").

Sec. III: signal simulation via MadGraph5_aMC@NLO + Pythia8 (up to 1
jet, MLM-matched) — **no PDF set, merging scale, or shower tune given in
the paper text** (confirmed this task by full-text search). Trigger:
pT(quirk pair CM)>200GeV, motivated by ISR-recoil MET (paper page 4,
verified verbatim this task). Sec. IIIC: coplanarity tensor T_ij (Eq.10-11),
Δs=smallest eigenvalue (thickness), Δw=second eigenvalue (width),
seeding+iterative plane-finding algorithm.

Sec. IV: total efficiency ε=ε_trig×ε_fid×ε_reco (Eq.12), with ε_reco
defined as "the efficiency of our algorithm in finding quirks which
satisfy both the trigger and fiducial requirements" (verified verbatim
this task, page 7) — i.e. conditional on both prior stages. Background:
Z+γ+j → νν+γ with MET>200GeV, pT_γ>0.5GeV (verified verbatim this task,
page 6), converting in the beampipe.

Appendix A: dE/dx via PDG most-probable-value vs βγ [ref 35], explicitly
**not used in the paper's own analysis** — shown "for completeness" only.
βγ<0.1 hits omitted from the dE/dx panel.

**Paper has exactly 7 figures** (Fig.1-7), confirmed by direct PDF
page-by-page extraction, this task (10 pages total, "FIG." occurs exactly
7 times).

## 3. Detector implementation

8-layer ATLAS-like barrel (4 pixel/IBL + 4 SCT), radii from ATLAS
arXiv:2007.07624 Table 1. Pixel/IBL resolution = pixel pitch (paper Sec
IIIA rule); SCT resolution = 2× intrinsic accuracy (paper's own
conservative choice). B=2T along z. |η|<1.8 barrel-only fiducial region
(PROJECT SIMPLIFICATION — no endcap/TRT/calorimeter). 45mm beamspot
smearing (paper value). Beampipe conversion radius 23.5mm.

## 4. Trajectory propagation

Fixed-step RK4 integration of Eq.3 (`quirk_trajectory.py`), validated
against the exact B=0 solution (Eq.4) to 1e-12, and against a pure-Lorentz
gyroradius cross-check to 4e-5. Adaptive dt-coarsening with a validated
300-steps/period floor (`validate_dt_convergence.py`: rel. error <1e-4
down to 30 steps/period, so 300 carries a ~10x safety margin).

## 5. Reconstruction algorithm

`coplanarity_fit.py`: seed from outer 2 layers (Δφ<0.1, Δz<2cm), 4-hit
combinations, Δs<0.05cm/Δw<1cm seed cut; iterative outside-in hit
addition (growth factor ≤3); Sec IIIC event selection = smallest Δs among
Δw<1cm candidates; Sec IV signal region = plane found + hit-multiplicity
(all-but-one-layer ≥2 hits, remaining ≥1) + Δw<1cm & Δs<0.01cm. All hits
are vertex-relative (transform applied before fitting, corrects an
earlier confounded-baseline bug, documented in `analyze_ew_quirk.py`'s
own header).

## 6. Colored results

| Stage | N | Efficiency (of prior stage) |
|---|---|---|
| Matched | 419 | — |
| Charge-filtered | 125 | 29.8% (paper: ~30%) |
| Trigger (pT_pair>200GeV) | 27 | 21.6% (of matched, paper: 24%) |
| Fiducial (8/8 layers + 25ns) | 7 | 25.9% (of trigger, paper: 28%) |
| Sec IIIC plane found | 5 | 71.4% (of fiducial, paper ε_reco: 35% — TENSION, but N=7 statistically inconclusive) |
| Hit-multiplicity pass | 3 | — |
| Sec IV final pass | 1 (event 386) | 14.3% (of fiducial; not a paper-defined quantity) |

Event 386 verified as the sole final-pass event, Δs=0.009367cm,
Δw=0.242530cm.

## 7. EW results

| Stage | N | Efficiency (of prior stage) |
|---|---|---|
| Matched | 511 | — |
| Trigger | 89 | 17.4% (paper: 10% — TENSION, audited Phase 5, no bug found) |
| Fiducial | 40 | 44.9% (paper: 28% — TENSION, audited Phase 5, no bug found) |
| Sec IIIC plane found | 32 | 80.0% (paper ε_reco: 72% — CONSISTENT within Wilson 95% CI) |
| Hit-multiplicity pass | 16 | — |
| Sec IV final pass | 6 | events 260, 313, 322, 332, 362, 438 |

## 8. EW trigger/fiducial discrepancy (Phase 5 audit)

**Verdict: NO BUG FOUND.** Trigger/fiducial cut definitions and
denominators independently verified against the paper's own text
(word-for-word extraction, this task) to be exact matches. Root cause:
undocumented MC generation settings (PDF set, merging scale, shower
tune) — neither the paper nor this project's own stored files specify
these — compounded by the well-documented sensitivity of Drell-Yan pT
spectra specifically to merging-scale choices (unlike QCD pair
production, which shows close paper agreement in this project). Retained
as an unresolved modeling difference; no code changed. Full 511-row
event-level audit table:
`05_coplanarity_analysis/ew_discrepancy_audit_v1/EW_event_level_audit_table_v1.csv`.

## 9. Table I comparison

| Benchmark | Quantity | Paper | Project | Verdict |
|---|---|---|---|---|
| Colored | ε_trig | 0.24 | 0.216 | CONSISTENT (Wilson 95%) |
| Colored | ε_fid | 0.28 | 0.259 | CONSISTENT (Wilson 95%) |
| Colored | ε_reco | 0.35 | 0.714 | TENSION, N=7 inconclusive |
| EW | ε_trig | 0.10 | 0.174 | TENSION, audited, no bug (Sec.8) |
| EW | ε_fid | 0.28 | 0.449 | TENSION, audited, no bug (Sec.8) |
| EW | ε_reco | 0.72 | 0.800 | CONSISTENT (Wilson 95%) |

## 10. Pile-up-only results

μ=0,5,10,20,50, N=5000 each. Selected planes: 0,3,6,22,172. Hit-multiplicity
pass and Sec IV final pass: **0 at every μ** — "zero observed, not zero
probability" (Wilson 95% UL≈7.68×10⁻⁴ at μ=50).

## 11. Converted-photon-only results

9139 events → 2982 selected planes → 4 hit-multiplicity pass → **0**
Sec IV final pass.

## 12. Converted-photon+pile-up μ=50 result

9139 events → 3276 selected planes → 203 hit-multiplicity pass → **1**
Sec IV final pass (event 2555). P_raw=1/9139=1.09421×10⁻⁴, Wilson
95%=[1.93×10⁻⁵,6.20×10⁻⁴] (corrected this session from an earlier
missing-z-multiplier Wilson bug). P_weighted (1% conversion
factor)=1.09421×10⁻⁶, σ_final≈2.3105×10⁻⁴ fb.

## 13. Event 2555 forensic explanation

μ=0: layers 1,2,5 deficient (3 layers <2 hits, only 1 allowed) → FAIL,
though Δs=0.00582cm already <0.01cm. μ=50: one primary pion, pT=0.242GeV,
minbias pool event 3628 particle 10, fills layers 1&2 → PASS,
Δs=0.00910cm. Under this project's implemented Loose tracking-efficiency
model, pT=0.242GeV<0.4GeV gives ε_track=0, so its hits remain in the
simulated unassociated-hit pool — a statement about this project's
implemented model, not a universal ATLAS fact.

## 14. Figures 1-7 status

| Fig | Status | Exact/Approx |
|---|---|---|
| 1 | Achieved (conceptual) | Illustrative only |
| 2 | Achieved (diagnostic) | Approximate |
| 3 | **Achieved this task** (corrects prior "NOT ACHIEVED") | Approximate |
| 4 | Achieved (vertex-fixed replay, event 386) | Approximate |
| 5 | Achieved (shape) + corrected (absolute) | Approximate |
| 6 | **BLOCKED** | N/A — verified grid plan ready, not launched |
| 7 | **BLOCKED** | N/A — standalone Bethe-Bloch formula validated only |

## 15. Figure 5 normalization

Product A (4-component unit-area shape): colored N=5, EW N=32,
pileup_mu50 N=172 (full population), converted-γ+PU_mu50 N=3276 (full
overlay, not the conversion-only N=2982). Product B (3-component
corrected absolute): colored 7.5036×10⁻⁴ fb/event (N=419 denominator —
corrects an earlier N=125-denominator bug that gave 2.5152×10⁻³, 3.352×
too high), EW 4.5738×10⁻⁴ fb/event, converted-γ+PU 2.3105×10⁻⁴ fb/event.
Pile-up excluded from the absolute panel (no cross-section concept for a
per-bunch-crossing overlay process).

## 16. Figure 6 readiness

**FIGURE 6 NOT YET COMPLETE — VERIFIED GRID PLAN READY.** 91-point grid
plan verified (axis coverage, events/point, checkpoint infrastructure
proven). NOT launched: generator settings for the 2 EXISTING benchmark
points are not independently verifiable (no run_card/banner preserved),
and the physics-pipeline-only cost alone is ≈425 hours at the measured
per-event rate — before any MadGraph generation time, which is unknown.
See `05_coplanarity_analysis/figure6_figure7_blockers_v1/Figure_6_readiness_and_pilot_v1.md`.

## 17. Figure 7 readiness

**FIGURE 7 BLOCKED — MATERIAL MODEL NOT SPECIFIED/IMPLEMENTED.** A
standalone Bethe-Bloch mean-dE/dx validation module was built and
verified this task (minimum-ionizing dE/dx in silicon: 1.694 vs PDG's
1.664 MeV·cm²/g, 1.8% agreement; 10/10 unit/limiting-behavior tests
pass). NOT integrated into the propagator or detector simulation: the
material thickness / path-length inputs needed are specified by neither
the paper nor this project's existing geometry, and none were invented.
See `05_coplanarity_analysis/figure7_dedx_feasibility_v1/`.

## 18. Statistical methodology

Wilson score intervals (with an independently re-derived, tested
`wilson_correct()`) and Clopper-Pearson intervals, both cross-checked via
`scipy.stats.beta` and a manual re-derivation (statsmodels unavailable in
this environment). A prior Wilson-interval bug (missing leading `z`
multiplier) was found, fixed, and regression-tested (5/5 cases pass,
re-verified this task).

## 19. Tests

See Section 12 (Phase 12) of the task and `docs/RUN_LOG.md` for the full
list of exit codes. New this task: `tests/test_bethe_bloch_validation.py`
(10/10 pass).

## 20. Runtime and resources

Photon+PU overlay: 53240.8s (14.79h). Pileup sweep (all μ): ~24700s.
Figure 3 diagnostic (11 configs): ~3-4 min total. Figure 4 replay
(event 386, vertex-fixed): 4115.4s (~68.6 min). No new heavy simulation
was launched this task (Phases 6/7 explicitly stopped short of a launch
per their own verification gates).

## 21. Assumptions

See `05_coplanarity_analysis/final_tables_v1/13_assumptions_and_limitations.csv`
for the complete, itemized list (pile-up pool size, barrel-only detector,
unpreserved MC generation settings, Figure 3 initial-orientation
assumption, Figure 4 event substitution, pile-up reweighting ambiguity).

## 22. Limitations

Colored ε_reco statistically inconclusive (N=7). EW ε_trig/ε_fid
discrepancy unresolved (traced to undocumented generation settings, not a
bug). Figure 3 plot retains residual angle-unwrapping spike artifacts at
isolated r values. Figure 6/7 blocked. No endcap/TRT/calorimeter
modeling.

## 23. Bugs found and corrections (this project's full history, not just this task)

- Wilson interval missing `z` multiplier (fixed, regression-tested).
- Colored per-event weight used wrong N=125 denominator instead of N=419
  (3.352× error, fixed).
- EW charge-sign assignment was backwards relative to per-row PDG codes
  (fixed, predates this task).
- Vertex-relative hit transform was missing in an earlier EW baseline
  (confounded baseline retained for comparison, not deleted).
- Figure 3's prior "NOT ACHIEVED" verdict was itself a measurement bug
  (wrong observable + over-loose numerical validity threshold), corrected
  this task.
- `figure6_requirement_matrix.csv` and
  `final_freeze_v1/authoritative_obsolete_file_inventory.csv` both
  contained stale entries not updated after earlier corrections; fixed
  this task.
- `scratch/fig4_artifact.html` presented pre-vertex-fix Figure 4 values
  with no staleness label; annotated OBSOLETE this task.

## 24. What is exactly reproduced

**Nothing is claimed exact.** Every figure and efficiency number carries
either an "approximate" label or an explicit statistical-consistency
caveat. This is a deliberate, standing project convention, re-affirmed
this task.

## 25. What is approximately reproduced

Figures 1-5 (see Section 14). Table I: colored ε_trig/ε_fid and EW
ε_reco (statistically consistent); colored ε_reco and EW ε_trig/ε_fid
show real, audited tensions attributed to statistics (colored) or
unresolved MC modeling differences (EW), not code bugs.

## 26. What remains blocked

Figure 6 (production cross-section grid, luminosity-normalized
significance — verified grid plan ready, not launched). Figure 7
(material budget / path-length model — standalone formula validated,
not integrated).

## 27. Exact recommended next work

1. Reconstruct and archive MadGraph run_cards/banners for the 2 existing
   benchmark points, to enable a self-consistent Figure 6 grid and to
   potentially resolve the EW trigger/fiducial tension.
2. Benchmark MadGraph generation time at small scale (~100 events) before
   committing to any larger colored-statistics or Figure 6 grid run.
3. If Figure 6 is pursued: generate the verified 91-point grid
   sequentially with checkpointing, in a dedicated, explicitly
   time-gated future task.
4. If Figure 7 is pursued: digitize the PDG MPV-dE/dx-vs-βγ curve and
   define an explicit, documented (not invented) material-budget model
   for each of the 8 detector layers before any integration attempt.
5. Read a specific real signal event's stored 4-momenta (e.g. event 386)
   directly into the Figure 3 diagnostic for a fully first-principles
   single-event reproduction, replacing the current parametric initial
   orientation.
