# EW Trigger and Fiducial Efficiency Discrepancy — Complete Audit

**Benchmark**: EW quirk, mQ=800 GeV, Λ=4 keV. **Read-only** except for one
minimal, deterministic, seed-based replay of already-generated events
(explicitly permitted — not new event generation; no MadGraph/Pythia8
run, no new physics). No frozen file modified. No commit/push. Figure 6
untouched. The ε_reco-definition question is explicitly out of scope per
instruction and not discussed here.

**IMPORTANT CORRECTION (see `CAUSAL_KINEMATICS_FOLLOWUP.md`)**: this
original document initially stated the "harder ISR spectrum" explanation
for the fiducial discrepancy as if demonstrated. At the time it was
written, that was a plausible, physically-motivated hypothesis, not a
tested result. A follow-up causal test (binned efficiency, correlation,
and mediation analysis on existing events, no new simulation) has since
**demonstrated** that harder pT_pair kinematics do have a real,
statistically significant, η-independent positive association with
fiducial pass rate — see the follow-up document for the actual test and
its appropriately hedged conclusion. The trigger-efficiency root cause
itself remains UNRESOLVED either way. Read the follow-up alongside this
document; do not treat this document's original phrasing below as final.

**Headline verdict: NO BUG FOUND in the trigger or fiducial computation.**
Both discrepancies (17.80% vs paper's 10%; 50.54% vs paper's 28%) are
classified **UNRESOLVED — undocumented paper generator settings**, with
a specific, well-evidenced physical mechanism identified (below, and now
causally tested in the follow-up). This matches and extends an earlier,
independent audit of the same question
(`05_coplanarity_analysis/ew_discrepancy_audit_v1/`, 2026-09-21) reaching
the same conclusion on the 1000-event sample — this audit reproduces
that conclusion on the fresh 2000-event sample with a deeper, more
exhaustive check (including an item not previously tested: the
per-quirk layer-coverage false-positive risk).

---

## 1–2. Paper definitions, reread directly, with exact quotes

**Trigger** (Sec. III B, p.4-5, direct quote): *"...we therefore impose
a pT > 200 GeV cut on the center of mass momentum of the quirk/anti-quirk
system."* This is a cut on the **vector-sum transverse momentum of the
two quirks themselves** — explicitly NOT MET as a separately-measured
quantity (MET is only discussed earlier in the same section as what the
*trigger hardware* would misinterpret the recoil as; the analysis-level
cut used throughout the paper is stated as the CM-system pT itself).

**Fiducial** (Sec. IV, p.7, immediately after Eq. 12, direct quote):
*"The fiducial efficiency parametrizes the likelihood that each quirk
intersect with each layer at least once, in events passing the trigger.
We also include a 25 ns timing cut..."* — denominator is explicitly
"events passing the trigger"; numerator requires **each** quirk (i.e.
both, independently) to intersect **each** layer (all 8) at least once,
plus the 25 ns timing cut.

Full table with page/section citations: `tables/paper_vs_project_requirements.csv`.

## 3. Event trace, generated → showered/matched → trigger → 2 quirks → propagation → geometric → timing

Full per-event table (all 1045 matched events, every stage labeled):
`tables/event_level_cutflow.csv`. Closure verified exactly:
859 (matched, not triggered) + 92 (triggered, not fiducial) + 54 (plane
found) + 19 (fiducial only) + 21 (final Sec IV pass) = 1045 = N_matched;
92+54+19+21 = 186 = N_trigger; 54+19+21 = 94 = N_fiducial. No missing or
duplicated events at any stage.

## 4. Trigger variable verified exactly as paper's CM-system pT

Confirmed by direct code read (`01_signal_generation/extract_pilot_data.py`,
`parse_hepmc()`): quirks are selected as `status==1` (final-state,
post-shower) particles with an **exact PDG match** (`|pdg|==9000011`),
then `quirk_pair_pt_gev = hypot(px1+px2, py1+py2)` — the vector sum of
the two identified quirks' own momenta. The `leading_other_pt_gev`
column (the leading non-quirk particle's pT, i.e. what a real MET
trigger would actually see) is stored but **confirmed not used anywhere**
in the trigger decision. `trigger_proxy_pass = quirk_pair_pt_gev > 200`
(strict `>`). This is the paper's literal criterion, not an approximation
— the project's own "trigger proxy" naming undersells its accuracy (a
labeling nit, not a bug, already flagged in the prior 2026-09-21 audit).

