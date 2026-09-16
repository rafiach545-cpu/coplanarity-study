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
