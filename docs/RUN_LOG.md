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

## [2026-09-17 ~11:15] User-suggested classifier gap independently
re-verified, confirmed genuine, patched, and PROVEN to change zero
classifications across the entire pool.

Independent verification performed BEFORE accepting the user's suggestion
(not inherited as a conclusion): (1) re-read ATL-PHYS-PUB-2015-051 p.5
directly again -- "Primary charged particles are defined as charged
particles with a mean lifetime tau>300ps, either directly produced...";
confirmed this is a COMPOUND condition (particle's own tau AND production
chain), not production-chain-only. (2) Re-read the complete current
ancestry_classifier.py fresh -- confirmed prt.tau0() (the tracked
particle's own lifetime) was never referenced anywhere in the function,
only ancestor lifetimes were checked -- genuine literal gap confirmed.
(3) Queried Pythia8's own particleData.tau0() directly for all 10 species
present in the pool (p,pbar,e+,e-,mu+,mu-,pi+,pi-,K+,K-): found a critical
subtlety -- Pythia8 encodes an ABSOLUTELY STABLE particle's tau0() as
EXACTLY 0.0 (meaning infinite lifetime), not a large finite value. A naive
`tau0() > 300ps-threshold` patch would have WRONGLY classified every
proton and electron as failing the lifetime requirement -- this would have
been a NEW, WORSE bug than the one being fixed. The correct patch
special-cases tau0()==0.0 as "stable, trivially satisfies tau>300ps".
(4) With the CORRECT special-casing, all 10 actual species pass trivially
(K+-/pi+-/mu+- have finite tau0 >>300ps threshold; p/pbar/e+/e- are
tau0()==0.0, i.e. stable).

Patch applied (ancestry_classifier.py): smallest possible change, checks
prt.tau0() once at function entry, correctly handles the tau0()==0.0
stable-particle sentinel, does not touch any other logic, cut, detector
assumption, sample, or parameter. Original preserved at
/tmp/ancestry_classifier_BEFORE_PATCH.py before editing.

Classifier-level validation, OLD vs PATCHED, row-by-row:
  - 200-event sample: 20,828 particles tested, 0 changed.
  - FULL POOL (all 20,000 events, EXHAUSTIVE, not a sample): 2,256,066
    particles tested, 0 changed. old_counts == new_counts exactly:
    primary=2,026,487, secondary=229,523, ambiguous=56 (identical to the
    unpatched classifier's counts in every category).

Dependency chain proof (no downstream rerun performed or required):
classify_particle() is called from exactly ONE place in the entire
codebase -- generate_ancestry_pool.py, which writes the ancestry_label
column into minbias_pool_20000_ANCESTRY_v1.csv. (pileup_hits_suppressed.py
imports classify_particle but never calls it -- it reads the pre-computed
ancestry_label column from the CSV instead.) Since the classifier's output
is proven byte-identical across the COMPLETE pool (not sampled), the
ancestry_label column would be unchanged if the pool were regenerated;
every downstream consumer (pileup_hits_suppressed.py, track_suppression.py,
run_pileup_fake_background_suppressed.py, run_sweep_resumable.py, and
therefore all 5 mu-sweep result CSVs and the post-sweep audit) reads that
column from the already-committed CSV, not by calling the classifier live
-- so all downstream results are mathematically identical given identical
inputs and identical RNG seeds. minbias_pool_20000_ANCESTRY_v1.csv was NOT
regenerated (proven unnecessary, not assumed).

VERDICT:
  Source requirement: ATL-PHYS-PUB-2015-051 p.5 -- primary charged particle
    requires tracked particle's OWN mean lifetime tau>300ps, compound with
    the production-chain condition.
  Current code behavior (before patch): checked only the production/
    ancestry chain, never the tracked particle's own tau0().
  Genuine bug/gap? YES.
  Patch applied? YES (smallest correct form, handling the tau0()==0.0
    stable-particle sentinel correctly -- a naive patch would have
    introduced a worse bug).
  Classification changes after patch: ZERO (exhaustively verified across
    the complete 2,256,066-particle pool, not sampled).
  Full downstream rerun required? NO.
  Exact reason: classify_particle() has exactly one call site
    (generate_ancestry_pool.py); its output is proven byte-identical for
    every particle in the pool; every downstream stage consumes the
    resulting CSV column, not a live function call; therefore every
    downstream result is a deterministic function of unchanged inputs and
    is provably unchanged without needing to be recomputed.

## [2026-09-17 ~12:00] Fig 1(b) systematic-uncertainty bands digitized and
audited (reference material -- NOT yet wired into any code, no rerun).

Re-verified from the source (ATL-PHYS-PUB-2015-051, p.5, Figure 1 caption,
re-read fresh, not from memory): "Figure 1: Track reconstruction
efficiency, evaluated by using minimum bias simulated events, as a function
of truth eta (a) and pT (b) for Loose and Tight Primary track selections.
THE BANDS INDICATE THE TOTAL SYSTEMATIC UNCERTAINTY." Cross-checked against
the earlier-extracted Eq. 3 description (p.6): the systematic uncertainty
is the quadrature sum of three MATERIAL-BUDGET-related components
(Sys+5%Extra, SysPixServExtra, Sys+30%IBLExtra) -- confirmed PURE
SYSTEMATIC (material-modeling driven), not statistical, not combined.
Both Loose and Tight Primary are explicitly, separately shown in the same
figure (not defined elsewhere).

Digitization method (band edges): initial naive column-wise min/max
approach was CONTAMINATED by stray same-colored anti-aliased pixels
elsewhere on the page (title text) -- caught via a sanity check
(central value must lie within [lower,upper]), which initially FAILED for
several points with clearly unphysical upper bounds (e.g. 1.08, 1.14).
Root cause diagnosed and fixed in two stages: (1) restrict to contiguous
pixel runs within a distance window of the marker's own y-position: still
failed for 4/17 Loose points because the marker's OWN opaque color occupies
the full column at its exact x-center, leaving no band pixels visible
there; (2) sample multiple OFFSET columns (+-4 to +-8px from the marker
center, skipping the marker's own occluded region) and combine all nearby
runs. Final result: ALL 34 points (17 Loose + 17 Tight Primary) pass the
central-in-[lower,upper] sanity check, robust to color-tolerance choice
(tested tol=20 and tol=35, identical pass result).

Cross-check: digitized band widths (~1.4-2.3% efficiency) are consistent
with Table 1's independently-known, EXACTLY PRINTED systematic uncertainty
range (0.4-2.6%, eta-binned) -- different binning (pT vs eta-integrated) so
not a literal match, but same order of magnitude, supporting the
digitization's validity.

Digitization precision: 1 pixel corresponds to ~0.0014 efficiency units
(from the same axis calibration as the central-value digitization); band
widths (14-23 pixels) are well above this pixel-noise floor.

Saved: fig1b_digitized_with_bands_v2.csv (selection, pT_GeV,
central_efficiency, lower_efficiency, upper_efficiency, band_width,
digitization_note columns) in docs/reference/atl_phys_pub_2015_051/.

Comparison against the current suppression implementation: tracking_
efficiency.py's track_efficiency() reads ONLY fig1b_digitized.csv (the
central curve) -- confirmed by direct code inspection, no band usage
anywhere. The completed 5-mu sweep therefore used ONLY the central curve;
by construction (central is always inside its own [lower,upper] band,
verified above), the sweep's suppression fraction trivially lies inside
the source-supported systematic range, but NO sensitivity to the +-
systematic variation has been tested yet.

Tight Primary: explicitly source-defined (same section, same figure,
already digitized in the same CSV files) -- the code (tracking_efficiency.
track_efficiency(selection="TightPrimary")) already supports it; the
5-mu sweep used only "Loose" by earlier explicit user decision, not because
Tight Primary is undefined or undigitized.

Minimal sensitivity sweep proposed (NOT launched): a small, bounded
comparison (e.g. n=50-100 background-only events at 1-2 representative mu
values, e.g. mu=10 and mu=50) run three times each -- once with the central
Loose curve (already effectively covered by the existing full sweep),
once with the lower-envelope curve, once with the upper-envelope curve --
to quantify how much the suppression fraction and downstream fake-plane
rate shift under the source's own quoted systematic range. This is
explicitly NOT the large-statistics run and has NOT been launched pending
user confirmation.

## [2026-09-17 ~12:30] Bounded Fig 1(b) suppression-systematics sensitivity
test RUN AND COMPLETE (NOT the large-statistics run; n=75/variant/mu,
mu=10 and mu=50, central/lower/upper, paired same-seed comparison).

Implementation: purely additive changes only. tracking_efficiency.py gained
a NEW track_efficiency_variant(pt, selection, variant) function (central/
lower/upper lookup from fig1b_digitized_with_bands_v2.csv); the existing
track_efficiency() is untouched (re-ran test_suppression_boundaries.py
after the change -- all 3 tests still pass, confirming no regression).
track_suppression.suppress_tracks() and pileup_hits_suppressed.
sample_pileup_hits_suppressed() each gained a new efficiency_variant="central"
default parameter (backward-compatible, unused by any existing caller,
including the completed 5-mu sweep). No cut, threshold, detector value,
ancestry classifier, or minbias pool was touched.

Paired design: SAME per-event SeedSequence([seed=90210777, mu, event_i])
used across all 3 variants -- rng_pileup/rng_suppression draws are
IDENTICAL; only the efficiency LOOKUP value differs. Runtime: mu=10,
21.3-21.6s/75 events per variant; mu=50, 260-271s/75 events per variant
(864s total for the whole 6-configuration test).

RESULTS:

mu=10 (all 3 variants): mean hits after suppression 1492.8-1509.2 (central
1500.2) -- a ~1.1% relative spread across the full systematic range. 0/75
events produced any candidate in ANY variant. 0/75 final Sec IV passes.

mu=50 (all 3 variants): mean hits after suppression 7331.0-7412.4 (central
7364.0) -- ~1.1% relative spread. 2/75 events produced a candidate/winner
IN EVERY VARIANT (same 2 events: event_i=43,58) -- for BOTH events, Delta_s
and Delta_w are BIT-IDENTICAL across central/lower/upper (e.g. event 43:
delta_s=0.042266, delta_w=0.846445, unchanged to the last printed digit in
all 3 variants), even though the event's total surviving hit count shifts
by a few percent -- the specific hits forming the winning candidate are
unaffected by the efficiency-curve variation for these two events. 0/75
final Sec IV passes in any variant (consistent with the full sweep's
proven 0/5000 result).

PAIRED per-event check (150 event-mu combinations total): zero events
where final_sec_iv_pass, has_winner, or n_candidates differs across
variants. Complete, verified null result -- not merely "small," genuinely
zero observed reconstruction-level sensitivity in this sample.

VERDICT:
  Sensitivity to Fig 1(b) systematic: NEGLIGIBLE (mean hit-count shift
    ~1.1%; zero change in candidates/planes/final-pass status across 150
    paired event-mu tests).
  Does the background conclusion change? NO (0/75 final Sec IV passes in
    every variant at every mu tested, consistent with the full sweep).
  Is Tight Primary testing still scientifically necessary? Assessed as
    LOWER PRIORITY given the demonstrated insensitivity to a comparably-
    sized curve shift (Tight Primary's own central-value difference from
    Loose, ~5-10% per ATL-PHYS-PUB-2015-051 p.5, is larger than this
    systematic band, so it is NOT automatically covered by this null
    result and remains a DISTINCT open question if pursued later) -- not
    run in this turn.
  Is suppression modeling now sufficiently validated to freeze (for the
    Loose baseline, central-vs-systematic-envelope axis)? YES.
  Is a larger-statistics run justified next? Not decided here -- reported,
    not launched, pending user direction.

## [2026-09-17 ~13:15] epsilon_reco LABELING FIX (labels/summary statistics
only -- no event-level result changed, no new simulation).

ROOT CAUSE (confirmed by direct source re-read, Sec IV p.7, exact quote):
"The reconstruction efficiency is defined as the efficiency of our
algorithm in finding quirks which satisfy both the trigger and fiducial
requirements." Combined with the paper's own explanation of what makes
epsilon_reco drop ("a stringent Delta_w requirement", "hits start
merging... a plane cannot be found") -- both describe Sec III C's own
Event Selection (>=1 candidate surviving Delta_w<1cm, smallest Delta_s
selected), NOT the stricter Sec IV final cuts (hit multiplicity + Delta_s
<0.01cm).

The PREVIOUS "epsilon_reco" label in analyze_ew_quirk.py and analyze_
colored_quirk.py incorrectly referred to N_signal_region/N_truth_fiducial,
i.e. the FULL Sec IV final-selection pass rate -- a real, well-defined,
correctly-computed quantity, but NOT what the paper's Table I calls
epsilon_reco. This was a DEFINITION/LABELING mismatch, not a bug in
seeding_and_iterative_fit, select_reconstructed_plane, check_hit_
multiplicity, or apply_signal_region_cuts, all of which remain independently
verified correct against Sec III C/IV.

CORRECTED VALUES (recomputed from the EXISTING, unmodified cutflow CSVs --
ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv sha256=b3251c3170faf52f...,
colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv sha256=a731d74e26a...
-- both confirmed BYTE-IDENTICAL to their previously-committed versions via
`git status --short` showing zero diff):

  EW quirk (800GeV, 4keV): epsilon_reco (paper definition) = 32/40 = 0.800
    (paper: 0.72) -- gap goes from 4.8x-too-low (old mislabeled 0.150) to
    ~11% high. The EW discrepancy is LARGELY RESOLVED by this correction.

  Colored quirk (1800GeV, 2keV): epsilon_reco (paper definition) = 5/7 =
    0.714 (paper: 0.35) -- gap flips from ~2.4x-too-low to ~2x-too-high.
    Binomial test: P(observing >=5/7 | true rate=0.35) = 0.056 -- borderline,
    NOT strongly inconsistent given N_fid=7. This is SMALL-N LIMITED and
    should NOT be treated as a confirmed independent algorithm discrepancy
    -- more fiducial colored-quirk events (a new simulation, not performed
    here) would be needed to resolve it further.

sec_iv_final_pass_rate (the OLD mislabeled quantity, now correctly named):
  EW: 6/40 = 0.150. Colored: 1/7 = 0.143. These remain valid, correctly-
  computed Sec IV final-selection pass rates -- just never equal to the
  paper's own epsilon_reco definition.

FILES CHANGED: analyze_ew_quirk.py, analyze_colored_quirk.py. Changes are
STRICTLY confined to (a) renaming/relabeling print statements inside each
file's `if __name__=="__main__":` block (affects only future re-runs, not
existing outputs) and (b) a NEW report_summary_from_csv() function in each
file that recomputes the corrected summary from an already-saved CSV
without any re-simulation, new random draw, or change to analyze_one()
(the per-event reconstruction function -- seeding, candidate selection,
Sec IV cuts, detector smearing all untouched). Verified via git diff: no
change touches analyze_one(), no change touches any rdf.to_csv() call, no
change touches signal generation, background code, or any random seed.
Verified via `git status --short` on both cutflow CSVs: zero modification.

DOWNSTREAM IMPACT: Fig 4 (single-event hit-pattern display) and Fig 5
(Delta_s/Delta_w distributions) are UNAFFECTED -- both depend on the raw
ds/dw values themselves, which are unchanged; only a summary RATIO's label
and denominator-numerator pairing was corrected. Fig 6 readiness: the
epsilon_reco term that would feed any future exclusion-contour calculation
should use this corrected definition going forward; Fig 6 itself remains
NOT YET REPRODUCED (no grid scan attempted), now on a firmer footing for
the EW benchmark specifically.

NOT DONE (explicitly out of scope, correctly not attempted): no new signal
events generated; colored-quirk's small-N limitation was NOT resolved
(would require new simulation); Fig 6 grid scan not started.

## 2026-09-17 ~15:30 — Fig. 5 reproduction (existing data only)

Reproduced Fig. 5 (Δs/Δw signal+background distributions) using ONLY existing pipeline
outputs; no new simulation run. Fresh re-read of paper.txt Sec IIIC/IIID/IV + Fig 5 caption
confirmed: left panel = dσ/dlogΔs (fb/bin, absolute-normalized); right panel =
(1/σ)dσ/dlogΔw (unit-normalized); population = Sec IIIC plane-found (paper's own εreco
population, pre-Sec-IV-final-cuts) — explicitly NOT contaminated by the earlier-corrected
sec_iv_final_pass_rate quantity.

Used: colored/EW quirk cutflow CSVs (ds/dw populated via select_reconstructed_plane
fallback, N=5/N=32). Used pileup mu=50 audit-reproduction CSV (N=59), flagged as a BIASED
subsample (>=4-layer winning candidates only, not the full Sec IIIC winner population).
Converted-photon CONFIRMED UNUSABLE: ds/dw never recorded in
conversion_scan_results_v2_VERTEX_FIXED.csv for any of 9139 rows — genuine data gap, not
fabricated.

Both panels rendered unit-normalized (shape only) as a stated approximation, since no
measured cross-section exists for colored-quirk or pile-up to support the paper's absolute
fb/bin left-panel convention. No detector/cut/bin/weight values tuned.

Outputs: 05_coplanarity_analysis/fig5_reproduction_2026-09-17/{fig5_left_panel_ds.png,
fig5_left_ds_only.png, fig5_right_dw_only.png, fig5_data_v3_2026-09-17.json,
AUDIT_NOTE.md}. No physics code modified. Fig 6 not started.

## 2026-09-17 ~19:15 — Converted-photon Fig. 5 recovery (analysis-only, no new physics)

Patched convert_and_analyze.py to also call select_reconstructed_plane(candidates)
(Sec IIIC winner, no RNG draw) alongside the existing Sec IV apply_signal_region_cuts()
call, recording sec3c_ds/sec3c_dw/sec3c_plane_found/sec3c_n_layers. Reran the full
9139-event zgamma_photons.csv sample, same seed=99, same event order. Verified
bit-identical to conversion_scan_results_v2_VERTEX_FIXED.csv on every pre-existing
column (status, n_hits, n_candidates, passes, ds, dw, conv_r_cm, weight_pb) and on
final Sec IV pass (0/9139 both). New result: N_plane_found=2982/9139; Delta_s
median=0.02116, p16=0.01489, p84=0.02723, min=0.00089, max=0.04816, frac<0.01cm=0.0312
(93 events); Delta_w median=0.17767, p16=0.06663, p84=0.38705, min=0.01512, max=0.76062.
Saved: conversion_scan_results_v3_SEC3C_DS_DW.csv. Commit 96f0fe0.

Gap discovered during this recovery: v3 does NOT record a hit-multiplicity-pass flag
for the Sec IIIC winner (only ds/dw/plane_found/n_layers) -- a small follow-up gap,
not blocking the Fig. 5 Delta_s/Delta_w curves themselves.

## 2026-09-17 ~19:20 — Pile-up analysis-only full-cutflow recovery (launched, no new physics)

Added run_one_background_event_full_cutflow() (additive twin of
run_one_background_event_suppressed(), same detector/suppression/ancestry/vertex chain,
adds select_reconstructed_plane + check_hit_multiplicity diagnostics) and
run_sec3c_fullcutflow_sweep.py (same SeedSequence([90210777,mu,i]) convention, same
minbias_pool_20000_ANCESTRY_v1.csv pool as the original sweep). Verified bit-identical
against audit_mu5_event2006_reproduced.csv and 5 spot-checked audit_mu50_4of8_events_
reproduced.csv rows before launching. Commit 57941cc. Launched as PID 124614,
sequential mu=0,5,10,20,50, n=5000 each, checkpointed, outputs
pileup_mu{N}_n5000_sec3c_fullcutflow_v1.csv under sweep_mu_2026-09-16/.

## 2026-09-18 ~00:15 — Pile-up full-cutflow recovery COMPLETE (all 5 mu points, no new physics)

run_sec3c_fullcutflow_sweep.py completed all 5 mu points (0,5,10,20,50, n=5000 each) after
one metadata-only crash (provenance study_type whitelist, fixed commit e79e6ff, mu=0 data
unaffected/skipped-on-resume). Total wall time ~16193s for mu=50 alone (dominant cost);
mu=0/5/10/20 << 100s combined.

DIRECT (not inferred) results: N_plane=0,3,6,22,172 at mu=0,5,10,20,50. N_hit_mult_pass=0
at every mu. N_final_SecIV=0/5000 at every mu -- this UPGRADES the prior logical-inference-
based "0/5000 proven" result (RUN_LOG 2026-09-17 ~10:30, Evidence class B+C) to a direct
full-statistics computation (Evidence class A) for all five mu points.

Confirmed N_plane==N_raw_candidates exactly at every mu: every raw seeding_and_iterative_fit
candidate in this pile-up sample already satisfies Delta_w<1cm (verified: dw range among
mu=50's 172 plane-found events is [0.321, 0.997]cm, all <1.0) -- select_reconstructed_plane's
own filter is a structural no-op here, not a bug.

Fig. 5 mu=50 pile-up reweighting (paper's exact 1-hit-per-layer prescription, computed on
the FULL unbiased 172-event plane-found population, superseding the biased 59-event
>=4-layer-only subsample used previously): w_mult = N_hit_mult_pass/N_plane = 0/172 = 0.0
point estimate, Wilson 95% CL upper bound ~0.0218. Delta_s (unweighted, plane-found
population): median=0.03143, p16=0.01948, p84=0.04045, min=0.00168, max=0.04991,
N(<0.01cm)=7/172=0.0407. Delta_w: median=0.76399, p16=0.60847, p84=0.88552, min=0.32071,
max=0.99659.

Saved: pileup_mu{0,5,10,20,50}_n5000_sec3c_fullcutflow_v1.csv,
pileup_fullcutflow_summary_v1.json. Commits e79e6ff (fix), e32e03e (results).

## 2026-09-18 ~07:00 — Pile-up-only statistics freeze (v1) COMPLETE, no new simulation

Built build_pileup_only_statistics.py: joins the original sweep and Sec IIIC/
Sec IV fullcutflow CSV families (both already-completed, mu=0,5,10,20,50,
n=5000) on event_i, runs full file-integrity validation (all 10 files: 5000
rows, 5000 unique event_i, 0 duplicates/missing, non-negative fields,
postmerge<=premerge, final_sec_iv_pass implies all upstream cuts, mu=0
all-zero sanity -- ZERO issues found), then computes Poisson/ancestry/
suppression/per-layer/cutflow/Delta_s/Delta_w/coverage/paper-comparison/
reweighting statistics with Wilson/Clopper-Pearson intervals throughout.

Corrections made during this freeze: (1) the paper's quoted ~1e-3/~6e-5
values correspond to the >=4/8 and 8/8 RAW-CANDIDATE coverage diagnostics,
not the Sec IIIC selected-plane population or the final Sec IV rate --
explicitly separated in table8_paper_comparison.csv (comparability
PARTIAL/PARTIAL/NO respectively). (2) w_mult=0/172's denominator-population
match to the paper's "1-hit-per-layer-allowed" phrase is UNRESOLVED/
ASSUMPTION, not settled; the zero point estimate carries a Wilson 95% CL
upper bound ~0.0218, must never be presented as an exact physical weight.

Explicitly NOT AVAILABLE FROM STORED FIELDS (documented, not fabricated):
pool-reuse identities (sampled_pool_event_ids never persisted), per-class
hit-removal breakdown, postmerge/timing-rejected hit counts, full
raw-candidate layer-coverage histogram. One tiny 1-event deterministic
replay (mu=5, event_i=2006, the sweep's only has_8_of_8_plane=True event)
recovered its exact per-layer hit breakdown -- bit-identical to the prior
independent audit reproduction; failure reason: only 2/8 layers have >=2
hits (need >=7).

Outputs: 05_coplanarity_analysis/pileup_only_statistics_v1/ (10 tables, 12
figures, 5 per-layer CSVs, w_mult_reassessment.json, integrity_check_
report.json), docs/pileup_only_final_statistics_v1.md. Commits b9c2547
(script), 1f697f0 (tables), 4f0e4ff (figures), 0d2e391 (report).

CONCLUSION: The pile-up-only study is frozen as an authoritative project
result with documented limitations. Zero final Sec IV events were observed
in each 5000-crossing sample; this is not a claim that the underlying
probability is exactly zero. Converted-photon overlay work NOT started in
this task, per explicit instruction -- awaiting separate authorization.

## 2026-09-18 ~08:15 — Converted-photon-only statistics freeze (v1) COMPLETE, no new simulation

Built build_converted_photon_only_statistics.py + test_converted_photon_only_
statistics.py for the completed 9139-event conversion_scan_results_v3_
SEC3C_DS_DW.csv (commit 96f0fe0). Independently verified rather than
blindly repeated: historical PID 95330 (confirmed via live ps checks earlier
in this session, not log reconstruction); exit code 0; wall time 17057s
(4.738h, 1.8672s/event, 1928.85 events/hour -- CORRECTS an unverifiable
"535.8 events/hour" figure supplied in the task prompt, which could not be
reproduced by any consistent unit interpretation); v3 bit-identical to v2 on
all 8 common columns (0 unequal cells); all 12 previously-reported Delta_s/
Delta_w statistics independently reproduced to 1e-4 tolerance.

Confirmed CONVERTED-PHOTON-ONLY / NO PILE-UP classification via direct
source inspection (zero "pileup"/"overlay" occurrences in convert_and_
analyze.py). New intermediate cutflow counts recovered: N(any detector hit)
=7811/9139 (85.47%), N(raw candidate | any hit)=2982/7811 (38.18%),
N(>=4/8 layers)=2957/2982, N(8/8 layers)=1479/2982 -- none of these were
previously reported. Confirmed dataset-specific (not general) identity:
n_candidates>=1 exactly equals sec3c_plane_found in this sample (max 1
candidate/event throughout).

Documented gaps (not fabricated): hit-multiplicity pass flag, electron/
positron-origin hit split, per-layer raw/postmerge hit tables, timing/eta-
rejected hit counts, CPU time, peak/average RSS, and runtimes for
generation/extraction/v1/v2 stages -- all require either a full rerun or
were never instrumented.

18/18 reproducibility tests pass (exit 0). Outputs: 05_coplanarity_analysis/
converted_photon_only_statistics_v1/ (7 required tables + sidecars + 9
figures + 3 plot-source CSVs), docs/converted_photon_only_final_statistics_
v1.md. Commits 5daf50b (script+tests), 9c2af53 (tables), 59df98d (figures),
788d3a8 (report).

CONCLUSION: The 9139-event converted-photon result is a validated
conversion-only baseline. The paper-required converted-photon plus pile-up
result has not yet been demonstrated. Overlay implementation NOT started in
this task, per explicit instruction -- awaiting separate authorization.

## 2026-09-18 ~09:30 — Master PPT statistics package (read-only, no new simulation)

Built build_ppt_statistics.py: independently recomputed complete EW/colored
signal statistics directly from cutflow CSVs (not from memory), and
cross-checked the prompt-supplied pile-up cutflow table against the already-
frozen pileup_only_statistics_v1 package -- CONFIRMED exact match for all 5
mu. Combined with the existing converted-photon-only freeze package
(read-only reuse, no recomputation of underlying physics) to build master
cutflow, master Delta_s/Delta_w, paper-vs-project, and notable-events
tables.

Verified directly from CSVs (not assumed): EW final-passing events
[260,313,322,332,362,438]; colored final pass event 386 (ds=0.009367);
colored near-misses 208 (ds=0.010464) and 369 (ds=0.011863); colored
zero-candidate events 38 and 169 (truth_fiducial=True, n_candidates=0);
colored full cutflow 125->27->11->7->5->1 confirmed exactly.

Outputs: 05_coplanarity_analysis/ppt_statistics_v1/ (12 ppt_table*.csv +
8 appendix JSON/CSV files), docs/PPT_STATISTICS_SOURCEBOOK_v1.md. Commits
1f152e4 (script), d1920fd (tables), [this commit] (sourcebook + RUN_LOG).

No physics code, cuts, or authoritative CSVs modified. No simulation
launched. PPT itself NOT created, per explicit instruction -- awaiting
review.

## 2026-09-18 ~10:15 — Converted-photon A-Z PPT study: v3 deliverables complete, v4 rerun launched

Re-verified baseline (unchanged): v3 9139/9139, PID 95330 (historical),
17057s=4.738h, 1.8672s/event, 1928.85 events/hour, final 0/9139.

Added convert_and_analyze_v4_full_diagnostics.py (additive, new standalone
script, does NOT modify v3): recovers hit_multiplicity_pass,
winner_layer_hit_counts, e-/e+/mixed hit-origin split, hit-timing stats --
all derivable from objects v3's own simulate_quirk_hits/candidates already
compute but discard, zero new physics, zero new RNG draws. Regression-tested
(test_v4_regression.py) against v3 for n=5 and n=50 event prefixes: all 11
pre-existing columns bit-identical, 0 failures. Benchmarked 97.06s/50 events
=1.94s/event, projecting ~4.93h (under the 6h authorization threshold).
Confirmed no other CPU-heavy process, 946G disk/2.9G RAM free. Launched
PID 165371.

Built 17 PPT tables + 10 figures under converted_photon_ppt_statistics_v1/
from v3 + zgamma_photons.csv (new: photon pT/eta/MET kinematics, all trivially
satisfy the MET>200/pT_gamma>0.5 cuts by construction, confirming the
extraction file). Hit-multiplicity-dependent fields explicitly marked
PENDING v4, not fabricated. Wrote interim docs/converted_photon_A_to_Z_
final_report_v1.md (STATUS: INTERIM).

Commits: e999fc0 (v4 driver+tests), 6f5eece (figure regen script), 9bc278c
(17 tables), 2257274 (figures), [pending] (report+RUN_LOG). Converted-photon
+ pile-up overlay and PPT itself NOT started, per explicit instruction.

## 2026-09-18 ~11:10 — Converted-photon reusable event/hit/candidate cache PROTOTYPE (n=100, no full rerun)

Per explicit instruction to prevent future full photon reruns: assessed the
currently-running v4 process (PID 165371, healthy, untouched, still running)
and confirmed its columns are INSUFFICIENT for full future reuse -- v4 only
saves scalar/aggregate summaries (hit_multiplicity_pass, winner-only layer
counts, e-/e+/mixed hit counts), not raw per-hit records, candidate
memberships, or per-hit provenance. v4's checkpoint is a plain partial CSV,
not a stored-object cache, so richer data cannot be retroactively extracted
from it without repropagation.

Per the task's own decision tree, produced only a SMALL diagnostic cache
SAMPLE (n=100, NOT a full 9139-event rerun): build_photon_event_cache_
prototype.py, a separate process (same rng=default_rng(99) stream,
read-only against zgamma_photons.csv), captures event identity, raw
pre-merge hits (traj["raw_hits"], pre-existing field), merged post-merge
hits with source_quirk_indices provenance, ALL raw candidates (not just
winners) with per-layer hit counts, and a candidate<->hit join table.
Stored as compressed .npz (no pyarrow/h5py available in this environment;
NPZ satisfies the task's own "Parquet/HDF5/NPZ or another compressed
structured format" allowance) + one compact CSV, with a schema-version/
units JSON sidecar.

Validated (test_cache_only_analysis.py, 11/11 pass): unique IDs, no
duplicates, all links resolve, raw/postmerge counts match the event
summary exactly, and -- the key result -- complete cutflow, per-layer
table, Delta_s/Delta_w stats, multiplicity, failure-reason classification,
notable-event lookup, AND a hypothetical Delta_s<0.02cm cut-threshold
diagnostic are all reproduced from the cache ALONE in 0.025s (vs 279.78s
to generate the cache), peak RSS 71.6MB.

Documented gaps: raw-to-merged hit provenance not individually resolved
(only merged_count); eta/timing-rejected raw crossings not separately
logged (filtered inline in simulate_quirk_hits, never counted). NO full
9139-event cache was generated -- that remains a future, separately-
authorized decision.

Commits: 04ce39d (script+test), 4411c6d (n=100 cache outputs, 132KB).

v4 (PID 165371) confirmed healthy and undisturbed throughout this work.
