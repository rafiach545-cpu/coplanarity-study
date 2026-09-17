# Autonomous multi-stage run log (append-only)

Started: 2026-09-15, following user's overnight autonomous-work instruction.
Baseline preserved: commit af0fca7 (validated EW v3 vertex-corrected result).
Rule: one CPU-intensive simulation at a time; versioned outputs only; no report generation.

## [2026-09-15 17:58] STAGE 1 start
Re-read Sec II/IIIA/IIIC/IV, Eqs 3-12, Table I (already extensively quoted
earlier this session; re-verified proc_card_mg5.dat + param_card.dat for
colored quirk production mode and charge directly, not from memory).
Verification table: 21/21 items MATCH. No analyze_colored_quirk.py script
existed previously -- building it now, reusing already-validated global
fixes in trajectory_to_hits.py / coplanarity_fit.py unchanged.

## [2026-09-15 18:05] STAGE 1 validation
- All existing suites re-run and PASS: validate_against_eq4.py (9.3e-13),
  validate_dt_convergence.py (D2, 16x/halving confirmed), validate_corrections_suite.py
  (D3-D10, all PASS).
- Built 05_coplanarity_analysis/analyze_colored_quirk.py (first working driver
  for this benchmark; none existed before). Mirrors analyze_ew_quirk.py's fully
  corrected structure: per-event charge from CSV (Pythia8-verified), vertex-
  relative coplanarity fit, 25ns timing from pre-merge truth, transverse-beta
  timing sizing, 300-steps/period floor -- all reused unchanged from the
  already-validated global fixes.
- 3-event end-to-end validation (events 6, 10, 34): no errors, on-shell energy
  warnings fire as expected (same ~1e-4 level as EW sample), R-hadron charges
  load correctly per-event (+-1, +-2 magnitudes seen, matching physical
  expectation), timing computed from pre-merge truth crossings, vertex
  subtraction active (default). None of these 3 reached 16/16 fiducial
  coverage -- expected statistically, not an error (same downstream fit code
  already validated exhaustively via the EW run).
- Proceeding to launch full 27-event trigger-passing colored-quirk run.

## [2026-09-15 18:15] STAGE 2 audit (lightweight, ran concurrently with Stage 1's
heavy simulation still in progress -- no violation of the one-simulation-at-a-time
rule since this involved no RK4-heavy quirk integration).
Re-read Sec III D. Verified directly from run_card.dat/proc_card_mg5.dat:
- collision energy: ebeam1=ebeam2=6500 GeV -> sqrt(s)=13 TeV. MATCH.
- All 3 neutrino flavors: `vl=ve vm vt` in `z > vl vl~`. MATCH.
Found 1 real MISMATCH: convert_and_analyze.py's background reconstruction did
NOT apply the vertex-relative coplanarity correction already applied to the
signal pipeline (commit af0fca7) -- inconsistent treatment of signal vs
background. FIXED (now uses vertex_relative_hits with traj["vertex_cm"] ==
the conversion point).
Found 2 misleading comments (both explicitly named in the task): "misset cut
is EXACT" and "post-shower MET failures should be ~0" -- both corrected to
state the measured reality (861/10000, 8.6%, a real non-negligible effect).
Added explicit "hardest photon = unverified ancestry proxy" labeling.
Validated: compile check, parser test (2000-event subset, 193/2000=9.65%,
consistent scale with historical 8.6%), small detector test (5 events, no
errors, new file conversion_scan_results_v2_VERTEX_FIXED.csv).
Committed: 04d587d.
NOT YET DONE: the larger converted-photon sample run -- BLOCKED until Stage 1's
heavy colored-quirk simulation finishes (one-CPU-intensive-job-at-a-time rule).