## 5. Threshold/units/boundary audit

Full table: `tables/trigger_threshold_audit.csv`. All checks PASS:
- 0 events sit exactly at pT_pair=200.0 GeV (no strict-vs-≥ ambiguity
  materializes in this dataset).
- 8 events fall in the [195,205] GeV window; all `trigger_proxy_pass`
  values are consistent with the stated strict-`>` cut.
- Recomputing `quirk_pair_pt_gev` from stored `px/py` independently
  matches the stored column to floating-point roundoff (max diff 2.3e-13
  GeV).
- Units consistent throughout (GeV).
- Particle status: `status==1`, i.e. **post-shower** final-state
  momenta (see §6 discussion for why this is the physically correct
  choice, not a bug).

## 6. Generation and matching settings — full audit for ISR sensitivity

**Key physical fact established in this audit** (not previously stated
this explicitly): for a pure 2→2 Drell-Yan process, the quirk/anti-quirk
pair's net transverse momentum is **identically zero** by momentum
conservation — any nonzero pT_pair value is *entirely* generated by
extra QCD radiation (ISR, captured via the "+1 jet" MLM-matched sample).
This makes ε_trig for the EW channel a direct, sensitive probe of how
much hard ISR the generator/matching setup produces — unlike the
colored channel, whose 2→2+1jet QCD production is hard at leading order
regardless of merging-scale choice.

Full generation-config comparison: `tables/generation_matching_configuration_comparison.csv`.
**Direct diff of the original 1000-event and fresh 2000-event run_cards**
(`diff`, excluding only `nevents`/`iseed` lines) found **zero value
differences** — every remaining diff line is pure whitespace/tab
formatting from MadGraph's own card rewriting. xqcut=30 GeV, ickkw=1,
ptj=20 GeV, etaj=5.0, PDF=nn23lo1 (NNPDF2.3LO), dynamical scale,
scalefact=1.0 — **byte-identical** between the two project samples. This
project's own generation is fully self-consistent between its 1000- and
2000-event runs (also confirmed statistically: Fisher's exact test,
p=0.89 for ε_trig, `FULL_STATISTICAL_AUDIT_1000_2000_v1/tables/stability_1000_vs_2000.csv`).

**What the paper does not state, searched directly in the full text**:
zero mentions anywhere of PDF set, MLM/xqcut merging scale, shower tune,
or MadGraph/Pythia8 version numbers. Only stated: "up to 1 jet ... using
MadGraph5 aMC@NLO ... matched using Pythia8" (Sec III A) — no numerical
settings given. **This makes a value-for-value generator-setting
comparison against the paper structurally impossible** — not a gap in
this audit's effort, but a genuine absence in the published paper.

**Post-shower vs pre-shower momenta**: using `status==1` (post-shower)
momenta for the trigger cut is the physically correct choice, not a
proxy-vs-truth discrepancy — the post-shower quirk momenta already
include the recoil effect of any radiated ISR, which is exactly the
physical effect the paper's own cut is designed to be sensitive to
(momentum conservation guarantees the quirk pair recoils against
whatever was radiated). Using pre-shower (parton-level) momenta instead
would have been the actual bug, since a pure 2→2 parton-level pair has
pT_pair≡0 identically, before any radiation is added.

## 7. Fiducial-definition checks

- **Denominator = trigger-passing events only**: confirmed
  (`n_fid = recon_df["truth_fiducial"].sum()` computed over the
  186-row `trigger_passing_events.csv`-derived propagation set, not the
  full 1045-row matched sample).
- **Both quirks must independently intersect all 8 layers — verified
  structurally AND empirically, no false-positive risk found.**
  Code-level proof: `find_layer_crossing()` (`trajectory_to_hits.py`
  line 77) returns **at most one** crossing per (quirk, layer) pair —
  "ONLY THE FIRST outward crossing is retained" (the function's own
  docstring) — and the hit-generation loop (`simulate_quirk_hits`,
  lines 370-372) calls it exactly once per layer per quirk. This
  structurally caps each quirk at ≤8 raw hits, meaning
  `n_hits_premerge==16` (the `geometric_fiducial` check) is
  **mathematically equivalent** to both quirks independently covering
  all 8 layers (8+8) — there is no code path by which an asymmetric
  split (e.g. one quirk hitting 9 layers via a double-crossing, the
  other 7) could sum to 16 and be misclassified as fiducial. Empirically
  confirmed via a 5-event deterministic replay (same stored seeds, no
  new generation): 4/5 events with `n_hits_premerge==16` showed exactly
  8+8 layer coverage; the 1 geometric failure showed 1+3 layers (both
  quirks fell short — the "both-fail" category, not "one-quirk-only");
  zero mismatches between replayed and stored `truth_fiducial` across
  all 5 events. Full detail: `tables/EW2000_fiducial_replay_detail.csv`.
