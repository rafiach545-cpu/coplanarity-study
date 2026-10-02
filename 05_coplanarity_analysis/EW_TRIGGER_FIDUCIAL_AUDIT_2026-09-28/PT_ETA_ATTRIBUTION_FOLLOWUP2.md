# Follow-up 2: Does pT Actually Explain the Fiducial Gap? Zero-Hit Investigation

**Read-only, existing events only.** No new simulation launched this
round (per explicit instruction) — where a question genuinely requires
replaying trajectories (per-quirk radial reach, integration exit status,
propagation time), this is stated honestly as **UNAVAILABLE without
replay**, not inferred or guessed. No frozen file modified, no
commit/push.

## Headline answer (stated up front, per instruction)

1. **The ISR/pT_pair effect is demonstrated, but it does NOT
   quantitatively explain the 50.54% vs 28% gap.** Even the lowest
   pT_pair bin (200,300] GeV — the slice closest to the trigger
   threshold, least affected by hard ISR — still gives **34/83 = 41.0%**
   fiducial efficiency, Wilson 95% [31.0%, 51.7%], which is **still
   statistically significantly above the paper's 28%** (exact binomial
   p=0.0138). pT_pair explains part of the internal *trend* across bins,
   not the overall *offset* from the paper.
2. **77% of fiducial failures having zero hits is explained only
   partially by truth-level η.** 56% of zero-hit events have truth
   max\|η\|>1.6 (consistent with "physically forward, likely outside
   barrel acceptance"). The remaining 44% have moderate truth η
   (≤1.6) **and high momentum** (median pT≈800-900 GeV, β_min≈0.79) —
   the opposite kinematic signature of a "low-momentum trajectory that
   never reaches layer 1." This subset's cause **cannot be determined
   from existing stored data** — it requires replaying the actual bent
   trajectory (truth η is only the momentum direction at the origin,
   not the trajectory's direction at the point where it crosses each
   layer's radius, and quirks are expected to have oscillatory,
   non-straight-line trajectories by design).
3. **Verdict: kept UNRESOLVED**, per instruction — no single cause
   quantitatively explains the full paper-project difference.

---

## 1. Exact counts, Wilson 95% intervals, every pT_pair bin

Full table: `tables/pt_bin_exact_counts_wilson.csv`.

| Bin (GeV) | n | k (fiducial) | efficiency | Wilson 95% | p vs paper (0.28) |
|---|---|---|---|---|---|
| (200,300] | 83 | 34 | 41.0% | [31.0%, 51.7%] | **0.0138** |
| (300,400] | 34 | 16 | 47.1% | [31.5%, 63.3%] | 0.0202 |
| (400,600] | 42 | 23 | 54.8% | [39.9%, 68.8%] | 0.00039 |
| (600,900] | 22 | 17 | 77.3% | [56.6%, 89.9%] | 2.3e-6 |
| (900,1400] | 5 | 4 | 80.0% | [37.6%, 96.4%] | 0.024 |

**Every single bin, including the lowest, is individually statistically
inconsistent with the paper's 28%.** There is no pT_pair slice in this
project's existing sample that reproduces the paper's value.

## 2. Quantifying the attributable fraction (not inferring full explanation from correlation)

The correct test is not "is there a trend" (already shown, follow-up 1)
but "does the trend's low end reach the paper's value" — it does not
(§1, item 1 above). A regression-based decomposition: fitting
`truth_fiducial ~ quirk_pair_pt_gev` and evaluating at the sample's
minimum observed pT_pair (205.4 GeV) gives a predicted efficiency around
the observed lowest-bin rate (~41%), not 28% — confirming the trend,
even extrapolated to its most favorable end within the observed pT
range, does not reach the paper's value. **Conclusion: pT_pair
dependence explains at most part of the *spread* across this project's
own events; it does not explain the *overall offset* relative to the
paper.** The dominant remaining lever is rapidity/η-shape (§3), and
ultimately the undocumented generator settings that shape it (§7-8).

## 3. Fiducial efficiency in additional kinematic bins

Full table: `tables/fiducial_efficiency_binned_v2.csv`. Pair rapidity is
the most striking:

| \|Y_pair\| bin | n | k | efficiency |
|---|---|---|---|
| (0, 0.3] | 69 | 64 | **92.8%** |
| (0.3, 0.6] | 54 | 24 | 44.4% |
| (0.6, 0.9] | 38 | 6 | 15.8% |
| (0.9, 1.2] | 23 | 0 | **0.0%** |
| (1.2, 1.6] | 2 | 0 | 0.0% |

This is a near step-function — far sharper than the pT_pair trend (§1)
or even the per-quirk η trend. **Pair rapidity (equivalently, how
central the DY system is) is the single strongest kinematic predictor
of fiducial acceptance found in this analysis.** This is directly
relevant to the root-cause question (§7): DY rapidity spectra are
well known in QCD phenomenology to be sensitive to PDF choice
specifically (not only merging scale/ISR hardness) — refining, not
replacing, the earlier ISR-only framing.

## 4–5. Zero-hit event investigation

Full per-event table: `tables/zero_hit_events_detail.csv` (71 events,
event ID, both quirks' full 4-momenta, η, pT — all from existing stored
truth-level data, no replay).

**What IS available without replay, reported exactly:**
- Event ID, quirk 4-momenta, η1/η2, pT1/pT2 — all retrieved directly.
- Since `n_hits_premerge==0` requires the *sum* of both quirks' hits to
  be zero, and each quirk's hit count is non-negative, **both quirks
  necessarily have zero hits each** for all 71 events (this specific
  sub-question IS answerable from existing data, no replay needed).

**What is NOT available without replay (stated honestly, not guessed):**
maximum radial distance reached, integration exit/status, propagation
time. These require re-running the trajectory integrator on each event,
which this round's instruction excludes. **Not fabricated or inferred
from proxies presented as fact.**

**Kinematic split, existing-data only** (`tables/zero_hit_events_detail.csv`):

| Subset | n | median max\|η\| | median pT (either quirk) | median β_min | Interpretation |
|---|---|---|---|---|---|
| Zero-hit, forward (max\|η\|>1.6) | 40 (56%) | >1.6 | ~293 GeV | 0.624 | Consistent with "physically outside barrel η acceptance" — the paper's own barrel-only geometry would plausibly exclude these regardless of generator settings |
| Zero-hit, central (max\|η\|≤1.6) | 31 (44%) | ≤1.6 (min 0.58) | ~800-900 GeV, **high** | 0.786-0.91, **high** | **Cannot be classified from existing data.** High momentum/β rules out "too slow to reach layer 1" as the naive explanation. Truth η (momentum direction at production) is not the same quantity as the trajectory's direction at the actual layer-crossing point for an oscillating, string-tied quirk pair — replay is required to determine whether these trajectories genuinely miss the barrel geometrically (bent outside |η|<1.8 at the crossing radius despite a central production angle) or encounter something else. **Flagged as a genuine open question, not resolved here.** |
| Non-zero-hit ("rest") | 115 | ~1.0-1.1 | ~480-500 GeV | 0.52 | Reference population |

## 5 (continued). Requested 5-way categorization — honestly partial

Per instruction, zero-hit events should separate into: physically
outside barrel acceptance / timing failure / trajectory turns before
layer 1 / numerical failure / unidentified. **Timing failure is
structurally excluded for zero-hit events** — the fiducial timing check
only evaluates `max_hit_t_ns_premerge` over existing hits, so an event
with zero hits cannot be classified as a timing failure by construction
(this is a code-structure fact, not new evidence, verified from
`trajectory_to_hits.py`'s `traj["max_hit_t_ns_premerge"] = (max(...) if
raw_hits else float("nan"))` — zero hits gives NaN, and NaN correctly
excludes from a timing-pass classification but doesn't itself indicate
"timing failure" vs another cause). Given the constraint against new
simulation this round, this audit can only confidently place:
- **~56% (40/71) as plausibly "physically outside barrel acceptance"**
  (forward truth η, consistent picture, not proven without replay of
  the actual crossing-point geometry).
- **~44% (31/71) as unidentified** pending replay — explicitly not
  forced into "trajectory turns before layer 1" or "numerical failure"
  without evidence, since the momentum/β data available argues against
  the "too slow" explanation and there is no stored integration-exit
  information to support or rule out a numerical-failure explanation.

## 6. Detector geometry verification against the paper

Directly re-checked (`atlas_geometry.py`): 8 barrel layers at radii
3.325, 5.05, 8.85, 12.25 cm (pixel: IBL, B0, B1, B2) and 29.9, 37.1,
44.3, 51.4 cm (SCT: B3-B6) — these are the standard public ATLAS Run-2
barrel radii (matching ref [27], previously verified in this project's
`PAPER_REQUIREMENTS.md` row 6, re-confirmed here). `FIDUCIAL_ETA_MAX =
1.8` matches the paper's "\|η\| ≲ 1.8" statement exactly.
`BEAMSPOT_SIGMA_Z_CM = 4.5` cm = 45 mm matches the paper's stated
"gaussian smearing with width 45 mm" exactly. **No discrepancy found —
detector geometry matches the paper as closely as the paper's own text
specifies.**

## 7. Which single cause best explains the higher fiducial efficiency?

Ranked by evidence strength, all from this audit's own quantitative
tests:
1. **Pair rapidity / η-centrality** — by far the strongest, sharpest
   predictor (§3: 92.8%→0% across 5 bins). This is a real, demonstrated,
   dominant driver of the *shape* of fiducial efficiency across this
   project's own sample.
2. **Harder pT_pair (ISR)** — demonstrated (follow-up 1) but weaker
   (r≈0.23) and explicitly shown (§1-2, this document) to be
   insufficient to explain the overall offset by itself.
3. **Detector geometry** — verified matching the paper; ruled out as a
   contributor to the discrepancy.
4. **Propagation/numerical treatment** — genuinely unresolved for ~44%
   of zero-hit events (§4-5); cannot be ruled in or out without replay.
5. **Unpublished paper generation settings** — remains the necessary
   upstream explanation for *why* this project's own rapidity/η/pT
   distribution shape differs from whatever the paper's (undisclosed)
   generator produced. Items 1-2 are real, demonstrated *mechanisms*
   internal to this project's sample; they do not, by themselves,
   explain why the paper's sample apparently has a different rapidity
   distribution — that traces back to PDF/scale/merging choices the
   paper never states.

**No single cause quantitatively explains the full paper-project
difference.** Rapidity-shape is the strongest internal driver found;
undocumented generator settings remain the necessary root explanation
for why that shape differs from the paper's.

## 8. Verdict

**UNRESOLVED**, per instruction (no single cause quantitatively closes
the 50.54%-vs-28% gap). This is a refinement, not a reversal, of the
prior two reports: the ISR/pT effect is real but insufficient; rapidity/
η-centrality is now identified as the dominant internal driver but its
origin (why this project's η/rapidity distribution differs from the
paper's) remains attributable only to undocumented generator settings,
which cannot be tested without the paper's own cards.

---

## Required final statements

- **Is the ISR effect demonstrated but insufficient to quantitatively
  explain the gap?** Yes — demonstrated (follow-up 1), and now shown
  quantitatively insufficient (§1-2 above): even the lowest pT_pair bin
  remains statistically significantly above the paper's value.
- **Why do 77% of failures have zero hits?** Partially explained:
  56% of zero-hit events have high truth-level \|η\| (>1.6), consistent
  with genuinely exiting the barrel's angular acceptance. The remaining
  44% have moderate truth η but high momentum — an unexpected
  combination that is **not explained by any hypothesis testable from
  existing stored data.**
- **Are the zero-hit events physical acceptance losses or numerical
  propagation failures?** **Both categories likely present, in
  proportions that cannot be determined without replay.** ~56% are
  plausibly physical (forward-η) acceptance losses; the remaining ~44%
  are unidentified — genuinely could be either a physical effect
  (oscillatory trajectory bending outside acceptance despite central
  production angle) or something in the numerical propagation, and this
  audit does not guess which.
- **Strongest remaining explanation for 50.54% vs 28%?** Rapidity/η-
  centrality shape is the strongest *internal* driver identified; its
  ultimate cause is attributed to **undocumented paper generation
  settings** (PDF/scale/merging choices shaping the DY rapidity
  spectrum), consistent with — and now more specific than — the original
  report's conclusion. The verdict remains **UNRESOLVED**.