## [2026-09-15 ~18:30] STAGE 1 COMPLETE
Full 27-event trigger-passing colored-quirk run finished (818s wall time,
no errors, on-shell-energy warnings fired as expected same as EW ~1e-4 level).
Cutflow: N_matched=125, N_trigger=27, N_geometric_fiducial=11, N_truth_fiducial=7,
N_seed_found=5, N_signal_region=1.
eps_trig=0.2160 (paper Table I: 0.24) -- close.
eps_fid=0.2593 (paper: 0.28) -- close.
eps_reco=0.1429 (paper: 0.35) -- gap, same DIRECTION and qualitative pattern
as the EW benchmark's 0.15 vs 0.72 gap (trig/fid roughly match, reco is
systematically low). This is a NEW, independent confirmation that whatever
suppresses eps_reco is a generic effect across both benchmarks, not EW-
specific -- noted for the record only, NOT investigated further tonight per
explicit instruction to not work on the EW discrepancy further.
No cuts loosened, no parameters tuned to approach the paper's numbers.
Validated: 27/27 rows, unique event IDs, no duplicates, all required columns
present, zero NaN in diagnostic columns for fiducial rows.
Committed: 8f14ab2.
Output: colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv (NEW,
versioned; old colored_quirk_1800gev_2kev_cutflow_v2_FIXED.csv is untouched
and remains OBSOLETE -- pre-dates every fix this session).
Proceeding to Stage 2's larger converted-photon sample now that Stage 1's
heavy job has fully released the CPU.

