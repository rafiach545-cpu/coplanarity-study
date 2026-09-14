# arXiv:1708.02243v2 -- complete figure/table inventory and reproduction status

Every figure and table in the paper, what it shows, what's needed to reproduce
it, and current status in this project. Updated as work progresses.

---

## Fig. 1 -- Schematic event display (illustration only)

Hand-drawn schematic of quirk pair + ISR jet, cylinders = 3 innermost tracker
layers, hits on a shaded plane. **Not a data figure** -- purely illustrative,
no reproduction needed (could redraw for our own report later, optional).

Status: N/A (illustration, not a physics result)

---

## Fig. 2 -- Angular momentum L and separation d vs radial distance r

Single representative event, mQ=1.8 TeV, Lambda=2 keV, B=2T. Shows L(r) and
d(r) oscillating, illustrating L,d do not vanish except at r=0.

Needs: Stage 1 trajectory integrator (DONE, validated to 1e-12 vs Eq.4),
`angular_momentum_and_separation()` helper (DONE, in quirk_trajectory.py).

Status: **Partially done.** Core integrator validated rigorously. A
qualitative L(r)/d(r) plot was generated during B-field validation
(validate_bfield_fig2_fig3.py) but not as a polished, paper-comparable
figure yet -- the paper's exact initial conditions for "a representative
event" are not published, so this can only ever be a qualitative shape
match, not a digit-for-digit reproduction.

## Fig. 3 -- Delta_phi vs radial distance r (two mass points)

mQ=1.8 TeV and mQ=800 GeV, both Lambda=2 keV, B=2T. Shows Delta_phi rising
and saturating below ~1e-3.

Needs: same trajectory integrator + a properly-defined Delta_phi diagnostic.

