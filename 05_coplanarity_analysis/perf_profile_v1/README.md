# Bounded performance profile of the Figure 6 downstream pipeline (v1) — 2026-09-21

## Bottleneck: unambiguous, 7/7 diverse events, 99.96–99.98% of wall time

`integrate_trajectory` (RK4 propagation, `quirk_trajectory.py`) dominates
completely. Detector hit-building, smearing, merging, and reconstruction
combined account for **<0.03%** of total wall time. Confirmed across all
7 profiled events (colored + EW, low + high boost, 2 Λ values for
colored) — no exceptions.

**Mechanistic explanation** (not just correlation): step count scales as
`t_max/dt`, where `dt` targets a validated 300-steps-per-period floor and
`period ~ 1/Λ²` (Eq.4). Higher Λ → shorter period → more steps needed to
cover the same physical flight time. Confirmed empirically: colored event
236 at Λ=5keV took 7.1× longer than at Λ=2keV (1429s vs 201s), consistent
with the (5/2)²=6.25 scaling expectation.

## Coverage note (honest, not full 16-run grid)

The originally-planned 16-run grid (8 base events × 2 Λ each) was cut
short after a hard 45-minute time cap — individual runs ranged 114s to
1429s, and completing all 16 could have taken many more hours, which is
not "bounded." **6 diverse runs completed** (colored: events 236 at both
Λ values, 322, 34; EW: events 438, 417) spanning both benchmarks, both
boost classes, and 2 Λ values for colored. The bottleneck conclusion is
statistically overwhelming already at this sample size (7/7 including one
extra single-Λ probe, 99.96–99.98% RK4 share, near-zero variance) and did
not need the full 16 runs to establish.

## Optimization implemented (separate versioned files, baseline untouched)

- `03_trajectory_sim/quirk_trajectory_optimized_v1.py` — eliminates
  `QuirkPairState` object-construction and function-call-layering
  overhead. **3.5× speedup, bit-identical output** (synthetic test).
- `03_trajectory_sim/quirk_trajectory_optimized_v2.py` — pure-Python-float
  variant (avoids numpy per-call dispatch overhead on 3-element arrays
  entirely; same IEEE-754 double arithmetic, same order of operations).
  **17.9× speedup, bit-identical output** (synthetic test). This is the
  version used for the full validation below.
- `trajectory_cache_v1.py` — disk cache keyed by a hash of the exact
  physics inputs (4-momenta, mass, Λ, B, charges, seed). Cache hits are
  bit-identical to a fresh computation, 47× faster than recomputing.
  Protects against wasted recomputation during grid preparation,
  checkpointed reruns, and debugging — does not reduce a single fresh
  grid's own cost (every point is still computed once).

**Neither `quirk_trajectory.py` nor `trajectory_to_hits.py` (the
validated baseline files) were modified.** The optimized integrator was
swapped in for validation via monkey-patching
`trajectory_to_hits.integrate_trajectory` after import (rebinding a
module-level name, not touching the file on disk) — the exact same,
unmodified detector-response/hit-building/reconstruction code runs either
way.

## Priority-list coverage

1. **Prefiltering trigger/truth-fiducial failures**: trigger prefiltering
   is already baseline architecture (Stage 3's cut is applied before
   Stage 1/2 propagation, per `CUTS_AND_PIPELINE.md`) — confirmed
   unchanged, not re-implemented. Truth-fiducial prefiltering is not
   possible before propagation (it depends on the propagated trajectory,
   which depends on Λ) — not applicable here.
2. **Reusable trajectory/raw-hit caches**: implemented (`trajectory_cache_v1.py`).
3. **Eliminating repeated calculations**: implemented (v1 — object/
   function-call overhead removed).
4. **Safe vectorization**: implemented, in the sense that matters for
   arrays this small — v2 REMOVES numpy vectorization overhead (numpy's
   per-call dispatch on 3-12 element arrays is slower than plain Python
   float arithmetic at this scale; there is no useful SIMD/array
   vectorization opportunity here since RK4 is inherently sequential in
   time, each step depends on the previous one).