## [2026-09-15 18:40] STAGE 3 pre-check (lightweight, runs concurrently with
Stage 2's heavy conversion job -- no RK4/simulation work here, so no rule
violation).
Confirmed by direct filesystem search: NO minimum-bias sample, NO pileup
data, NO prior pileup code exists anywhere in /home/rafia/coplanarity_study
or /home/rafia/hep_tools. The paper's own pileup model (Sec III D) requires
a 125,000-event ATLAS Pythia8 minimum-bias sample processed through the
detector model of ref [34] -- this project has 0 of those events.
Per explicit instruction: will NOT invent or approximate this input as if
it were real. Will build+validate the OVERLAY FRAMEWORK ONLY using clearly-
labeled SYNTHETIC placeholder pileup hits (random, uncorrelated per-layer
hits, scaled toward the paper's stated "O(1000) hits/layer at mu=50"), to
verify the mechanics (no double counting, deterministic seeding, hit/layer
distributions, NaN/duplicate checks, mu=0 consistency) -- NOT to produce any
claimed pileup background rate. Will stop after framework validation once
Stage 2 releases the CPU.

## [2026-09-15 18:50] STAGE 3 framework validation COMPLETE (synthetic only)
Built 02_backgrounds/pileup/synthetic_pileup_framework.py. Explicitly and
repeatedly labeled as SYNTHETIC/placeholder, not real physics, throughout
(module docstring, inline comments, and printed "SCOPE STATEMENT").
Validated:
- mu=0 exactly reproduces the pure-signal baseline (0 pileup hits added,
  identical candidate/pass result) -- confirms no accidental hit injection
  at mu=0.
- Hit-count scaling exactly linear and correct: mu=5/10/20/50 ->
  800/1600/3200/8000 total synthetic hits (== 1000*mu/50 per layer x 8
  layers), matching the paper's own O(1000)/layer-at-mu~50 anchor (Sec IV).
- Zero NaN/inf hit coordinates at any mu.
- Zero exact-duplicate hit coordinates at any mu (no double-counting of the
  hard-event hits when overlaid with pileup).
- Reproducibility: identical synthetic pile-up hit sets across two
  independent calls with the same seed.
- n_candidates stayed at 1 (== baseline) even at mu=50/8000 synthetic hits --
  qualitatively consistent with the paper's own claim (Sec IV) that only
  ~1e-3 of background events form even a partial plane candidate, though
  this is NOT claimed as a measurement (synthetic data only).
STOPPED HERE as instructed: no real minimum-bias sample exists (0 vs
paper's 125,000-event pool) -- documented honestly, no expensive/real
pile-up run launched, no result fabricated.
Committed: 65336a0.
STAGE 3 STATUS: framework built and validated; physics result BLOCKED on
missing input (not a bug, not fixable from within this repository).

## [2026-09-15 18:52] STAGE 2 progress note
Full 9139-event converted-photon run (PID 70556) in progress. Observed rate
~2.0s/event (slower than the initial 5-event spot-check's 0.6s/event -- real
sample has more energy/momentum spread). Projected total runtime ~5 hours.
Continuing to let this run as the single active CPU-intensive job; no other
heavy work will be launched until it completes, per the one-job-at-a-time
rule. Stages 1 and 3 are both already complete for tonight's scope.

## [2026-09-16 ~06:59] STAGE 2 COMPLETE
Full 9139-event converted-photon run finished (PID 70556, ~54228s real
per-process elapsed across the session, no errors, all 9139 events status=ok).
Result: 0/9139 pass signal region. 95% CL upper limit on efficiency: 0.0003.
95% CL upper limit on passing cross-section: 0.000693 fb.
n_hits distribution: mean 11.26, max 16 -- consistent with the vertex-relative
fit being applied (no anomalies).
Validated: 9139/9139 rows, unique event IDs, no duplicates, zero NaN, all
status=ok. Committed.
Output: conversion_scan_results_v2_VERTEX_FIXED.csv (NEW; old
conversion_scan_results.csv, 1500-event pre-vertex-fix test, is OBSOLETE).
ALL THREE STAGES NOW COMPLETE. Proceeding to Stage 4 final status summary.

## [2026-09-16 07:05] HOUSEKEEPING
Verified RUN_LOG.md content against actual git log and output files:
- Stage 1 commit 8f14ab2: confirmed present in git log, matches described content.
- Stage 2 audit commit 04d587d: confirmed present, matches.
- Stage 3 commit 65336a0: confirmed present; fixed a vague "(see next commit
  hash in git log)" placeholder left in this file to the actual hash.
- Stage 2 completion commit 0382101: confirmed present (added after the
  0382101 commit was made, cross-checked against docs/conversion_v2_run.log's
  final lines -- counts match exactly: 9139/9139, 0 pass, upper limit 0.0003).
This file is being committed now as an accurate, append-only record.

## [2026-09-16 ~07:15] STAGE 3 REAL — PART B (paper audit) complete
Full 31-item audit performed, re-quoting Sec III D/IV directly (not from
memory/paraphrase). Evidence table: 20 MATCH, 6 AMBIGUOUS (documented
assumptions: Poisson mu, sampling with replacement, collision energy,
minbias definition, stable-particle def, vertex lifetimes), 2 genuine
MISMATCH/gaps flagged:
  (16) paper's pileup detector model (ref 34) includes endcaps+service
       material; our barrel-only 8-layer model is necessarily simpler --
       documented limitation, not silently ignored.
  (31) paper's own background-rate normalization uses an explicit
       reweighting procedure (Sec IV: derive rate from 1-hit-per-layer
       events, weighted by the efficiency of the stricter cut) because raw
       full-multiplicity pileup events are extremely rare (paper's own
       quoted 6e-5). Our existing Stage-3 synthetic framework does NOT
       implement this -- flagged as required before any real rate can be
       trusted, will implement in Part D.
Pythia8 confirmed available: version 8.312 (paper cites the "8.2" series,
ref [21] = arXiv:1410.3012 -- version mismatch documented, best available used).
Proceeding to Part C (real minimum-bias generation) with all above
assumptions explicitly recorded, none presented as paper-mandated.

## [2026-09-16 ~14:20] STAGE 3 REAL — Part B addendum: read the actual paper
and ref [34] PDFs directly (arXiv:1708.02243v2 full text + arXiv:1612.00850
Appendix A, both via pypdf text extraction, not from memory/prior summary).
Confirmed as genuine MATCH (not just AMBIGUOUS-with-assumption) via ref [34]
p.14: "we assume the number of pile-up vertices follows a Poisson
distribution with an average of 50 interactions per bunch crossing... the
longitudinal z-coordinate of the primary vertex follows a Gaussian
distribution... width of 45mm... We neglect the width of the beamspot in
the transverse direction." Ref [34] Appendix A also confirms its pile-up
detector model is materially richer than the main paper's own Sec III A
barrel-8-layer model used here (adds endcap SCT discs, service layer, TRT
barrel+endcap, ECAL, Bethe-Bloch energy loss, single-photon bremsstrahlung).
DECISION (user-directed): reuse the existing validated Sec III A barrel-8-
layer model for pile-up too, rather than implement ref [34]'s fuller
detector -- documented simplification, not a paper requirement, expected to
UNDER-count pile-up hits somewhat (partially offset by the paper's own
factor-of-2-conservative <mu>=50 choice, per ref [34]'s own discussion of
its ~30% Pythia8 soft-track undercount).

## [2026-09-16 ~14:35] Part D prerequisite: helix_propagation.py (exact
analytic solution for ordinary, non-string-bound charged particles at
Lambda=0) validated against the existing RK4 quirk integrator across 4
cases (charge sign, z-shifted vertex, off-axis vertex, electron mass) --
all PASS, max position diff 1.2e-7 cm, max time diff 5.8e-10 ns across all
8 layers. Committed (e589eff). pileup_hits.py (pile-up hit generation +
hard/pile-up overlay + combined pixel merging) built on top of it.