Status: **Attempted, found methodologically tricky.** Naive instantaneous-L-
direction tracking is unstable near L~0 crossings (documented in this
session's earlier work). A robust reproduction likely needs the ACTUAL
plane-fit algorithm (Stage 5) applied to a full simulated trajectory's hits,
not a shortcut angular-momentum diagnostic -- not yet built this way.

## Fig. 4 -- Single signal event, hits projected onto (n3,n2) plane

Colored quirk, mQ=1.8 TeV, Lambda=2000 eV. Shows the characteristic thin
strip of hits, Delta_w~0.074cm, Delta_s~83um annotated.

Needs: Stage 0 signal event (DONE) -> Stage 1 trajectory (DONE) -> Stage 2
detector hits (DONE) -> Stage 5 plane fit + projection (DONE, all pieces
exist and were exercised together, e.g. in the audit's regression tests).

Status: **All pipeline pieces built and individually exercised on real
events.** Not yet assembled into one polished, labeled, paper-style plot
artifact. This is a near-term achievable deliverable -- pick one clean
trigger-passing event with Delta_s<0.01cm (need to find/generate one; the
audited pipeline can identify candidates), project onto (n3,n2), plot with
Delta_w/Delta_s annotated like the paper's figure.

## Fig. 5 -- Delta_s and Delta_w distributions, signal vs backgrounds

Colored quirk (1.8TeV,2keV) + EW quirk (800GeV,4keV) vs pile-up vs converted
photon, before final cuts, log-scale histograms.

Needs: Stage 0/1/2/5 for BOTH benchmark points (colored DONE for 1800GeV/
2keV; EW quirk model exists but not yet run through full pipeline) + Stage
6a pile-up (NOT BUILT) + Stage 6b photon conversion (BUILT, 1500-event test
done, cross-section-normalization now resolved per this session's decision
to use our own measured 0.231051 pb rather than chase the paper's
unreproducible ~1pb).

Status: **Signal (colored) piece exists in raw form** (Delta_s/Delta_w per
event already computed in multiple scans this session). **EW quirk
benchmark: not yet run end-to-end.** **Pile-up: not started.** **Photon
conversion: built and run (1500 events), needs scaling up for a proper
histogram-quality sample.** This is the single largest remaining piece of
work -- needs all 4 populations (2 signal points + 2 backgrounds) at
reasonable statistics before a real Fig.5-style plot can be made.

## Fig. 6 -- mQ vs Lambda exclusion/discovery contours, 300 fb^-1

Full 2D grid scan for BOTH representations ((3,1)_2/3 and (1,1)_1), 3-event
(2-sigma exclusion) and 5-event (discovery) contours, overlaid with HSCP/
monojet limits and dcm iso-contours.

Needs: full efficiency (epsilon_trig x epsilon_fid x epsilon_reco) at MANY
(mQ, Lambda) grid points for both representations, plus a luminosity/
cross-section model to convert efficiency -> expected event count at
300 fb^-1, plus external HSCP/monojet limit curves (paper credits M.Farina/
M.Low "private communication" for those -- we do NOT have access to that
input and cannot reproduce those overlay curves at all).

Status: **Far off.** This is the most ambitious figure in the paper and
requires the full pipeline running efficiently across a 2D parameter grid,
plus external inputs (HSCP/monojet limits) that are fundamentally
unreproducible from the paper alone (private communication data). Realistic
goal: reproduce OUR OWN exclusion/discovery contours from our own pipeline,
explicitly noting the HSCP/monojet overlay curves cannot be reproduced.

## Fig. 7 / App. A -- dE/dx and beta*gamma distributions

Two benchmark points, Lambda=2keV. Explicitly NOT used in the main analysis
cuts (paper's own words: "we did not make use of variables relying on
dE/dx measurements in our analysis").

Status: **Lowest priority.** Would need a dE/dx model (Bethe-Bloch-like
most-probable-value vs beta*gamma, paper cites PDG for this) applied to
each simulated hit. Not needed for the main cut-flow/efficiency results;
defer until everything else is done.

---

## Table I -- Efficiency breakdown, two benchmarks x Lambda scan

DY (EW quirk, 800 GeV): Lambda = 1,2,3,4,5 keV
QCD (colored quirk, 1800 GeV): Lambda = 1,2,3,5,10 keV
Columns: epsilon_trig, epsilon_fid, epsilon_reco

Needs: full Stage 0-5 pipeline at EACH of these 10 (mQ,Lambda) combinations,
for BOTH representations, with enough statistics per point to quote a
stable efficiency number.

Status: **One (mQ,Lambda) point partially done**: colored quirk, 1800 GeV,
Lambda=2 keV (close to but not exactly one of Table I's listed Lambda
values -- Table I has 1,2,3,5,10 keV for QCD, and 2 keV IS one of them, so
this is directly comparable). Current measured epsilon_reco context: 0/23
full-hit events passed signal region in the initial audit-era sample
(small-N, and using REAL Run-2 SCT resolution rather than the paper's own
2009-projection inputs, a deliberate choice already discussed and kept).
The other 9 grid points, and the entire EW/DY benchmark line, not started.

---

## Overall status summary

| Piece | Status |
|---|---|
| Colored quirk UFO model + QCD-only production | Done, validated (R-hadron formation working) |
| EW quirk UFO model + Drell-Yan production | Built, NOT yet run through full detector+algorithm pipeline |
| Trajectory integrator (Eq. 3) | Done, validated to 1e-12 (Eq.4) and 4e-5 (gyroradius) |
| ATLAS Run-2 8-layer geometry | Done, verified against reference |
| Detector hit simulation | Done, audited, 2 bugs fixed (merging, CM-frame timestep) |
| Coplanarity plane-fit algorithm | Done, audited, 1 bug fixed (missing per-layer cut) |
| Photon-conversion background (Stage 6b) | Built, tested at 1500 events; cross-section normalization
resolved (use our own 0.231051 pb measured value, 1% conversion weight, per user's explicit decision) |
| Pile-up background (Stage 6a) | Not started |
| Fig. 2 | Qualitative only, exact match impossible (unpublished init conditions) |
| Fig. 3 | Needs rebuilding via real plane-fit algorithm, not the shortcut diagnostic |
| Fig. 4 | All pieces exist, not yet assembled into one polished plot |
| Fig. 5 | Needs EW quirk point + pile-up + larger photon-conversion stats |
| Fig. 6 | Far off; external HSCP/monojet overlay data fundamentally unreproducible |
| Fig. 7 / dE/dx | Lowest priority, paper itself doesn't use it in main analysis |
| Table I | 1/10 grid points partially done |