- **25 ns timing cut applied correctly**: `max_hit_t_ns_premerge < 25.0`,
  computed from the pre-merge raw-hit timing (deliberately not from
  merged hits, which inherit an arbitrary cluster member's time — see
  the code's own comment, `trajectory_to_hits.py` lines 428-434). Only
  1 of 186 trigger-passing events fails via timing alone (geometric OK,
  timing fails) — a small, genuine physical effect, not a bug.
- **No endcap acceptance**: confirmed — `LAYERS` contains exactly 8
  barrel-only entries; `FIDUCIAL_ETA_MAX = 1.8` (`atlas_geometry.py`
  line 87) enforced per-hit inside the hit-generation loop, matching
  the paper's "|η| ≲ 1.8" statement exactly.
- **Layer radii/detector dimensions**: not independently re-derived in
  this audit (out of scope — this exact check was performed and
  verified in earlier project phases, `PAPER_REQUIREMENTS.md` row 6;
  not re-litigated here to stay within the audit's stated scope).
- **Propagation stopping conditions, units, particle identities**:
  units consistent (cm for position, ns for time, GeV for momenta);
  particle identity for the fiducial stage is carried through from the
  already-identified trigger-passing quirks (same `event_idx`/`seed`
  chain, no re-identification ambiguity at this stage).

## 8. Fiducial failure categories (item 8)

Full table: `tables/fiducial_failure_categories.csv`. Closure verified
exactly (2+89+1+94=186):

| Category | Count | Note |
|---|---|---|
| Technical exception (known physics-driven integration edge case) | 2 | Pre-existing, documented category (e.g. `ABSOLUTE_MAX_STEPS` ceiling reached for a genuinely slow-converging low-pT oscillatory trajectory — hit during this audit's own spot-check attempt on event 175, confirming this is a real, reproducible, already-classified edge case, not new) |
| Geometric failure (≥1 quirk misses ≥1 layer) | 89 | The dominant failure mode |
| Timing failure (geometric OK, ≥25ns) | 1 | Rare |
| One-quirk-only failure (asymmetric false-accept) | 0 | **Structurally impossible** (§7) — verified, not merely absent by luck |
| Truth-fiducial (pass) | 94 | = N_fiducial |

## 9. 1000-event vs 2000-event comparison (configuration-level, not reconstruction outputs)

Full table: `tables/config_1000_vs_2000_item9.csv`. Every generator
setting is byte-identical (§6); only `N_requested` and `iseed` differ,
by design. The downstream trajectory integrator differs by code version
(`quirk_trajectory_optimized_v2.py` for the 2000-event sample vs the
pre-optimization baseline for the 1000-event sample) but was previously
validated bit-identical in physics output (not re-derived here). This
confirms the two samples are independent draws from the *same*
underlying generator configuration — their ε_trig/ε_fid values (17.42%/
17.80% and 44.94%/50.54%) are statistically compatible with each other
(Fisher exact p=0.89 and p=0.44 respectively,
`FULL_STATISTICAL_AUDIT_1000_2000_v1/tables/stability_1000_vs_2000.csv`)
and both disagree with the paper by a similar factor — consistent with
a single root cause (undocumented paper generator settings) rather than
two different, sample-specific problems.

## 10. Classification of every checked item

Full table: `tables/paper_vs_project_requirements.csv`. Summary:

| Item | Classification |
|---|---|
| Trigger = CM-system pT>200 GeV, strict, post-shower quirk momenta | VERIFIED PAPER REQUIREMENT / VERIFIED PROJECT IMPLEMENTATION |
| Fiducial = both quirks all 8 layers + 25ns, conditional on trigger | VERIFIED PAPER REQUIREMENT / VERIFIED PROJECT IMPLEMENTATION |
| Barrel-only, \|η\|<1.8, no endcaps | VERIFIED PAPER REQUIREMENT / VERIFIED PROJECT IMPLEMENTATION |
| PDF set, xqcut/qCut, scale choice, generator version | PAPER UNDOCUMENTED |
| Beam energy 13 TeV | PROJECT APPROXIMATION (standard, well-motivated, not paper-restated in this section) |
| 25ns cut measured to outermost tracker layer (not literal muon chamber) | PROJECT APPROXIMATION (defensible interpretation of an underspecified cross-reference between Sec III B's motivation and Sec IV's fiducial definition) |
| One-quirk-only false-accept risk | **VERIFIED: not a bug** (structurally impossible, empirically confirmed) |
| Root cause of the 17.8%-vs-10% and 50.5%-vs-28% gaps | **UNRESOLVED — undocumented paper generator settings**, with a specific, testable physical mechanism identified (§6) |

No item in this audit is classified **VERIFIED BUG**.

## 11–12. No tuning performed; no correction applied

Per instruction, no cut or parameter was tuned toward reproducing 10%/
28%. No definite code/configuration bug was found, so per instruction
item 12 ("apply a correction only if a bug is found"), **no correction
is applied and none is needed**. `tables/corrected_efficiencies_if_bug_found.csv`
is produced as required but contains no rows — explicitly documented as
empty-by-finding, not omitted.

## 13–14. Scope compliance

No raw sample, frozen report, Figure 6 checkpoint, or the existing
2000-event directory's own files were modified. The one replay performed
(§7, 5 events) is read-only with respect to all stored data — it writes
only to this audit's own new directory
(`05_coplanarity_analysis/EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/`). No
commit or push was performed.

---

## Final answers (as required)

**Why is 17.80% higher than the paper's 10%?** Because the EW channel's
pT_pair distribution — and therefore its trigger pass rate — is a direct
measure of how much hard ISR the MLM-matched generation produces, and
this quantity is well known to be sensitive to the exact merging-scale
(xqcut/qCut) and PDF/shower-tune choices, none of which the paper
publishes. This project's own settings (xqcut=30 GeV, NNPDF2.3LO,
dynamical scale) are internally consistent and verified bug-free across
two independent generations (1000- and 2000-event, statistically
compatible with each other), but cannot be checked against the paper's
own (unpublished) choice. **Classification: UNRESOLVED — undocumented
paper generator settings** (not a bug, not a project approximation with
a known correction, not yet independently confirmable).

**Why is 50.54% higher than the paper's 28%?** [SUPERSEDED BY
`CAUSAL_KINEMATICS_FOLLOWUP.md` — the paragraph below stated this as a
plausible mechanism, not yet a demonstrated one, when first written.] A
harder ISR/pT_pair spectrum (same undocumented-settings root cause as
ε_trig) was hypothesized to produce more central kinematics after the
trigger cut, mechanically raising 8-layer coverage. The follow-up
document has since tested this directly on existing events: pT_pair
does show a real, statistically significant, η-independent positive
association with fiducial pass (point-biserial r=0.23, p=0.0016;
unmediated by η-centrality, confirmed via partial correlation). η-
centrality itself is the numerically dominant driver (r≈−0.47). **Revised
classification: the root cause (why this project's ISR spectrum differs
from the paper's) remains UNRESOLVED — undocumented paper generator
settings; but the specific claim that harder-ISR-induced kinematics
contribute to the higher fiducial efficiency is now DEMONSTRATED, not
merely hypothesized**, on this project's own existing data.

**Bug, approximation, undocumented setting, or unresolved — per item:**
see the table in §10. No bug was found in either the trigger or fiducial
computation, cut definitions, denominators, or event bookkeeping. The
one genuinely provable defensive concern raised (one-quirk-only
false-accept) was checked exhaustively and is confirmed not to occur.
The remaining gap is attributed to undocumented MC generation settings,
consistent with — and now further evidenced beyond — the prior
2026-09-21 audit's conclusion.

**Corrected values**: none — no demonstrated bug exists to correct.
The values already reported (186/1045 = 17.80% [Wilson 95%:
15.60%,20.24%]; 94/186 = 50.54% [Wilson 95%: 43.42%,57.64%]) stand as
independently re-verified, bug-free measurements of this project's own
pipeline, still in tension with the paper for reasons that remain
outside this project's ability to independently resolve without the
paper's own generator cards.
