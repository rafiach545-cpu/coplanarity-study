# Figure 6 Three-Point Pilot — Report v1

**Purpose:** validate the full generation → trajectory → detector → reconstruction
pipeline and measure per-event runtime at a small number of mass points, using the
validated optimized-v2 trajectory integrator, before any decision is made about
launching the complete Figure 6 grid. This pilot does **not** attempt a Figure 6
reproduction.

**Directory:** `05_coplanarity_analysis/figure6_three_point_pilot_v1/`
**SHA-256 manifest:** `SHA256_MANIFEST.txt` (68 files, computed after all pilot
outputs were finalized, no process running, `git status` clean of any competing
write).

## 1. Points run

Three points only, chosen from previously-proposed grid mass values, satisfying
"low/central/high mass, ≥1 EW + ≥1 colored":

| Point | Benchmark | Mass | Λ (GeV) | Seed | Source card directory (immutable template) |
|---|---|---|---|---|---|
| EW_200GeV | EW | 200 GeV | 2×10⁻⁶ | 9201 | `quirk_ew_800gev_4kev/` (mass edited only) |
| colored_1500GeV | colored | 1500 GeV | 2×10⁻⁶ | 9202 | `quirk_signal_1800gev_2kev/` (mass edited only) |
| colored_2400GeV | colored | 2400 GeV | 2×10⁻⁶ | 9203 | `quirk_signal_1800gev_2kev/` (mass edited only) |

Each point was produced by `rsync`-copying an already-compiled MadGraph process
directory (excluding prior `Events/run_01`), then editing only
`Cards/param_card.dat` (mass) and `Cards/run_card.dat` (`nevents=100`, `iseed`).
No matrix-element recompilation was required (mass is a runtime parameter, not
compiled into the process). SHA-256 checks before/after confirmed the original
template directories' banners were untouched (byte-identical to the
`madgraph_pilot_v1/SHA256_MANIFEST.txt` entries recorded previously).

Λ = 2×10⁻⁶ GeV is a **PROJECT ASSUMPTION carried over from prior pilot work**,
not re-derived here — this pilot reuses it for consistency with previously
validated trajectory-integration behavior, not because the paper specifies this
exact value for these particular mass points.

Execution was strictly sequential (point 1 fully completed, including
downstream analysis, before point 2 was started, etc. — enforced by the
single-process, per-point directory structure and checkpoint markers).

## 2. Generation results (100 events requested per point)

| Point | LHE events | Matched events | Matching eff. | Parton xsec (pb) | Matched xsec (pb) | Wall time | Seed | Exit |
|---|---|---|---|---|---|---|---|---|
| EW_200GeV | 100 | 60 | 60.0% | 0.15886 ± 0.00093 | 0.09531 ± 0.00780 | 327.64 s | 9201 | 0 |
| colored_1500GeV | 100 | 43 | 43.0% | 0.003936 ± 0.0000229 | 0.001692 ± 0.000195 | 41.49 s | 9202 | 0 |
| colored_2400GeV | 100 | 42 | 42.0% | 0.0000341 ± 0.0000003 | 0.0000143 ± 0.0000017 | 37.67 s | 9203 | 0 |

Full cross-section/weight detail: `metadata/cross_sections_and_weights.csv`
(derived directly from each point's `metadata/lhe_init.json`, which was parsed
from the raw LHE `<init>` block — not hand-transcribed).

All three generations completed with exit code 0, no crash/timeout, no disk or
RAM safety-gate violations recorded.

## 3. Charge filtering (colored only)

| Point | Matched | Charge-filtered | Fraction | Same-sign anomalies |
|---|---|---|---|---|
| colored_1500GeV | 43 | 16 | 37.2% | 0 |
| colored_2400GeV | 42 | 14 | 33.3% | 0 |

Computed with `_make_rhadron_charge_lookup()` (reused unmodified from
`01_signal_generation/extract_quirk_momenta.py`), which queries Pythia8's own
R-hadron charge table via its read-only Python bindings. EW events carry
charge directly from the fixed PDG-code-to-charge map (no separate filter
step needed — stau-like EW quirks have a fixed, unambiguous charge).

## 4. Trigger

| Point | Charge-filtered (or matched, EW) | Trigger-passing | ε_trig |
|---|---|---|---|
| EW_200GeV | 60 | 3 | 5.0% |
| colored_1500GeV | 16 | 4 | 25.0% |
| colored_2400GeV | 14 | 3 | 21.4% |

Ten trigger-passing events total went into the downstream (trajectory →
detector → reconstruction) stage.

## 5. Downstream physics results (10 trigger-passing events)

Produced by `run_downstream_pipeline.py`, using the validated optimized-v2
integrator (`quirk_trajectory_optimized_v2.integrate_trajectory_fast_v2`,
commit `3c33601`) via monkey-patching `trajectory_to_hits.integrate_trajectory`
— the unmodified `simulate_quirk_hits()` / `coplanarity_fit` reconstruction
code runs identically regardless of which integrator is active, exactly as
validated in the prior `perf_profile_v1` task.

| point | row | truth_fiducial | sec3c_plane_found | sec3c_Δs (cm) | final_sec_iv_pass | wall (s) |
|---|---|---|---|---|---|---|
| EW_200GeV | 0 | False | False | — | False | 12.59 |
| EW_200GeV | 1 | True | True | 0.017899 | False | 10.22 |
| EW_200GeV | 2 | False | True | 0.016575 | False | 26.68 |
| colored_1500GeV | 0 | True | True | 0.012661 | False | 4.13 |
| colored_1500GeV | 1 | False | False | — | False | 4.79 |
| colored_1500GeV | 2 | False | False | — | False | 22.34 |
| colored_1500GeV | 3 | True | True | 0.017245 | False | 7.58 |
| colored_2400GeV | 0 | False | True | 0.001374 | False | 86.92 |
| colored_2400GeV | 1 | False | True | 0.009144 | False | 15.53 |
| colored_2400GeV | 2 | False | False | False | 12.07 |

