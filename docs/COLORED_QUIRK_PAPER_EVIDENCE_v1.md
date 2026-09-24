# Colored-Quirk Paper Evidence — Direct Extraction, arXiv:1708.02243v2

All quotations verbatim from the cached paper text extraction
(`paper.txt`), with page numbers from the rendered PDF (`===== PAGE N =====`
markers) and paper.txt line numbers. Every entry labeled DIRECT PAPER
EVIDENCE unless noted.

## 1. Production process (Sec III A, p.5, lines 386-392)

> "We generate signal samples of vector-like fermions with up to 1 jet
> using MadGraph5_aMC@NLO [24, 25], which is subsequently matched using
> Pythia8 [21, 26]. For electroweak production the quirks are taken to
> have unit charge and are produced in Drell-Yan, while for colored
> production only QCD contributions are included."

- Colored: QCD-only production, matched with Pythia8, up to 1 extra jet
  (MLM matching). **DIRECTLY STATED.** Matches project's `ickkw=1` run_card
  setting and `quirk_signal_1800gev_2kev` process definition (QCD-only).

## 2. Trajectory/detector simulation (Sec III A, p.5, lines 392-409)

> "The resulting four-momenta of the quirks are then evolved by numerically
> solving the equation of motion in (3) assuming a uniform 2T magnetic
> field along the z-direction. ... we use the parameters of the various
> detector elements as specified in [27]. Specifically, for the pixel
> detector we use the pixel size rather than the resolution and for the
> silicon microstrip tracker (SCT) we conservatively assume a resolution of
> twice the intrinsic accuracy quoted in [27]. Hits in neighboring pixels
> ... are merged to a single hit ... We further apply a uniform, gaussian
> smearing with width 45 mm to the z-coordinates of all the hits, to
> account for the finite longitudinal size of the beamspot. For simplicity,
> we only included the barrel of the pixel and SCT detectors ... which
> effectively restricts the fiducial range to |η| ≲ 1.8."

- B = 2T along z — **DIRECTLY STATED**, matches project (`B_tesla=2.0`
  everywhere).
- SCT resolution = 2× the intrinsic Run-2 accuracy — **DIRECTLY STATED**,
  already the subject of a prior project audit (`DEVIATIONS_LOG.md`,
  2026-09-12/13 entry): "SCT z-resolution from the real Run-2 paper is
  580 μm intrinsic → 1160 μm after the paper's own 'double the intrinsic
  accuracy' conservative prescription" — used correctly by this project.
- Barrel-only, |η|≲1.8 fiducial — **DIRECTLY STATED**, matches project's
  8-layer barrel-only geometry (no endcaps).
- 45mm beamspot z-smearing — **DIRECTLY STATED**, matches project's
  `BEAMSPOT_SIGMA_Z_CM`.

## 3. Trigger (Sec III B, p.5, lines 444-448)

> "With start-up trigger thresholds for run-2 in mind [29], we therefore
> impose a pT > 200 GeV cut on the center [of] mass momentum of the
> quirk/anti-quirk system."

- **The paper's trigger is pT(quirk-pair CM system) > 200 GeV — NOT missing
  ET (MET).** This is directly, unambiguously stated. **DIRECTLY STATED.**
  Matches this project's `trigger_proxy_pass = quirk_pair_pt_gev > 200`
  (`extract_pilot_data.py::parse_hepmc`) exactly — the project's trigger
  implementation is paper-matching, not an approximation, for the colored
  channel and the EW channel alike.

## 4. Colored charge-state treatment (Sec II, p.2, lines 138-144)

> "In the latter case [(3,1)_2/3 colored quirks], the quirks will quickly
> hadronize into quirk-hadrons, and the probability for those final states
> to have ±1 charges is roughly 30% as estimated using Pythia8 [21]. Our
> analysis is largely independent on the charges of the quirk-hadrons, as
> long as both quirk-hadrons carry non-zero electric charge, such that they
> leave a signal in the inner trackers of ATLAS and CMS."

- ~30% probability both R-hadrons are ±1 charged — **DIRECTLY STATED**
  (order-of-magnitude figure, "roughly 30%", not a precise value with
  uncertainty quoted). Project's own measured values across 3 mass points
  this session: 31.2%-37.2% (colored_1500/1800/2400 GeV) — consistent with
  "roughly 30%".
