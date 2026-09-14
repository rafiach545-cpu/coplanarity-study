# Deviations from arXiv:1708.02243 — running log

Every place our numbers/inputs differ from the paper's own choices, logged as
it's found, with the reasoning. No silent substitutions.

---

## 1. Detector geometry source: real Run-2 alignment paper, not the paper's own [27]

**What the paper used:** ref [27], "The Expected Performance of the ATLAS
Inner Detector," ATL-PHYS-PUB-2009-002 — a **2009, pre-Run-2 projected**
performance document.

**What we use instead:** ATLAS Collaboration, "Alignment of the ATLAS Inner
Detector in Run-2," arXiv:2007.07624 (Table 1) — **actual measured Run-2**
geometry/resolution, per your explicit instruction ("geometry atlas geometry
ho run ii").

**Why:** you asked for real Run-2 geometry rather than the paper's own
pre-Run-2 projection, on the reasoning that we should "copy all the things
from the paper and try to bring the better results" — i.e. improve on the
paper's inputs where a more accurate source exists, not just reproduce it
verbatim.

**Consequence (found during audit, 2026-09-12/13):** SCT z-resolution from
the real Run-2 paper is 580 um intrinsic -> 1160 um after the paper's own
"double the intrinsic accuracy" conservative prescription (Sec III A). This
is large enough, relative to the paper's tight seeding cut (Delta_s < 0.05
cm at the 4-hit seed stage, Sec III C), to noticeably reduce reconstruction
efficiency versus the paper's published Table I numbers.

**Verification that this is real detector resolution, not a bug:**
recomputing the same seed 4-hit combination using the exact, UNSMEARED
trajectory crossing points (bypassing all detector resolution effects
entirely) gives Delta_s = 0.00049 cm (4.9 microns) — i.e. the underlying
physics is essentially perfectly coplanar, exactly as expected. The full
0.064 cm Delta_s seen once realistic SCT smearing is applied is entirely a
detector-resolution effect, not a trajectory-integration or algorithm bug.

**Measured result** (colored quirk benchmark, mQ=1800 GeV, Lambda=2 keV,
101 trigger-passing events from a 1000-event signal sample, seed algorithm
exactly as coded per Sec III C):
- 23/101 events reach the full 16 hits (both quirks through all 8 layers)
- 0/23 of those pass the final signal-region cuts (Delta_s<0.01cm AND
  Delta_w<1.0cm)
- Paper's own Table I claims epsilon_reco = 0.35 at this exact benchmark
  point (mQ=1800 GeV, Lambda=2 keV) — using their own (2009-projection-
  based) detector resolution assumptions.

**Decision (user, 2026-09-14):** keep the real Run-2 resolution numbers.
Report the resulting (lower) efficiency honestly as a genuine, explained
consequence of using more accurate detector inputs than the paper had
available — not as an unresolved bug. Do not tune resolution values to
force agreement with the paper's published efficiency number.

**Open item:** current statistics (0/23) are compatible with, but do not by
themselves prove, a small-but-nonzero true efficiency under the real Run-2
resolution — 23 events is not enough to resolve efficiencies below a few
percent reliably. Larger event samples are needed for a precise number.

---

## 2. Trajectory-integrator timestep: CM-frame vs lab-frame velocity (bug, fixed)

**Bug found (2026-09-13):** the oscillation-period estimate used to choose
the RK4 integration timestep in `simulate_quirk_hits()` used quirk 1's
LAB-FRAME velocity/gamma. Eq. 4's period formula is derived in the PAIR's
CM frame; using lab-frame quantities is only correct for a non-boosted
pair. Every real MadGraph-generated event has a boosted, asymmetric pair,
so this was wrong for all real events tested — even though the core
integrator had already been validated to 1e-12 relative error against Eq.4,
because that validation deliberately used symmetric, non-boosted test
conditions where lab frame == CM frame by construction, and so never
exercised this bug.

**Fix:** properly boost quirk 1's 4-momentum into the pair's own CM frame
(general relativistic boost along the pair's actual net-momentum direction,
not restricted to a single Cartesian axis) before extracting v_internal and
gamma_internal for the period/timestep estimate.

**Impact measured:** for the specific high-pT test event checked, the
correct CM-frame period was ~61% of the (buggy) lab-frame-based estimate.
Despite this, the seed-stage Delta_s barely changed (0.0641 -> 0.0643 cm)
once the fix was applied — RK4 was already accurate enough at the coarser
(buggy) timestep for this event, so this bug was NOT the dominant cause of
the reduced reconstruction efficiency (see item 1 above), but it was a real
correctness bug regardless and is now fixed.