5. **Parallel execution**: NOT implemented this task (time-bounded). Note
   for a future task: `integrate_trajectory` has **no RNG dependency at
   all** (fully deterministic given momenta/mass/Λ/charges/B) — the RNG
   is only used in `simulate_quirk_hits` for beamspot z0 and pixel
   smearing, both AFTER the trajectory is returned. This makes
   parallelizing across independent (event, Λ) grid points trivially
   safe with no RNG-independence work needed; recommended as the next
   optimization step if the revised estimate below still isn't fast
   enough for the intended use.

## Validation: exact agreement, real speedup

Full pipeline (via monkey-patched integrator) run on all 6 profiled
events, reusing the already-computed baseline hits/plane from the
profiling run (not recomputed — applying "eliminate repeated
calculations" to the validation step itself, saving ~50 minutes):

| Check | Result |
|---|---|
| Discrete outputs (n_postmerge, plane_found, hit_multiplicity, final verdict) | **6/6 exact match** |
| Hit coordinates (x,y,z,t_ns) | **6/6 bit-identical** (0.0 diff) |
| Δs, Δw | bit-identical (a 2-event ~1e-17 "diff" in the first pass was traced to the validation script's own CSV-round-trip precision loss when redundantly recomputing baseline Δs, not a real difference — corrected, see `comparisons/VALIDATION_SUMMARY.json`) |
| Speedup | 14.09×–19.57×, mean **16.87×** |

`tests/test_optimized_trajectory_agreement.py`: 19/19 checks pass,
including one honestly-documented edge case (exactly-antiparallel,
exactly-equal-magnitude momenta — never occurs in real MadGraph data)
that agrees to 4.44e-16 absolute (2 ULPs) rather than bit-identical,
with a stated 1e-14 tolerance.

## Revised Figure 6 runtime estimate

| | Hours |
|---|---|
| Old downstream (trajectory+detector+reconstruction) estimate (Phase 7) | 425.0 |
| **Revised downstream estimate** (425.0h / 16.87×) | **25.20** |
| Generation stage (unchanged, separate bottleneck, from `madgraph_pilot100_generation_v1/`) | 12.72 |
| **Revised TOTAL Figure 6 estimate** | **37.92h** |
| Old total | 437.7h |
| **Reduction** | **91.3%** |

**Caveat, stated explicitly**: this rescales the previously-verified 425h
estimate by a speedup factor measured on 6 representative points, not a
re-measurement of the full 91-point grid (not launched, per the explicit
stop instruction). The speedup was highly consistent across all 6
(14.09×–19.57×, no systematic dependence on benchmark/boost-class/Λ
observed), supporting this extrapolation, but it is an estimate, not a
direct measurement of the full grid.

## Files
- `profile_pipeline.py`, `profile_supplement.py` — profiling harness (cProfile-based, exact baseline code path)
- `profiles/` — per-event profiles, baseline hits/plane CSVs, `PROFILE_SUMMARY_BASELINE.csv`. **Known gap**: `*_full_cprofile.txt` dumps are empty (0 bytes) — `pstats.Stats.print_stats()` was never called on the stream (only `.stats` dict was read, which correctly populated every number reported in this README and in `BOTTLENECK_IDENTIFICATION.json`). Not re-run to fix this cosmetic gap, given the expensive baseline runs it would require re-executing (114s-1429s each).
- `runtime/BOTTLENECK_IDENTIFICATION.json`, `REVISED_FIGURE6_ESTIMATE.json`
- `validate_optimized_pipeline.py` — end-to-end old-vs-optimized validation
- `comparisons/` — per-event comparison CSVs, `VALIDATION_SUMMARY.json`, `HIT_COORDINATE_COMPARISON_CORRECTED.csv`
- `trajectory_cache_v1.py` — disk cache module
- `tests/test_optimized_trajectory_agreement.py` — 19/19 passing regression test

## What was NOT done (per explicit instruction)

No Figure 6 grid launched. Baseline files (`quirk_trajectory.py`,
`trajectory_to_hits.py`, `coplanarity_fit.py`) were not modified. Parallel
execution was not implemented (noted as a viable future step). The full
16-run profile grid was not completed (6 diverse runs were sufficient to
establish the bottleneck with statistical certainty).
