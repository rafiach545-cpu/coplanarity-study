# Phase 5 Launch Justification — event-count reconciliation

This document resolves the apparent discrepancy between the original
proposal's "~182,000" figure and this task's "~8,580" figure. **Both numbers
are real and internally consistent; they measure different things.** Neither
was quietly substituted for the other. Below, every quantity is defined
precisely and the full 91-point grid is tabulated.

## 1-5. The four distinct quantities, per distinct mass point

| Quantity | What it is | Depends on Λ? |
|---|---|---|
| N_generated | Raw LHE events requested from MadGraph | No — fixed at 2000/mass point regardless of how many Λ values will later reuse the sample |
| N_matched | Events surviving MLM matching (Pythia8 shower/matching step) | No |
| N_charge_filtered | Matched events with BOTH R-hadrons at ±1 charge (colored only; EW has no analogous filter — charge is fixed by the PDG code) | No |
| N_trigger | Events passing the trigger proxy (`quirk_pair_pT > 200 GeV`), computed from parton-level/matched kinematics | **No** — this is the crux of the reconciliation, see §6 |
| N_to_propagate | Events actually run through the expensive trajectory→detector→Sec IIIC/IV pipeline, **at a given Λ** | Yes, but the same underlying trigger-passing *event set* is reused at every Λ for a mass point |

**N_generated = 2000 for every one of the 13 distinct mass points, always**
(matches this project's existing per-benchmark statistical scale — see
`PAPER_FIGURE6_REQUIREMENTS.md` item 9 for the confirmation that Λ is a
post-generation-only parameter).

Per-mass-point projected values (full detail in
`tables/figure6_grid91_full.csv`; representative rows below — **all values
below N_generated are PROJECTIONS pending actual Phase 5 generation**, built
from a small number of directly-measured anchor points, disclosed as such):

| channel | mass (GeV) | N_generated | N_matched (proj.) | N_charge_filtered (proj., colored only) | N_trigger (proj.) | basis |
|---|---|---|---|---|---|---|
| EW | 100 | 2000 | 1200 | 1200 | 64 | match_eff 0.60 flat (measured 200/800 GeV); trig_eff linear-interpolated between measured 200 GeV (0.06) and Table I 800 GeV (0.10), extrapolated down |
| EW | 200 | 2000 | 1200 | 1200 | 72 | match_eff, trig_eff **directly measured this task** (n=500 throughput test: 0.646 matched, 0.068 of matched trigger) |
| EW | 800 | 2000 | 1200 | 1200 | 120 | match_eff measured (original 100-evt pilot, 0.60); trig_eff = Table I paper value (0.10), paper-quoted for this exact benchmark |
| EW | 1000 | 2000 | 1200 | 1200 | 136 | extrapolated |
| colored | 1500 | 2000 | 900 | 297 | 74 | match_eff/charge_eff/trig_eff **directly measured** (100-evt pilot: 0.43/0.372/0.25) |
| colored | 1800 | 2000 | 900 | 297 | 71 | match_eff measured (original 100-evt pilot, 0.49); trig_eff = Table I (0.24), paper-quoted for this exact benchmark |
| colored | 2400 | 2000 | 900 | 297 | 65 | match_eff/charge_eff/trig_eff **directly measured this task** (n=800 throughput test: 0.449/0.312/0.223) |

Only 2 EW points (200, 800 GeV) and 3 colored points (1500, 1800, 2400 GeV)
have directly measured or paper-quoted anchors. The other 8 mass points'
efficiencies are interpolated/held flat from these anchors — genuine
projections, to be replaced with real measurements as each mass point is
actually generated in Phase 5 (each generation run reports its own real
N_matched/N_charge_filtered/N_trigger, which supersede the projection for
that point immediately).

## 6-7. What "N_to_propagate" (~8,580 in the launch prompt, 7,714 revised
here) actually counts, and why it differs from 182,000

**It is neither raw generated events, nor matched events, nor fiducial
events. It is the number of calls to the expensive trajectory→detector→
Sec IIIC/IV reconstruction pipeline** — i.e. the compute-cost metric, not a
statistics metric. The statistics metric is N_generated (2000/mass point,
26,000 total) and its funnel (N_matched, N_charge_filtered, N_trigger).

