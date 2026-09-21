# EW trigger/fiducial discrepancy audit (v1) — 2026-09-21

## The discrepancy

| Quantity | Paper (EW, DY 800GeV) | Project (EW, 800GeV/4keV) | Ratio |
|---|---|---|---|
| ε_trig | 0.10 | 0.174 (89/511) | 1.74× |
| ε_fid | 0.28 | 0.449 (40/89) | 1.60× |
| ε_reco | 0.72 | 0.800 (32/40) | 1.11× (within Wilson 95% CI, CONSISTENT) |

For comparison, the colored benchmark shows much closer agreement:

| Quantity | Paper (colored, QCD 1800GeV) | Project | Ratio |
|---|---|---|---|
| ε_trig | 0.24 | 0.216 (27/125) | 0.90× (CONSISTENT within Wilson 95% CI) |
| ε_fid | 0.28 | 0.259 (7/27) | 0.93× (CONSISTENT within Wilson 95% CI) |

Only EW ε_trig and ε_fid show real tension; EW ε_reco and both colored
quantities are statistically consistent with the paper.

## Definitions verified against the paper (direct text extraction, this task)

Paper page 4 (Sec. III B, "Trigger"), verified verbatim: *"...we therefore
impose a pT > 200 GeV cut on the center of mass momentum of the
quirk/anti-quirk system."* — **this is exactly the project's own trigger
cut** (`pT_pair = hypot(px1+px2, py1+py2) > 200`, computed from the truth
4-momenta in `01_signal_generation/extract_ew_quirk_momenta.py:102`, applied
in `analyze_ew_quirk.py:218`). The project's own documentation elsewhere
calls this a "trigger proxy," which UNDERSELLS it — it is the paper's
literal, exact criterion, not an approximation. This mislabeling is
corrected in this task's final report/sourcebook (Phase 10/11).

Paper page 7 (Sec. IV, immediately after Eq. 12), verified verbatim: *"The
fiducial efficiency parametrizes the likelihood that each quirk intersect
with each layer at least once, in events passing the trigger. We also
include a 25 ns timing cut..."* — matches the project's fiducial
definition exactly (`analyze_ew_quirk.py`: `N_truth_fiducial` = both quirks
cross all 8 layers within |η|<1.8 AND last crossing <25ns, evaluated only
on the trigger-passing subset — i.e. ε_fid = N_truth_fiducial / N_trigger,
conditional on trigger, exactly as the paper states).

## Code-level checks performed (no bug found)

1. **Denominators**: `ε_trig = N_trigger/N_matched`, `ε_fid =
   N_truth_fiducial/N_trigger` — both match the paper's own Eq.12
   factorization and the "in events passing the trigger" conditioning
   exactly. Verified directly in `analyze_ew_quirk.py:283-284`.
2. **pT_pair construction**: `np.hypot(px1+px2, py1+py2)` — the vector
   sum of both quirks' transverse momenta, i.e. the CM system's pT
   (equivalently, the ISR recoil magnitude by momentum conservation).
   Matches the paper's "center of mass momentum of the quirk/anti-quirk
   system" exactly. Verified in `extract_ew_quirk_momenta.py:102`.
3. **No generation-level bias**: `docs/CUTS_AND_PIPELINE.md` line 45
   confirms "none of the paper's kinematic cuts (pT_CM>200 GeV etc.)
   apply at the matrix-element level" — the 511 matched events are an
   unbiased sample with respect to the trigger cut; ε_trig is not
   artificially inflated or deflated by a generation-time pre-filter.
4. **No charge-sign bug** (previously found and fixed in this benchmark,
   unrelated to this discrepancy, documented in `analyze_ew_quirk.py`'s
   own header comment) — re-verified this was already corrected and does
   not affect pT_pair or the fiducial hit-count logic (charge only
   affects the Lorentz-force bending direction inside the detector
   simulation, which runs AFTER the trigger cut and does not feed back
   into `pT_pair`).
