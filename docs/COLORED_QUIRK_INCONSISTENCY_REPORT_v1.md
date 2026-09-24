# Colored-Quirk Paper–Project Inconsistency Audit — Report

**Prepared for:** answering "why does the colored-quirk result appear
inconsistent with the paper?"
**Benchmark under audit:** mQ = 1.8 TeV, Λ = 2 keV, QCD/colored production, B = 2T
**Paper:** arXiv:1708.02243v2, Table I (colored/QCD row)

## 1. What exactly is inconsistent?

Only **one** of Table I's three colored-channel quantities shows a numeric
gap large enough to notice at a glance: **ε_reco = 5/7 = 0.714 (project)
vs. 0.35 (paper)**, a factor of ~2. The other two (ε_trig, ε_fid) are
close to the paper's values once measured correctly (see §3).

## 2. Which quantities agree? [DIRECT PROJECT DATA, INDEPENDENTLY RECOMPUTED]

| Quantity | Paper | Project | Verdict |
|---|---|---|---|
| ε_trig (charge-conditional, 27/125) | 0.24 | 0.216 | **CONSISTENT**, p=0.60 |
| ε_trig (full-matched sample, CORRECTED, 101/419) | 0.24 | 0.2411 | **CONSISTENT**, p=0.95 (near-exact) |
| ε_fid (7/27) | 0.28 | 0.259 | **CONSISTENT**, p=1.00 |
| ε_reco (paper-defined, 5/7) | 0.35 | 0.714 | **STATISTICALLY INCONCLUSIVE**, p=0.056 (borderline) |

## 3. Which denominator definitions caused apparent contradictions?
[INDEPENDENTLY RECOMPUTED — the key finding of this audit]

Prior project documentation (including this session's own earlier work)
repeatedly cited **"27/419 = 0.064"** as "the alternative, full-matched-
sample trigger efficiency" for the colored channel — implying the project's
trigger efficiency was roughly **4× too low** relative to the paper's 0.24.

**This figure was wrong.** It silently assumed the *same* 27 events (those
passing trigger **AND** already charge-filtered) were the correct numerator
for the full 419-event denominator. But trigger (a cut on quirk-pair pT)
and charge-filtering (a cut on R-hadron charge) are independent selections
on the same 419-event sample. Recomputing directly from the raw HepMC
record, independently, twice (once via a pre-computed boolean column, once
via a fresh threshold check on the raw pT value) gives:

**ε_trig(full matched) = 101/419 = 0.2411** — almost exact agreement with
the paper's 0.24 (p=0.95).

The earlier 27/419 figure was actually the **joint** probability of passing
both trigger and charge-filter relative to the full sample — a real,
correctly-computed quantity, just mislabeled as a marginal trigger
efficiency. This single correction resolves what looked like the project's
most serious apparent disagreement with the paper.

## 4. Is ε_reco = 5/7 genuinely inconsistent with the paper's 0.35?
[INDEPENDENTLY RECOMPUTED]

**No, not at a defensible confidence level.** The exact two-sided binomial
test against p₀=0.35 gives **p = 0.056** — just above the conventional 0.05
threshold. Wilson 95% CI on the project's own point estimate is [0.359,
0.918], which *does* exclude 0.35 at its lower edge only marginally; the
Clopper-Pearson 95% interval [0.290, 0.963] comfortably *includes* 0.35.
**Verdict: numerically different, but statistically inconclusive** — not a
confirmed discrepancy.

## 5. How much is due to N=7 statistics?

Almost entirely. At N_fid=7, a true rate of 0.35 has a standard deviation
of √(0.35×0.65/7) ≈ 0.18 — the observed 0.714 is well within ~2 standard
deviations of that. A rough (asymptotic, illustrative — not as rigorous as
the exact binomial test above) discrimination calculation suggests roughly
16 fiducial events would be needed for a defensible 3σ conclusion either
way, assuming the true underlying rate is close to what's observed here.
**This project's own colored-benchmark sample was never large enough to
resolve this specific question — that's an existing, disclosed statistical
limitation, not a new finding.**

## 6. Which modelling differences remain?
[DIRECT PAPER EVIDENCE + DIRECT CODE EVIDENCE]

19 of 25 audited modeling items are **EXACT MATCH** (trigger definition,
fiducial geometry, pixel dimensions, SCT resolution convention, beamspot
smearing, timing cut, hit acceptance, Sec IIIC seeding/growth/selection
algorithm, Δs/Δw definitions, B-field, material-interaction treatment,
dE/dx, glueball radiation). 4 are **APPROXIMATE MATCH** (ISR treatment,
primary-vertex handling, hit-merging exact algorithm, jet-matching xqcut
value). 2 are **UNDOCUMENTED BY PAPER** (PDF set, renorm/fact scales — the
paper simply never states these). Full matrix:
`tables/colored_modeling_comparison_matrix.csv`.