**Why pre-filtering by trigger before propagation is mathematically exact,
not an approximation:** the trigger proxy is computed directly from the
matched-event 4-momenta (parton-level kinematics), which do not depend on Λ
(Λ only enters the post-production classical trajectory, Eq. 3-4). An event
that fails the trigger fails it identically at every Λ value and therefore
cannot pass the final Sec. IV selection (`final_sec_iv_pass` structurally
requires `sec3c_plane_found` and `hit_multiplicity_pass`, both of which are
downstream of — and gated by — the same event being in the analysis at all;
trigger is applied as a hard pre-selection in every stage of this project's
existing pipeline, not a soft weight). Running the expensive downstream
simulation on a trigger-failing event would produce a result that is
discarded regardless of Λ. Skipping it changes nothing about any table,
efficiency, or contour value — it only skips computation whose outcome is
already determined by data already in hand.

**Arithmetic reconciliation:**
- If NO optimization were applied (propagate every one of the 2000
  generated events, at every Λ, ignoring both the Λ-reuse insight AND the
  trigger pre-filter): 91 × 2000 = **182,000**. This is exactly the
  original proposal's headline number.
- Applying ONLY the Λ-reuse insight (13 distinct mass points generated
  once, not 91) but still propagating every generated event at every Λ
  regardless of trigger status: 13 × 2000 × 7 = **182,000** — the identical
  number, because 13×7 = 91 exactly. (This is a coincidence of the grid's
  own arithmetic, not evidence the two optimizations are the same thing.)
- Applying BOTH the Λ-reuse insight AND the trigger pre-filter (this
  project's actual, validated approach): Σ over 13 mass points of
  (N_trigger(mass) × 7) = **7,714** (revised, mass-dependent efficiency
  model — see §8 for why this supersedes the earlier flat-efficiency 8,580
  estimate used in the preflight report).

So: **182,000 was always the "no optimization" number, 7,714 (≈8,580 in the
earlier flat-efficiency estimate) is the "both optimizations applied"
number.** Both describe the same 91-point, 2000-events/point plan; they are
not competing plans, and the *statistical content* of the plan (2000 raw
events per mass point) has not been reduced. Only the *expensive-simulation
call count* dropped, and only because trigger-failing events are proven, not
assumed, incapable of affecting any final result.

## 8. Why 7,714 supersedes the earlier ~8,580 preflight estimate

The preflight report's 8,580 figure used Table I's two paper-quoted trigger
efficiencies (0.10 EW, 0.24 colored) FLAT across every mass point in that
channel. This task's own throughput-test measurements (EW 200 GeV: 0.068 of
matched; colored 2400 GeV: 0.223 of charge-filtered) showed real,
mass-dependent variation — lower trigger efficiency at lower EW mass (less
pT), and Table I's own two benchmark values are close to but not identical
to this project's own remeasurement of nearby points. The revised 7,714
figure replaces the flat assumption with mass-interpolated efficiencies
anchored to actual measurements, and is used for all remaining Phase 4/5
statements in this document.

## 9. Λ-reuse confirmation

Confirmed by direct code inspection (already stated in
`PAPER_FIGURE6_REQUIREMENTS.md` item 9): `Λ_gev` is a keyword argument to
`simulate_quirk_hits`, never a MadGraph `run_card`/`param_card` parameter for
these processes. Generation happens exactly 13 times (once per distinct
mass point); the same matched/trigger-passing event sample is reused,
unmodified, as the starting 4-momenta for trajectory propagation at each of
that mass point's 7 Λ values.

## 10. Complete 91-row grid table

Saved in full at `tables/figure6_grid91_full.csv` (91 rows × columns:
channel, mass_gev, lambda_kev, N_generated, N_matched_expected,
N_charge_filtered_expected, N_trigger_expected, N_to_propagate,
generation_seed, downstream_seed_base, checkpoint_path).

