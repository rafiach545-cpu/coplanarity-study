# Phase 3 — Final EW Trigger/Fiducial Verdict

EW 2000: N_matched=1045, N_trigger=186, N_fiducial=94.

| Quantity | k/n | value | std binom err | Wilson 68% | Wilson 95% | paper | exact p |
|---|---|---|---|---|---|---|---|
| ε_trig | 186/1045 | 17.80% | 1.18% | [16.65%,19.01%] | [15.60%,20.24%] | 10% | 1.79e-14 |
| ε_fid | 94/186 | 50.54% | 3.67% | [46.88%,54.19%] | [43.42%,57.64%] | 28% | 1.26e-10 |

## 1. Why does trigger efficiency exceed the paper?

Verified (`EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/`, earlier phases): the
trigger variable, cut direction, and threshold exactly match the paper's
own definition (quirk-pair CM-system pT > 200 GeV, no unit/boundary
issue). Generation/matching settings (xqcut, PDF, scale) are
byte-identical between this project's own 1000- and 2000-event samples,
ruling out an internal project inconsistency. Since a pure 2→2 Drell-Yan
process gives the quirk pair exactly zero net pT by momentum
conservation, ε_trig is a direct, sensitive probe of how much hard ISR
this project's MLM-matched generation produces — a quantity known to be
PDF/merging-scale-sensitive. The paper does not publish its own PDF,
merging scale, or shower tune (confirmed by direct full-text search:
zero mentions). **Classification: UNRESOLVED — undocumented paper
generator settings.** No bug found in the trigger computation itself.

## 2. How does pair-pT contribute to fiducial acceptance?

Demonstrated (not merely hypothesized) via binned efficiency and
correlation analysis on existing events only
(`PT_ETA_ATTRIBUTION_FOLLOWUP2.md`): fiducial efficiency rises
monotonically with quirk-pair pT (41.0%→80.0% across 5 bins, point-
biserial r=0.230, exact p=0.0016), and this association is **independent**
of η-centrality (mediation check: pT_pair and max|η| are not
significantly correlated with each other, Spearman r=−0.066, p=0.37;
partial correlation of pT_pair with fiducial pass controlling for
max|η| is 0.191, barely attenuated from the raw 0.230).

## 3. Why does pair-pT NOT fully explain the 50.54% vs 28% gap?

Quantified directly: even the **lowest** pT_pair bin (200,300] GeV — the
slice least affected by hard ISR — gives 34/83 = 41.0% fiducial
efficiency, Wilson 95% [31.0%,51.7%], still statistically significantly
above the paper's 28% (exact p=0.0138). Every single pT bin tested,
including the most favorable one, individually exceeds the paper's
value. pT_pair explains part of the internal *spread* across this
project's own events; it does not explain the *offset* relative to the
paper.

## 4. How do pair rapidity and crossing-point η affect barrel acceptance?

Pair rapidity is the single strongest kinematic predictor found in this
audit: fiducial efficiency falls from 92.8% (|Y_pair|≤0.3) to 0%
(|Y_pair|>0.9) — a near step-function, sharper than the pT_pair trend.
Separately, the Phase-1 replay (this session) demonstrated that
crossing-point |η| (evaluated where the propagated trajectory actually
crosses each layer's radius) is **systematically larger** than the
production-level |η| for every one of the 30 classified "moderate
truth-η, zero-hit" events (mean drift at layer 1: +1.28, range
+0.36 to +1.71, always positive). **Per instruction, no claim is made
about which force or mechanism causes this** — only the demonstrated
result: propagated layer-crossing |η| exceeds production-level |η| in
100% of the 30 events tested, and this exceeds what a pure vertex-offset
(beamspot-smearing) geometric effect alone would predict (mean
geometric-only |drift|=0.55 vs mean actually-observed |drift|=1.60,
weak correlation r=0.38 between the two) — i.e. the drift is real
trajectory behavior beyond a coordinate/origin artifact, without
asserting which physical component (string tension vs magnetic
component vs their interplay) is responsible.

## 5. Are zero-hit losses physical or numerical?

**Physical**, for 30 of 31 tested events (97%, exhaustive within the
150s+600s bounded budgets): every one shows all 16 (quirk×layer)
crossings geometrically found, all 16 rejected solely by the |η|<1.8
cut, zero root-finding failures, zero non-finite states, replay
reproduces the stored zero-hit decision exactly. 1 event (165) remains
genuinely unresolved (timed out at both budgets) — not classified by
extrapolation.

## 6. Does a detector-acceptance bug or double-counting exist?

**No double-counting**: only one acceptance mechanism (the constant
|η|<1.8 cut) exists in the code; no separate finite-z boundary is
implemented (Phase 2, §3-4). **A genuine, quantitatively-demonstrated
modeling-choice difference was found**, however (Phase 2): the
project's constant-|η| cone acceptance is geometrically **not
equivalent** to a literal finite-length barrel cylinder (the more literal
reading of the paper's own "we only included the barrel... of the pixel
and SCT detectors"), and would be systematically *looser* at inner
layers under the latter model — this is flagged as an **INFERENCE**,
explicitly not proven against the paper's actual (unavailable) code or
ref [27]'s exact dimensions, and is a candidate (not confirmed)
contributor to the fiducial gap. This is **not classified as a bug** in
the project's code — the project directly and defensibly implements the
paper's own stated words — but as a **modeling-choice difference worth
disclosing**.

## 7. What remains attributable only to undocumented paper settings?

The residual, unexplained magnitude of both the ε_trig gap (17.80% vs
10%) and the ε_fid gap (50.54% vs 28%, beyond what pT/η/rapidity-shape
and the finite-z-vs-cone modeling question can quantitatively account
for) remains attributable only to **undocumented paper generator, PDF,
matching, or shower settings** — consistent with, and unchanged from,
every prior phase of this audit's conclusion. This audit does not close
that gap, and does not claim to.

**Overall verdict: UNRESOLVED**, with (a) the ISR/pT_pair mechanism
demonstrated but quantitatively insufficient, (b) rapidity/η-centrality
identified as the dominant internal driver, (c) 30/31 zero-hit losses
demonstrated physical (not numerical), (d) a real, disclosed
finite-z-vs-cone modeling-choice question raised but not resolved, and
(e) the ultimate root cause remaining the paper's undocumented
generation settings.
