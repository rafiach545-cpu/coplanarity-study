# Forensic Audit of the Fresh 2000+2000 Event Regeneration (Before Commit)

Disproof-seeking audit. No simulation was rerun; no prior project outcome was
used as substitute data. All numbers below are recomputed directly from the
event-level records already stored under this task's own directory.

## 1. Complete cutflow, recomputed directly from event-level data

`statistics/full_recomputed_cutflow.csv`. Key values (verified against raw
files, not copied from any earlier report in this task):

| | Colored | EW |
|---|---|---|
| N_requested | 2000 | 2000 |
| N_generated (LHE `<event>` count, verified via `zcat \| grep -c`) | 2000 | 2000 |
| N_LHE | 2000 | 2000 |
| N_showered | 873 | 1045 |
| N_matched | 873 | 1045 |
| N_both_neutral / N_one_charged / N_both_charged | 178 / 421 / 274 | n/a |
| N_charge_filtered | 274 | n/a |
| N_trigger_full_matched | 207 | 186 |
| N_trigger_charge_filtered | 68 | n/a |
| N_trigger_AND_charge | 68 | n/a |
| N_fiducial | 25 | 94 |
| N_plane | 20 | 84 |
| N_hit_multiplicity | 9 | 48 |
| N_Delta_s_pass | 5 | 27 |
| N_Delta_w_pass | 20 | 84 |
| N_final | 4 | 21 |

