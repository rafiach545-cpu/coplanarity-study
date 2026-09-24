# Figure 6 Full Implementation — Preflight Report

**UPDATE (post-investigation, supersedes Section 5 below for the runtime
verdict — original Section 5 kept unmodified beneath for audit trail):**

Per user direction, the runtime blocker in Section 5 was investigated rather
than accepted at face value. Two findings:

1. **Root cause of the outlier-driven 43-61h projection identified and
   resolved by better sampling, not by changing anything physics-related.**
   The original three-point pilot's 20.3 s/event mean downstream rate was
   dominated by a single outlier (one event out of 10, needing genuinely
   ~2.4M physics-required RK4 steps at the validated 300-steps/period
   accuracy floor — confirmed via cProfile, not a bug). A larger, more
   representative sample (47 real trigger-passing events, freshly generated
   at n=500/800 requested LHE events for EW_200GeV and colored_2400GeV) gives
   a much better-conditioned mean: **12.33 s/event serial**, not 20.3.
2. **A genuine, separate infrastructure bug was found and fixed while
   generating that larger sample**, documented in full in
   `THROUGHPUT_TEST_RESULT.json` and the task conversation: `conda activate
   hep` unconditionally exports `PYTHIA8DATA` pointing at the conda
   package's own Pythia8 install (8.312), while MadGraph's compiled shower
   executables are linked against its own bundled `HEPTools/pythia8`
   (8.317) per `mg5_configuration.txt`. This mismatch aborts Pythia8
   showering above roughly 100 events (where MadGraph's job-splitting
   engages) with `PYTHIA Abort: unmatched version numbers, in code 8.317
   but in XML 8.312`. Fix: `unset PYTHIA8DATA` immediately before invoking
   `./bin/generate_events`, scoped to that one subprocess call only — the
   conda env's own `PYTHIA8DATA` is left untouched for every other use in
   this project (e.g. the Pythia8 python bindings used by
   `_make_rhadron_charge_lookup()`, which are self-consistent within the
   conda env and unaffected). Verified: both throughput-test generations
   (EW_200GeV n=500, colored_2400GeV n=800) completed cleanly with this fix,
   producing normal matching efficiencies (64.6% EW, 44.9% colored,
   consistent with the original 100-event pilot's 60%/42-43%).

**Parallelization (the fix requested by the user) was also validated on
this larger, 47-event sample:** 3 worker processes (1 core left free on this
4-core machine), correctness confirmed (parallel output bit-identical to
serial for matching seeds), determinism confirmed (two parallel reruns
bit-identical to each other), measured speedup **2.23-2.64x** (avg ~2.4x),
giving parallel rate **5.10 s/event**.

**Revised total runtime projection**, using the ~8,580-downstream-event
estimate from Section 5 below (unchanged methodology) with these
directly-measured rates:

| | rate (s/event) | downstream total | + generation (12.72h) |
|---|---|---|---|
| Serial | 12.33 | 29.4h | **42.1h** |
| Parallel (3 workers) | 5.10 | 12.2h | **24.9h** |

Both are comfortably under the 60h stop-gate — even the serial fallback.
**Verdict: the runtime blocker is resolved. Phase 4/5 can proceed**, using
the parallel downstream pipeline (validated correct + deterministic) and the
`unset PYTHIA8DATA`-scoped generation fix. No physics, cuts, tolerances, or
grid design were changed to reach this conclusion — the resolution was
better sampling (fixing a measurement artifact) plus two legitimate
engineering fixes (an environment bug affecting generation, and safe
multi-core parallelization of independent events).


## 1. No simulation currently running

`pgrep -fal "madgraph|pythia|mg5"` returns nothing (only the check command
itself). Confirmed clean.

## 2. Hardware

- CPU: **4 cores** (`nproc`).
- RAM: **7.6 GiB total, 5.3 GiB free, 2.0 GiB swap, 0 swap used**.
- Disk: **945 GiB free / 1007 GiB (2% used)** — ample for this task.

This is a modest, shared machine. 91 grid points run strictly sequentially
(per this project's established convention, carried over from the
three-point pilot) will not stress RAM/disk, but wall-clock time is the
binding constraint, addressed below.

## 3. Toolchain / environment

- `hep` conda environment: unchanged, used for all pilot work, confirmed
  working (three-point pilot ran successfully in it).
- `mg5_build_tools` conda environment: available if any process directory
  needs recompilation (not expected — mass-only edits do not trigger
  recompilation, confirmed in the three-point pilot).
- Optimized-v2 trajectory integrator (`quirk_trajectory_optimized_v2.py`,
  commit `3c33601`): validated bit-identical to baseline in both the
  isolated `perf_profile_v1` self-test and, this task, on 3 real pilot
  events (Δs diff = 0.0 in all 3, speedups 9.8–14.1x).
- Checkpoint/resume logic (`run_downstream_pipeline.py` pattern): verified
  idempotent in the three-point pilot (full rerun after completion produced
  10/10 `SKIP (already checkpointed)`, no duplicate or altered results).

## 4. Grid (per existing proposal, `Figure_6_future_work_grid_proposal_v1.md`)

- 7 colored mass points, 6 EW mass points, 7 Λ values = **91 total
  (mQ, Λ) combinations**.
- **Correction from this task's paper reread:** the existing EW mass list
  (200–1200 GeV) includes 1200 GeV, which falls **outside** the paper's own
  Fig. 6 EW-panel axis range (0–1000 GeV, confirmed by direct reading of the
  Fig. 6 axis labels, p.9). This is flagged for correction in Phase 2/3 (drop
  1200 GeV, keep 6 EW points within 0–1000 GeV) before grid finalization.
  Colored mass list (600–2400 GeV) is within the paper's stated axis
  (500–2500 GeV, p.9) — no correction needed there.
- Confirmed (Sec. II, p.2 and code inspection): Λ requires no new MadGraph
  generation — only 13 distinct mass points need generation; each is reused
  across all 7 Λ values via trajectory re-integration only.

## 5. Runtime — critical finding: the existing 37.9h estimate does not match this pilot's real measurement

The most recent pre-existing estimate
(`perf_profile_v1/runtime/REVISED_FIGURE6_ESTIMATE.json`) is:
- generation: 12.72h (measured, 100-event pilot, scaled to 13 mass points × 2000 events)
- downstream: 25.2h (**not measured end-to-end** — derived by rescaling an
  old 425h estimate by a 16.87x speedup factor measured in isolation on the
  trajectory-integration call only, via `profile_pipeline.py`)
- total: **37.9h**

This task's own three-point pilot (Phase 4-equivalent work already done)
measured the **full** downstream chain end-to-end (integration + detector
hits + Sec. IIIC seeding/iterative fit + Sec. IV cuts + CSV I/O) on 10 real
trigger-passing events, using the same optimized-v2 integrator:

- mean wall time per downstream event: **20.3 s** (including one 86.9 s
  outlier at colored_2400GeV) or **12.9 s** (excluding that outlier)
- this is **26–41x higher** than the 0.5 s/event implied by the existing
  37.9h estimate.

**Root cause (assessed, not yet independently reprofiled in isolation this
task):** the 16.87x speedup factor used for the old estimate was measured on
`integrate_trajectory` calls alone. The Sec. IIIC seeding/candidate search
and iterative plane fit (`seeding_and_iterative_fit`, a separate,
non-integrator algorithm) is not accelerated by the optimized-v2 integrator
and appears to dominate total per-event wall time — consistent with the
large event-to-event variance seen in the pilot (4.1s to 86.9s), which
tracks candidate/hit-count variation, not integration cost (integration
step count is roughly fixed per Λ/mass).

### Recomputed downstream-event count and runtime

Using Table I's own trigger efficiencies (ε_trig = 0.10 EW, 0.24 colored,
more statistically robust than this pilot's own noisy N=100 estimate) and
this pilot's measured matching/charge-survival efficiencies, projected at
2000 events/mass point:

| | per mass point | × Λ (7) | × mass points | total downstream events |
|---|---|---|---|---|
| EW | ~120 trigger-passing | 840 | ×6 masses | ~5,040 |
| Colored | ~72 trigger-passing | 504 | ×7 masses | ~3,528 |
| **Total** | | | | **~8,580** |

At the pilot's measured rate:
- **30.7h** (outlier excluded) to **48.3h** (outlier included) for the
  downstream stage alone, strictly serial on 1 core.
- Plus 12.72h generation (unaffected by this finding).
- **Revised total: ~43.4h to ~61h**, i.e. straddling directly across the
  60-hour stop threshold set explicitly for this task, and well above the
  previous 37.9h figure.

This is a genuine, pilot-measured discrepancy, not a hypothetical one. Per
this task's own Phase 4 rule ("If validation fails, stop before full
production and report the blocker") and Phase 7 rule ("If projected runtime
exceeds 60 hours... report the measured bottleneck and request authorization
before changing event counts or grid design"), **production is not launched
in this pass.** The trigger-fraction inputs above come from a 100-event
pilot (large relative statistical uncertainty) and Table I values for two
specific benchmark points only (not the full grid), so the true figure could
land anywhere in a wider band around 43–61h+; it should not be read as a
precise number, only as evidence that the old 37.9h figure is not reliable
and that the true cost is at or above the stated stop-gate.

## 6. Expected output size

At ~8,580 downstream events with per-event hit/plane CSVs plus one compact
summary/cache row each (similar structure to the three-point pilot, which
used 1.3 MB for 10 events, i.e. ~130 KB/event including cards/logs): rough
order **~1.1 GB** for the full grid's per-event artifacts, well within the
945 GB free. Not a constraint.

## 7. Working directory / seed scheme

- Working directory: `05_coplanarity_analysis/figure6_full_v1/` (this task),
  final consolidated output later moved/copied to
  `05_coplanarity_analysis/FIGURE6_FINAL_IMPLEMENTATION_v1/` per Phase 11.
- Seed scheme (to be finalized in Phase 3's `SEED_REGISTRY.csv`): one
  distinct MadGraph/Pythia generation seed per of the 13 mass points
  (extending the pilot's 9201-9203 scheme, e.g. 93xx range to avoid
  collision with any prior seed used in this project), one distinct
  downstream RNG stream per (mass, Λ) combination (91 total) so that
  detector-smearing randomness is reproducible and non-repeating across
  Λ values sharing the same generated events.

## 8. Verdict

**BLOCKED pending authorization**, per this task's own explicit stop-gate
rules — not a silent or unilateral pause. Phase 0 (paper reread,
requirements matrix, this preflight) is complete. Phase 1 (cleanup),
Phase 2-3 (physics definition, grid finalization) can proceed safely
regardless of the runtime question and are not blocked. Phase 4
(preproduction validation) and Phase 5 (production launch) should not start
until the runtime/authorization question is resolved with the user, since:

1. The measured (not estimated) downstream-stage cost is markedly higher
   than previously assumed.
2. The revised total (~43–61h+) sits at or above the 60h stop-gate the task
   itself specifies.
3. This machine has only 4 cores / 7.6 GiB RAM — a 43-61+ hour unattended
   serial run is a large, hard-to-reverse-in-practice time commitment on
   shared, modest hardware, and this task explicitly requires authorization
   before changing event counts or grid design in response to such a
   finding, rather than silently deciding for the user.

No physics cuts, tolerances, or grid design were altered to make the
runtime look more favorable.