5. **Event-level audit table**: built directly from stored data (no
   rerun) — `EW_event_level_audit_table_v1.csv`, 511 rows, each with
   `pT_pair`, `trigger_pass`, `trigger_reason`, and (for the 89
   trigger-passing events) `fiducial_status`. Confirms 89/511 trigger,
   40/89 fiducial, matching the cutflow CSV exactly — no double-counting,
   no off-by-one, no denominator drift.

## Root-cause investigation: what the paper does NOT specify

Direct text search of the full paper (this task) found **zero** mentions
of: PDF set, MLM/MadGraph merging (`xqcut`) scale, or Pythia8 shower tune.
The paper's only generation-method statement (Sec. III A) is: *"We
generate signal samples of vector-like fermions with up to 1 jet using
MadGraph5_aMC@NLO [24,25], which is subsequently matched using Pythia8
[21,26]."* No numerical settings are given for either DY or QCD
production. This project's own generation scripts do not preserve a
MadGraph run_card/banner (confirmed: no `.dat`/run_card/banner files
exist anywhere in the repository) — the exact settings used for this
project's own EW sample generation are themselves not independently
recoverable from stored files, only the output momenta CSV is preserved.

**This means an exact apples-to-apples generator-setting comparison is
structurally impossible from either side** — neither the paper's nor
(fully) this project's own generation parameters are available to diff
against each other.

## Physical explanation for why EW is affected but colored is not

Drell-Yan (EW) production's transverse-momentum spectrum — the pT of the
recoiling qq̄→Z*/γ*-like system, which IS the "ISR recoil" that the
pT_pair trigger cut is sensitive to — is a well-known example in QCD
phenomenology of an observable that is **highly sensitive to the
MLM/CKKW merging scale and shower-matching prescription** chosen (this is
a standard, well-documented feature of Drell-Yan pT resummation/merging
studies, not specific to this project). By contrast, QCD pair production
(the colored benchmark) is dominated by genuinely hard 2→2+1jet
matrix-element radiation already at leading order, making its pT_pair
spectrum shape comparatively insensitive to the precise merging-scale
choice.

This gives a coherent, physically-motivated explanation for the observed
pattern: **colored ε_trig/ε_fid agree with the paper (QCD radiation
spectrum is merging-scale-robust); EW ε_trig/ε_fid do not (DY recoil
spectrum is merging-scale-sensitive, and the paper does not specify the
scale it used).** A harder ISR/pT_pair spectrum in this project's EW
sample relative to the paper's (from an unknown, undocumented difference
in merging scale, PDF set, or shower tune) would directly explain BOTH
the higher ε_trig (more events clear the 200 GeV cut) AND the higher
ε_fid (events that clear a harder pT_pair cut tend to have more central
kinematics, all else equal, so a higher fraction also achieve full
8-layer coverage) — a single root cause explaining both observed
tensions simultaneously.

## Verdict

**NO BUG FOUND.** All cut definitions, denominators, and computations were
independently verified to be correct and to match the paper's stated
definitions exactly (word-for-word extraction from the source PDF, this
task). The discrepancy is retained as an **UNRESOLVED MODELING
DIFFERENCE**, attributed to undocumented MC generation settings (PDF set,
merging/matching scale, shower tune) that the paper itself does not
specify and that were not independently preserved in this project's own
generation records — compounded by the well-known sensitivity of
Drell-Yan pT spectra specifically to those choices, consistent with the
observation that the QCD-dominated colored benchmark shows no such tension.

No project implementation was changed as a result of this audit, per the
task's explicit instruction ("do not change the project implementation
unless a direct mismatch or bug is proven").

## Files
- `EW_event_level_audit_table_v1.csv` — 511-row per-event audit (pT_pair,
  trigger pass/reason, fiducial status for trigger-passing events)
- `EW_trigger_fiducial_discrepancy_audit_v1.md` — this document