---

## 3. Photon-conversion background pT_gamma cut, MET cut (built 2026-09-14)

Built as an exact generation-level cut, not a proxy: MadGraph's run_card
`misset` parameter is documented as "minimum missing Et (sum of neutrino's
momenta)" and the run_card explicitly states this and similar cuts "always
apply" at generation time. Since neutrinos are neutral and colorless, they
are completely untouched by Pythia8's shower, so this cut is exact, not an
approximation -- confirmed by re-deriving MET from the actual post-shower
event record.

**Caveat found and handled:** an exact match between the generation-level
`misset` cut and the "true" physical MET is NOT guaranteed, because Pythia8's
hadronization step creates ADDITIONAL soft neutrinos from semileptonic
hadron decays inside the jet (b -> c + lepton + neutrino, etc.), which the
generation-level cut (evaluated on only the 2 primary Z-decay neutrinos)
does not see. A real calorimeter-based MET trigger would see all of these.
Measured impact: 861/10000 events (8.6%) have true post-shower MET < 200 GeV
despite passing the generation-level cut. Fix: apply an exact final MET cut
using ALL final-state neutrinos (primary + secondary) post-shower, rejecting
those 861 events, rather than trusting the generation-level value alone.

## 3b. Trajectory integration cutoff bug: silently truncated low-boost events (found 2026-09-14, FIXED)

**Found while running the EW quirk (mQ=800 GeV, Lambda=4 keV) benchmark**: 0/89
trigger-passing events reached full 16-hit fiducial coverage -- a stark,
suspicious contrast to the colored quirk benchmark's 23/101. Investigated
rather than reported as a bare efficiency number.