**One quantified, directionally-understood effect:** the SCT resolution
convention (2× intrinsic Run-2 accuracy, per the paper's own "conservative"
prescription) increases Δs at fixed geometry relative to a hypothetical
zero-smearing case — already investigated and confirmed real (not a bug)
in a prior project audit (`DEVIATIONS_LOG.md`, 2026-09-12/13). Event-level
forensics (§7) show this effect concretely: 2 of the 3 events that pass
plane-finding and multiplicity requirements fail the final Δs<0.01cm cut
by a very narrow margin (0.0105, 0.0119 — both just over the threshold).

## 7. Event-level forensic verdict — all 7 truth-fiducial events
[INDEPENDENTLY RECOMPUTED from raw stored hit data]

| Event | Plane found | Δs | Δw | Multiplicity pass | Final pass | First failure |
|---|---|---|---|---|---|---|
| 38 | No | – | – | – | No | no candidate found at all |
| 169 | No | – | – | – | No | no candidate found at all |
| 208 | Yes | 0.01046 | 0.219 | Yes | **No** | Δs just above 0.01cm threshold |
| 302 | Yes | 0.02644 | 0.227 | No | No | multiplicity (only 5/8 layers with 2+ hits) |
| 344 | Yes | 0.01635 | 0.442 | No | No | multiplicity (only 6/8 layers with 2+ hits) |
| 369 | Yes | 0.01186 | 0.233 | Yes | **No** | Δs just above 0.01cm threshold |
| 386 | Yes | 0.00937 | 0.243 | Yes | **Yes** | (final pass) |

**Driver of the low N_final:** the sole final-pass event (386) and the two
narrow misses (208, 369) show the Δs values are clustered right around the
0.01cm threshold (0.0094, 0.0105, 0.0119) — the tight final Δs cut, combined
with the paper's own conservative SCT resolution, is genuinely responsible
for most of the attrition from ε_reco (5/7) down to the final Sec IV rate
(1/7), not a code defect. This is consistent with, not contradictory to,
the paper's own text (Sec IV, p.7): the reconstruction efficiency and the
final signal-region pass rate are explicitly different quantities (§ the
separate ε_reco audit earlier this session established this same
distinction from the paper text directly).

## 8. Was any code bug found?

**No bug in the reconstruction/trigger/fiducial code itself.** The one
genuine error found and corrected in this audit is a **documentation/
labeling error** (the erroneous 27/419 "full-matched trigger efficiency"
figure, §3) — not a defect in `coplanarity_fit.py`, `seeding_and_iterative_fit`,
`select_reconstructed_plane`, `check_hit_multiplicity`, `apply_signal_region_cuts`,
or the charge-lookup code, all of which were independently re-exercised
this audit and reproduced identical numbers to prior, already-validated
runs.

## 9. What can and cannot be claimed?

**Can claim:** ε_trig and ε_fid for the colored channel are statistically
consistent with the paper once the correct (and now corrected) denominators
are used. ε_reco's numeric gap is real but not statistically established
at N=7 — it is neither confirmed consistent nor confirmed inconsistent.
The methodology match (19/25 exact) rules out most systematic/modeling
explanations for the ε_reco gap; the SCT-resolution-driven Δs tightness is
the one quantitatively-supported partial explanation for why the *final*
(Sec IV) rate is so much lower than ε_reco itself, which is a separate,
already-understood effect.

**Cannot claim:** that ε_reco=0.714 is confirmed to disagree with the
paper's 0.35 (p=0.056, not below the conventional 0.05 threshold). Cannot
claim the paper's own ε_trig denominator convention (charge-conditional vs.
full-matched) is resolved from the text alone — both readings now agree
with the paper numerically, which somewhat reduces the practical stakes of
that ambiguity for the colored channel specifically.

## 10. Minimum next test needed (not run — proposal only, not authorized)

A larger colored-quirk fiducial sample (target ≥30-40 truth-fiducial
events, requiring roughly 4000-6000 additional matched events based on the
measured ~1.7% fiducial-per-matched rate observed this audit) would let the
ε_reco question be resolved at a defensible 2-3σ level. **Not run — this
audit performed cache-only/read-only analysis exclusively, per the explicit
instruction; any new production requires separate authorization.**

## Evidence labels used throughout

DIRECT PAPER EVIDENCE (paper text quotes), DIRECT PROJECT DATA (stored
files, read as-is), INDEPENDENTLY RECOMPUTED (freshly calculated this
audit, not cited from a prior report), INFERENCE (reasoned conclusion from
the above), UNRESOLVED (genuinely undetermined from available evidence).