## [2026-09-16 ~13:15-14:09] REAL 125,000-event minimum-bias pool: FIRST
ATTEMPT OOM-KILLED. The original generate_events() buffered all rows in
memory before writing; confirmed via dmesg the process reached 7.4GB RSS on
this 7.6GB-RAM machine before SIGKILL (exit 137) -- the 1000-event
benchmark's linear ~1.4GB projection undercounted per-Python-object
overhead at ~14M particle rows. FIXED: generate_events_streaming() flushes
to CSV in ~2000-event chunks, holding only lightweight summary stats for
the full run. Verified at 20,000 events: peak RSS 232MB. Committed (93db9da).
A second 125,000-event attempt was subsequently launched and was still
running when the USER DECIDED a 20,000-event pool is sufficient for this
study; that run was stopped cleanly (SIGTERM to the exact PID, confirmed
exited, no other process touched) at ~118,156/125,000 events. Its partial
output was preserved (not deleted) as
minbias_pool_125000_PARTIAL_NOT_FOR_ANALYSIS.csv pending any future
decision to resume/redo a full-size pool -- NOT used for any physics result
below.

## [2026-09-16 ~14:40] REAL 20,000-event minimum-bias pool: FINAL, validated.
minbias_pool_20000_FINAL.csv -- Pythia8 8.312, SoftQCD:nonDiffractive=on,
13 TeV, Beams:allowVertexSpread=off (beamspot applied at overlay time per
module docstring), seed=20260916 (same audited seed as the original attempt).
Validated: 20000/20000 unique event IDs (0..19999, no gaps/dupes), 2,256,066
charged final-state particle rows, zero NaN/Inf, all charges in {-1,+1},
10 distinct PDG species, on-shell E^2-p^2-m^2 residual <= 1.1e-5 GeV^2
(Pythia8 rounding-level), charged multiplicity/event mean=112.80 (min 10,
max 490, matches the earlier 1000- and 20000-event benchmarks exactly).
Runtime: 105.4s (5.27 ms/event). File size: 233.5 MB. Reproducibility:
independent 200-event same-seed regeneration is byte-for-byte identical
(DataFrame.equals == True).

LIMITATION, explicitly recorded (not to be silently forgotten downstream):
the paper's own pile-up model uses a 125,000-event minimum-bias pool
(Sec III D). This implementation uses 20,000 events, a deliberate USER
DECISION (not a paper requirement, not a feasibility finding -- 125,000 was
independently confirmed feasible via the streaming-fixed generator, ~11 min
projected). A 20,000-event pool is smaller than the paper's by 6.25x.
Consequences documented, not ignored:
  - sampling WITH replacement (already the documented assumption -- see
    pileup_hits.py module docstring) becomes materially more consequential:
    at mu=50, an event draws 50 interactions from only 20,000 available,
    still low individual reuse probability per event, but AGGREGATE reuse
    across many hard events in a mu=50 run will be substantial.
  - repeated reuse of the same pool events across different pile-up draws
    reduces the STATISTICAL INDEPENDENCE of the pile-up background estimate
    relative to what a 125,000-event (or larger) pool would give -- results
    below should be read as a real-physics DEMONSTRATION of the overlay
    pipeline at reduced statistics, not as an exact reproduction of the
    paper's own pile-up background rate at its native pool size.
  - pileup_hits.py's sample_pileup_hits()/build_pool_index() were refactored
    (pre-group the pool ONCE into numpy arrays per event, reused across all
    overlay calls) specifically so repeated high-multiplicity draws from
    this smaller, more-reused pool stay memory-safe and don't re-pay a full
    pandas groupby() per hard event.