**Root cause**: `simulate_quirk_hits()`'s integration time cutoff was
`t_max = n_periods_to_integrate * period_est` (40 internal oscillation
periods) with NO guaranteed floor tied to the actual geometric requirement
(the CM's flight time to physically reach the outer detector layer). For
one traced EW quirk event: 40 periods = 1.4e15 (natural units) vs the
~4.7e16 actually needed given that event's CM boost (beta_cm=0.194) --
**33x too short**. Both quirks' trajectories were found to max out at
r~4.5cm (never even reaching layer 2 at r=5.05cm), confirming the
trajectory was being cut off, not genuinely failing to reach the detector.

This is exactly the failure mode flagged as a risk in a code comment when
`simulate_quirk_hits` was first written (an earlier version of this log /
code commentary already said "this cap might not even engage t_needed
meaningfully... could cause the integration to stop too early") -- flagged
as a possibility but never verified to actually occur, and it turned out to
occur systematically for the EW quirk benchmark (short Lambda=4keV period,
lighter 800 GeV mass, and typically lower per-event CM boost) even though
the colored-quirk benchmark's parameters happened to avoid triggering it in
the runs done so far. Given this was never verified for the colored quirk
sample either, some of ITS low-boost events could plausibly have been
silently truncated too -- not yet re-audited event-by-event, flagged as an
open follow-up.

**Fix**: `t_max` now always covers `max(n_periods_to_integrate * period_est,
t_needed_geometric)` when `max_layer_r_cm` is given, where `t_needed_geometric`
is the CM flight time to 3x the outer layer radius. To keep runtime bounded
for events needing many periods, `dt` is coarsened (relaxed) to stay within a
120,000-step budget, rather than either silently truncating `t_max` or letting
step count grow unbounded. Verified on the exact event that exposed the bug:
now correctly finds all 16 hits, trajectory reaches r=152cm (well past the
outer layer), vs the previous r=4.5cm cutoff.

**Cost**: this fix makes low-boost events noticeably slower (the traced
event went from failing fast to ~42s, using the full step budget) since
they now correctly integrate the full required flight time. Necessary
correctness fix, not optional.

**Status**: fixed and fully re-verified. Corrected results (both re-runs
complete, 2026-09-14):
- Colored quirk (1800 GeV, 2 keV): N_truth_fiducial 56/101 (55.4%), vs the
  bugged run's 23/101. Best full-8-layer-coverage candidate: event 12,
  Delta_s=0.0192cm, Delta_w=0.548cm (still fails the final Delta_s<0.01cm
  cut; the Fig.4 artifact was rebuilt with this corrected event, replacing
  the old bugged "event 27" at Delta_s=0.0184cm). 0/101 events pass the
  complete signal-region cuts (same qualitative conclusion as before the
  fix, but now on a doubled, non-truncated fiducial sample).
- EW quirk (800 GeV, 4 keV): N_truth_fiducial 41/89 (46.1%), vs the bugged
  run's 0/89 -- this benchmark was unusable before the fix. 0/41 events
  pass the complete signal-region cuts.
- A separate, real algorithmic subtlety was found and confirmed (not a
  bug): the smallest-Delta_s candidates in both samples come from the
  greedy iterative algorithm finding a very tight fit across only 3-5 of
  the 8 layers (the growth-factor<=3x check legitimately stops it from
  extending further), correctly rejected by the per-layer hit-multiplicity
  cut. This is the paper's own specified algorithm behavior, faithfully
  reproduced -- verified by direct inspection of a specific case (event 48,
  colored quirk: Delta_s=0.0032cm from a 5-hit/3-layer candidate, correctly
  rejected).

## 4. Z+gamma+jet cross-section: ~4.7x gap vs paper's quoted ~1 pb -- UNRESOLVED

Measured: 0.2311 pb (10000-event MadGraph5_aMC@NLO+Pythia8 sample, pT_gamma>
0.5 GeV, MET>200 GeV exactly, ptj=20 GeV default, draj=0.4 default,
nn23lo1 PDF, MadGraph default dynamical scale). Paper (Sec III D) quotes
"~1 pb" at this same stage (before the beampipe-conversion requirement).

The paper's text gives ONLY two generation cuts explicitly: pT_gamma>0.5 GeV
and MET>200 GeV. It does not state ptj, any isolation parameter, PDF set,
scale choice, or whether an NLO K-factor was applied. Every other choice in
my run_card (ptj=20 GeV, draj=0.4, nn23lo1 PDF, dynamical scale) is a
MadGraph DEFAULT, never independently verified against the paper, because
the paper does not specify a value to check against.

**Tests actually performed (not just argued):**
- ptj 20 GeV -> 5 GeV: 0.2311 -> 0.2225 pb. Negligible, WRONG DIRECTION
  anyway if this were the fix (paper's cross-section is HIGHER than mine,
  and loosening ptj barely moved mine at all). Ruled out as the cause.
  Physical reason for the near-zero sensitivity: MET>200 GeV already forces
  a hard recoiling jet via momentum conservation, so ptj was never the
  binding constraint.
- draj (photon-jet isolation) 0.4 -> 0.1 (looser): 0.2311 -> 0.3057 pb.
  Real, ~32% effect -- but far short of the needed ~4.7x, AND the paper's
  own wording ("isolated photon conversions") suggests TIGHTER isolation
  than default, not looser, meaning this knob likely moves the wrong way to
  help close the gap, not the right way.
- PDF (nn23lo1) and scale (MadGraph dynamical default): not individually
  scanned; standard, unremarkable choices, not expected to produce a 4.7x
  shift on their own for this process class, but not conclusively ruled out
  either.

**Status: genuinely unresolved, but with a leading candidate explanation**
(user's suggestion, 2026-09-14): the paper's generator is named
"MadGraph5_aMC@NLO" -- the "aMC@NLO" capability means it CAN run at
next-to-leading order, and our own run was confirmed LO (Sec 1 of the
earlier read-only audit: plain `sm` model, no NLO tags in the process
definition, `output` not the NLO pipeline). An NLO K-factor of ~2-5x for a
Z+gamma+jet-type process is physically plausible and would be large enough
to explain the gap on its own. This was NOT tested (would require setting
up the NLO generation pipeline, a nontrivial additional step) and is not
being chased further -- **decision (user, 2026-09-14): use our own LO
cross-section values as-is, clearly documented as LO (not the paper's
possible NLO number), since this reproduction is for training/validation
purposes.** Every place this cross-section is quoted must be labeled
"LO, MadGraph5_aMC@NLO run in leading-order mode" so the distinction is
never silently lost. Not dismissed as "likely minor" -- that was an
incorrect assessment made without evidence and has been corrected; this is
a documented, plausible, unconfirmed candidate cause, not a solved problem.

**NLO test actually attempted (2026-09-14), blocked by a real environment
limitation, not by the physics setup:**
1. Generated `p p > z a [QCD]` (genuine NLO QCD process) with MadGraph5_aMC@
   NLO's real NLO pipeline -- this succeeded (auto-installed ninja and
   collier, the one-loop reduction libraries, without issue).
2. Attempted a fixed-order NLO cross-section calculation (`fixed_order=ON`)
   with `ptgmin=0.5` matching the LO run. Failed: linking against FastJet's
   C++ library (needed for jet clustering in the real-emission/FKS
   subtraction terms) produced dozens of "undefined reference" errors for
   core FastJet classes (ClusterSequence, PseudoJet, etc.) -- a compiler
   ABI mismatch between conda's toolchain and the installed FastJet build,
   not a physics or configuration error.
3. Attempted the same fix that resolved the earlier Pythia8 version
   mismatch: reinstalling the dependency via MadGraph's own installer
   (`install fastjet`) for a self-consistent build. This failed at an even
   more fundamental level: `undefined reference to '__TMC_END__'` when
   linking the shared library -- a known class of incompatibility between
   conda's bundled GCC/binutils and `-shared -nostdlib` link flags,
   unrelated to FastJet specifically. This is a deeper conda-toolchain
   limitation than the Pythia8 case, not something fixable by the same
   trick.

**Conclusion**: NLO calculation is blocked by a genuine environment
limitation in this specific conda-based setup, not abandoned out of
convenience. Per the user's explicit authorization, not pursued further
(e.g. rebuilding FastJet from source with matched compiler flags, or
setting up a non-conda toolchain, would likely resolve it, but is out of
scope for a training/validation reproduction). LO cross-section values are
used throughout, clearly labeled as such.

## 5. `apply_signal_region_cuts` selection-order bug: cut-shopping across raw candidates instead of the paper's single designated plane (bug, fixed 2026-09-14)

**Bug found on a direct re-audit of `coplanarity_fit.py` against Sec III C /
Sec IV of arXiv:1708.02243**: the paper's algorithm is explicitly two-stage.

- Sec III C, step 3 ("Event Selection"): "Gather all the reconstructed
  lists, apply the final cut Delta_w < 1cm. If there are more than one
  plane identified, keep the one with the smallest Delta_s." This collapses
  ALL raw seed-candidates down to exactly ONE reconstructed plane per event.
- Sec IV then checks that SAME single plane against the hit-multiplicity
  cut and Delta_s < 0.01cm.

The old `apply_signal_region_cuts` instead searched across every raw
candidate for one that simultaneously satisfied Delta_w<1cm, Delta_s<0.01cm
AND hit-multiplicity, then took the smallest-Delta_s survivor of THAT
filtered set. This lets an event pass via a candidate the paper's own
algorithm would never have designated as "the" reconstructed plane --
e.g. if the true Sec-III-C winner (globally smallest Delta_s among
Delta_w<1cm candidates) fails hit-multiplicity, but some other, non-winning
candidate with a larger (still <0.01cm) Delta_s happens to pass every cut,
the old code accepted the event; per the paper it must be rejected, since
the event is already decided by the single Sec-III-C-selected plane.
Directly demonstrated with hand-crafted candidate fits: a candidate A
(smallest Delta_s, fails hit-multiplicity) and candidate B (larger but
passing Delta_s, passes hit-multiplicity) -- old code returned B (PASS),
new code correctly returns None (REJECT), matching the paper's stipulation
that A is the only plane the algorithm designates.

**Fix**: split out `select_reconstructed_plane()` implementing Sec III C
step 3 verbatim (filter Delta_w<1cm, keep smallest Delta_s), and rewrote
`apply_signal_region_cuts()` to check Sec IV's hit-multiplicity and
Delta_s<0.01cm cuts ONLY against that single winner. Also fixed
`analyze_ew_quirk.py`'s Fig-5-style "informational Delta_s/Delta_w even when
final cuts fail" fallback, which previously took an unfiltered global-min-
Delta_s candidate (not even applying the Sec-III-C Delta_w<1cm filter) --
now uses `select_reconstructed_plane()` too.

**Impact on previously reported numbers**: not yet re-measured on the full
colored-quirk (1800 GeV, 2 keV) / EW-quirk (800 GeV, 4 keV) samples from
item 3b above -- those reported 0/101 and 0/41 events passing regardless,
so the two logics may or may not disagree on those specific samples; this
needs a re-run to confirm whether the 0/101, 0/41 conclusion still holds
under the corrected selection order. Flagged as an open follow-up, not
assumed unaffected.