- The paper does **not** state whether Table I's own ε_trig=0.24 for the
  colored (QCD) benchmark is computed relative to the full matched sample
  or the charge-filtered subsample — **UNRESOLVED, paper does not specify**
  (see §7 below, this is the crux of the audit's denominator question).

## 5. Eq. 12 factorization and ε_reco (p.6-7) — already established this
session, reused here unchanged

> "ε = ε_trig × ε_fid × ε_reco." (Eq. 12, p.6)
> "The reconstruction efficiency is defined as the efficiency of our
> algorithm in finding quirks which satisfy both the trigger and fiducial
> requirements." (p.7)

- ε_reco numerator = Sec IIIC plane-finding algorithm's own event-selection
  output (Δw<1cm, smallest-Δs tiebreak); denominator = N(trigger AND
  fiducial) = N_fiducial. **DIRECTLY STATED and independently re-derived
  this session** (see the standalone ε_reco audit earlier in this
  conversation for the full textual argument — not repeated verbatim here).
  This is a DIFFERENT, stricter quantity from the Sec IV final-selection
  pass rate (hit-multiplicity + Δs<0.01cm on top).

## 6. Table I values (p.7, caption + rows)

> "800 (DY): 1 keV → ε_trig=0.10, ε_fid=0.28, ε_reco=0.11 / 2 keV → 0.41 /
> 3 keV → 0.65 / 4 keV → 0.72 / 5 keV → 0.74"
> "1800 (QCD): 1 keV → ε_trig=0.24, ε_fid=0.28, ε_reco=0.083 / 2 keV → 0.35
> / 3 keV → 0.59 / 5 keV → 0.74 / 10 keV → 0.58"

- **The colored benchmark (mQ=1800 GeV, Λ=2 keV, this audit's exact
  subject) has ε_reco(paper) = 0.35** — DIRECTLY STATED.
- ε_trig=0.24 and ε_fid=0.28 are given as flat, Λ-independent values for
  the colored channel — DIRECTLY STATED, caption: "ε_trig and ε_fid are
  independent of Λ, [with] the latter [ε_fid] with the exception of small
  edge effects."
- Table I gives **no explicit statement of ε_trig's denominator** (matched
  sample vs. charge-filtered subsample) — **UNRESOLVED from the paper
  text alone.**

## 7. The denominator ambiguity — paper does not resolve it explicitly

The paper introduces the ~30% charge-survival probability in Sec II (§4
above) as a physical fact about hadronization, separate from the Eq. 12
efficiency chain (ε_trig × ε_fid × ε_reco), which contains no explicit
fourth "ε_charge" factor. Two readings are grammatically and physically
possible:

- **Reading A (charge-conditional):** Eq. 12's three efficiencies are
  implicitly computed on the population of events that ALREADY have both
  quirk-hadrons charged (since only charged quirks "leave a signal in the
  inner trackers," per §4's own text — an uncharged quirk-hadron produces
  no measurable hits at all, so it is physically excluded from the
  trigger/fiducial/reco chain from the start, not merely down-weighted).
  Under this reading, ε_trig(paper)=0.24 is charge-conditional, matching
  this project's own `27/125` convention (125 = charge-filtered).
- **Reading B (full-matched-sample):** ε_trig is computed relative to the
  full matched (pre-charge-filter) sample, with charge survival treated as
  a separate, unstated multiplicative factor the paper simply omits from
  Eq. 12 (perhaps folded into the overall cross-section instead). Under
  this reading, ε_trig(paper)=0.24 would correspond to this project's
  `27/419` (419 = full matched sample).

**This ambiguity is UNRESOLVED by the paper text alone** — Section 4 of
this audit (below) computes both and lets the numerical comparison inform,
without forcing a conclusion the text doesn't support.

## 8. Figure/Table inventory referenced for this audit (brief)

- Figure 2 (p.4): representative Δs/L(ħ) vs r for colored benchmark
  1.8TeV/2keV, plateau/oscillation shape only, no cutflow numbers.
- Figure 4 (p.6): example hit pattern, single representative event, no
  statistical cutflow numbers.
- Figure 5 (p.7): Δs/Δw distributions, colored 1.8TeV/2keV among signal
  curves, background rejection discussion, no explicit numerator/denominator
  table.
- Figure 6 (p.8-9): 95% exclusion/discovery contours, L=300fb⁻¹, no
  colored-benchmark-specific cutflow numbers relevant to this audit
  (already the subject of the separate, ongoing Phase 5 production).

None of Figures 2, 4, 5, 6 contain a colored-benchmark cutflow number that
independently corroborates or contradicts Table I's ε_trig/ε_fid/ε_reco —
Table I remains the sole quantitative source for this audit's comparison.