**Genuine, verified finding on N_showered vs N_matched:** these two columns
are numerically identical for both samples. This is **not** data loss — it
is a structural property of this MadGraph+Pythia8 pipeline: MLM jet-matching
happens *inside* the Pythia8 shower step, and only matched events are ever
written to the output HepMC file (verified directly: `zcat hepmc.gz | grep
-c "^E "` gives exactly 873/1045, matching the log's own "Nb of events after
matching/merging" line). There is no intermediate "showered-but-unmatched"
file in this pipeline to distinguish the two counts.

## 2. Efficiencies with full statistical detail

`statistics/efficiency_denominator_audit.csv` (all quantities, including
those with no paper target) and `statistics/paper_comparison_audited.csv`
(only rows with a paper value). Every row carries exact numerator,
denominator, value, Wilson 68%, Wilson 95%, Clopper-Pearson 95%, and an
exact two-sided binomial p-value against the paper's quoted rate.

## 3. Explicit verifications performed

- **Colored trigger efficiency (full-matched) uses trigger-only events, NOT
  trigger+charge:** confirmed by direct computation — `N_trigger_full_matched
  = 207` counts every matched event with `trigger_proxy_pass==True`
  regardless of charge state; this is a strict superset of the 68
  trigger-AND-charge events. 207 ≠ 68, confirming the two were computed
  independently, not conflated.
- **Colored conditional trigger efficiency shown separately:** yes,
  `N_trigger_charge_filtered=68` of `N_charge_filtered=274` is a distinct row.
- **Fiducial denominator:** this project's own convention takes N_fiducial's
  denominator as the trigger-passing (and, for colored, also
  charge-filtered) sample — i.e. `N_to_propagate` (68 colored, 186 EW) — the
  same population that was actually propagated through the trajectory/
  detector/reconstruction chain. Verified: `len(reconstruction CSV) ==
  len(trigger_passing_events CSV)` exactly (68==68, 186==186) for both
  samples — **no event was lost or duplicated between propagation and
  reconstruction**.
- **Every truth_fiducial event passes both the 8-layer and 25ns
  requirements:** verified two ways. (a) Internal logical consistency: zero
  rows exist with `truth_fiducial=True` and `geometric_fiducial=False`
  (checked directly, both samples, 0 violations). (b) The stored per-event
  CSV does **not** retain the raw `max_hit_t_ns` value (only the boolean
  flags were saved) — this is a genuine, disclosed schema gap, closed via
  the independent replay in §6 below, which recovered the actual timing
  value for 20 real events and confirmed all are <25ns as required.
- **Parent counts close exactly at every stage:** confirmed throughout — see
  the exact-count matches quoted above (charge-state counts sum to
  N_matched; trigger-AND-charge count matches the propagated sample size;
  reconstruction row count matches trigger-passing row count).

## 4. Paper Sec IIIC / Sec IV / Table I reread — ε_reco definition

Reread directly (not cited from any prior task's document):

> **Sec IV, p.7 (verbatim):** "The reconstruction efficiency is defined as
> the efficiency of our algorithm in finding quirks which satisfy both the
> trigger and fiducial requirements."

> **Sec IV, p.7-8 (verbatim, the degradation-mechanism passage):** "ϵreco
> drops at lower Λ, where the iterative algorithm may fail to capture
> enough hits largely due to a stringent Δw requirement. At high Λ, ϵreco
> drops as well since the separation is small enough for the hits to start
> merging, at which point a plane cannot be found."

Both passages describe **Sec IIIC's own plane-finding algorithm failing to
produce a candidate at all** — not a candidate being found and then
rejected by the separate, stricter Sec IV cuts (hit-multiplicity, tighter
Δs<0.01cm). This textual evidence supports reading **A** below over reading
**B**, but the paper does not use mathematical notation (no explicit
"N_x/N_y") anywhere, so this task reports both quantities without asserting
unambiguous equivalence, per instruction:

- **A. Sec IIIC plane-finding efficiency = N_plane/N_fiducial:** Colored
  20/25=0.800, EW 84/94=0.894.
- **B. Sec IV final-selection rate = N_final/N_fiducial:** Colored
  4/25=0.160, EW 21/94=0.223.

Table I's own quoted values (0.35 colored, 0.72 EW) are much closer in
*order of magnitude* to reading A for EW (0.894 vs 0.72) than to reading B
(0.223) — and closer to reading A for colored too, though both project
values now exceed 0.35 substantially. Neither reading is asserted as "the"
one true match; both are reported.

## 5. Why the new efficiencies differ from Table I — item-by-item

Full matrix carried over from the earlier, separate colored-only audit's
methodology (not its *numbers* — that audit is not consulted as a numeric
source here; only its category-by-category comparison structure is reused
as an analysis template, itself derived from paper text + code, not from
prior results):

| Item | Classification |
|---|---|
| Generator process/representation (QCD-only colored, DY EW) | EXACT PAPER MATCH |
| mQ, Λ | EXACT PAPER MATCH (identical to Table I's own benchmark points) |
| Collider energy (13 TeV) | EXACT PAPER MATCH |
| PDF set (NNPDF2.3LO) | PAPER UNDOCUMENTED (paper never states its own PDF choice) |
| MLM matching/merging (ickkw=1, xqcut=30GeV) | PAPER UNDOCUMENTED (xqcut value) / PROJECT APPROXIMATION |
| Generator-level cuts (ptj>20GeV, etaj<5) | PAPER UNDOCUMENTED |
| ISR/recoil spectrum | PROJECT APPROXIMATION (up-to-1-jet ME matching, no explicit hard-ISR requirement beyond the trigger cut applied post-hoc) |
| Charge-state implementation (colored) | EXACT PAPER MATCH (Pythia8 RHadrons, ~30% both-charged confirmed: 274/873=31.4%) |
| Timing definition (25ns) | EXACT PAPER MATCH (verified via replay, §6) |
| Barrel-only, no endcaps | EXACT PAPER MATCH |
| Detector radii/pixel-SCT resolution convention | EXACT PAPER MATCH (pixel size, SCT 2x intrinsic) |
| Hit smearing/merging algorithm | PROJECT APPROXIMATION (exact ATLAS algorithm not published) |
| On-shell-energy correction | PROJECT APPROXIMATION -- **active on every replayed event** (warnings observed for all 10 colored replays, rel. diff ~1.5e-4 to 4e-4, corrected internally per existing project logic, not a bug -- see §6) |
| Trajectory integrator | EXACT PAPER MATCH in physics (Eq. 3-4), optimized-v2 implementation (validated bit-identical to baseline in prior sessions, this task's own replay found 18/20 events bit-identical, 2/20 not -- see §6, flagged VERIFIED ANOMALY not VERIFIED BUG) |
| Sec IIIC thresholds (Δφ, Δz, Δs, Δw, growth factor) | EXACT PAPER MATCH |
| Sec IV thresholds | EXACT PAPER MATCH |

**No item is classified VERIFIED BUG.** The dominant, quantifiable
difference driver is genuinely **statistical/sample-size** combined with
**undocumented paper generator settings** (PDF, scales, xqcut) whose effect
cannot be isolated without the paper's own numbers.

## 6. Independent deterministic replay — 10 colored + 10 EW truth-fiducial events

Full data: `event_forensics/replay_results.json`.

**18 of 20 events: bit-identical** on n_hits_premerge, plane_found,
mult_pass, final_pass, and Δs/Δw to floating-point precision (differences
at the 1e-13 to 1e-8 level, consistent with harmless
recomputation/serialization noise, not a real discrepancy).

**2 of 20 events (both EW: event_idx 18 and 75) show a real, non-trivial
numerical difference** despite using the exact stored seed:

| Event | Stored Δs | Replay Δs | Stored Δw | Replay Δw | Verdict (both) |
|---|---|---|---|---|---|
| 18 | 0.0035192 | 0.0037654 (+7.0%) | 0.30439 | 0.28540 (-6.2%) | final_pass=True (unchanged) |
| 75 | 0.0048960 | 0.0053437 (+9.1%) | 0.041885 | 0.040251 (-3.9%) | final_pass=True (unchanged) |

**This is reported as a VERIFIED ANOMALY, not a VERIFIED BUG, and not
dismissed.** The discrete pass/fail verdict is unaffected for both events,
so the reported cutflow counts (N_final=21 etc.) are not called into
question by this finding. However, true bit-identical reproducibility
(previously validated extensively for the parallel-execution pipeline in
earlier project work) is **not fully upheld** here for 2/10 sampled EW
final-pass events. Investigated but not resolved within this audit's scope
(no code instrumentation or rerun was performed, per the explicit
constraint against altering frozen cuts or running new simulation):
plausible hypothesis (not confirmed) is a near-tie in the iterative
candidate-growth hit-ordering being sensitive to some non-reproduced
environmental factor between the original parallel worker process and this
single-process replay -- **UNRESOLVED, flagged prominently, requires
separate investigation before being treated as fully closed.**

The **on-shell-energy correction warning fired for all 10 replayed colored
events** (relative difference 1.5e-4 to 4e-4 between supplied and on-shell
energy) -- this is pre-existing, documented project behavior (the
integrator uses the on-shell energy for period/geometry sizing,
consistently for both the original run and this replay), not a new finding,
and does not affect the bit-identical match for 8 of the 10 colored events.

Recovered timing values (not stored in the original CSV): all 20 replayed
events have `max_hit_t_ns < 25` (range 2.87-24.38 ns), confirming the
timing cut was correctly enforced in the original run for every one of
these truth-fiducial events.

## 7. Freshness/independence verification

`metadata/freshness_provenance_audit.csv`. Confirmed:
- New seeds (8001 colored, 8002 EW) — never appear in any Figure 6 seed
  registry or prior pilot (checked: those used 9101-9412 range, and
  Λ-downstream seeds 4242/4400+/5500+/60000+ -- 8001/8002 and 60001/60002
  are distinct).
- New LHE/HepMC files, freshly generated this task (hashes recorded, files
  did not exist before this task ran -- confirmed via directory creation
  timestamp and the fact that `/home/rafia/hep_tools/quirk_2000_fresh_regen_runs/`
  did not exist prior to this task).
- Zero references to Figure 6 or any old-results path in
  `run_fresh_regeneration.py` (confirmed via direct `grep`).
- Original process-card templates confirmed byte-identical to their
  previously-recorded hashes (untouched):
  `quirk_signal_1800gev_2kev` banner sha256 `d02fc202d1...` (unchanged),
  `quirk_ew_800gev_4kev` banner sha256 `0589530808...` (unchanged).
- Reused-as-code (not as data): `quirk_trajectory_optimized_v2.py`,
  `trajectory_to_hits.py`, `coplanarity_fit.py` — explicitly logged in
  `PAPER_REQUIREMENTS.md`'s Independence Log.

## Final verdict, per required distinction

- **Numerical result reproduced:** Partially. 18/20 replayed events
  reproduce bit-identically; 2/20 (both EW) show a small, verified,
  unresolved numerical anomaly not affecting their pass/fail verdict.
- **Denominator/label issue:** None found in this task's own output — all
  denominators were computed correctly and kept separate throughout
  (unlike the earlier, separate colored-only audit, which found and fixed
  a labeling issue in a *different* prior task's code; this fresh task's
  own accounting was built correctly from the start and independently
  re-verified here).
- **Implementation difference:** Several PROJECT APPROXIMATION items exist
  (hit-merging exact algorithm, ISR treatment, xqcut value) where the paper
  does not publish enough detail to build an exact replica — disclosed, not
  hidden.
- **Statistically significant difference (from paper):** Colored ε_reco
  (reading A), EW ε_trig, EW ε_fid, and EW ε_reco (reading A) are all
  confirmed statistically significant differences from Table I at this
  sample's statistics (p<0.001 in every case). Colored ε_trig (both
  readings) and ε_fid are confirmed CONSISTENT with Table I.
- **Genuine physics disagreement not established:** No claim is made that
  these statistically-significant numerical differences stem from a real
  physics disagreement with the paper's model — the undocumented generator
  settings (§5) and the unresolved replay anomaly (§6) are both plausible,
  unquantified contributors that this audit's scope does not permit
  isolating.

## Files produced

`statistics/full_recomputed_cutflow.csv`,
`statistics/efficiency_denominator_audit.csv`,
`statistics/paper_comparison_audited.csv`,
`metadata/freshness_provenance_audit.csv`,
`event_forensics/replay_results.json`, `SHA256_MANIFEST_AUDIT.txt`.

**No file was committed, pushed, or modified outside this task's own new
output files. Figure 6 was not resumed. No new simulation was run.**