**Grid correction disclosed here explicitly:** the original EW mass list
proposed 200-1200 GeV; Phase 0's paper reread found the paper's own Fig. 6
EW-panel axis is 0-1000 GeV, so 1200 GeV was out of range. To preserve the
originally-committed **6 EW mass points** (not silently drop to 5), **100
GeV was added at the low end** (extending the original series' 200 GeV
spacing downward instead of upward past the axis limit) rather than simply
deleting 1200 GeV. Final EW list: 100, 200, 400, 600, 800, 1000 GeV (6
points). Colored list unchanged: 600, 900, 1200, 1500, 1800, 2100, 2400 GeV
(7 points, within the paper's 500-2500 GeV axis). Total: 6×7 + 7×7 = 42 + 49
= **91**, matching the original commitment exactly.

Seed scheme: `generation_seed` (9400-9412, distinct per mass point, outside
the pilot's 920x and throughput-test's 930x ranges) governs MadGraph/Pythia8
generation. `downstream_seed_base` + row-local `SeedSequence.spawn()` offset
(the scheme validated this task on 47 real events, both correct and
deterministic — see §15) governs per-event RNG for trajectory/detector
smearing, distinct per (mass, Λ) block so no two grid cells share a
downstream RNG stream.

## 11-12. Statistical precision and sufficiency verdict

95% Wilson-interval half-width on ε_reco, as a function of N_to_propagate
(the sample size at a given grid cell) and assumed true ε_reco (Table I's
own observed range is 0.083-0.74):

| N | ε_reco≈0.1 | ε_reco≈0.3 | ε_reco≈0.5 | ε_reco≈0.7 |
|---|---|---|---|---|
| 50 | ±0.085 (85% rel) | ±0.123 (41% rel) | ±0.134 (27% rel) | ±0.123 (18% rel) |
| 100 | ±0.060 (60% rel) | ±0.088 (29% rel) | ±0.096 (19% rel) | ±0.088 (13% rel) |
| 200 | ±0.042 (42% rel) | ±0.063 (21% rel) | ±0.069 (14% rel) | ±0.063 (9% rel) |
| 300 | ±0.052 (17% rel, at N=300 eps=0.7) | | | |

This grid's N_to_propagate per mass point ranges **64-136** (EW) and
**65-83** (colored) — see §13. At Table I's peak-efficiency Λ values
(ε_reco ~0.6-0.74, near Λ=4-5 keV), relative precision at these sample
sizes is **roughly 15-25%** — adequate to trace a contour's central shape.
At Table I's lowest-efficiency Λ (1 keV, ε_reco 0.083-0.11), relative
precision at the same N is **50-85%** — genuinely weak, and expected: this
is the paper's own least-efficient corner too, not a defect introduced by
this project's sample size.

**Verdict on sufficiency:** 2000 generated events per mass point is the same
statistical scale already validated and used for every other benchmark
result in this project (not a reduced or pilot-level sample). It gives
adequate precision (rel. unc. ~10-30%) across the bulk of the grid, and weak
(rel. unc. 40-85%) precision at the grid's own least-efficient corners
(lowest Λ, and to a lesser extent the lowest-mass EW point) — a limitation
inherent to the physics (matching the paper's own described efficiency
degradation at Λ=1 keV, Table I), not a flaw in the plan. **This is
sufficient to construct the qualitative contour shape and an honestly-wide
uncertainty band at the edges; it is not sufficient to claim precision
matching the paper's own (unpublished, likely much larger) sample size at
the contour boundary itself.**

## 13. Grid points likely to have few propagated events

Lowest N_trigger (shared across all 7 Λ for that mass point):

| channel | mass (GeV) | N_trigger (proj.) |
|---|---|---|
| EW | 100 | 64 |
| colored | 2400 | 65 |
| colored | 2100 | 68 |
| colored | 1800 | 71 |
| EW | 200 | 72 |

Additionally, **every mass point at Λ=1 keV** will have the lowest
downstream-yield fraction within its own Λ series (Table I: ε_reco = 0.11
EW / 0.083 colored at Λ=1 keV, roughly 3-9x lower than the peak). Combining
EW 100 GeV with Λ=1 keV is the single most statistics-starved cell in the
grid (expected final-pass count could plausibly be 0-2 events at N_generated
=2000) — flagged explicitly, not hidden. Per Phase 7's failure policy, any
cell landing at N_final=0 will be labeled incomplete/zero-count, not
silently interpolated over.

## 14. Confirmation: no cuts or counts reduced to fit the runtime limit

N_generated remains 2000/mass point, unchanged from the original proposal,
for all 13 mass points. No Sec. III C or Sec. IV cut, tolerance, or
threshold was altered. The only change from the "182,000" framing is
skipping trajectory propagation for events already known (via a
Λ-independent, already-computed trigger flag) to fail the analysis
regardless of Λ — a compute optimization proven exact in §6, not a
statistical reduction.

## 15. Parallel RNG determinism confirmation

Validated this task on 47 real trigger-passing events (`THROUGHPUT_TEST_RESULT.json`):
- `all_match_serial: true` — 3-worker parallel output bit-identical to
  serial output for the same per-event seed.
- `all_match_rerun: true` — two independent parallel runs bit-identical to
  each other.
Mechanism: `numpy.random.SeedSequence(downstream_seed_base).spawn(n_events)`
generates independent, high-quality child seeds per event index, assigned
before dispatch — not dependent on which worker or completion order a job
lands in. This is the numpy-recommended approach for parallel Monte Carlo
and does not alter the RNG algorithm itself (still `default_rng`/PCG64), only
which independent stream each event draws from.

## 16. Projected CPU/RAM/disk/wall time

| | Serial | Parallel (3 workers) |
|---|---|---|
| CPU | 1 of 4 cores | 3 of 4 cores (1 free for OS/monitoring) |
| Downstream wall time | 7714 × 12.33s = 26.4h | 7714 × 5.10s = 10.9h |
| + Generation (unchanged, unaffected by parallelization) | 12.72h | 12.72h |
| **Total wall time** | **39.1h** | **23.6h** |
| RAM | <1GB observed | ~1.5-3GB projected (3 lightweight numpy/pandas worker processes; current baseline 1.4GB used / 7.6GB total) |
| Disk | ~2GB projected (858MB generation outputs at 13×2000 events, scaled from throughput-test's 20-23MB/500-800-event runs; ~1GB downstream per-event artifacts at 7714 events, scaled from the 3-point pilot's 130KB/event) | same |

Both totals are well under the 60h stop-gate (Phase 7).

## 17. Checkpointing / crash-resume confirmation

Validated this task and the prior three-point pilot:
- Downstream: per-event atomic JSON checkpoint (`checkpoints/*/progress.json`),
  confirmed idempotent — a full pipeline rerun after completion produces
  `SKIP (already checkpointed)` for every event with zero redundant physics
  work (three-point pilot, 10/10 events).
- Generation: per-mass-point isolated run directories with
  `checkpoints_DONE_generation.txt` atomic markers written only after exit
  code 0; a failed attempt is renamed
  `FAILED_ATTEMPT_NOT_AUTHORITATIVE_<n>` and never overwritten in place
  (used this task when the PYTHIA8DATA bug caused 2 failed generation
  attempts before the fix).
A crash mid-grid resumes from the next incomplete (mass, Λ) cell without
regenerating or reprocessing any already-checkpointed work.

## Final verdict

**STATISTICALLY SUFFICIENT — SAFE TO LAUNCH**, with the following explicit,
disclosed caveats carried into the Phase 6-10 writeup (not hidden):
- 8 of 13 mass points' matching/charge/trigger efficiencies are projections
  from a small number of measured anchors, to be replaced with real,
  per-point measurements as Phase 5 generation actually runs each one.
- The grid's own least-efficient corners (Λ=1 keV generally, EW 100 GeV
  specifically) will carry wide (40-85% relative) statistical uncertainty,
  inherent to the physics, not a plan defect.