## [2026-09-16 ~15:00-15:20] Part D: mu=0 exact-match validation + mu=5
smoke test (5 events), both REAL (Pythia8 minbias pool + real EW-quirk
truth momenta), no synthetic data.

mu=0 exact match (run_pileup_overlay.py, event=3, rng seed=4242 matching
analyze_ew_quirk.py's own original seed exactly): reproduces the already-
committed v3 result BIT-FOR-BIT -- ds=0.013232430572373607 (v3: 0.013232),
dw=0.043214639013254806 (v3: 0.043215), passes_signal_region=False in both.
Confirms the overlay/merge code path adds zero artifacts at mu=0. A first
attempt at this check used a different (non-matching) RNG seed and gave a
DIFFERENT ds/dw (0.017560 vs 0.013232) -- investigated and confirmed as
expected stochastic RNG-stream difference (SCT Gaussian smearing depends on
the RNG draws), NOT a bug; re-run with the matching seed to get the true
bit-for-bit check above.

Also caught and fixed a real bug during this validation: the first version
of run_pileup_overlay.py did not apply Sec IV's pT_pair>200 GeV trigger cut
before running the expensive RK4 simulation, so it processed the raw
511-event untriggered sample's first N rows instead of the validated
89-event trigger-passing sample -- fixed to match analyze_ew_quirk.py's own
cutflow order exactly (trigger cut BEFORE simulate_quirk_hits).

mu=5 smoke test (5 events: 3,8,11,13,15 -- the trigger-passing sample's
first 5 by event id): ALL PASS mechanically -- 5/5 unique event IDs, zero
NaN/Inf, Poisson(5) draws (n_pu=7,2,7,5,6, sample mean 5.4) qualitatively
consistent, per-layer hit counts (~100-190/layer) scale sensibly relative
to the paper's own O(1000)/layer-at-mu=50 anchor, event 3's Delta_s/Delta_w
UNCHANGED from its mu=0 value even with 919 pile-up hits overlaid (the
tight growth-factor-3 iterative-fit cut correctly rejects pile-up hits from
joining the real signal candidate -- a real, physically meaningful check,
not assumed). Reproducibility: independent re-run of event 3 at mu=5 with
the same per-event seed formula (seed=20260916+event) is byte-identical.
Transition table vs mu=0: all 5/5 are 0->0 (none of these 5 specific events
happen to be among the 6/89 events that pass at mu=0 -- expected for a
5-event random subsample when only ~6.7% pass overall; no 1->0/0->1/1->1
example was observed in this smoke sample, honestly noted as a sampling
gap, not claimed as "no transitions exist"). Committed.

FEASIBILITY FINDING (real, measured, not estimated from a benchmark
projection): per-event wall time for the real EW-quirk RK4 trajectory
integration is ~130-170s in this pure-Python pipeline (measured directly:
171.6s for the mu=0 single-event check, 127.95s/event average for the
5-event mu=5 smoke test). Extrapolating to the full 89-event trigger-
passing sample: ~4.2 hours for mu=0, ~3.2 hours for mu=5, and mu=10/20/50
are expected to take AT LEAST as long (likely longer, since the naive O(N^2)
seeding pair-combinatorics in coplanarity_fit.py grows with pile-up hit
density -- the paper's own Sec III C notes an amortized O(N) implementation
is possible with spatial binning, which this repo's seeding_and_iterative_fit
does NOT implement). Full 89-event sweeps at mu=5/10/20/50 are NOT complete
in this session -- reported honestly as pending, not attempted-and-hidden,
per the explicit instruction to never report an incomplete run as complete.

## [2026-09-16 ~15:30-16:15] Part D re-audit (user-directed): re-read the
paper + ref [34] directly a second time for 12 specific doubtful points in
pileup_hits.py. Found and fixed a REAL crash bug (merge_neighboring_pixel_
hits raised TypeError on any merged cluster mixing a hard-event hit
[integer quirk_index] with a pile-up hit [string particle_tag] -- caught by
a new 6-case pixel-merging unit-test suite, all 6 now pass, see
04_detector_sim/trajectory_to_hits.py). Added the previously-missing
per-hit 25ns timing cutoff (ref [34] Appendix A stopping condition iii,
verbatim). Corrected an unsubstantiated "roughly offset" claim about the
missing ref[34] detector components to state the direction/size of that
simplification's effect is unquantified. Fixed a typo
(n_hits_prehmerge_combined -> n_hits_premerge_combined), numpy.int64
serialization, and a needless ~230MB memory duplication (pool DataFrame
kept alive alongside pool_index). Committed (358d74f).

CONCEPTUAL CORRECTION: implemented run_pileup_only_background.py, the
paper's ACTUAL pile-up background-rate metric (Sec IV: rate of "background
events" -- pile-up ONLY, no hard-scatter object -- that accidentally form a
>=4/8-layer or 8/8-layer candidate plane). The existing run_pileup_
overlay.py (signal+pileup) answers a different, still-useful question
(does a real EW-quirk event's reconstruction survive pile-up contamination)
but must never be reported as the paper's own background rate -- this was
a real gap in the previous session's framing, now fixed. Primary vertex for
a pile-up-only event (no real hard vertex to identify): NOT SPECIFIED by
the paper; used the global origin (0,0,0), the literal degenerate reading
of Sec III C's own vertex-assumption sentence -- documented, not asserted
as a paper requirement.

REAL RESULTS (small-N, explicitly caveated):
  - mu=5, n=500 background-only events: rate(>=4/8 layers)=0.004 (3/500),
    rate(8/8 layers)=0/500. Paper quotes ~1e-3 and ~6e-5 respectively --
    the 4/8 rate is the same order of magnitude (within ~4x, and 3/500 has
    a ~sqrt(3)/500~=0.7e-2 Poisson uncertainty, i.e. statistically
    consistent with the paper's value at ~1-2 sigma); 0/500 at 8/8 is
    consistent with needing >>500 events to see the paper's own much rarer
    6e-5 rate at all.
  - mu=50, n=3 background-only events (too few to trust as a rate
    measurement): 1/3 formed a >=4/8-layer plane. Measured hit density at
    mu=50 (~1500-2000/layer) is somewhat higher than the paper's own
    quoted "O(1000)/layer" anchor. A back-of-envelope check: since the
    seed-pairing combinatorics scale roughly quadratically with hit
    density, (hit_density_mu50/hit_density_mu5)^2 ~ (1750/151)^2 ~ 134
    predicts a ~134x higher rate than mu=5's measured 0.004, i.e. ~0.5 --
    QUALITATIVELY CONSISTENT with observing 1/3 at mu=50, not an
    unexplained anomaly. NOT presented as a validated rate (n=3 is far too
    small); flagged as needing a much larger mu=50 sample (thousands of
    events, ~22s/event measured -> hours) to actually resolve, not run in
    this session.
  - Pool reuse (pure sampling, no physics, exact): for the real 89-event
    EW hard sample, mu=50 touches only ~20% of the 20,000-event pool (max
    single-event reuse: 4). For a background-only study large enough to
    resolve the paper's 6e-5 rate (~10,000+ events needed), reuse is much
    heavier: 100% pool coverage, mean reuse ~25x per pool event at mu=50 --
    now quantified, not just asserted as a concern.

READINESS FOR FULL mu=0,5,10,20,50 SWEEPS: NOT YET. Two independent,
measured (not assumed) blockers: (1) the real EW-quirk RK4 cost (~130-170s/
event, ~3-4+ hours for the full 89-event trigger-passing sample per mu,
unchanged from the earlier finding) for the signal+pileup robustness study,
and (2) the pile-up-only background-rate study needs thousands of events
per mu to resolve the paper's own quoted rates with any statistical
confidence, which at mu=50's measured ~22s/event is itself several hours.
Neither is a code-correctness blocker (both pipelines are now validated:
mu=0 bit-for-bit, mu=5 mechanically clean, pixel-merging bug fixed, real
background metric implemented) -- both are pure wall-clock-time blockers,
honestly reported rather than run partially and presented as complete.

## [2026-09-16 ~18:00] Incomplete 125,000-event pool DELETED by explicit
user decision.

02_backgrounds/pileup/minbias_pool_125000_PARTIAL_NOT_FOR_ANALYSIS.csv
(1,387,722,114 bytes, 13,327,204 lines, stopped mid-generation at
~event 118,156/125,000 when the original generation task was terminated --
see the 2026-09-16 ~14:09 entry above) was deleted. Verified before
deletion: resolved absolute path; filename confirmed to contain
PARTIAL_NOT_FOR_ANALYSIS; confirmed distinct from minbias_pool_20000_
FINAL.csv; confirmed via lsof/fuser that no process had it open; confirmed
via `git ls-files` that it was never git-tracked (gitignored per
minbias_pool_*.csv). Deleted with an exact, non-wildcard path. Verified
after deletion: file no longer exists; minbias_pool_20000_FINAL.csv still
exists, unchanged (same size, same sha256
e03cf9a6c9b768c0695bf384b3cae6e16514055ff28c180b05feb3943000e2c9 as
recorded in this file's own provenance sidecars from its generation run).

This partial file was NEVER used for any analysis result in this
repository -- every committed pile-up output (validated 20,000-event pool
runs, SIGNAL_WITH_PILEUP driver, PILEUP_FAKE_BACKGROUND driver, all8layer
diagnostic) used minbias_pool_20000_FINAL.csv exclusively. Its deletion
removes an explicitly-rejected, unusable artifact; it does not retract or
invalidate any prior committed result.

## [2026-09-17 ~10:30] FINAL READ-ONLY AUDIT of the 5-configuration mu
sweep (mu=0,5,10,20,50, Loose, suppressed, n=5000 each, committed d35b562/
778df08). All values independently recomputed directly from the 5
authoritative CSVs, no summary code reused. Findings:

1. LABEL CORRECTION: "hits before/after suppression" values reported in
   the plots/table are MEANS PER BUNCH CROSSING (verified against medians
   and totals, computed directly: e.g. mu=50 mean_before=11842.97,
   median_before=11713.0, total_before=59,214,840 across 5000 events --
   all three now distinguished in COMPARISON_TABLE_CORRECTED.csv's
   explicit hits_before_mean/hits_before_median columns).

2. MAJOR CORRECTION -- what "4/8" and "8/8" actually mean: the sweep's
   driver (run_one_background_event_suppressed) only ever computed
   COVERAGE (best_candidate_n_layers_with_hit, i.e. has_4_of_8_plane /
   has_8_of_8_plane) -- it never called select_reconstructed_plane,
   check_hit_multiplicity, or apply_signal_region_cuts. These "4/8"/"8/8"
   counts previously reported (59/5000 at mu=50, etc.) are coverage-only
   diagnostics, matching the paper's own Sec IV phrasing ("a plane with at
   least one hit in 4 out of 8 layers" / "in each layer") -- but they are
   NOT the final Sec IV signal-region pass count, and must never be
   presented as such.

   To get the true final Sec IV rate WITHOUT launching a new simulation,
   the 59 mu=50 events with has_4_of_8_plane=True and the 1 mu=5 event
   (event_i=2006) with has_8_of_8_plane=True were individually REPRODUCED
   (bounded, deterministic replay of their exact recorded seeds --
   SeedSequence([90210777, mu, event_i]) -- not a new simulation; results
   saved as audit_mu50_4of8_events_reproduced.csv and audit_mu5_event2006_
   reproduced.csv). Reproduction verified bit-consistent with the original
   sweep CSVs (n_candidates and best_candidate_n_layers_with_hit match
   exactly for all 60 events). Result: ALL 60 reproduced events FAIL
   check_hit_multiplicity, and therefore ALL FAIL apply_signal_region_cuts
   (final_sec_iv_pass = False for all 60, with zero exceptions).

   A structural/logical check (check_hit_multiplicity requires n_with_1plus
   ==8, i.e. full 8-layer coverage, as a NECESSARY condition -- directly
   verified: a synthetic 7-layers-represented candidate always fails)
   combined with the fact that has_8_of_8_plane=True occurred EXACTLY ONCE
   across the entire 25,000-event sweep (the one mu=5 event, directly
   verified to fail) PROVES, not merely observes, that the final Sec IV
   signal-region fake rate is EXACTLY 0/5000 at every mu (0/25,000 total)
   -- a complete census of the only event that could possibly have passed,
   not a "zero observed in a finite sample" statement.

3. Re-read Sec III D's exact text again: "The biggest background for our
   search are unassociated hits, which predominantly come from pile-up
   tracks for which the track reconstruction failed. For this purpose we
   use the public available tracking efficiency plots [33]..." -- this
   means the paper's OWN "~1e-3"/"~6e-5" Sec IV numbers are computed on
   tracking-efficiency-SUPPRESSED hits already, not raw pile-up hits.
   CORRECTION to earlier wording: the mismatch between this sweep's rates
   and the paper's quoted values is NOT primarily a "different denominator"
   (no direct textual evidence supports that claim, and it is retracted) --
   it is uncertainty in the specific tracking-efficiency curve/selection/
   suppression-mechanism details (all documented assumptions here) plus
   detector-model fidelity and pool-size/statistics differences. Also: the
   EARLIER (unsuppressed) direct-count driver's comparison to these same
   paper numbers was even less apt than previously stated, since that
   driver applied no suppression at all while the paper's own numbers
   apparently already do.

4. REAL BUG FOUND AND FIXED (metadata only, not physics): every one of the
   5 committed provenance JSON sidecars incorrectly records pool_filename/
   pool_sha256 as minbias_pool_20000_FINAL.csv's identity
   (e03cf9a6c9b768c0695bf384b3cae6e16514055ff28c180b05feb3943000e2c9),
   because build_provenance()'s default pool_path was never overridden in
   run_sweep_resumable.py or run_pileup_fake_background_suppressed.py. The
   ACTUAL simulation correctly sampled from minbias_pool_20000_ANCESTRY_v1.csv
   (sha256 a8f9149c07b9967332cfd7eba49960dd137bbc927c4be7309b92df6979b172ad
   -- CORRECT value for the record) -- confirmed by direct inspection of
   the sampling code path and by the presence of ancestry-dependent
   behavior (secondary/ambiguous track counts) in every result row. This is
   a provenance-METADATA bug only; the physics results are unaffected and
   unchanged. Fixed in both driver files (pool_path=ANCESTRY_POOL_PATH now
   passed explicitly), verified with a 3-event test showing the corrected
   field. The 5 already-committed provenance JSONs are NOT retroactively
   edited (preserving the historical record); this entry is the
   authoritative correction for anyone reading them.

5. Independently re-verified: all Wilson 68%/95% intervals recomputed from
   scratch match the originally-reported values exactly. Clopper-Pearson
   95% intervals additionally computed for comparison (e.g. mu=50 A: Wilson
   95%=[0.00916,0.01519] vs Clopper-Pearson 95%=[0.00899,0.01520] -- close,
   Clopper-Pearson slightly wider/more conservative as expected). For
   zero-observation cases, the naive "3/N" Poisson-upper-limit rule of
   thumb gives 3/5000=6.0e-4, somewhat tighter than the Wilson/Clopper-
   Pearson 95% upper bound of ~7.4-7.7e-4 -- both conventions are reported
   in COMPARISON_TABLE_CORRECTED.csv, Wilson used as the primary reported
   interval (consistent with all earlier reporting in this project).

6. Provenance/hash/DONE-marker check (all 5 files): seed=90210777 (all),
   mu correctly recorded per file, n_events_processed=5000 (all),
   tracking_efficiency_selection="Loose" (all), git_commit_hash=d861f2a76d
   (all -- consistent, since no commits were made between the sweep's
   start and its completion). CSV files confirmed unmodified since commit
   (git diff clean against d35b562/778df08). minbias_pool_20000_FINAL.csv
   confirmed unchanged throughout (same hash as originally recorded).

7. Item 12 disposition: this is a labels/summary/metadata correction, not
   a physics-code or results correction -- no simulation results are
   altered. Corrected outputs: COMPARISON_TABLE_CORRECTED.csv (explicit
   A/B/C split: partial-plane >=4/8 diagnostic, complete-plane 8/8
   diagnostic, final Sec IV rate proven zero), audit_mu50_4of8_events_
   reproduced.csv, audit_mu5_event2006_reproduced.csv, and the
   run_sweep_resumable.py / run_pileup_fake_background_suppressed.py
   pool_path fix, all committed separately from the original sweep commit.
