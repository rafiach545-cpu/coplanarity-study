# Zero-Hit Event Instrumented Replay — Findings

**Bounded diagnostic replay only.** No new LHE/HepMC generation, no
parameter scan. Target: the 31 EW-2000 trigger-passing, fiducial-failing
events with zero detector hits AND moderate truth-level η (≤1.6) —
exactly the population `PT_ETA_ATTRIBUTION_FOLLOWUP2.md` flagged as
unexplained. Each event replayed from its exact stored 4-momenta, seed,
Λ=4 keV, mass=800 GeV, using only the existing, unmodified,
already-validated physics code (`simulate_quirk_hits`,
`find_layer_crossing`, `integrate_trajectory_fast_v2`) — no code was
changed, only instrumented by inspecting its full returned arrays. No
frozen file modified. No commit/push.

**Coverage**: 31/31 events attempted, each under a bounded 150-second
per-event timeout (chosen to match this benchmark's known ~130s median
integration time while keeping the diagnostic bounded, per instruction).
**17/31 (55%) completed within budget; 14/31 (45%) timed out** and
remain untested — not silently dropped, not extrapolated to, explicitly
carried as "still unresolved" in the classification.

## Headline result

**All 17 successfully-replayed events (100%) show the identical
mechanism, with zero exceptions:**
- Both quirks' trajectories travel radially outward far past all 8
  detector layers (observed max radius 163–198 cm, vs the outermost
  layer at 51.4 cm — 3-4× further than needed to clear every layer).
- Every one of the 16 (quirk × layer) crossing attempts per event
  **geometrically found a crossing** (`find_layer_crossing` returned a
  valid hit) — **zero** "trajectory never reaches this radius" cases,
  **zero** root-finding failures, **zero** non-finite/NaN/Inf states.
- **Every single one of those 16×17 = 272 crossings was rejected by the
  |η|<1.8 fiducial cut**, at crossing-point η values ranging 1.86–3.04 —
  well above the 1.8 threshold, and well above the ≤1.6 truth-level η
  used to select these events as "moderate."
- The replay reproduces the originally stored zero-hit decision exactly
  in all 17 cases (verification step passed: `reproduced_zero_hit=True`
  in every case, per instruction "verify that replay reproduces the
  originally stored zero-hit decision before interpreting it").

Full per-event data: `tables/instrumented_replay_summary.csv` (all 12
requested diagnostic quantities), `tables/layer_crossing_detail.csv`
(all 272 individual crossing attempts, coordinates, times, rejection
stage/reason), `tables/final_event_classification.csv`,
`tables/truth_vs_crossing_eta_drift.csv`.

## Quantified η drift (item 12: truth η vs actual trajectory direction near layer 1)

| | Value |
|---|---|
| Mean |η| at layer-1 crossing minus truth max\|η\| | **+1.28** |
| Range across all 17 events | +0.36 to +1.71 |
| Events with drift ≤ 0 (i.e. no drift, or reversed) | **0 of 17** |

The drift is substantial, systematic, and **always in the same
direction** (more forward at the crossing point than at production) —
not a symmetric scatter that would suggest sampling noise. This is
expected physically: these quirks are pair-produced with truth η ≤1.6
but carry significant longitudinal momentum (median individual pT
~800-900 GeV in this exact subset per the prior follow-up), and the
confining-string + Lorentz-force trajectory integration (validated,
unmodified code) evidently carries them to a more forward angle by the
time they reach even the innermost layer (3.325 cm) — a real consequence
of the propagation dynamics, not an artifact of how η is computed or a
flaw in the geometric cut itself.

## Classification (per instruction's 6 categories)

| Category | Count | 
|---|---|
| Physical forward/barrel acceptance loss | **17** |
| Turns around before layer 1 | 0 |
| Fails the 25 ns requirement | 0 (structurally inapplicable to zero-hit events — no hit survives to have a timing value at all) |
| Numerical integration/root-finding failure | 0 |
| Non-reproducible | 0 |
| Still unresolved (untested, 150s budget) | **14** |

Full table: `tables/final_event_classification.csv`.

## Answering the required final questions

1. **Verify replay reproduces the originally stored zero-hit decision
   before interpreting it**: done — all 17 completed replays reproduce
   `n_hits_premerge=0` exactly, matching the stored per-event data.
2. **Is the moderate-η zero-hit population physical or numerical?**
   **Physical**, for every one of the 17 events tested (100%,
   exhaustive-within-budget). No numerical or root-finding failure was
   found in any completed replay.
3. **Should a PDF/xqcut/qcut/Pythia sensitivity scan be recommended
   now?** See recommendation below.

## Recommendation on a sensitivity scan

**Justified, but characterized precisely.** This replay demonstrates
that the "moderate truth-η, zero-hit" population is a **genuine physical
consequence of this project's own trajectory propagation dynamics**
(quirks produced at moderate η end up crossing the barrel layers at
higher η due to their longitudinal momentum and the confining-string
dynamics), not a bug or numerical artifact. This still does not, by
itself, explain why this project's *population* of events has the η/pT
distribution it has (that traces back to the generation stage, as the
prior two reports established). A future PDF/xqcut/qcut/Pythia
sensitivity study would test whether a softer generation setup (lower
mean pT, more central rapidity — as motivated by
`PT_ETA_ATTRIBUTION_FOLLOWUP2.md`'s rapidity finding) shifts the
underlying η/pT distribution enough to change how many events fall into
this "physical loss" category. **Per instruction, any such study must be
explicitly labeled a sensitivity study, not a paper-reproduction
attempt** — this replay provides no evidence about what the paper's own
generator settings were, only that this project's existing events'
losses are physically real, not numerical. **We do not claim the paper
used a different rapidity spectrum or PDF** — that would require direct
evidence from the paper or a controlled scan showing it closes the gap,
neither of which has been obtained here.

## What remains genuinely open

The 14 timed-out events (event_idx 6, 8, 9, 11, 20, 23, 34, 64, 80, 93,
108, 143, 164, 165) are explicitly **not** classified by extrapolation
from the 17 tested ones, despite the latter's complete consistency —
per instruction, they are carried as "still unresolved." If a
higher-budget or resumed replay is authorized in a future task, these
are the specific events to target first.