- Total revised runtime: 23.6h (parallel, 3 workers) to 39.1h (serial
  fallback), both under the 60h stop-gate — no reduction in N_generated,
  cuts, or grid points was made to reach this.

## Addendum (during production, 2026-09-22): confirmed Λ² per-event cost scaling

Real production data at EW 100GeV (the grid's lightest mass point) revealed
per-event downstream cost scales as **Λ²/mass**, confirmed empirically
(measured k=rate/Λ² consistent to within ~10% across Λ=2-5 keV: k≈5.0-6.1,
average 5.467) and matching the integrator's own timestep-sizing logic
exactly: `period_est ∝ mass/Λ²`, and for a fixed geometric flight-time to
the outer detector layer, required step count ∝ 1/period_est ∝ Λ²/mass.

This was **not characterized during pre-launch validation** — both the
three-point pilot and the larger 47-event throughput test used Λ=2 keV
exclusively, never sampling the grid's higher-Λ (7, 10 keV) cells.

Extrapolating this confirmed model across the full 91-point grid (using the
EW 100GeV measurement as the worst-case anchor, scaled by 1/mass for every
other point) gives a **revised total projected downstream time of ~11.8h
parallel (3 workers) + ~0.9h generation (already measured) ≈ 12.7h total**
— comfortably under the 60h gate, and below the original ~24.9h estimate.
This is because EW 100GeV, being the lightest mass in the entire grid, is
specifically the most expensive point; every other point (especially the
600-2400 GeV colored points) is expected to be substantially cheaper per
event under this confirmed model.

No physics constant, cut, or tolerance was changed in response to this
finding — it is a cost-model discovery, not a plan revision.
