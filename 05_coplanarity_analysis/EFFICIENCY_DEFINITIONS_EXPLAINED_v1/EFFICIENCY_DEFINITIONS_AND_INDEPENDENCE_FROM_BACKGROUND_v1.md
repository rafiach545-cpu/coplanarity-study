# Efficiency Definitions, Statistical Uncertainty, and Independence from the Converted-Photon Background Audit

Prepared in response to advisor feedback requesting: (1) explicit
confirmation of whether the `CROSS_SECTION_AUDIT_v1` background
investigation affects the signal efficiency numbers; (2) full,
self-contained definitions of every efficiency quantity with numerator,
denominator, and statistical uncertainty; (3) explicit justification for
why these numbers are comparable to the paper's Table I.

## 1. Does the converted-photon cross-section audit affect any signal efficiency number?

**No.** These are two structurally independent pipelines that never share
an input or an output:

| | Signal (this document) | Converted-photon background (`CROSS_SECTION_AUDIT_v1`) |
|---|---|---|
| Physics process | p p → quirk quirk̄ (colored: QCD-only; EW: Drell-Yan) | p p → Z(→νν) γ j |
| MadGraph directory | `quirk_signal_1800gev_2kev/`, `quirk_ew_800gev_4kev/` (separate) | `zgamma_background_test/` (separate) |
| Downstream code | `quirk_trajectory_optimized_v2.py`, `coplanarity_fit.py` | `extract_zgamma_photons.py`, background overlay scripts |
| Output used for | ε_trig, ε_fid, ε_reco (this document) | An estimated background *rate* (pb → fb) for the Fig. 5-style background-shape comparison |

No background event is ever eligible to be counted in the numerator or
denominator of ε_trig, ε_fid, or ε_reco (see §2) — these are defined and
computed exclusively from quirk-pair events. The cross-section audit's
findings (about the Z+γ+j generator setup) therefore cannot and do not
change any number in this document.

## 2. Exact definitions

Paper's own definition, quoted directly (arXiv:1708.02243v2, Sec. IV,
p.7, Eq. 12):

> "We factorize the total signal efficiency into the trigger efficiency
> (ε_trig), the fiducial efficiency (ε_fid) and the reconstruction
> efficiency (ε_reco) such that the total efficiency ε is given by
> ε = ε_trig × ε_fid × ε_reco."
>
> "The fiducial efficiency parametrizes the likelihood that each quirk
> intersect with each layer at least once, in events passing the
> trigger... We also include a 25 ns timing cut."
>
> "The reconstruction efficiency is defined as the efficiency of our
> algorithm in finding quirks which satisfy both the trigger and
> fiducial requirements."

| Quantity | Meaning | Numerator | Denominator |
|---|---|---|---|
| ε_trig | Fraction of generated/matched quirk-pair events passing the trigger (pT of the quirk-pair center-of-mass system > 200 GeV) | N(pT_pair > 200 GeV) | N(all matched signal events) |
| ε_fid | Given a triggered event, fraction where both quirks hit all 8 barrel tracker layers and arrive within 25 ns | N(both quirks hit all 8 layers, t < 25 ns) | N(trigger-passing events) |
| ε_reco | Given a fiducial event, fraction where the Sec. III C plane-finding algorithm successfully reconstructs a coplanar hit-plane | N(plane found) | N(trigger- and fiducial-passing events) |

Each stage's denominator is exactly the previous stage's numerator — a
strictly signal-only chain, per the paper's own factorization (Eq. 12).

## 3. Why these are comparable to the paper's Table I

Every input to this chain was fixed *before* generation, directly from
the paper text, and logged in `PAPER_REQUIREMENTS.md`:
- Process definitions: colored = QCD-only, EW = Drell-Yan (Sec. III A).
- Trigger cut: pT(quirk pair) > 200 GeV (Sec. III B).
- Fiducial geometry: 8-layer barrel, |η| ≲ 1.8, 25 ns timing cut (Sec. III A/B).
- Reconstruction algorithm: identical seeding (layers 8/7, Δφ<0.1,
  Δz<2cm), identical growth-factor-3 rule, identical Δs/Δw thresholds
  (Sec. III C).

Because both the cut definitions and the algorithm are identical to the
paper's own description, a difference in the resulting efficiency
numbers reflects a genuine measurement difference (or, if it later turns
out one exists, a modeling/generator-setting difference) — not a
different quantity being compared under the same name.

## 4. Full table with statistical uncertainty

Source: `statistics/paper_comparison_table.csv` (fresh, independent
2000+2000-event regeneration; see `FINAL_FRESH_2000_EVENT_REPORT.md`).

| Sample | Quantity | Our value (k/n) | Paper's value | Wilson 95% CI | Exact binomial p-value | Verdict |
|---|---|---|---|---|---|---|
| Colored | ε_trig | 207/873 = 0.2371 | 0.24 | [0.210, 0.266] | 0.874 | Consistent |
| Colored | ε_fid | 25/68 = 0.3676 | 0.28 | [0.263, 0.486] | 0.136 | Consistent |
| Colored | ε_reco | 20/25 = 0.8000 | 0.35 | [0.609, 0.911] | <0.0001 | **Inconsistent** |
| EW | ε_trig | 186/1045 = 0.1780 | 0.10 | [0.156, 0.202] | <0.0001 | **Inconsistent** |
| EW | ε_fid | 94/186 = 0.5054 | 0.28 | [0.434, 0.576] | <0.0001 | **Inconsistent** |
| EW | ε_reco | 84/94 = 0.8936 | 0.72 | [0.815, 0.941] | 0.0001 | **Inconsistent** |

**How to read this table:**
- "k/n" is the exact numerator/denominator count from our own simulation
  (e.g. colored ε_trig: 207 of 873 matched events passed the trigger cut).
- "Wilson 95% CI" is the 95% confidence interval on *our own* measured
  proportion, accounting for finite-sample statistics. It answers: "given
  we only generated n events, how precisely do we know the true
  efficiency?"
- **If the paper's quoted value falls inside our interval**, the two are
  statistically consistent — the numerical difference is plausibly just
  sampling noise from our (smaller) event count, not a real physics
  difference.
- **If the paper's value falls outside our interval**, the difference is
  statistically significant at 95% confidence and requires an
  explanation beyond sampling noise (colored ε_reco and all three EW
  quantities fall in this category).
- The exact binomial p-value is the two-sided probability of seeing a
  deviation this large (or larger) from the paper's quoted value, if the
  paper's value were the true efficiency and our count were drawn from
  it by chance alone. Small p-values (≪0.05) indicate the same
  "statistically significant, not just sample noise" conclusion as the
  CI check, from a different angle.

## 5. What remains open (explicitly, not glossed over)

This document establishes *that* four of six efficiency quantities are
statistically inconsistent with the paper at this sample size — it does
**not** identify *why*. Root-causing those four gaps (colored ε_reco;
EW ε_trig, ε_fid, ε_reco) is a separate, not-yet-completed investigation,
independent of and unaffected by the converted-photon cross-section
audit discussed in §1.