Full table with hit multiplicity, Δw, per-event RSS, and NaN/Inf flags:
`metadata/downstream_results_all_points.csv`. Per-event hit-level and
plane-level detail: `<point>/hits/row{i}_hits.csv`,
`<point>/planes/row{i}_plane.csv`.

**No event passed the final Sec. IV signal-region cuts.** This is expected —
this pilot ran O(10²) generated events per point, whereas the full production
pipeline's own measured survival rates are of order 1-in-hundreds after all
cuts; a 3-point, 100-event/point pilot has essentially no statistical power to
observe a passing event and was never intended to.

**Validation gates (all events):**
- NaN in Δs: **False**
- Inf in Δs: **False**
- Duplicate `(point, row_index)`: **False**
- Wall time and peak RSS recorded per event (`metadata/downstream_results_all_points.csv`); no event exceeded the disk/RAM/CPU safety thresholds used elsewhere in this project.

## 6. Baseline-vs-optimized integrator comparison (1 real event per point)

For one real trigger-passing event per point
(`EW_200GeV` row 1, `colored_1500GeV` row 0, `colored_2400GeV` row 1), the
**unmodified** `quirk_trajectory.integrate_trajectory` (baseline) and the
**validated optimized-v2** integrator were each run through the identical,
unmodified downstream code, each seeded with the same
`np.random.default_rng(4242)`:

| point | row | discrete_match | Δs diff | baseline (s) | optimized (s) | speedup | verdict unchanged |
|---|---|---|---|---|---|---|---|
| EW_200GeV | 1 | True | 0.0 | — | — | 10.10x | True |
| colored_1500GeV | 0 | True | 0.0 | — | — | 14.08x | True |
| colored_2400GeV | 1 | True | 0.0 | — | — | 9.84x | True |

Full timing detail: `metadata/baseline_vs_optimized_comparison.csv`.

**ALL DISCRETE OUTPUTS MATCH: True**
**ALL PHYSICS VERDICTS (`final_sec_iv_pass`) UNCHANGED: True**

The optimized-v2 integrator reproduces the baseline bit-for-bit on real pilot
events (Δs difference exactly 0.0 in all three cases), consistent with the
prior isolated validation of commit `3c33601`.

## 7. Reusability / checkpointing

- **Per-event checkpointing:** `run_downstream_pipeline.py` writes an atomic
  JSON progress record (`checkpoints/downstream_progress.json`) after each
  event and skips any event already recorded on rerun. This was verified
  directly in this pilot: rerunning the script after full completion produced
  `SKIP (already checkpointed)` for all 10 events and reproduced the same
  validation-gate results with no new work performed — confirming the
  checkpointing is both correct and idempotent.
- **Generation-phase DONE markers:** each point directory has a
  `checkpoints_DONE_generation.txt` marker, written only after that point's
  generation completed with exit code 0.
- **Honest note on the lower-level trajectory cache:** the standalone
  `perf_profile_v1/trajectory_cache_v1.py` disk-cache module (previously
  built and validated with a 47x cache-hit speedup and bit-identical results
  in a separate self-test) was **not** wired into
  `run_downstream_pipeline.py`. The pipeline instead relies on its own
  event-level JSON checkpoint plus saved per-event hit/plane CSVs, which
  gives the required reusability (a rerun does no redundant physics work) but
  is a coarser granularity than the trajectory_cache_v1 module's per-trajectory
  keying. Since all 10 pilot events have distinct physics inputs, no
  trajectory-level cache hits would have occurred in this run regardless —
  this is noted as a known gap for any future run with repeated or shared
  inputs, not a defect discovered in this pilot's own results.

## 8. Provenance

- Seeds: 9201 (EW_200GeV), 9202 (colored_1500GeV), 9203 (colored_2400GeV) — distinct per point, recorded in each point's `run_card.dat` (preserved in `<point>/cards/`).
- Downstream RNG: `np.random.default_rng(4242)`, reused per point (governs detector smearing / hit response, not the underlying LHE physics, which is fixed by the MadGraph/Pythia seed above).
- Full SHA-256 manifest of all 68 pilot output files: `SHA256_MANIFEST.txt`.
- Original (never-modified) MadGraph process-directory banners verified byte-identical via SHA-256 against `madgraph_pilot_v1/SHA256_MANIFEST.txt` before this pilot's directories were created from them.
- No process left running; disk usage of pilot directory: 1.3M; host free disk: 945G/1007G (2% used) after completion.

## 9. Scope and limits

This pilot ran 100 generated events at 3 mass points (1 EW, 2 colored),
producing 10 trigger-passing events total, 0 of which pass the full Sec. IV
signal-region cuts — a sample far too small to estimate Figure 6's efficiency
curves, let alone reproduce them. It exercised every pipeline stage
(generation → matching → charge filter → trigger → trajectory integration →
detector hits → Sec. IIIC seeding/plane reconstruction → Sec. IV cuts) end to
end at each of the 3 points, confirmed the optimized-v2 integrator is
bit-identical to baseline on real events with an ~10–14x speedup, and
confirmed checkpointing is correct and idempotent. Per-point wall time
(generation + downstream) was well under the 8-hour autonomous-execution
threshold set before this pilot began.

**THE THREE-POINT PILOT VALIDATES THE PIPELINE AND RUNTIME; IT DOES NOT CONSTITUTE A FIGURE 6 REPRODUCTION.**
